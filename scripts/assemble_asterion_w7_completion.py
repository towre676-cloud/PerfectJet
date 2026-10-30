"""Assemble standard-format representatives and the exact rank-bound argument."""
import gzip
import json
from pathlib import Path
from perfectjet.asterion import source_digests
from perfectjet.asterion_primitives import (
    JetAlgebra, decode_polynomial, encode_polynomial, digest, load_certificates,
)
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'results/asterion-primitives'

def read(name):
    path=FOLDER/name
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())


def main():
    records={}
    ideal=read('w7-adjoint-ideal.json.gz')
    for dimension in (1,248):
        bound=read(f'w7-{dimension}-projected-rank.json.gz')
        h=bound['top_highest']; lower=bound['lower_highest']; rank=bound['projected_rank_Q']
        ideal_rank=0 if dimension==1 else ideal['ideal_rank_Q']
        known=0 if dimension==1 else ideal['ideal_plus_D2P_rank_Q']-ideal_rank
        assert h+lower-rank==ideal_rank+known
        reps=[]
        if dimension==248:
            encoded={'symbol':ideal['derivative_symbol'],'correction':ideal['derivative_correction']}
            encoded.update(symbol_terms=len(encoded['symbol']),correction_terms=len(encoded['correction']))
            encoded['sha256']=digest([encoded['symbol'],encoded['correction']])
            reps=[encoded]
        records[f'w7-{dimension}']={
            'label':f'w7-{dimension}','conformal_weight':7,'li_degree':4,'current_length':3,
            'highest_weight_root_coordinates': [0]*8 if dimension==1 else [2,4,6,5,4,3,2,3],
            'weyl_dimension':dimension,'top_shapes':[[0,0,4],[0,1,3],[0,2,2],[1,1,2]],
            'top_monomial_columns':bound['top_columns'],'polynomial_highest_vectors':h,
            'lower_length_highest_vectors':lower,'ideal_highest_rank':ideal_rank,
            'arc_multiplicity':h-ideal_rank,'lattice_null_dimension':h+lower-rank,
            'projected_lattice_rank_Q':rank,'kernel_multiplicity':known,
            'new_primitive_multiplicity':0,'representatives':reps,
            'class':None if dimension==1 else 'D^2 P_248 from weight five',
            'completeness_proof':'Projected rank bounds full rank from below; independent ideal null lifts and the translated weight-five null lift attain the resulting nullity bound. Their symbols are independent, so the projection of the full null space has the same dimension.',
        }
    result={
        'schema':'perfectjet/asterion-w7-length-three-completion/1',
        'source_sha256':source_digests(),'sectors':records,
        'complete_weight_seven_length_three_kernel':{'248':1,'3875':1,'30380':1,'147250':1},
        'kernel_dimension':181753,'new_length_three_primitive_multiplicity':0,
        'previous_sectors':'length-three-boundary.json; seven previously certified sectors reused',
        'scope':'Completes weight-seven length three only. Weight-seven length four and longer, the full weight-seven kernel, and all-weight generator assertions remain open.',
    }
    path=ROOT/'src/perfectjet/resources/asterion_w7_certificates.json'
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (FOLDER/'w7-completion-summary.json').write_text(json.dumps(
        {k:v for k,v in result.items() if k!='sectors'}|{'sector_dimensions':{
            key:{k:v for k,v in row.items() if k not in ('representatives','completeness_proof')}
            for key,row in records.items()}},indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('Assembled weight-seven length-three completion; no full-weight-seven claim.')


if __name__=='__main__':
    main()
