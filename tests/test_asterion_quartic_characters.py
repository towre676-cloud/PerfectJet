"""Exact quartic finite characters and the multiplicity-forced1+3875 bound."""
import copy
import json
import unittest

from perfectjet.asterion_quartic_characters import (
    quartic_characters_receipt, verify_quartic_character_certificate,
)


class QuarticCharacterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = quartic_characters_receipt()

    def test_complete_3875_weight_input_is_reconstructed_from_the_lattice(self):
        proof = self.receipt
        self.assertTrue(proof['passed'])
        self.assertTrue(all(proof['checks'].values()))
        self.assertEqual(proof['weight_input']['distinct_adjoint_weights'], 241)
        self.assertEqual(proof['weight_input']['distinct_adjoint_square_weights'], 9361)
        self.assertEqual(proof['weight_input']['distinct_3875_weights'], 2401)
        self.assertEqual(proof['weight_input']['3875_support_shell_counts'], {0:1,2:240,4:2160})
        self.assertEqual(proof['weight_input']['3875_multiplicity_by_squared_norm'], {0:35,2:7,4:1})

    def test_exact_Sym2W_and_Sym4g_decompositions_have_complete_dimension_checks(self):
        proof = self.receipt
        char = lambda name: {r['dimension']: r['multiplicity'] for r in proof[name]['irreducibles']}
        self.assertEqual(char('Sym2_3875'), {1:1,3875:1,27000:1,147250:1,2450240:1,4881384:1})
        self.assertEqual(char('Sym2_W'), {1:2,3875:2,27000:1,147250:1,2450240:1,4881384:1})
        self.assertEqual(char('Sym4_g'), {1:1,3875:1,27000:2,147250:1,2450240:1,
                                         4096000:1,4881384:1,70680000:1,79143000:1})
        self.assertEqual(proof['Sym2_3875']['reconstructed_dimension'], 7509750)
        self.assertEqual(proof['Sym2_W']['reconstructed_dimension'], 7513626)
        self.assertEqual(proof['Sym4_g']['reconstructed_dimension'], 161455750)
        for name in ('Sym2_3875','Sym2_W','Sym4_g'):
            for row in proof[name]['dominant_weight_rows']:
                self.assertEqual(row['Schur_weight_multiplicity'],
                                 row['higher_irrep_contribution']+row['highest_irrep_multiplicity'])

    def test_Newton_rows_are_exact_and_norm_bounds_exhaust_highest_weights(self):
        proof = self.receipt
        self.assertEqual(proof['norm_bounds']['Sym2_W'], 16)
        self.assertEqual(proof['norm_bounds']['Sym4_g'], 32)
        self.assertTrue(any(row['squared_norm'] == 32 for row in proof['Sym4_Newton_weight_rows']))
        for row in proof['Sym4_Newton_weight_rows']:
            numerator = (row['chi4']+6*row['chi2_psi2']+3*row['psi2_squared']
                         +8*row['chi_psi3']+6*row['psi4'])
            self.assertEqual(numerator, row['numerator'])
            self.assertEqual(numerator, 24*row['Sym4_weight_multiplicity'])

    def test_multiplicity_forces_a_kernel_without_assuming_all_other_ranks(self):
        proof = self.receipt
        self.assertEqual(proof['forced_multiplication_kernel_character'], {1:1,3875:1})
        self.assertEqual(proof['forced_multiplication_kernel_dimension_lower_bound'], 3876)
        self.assertEqual(proof['quartic_arc_dimension_lower_bound'], 3876)
        self.assertIn('separate', proof['quartic_arc_identification_dependency'])
        self.assertFalse(proof['exact_full_quartic_kernel_claim'])
        self.assertFalse(proof['all_other_multiplication_blocks_maximal_rank_claim'])
        self.assertFalse(proof['explicit_quartic_VOA_null_vector_claim'])
        self.assertFalse(proof['complete_weight6_arc_kernel_claim'])
        self.assertFalse(proof['large_tensor_product_tables_imported'])

    def test_json_character_certificate_detects_tampering(self):
        record = json.loads(json.dumps(self.receipt, allow_nan=False))
        record['passed'] = False
        self.assertTrue(verify_quartic_character_certificate(record)['passed'])
        corrupt = copy.deepcopy(record)
        corrupt['Sym2_W']['irreducibles'][0]['multiplicity'] += 1
        self.assertFalse(verify_quartic_character_certificate(corrupt)['checks']['Sym2_W'])
        corrupt = copy.deepcopy(record)
        corrupt['Sym4_g']['irreducibles'][0]['dimension'] += 1
        self.assertFalse(verify_quartic_character_certificate(corrupt)['checks']['Sym4_g'])
        duplicate = copy.deepcopy(record)
        duplicate['Sym4_g']['irreducibles'].append(duplicate['Sym4_g']['irreducibles'][0])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            verify_quartic_character_certificate(duplicate)

    def test_exhaustive_trace_remains_exact_and_does_not_expand_claim_scope(self):
        proof = quartic_characters_receipt(exhaustive=True)
        self.assertTrue(proof['passed'])
        self.assertEqual(len(proof['Freudenthal_recursion_trace']), proof['Freudenthal_recursion_states'])
        for row in proof['Freudenthal_recursion_trace']:
            self.assertGreater(row['denominator'], 0)
            self.assertEqual(row['numerator'], row['denominator']*row['multiplicity'])
        json.dumps(proof, allow_nan=False)
        self.assertFalse(proof['complete_infinite_kernel_claim'])

    def test_malformed_certificate_and_non_boolean_flags_are_rejected(self):
        for bad in ('yes',1,None):
            with self.assertRaises(ValueError):
                quartic_characters_receipt(exhaustive=bad)
        with self.assertRaises(ValueError):
            verify_quartic_character_certificate([])
        bad = copy.deepcopy(self.receipt)
        bad['Sym2_W']['irreducibles'][0]['multiplicity'] = True
        with self.assertRaises(ValueError):
            verify_quartic_character_certificate(bad)


if __name__ == '__main__':
    unittest.main()
