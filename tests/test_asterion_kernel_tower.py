"""Higher E8 kernel translations, exact finite characters and short-current ranks."""
from fractions import Fraction as Q
import copy
import json
import unittest

from perfectjet.asterion_kernel_tower import (
    E8Freudenthal, differentiate_jets, differential_annihilator_receipt,
    kernel_tower_receipt, lower_jets, multiply_jet_variable,
    short_current_injectivity_receipt, tensor_cube_character_receipt,
    translation_tower_receipt, verify_voa_character_certificate, _finite_kernel_closure,
)
from perfectjet.asterion_kernel_characters import kernel_characters_receipt
from perfectjet.asterion_relations import _add


class KernelTowerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = E8Freudenthal(6)
        cls.characters = [cls.engine.voa_character(n) for n in range(7)]
        cls.schur = tensor_cube_character_receipt()
        cls.short5 = short_current_injectivity_receipt(5)
        cls.short6 = short_current_injectivity_receipt(6)
        cls.arc_proof = kernel_characters_receipt()
        cls.closure = _finite_kernel_closure(cls.arc_proof, cls.characters, cls.schur,
                                            cls.short5, cls.short6)

    def test_lowering_translation_commutator_is_ordinary_degree(self):
        polynomial = {((8, 0), (12, 2), (247, 1)): Q(7, 3),
                      ((0, 3), (1, 0), (2, 0)): Q(-5)}
        commutator = lower_jets(differentiate_jets(polynomial))
        _add(commutator, differentiate_jets(lower_jets(polynomial)), -1)
        self.assertEqual(commutator, {m: 3*z for m, z in polynomial.items()})
        lowered = polynomial
        for _ in range(4):
            lowered = lower_jets(lowered)
        self.assertFalse(lowered)

    def test_lowering_preserves_all_differential_quadratic_generators(self):
        # The singular-square highest relation is homogeneous of degree2.
        relation = {((247, 0), (247, 0)): Q(1)}
        current = relation
        for order in range(1, 6):
            previous = current
            current = differentiate_jets(current)
            self.assertEqual(lower_jets(current), {m: 2*order*z for m, z in previous.items()})

    def test_explicit3875_translation_left_inverse_and_all_order_scope(self):
        proof = translation_tower_receipt(3)
        self.assertTrue(proof['passed'])
        self.assertTrue(proof['translation_injective_on_every_positive_ordinary_degree'])
        self.assertEqual([r['left_inverse_scalar'] for r in proof['finite_checks']], [1,3,18,162])
        self.assertEqual([r['Li_degree'] for r in proof['finite_checks']], [1,2,3,4])
        self.assertEqual(proof['all_weight_kernel_dimension_lower_bound'], 3875)
        self.assertEqual(proof['all_weight_Jordan_grade_lower_bound'], 31)
        self.assertFalse(proof['full_higher_kernel_claim'])

    def test_exact_differential_annihilator_syzygies(self):
        proof = differential_annihilator_receipt(index=8, max_derivative=3)
        self.assertTrue(proof['passed'])
        self.assertEqual(proof['generator_zero_jet_degree'], 2)
        self.assertTrue(proof['all248_ordinary_currents_annihilate_K4'])
        self.assertTrue(all(r['identity_checked'] for r in proof['syzygies']))
        self.assertFalse(proof['complete_syzygy_presentation_claim'])

    def test_exact_freudenthal_folds_root_weights_and_zero_weights(self):
        e = self.engine
        adjoint = (0,0,0,0,0,0,1,0)
        theta = e.root_coordinates(adjoint)
        self.assertEqual(e.casimir(theta), 60)
        self.assertEqual(e.multiplicity(adjoint, (0,)*8), 8)
        for root in e.algebra.roots:
            self.assertEqual(e.dominant(root), theta)
            self.assertEqual(e.multiplicity(adjoint, root), 1)
        self.assertEqual(e.multiplicity((1,0,0,0,0,0,0,0), (0,)*8), 35)
        self.assertEqual(e.multiplicity((1,0,0,0,0,0,0,0), theta), 7)

    def test_complete_finite_voa_characters_through_weight_six(self):
        self.assertTrue(all(r['passed'] for r in self.characters))
        self.assertEqual([r['reconstructed_dimension'] for r in self.characters],
                         [1,248,4124,34752,213126,1057504,4530744])
        char5 = {r['dimension']: r['multiplicity'] for r in self.characters[5]['irreducibles']}
        self.assertEqual(char5, {1:2,248:5,3875:3,27000:1,30380:3,147250:1,779247:1})
        self.assertTrue(all(row['denominator'] > 0 for row in self.engine.recursion_trace.values()))
        self.assertTrue(all(row['numerator'] == row['denominator']*row['multiplicity']
                            for row in self.engine.recursion_trace.values()))

    def test_json_finite_character_certificate_detects_corruption(self):
        original = json.loads(json.dumps(self.characters[5], allow_nan=False))
        self.assertTrue(verify_voa_character_certificate(original)['passed'])
        bad = copy.deepcopy(original)
        bad['irreducibles'][0]['multiplicity'] += 1
        self.assertFalse(verify_voa_character_certificate(bad)['passed'])
        bad = copy.deepcopy(original)
        bad['irreducibles'][0]['dimension'] += 1
        self.assertFalse(verify_voa_character_certificate(bad)['checks']['Weyl_dimensions'])
        duplicate = copy.deepcopy(original)
        duplicate['irreducibles'].append(duplicate['irreducibles'][0])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            verify_voa_character_certificate(duplicate)

    def test_tensor_cube_schur_characters_need_no_large_tensor_table(self):
        proof = self.schur
        self.assertTrue(proof['passed'])
        self.assertFalse(proof['large_tensor_product_tables_imported'])
        pieces = proof['Schur_components']
        self.assertEqual(pieces['symmetric_cube']['reconstructed_dimension'], 2573000)
        self.assertEqual(pieces['mixed_S21']['reconstructed_dimension'], 5084248)
        exterior = {r['dimension']: r['multiplicity']
                    for r in pieces['exterior_cube']['irreducibles']}
        self.assertEqual(exterior, {1:1,3875:1,27000:1,30380:1,2450240:1})
        self.assertTrue(all(proof['quadratic_tensor_checks'].values()))
        self.assertEqual({r['dimension']: r['multiplicity']
                          for r in proof['g_tensor_I27000']['irreducibles']},
                         {248:1,27000:1,30380:1,779247:1,1763125:1,4096000:1})

    def test_complete_short_current_gram_blocks_at_weights_five_and_six(self):
        for proof, total, ranks in ((self.short5,96256,[2,2,1,3,2]),
                                    (self.short6,127132,[3,3,2,3,2])):
            self.assertTrue(proof['passed'])
            self.assertTrue(all(proof['checks'].values()))
            self.assertEqual(proof['injective_short_current_dimension'], total)
            self.assertEqual([r['exact_Gram_rank'] for r in proof['blocks']], ranks)
            self.assertFalse(proof['dense_full_PBW_sector_allocated'])
            json.dumps(proof, allow_nan=False)

    def test_weight_five_complete_kernel_and_primitive_quotient(self):
        proof = self.closure
        self.assertTrue(proof['passed'])
        self.assertTrue(all(proof['checks'].values()))
        w5 = proof['weight_five']
        self.assertEqual((w5['arc_dimension'],w5['simple_dimension']), (1208877,1057504))
        self.assertEqual(w5['kernel_finite_character'], {248:1,3875:1,147250:1})
        self.assertEqual(w5['kernel_dimension'], 151373)
        self.assertEqual(w5['entire_kernel_Li_degree'], 2)
        self.assertEqual(w5['primitive_quotient_character'], {248:1,147250:1})
        self.assertEqual(w5['primitive_quotient_dimension'], 147498)
        self.assertEqual(w5['Jordan_kernel_distribution']['neutral_grade_dimension'], 1209)
        self.assertEqual(w5['Jordan_kernel_distribution']['each_of124_nonzero_grades_dimension'], 1211)
        self.assertEqual(w5['Jordan_primitive_distribution']['neutral_grade_dimension'], 1178)
        self.assertEqual(w5['Jordan_primitive_distribution']['each_of124_nonzero_grades_dimension'], 1180)

    def test_weight_six_forces_new30380_primitive_in_Li_three(self):
        w6 = self.closure['weight_six']
        self.assertEqual(w6['length_three_arc_dimension'], 4585365)
        self.assertEqual(w6['injective_short_current_dimension'], 127132)
        self.assertEqual(w6['length_three_kernel_dimension_lower_bound'], 181753)
        self.assertEqual(w6['forced_length_three_kernel_submodule'],
                         {248:1,3875:1,30380:1,147250:1})
        self.assertEqual(w6['forced_new_primitive_submodule'], {30380:1})
        self.assertEqual(w6['new_primitive_dimension_lower_bound'], 30380)
        self.assertEqual(w6['Jordan_forced_primitive_lower_bound']['neutral_grade_dimension'], 248)
        self.assertEqual(w6['Jordan_forced_primitive_lower_bound']['each_of124_nonzero_grades_dimension'], 243)
        self.assertFalse(w6['full_kernel_or_primitive_character_claim'])
        self.assertFalse(self.closure['full_infinite_differential_kernel_presentation_claim'])
        self.assertEqual(self.closure['all_weight_kernel_dimension_lower_bound_from_weight5'], 151373)
        json.dumps(self.closure, allow_nan=False)

    def test_strict_bounds_and_rational_jet_inputs(self):
        for bad in (True,-1,13,2.5):
            with self.assertRaises(ValueError):
                E8Freudenthal(bad)
        for bad in (True,-1,9):
            with self.assertRaises(ValueError):
                translation_tower_receipt(bad)
        for bad in ({((248,0),):1}, {((1,-1),):1}, {((True,0),):1},
                    {((1,0),):0.5}, {((1,0),):True}, {((1,0),):'1/2'}, []):
            with self.assertRaises(ValueError):
                lower_jets(bad)
        with self.assertRaises(ValueError):
            multiply_jet_variable({}, 248)
        with self.assertRaises(ValueError):
            self.engine.voa_character(True)
        with self.assertRaises(ValueError):
            self.engine.dominant((100,)*8)
        with self.assertRaises(ValueError):
            self.engine.multiplicity((True,)*8, (0,)*8)
        with self.assertRaises(ValueError):
            kernel_tower_receipt(exhaustive='yes')


if __name__ == '__main__':
    unittest.main()
