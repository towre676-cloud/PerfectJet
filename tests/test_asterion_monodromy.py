"""Actual-level monodromy closure gates, with rigorous arithmetic bounds."""
from fractions import Fraction as Q
import json
import unittest

from perfectjet.asterion_kz import RationalComplex as C, identity
from perfectjet.asterion_monodromy import (
    ComplexBall, MatrixBall, SPECTRUM_EXPONENTS, irreducibility_receipt,
    local_spectrum_receipt, monodromy_receipt, root_certificate, seventeenth_roots,
)


class MonodromyGroupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This single integration is a required proof input, rather than a
        # floating point smoke test or an unverified saved approximation.
        cls.receipt = monodromy_receipt(exhaustive=True)

    def test_actual_fixed_level_closure_is_classified_after_all_gates(self):
        receipt = self.receipt
        self.assertTrue(receipt['passed'])
        self.assertTrue(receipt['group_closure_certified_in_this_run'])
        self.assertTrue(receipt['kz_algebra_verification']['passed'])
        self.assertTrue(all(r['log_free_all_orders_certified'] for r in receipt['local_frobenius']))
        self.assertEqual(receipt['compact_identity_component'], 'SU(5)')
        self.assertEqual(receipt['projective_compact_closure'], 'PU(5)')
        self.assertEqual(receipt['complex_zariski_identity_component'], 'SL(5,C)')
        self.assertEqual(receipt['component_count'], 17)
        self.assertEqual(receipt['closure_lie_algebra_dimension'], 24)
        self.assertFalse(receipt['positive_invariant_hermitian_form_explicitly_computed'])
        self.assertFalse(receipt['worldwide_priority_claim'])
        json.dumps(receipt, allow_nan=False)

    def test_all_twenty_actual_spectral_blocks_are_separated_from_zero(self):
        proof = self.receipt['specialized_irreducibility']
        self.assertTrue(proof['passed'])
        self.assertTrue(proof['full_matrix_algebra_generated'])
        self.assertEqual(proof['edge_count'], 20)
        self.assertEqual(len(set(map(tuple, proof['certified_directed_edges']))), 20)
        for edge in proof['projector_blocks']:
            self.assertTrue(edge['nonzero_certified'])
            self.assertGreater(Q(edge['center_norm_lower_bound']), Q(edge['matrix_error_upper_bound']))
        self.assertLess(max(Q(x) for x in proof['projector_error_bounds']), Q(1, 10**7))

    def test_exact_local_order_determinant_and_orthogonal_obstruction(self):
        spectrum = local_spectrum_receipt()
        self.assertEqual(spectrum['local_order'], 17)
        self.assertEqual(spectrum['spectral_exponents'], list(SPECTRUM_EXPONENTS))
        self.assertEqual(spectrum['determinant_exponent'], 1)
        self.assertEqual(spectrum['determinant_image_order'], 17)
        self.assertEqual(spectrum['projective_self_duality_reflections'], [])
        self.assertTrue(spectrum['projective_symmetric_form_excluded'])
        # Other levels have exact spectral data but no automatic closure claim.
        self.assertEqual(local_spectrum_receipt(5)['determinant_image_order'], 7)
        self.assertFalse(local_spectrum_receipt(18)['distinct_eigenvalues'])
        self.assertFalse(local_spectrum_receipt(30)['distinct_eigenvalues'])
        self.assertFalse(local_spectrum_receipt(32)['distinct_eigenvalues'])

    def test_roots_are_analytic_rational_enclosures_with_branch_control(self):
        receipt = root_certificate()
        self.assertTrue(receipt['passed'])
        self.assertTrue(receipt['machin_branch_checked'])
        self.assertTrue(receipt['root_power17_enclosure_contains_one'])
        self.assertTrue(receipt['all_root_balls_pairwise_disjoint'])
        self.assertTrue(all(Q(r['modulus_error_bound']) < Q(1, 10**30) for r in receipt['roots']))
        root = seventeenth_roots()[1]
        self.assertGreater(root.center.imag, 0)
        self.assertGreater(root.center.real, 0)

    def test_commuting_diagonal_data_do_not_pass_irreducibility(self):
        roots = seventeenth_roots()
        matrix = tuple(tuple(roots[SPECTRUM_EXPONENTS[i]].center if i == j else C(0)
                             for j in range(5)) for i in range(5))
        radius = max(roots[r].radius for r in SPECTRUM_EXPONENTS)
        proof = irreducibility_receipt(MatrixBall(matrix, radius), MatrixBall(matrix, radius))
        self.assertFalse(proof['passed'])
        self.assertFalse(proof['irreducible_at_specified_level'])

    def test_loose_enclosures_do_not_prove_the_actual_blocks_nonzero(self):
        pair = self.receipt['loop_enclosures']
        u = MatrixBall(tuple(tuple(C(x) for x in row)
                             for row in pair['first_loop']['approximation_exact']), Q(1, 10))
        v = MatrixBall(tuple(tuple(C(x) for x in row)
                             for row in pair['second_loop_approximation_exact']), Q(1, 10))
        proof = irreducibility_receipt(u, v)
        self.assertFalse(proof['passed'])

    def test_fast_mode_leaves_specialized_group_gate_open(self):
        receipt = monodromy_receipt()
        self.assertTrue(receipt['passed'])
        self.assertFalse(receipt['group_closure_certified_in_this_run'])
        self.assertIsNone(receipt['compact_identity_component'])
        self.assertIsNone(receipt['specialized_irreducibility'])
        self.assertFalse(receipt['proof_gates']['infinite_image_certified'])

    def test_ball_and_specialization_input_contracts(self):
        with self.assertRaises(ArithmeticError):
            ComplexBall(C(1), Q(1)).inverse()
        with self.assertRaises(ValueError):
            ComplexBall(C(1), Q(-1))
        with self.assertRaises(ValueError):
            MatrixBall(identity(), Q(-1))
        with self.assertRaises(TypeError):
            monodromy_receipt(exhaustive=1)
        with self.assertRaises(ValueError):
            monodromy_receipt(level=5)
        for level in (True, 4.0, 3):
            with self.assertRaises(ValueError):
                local_spectrum_receipt(level)
        with self.assertRaises(ValueError):
            root_certificate(16)


if __name__ == '__main__':
    unittest.main()
