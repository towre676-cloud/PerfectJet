"""Exact R3875 covariants: compute ideal maps in small multiplicity spaces."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial
import json
from quartic_adjoint_ideal import J,add,scale,bracket,form,samples,SOURCES
from perfectjet.asterion_primitives import omega_pair,_contraction,exact_rank,solve_combination

PAIR_NAMES=('P_R(x sym x) Byz','P_R(x sym y) Bxz','P_R(x sym z) Bxy',
            'P_R(y sym z) Bxx','P_R([x,y] sym [x,z])',
            'P_R(x sym [x,[y,z]])','P_R(x sym [y,[x,z]])',
            'P_R(y sym [x,[x,z]])','P_R(z sym [x,[x,y]])')
TRIPLE_NAMES=('P_R(x sym x) Bxw','P_R(x sym w) Bxx','P_R(x sym [x,[x,w]])')

def sym(a,b):
    out={}
    for i,x in a.items():
        for j,y in b.items():
            key=tuple(sorted((i,j)));out[key]=out.get(key,0)+x*y
    return {k:z for k,z in out.items() if z}

def covariants(x,y,z):
    xy=bracket(x,y);xz=bracket(x,z);yz=bracket(y,z)
    return (scale(sym(x,x),form(y,z)),scale(sym(x,y),form(x,z)),
            scale(sym(x,z),form(x,y)),scale(sym(y,z),form(x,x)),sym(xy,xz),
            sym(x,bracket(x,yz)),sym(x,bracket(y,xz)),
            sym(y,bracket(x,xz)),sym(z,bracket(x,xy)))

def triple(x,w):
    return (scale(sym(x,x),form(x,w)),scale(sym(x,w),form(x,x)),
            sym(x,bracket(x,bracket(x,w))))

def polar(a,b,y,z):
    ab=covariants(add(a,b),y,z);aa=covariants(a,y,z);bb=covariants(b,y,z)
    return tuple(scale(add(add(v,u,-1),w,-1),Q(1,2)) for v,u,w in zip(ab,aa,bb))

def projected(x,y,z):
    base=covariants(x,y,z);omega=[{} for _ in base];trace=[{} for _ in base]
    for a in range(248):
        ta={a:1};dual=J.dual(a);ax=bracket(ta,x);bx=bracket(dual,x)
        if ax and bx:
            for i,v in enumerate(polar(ax,bx,y,z)):omega[i]=add(omega[i],v)
        for i,v in enumerate(polar(ta,dual,y,z)):trace[i]=add(trace[i],v)
    return tuple(scale(add(add(scale(base[i],372),omega[i],31),trace[i],6*form(x,x)),Q(1,434)) for i in range(len(base)))

def dual_tensor(t):
    out={}
    for (a,b),z in t.items():
        left=[(i,J.form(i,a)) for i in range(248) if J.form(i,a)]
        right=[(j,J.form(j,b)) for j in range(248) if J.form(j,b)]
        for i,x in left:
            for j,y in right:
                key=tuple(sorted((i,j)))
                out[key]=out.get(key,0)+z*x*y/(2 if i!=j else 1)
    return {k:z for k,z in out.items() if z}

def probe_functional(a,b):
    c={tuple(i for i,r in m):z for m,z in _contraction(J,None,0,0).items()}
    out=scale({tuple(sorted((a,b))):Q(1)},2)
    out=add(out,omega_pair(J,a,b),-1)
    out=add(out,c,-Q(J.form(a,b),4))
    return dual_tensor(scale(out,Q(1,14)))

def probes():
    a=J.algebra.simple_roots[0]
    b=next(b for b in J.algebra.simple_roots if tuple(x+y for x,y in zip(a,b)) in J.algebra.root_index)
    u,v=[J.algebra.root_index[r] for r in (a,b)]
    return [(0,0),(0,1),(1,2),(u,J.opposite[u]),(u,v),(0,u),(u,J.opposite[v])]

def flatten(values,functionals):
    return [{(s,p):sum(t.get(key,0)*z for key,z in f.items())
             for s,vs in enumerate(values) for p,f in enumerate(functionals) if (t:=vs[i]) is not None}
            for i in range(len(values[0]))]

def run():
    pts=list(samples(12));ps=probes();funcs=[probe_functional(*p) for p in ps]
    vals=[covariants(x,y,z) for x,y,z,w in pts]
    cols=flatten(vals,funcs)
    print('Repeated-pair covariance rank',exact_rank(cols),'expected9',flush=True)
    assert exact_rank(cols)==9
    av=[(*triple(x,w),*covariants(x,y,z),*triple(y,x)) for x,y,z,w in pts]
    acols=flatten(av,funcs)
    print('Ambient rank',exact_rank(acols),'expected15',flush=True)
    assert exact_rank(acols)==15
    pvals=[]
    for i,(x,y,z,w) in enumerate(pts):
        pvals.append(projected(x,y,z));print('3875 projected sample',i+1,flush=True)
    pcols=flatten(pvals,funcs)
    projector=[solve_combination(v,cols) for v in pcols]
    assert all(v is not None for v in projector)
    assert all(sum(projector[i][k]*projector[k][j] for k in range(9))==projector[i][j] for i in range(9) for j in range(9))
    print('Input I projector rank',exact_rank([dict(enumerate(v)) for v in projector]),flush=True)
    images=[]
    for k,a,b in SOURCES:
        samplevalues=[]
        for xs in pts:
            sums=[{} for _ in range(9)]
            for r in range(k+1):
                polars=polar(xs[r],xs[k-r],xs[a],xs[b])
                for i in range(9):
                    for j,t in enumerate(polars):sums[i]=add(sums[i],t,factorial(k)*projector[i][j])
            samplevalues.append(sums)
        images.extend(flatten(samplevalues,funcs))
    coords=[solve_combination(v,acols) for v in images]
    assert all(v is not None for v in coords)
    rank=exact_rank([dict(enumerate(v)) for v in coords])
    print('3875 ideal rank',rank,'arc multiplicity',15-rank,flush=True)
    enc=lambda vec:[str(z) for z in vec]
    def columns(vs):return [[[s,p,str(z)] for (s,p),z in sorted(v.items())] for v in vs]
    record={'schema':'asterion/weight7-quartic-3875-ideal/1','passed':True,
            'ambient_multiplicity':15,'pair_symmetric_multiplicity':9,
            'pair_covariant_names':PAIR_NAMES,'triple_covariant_names':TRIPLE_NAMES,
            'pair_projector':list(map(enc,projector)),'ideal_sources':SOURCES,
            'ideal_coordinate_matrix':list(map(enc,coords)),'ideal_rank_Q':rank,
            'arc_multiplicity':15-rank,'VOA_rank_computed':False,'primitive_quotient_computed':False,
            'samples':[[[[i,str(z)] for i,z in sorted(v.items())] for v in pt] for pt in pts],
            'probes':ps,'source_evaluation_columns':columns(acols),
            'pair_evaluation_columns':columns(cols),'pair_projected_evaluation_columns':columns(pcols),
            'ideal_evaluation_columns':columns(images)}
    Path('quartic_3875_ideal_receipt.json').write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':run()
