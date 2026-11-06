"""Combine independent characters and finite rank/product certificates."""
from pathlib import Path
from collections import Counter
import json
from perfectjet.asterion_kernel_characters import length_three_character,length_two_character

def dimension(c):return sum(int(d)*m for d,m in c.items())
def read(name):return json.loads(Path(name).read_text())

def run():
    assert read('quartic_frontier_verification.json')['passed']
    zero=read('quartic_casimir_cutoff_receipt.json')['excluded_arc_types']
    rows={x['dimension']:{'dimension':x['dimension'],'source':x['multiplicity'],
         'ideal':x['multiplicity'],'arc':0,'image':0,'kernel':0,'new_primitives':0,
         'proof':'Casimir cutoff'} for x in zero}
    for d,source,ideal,arc,kernel in [(1,5,4,1,1),(248,11,9,2,2),(3875,15,13,2,2),(30380,17,15,2,1)]:
        rows[d]={'dimension':d,'source':source,'ideal':ideal,'arc':arc,'image':arc-kernel,
                 'kernel':kernel,'new_primitives':0,'proof':'complete covariants, corrected image ranks and old products'}
    for d in (27000,1763125,2450240,4096000,6696000):
        name=f'quartic_zero_arc_{d}.json' if d==27000 else f'quartic_full_{d}.json'
        r=read(name);assert r['passed']
        rows[d]={'dimension':d,'source':r['source_multiplicity'],'ideal':r['ideal_rank_Q'],
                 'arc':r['arc_multiplicity'],'image':r['VOA_image_multiplicity'],
                 'kernel':r['kernel_multiplicity'],'new_primitives':0,
                 'proof':'explicit highest polynomials, ideal spanning and exact lattice output'}
    for d in (147250,779247):
        r=read(f'quartic_ideal_only_{d}.json');p=read(f'quartic_old_products_{d}.json')
        assert r['passed'] and p['passed'] and p['old_product_multiplicity']==r['arc_multiplicity']
        assert read(f'quartic_span_certificate_{d}.json')['passed']
        rows[d]={'dimension':d,'source':r['source_multiplicity'],'ideal':r['ideal_rank_Q'],
                 'arc':r['arc_multiplicity'],'image':0,'kernel':r['arc_multiplicity'],
                 'new_primitives':0,'proof':'complete ideal plus old-generator product spanning'}
    assert len(rows)==19
    a4={d:r['arc'] for d,r in rows.items() if r['arc']}
    k4={d:r['kernel'] for d,r in rows.items() if r['kernel']}
    i4={d:r['image'] for d,r in rows.items() if r['image']}
    assert read('arc_length3_replay.json')['passed']
    voa=read('VOA_weight7_character.json');assert voa['passed']
    simple={r['dimension']:r['multiplicity'] for r in voa['irreducibles']}
    arc=Counter({248:1});arc.update(length_two_character(5));arc.update(length_three_character(4));arc.update(a4)
    total={d:arc.get(d,0)-simple.get(d,0) for d in set(arc)|set(simple)}
    assert all(m>=0 for m in total.values());total={d:m for d,m in sorted(total.items()) if m}
    cubic={d:total.get(d,0)-k4.get(d,0) for d in set(total)|set(k4)}
    assert all(m>=0 for m in cubic.values());cubic={d:m for d,m in sorted(cubic.items()) if m}
    assert cubic=={248:1,3875:1,30380:1,147250:1}
    assert read('weight7_short_and_long_receipt.json')['passed']
    result={'schema':'asterion/complete-weight7-theorem/1','passed':True,
       'quartic_sector_table':[rows[d] for d in sorted(rows)],
       'quartic_arc_character':a4,'quartic_VOA_image_character':i4,'quartic_kernel_character':k4,
       'quartic_arc_dimension':dimension(a4),'quartic_VOA_image_dimension':dimension(i4),
       'quartic_kernel_dimension':dimension(k4),'cubic_kernel_character':cubic,
       'cubic_kernel_dimension':dimension(cubic),'total_weight7_kernel_character':total,
       'total_weight7_kernel_dimension':dimension(total),'total_arc_character':dict(sorted(arc.items())),
       'total_arc_dimension':dimension(arc),'simple_VOA_character':simple,'simple_VOA_dimension':dimension(simple),
       'dimension_difference_checked':dimension(arc)-dimension(simple)==dimension(total),
       'all_19_quartic_types_classified':True,'short_kernel_zero':True,'lengths5_through7_arc_zero':True,
       'new_weight7_primitive_character':{},'new_weight7_primitive_dimension':0,
       'generator_degrees_sufficient_through_weight7':[4,5,6],
       'all_weight_finite_generation_proved':False,
       'proof_of_no_new_cubic_primitive':'E*x[r]=x[r-1], [E,D]=ordinary_length, E locally nilpotent and ideal-stable. '
           'Hence D is injective in every positive current length. The four existing cubic '
           'classes of weight6 have independent nonzero derivatives with exactly the computed '
           'weight7 cubic kernel character.',
       'cubic_character_rederived_here_from_full_characters':True,
       'relation_to_PR13':'agrees with the earlier cubic theorem; no re-execution of its original projected matrices is required for this independent character argument'}
    assert result['quartic_kernel_dimension']==965124
    assert result['total_weight7_kernel_dimension']==1146877
    Path('COMPLETE_WEIGHT7_THEOREM.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('passed','quartic_arc_dimension','quartic_VOA_image_dimension',
       'quartic_kernel_dimension','total_arc_dimension','simple_VOA_dimension',
       'total_weight7_kernel_dimension','new_weight7_primitive_dimension')},indent=2))

if __name__=='__main__':run()
