"""Independent fraction-free rank verification; --lattice re-evaluates all images.

Without --lattice this verifies the stored exact image matrices, highest
columns and their completeness, but does not regenerate lattice images.
"""
import argparse
import gzip
from fractions import Fraction as Q
import json
from math import lcm
from pathlib import Path
from perfectjet.asterion_primitives import (
    JetAlgebra, decode_polynomial, encode_polynomial, g_tensor_i_highest,
    ideal_highest_images, load_certificates, THETA,
)
from perfectjet.asterion_lattice_projection import ProjectedLatticeE8VOA
from perfectjet.asterion_kernel_tower import tensor_cube_character_receipt
from perfectjet.asterion import source_digests

ROOT=Path(__file__).resolve().parents[1]


def bareiss_rank(matrix):
    """Integer fraction-free elimination, independent of the production rank code."""
    a=[list(row) for row in matrix]
    if not a:
        return 0
    previous=1; rank=0
    for col in range(len(a[0])):
        pivot=next((r for r in range(rank,len(a)) if a[r][col]),None)
        if pivot is None:
            continue
        a[rank],a[pivot]=a[pivot],a[rank]
        value=a[rank][col]
        for r in range(rank+1,len(a)):
            for c in range(col+1,len(a[0])):
                numerator=value*a[r][c]-a[r][col]*a[rank][c]
                quotient,remainder=divmod(numerator,previous)
                if remainder:
                    raise ArithmeticError('non-exact Bareiss division')
                a[r][c]=quotient
            a[r][col]=0
        previous=value;rank+=1
        if rank==len(a):
            break
    return rank


def vector_rank(vectors):
    keys=sorted(set().union(*vectors))
    scales=[lcm(*(Q(z).denominator for z in v.values())) if v else 1 for v in vectors]
    return bareiss_rank([[int(v.get(k,0)*scale) for v,scale in zip(vectors,scales)] for k in keys])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lattice',action='store_true')
    parser.add_argument('--source-null',action='store_true',help='replay the weight-five source lift with the original full evaluator')
    args=parser.parse_args()
    jets=JetAlgebra()
    reconstructed=tensor_cube_character_receipt()
    assert reconstructed['passed']
    components=reconstructed['Schur_components']
    ideal_record=json.loads(gzip.decompress((ROOT/'results/asterion-primitives/w7-adjoint-ideal.json.gz').read_bytes()))
    assert ideal_record['source_sha256']==source_digests()
    sources=g_tensor_i_highest(jets,THETA)
    assert [encode_polynomial(v) for v in sources]==ideal_record['ideal_source_vectors']
    ideal=ideal_highest_images(jets,sources,7)
    source=load_certificates()['sectors']['w5-248']['representatives'][0]
    derived=jets.derivative(jets.derivative(decode_polynomial(source['symbol'])))
    correction=jets.derivative(jets.derivative(decode_polynomial(source['correction'])))
    assert encode_polynomial(derived)==ideal_record['derivative_symbol']
    assert encode_polynomial(correction)==ideal_record['derivative_correction']
    assert vector_rank(ideal)==ideal_record['ideal_rank_Q']==5
    assert vector_rank(ideal+[derived])==ideal_record['ideal_plus_D2P_rank_Q']==6
    if args.source_null:
        from perfectjet.asterion_primitives import verify_primitive_certificate
        replay=verify_primitive_certificate(load_certificates()['sectors']['w5-248'],lattice_replay=True)
        assert replay['passed']
        (ROOT/'results/asterion-primitives/w7-source-null-replay.json').write_text(json.dumps(replay,indent=2,sort_keys=True)+'\n')
    for dimension in (1,248):
        expected_top=sum(coefficient*sum(
            irrep['multiplicity'] for irrep in components[name]['irreducibles']
            if irrep['dimension']==dimension) for coefficient,name in (
                (4,'symmetric_cube'),(5,'mixed_S21'),(1,'exterior_cube')))
        path=ROOT/f'results/asterion-primitives/w7-{dimension}-projected-rank.json.gz'
        record=json.loads(gzip.decompress(path.read_bytes()))
        assert record['source_sha256']==source_digests()
        columns=[decode_polynomial(c) for c in record['columns']]
        assert all(jets.is_highest(c) for c in columns)
        target=(0,)*8 if dimension==1 else (2,4,6,5,4,3,2,3)
        assert all(jets.weight(m)==target and sum(r+1 for _,r in m)==7
                   for c in columns for m in c)
        assert record['top_highest']==expected_top
        assert record['lower_highest']==(3 if dimension==1 else 4)
        assert len(columns)==record['top_highest']+record['lower_highest']
        assert vector_rank(columns)==len(columns)
        images=[{(tuple(beta),tuple(tuple(x) for x in osc)):Q(z)
                 for beta,osc,z in im} for im in record['images']]
        keys=sorted(set().union(*images))
        scales=[lcm(*(z.denominator for z in im.values())) if im else 1 for im in images]
        matrix=[[int(im.get(k,0)*scale) for im,scale in zip(images,scales)] for k in keys]
        rank=bareiss_rank(matrix)
        assert rank==record['projected_rank_Q']
        assert vector_rank(images[record['top_highest']:])==record['lower_highest']
        known_nullity=0 if dimension==1 else 6
        assert len(columns)-rank==known_nullity
        if args.lattice:
            lattice=ProjectedLatticeE8VOA(jets,support=record['support'])
            for c,im in zip(columns,images):
                assert lattice.symmetric_lift(c)==im
            lattice.clear_cache()
        print(json.dumps({'sector':dimension,'independent_rank_Q':rank,
                          'stored_image_matrix_verified':True,'lattice_replayed':args.lattice}),flush=True)


if __name__=='__main__':
    main()
