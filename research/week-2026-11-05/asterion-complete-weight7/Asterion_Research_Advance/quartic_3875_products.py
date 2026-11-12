"""Exhaust the surviving R3875 arc space by old P248 products."""
from fractions import Fraction as Q
from pathlib import Path
import json
from perfectjet.asterion_primitives import exact_rank

def run():
    r=json.loads(Path('quartic_3875_ideal_receipt.json').read_text())
    ideal=[{i:Q(z) for i,z in enumerate(v) if Q(z)} for v in r['ideal_coordinate_matrix']]
    # First3 covariants x^3w, next9 x^2yz, last3 y^3x; all output-projected to R3875.
    # P=20x Bxz-21x Byy-12y Bxy, DP=-4y Bxz-33y Byy-64x Byz+60x Bxw-24z Bxy.
    p={4:Q(20),13:Q(-21),12:Q(-12)}
    dp={4:Q(-4),13:Q(-33),3:Q(-64),0:Q(60),5:Q(-24)}
    ranks=[exact_rank(ideal),exact_rank(ideal+[p]),exact_rank(ideal+[dp]),exact_rank(ideal+[p,dp])]
    assert ranks==[13,14,14,15]
    source=json.loads(Path('weight5_adjoint_source_replay.json').read_text())
    assert source['source_replay']['passed']
    record={'schema':'asterion/weight7-quartic-3875-products/1','passed':True,
            'product_classes':['P3875(y sym P248)','P3875(x sym D P248)'],
            'product_coordinate_vectors':[[str(v.get(i,0)) for i in range(15)] for v in (p,dp)],
            'ranks_ideal_idealP_idealDP_idealPDP':ranks,
            'arc_3875_multiplicity':2,'kernel_3875_multiplicity':2,
            'VOA_image_rank_on_arc_3875':0,'new_primitive_3875_multiplicity':0,
            'proof':'Multiplication and translation preserve the Li kernel. The verified '
                    'weight5 adjoint class supplies both products, whose rank increase '
                    'exhausts this entire arc multiplicity space.',
            'null_lift_dependency':'weight5_adjoint_source_replay.json'}
    Path('quartic_3875_products_receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    print({k:record[k] for k in ('passed','kernel_3875_multiplicity','new_primitive_3875_multiplicity')})

if __name__=='__main__':run()
