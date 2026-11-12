"""Construct old-generator products as actual highest jet polynomials."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json
from quartic_remaining_sectors import QuarticJets
from perfectjet.asterion_primitives import (JetAlgebra,_add,omega_pair,exact_rank,
    encode_polynomial,decode_polynomial,load_certificates,_contraction)
from perfectjet.asterion_relations import AffinePBW

def R_project(j,p):
    out={};C=_contraction(j,None,0,0)
    for monomial,z in p.items():
        pair=[i for i,r in monomial if r==0];extra=tuple(x for x in monomial if x[1]!=0)
        a,b=pair;_add(out,{monomial:z*Q(1,7)})
        for (u,v),c in omega_pair(j,a,b).items():_add(out,{tuple(sorted(((u,0),(v,0))+extra)):z*c*Q(-1,14)})
        if j.form(a,b):
            for m,c in C.items():_add(out,{tuple(sorted(m+extra)):z*c*j.form(a,b)*Q(-1,56)})
    return out

def run(dim):
    path=Path(f'quartic_ideal_only_{dim}.json')
    if not path.exists():path=Path(f'quartic_full_{dim}.json')
    sector=json.loads(path.read_text()) if path.exists() else None
    j=QuarticJets()
    if sector is None:
        e=next(x for x in json.loads(Path('quartic_schur_receipt.json').read_text())['weight7_length4_ambient']['irreducibles'] if x['dimension']==dim)
        target=tuple(int(sum(j.cartan_inverse[i][k]*e['dynkin_labels'][k] for k in range(8))) for i in range(8))
    else:target=tuple(sector['target_root_coordinates'])
    ideal=[decode_polynomial(v) for v in sector['ideal_highest_columns']] if sector else []
    old=[]
    if dim==27000:
        p=decode_polynomial(load_certificates()['sectors']['w5-248']['representatives'][0]['symbol'])
        u=j.algebra.root_index[(2,4,6,5,4,3,2,3)]
        old=[j.multiply({((u,1),):Q(1)},p),j.multiply({((u,0),):Q(1)},j.derivative(p))]
        dependency=['weight5_adjoint_source_replay.json']
    else:
        basis,_=j.highest_vectors([(0,0,9)],target)
        R=[R_project(j,p) for p in basis]
        assert exact_rank(R)==1 and all(j.is_highest(p) for p in R)
        source=next(p for p in R if p)
        module=AffinePBW(algebra=j.algebra)
        # q in R3875 -> F_Q; vary the free-current order and derivative.
        for derivative,free_order in ((0,2),(1,1),(2,0)):
            grouped={}
            for monomial,z in source.items():
                pair=tuple(i for i,r in monomial if r==0);free=next(i for i,r in monomial if r==9)
                grouped.setdefault(free,{})[pair]=grouped.setdefault(free,{}).get(pair,0)+z
            out={}
            for free,quadratic in grouped.items():
                fq=module.quadratic_jet_tensor(quadratic)
                for _ in range(derivative):fq=j.derivative(fq)
                _add(out,j.multiply({((free,free_order),):Q(1)},fq))
            assert j.is_highest(out)
            old.append(out)
        dependency=['weight4_3875_source_replay.json']
    for path in dependency:
        r=json.loads(Path(path).read_text());assert r.get('passed',r.get('source_replay',{}).get('passed'))
    assert all(j.is_highest(p) for p in old)
    Path(f'quartic_old_product_columns_{dim}.json').write_text(json.dumps({'dimension':dim,'product_highest_columns':[encode_polynomial(p) for p in old],'null_dependencies':dependency},indent=2)+'\n')
    if sector is None:
        print('Precomputed old product columns',dim,[len(p) for p in old],flush=True)
        return
    rank0=exact_rank(ideal);rank1=exact_rank(ideal+old)
    assert rank0==sector['ideal_rank_Q']
    expected=sector.get('kernel_multiplicity',sector['arc_multiplicity'])
    exhausted=rank1-rank0==sector['arc_multiplicity']
    result={'schema':'asterion/weight7-quartic-old-products/1','passed':rank1-rank0==expected,
       'dimension':dim,'ideal_rank_Q':rank0,'ideal_plus_old_products_rank_Q':rank1,
       'old_product_multiplicity':rank1-rank0,'kernel_multiplicity':expected if exhausted or 'kernel_multiplicity' in sector else None,
       'VOA_image_multiplicity':0 if exhausted else sector.get('VOA_image_multiplicity'),
       'new_primitive_multiplicity':0 if rank1-rank0==expected else None,
       'product_highest_columns':[encode_polynomial(p) for p in old],
       'null_dependencies':dependency}
    Path(f'quartic_old_products_{dim}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['dimension'],result['passed'],'kernel',result['kernel_multiplicity'],'old products',result['old_product_multiplicity'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('dimension',type=int);run(p.parse_args().dimension)
