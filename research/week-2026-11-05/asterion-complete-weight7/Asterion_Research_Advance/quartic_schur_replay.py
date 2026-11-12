"""Exact four-adjoint Schur characters and weight-seven quartic source.

No imported exceptional tensor table. Uses the pinned PerfectJet E8 root,
Weyl dimension and Freudenthal routines. Characters are independent of
any claimed arc-ideal rank or VOA evaluation rank.
"""
from fractions import Fraction as Q
from math import prod
from pathlib import Path
import json
from perfectjet.asterion_quartic_characters import (
    _QuarticFreudenthal, _plus, _minus, _adams_coefficient, _decompose)

PARTITIONS={'4':(4,), '31':(3,1), '22':(2,2), '211':(2,1,1), '1111':(1,1,1,1)}
S4_CHARACTERS={'4':(1,1,1,1,1), '31':(3,1,-1,0,-1),
               '22':(2,0,2,-1,0), '211':(3,-1,-1,0,1),
               '1111':(1,-1,1,1,-1)}
CLASS_SIZES=(1,6,3,8,6)

def schur_dimension(partition,n=248):
    result=Q(1)
    for i,length in enumerate(partition):
        for j in range(length):
            hook=length-j+sum(x>j for x in partition[i+1:])
            result*=Q(n+j-i,hook)
    assert result.denominator==1
    return int(result)

def run():
    engine=_QuarticFreudenthal(); zero=(0,)*8
    adjoint={zero:8,**{r:1 for r in engine.algebra.roots}}
    square={}
    for a,m in adjoint.items():
        for b,n in adjoint.items():
            w=_plus(a,b); square[w]=square.get(w,0)+m*n
    weights=engine.dominant_weights(32)
    chars={p:{} for p in PARTITIONS}; rows=[]
    for labels,root,norm in weights:
        terms=(sum(m*square.get(_minus(root,a),0) for a,m in square.items()),
               sum(m*square.get(_minus(root,a,2),0) for a,m in adjoint.items()),
               _adams_coefficient(square,root,2),
               sum(m*adjoint.get(_minus(root,a,3),0) for a,m in adjoint.items()),
               _adams_coefficient(adjoint,root,4))
        for p,chi in S4_CHARACTERS.items():
            value=Q(sum(s*c*t for s,c,t in zip(CLASS_SIZES,chi,terms)),24)
            assert value.denominator==1 and value>=0
            chars[p][root]=int(value)
        rows.append({'labels':labels,'norm':norm,'power_sum_coefficients':terms})
    results={p:_decompose(engine,weights,chars[p],schur_dimension(PARTITIONS[p])) for p in PARTITIONS}
    assert all(r['passed'] for r in results.values())
    # Schur-Weyl dimension check for the complete fourth tensor power.
    assert sum(S4_CHARACTERS[p][0]*r['reconstructed_dimension'] for p,r in results.items())==248**4
    def combine(coefficients):
        out={}
        for p,c in coefficients.items():
            for row in results[p]['irreducibles']:
                labels=tuple(row['dynkin_labels'])
                rec=out.setdefault(labels,dict(row,multiplicity=0))
                rec['multiplicity']+=c*row['multiplicity']
        return sorted(out.values(),key=lambda x:(x['dimension'],x['dynkin_labels']))
    ambient=combine({'4':3,'31':4,'22':1,'211':1})
    # Only a character of this auxiliary Schur sum, not an arc dimension.
    reduced=combine({'31':1,'22':1,'211':1})
    dim=sum(x['dimension']*x['multiplicity'] for x in ambient)
    assert dim==2*248*(248*249*250//6)+248**2*(248*249//2)
    r={'schema':'asterion/quartic-schur-replay/1','passed':True,
       'source_commit':'9b69eab9beff3011bc6216b30a460c2c6d0e97be',
       'method':'S4 Frobenius characters; 241 distinct adjoint weights; exact Freudenthal subtraction; hook dimensions',
       'norm_bound':32,'S4_class_order':['1^4','2,1,1','2,2','3,1','4'],
       'S4_characters':S4_CHARACTERS,'class_sizes':CLASS_SIZES,
       'Schur_components':results,'power_sum_weight_rows':rows,
       'weight7_length4_ambient':{'jet_shapes':[[3,0,0,0],[2,1,0,0],[1,1,1,0]],
           'Schur_coefficients':{'4':3,'31':4,'22':1,'211':1},
           'irreducibles':ambient,'dimension':dim},
       'auxiliary_S31_plus_S22_plus_S211':{'irreducibles':reduced,
           'arc_upper_bound_claim':False},
       'arc_ideal_rank_computed':False,'VOA_rank_computed':False,
       'primitive_quotient_computed':False,
       'scope':'complete polynomial source characters only; no arc quotient or VOA kernel conclusion'}
    Path('quartic_schur_receipt.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'passed':True,'ambient_dimension':dim,
         'ambient_sectors':len(ambient),'Schur_dimensions':{p:v['reconstructed_dimension'] for p,v in results.items()},
         'small_sector_multiplicities':[x for x in ambient if x['dimension']<=30380]},indent=2),flush=True)

if __name__=='__main__':run()
