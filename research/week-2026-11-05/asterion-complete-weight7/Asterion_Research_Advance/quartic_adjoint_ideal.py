"""Small covariant-space computation of the weight-seven quartic adjoint ideal.

Exact evaluations become a proof only after exhibiting an injective
evaluation map on the complete character-certified source multiplicity space.
"""
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import json, random
from perfectjet.asterion_primitives import JetAlgebra, exact_rank, solve_combination

J=JetAlgebra()
def add(a,b,scale=1):
    out=dict(a)
    for i,z in b.items():
        v=out.get(i,0)+scale*z
        if v:out[i]=v
        else:out.pop(i,None)
    return out
def scale(a,c):return {i:z*c for i,z in a.items() if z*c}
def bracket(a,b):
    out={}
    for i,z in a.items():
        for j,w in b.items():
            for k,c in J.bracket(i,j):
                v=out.get(k,0)+z*w*c
                if v:out[k]=v
                else:out.pop(k,None)
    return out
def form(a,b):return sum(z*w*J.form(i,j) for i,z in a.items() for j,w in b.items())

NAMES=('Bxx[y,z]','Bxy[x,z]','Bxz[x,y]','x B(x,[y,z])',
       '[x,[x,[y,z]]]','[x,[y,[x,z]]]','[y,[x,[x,z]]]')
def covariants(x,y,z):
    yz=bracket(y,z);xz=bracket(x,z);xy=bracket(x,y)
    return (scale(yz,form(x,x)),scale(xz,form(x,y)),scale(xy,form(x,z)),
            scale(x,form(x,yz)),bracket(x,bracket(x,yz)),
            bracket(x,bracket(y,xz)),bracket(y,bracket(x,xz)))

def polar(a,b,y,z):
    ab=covariants(add(a,b),y,z);aa=covariants(a,y,z);bb=covariants(b,y,z)
    return tuple(scale(add(add(v,u,-1),w,-1),Q(1,2)) for v,u,w in zip(ab,aa,bb))

def projected(x,y,z):
    """Apply P_I=(372 Id+31 Omega+6 |C><C|)/434 in the repeated x pair."""
    base=covariants(x,y,z);omega=[{} for _ in range(7)];trace=[{} for _ in range(7)]
    for a in range(248):
        ta={a:1};dual=J.dual(a)
        ax=bracket(ta,x);bx=bracket(dual,x)
        if ax and bx:
            for i,v in enumerate(polar(ax,bx,y,z)):omega[i]=add(omega[i],v)
        for i,v in enumerate(polar(ta,dual,y,z)):trace[i]=add(trace[i],v)
    return tuple(scale(add(add(scale(base[i],372),omega[i],31),trace[i],6*form(x,x)),Q(1,434)) for i in range(7))

def samples(n=12):
    rng=random.Random(20261104)
    a=J.algebra.simple_roots[0]
    b=next(b for b in J.algebra.simple_roots if tuple(x+y for x,y in zip(a,b)) in J.algebra.root_index)
    c=tuple(x+y for x,y in zip(a,b))
    roots=[a,b,c]+[tuple(-x for x in r) for r in (a,b,c)]
    pool=list(range(8))+[J.algebra.root_index[r] for r in roots]
    for _ in range(n):
        yield tuple({i:rng.choice((-2,-1,1,2)) for i in rng.sample(pool,8)} for _ in range(4))

def flatten(values):
    return [{(sample,index):z for sample,vs in enumerate(values) for index,z in vs[i].items()}
            for i in range(len(values[0]))]

def ambient(x,y,z,w):
    xx=form(x,x);yy=form(y,y)
    return (scale(bracket(x,w),xx),bracket(x,bracket(x,bracket(x,w))),
            *covariants(x,y,z),scale(bracket(y,x),yy),bracket(y,bracket(y,bracket(y,x))))

SOURCES=((0,0,3),(0,1,2),(1,0,2),(1,1,1),(2,0,1),(3,0,0))
def run():
    points=list(samples())
    cvalues=[covariants(x,y,z) for x,y,z,w in points]
    cols=flatten(cvalues)
    assert exact_rank(cols)==7
    print('Seven complete repeated-pair covariants independent',flush=True)
    pvalues=[]
    for s,(x,y,z,w) in enumerate(points):
        pvalues.append(projected(x,y,z))
        print('projected sample',s+1,flush=True)
    pcols=flatten(pvalues)
    projector=[solve_combination(v,cols) for v in pcols]
    assert all(v is not None for v in projector)
    # Rows describe the projected covariant in the seven original covariants.
    assert all(sum(projector[i][k]*projector[k][j] for k in range(7))==projector[i][j] for i in range(7) for j in range(7))
    print('Exact pair projector recovered; rank',exact_rank([dict(enumerate(v)) for v in projector]),flush=True)
    acol=flatten([ambient(*p) for p in points])
    assert exact_rank(acol)==11
    # Each ideal source is D^k(I) times two free currents of orders a,b.
    # D^k q(x0,x0)=k! sum_(r+s=k) q(xr,xs).
    images=[]
    for k,a,b in SOURCES:
        for i in range(7):
            value={}
            for sample,xs in enumerate(points):
                out={}
                for r in range(k+1):
                    vals=polar(xs[r],xs[k-r],xs[a],xs[b])
                    for j,v in enumerate(vals):out=add(out,v,factorial(k)*projector[i][j])
                for index,z in out.items():value[sample,index]=z
            images.append(value)
    coordinates=[solve_combination(v,acol) for v in images]
    assert all(v is not None for v in coordinates)
    rank=exact_rank([dict(enumerate(v)) for v in coordinates])
    print('Ambient adjoint multiplicity11; ideal rank',rank,'arc multiplicity',11-rank,flush=True)
    enc=lambda v:[str(z) for z in v]
    record={'schema':'asterion/weight7-quartic-adjoint-ideal/1','passed':True,
            'ambient_adjoint_multiplicity':11,'pair_symmetric_adjoint_multiplicity':7,
            'pair_covariant_names':NAMES,'pair_projector':list(map(enc,projector)),
            'ideal_sources':SOURCES,'ideal_coordinate_matrix':list(map(enc,coordinates)),
            'ideal_rank_Q':rank,'arc_adjoint_multiplicity':11-rank,
            'samples':[[[[i,str(z)] for i,z in sorted(v.items())] for v in point] for point in points],
            'ambient_covariant_names':['Bxx[x,w]','[x,[x,[x,w]]]']+list(NAMES)+['Byy[y,x]','[y,[y,[y,x]]]'],
            'ambient_evaluation_columns':[[[s,i,str(z)] for (s,i),z in sorted(v.items())] for v in acol],
            'pair_covariant_evaluation_columns':[[[s,i,str(z)] for (s,i),z in sorted(v.items())] for v in cols],
            'pair_projected_evaluation_columns':[[[s,i,str(z)] for (s,i),z in sorted(v.items())] for v in pcols],
            'ideal_evaluation_columns':[[[s,i,str(z)] for (s,i),z in sorted(v.items())] for v in images],
            'proof_scope':'Exact arc-ideal adjoint multiplicity; no VOA rank or primitive quotient computed.',
            'VOA_rank_computed':False,'primitive_quotient_computed':False}
    Path('quartic_adjoint_ideal_receipt.json').write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':run()
