"""Exact five-dimensional invariant calculation at weight7/length4."""
from fractions import Fraction as Q
from pathlib import Path
from math import factorial
import json
from quartic_adjoint_ideal import samples,form,bracket,add
from perfectjet.asterion_primitives import exact_rank,solve_combination

def ambient(x,y,z,w):
    return (form(x,x)*form(x,w),form(x,x)*form(y,z),
            form(x,y)*form(x,z),form(bracket(x,y),bracket(x,z)),
            form(x,y)*form(y,y))

def pair(x,y,z):
    return (6*form(x,x)*form(y,z)+372*form(x,y)*form(x,z)
            +31*form(bracket(x,y),bracket(x,z)))/Q(434)

def polar(a,b,y,z):return (pair(add(a,b),y,z)-pair(a,y,z)-pair(b,y,z))/2

def run():
    points=list(samples(16))
    cols=[{i:ambient(*p)[j] for i,p in enumerate(points)} for j in range(5)]
    assert exact_rank(cols)==5
    sources=((0,0,3),(0,1,2),(1,0,2),(1,1,1),(2,0,1),(3,0,0))
    images=[]
    for k,a,b in sources:
        value={i:factorial(k)*sum(polar(p[r],p[k-r],p[a],p[b]) for r in range(k+1))
               for i,p in enumerate(points)}
        images.append(solve_combination(value,cols))
    assert all(v is not None for v in images)
    vectors=[dict(enumerate(v)) for v in images]
    assert exact_rank(vectors)==4
    df0={1:Q(-8),2:Q(8),3:Q(-4)}
    assert exact_rank(vectors+[df0])==5
    dual=(0,-62,31,-360,0)
    assert all(sum(a*b for a,b in zip(v,dual))==0 for v in images)
    assert sum(df0.get(i,0)*v for i,v in enumerate(dual))==2184
    dependency=json.loads(Path('weight5_adjoint_source_replay.json').read_text())
    assert dependency['source_replay']['passed'] and dependency['source_replay']['lattice_replayed']
    assert dependency['quartic_product']['passed']
    assert dependency['quartic_product']['F0_equals_c_Y_modulo_ideal']=='91/155'
    assert json.loads(Path('weight6_quartic_source_replay.json').read_text())['passed']
    record={'schema':'asterion/weight7-quartic-singlet-ideal/1','passed':True,
       'ambient_basis':['Bxx Bxw','Bxx Byz','Bxy Bxz','B([x,y],[x,z])','Bxy Byy'],
       'ideal_sources':sources,'ideal_coordinate_matrix':[[str(z) for z in v] for v in images],
       'ambient_singlet_multiplicity':5,'ideal_rank_Q':4,'arc_singlet_multiplicity':1,
       'surviving_class':'D F0 = -8 Bxx Byz + 8 Bxy Bxz - 4 B([x,y],[x,z])',
       'quotient_functional':dual,'functional_value_on_DF0':2184,
       'full_null_dependency':'F0 is a product of the verified weight5 adjoint kernel class, '
           'up to an arc-ideal element; D preserves the kernel.',
       'kernel_singlet_multiplicity':1,'new_primitive_singlet_multiplicity':0,
       'samples':[[[[i,str(z)] for i,z in sorted(v.items())] for v in p] for p in points],
       'source_evaluation_columns':[[str(v.get(i,0)) for i in range(len(points))] for v in cols]}
    Path('quartic_singlet_ideal_receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    print({k:record[k] for k in ('passed','ideal_rank_Q','arc_singlet_multiplicity','kernel_singlet_multiplicity','new_primitive_singlet_multiplicity')})

if __name__=='__main__':run()
