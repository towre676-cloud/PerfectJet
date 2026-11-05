"""S4 jet-label frame certificate for the universal quartic C<=196 cutoff."""
from fractions import Fraction as Q
from itertools import product,permutations,combinations
from pathlib import Path
import json
from perfectjet.exact import nullspace,rref
from perfectjet.asterion_quartic_characters import _QuarticFreudenthal

MONOMIALS=tuple(e for e in product(range(4),repeat=4) if sum(e)==3)
POS={e:i for i,e in enumerate(MONOMIALS)}
PERMS=list(permutations(range(4)))
def add(a,b,c=1):return [x+c*y for x,y in zip(a,b)]
def scale(a,c):return [c*x for x in a]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def action(p,v):
    out=[Q(0)]*20
    for e,z in zip(MONOMIALS,v):
        f=[0]*4
        for i in range(4):f[p[i]]=e[i]
        out[POS[tuple(f)]]+=z
    return out
def cycle_type(p):
    seen=set();lengths=[]
    for i in range(4):
        if i in seen:continue
        j=i;n=0
        while j not in seen:seen.add(j);n+=1;j=p[j]
        lengths.append(n)
    return tuple(sorted(lengths,reverse=True))
TYPES=((1,1,1,1),(2,1,1),(2,2),(3,1),(4,))
CHARS={'31':(3,1,-1,0,-1),'22':(2,0,2,-1,0),'211':(3,-1,-1,0,1)}
def project(name,v):
    out=[Q(0)]*20;chi=CHARS[name]
    for p in PERMS:out=add(out,action(p,v),Q(chi[0]*chi[TYPES.index(cycle_type(p))],24))
    return out
def pair_vector(i,j):
    k,l=[a for a in range(4) if a not in (i,j)]
    out=[Q(0)]*20
    for a,b,c in ((i,i,1),(i,j,-2),(j,j,1)):
        for t,sgn in ((k,1),(l,-1)):
            e=[0]*4;e[a]+=1;e[b]+=1;e[t]+=1
            out[POS[tuple(e)]]+=c*sgn
    return out

def run():
    restrictions=[]
    for outside in range(4):
        for exponent in range(4):restrictions.append([Q(e[outside]==exponent) for e in MONOMIALS])
    U=nullspace(restrictions,20);assert len(U)==8
    r=pair_vector(0,1);r31=project('31',r);r211=project('211',r)
    assert r==add(r31,r211) and not any(project('22',r))
    n31=dot(r31,r31);n211=dot(r211,r211);assert n31 and n211
    # Positive S4-invariant metric with ||r31||²_H:||r211||²_H=13:1.
    s31=13/n31;s211=1/n211
    def H(v):return add(add(scale(project('31',v),s31),project('22',v)),project('211',v),s211)
    pairs=list(combinations(range(4),2));rs=[pair_vector(*p) for p in pairs]
    def frame(v):
        out=[Q(0)]*20
        for w in rs:out=add(out,w,dot(w,H(v))/dot(w,H(w)))
        return out
    def class_sum(v):
        out=[Q(0)]*20
        for i,j in pairs:
            p=list(range(4));p[i],p[j]=p[j],p[i]
            out=add(out,action(p,v))
        return out
    checks=[]
    for v in U:
        for name,eigen,ceigen in [('31',Q(13,7),2),('22',Q(0),0),('211',Q(1,7),-2)]:
            part=project(name,v)
            assert frame(part)==scale(part,eigen)
            assert class_sum(part)==scale(part,ceigen)
        assert v==add(add(project('31',v),project('22',v)),project('211',v))
    # Pair12 restriction on U has one-dimensional even kernel, spanned by r12.
    sw=list(range(4));sw[0],sw[1]=sw[1],sw[0]
    row_constraints=[]
    for i in range(20):row_constraints.append([action(sw,v)[i]-v[i] for v in U])
    for exponent in range(4):
        for third in range(4-exponent):
            fourth=3-exponent-third
            row_constraints.append([sum(z for e,z in zip(MONOMIALS,v) if e[0]+e[1]==exponent and e[2]==third and e[3]==fourth) for v in U])
    kernel=nullspace(row_constraints,len(U));assert len(kernel)==1
    actual=[sum(c*v[i] for c,v in zip(kernel[0],U)) for i in range(20)]
    ratio=next(actual[i]/r[i] for i in range(20) if r[i]);assert actual==scale(r,ratio)
    # Pair inequality: Omega<=-6(1+tau)+14 P_I, checked on all five g² types.
    pair_spectra=[('1',-60,1,0),('3875',-12,1,0),('27000',2,1,1),('248',-30,-1,0),('30380',0,-1,0)]
    assert all(o<=-6*(1+t)+14*p for _,o,t,p in pair_spectra)
    bounds={'31':168-12*2+28*Q(13,7),'22':168,'211':168+24+28*Q(1,7)}
    assert bounds=={'31':196,'22':168,'211':196}
    char=json.loads(Path('quartic_schur_receipt.json').read_text())
    engine=_QuarticFreudenthal();excluded=[];remaining=[]
    for row in char['weight7_length4_ambient']['irreducibles']:
        root=engine.root_coordinates(tuple(row['dynkin_labels']));c=engine.casimir(root)
        entry=dict(row,Casimir=c)
        (excluded if c>196 else remaining).append(entry)
    result={'schema':'asterion/weight7-quartic-Casimir-cutoff/1','passed':True,
            'jet_polynomial_monomials':MONOMIALS,'triple_diagonal_constraint_matrix':[[str(z) for z in r] for r in restrictions],
            'triple_diagonal_kernel_basis':[[str(z) for z in v] for v in U],
            'jet_kernel_dimension':8,'jet_kernel_S4_character':'S31+S22+S211',
            'pair_even_restriction_kernel_dimension':1,'pair_even_kernel_vector':[str(z) for z in r],
            'metric_weights':{'31':str(s31),'22':'1','211':str(s211)},
            'frame_eigenvalues':{'31':'13/7','22':'0','211':'1/7'},
            'transposition_class_sum':{'31':2,'22':0,'211':-2},
            'pair_spectra':pair_spectra,'Casimir_bounds':{k:int(v) for k,v in bounds.items()},
            'universal_quartic_Casimir_bound':196,'excluded_arc_types':excluded,'not_excluded_types':remaining,
            'dependency':'I27000*g=Sym3(g), proved by the pinned cubic-surjectivity certificate',
            'proof':'A dual arc tensor has jet labels in U. P_I(ij)T is supported on the '
                    'one-dimensional even restriction kernel r_ij, so sum||P_I T||² is bounded '
                    'by the jet-label rank-one frame. Summing the five-spectrum pair inequality '
                    'gives C_total<=168-12 sum(tau_ij)+28 sum(E_ij)<=196.'}
    Path('quartic_casimir_cutoff_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print({'passed':True,'bound':196,'excluded':[x['dimension'] for x in excluded]},flush=True)

if __name__=='__main__':run()
