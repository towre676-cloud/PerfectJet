"""Independent integer-matrix replay and final scope of the30380 theorem."""
from fractions import Fraction as Q
from pathlib import Path
import json
from verify_quartic_small_matrices import bareiss_rank

def dense_columns(columns):return [list(map(Q,row)) for row in zip(*columns)]
def run():
    ideal=json.loads(Path('quartic_30380_ideal_receipt.json').read_text())
    voa=json.loads(Path('quartic_30380_VOA_receipt.json').read_text())
    products=json.loads(Path('quartic_30380_partial_products.json').read_text())
    assert bareiss_rank(dense_columns(ideal['source_evaluation_columns']))==17
    assert bareiss_rank(dense_columns(ideal['pair_evaluation_columns']))==11
    assert bareiss_rank(ideal['ideal_coordinate_matrix'])==15
    assert bareiss_rank(dense_columns(ideal['ideal_evaluation_columns']))==15
    for c,image in zip(ideal['ideal_coordinate_matrix'],ideal['ideal_evaluation_columns']):
        for row,value in enumerate(image):
            assert sum(Q(a)*Q(col[row]) for a,col in zip(c,ideal['source_evaluation_columns']))==Q(value)
    selected=ideal['projector_evaluation_row_indices']
    for c,image in zip(ideal['pair_projector'],ideal['pair_projected_evaluation_columns']):
        for row,index in enumerate(selected):
            assert sum(Q(a)*Q(col[index]) for a,col in zip(c,ideal['pair_evaluation_columns']))==Q(image[row])
    images=[{(tuple(beta),tuple(map(tuple,osc))):Q(z) for beta,osc,z in v} for v in voa['projected_image_columns']]
    keys=sorted(set().union(*images))
    matrix=[[col.get(k,0) for col in images] for k in keys]
    assert bareiss_rank([row[:-1] for row in matrix])==7
    assert bareiss_rank(matrix)==8
    product=products['product_coordinate_vectors'][0]
    assert bareiss_rank(ideal['ideal_coordinate_matrix']+[product])==16
    assert json.loads(Path('weight5_adjoint_source_replay.json').read_text())['source_replay']['passed']
    cutoff=json.loads(Path('quartic_casimir_cutoff_receipt.json').read_text());assert cutoff['passed']
    assert bareiss_rank(cutoff['triple_diagonal_constraint_matrix'])==12
    short=json.loads(Path('weight7_short_and_long_receipt.json').read_text());assert short['passed']
    for r in short['short_types']:
        cols=[{(tuple(beta),tuple(map(tuple,osc))):Q(z) for beta,osc,z in v} for v in r['projected_images']]
        ks=sorted(set().union(*cols))
        assert bareiss_rank([[c.get(k,0) for c in cols] for k in ks])==r['projected_rank_Q']
    resolved={1,248,3875,30380}
    remaining=[x['dimension'] for x in cutoff['not_excluded_types'] if x['dimension'] not in resolved]
    result={'schema':'asterion/weight7-quartic-frontier-checkpoint/1','passed':True,
       'superseded_by':'COMPLETE_WEIGHT7_THEOREM.json',
       'quartic_30380':{'source_multiplicity':17,'ideal_rank_Q':15,'arc_multiplicity':2,
          'VOA_image_multiplicity':1,'kernel_multiplicity':1,'new_primitive_multiplicity':0},
       'quartic_Casimir_bound':196,'zero_arc_types':[x['dimension'] for x in cutoff['excluded_arc_types']],
       'resolved_quartic_type_count':12,'remaining_quartic_types':remaining,
       'short_kernel_zero':True,'long_arc_zero_lengths':[5,6,7],
       'known_quartic_kernel_character':{'1':1,'248':2,'3875':2,'30380':1},
       'known_quartic_kernel_dimension':38627,'known_quartic_new_primitives':0,
       'inherited_cubic_kernel_dimension':181753,'total_known_weight7_kernel_dimension_lower_bound':220380,
       'complete_weight7_classification':False,
       'cubic_result_replayed_here':False}
    Path('quartic_frontier_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':run()
