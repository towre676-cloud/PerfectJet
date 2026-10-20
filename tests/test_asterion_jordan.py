import json
import random
import unittest
from fractions import Fraction
from itertools import combinations

from perfectjet.asterion_jordan import (
    Cyclotomic5, JordanE8, ZETA, ZETA_POWERS, ZERO, ONE, LABELS,
    a4_bracket, exterior_star, grade_add, naive_permutation_counterexample,
    naive_permutation_no_go, same_line, construction_receipt,
)


class Cyclotomic5Tests(unittest.TestCase):
    def test_exact_field_relation_inverse_and_conjugation(self):
        self.assertEqual(sum(ZETA_POWERS, ZERO), ZERO)
        self.assertEqual(ZETA**5, ONE)
        for x in (1+2*ZETA-ZETA**3, (ZETA**2+3)/5, 7-ZETA+4*ZETA**3):
            self.assertEqual(x*x.inverse(), ONE)
            self.assertEqual(x.conjugate().conjugate(), x)
            self.assertEqual(x.conjugate()*x, (x.conjugate()*x).conjugate())
        self.assertEqual(hash(Cyclotomic5(Fraction(2, 3))), hash(Fraction(2, 3)))
        with self.assertRaises(ZeroDivisionError):
            ZERO.inverse()
        with self.assertRaises(TypeError):
            Cyclotomic5(0.5)
        with self.assertRaises(TypeError):
            Cyclotomic5((0.1, 0, 0, 0))

    def test_exterior_product_and_contraction_have_the_source_convention(self):
        self.assertEqual(exterior_star((0,), (1,)), ((0, 1), 1))
        self.assertEqual(exterior_star((1,), (0,)), ((0, 1), -1))
        self.assertIsNone(exterior_star((0,), (0,)))
        # x*y = volume(y wedge x) when the degrees add to five.
        self.assertEqual(exterior_star((0, 1), (2, 3, 4)), ((), 1))
        self.assertEqual(exterior_star((0, 1, 2, 3), (1, 2, 3, 4)), ((1, 2, 3), 1))


