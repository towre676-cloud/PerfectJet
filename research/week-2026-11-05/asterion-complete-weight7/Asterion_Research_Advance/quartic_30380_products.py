"""Product tests for the two weight-seven quartic30380 arc copies."""
from fractions import Fraction as Q
from pathlib import Path
import json
from quartic_adjoint_ideal import add,scale,bracket,form
from quartic_30380_ideal import wedge
from perfectjet.asterion_primitives import solve_combination,exact_rank

def rpair(a,b,u,v):
    # <P3875(a sym b),u sym v>, root-length-two normalization.
    identity=form(a,u)*form(b,v)+form(a,v)*form(b,u)
    omega=(form(bracket(a,u),bracket(b,v))+form(bracket(a,v),bracket(b,u)))/Q(2)
    return (identity-omega-form(a,b)*form(u,v)/Q(4))/14

def p248(x,y,z):return add(add(scale(x,20*form(x,z)),x,-21*form(y,y)),y,-12*form(x,y))

def q_product(x,y,z,u,v):
    # Anticommutator ad_z * Q + Q * ad_z, Q=2 P3875(x sym [x,y]).
    # It is B-skew; commuting probes remove its adjoint component.
    xy=bracket(x,y)
    return -2*rpair(x,xy,bracket(z,u),v)+2*rpair(x,xy,u,bracket(z,v))

def q_derivative_product(xs,k,u,v):
    x,y,z,w=xs;xy=bracket(x,y);xz=bracket(x,z)
    terms=([(2,x,xy)] if k==0 else [(2,y,xy),(4,x,xz)] if k==1 else
           [(4,z,xy),(8,y,xz),(4,x,bracket(y,z)),(12,x,bracket(x,w))])
    a=xs[2-k]
    return sum(c*(-rpair(b,d,bracket(a,u),v)+rpair(b,d,u,bracket(a,v))) for c,b,d in terms)

def p30380(xs,u,v):
    def A(r,s,t):
        return form(bracket(u,xs[t]),xs[r])*form(v,xs[s])-form(bracket(v,xs[t]),xs[r])*form(u,xs[s])
    def B(r,s,t):
        return form(bracket(bracket(u,xs[s]),bracket(v,xs[t])),xs[r])-form(bracket(bracket(v,xs[s]),bracket(u,xs[t])),xs[r])
    return 6*A(0,0,3)+2*A(0,1,2)+12*A(0,2,1)+10*A(1,0,2)+2*B(0,1,2)-Q(5,6)*B(1,1,1)

def run():
    r=json.loads(Path('quartic_30380_ideal_receipt.json').read_text())
    points=[[{i:Q(z) for i,z in v} for v in p] for p in r['samples']]
    cols=[dict(enumerate(map(Q,col))) for col in r['source_evaluation_columns']]
    ideal=[{i:Q(z) for i,z in enumerate(v) if Q(z)} for v in r['ideal_coordinate_matrix']]
    values=[{} for _ in range(5)]
    for row,(s,p) in enumerate(r['evaluation_row_labels']):
        x,y,z,w=points[s];u,v=[{i:1} for i in r['probes'][p]]
        values[0][row]=wedge(y,p248(x,y,z),u,v)
        for k in range(3):values[1+k][row]=q_derivative_product(points[s],k,u,v)
        values[4][row]=-p30380(points[s],bracket(x,u),v)-p30380(points[s],u,bracket(x,v))
    coords=[solve_combination(v,cols) for v in values]
    assert all(v is not None for v in coords)
    products=[dict(enumerate(v)) for v in coords]
    ranks=[exact_rank(ideal)]+[exact_rank(ideal+[p]) for p in products]+[exact_rank(ideal+products)]
    print('30380 product ranks:',ranks,flush=True)
    record={'schema':'asterion/weight7-quartic-30380-products/1',
            'passed':ranks[-1]==17,
            'product_classes':['P30380(y wedge P248)','P30380{ad_z,Q}','P30380{ad_y,DQ}',
                              'P30380{ad_x,D2Q}','g^[0] acting on P30380'],
            'product_coordinate_vectors':[[str(z) for z in v] for v in coords],
            'product_evaluation_columns':[[str(v[i]) for i in range(len(r['evaluation_row_labels']))] for v in values],
            'ranks_ideal_idealP_idealQ_idealPQ':ranks,
            'arc_30380_multiplicity':2,'kernel_30380_multiplicity':2 if ranks[-1]==17 else None,
            'new_primitive_30380_multiplicity':0 if ranks[-1]==17 else None,
            'VOA_image_rank_on_arc_30380':0 if ranks[-1]==17 else None,
            'null_lift_dependencies':['weight4_3875_source_replay.json','weight5_adjoint_source_replay.json',
                                      'weight6_30380_source_replay.json'],
            'proof':'These are equivariant projections of products of old kernel classes. '
                    'Their combined span supplies one nonzero kernel copy. The independent '
                    'corrected-VOA rank certificate resolves the complementary image copy.'}
    for dependency in record['null_lift_dependencies']:
        source=json.loads(Path(dependency).read_text())
        assert source.get('passed',source.get('source_replay',{}).get('passed'))
    record['arithmetic_checks_passed']=True
    record['exhausts_arc']=record.pop('passed')
    Path('quartic_30380_partial_products.json').write_text(json.dumps(record,indent=2)+'\n')
    if record['exhausts_arc']:
        Path('quartic_30380_products_receipt.json').write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':run()
