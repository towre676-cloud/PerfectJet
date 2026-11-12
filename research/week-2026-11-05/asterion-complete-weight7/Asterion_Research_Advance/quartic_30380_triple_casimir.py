"""Find the147250 triple-input summand without constructing that module."""
from fractions import Fraction as Q
from pathlib import Path
import json
from quartic_adjoint_ideal import J,add,bracket
from quartic_30380_ideal import middle
from perfectjet.asterion_primitives import solve_combination,decode_polynomial,JetAlgebra
from perfectjet.exact import nullspace,transpose
from perfectjet.asterion_quartic_characters import _QuarticFreudenthal
from perfectjet.asterion_relations import highest_weight_dimension

def run():
    r=json.loads(Path('quartic_30380_ideal_receipt.json').read_text());mi=r['middle_candidate_indices']
    points=[[{i:Q(z) for i,z in v} for v in p] for p in r['samples']]
    def f(x,y,z,u,v):
        vals=middle(x,y,z,u,v);return [Q(vals[i]) for i in mi]
    indices=r['projector_evaluation_row_indices']
    cols=[{i:Q(col[row]) for i,row in enumerate(indices)} for col in r['pair_evaluation_columns']]
    values=[]
    for index in indices:
        s,p=r['evaluation_row_labels'][index];x,y,z,w=points[s];u,v=[{i:1} for i in r['probes'][p]]
        base=f(x,y,z,u,v);total=[180*b for b in base]
        for a in range(248):
            ta={a:1};dual=J.dual(a);by=bracket(dual,y)
            if not by:continue
            au=bracket(ta,u);av=bracket(ta,v)
            if au:
                for i,value in enumerate(f(x,by,z,au,v)):total[i]+=2*value
            if av:
                for i,value in enumerate(f(x,by,z,u,av)):total[i]+=2*value
        values.append(total);print('Triple Casimir row',len(values),flush=True)
    images=[dict(enumerate(v)) for v in zip(*values)]
    matrix=[solve_combination(v,cols) for v in images];assert all(v is not None for v in matrix)
    eigen=nullspace(transpose([[z-(144 if i==j else 0) for j,z in enumerate(row)] for i,row in enumerate(matrix)]),11)
    assert len(eigen)==1
    coefficients=eigen[0]
    engine=_QuarticFreudenthal()
    matching=[(labels,highest_weight_dimension(labels,engine.algebra)) for labels,root,norm in engine.dominant_weights(18) if engine.casimir(root)==144]
    assert len(matching)==1 and matching[0][1]==147250
    source=json.loads(Path('primitive_147250_source.json').read_text())
    p=decode_polynomial(source['representatives'][0]['symbol'])
    a={m:z for m,z in p.items() if JetAlgebra.shape(m)==(0,0,2)}
    b={m:z for m,z in p.items() if JetAlgebra.shape(m)==(0,1,1)}
    relabel={tuple(sorted((i,1 if k==0 else 0) for i,k in m)):z for m,z in a.items()}
    ratio=solve_combination(b,[relabel]);assert ratio is not None
    # The same Schur tensor is evaluated at(x,x,z) and(y,y,x), with one common free y.
    def g(x,y,z,u,v):return sum(c*t for c,t in zip(coefficients,f(x,y,z,u,v)))
    evaluated={}
    for row,(s,p) in enumerate(r['evaluation_row_labels']):
        x,y,z,w=points[s];u,v=[{i:1} for i in r['probes'][p]]
        evaluated[row]=g(x,y,z,u,v)+ratio[0]*g(y,y,x,u,v)
    ambient=[dict(enumerate(map(Q,col))) for col in r['source_evaluation_columns']]
    product=solve_combination(evaluated,ambient);assert product is not None
    from perfectjet.asterion_primitives import exact_rank
    ideal=[dict(enumerate(map(Q,c))) for c in r['ideal_coordinate_matrix']]
    products=json.loads(Path('quartic_30380_partial_products.json').read_text())['product_coordinate_vectors']
    old=[dict(enumerate(map(Q,c))) for c in products]
    rank=exact_rank(ideal+old+[dict(enumerate(product))])
    print('147250 coupling ratio',ratio[0],'full product rank',rank,flush=True)
    record={'passed':True,'triple_Casimir_matrix':[[str(z) for z in row] for row in matrix],
            'Casimir144_eigenvector':[str(z) for z in coefficients],
            'unique_Casimir144_highest_weights':matching,
            'source_shape_relabel_ratio':str(ratio[0]),'product_coordinates':[str(z) for z in product],
            'product_evaluation_column':[str(evaluated[i]) for i in range(len(evaluated))],
            'rank_after_147250_product':rank,'source_null_dependency':'weight5_147250_source_replay.json'}
    Path('quartic_30380_147250_product_receipt.json').write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':run()
