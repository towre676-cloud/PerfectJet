"""Complete quartic30380 covariants using commuting output probes.

Commuting u,v give u wedge v in ker(bracket)=V30380. This evaluates
the30380 output projection without constructing a30380-dimensional array.
"""
from fractions import Fraction as Q
from itertools import permutations
from math import factorial
from pathlib import Path
import json
from quartic_adjoint_ideal import J,add,bracket,form,samples,SOURCES
from perfectjet.exact import rref
from perfectjet.asterion_primitives import solve_combination,exact_rank

def wedge(a,b,u,v):return Q(form(a,u)*form(b,v)-form(a,v)*form(b,u),2)

def word_pairs(shape):
    return sorted({min(p,p[::-1]) for p in set(permutations(shape)) if p!=p[::-1]})
MIDDLE_WORDS=word_pairs((0,0,1,2))
TRIPLE_WORDS=word_pairs((0,0,0,1))

def operators(variables,words,u,v):
    cache={():v}
    def act(w):
        if w not in cache:cache[w]=bracket(variables[w[0]],act(w[1:]))
        return cache[w]
    return [form(u,add(act(w),act(w[::-1]),-1)) for w in words]

def middle(x,y,z,u,v):
    xy=bracket(x,y);xz=bracket(x,z);yz=bracket(y,z)
    return [form(x,z)*wedge(x,y,u,v),form(x,y)*wedge(x,z,u,v),
            form(x,x)*wedge(y,z,u,v),wedge(xy,xz,u,v),
            wedge(x,bracket(x,yz),u,v),wedge(x,bracket(y,xz),u,v),
            wedge(y,bracket(x,xz),u,v),wedge(z,bracket(x,xy),u,v),
            *operators((x,y,z),MIDDLE_WORDS,u,v)]

def triple(x,w,u,v):
    return [form(x,x)*wedge(x,w,u,v),wedge(x,bracket(x,bracket(x,w)),u,v),
            *operators((x,w),TRIPLE_WORDS,u,v)]

def output_probes():
    a=J.algebra.simple_roots[0]
    b=next(b for b in J.algebra.simple_roots if tuple(x+y for x,y in zip(a,b)) in J.algebra.root_index)
    c=tuple(x+y for x,y in zip(a,b))
    u,v,w=[J.algebra.root_index[r] for r in (a,b,c)]
    pairs=[(0,1),(0,2),(1,3),(u,w),(v,w),(u,J.opposite[v]),(J.opposite[u],v)]
    for a,b in pairs:assert not J.bracket(a,b) and a!=b
    return pairs

def columns(values):return [dict(enumerate(v)) for v in zip(*values)]
def select(values,n):
    _,p=rref(values)
    assert len(p)==n,(len(p),n)
    return p

def run():
    points=list(samples(14));probes=output_probes()
    rows=[(s,p) for s in range(len(points)) for p in range(len(probes))]
    mv=[];tv=[]
    for s,p in rows:
        x,y,z,w=points[s];a,b=probes[p];u,v={a:1},{b:1}
        mv.append(middle(x,y,z,u,v));tv.append(triple(x,w,u,v))
    print('Candidate middle rank',exact_rank(columns(mv)),'triple',exact_rank(columns(tv)),flush=True)
    mi=select(mv,11);ti=select(tv,3)
    paircols=columns([[v[i] for i in mi] for v in mv])
    _,row_pivots=rref([[v[r] for r in range(len(rows))] for v in paircols])
    assert len(row_pivots)==11
    selected_rows=[rows[i] for i in row_pivots]
    def f(x,y,z,u,v):
        values=middle(x,y,z,u,v);return [values[i] for i in mi]
    def pol(a,b,y,z,u,v):
        ab=f(add(a,b),y,z,u,v);aa=f(a,y,z,u,v);bb=f(b,y,z,u,v)
        return [Q(x-y-z,2) for x,y,z in zip(ab,aa,bb)]
    projected=[]
    for row,(s,p) in enumerate(selected_rows):
        x,y,z,w=points[s];u,v=[{i:1} for i in probes[p]]
        base=f(x,y,z,u,v);omega=[Q(0)]*11;trace=[Q(0)]*11
        for a in range(248):
            ta={a:1};dual=J.dual(a);ax=bracket(ta,x);bx=bracket(dual,x)
            if ax and bx:
                for i,value in enumerate(pol(ax,bx,y,z,u,v)):omega[i]+=value
            for i,value in enumerate(pol(ta,dual,y,z,u,v)):trace[i]+=value
        projected.append([(372*b+31*o+6*form(x,x)*t)/434 for b,o,t in zip(base,omega,trace)])
        print('30380 projector row',row+1,flush=True)
    pcols=columns(projected)
    pc=[{i:col[r] for i,r in enumerate(row_pivots)} for col in paircols]
    projector=[solve_combination(v,pc) for v in pcols]
    assert all(v is not None for v in projector)
    assert all(sum(projector[i][k]*projector[k][j] for k in range(11))==projector[i][j] for i in range(11) for j in range(11))
    ambient=[]
    for s,p in rows:
        x,y,z,w=points[s];u,v=[{i:1} for i in probes[p]]
        a=triple(x,w,u,v);b=middle(x,y,z,u,v);c=triple(y,x,u,v)
        ambient.append([a[i] for i in ti]+[b[i] for i in mi]+[c[i] for i in ti])
    acols=columns(ambient);assert exact_rank(acols)==17
    images=[]
    for k,a,b in SOURCES:
        evaluated=[]
        for s,p in rows:
            xs=points[s];u,v=[{i:1} for i in probes[p]]
            vals=[Q(0)]*11
            for r in range(k+1):
                polar=pol(xs[r],xs[k-r],xs[a],xs[b],u,v)
                for i in range(11):vals[i]+=factorial(k)*sum(c*z for c,z in zip(projector[i],polar))
            evaluated.append(vals)
        images.extend(columns(evaluated))
    coords=[solve_combination(v,acols) for v in images];assert all(v is not None for v in coords)
    rank=exact_rank([dict(enumerate(v)) for v in coords])
    print('30380 source17 ideal',rank,'arc',17-rank,flush=True)
    record={'schema':'asterion/weight7-quartic-30380-ideal/1','passed':True,
            'ambient_multiplicity':17,'pair_symmetric_multiplicity':11,
            'middle_candidate_indices':mi,'triple_candidate_indices':ti,
            'middle_operator_words':MIDDLE_WORDS,'triple_operator_words':TRIPLE_WORDS,
            'source_evaluation_columns':[[str(v.get(i,0)) for i in range(len(rows))] for v in acols],
            'pair_evaluation_columns':[[str(v.get(i,0)) for i in range(len(rows))] for v in paircols],
            'projector_evaluation_row_indices':row_pivots,
            'pair_projected_evaluation_columns':[[str(v[i]) for i in range(11)] for v in pcols],
            'pair_projector':[[str(z) for z in v] for v in projector],
            'ideal_coordinate_matrix':[[str(z) for z in v] for v in coords],
            'ideal_evaluation_columns':[[str(v.get(i,0)) for i in range(len(rows))] for v in images],
            'ideal_rank_Q':rank,'arc_multiplicity':17-rank,
            'samples':[[[[i,str(z)] for i,z in sorted(v.items())] for v in pt] for pt in points],
            'probes':probes,'evaluation_row_labels':rows,'VOA_rank_computed':False,'primitive_quotient_computed':False}
    Path('quartic_30380_ideal_receipt.json').write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':run()