class JordanE8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.algebra = JordanE8()

    def test_all_248_vectors_are_independent_and_have_the_declared_grade(self):
        a = self.algebra
        self.assertEqual(len(a.labels), 248)
        for label in a.labels:
            vector = a.basis_vector(label)
            self.assertEqual(a.from_a4(vector), {label: ONE})
            for which, coordinate in (("grade", 0), ("clock", 1), ("shift", 2)):
                expected = {t: c*ZETA_POWERS[label[coordinate]] for t, c in vector.items()}
                self.assertEqual(a.automorphism(vector, which), expected)

    def test_full_fourier_roundtrip_and_rejection_of_traceful_input(self):
        a = self.algebra
        vector = {label: Cyclotomic5((n % 7-3, n % 3, Fraction(1, n+1), 0))
                  for n, label in enumerate(a.labels)}
        self.assertEqual(a.from_a4(a.to_a4(vector)), vector)
        with self.assertRaises(ValueError):
            a.from_a4({("m", 0, 0, 0): 1})
        with self.assertRaises(ValueError):
            a.basis_vector((0, 0, 0, 0))
        for label in ((False, 0, 1, 0), (0, 0, 1, True), (0.0, 0, 1, 0)):
            with self.assertRaises(ValueError):
                a.basis_vector(label)
        with self.assertRaises(ValueError):
            a.grade_kernel((False, 0, 1), (1, 2, 3))
        with self.assertRaises(ValueError):
            a.gauge_transform({(False, 0, 1): ((1, 0), (0, 1))})

    def test_actual_character_projector_selects_only_the_requested_grade(self):
        a = self.algebra
        vector = {(0, 0, 1, 0): 2, (1, 3, 4, 1): ZETA, (1, 3, 4, 0): -3}
        raw = a.to_a4(vector)
        for grade in ((0, 0, 0), (0, 0, 1), (1, 3, 4), (4, 1, 2)):
            expected = a.to_a4({k: v for k, v in vector.items() if k[:3] == grade})
            projected = a.project_grade(raw, grade)
            self.assertEqual(projected, expected)
            self.assertEqual(a.project_grade(projected, grade), projected)

    def test_all_7440_maps_replay_every_ambient_coefficient(self):
        a = self.algebra
        kernels = a.all_grade_kernels(check=True)
        self.assertEqual(len(kernels), 7440)
        # This test verifies all 29,760 cross-line unordered basis brackets,
        # including zero coefficients, against the actual exterior model.
        self.assertEqual(sum(bool(c) for kernel in kernels.values()
                             for row in kernel for col in row for c in col), 34080)
        receipt = a.kernel_receipt(kernels)
        self.assertEqual(receipt["distinct_nonzero_coefficients"], 50)
        self.assertEqual(receipt["power_basis_denominator_lcm"], 1)
        self.assertEqual(receipt["max_absolute_power_basis_coefficient"], "2")
        self.assertTrue(receipt["closed_free_Z_zeta5_lattice"])
        self.assertFalse(receipt["same_Chevalley_Z_lattice_claim"])
        self.assertEqual(len(receipt["kernel_sha256"]), 64)
        for left, right in list(kernels)[::113]:
            for r in range(2):
                for s in range(2):
                    direct = a.basis_bracket((*left, r), (*right, s))
                    reverse = a.basis_bracket((*right, s), (*left, r))
                    self.assertEqual(reverse, {k: -v for k, v in direct.items()})

    def test_31_cartan_lines_partition_and_commute_in_the_actual_bracket(self):
        receipt = self.algebra.verify_cartans()
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["ambient_brackets_checked"], 868)
        self.assertEqual(receipt["normalizer_minors_checked"], 3720)
        self.assertEqual(receipt["normalizer_dimension_each"], 8)
        self.assertEqual(len({label for line in self.algebra.cartan_lines() for label in line}), 248)

    def test_jacobi_on_a_reproducible_panel_with_scope_reported(self):
        rng = random.Random(734)
        panel = [rng.sample(LABELS, 3) for _ in range(10000)]
        receipt = self.algebra.verify_jacobi(panel)
        self.assertTrue(receipt["passed"])
        self.assertFalse(receipt["exhaustive"])
        self.assertEqual(receipt["triples_checked"], 10000)

    def test_exhaustive_jacobi_with_exact_integer_cyclotomic_products(self):
        receipt = self.algebra.verify_jacobi()
        self.assertTrue(receipt["passed"])
        self.assertTrue(receipt["exhaustive"])
        self.assertEqual(receipt["triples_checked"], 2511496)
        self.assertEqual(receipt["common_coefficient_denominator"], 1)

    def test_generic_bracket_transport_and_fiber_gauge(self):
        a = self.algebra
        x = {(0, 1, 2, 0): 2, (1, 3, 4, 1): ZETA}
        y = {(2, 1, 0, 0): ZETA**3, (0, 4, 1, 1): -1}
        self.assertEqual(a.to_a4(a.bracket(x, y)), a4_bracket(a.to_a4(x), a.to_a4(y)))
        grade = (0, 1, 2)
        gauge = a.gauge_transform({grade: ((1, ZETA), (0, 2))})
        self.assertEqual(gauge.from_original(gauge.to_original(x)), x)
        self.assertEqual(gauge.to_original(gauge.bracket(x, y)),
                         a.bracket(gauge.to_original(x), gauge.to_original(y)))
        with self.assertRaises(ValueError):
            a.gauge_transform({grade: ((1, 2), (2, 4))})

    def test_plain_degree_permutation_fails_with_an_exact_witness(self):
        self.assertEqual(naive_permutation_no_go()["derived_dimension_bound"], 124)
        witness = naive_permutation_counterexample(self.algebra)
        self.assertTrue(witness["exact_mismatch"])
        self.assertNotEqual(witness["mapped_original_bracket"], witness["bracket_of_mapped_inputs"])

    def test_receipt_is_json_serializable_and_does_not_overclaim(self):
        receipt = construction_receipt()
        json.dumps(receipt)
        self.assertFalse(receipt["integral_lattice_claim"])
        self.assertFalse(receipt["new_simple_lie_algebra_claim"])


if __name__ == "__main__":
    unittest.main()
