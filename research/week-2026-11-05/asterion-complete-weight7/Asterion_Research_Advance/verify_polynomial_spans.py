"""Compact exact rank certificates for large sparse highest-polynomial spans."""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json
from perfectjet.asterion_primitives import decode_polynomial
from perfectjet.exact import rref
from verify_quartic_small_matrices import bareiss_rank

def select(vectors):
    pivots={};chosen=[];keys=[]
    for n,v in enumerate(vectors):
        current={k:Q(z) for k,z in v.items() if z}
        while current:
            key=min(current)
            if key not in pivots:
                z=current[key];pivots[key]={k:x/z for k,x in current.items()}
                chosen.append(n);keys.append(key);break
            z=current[key]
            for k,w in pivots[key].items():
                value=current.get(k,0)-z*w
                if value:current[k]=value
                else:current.pop(k,None)
    return chosen,keys

def certify(vectors):
    chosen,keys=select(vectors);basis=[vectors[i] for i in chosen];rank=len(basis)
    minor=[[Q(v.get(k,0)) for v in basis] for k in keys]
    assert bareiss_rank(minor)==rank
    aug=[row+[Q(i==j) for j in range(rank)] for i,row in enumerate(minor)]
    inverse=rref(aug)[0];assert all(row[i]==1 for i,row in enumerate(inverse))
    inverse=[row[rank:] for row in inverse]
    coordinates=[]
    for v in vectors:
        c=[sum(z*Q(v.get(k,0)) for z,k in zip(row,keys)) for row in inverse]
        actual={}
        for z,b in zip(c,basis):
            if not z:continue
            for k,w in b.items():
                value=actual.get(k,0)+z*w
                if value:actual[k]=value
                else:actual.pop(k,None)
        assert actual=={k:Q(z) for k,z in v.items() if z}
        coordinates.append(c)
    return {'rank':rank,'basis_column_indices':chosen,
            'pivot_monomials':[[list(x) for x in k] for k in keys],
            'invertible_minor':[[str(z) for z in row] for row in minor],
            'all_column_coordinates':[[str(z) for z in row] for row in coordinates],
            'every_sparse_recombination_checked':True}

def run(dim):
    p=Path(f'quartic_ideal_only_{dim}.json')
    if not p.exists():p=Path(f'quartic_zero_arc_{dim}.json')
    if not p.exists():p=Path(f'quartic_full_{dim}.json')
    r=json.loads(p.read_text());ideal=[decode_polynomial(v) for v in r['ideal_highest_columns']]
    a=certify(ideal);assert a['rank']==r['ideal_rank_Q']
    products=Path(f'quartic_old_products_{dim}.json');b=None
    if products.exists():
        q=json.loads(products.read_text());old=[decode_polynomial(v) for v in q['product_highest_columns']]
        b=certify(ideal+old)
        assert b['rank']-a['rank']==q['old_product_multiplicity']
    result={'passed':True,'dimension':dim,'source_file':str(p),'ideal':a,'ideal_plus_old_products':b}
    Path(f'quartic_span_certificate_{dim}.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Independent sparse span',dim,a['rank'],b['rank'] if b else None,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('dimension',type=int);run(p.parse_args().dimension)
