import json
import unittest
from fractions import Fraction as Q

from perfectjet.asterion_kz import (
    E8KZ, EIGENVALUES, CHANNELS, identity, inverse, matrix_add,
    matrix_multiply, matrix_scale, matrix_vector, kz_receipt, RationalComplex,
)


class E8KZTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system = E8KZ()

    def test_actual_sparse_casimir_derivation_and_tensor_certificates(self):
        s = self.system
        receipt = s.verify(samples=128)
        self.assertTrue(receipt["passed"], receipt)
        self.assertTrue(receipt["checks"]["complete_metric_invariance"])
        self.assertTrue(receipt["checks"]["complete_adjoint_quadratic_casimir_60"])
        self.assertEqual(receipt["independent_evaluation_quadruples"], 197)
        self.assertEqual(receipt["four_root_circuit_evaluations"], 64)
        self.assertEqual(receipt["complete_lowered_structure_entries_checked"], 8088)
        self.assertEqual(s.A_tensor[0], (Q(-60), Q(0), Q(0), Q(0), Q(12)))
        self.assertEqual(s.A, tuple(tuple(v if i == j else Q(0) for j in range(5))
                                   for i, v in enumerate(EIGENVALUES)))

    def test_rational_crossing_is_an_involution_and_transports_residue(self):
        s = self.system
        self.assertEqual(matrix_multiply(s.crossing, s.crossing), identity())
        self.assertEqual(matrix_multiply(s.crossing, matrix_multiply(s.A, s.crossing)), s.B)
        self.assertEqual(matrix_add(matrix_add(s.A, s.B), s.C), matrix_scale(identity(), -60))
        self.assertEqual(s.crossing[0][0], Q(1, 248))
        self.assertEqual(tuple(CHANNELS), (1, 248, 3875, 30380, 27000))

    def test_exact_certificate_rejects_perturbed_residue(self):
        s = E8KZ()
        rows = [list(r) for r in s.B]
        rows[0][1] += 1
        s.B = tuple(map(tuple, rows))
        self.assertFalse(s.verify(samples=0, verify_form=False)["passed"])

    def test_projectors_resolve_and_have_the_right_eigenvalue(self):
        s = self.system
        for value in EIGENVALUES:
            p = s.projector(value)
            self.assertEqual(matrix_multiply(p, p), p)
            self.assertEqual(matrix_multiply(s.A_tensor, p), matrix_scale(p, value))
            self.assertEqual(sum(p[i][i] for i in range(5)), 1)
        with self.assertRaises(ValueError):
            s.projector(3)

    def test_frobenius_residual_and_all_integrable_resonances(self):
        s = self.system
        for branch in range(5):
            result = s.frobenius(Q(1, 34), order=6, branch=branch)
            self.assertTrue(result["passed"])
            self.assertTrue(result["recurrence_residual_zero"])
            self.assertTrue(result["log_free_all_orders_certified"])
        certificate = s.wzw_resonance_certificate()
        self.assertTrue(certificate["passed"])
        self.assertEqual(certificate["exceptional_levels"], [18, 30, 32])
        for level, records in certificate["exceptional_level_checks"].items():
            self.assertTrue(all(r["log_free_all_orders_certified"] for r in records), level)
            self.assertTrue(all(event["zero_source"] for r in records for event in r["resonances"]))

    def test_actual_logarithm_and_obstruction_are_not_silently_dropped(self):
        s = self.system
        with_logs = s.frobenius(Q(1, 2), order=3, branch=3)
        self.assertTrue(with_logs["passed"])
        self.assertTrue(with_logs["has_logarithms"])
        self.assertTrue(with_logs["recurrence_residual_zero"])
        without_logs = s.frobenius(Q(1, 2), order=3, branch=3, logarithms=False)
        self.assertFalse(without_logs["passed"])
        self.assertTrue(without_logs["obstructions"])
        self.assertEqual(without_logs["obstructions"][0]["order"], 1)
        self.assertEqual(without_logs["obstructions"][0]["target_channel"], 27000)

    def test_controlled_real_transport_has_a_rational_analytic_error_bound(self):
        s = self.system
        low = s.continue_real([1, 0, 0, 0, 0], start=Q(1, 3), target=Q(3, 8),
                              hbar=Q(1, 34), order=12)
        high = s.continue_real([1, 0, 0, 0, 0], start=Q(1, 3), target=Q(3, 8),
                               hbar=Q(1, 34), order=24)
        difference = max(abs(Q(a)-Q(b)) for a, b in zip(low["approximation_exact"], high["approximation_exact"]))
        self.assertLessEqual(difference, Q(low["infinity_norm_error_bound"])+Q(high["infinity_norm_error_bound"]))
        self.assertLess(Q(high["infinity_norm_error_bound"]), Q(low["infinity_norm_error_bound"]))
        self.assertFalse(low["global_monodromy_certified"])
        zero = s.continue_real([1, 2, 3, 4, 5], start=Q(1, 3), target=Q(2, 3), hbar=0, order=6)
        self.assertEqual(zero["approximation_exact"], ["1", "2", "3", "4", "5"])
        self.assertEqual(zero["infinity_norm_error_bound"], "0")

    def test_arithmetic_and_json_receipt(self):
        arithmetic = self.system.arithmetic_receipt()
        self.assertEqual(arithmetic["denominator_primes"], [2, 3, 5, 7, 31])
        self.assertEqual(len(arithmetic["matrix_sha256"]), 64)
        receipt = kz_receipt(order=4, samples=16, exhaustive=False)
        json.dumps(receipt)
        self.assertTrue(receipt["passed"])
        self.assertFalse(receipt["new_racah_matrix_claim"])
        self.assertFalse(receipt["dense_248_power4_array_used"])
        low = receipt["low_level_formal_system_diagnostics"]
        self.assertEqual(low["1"][0]["resonances"][0]["source_log_coefficients"], ["12/6727"])
        self.assertEqual(low["2"][1]["resonances"][0]["source_log_coefficients"], ["3/1736"])
        self.assertTrue(low["1"][0]["has_logarithms"])
        self.assertTrue(low["2"][1]["has_logarithms"])
        self.assertFalse(receipt["low_level_five_channel_integrable_claim"])
        self.assertEqual(receipt["all_positive_integer_formal_resonant_levels"], [1, 2, 18, 30, 32])

    def test_gaussian_rational_field_and_bounded_complex_transport(self):
        x, y = RationalComplex((Q(1, 3), Q(2, 5))), RationalComplex((Q(-3, 7), Q(1, 2)))
        self.assertEqual((x*y)/y, x)
        self.assertEqual(x+y-y, x)
        self.assertEqual((1/x)*x, RationalComplex(1))
        with self.assertRaises(TypeError):
            RationalComplex((0.5, 0))
        path = [(Q(1, 3), 0), (Q(3, 8), Q(1, 32))]
        low = self.system.continue_polygon(path, hbar=Q(1, 34), order=12)
        high = self.system.continue_polygon(path, hbar=Q(1, 34), order=20)
        difference = max(sum((RationalComplex(a)-RationalComplex(b)).norm_one()
                             for a, b in zip(ar, br))
                         for ar, br in zip(low["approximation_exact"], high["approximation_exact"]))
        # Our modulus-one comparison norm is at most twice the certified
        # ordinary complex-modulus matrix infinity norm.
        self.assertLessEqual(difference, 2*(Q(low["infinity_norm_error_bound"])+Q(high["infinity_norm_error_bound"])))
        self.assertTrue(high["passed"])
        self.assertLess(Q(high["infinity_norm_error_bound"]), Q(low["infinity_norm_error_bound"]))
        self.assertFalse(high["single_loop_holonomy_certified"])
        zero = self.system.continue_polygon(path+path[-2::-1], hbar=0, order=2)
        self.assertTrue(zero["single_loop_holonomy_certified"])
        self.assertEqual(zero["infinity_norm_error_bound"], "0")
        self.assertEqual([[RationalComplex(x) for x in row] for row in zero["approximation_exact"]],
                         [[RationalComplex(x) for x in row] for row in identity()])
        for bad in ([(-1, 0), (1, 0)], [(Q(1, 2), 0), (Q(3, 2), 0)], [(0, 0), (0, 1)]):
            with self.assertRaises(ValueError):
                self.system.continue_polygon(bad, hbar=Q(1, 34))

    def test_zero_connection_does_not_receive_a_nonabelian_claim(self):
        receipt = self.system.monodromy_pair_receipt(hbar=0, order=2)
        self.assertTrue(receipt["passed"])
        self.assertTrue(receipt["two_generator_approximations_certified"])
        self.assertFalse(receipt["nonabelian_image_certified"])
        self.assertEqual(receipt["commutator_difference_norm_lower_bound"], "0")
        self.assertEqual(receipt["commutator_difference_error_upper_bound"], "0")
        self.assertFalse(receipt["monodromy_density_claim"])

    def test_complex_enclosure_against_exact_infinite_series_solutions(self):
        # Independent scalar-pole calibration: Y' = hbar*Y/z has exact
        # rational-complex endpoints even when its local Taylor series is
        # infinite. This does not compare two numerical resolutions.
        scalar = E8KZ.__new__(E8KZ)
        scalar.A_tensor = identity()
        scalar.B_tensor = tuple(tuple(Q(0) for _ in range(5)) for _ in range(5))
        cases = [((Q(1, 4), Q(1, 4)), Q(-1), RationalComplex((1, -1))),
                 ((Q(3, 8), Q(1, 2)), Q(1, 2), RationalComplex((1, Q(1, 2))))]
        for endpoint, hbar, expected in cases:
            receipt = scalar.continue_polygon([(Q(1, 2), 0), endpoint], hbar=hbar,
                                               order=20, precision_bits=96, step_ratio=Q(1, 8))
            actual_upper = max(sum((RationalComplex(x)-(expected if i == j else 0)).norm_one()
                                   for j, x in enumerate(row))
                               for i, row in enumerate(receipt["approximation_exact"]))
            self.assertLessEqual(actual_upper, Q(receipt["infinity_norm_error_bound"]))
            self.assertTrue(receipt["passed"])

    def test_scope_and_input_contracts(self):
        s = self.system
        for level in (1, 2, 3, True, 4.0):
            with self.assertRaises((ValueError, TypeError)):
                s.level_parameter(level)
        with self.assertRaises(TypeError):
            s.frobenius(0.5)
        with self.assertRaises(ValueError):
            s.frobenius(1, order=-1)
        with self.assertRaises(ValueError):
            s.frobenius(1, branch=5)
        with self.assertRaises(ValueError):
            s.continue_real([1, 0, 0, 0, 0], start=0, target=Q(1, 2), hbar=1)
        with self.assertRaises(TypeError):
            kz_receipt(include_matrices=1)
        with self.assertRaises(ValueError):
            s.continue_real([1, 0, 0, 0, 0], start=Q(1, 3), target=Q(1, 2), hbar=10**8)


if __name__ == "__main__":
    unittest.main()
