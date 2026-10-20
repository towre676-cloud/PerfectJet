"""Independent exact checks of the scoped DELL profile obstruction."""

from fractions import Fraction as Q
import json
import unittest

from perfectjet.dell_obstructions import (
    WITNESS_POSITIONS, bracket_profile_polynomials,
    coupling_boundary_certificate, coupling_identity_certificate, coupling_witness,
    forced_mode_certificate, inverse_profile_counterexample,
    obstruction_receipt, profile_bracket,
)


class DellParticlewiseObstructionTests(unittest.TestCase):
    def test_interpolation_certificate_for_all_couplings(self):
        result = coupling_identity_certificate()
        self.assertTrue(result["all_checks_passed"])
        self.assertEqual(result["maximum_coupling_degree"], 4)
        self.assertEqual(result["distinct_exact_evaluations"], 5)
        # Independent factorization and evaluations outside the interpolation panel.
        for t in (Q(-3), Q(2), Q(11, 7)):
            self.assertEqual(coupling_witness(t),
                             (t-1)*(5*t**3-21*t**2-21*t+105)/72)

    def test_witness_coefficient_and_nonzero_inverse_correction(self):
        self.assertEqual(coupling_witness(2), Q(19, 72))
        self.assertEqual(inverse_profile_counterexample(),
                         (Q(0), Q(-95, 216), Q(95, 1296), Q(0)))
        value = profile_bracket(WITNESS_POSITIONS, 2, (2, 3, 3),
                                lambda y: y+1/y,
                                lambda y: y-1/y)
        self.assertEqual(value, -Q(95, 216)+Q(95, 1296))

    def test_exact_coupling_boundary_uses_two_witnesses_and_bezout(self):
        result = coupling_boundary_certificate()
        self.assertTrue(result["passed"])
        self.assertTrue(result["bezout_identity_passed"])
        self.assertTrue(result["second_identity"]["all_checks_passed"])
        self.assertEqual(result["only_common_coupling_zero"], "1")
        self.assertEqual(result["bezout_result_ascending"],
                         ["-2821105", "2821105", "0", "0", "0", "0", "0"])

    def test_general_rational_profile_diagonal_identity(self):
        # A mixed Laurent profile, not the inverse-only counterexample.
        f = lambda y: y**3+2/y+Q(3, 7)
        g = lambda y: 3*y**3-2/y
        for t, u, v in ((Q(11, 7), Q(2), Q(5)), (Q(-3), Q(3), Q(7))):
            bracket = profile_bracket(WITNESS_POSITIONS, t, (u, v, v), f, g)
            predicted = coupling_witness(t)*(f(v)-f(u))*(f(v)*g(u)-f(u)*g(v))
            self.assertEqual(bracket, predicted)
            self.assertNotEqual(bracket, 0)

    def test_power_and_constant_profiles_are_positive_controls(self):
        for exponent in (-3, -1, 0, 1, 2, 4):
            for x, t in (((1, 3, 7), 2), ((2, 5, 11), Q(7, 3))):
                self.assertEqual(profile_bracket(x, t, (2, 3, 5),
                    lambda y: 7*y**exponent,
                    lambda y: 7*exponent*y**exponent), 0)

    def test_forced_current_mode_support_and_two_sign_conventions(self):
        result = forced_mode_certificate()
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["first_numerator_support"]), 3)
        self.assertEqual(len(result["first_denominator_support"]), 6)
        self.assertTrue(result["target_absent_from_first_numerator"])
        self.assertEqual(result["sign_stripped_H1_coefficient"], "-715/6144")
        self.assertEqual(result["KS_O0_inverse_O1_coefficient"], "715/6144")
        row = result["normalization_contributions"][0]
        self.assertEqual(row["denominator_coefficient"], "143/384")
        self.assertEqual(row["leading_numerator_coefficient"], "5/16")

    def test_free_coupling_is_degenerate_and_inputs_are_checked(self):
        self.assertEqual(bracket_profile_polynomials(coupling=1), ({}, {}, {}))
        with self.assertRaises(ValueError):
            bracket_profile_polynomials((1, 1, 3))
        with self.assertRaises(ValueError):
            profile_bracket((1, 3, 7), 2, (2, 3), lambda y: y, lambda y: y)

    def test_receipt_is_json_safe_and_scope_is_explicit(self):
        receipt = obstruction_receipt()
        self.assertTrue(receipt["passed"])
        self.assertTrue(receipt["analytic_proof_required"])
        self.assertFalse(receipt["worldwide_priority_claim"])
        self.assertIn("not a no-go for general DELL", receipt["scope"])
        self.assertIsNone(receipt["analytic_elliptic_extension"]["computed_nonzero_radius"])
        self.assertFalse(receipt["analytic_elliptic_extension"]["all_moduli_claim"])
        json.dumps(receipt)


if __name__ == "__main__":
    unittest.main()
