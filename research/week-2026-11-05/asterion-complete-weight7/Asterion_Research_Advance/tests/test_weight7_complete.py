"""Global weight7 closure, exact witnesses and proof-scope regressions."""
from fractions import Fraction as Q
from pathlib import Path
import json
import unittest
from perfectjet.asterion_primitives import (JetAlgebra,decode_polynomial,exact_rank,THETA,
    _contraction,_add)
from perfectjet.asterion_kernel_tower import lower_jets
from perfectjet.asterion_lattice_projection4 import ProjectedLatticeE8VOA4
from perfectjet.asterion_primitives import LatticeE8VOA
from quartic_remaining_sectors import QuarticJets,I_project
from perfectjet.asterion_relations import AffinePBW
from verify_quartic_small_matrices import bareiss_rank

ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text())

class WeightSevenCompleteTests(unittest.TestCase):
    def test_complete_weight7_characters_and_dimensions(self):
        r=read('COMPLETE_WEIGHT7_THEOREM.json')
        self.assertEqual(r['total_weight7_kernel_character'],{'1':1,'248':3,'3875':3,'30380':2,'147250':2,'779247':1})
        self.assertEqual(r['total_arc_dimension']-r['simple_VOA_dimension'],1146877)
        self.assertEqual(r['simple_VOA_dimension'],17333248)
        self.assertEqual(r['quartic_kernel_dimension'],965124)
        self.assertEqual(r['quartic_VOA_image_dimension'],6726380)

    def test_all_nineteen_types_are_exhausted(self):
        r=read('COMPLETE_WEIGHT7_THEOREM.json');rows=r['quartic_sector_table']
        source=read('quartic_schur_receipt.json')['weight7_length4_ambient']['irreducibles']
        self.assertEqual({x['dimension'] for x in rows},{x['dimension'] for x in source})
        self.assertEqual(len(rows),19)
        for x in rows:self.assertEqual(x['arc'],x['image']+x['kernel']);self.assertEqual(x['source']-x['ideal'],x['arc'])

    def test_S4_frame_and_Casimir_cutoff(self):
        r=read('quartic_casimir_cutoff_receipt.json')
        self.assertEqual(bareiss_rank(r['triple_diagonal_constraint_matrix']),12)
        self.assertEqual(r['jet_kernel_dimension'],8)
        self.assertEqual(r['pair_even_restriction_kernel_dimension'],1)
        self.assertEqual(r['frame_eigenvalues'],{'31':'13/7','22':'0','211':'1/7'})
        self.assertEqual(r['Casimir_bounds'],{'31':196,'22':168,'211':196})
        self.assertEqual(len(r['excluded_arc_types']),8)
        self.assertTrue(all(x['Casimir']>196 for x in r['excluded_arc_types']))

    def test_30380_independent_ideal_and_corrected_image_ranks(self):
        r=read('quartic_30380_ideal_receipt.json')
        self.assertEqual(bareiss_rank(r['ideal_coordinate_matrix']),15)
        v=read('quartic_30380_VOA_receipt.json')
        cols=[{(tuple(b),tuple(map(tuple,o))):Q(z) for b,o,z in c} for c in v['projected_image_columns']]
        keys=sorted(set().union(*cols));m=[[c.get(k,0) for c in cols] for k in keys]
        self.assertEqual(bareiss_rank([x[:-1] for x in m]),7)
        self.assertEqual(bareiss_rank(m),8)
        j=JetAlgebra()
        self.assertTrue(all(j.is_highest(decode_polynomial(c)) for c in v['lower_highest_columns']))
        self.assertTrue(j.is_highest(decode_polynomial(v['quartic_symbol'])))

    def test_source_projector_is_correct_on_three_spectral_summands(self):
        j=QuarticJets();u=j.algebra.root_index[THETA]
        free=((0,9),(0,10))
        highest={tuple(sorted(((u,0),(u,0))+free)):Q(1)}
        self.assertEqual(I_project(j,highest),highest)
        c={tuple(sorted(m+free)):z for m,z in _contraction(j,None,0,0).items()}
        self.assertFalse(I_project(j,c))
        q=AffinePBW(algebra=j.algebra).highest_quadratic_3875()
        r={tuple(sorted(((a,0),(b,0))+free)):z for (a,b),z in q.items()}
        self.assertFalse(I_project(j,r))

    def test_meet_in_middle_extremal_weight(self):
        j=QuarticJets();u=j.algebra.root_index[THETA];target=tuple(4*x for x in THETA)
        for shape in ((0,0,0,3),(0,0,1,2),(0,1,1,1)):
            self.assertEqual(j.monomials(shape,target),[tuple(sorted((u,k) for k in shape))])

    def test_sparse_span_minor_certificates(self):
        for dim,rank in ((27000,18),(147250,9),(779247,15),(1763125,5),(2450240,10),(4096000,14),(6696000,4)):
            r=read(f'quartic_span_certificate_{dim}.json')
            self.assertEqual(bareiss_rank(r['ideal']['invertible_minor']),rank)
            self.assertTrue(r['ideal']['every_sparse_recombination_checked'])
            if dim in (147250,779247):self.assertEqual(r['ideal_plus_old_products']['rank'],rank+1)

    def test_old_products_exhaust_every_nonzero_quartic_kernel(self):
        for dim in (147250,779247):
            r=read(f'quartic_old_products_{dim}.json')
            self.assertTrue(r['passed']);self.assertEqual(r['old_product_multiplicity'],1)
            self.assertEqual(r['new_primitive_multiplicity'],0)
            j=JetAlgebra()
            self.assertTrue(all(j.is_highest(decode_polynomial(c)) for c in r['product_highest_columns']))
        r=read('COMPLETE_WEIGHT7_THEOREM.json')
        self.assertTrue(all(x['new_primitives']==0 for x in r['quartic_sector_table']))

    def test_full_support_matches_original_unprojected_evaluator(self):
        r=read('quartic_full_6696000.json');p=decode_polynomial(r['top_highest_columns'][4])
        j=JetAlgebra();a=LatticeE8VOA(j).symmetric_lift(p)
        b=ProjectedLatticeE8VOA4(j,support=tuple(range(8))).symmetric_lift(p)
        self.assertTrue(a);self.assertEqual(a,b)

    def test_short_and_long_current_lengths(self):
        r=read('weight7_short_and_long_receipt.json')
        self.assertEqual({x['dimension'] for x in r['short_types']},{1,248,3875,27000,30380})
        self.assertTrue(all(x['kernel_multiplicity']==0 for x in r['short_types']))
        for shapes in r['long_shapes'].values():self.assertTrue(all(s.count(0)>=3 for s in shapes))

    def test_translation_injectivity_algebra(self):
        j=JetAlgebra()
        for shape in ((0,),(0,0),(0,1,3),(0,0,1,2)):
            p={tuple((0,r) for r in shape):Q(3,7)}
            lhs=lower_jets(j.derivative(p));_add(lhs,j.derivative(lower_jets(p)),-1)
            self.assertEqual(lhs,{m:len(shape)*z for m,z in p.items()})
        u=j.algebra.root_index[THETA];q={((u,0),(u,0)):Q(1)};cur=q
        for k in range(1,6):
            prev=cur;cur=j.derivative(cur)
            self.assertEqual(lower_jets(cur),{m:2*k*z for m,z in prev.items()})

    def test_scope_and_all_weight_boundary(self):
        r=read('COMPLETE_WEIGHT7_THEOREM.json')
        self.assertTrue(r['all_19_quartic_types_classified'])
        self.assertEqual(r['new_weight7_primitive_dimension'],0)
        self.assertFalse(r['all_weight_finite_generation_proved'])
        self.assertTrue(read('arc_length3_replay.json')['passed'])
        self.assertTrue(read('VOA_weight7_character.json')['passed'])

if __name__=='__main__':unittest.main()
