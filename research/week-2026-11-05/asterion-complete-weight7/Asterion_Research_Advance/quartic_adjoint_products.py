"""The two surviving quartic adjoints are products of old kernel classes."""
from fractions import Fraction as Q
from pathlib import Path
import json
from perfectjet.asterion_primitives import exact_rank

def run():
    r=json.loads(Path('quartic_adjoint_ideal_receipt.json').read_text())
    ideal=[{i:Q(z) for i,z in enumerate(v) if Q(z)} for v in r['ideal_coordinate_matrix']]
    # Basis: two x^3w covariants, seven x^2yz covariants, two y^3x covariants.
    # [y,P248], P248=20x Bxz-21x Byy-12y Bxy.
    p={4:Q(-20),9:Q(-21)}
    # 14 times the contraction of z with 2 P3875(x sym [x,y]).
    # This is the g[2]*F_Q product projected to its adjoint component.
    q={4:Q(2),5:Q(2),6:Q(1),8:Q(-1)}
    ranks=[exact_rank(ideal),exact_rank(ideal+[p]),exact_rank(ideal+[q]),exact_rank(ideal+[p,q])]
    assert ranks==[9,10,10,11]
    record={'schema':'asterion/weight7-quartic-adjoint-products/1','passed':True,
            'product_classes':['[x^[1],P248]','g^[2]*F_Q projected to adjoint'],
            'product_coordinate_vectors':[[str(v.get(i,0)) for i in range(11)] for v in (p,q)],
            'ranks_ideal_idealP_idealQ_idealPQ':ranks,
            'arc_adjoint_multiplicity':2,'kernel_adjoint_multiplicity':2,
            'new_primitive_adjoint_multiplicity':0,
            'VOA_image_rank_on_arc_adjoint':0,
            'null_lift_dependencies':['weight4_3875_source_replay.json','weight5_adjoint_source_replay.json'],
            'proof':'Both product classes belong to the multiplicative Li kernel. '
                    'Their independence modulo the ideal exhausts the two-dimensional '
                    'adjoint multiplicity space. All its classes are old products.',
            'coupling_formula':'2x B([x,y],z)+2[x,y]Bxz+[x,[[x,y],z]]+[[x,y],[x,z]] '
                '=2F3+2F2+F4-F6; this is14 times the contraction of z with2P3875(x sym [x,y]).'}
    for dependency in record['null_lift_dependencies']:
        source=json.loads(Path(dependency).read_text())
        assert source.get('passed',source.get('source_replay',{}).get('passed'))
    Path('quartic_adjoint_products_receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    print({k:record[k] for k in ('passed','kernel_adjoint_multiplicity','new_primitive_adjoint_multiplicity')})

if __name__=='__main__':run()
