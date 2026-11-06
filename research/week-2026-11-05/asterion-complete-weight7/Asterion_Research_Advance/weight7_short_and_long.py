"""Close current lengths<=2 and>=5 at conformal weight seven."""
from fractions import Fraction as Q
from pathlib import Path
import json
from perfectjet.asterion_primitives import (JetAlgebra,THETA,DIMENSION_LABELS,jet_shapes,
    exact_rank,encode_polynomial)
from perfectjet.asterion_lattice_projection4 import ProjectedLatticeE8VOA4
from perfectjet.asterion_relations import highest_weight_dimension

def run():
    j=JetAlgebra();out=[]
    for dim in (1,248,3875,27000,30380):
        labels=DIMENSION_LABELS[dim]
        # Root coordinates from the normalized inverse Cartan matrix.
        target=tuple(int(sum(j.cartan_inverse[i][k]*labels[k] for k in range(8))) for i in range(8))
        lower,_=j.highest_vectors(jet_shapes(1,6),target)
        top,n=j.highest_vectors(jet_shapes(2,5),target)
        assert len(top)==3 and len(lower)==(1 if dim==248 else 0)
        lattice=ProjectedLatticeE8VOA4(j,support=(0,1))
        images=[lattice.symmetric_lift(v) for v in lower+top]
        rank=exact_rank(images);ideal_dimension=1 if dim==27000 else 0
        assert rank==len(lower)+len(top)-ideal_dimension
        out.append({'dimension':dim,'lower_highest_count':len(lower),'pair_highest_count':len(top),
                    'monomial_columns':n,'ideal_highest_dimension':ideal_dimension,
                    'projected_rank_Q':rank,'kernel_multiplicity':0,
                    'highest_columns':[encode_polynomial(v) for v in lower+top],
                    'projected_images':[[[list(beta),[list(x) for x in osc],str(z)] for (beta,osc),z in sorted(im.items())] for im in images]})
        print('Short type',dim,'rank',rank,'kernel0',flush=True)
    u=j.algebra.root_index[THETA]
    square={((u,0),(u,0)):Q(1)}
    assert not ProjectedLatticeE8VOA4(j).symmetric_lift(square)
    derived=square
    for _ in range(5):derived=j.derivative(derived)
    assert derived and j.is_highest(derived)
    shapes={length:jet_shapes(length,7-length) for length in (5,6,7)}
    assert all(shape.count(0)>=3 for ss in shapes.values() for shape in ss)
    dependency=json.loads(Path('weight6_quartic_source_replay.json').read_text())
    assert dependency['passed']
    result={'schema':'asterion/weight7-short-and-long/1','passed':True,'short_types':out,
            'short_completeness':'g tensor g=1+248+3875+27000+30380, each once; the three unequal mode pairs give three copies.',
            'quadratic_null_highest':encode_polynomial(square),'D5_quadratic_ideal_highest':encode_polynomial(derived),
            'long_shapes':shapes,'long_arc_components_zero':[5,6,7],
            'long_argument':'At length L and weight w, at least2L-w factors have zero jet. '
                 'If2L-w>=3, I27000*g=Sym3(g) kills every monomial. At w7 this covers L>=5.',
            'general_vanishing_condition':'2*current_length-conformal_weight>=3',
            'known_weight7_cubic_kernel_dimension':181753,
            'cubic_status':'inherited PR13 theorem; the complete cubic certificate is not rerun here'}
    Path('weight7_short_and_long_receipt.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':run()
