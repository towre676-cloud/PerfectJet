"""Exact structural certificates for the generated E8 algebra."""

import json
import unittest
from fractions import Fraction
from itertools import combinations

from perfectjet.asterion_e8 import E8LieAlgebra, e8_receipt, encode_vector


class E8ConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.algebra = E8LieAlgebra()

    def test_reflection_generated_roots_are_complete_norm_two_vectors(self):
        a = self.algebra
        self.assertEqual((len(a.roots), a.dimension), (240, 248))
        self.assertEqual(max(map(sum, a.roots)), 29)
        self.assertEqual(sum(sum(root) > 0 for root in a.roots), 120)
        for alpha in a.roots:
            self.assertEqual(a.inner_product(alpha, alpha), 2)
            self.assertTrue(all(x >= 0 for x in alpha) or all(x <= 0 for x in alpha))
            self.assertIn(tuple(-x for x in alpha), a.root_index)

    def test_cartan_chevalley_and_serre_relations(self):
        a = self.algebra
        for i in range(8):
            for j in range(8):
                self.assertEqual(a.bracket(a.cartan_vector(i), a.cartan_vector(j)), {})
                self.assertEqual(a.bracket(a.simple_e(i), a.simple_f(j)),
                                 a.cartan_vector(i) if i == j else {})
                coefficient = a.cartan_matrix[i][j]
                expected = {k: coefficient * v for k, v in a.simple_e(j).items() if coefficient}
                self.assertEqual(a.bracket(a.cartan_vector(i), a.simple_e(j)), expected)
                if i != j:
                    vector = a.simple_e(j)
                    for _ in range(1 - coefficient):
                        vector = a.bracket(a.simple_e(i), vector)
                    self.assertEqual(vector, {})

    def test_opposite_brackets_are_coroots(self):
        a = self.algebra
        for alpha in a.roots:
            negative = tuple(-x for x in alpha)
            expected = {i: Fraction(value) for i, value in enumerate(alpha) if value}
            self.assertEqual(a.basis_bracket(a.root_index[alpha], a.root_index[negative]), expected)

    def test_skew_symmetry_and_integer_structure_constants_on_all_pairs(self):
        a = self.algebra
        for i, j in combinations(range(248), 2):
            left = a.basis_bracket(i, j)
            right = a.basis_bracket(j, i)
            self.assertEqual(left, {k: -v for k, v in right.items()})
            self.assertTrue(all(isinstance(value, Fraction) and value.denominator == 1
                                for value in left.values()))

    def test_jacobi_exhaustively_on_all_distinct_basis_triples(self):
        receipt = self.algebra.verify_jacobi("full")
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["checked"], 2_511_496)
        self.assertTrue(receipt["exhaustive_distinct_triples"])

    def test_corrupting_one_cocycle_pair_breaks_jacobi(self):
        class CorruptedCocycle(E8LieAlgebra):
            def cocycle_sign(self, alpha, beta):
                sign = super().cocycle_sign(alpha, beta)
                if {alpha, beta} == {self.simple_roots[0], self.simple_roots[1]}:
                    return -sign
                return sign

        receipt = CorruptedCocycle().verify_jacobi("generators")
        self.assertFalse(receipt["passed"])
        self.assertTrue(receipt["residual"])

    def test_fractional_input_bilinearity(self):
        a = self.algebra
        e = {k: v / 3 for k, v in a.simple_e(0).items()}
        f = {k: 7 * v / 5 for k, v in a.simple_f(0).items()}
        self.assertEqual(a.bracket(e, f), {0: Fraction(7, 15)})


class E8CoxeterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.algebra = E8LieAlgebra()

    def test_order_thirty_signed_orbits_and_computed_cartan_polynomial(self):
        receipt = self.algebra.coxeter_receipt()
        self.assertTrue(receipt["order_thirty_on_all_basis_vectors"])
        self.assertEqual(receipt["root_orbit_lengths"], [30] * 8)
        self.assertEqual(receipt["signed_monodromy"], [1] * 8)
        self.assertEqual(receipt["cartan_characteristic_polynomial_ascending"],
                         [1, 1, 0, -1, -1, -1, 0, 1, 1])
        self.assertTrue(receipt["cartan_characteristic_polynomial_is_phi30"])
        self.assertEqual(sum(receipt["phase_multiplicities"]), 248)

    def test_coxeter_is_lie_automorphism_on_every_basis_pair(self):
        receipt = self.algebra.verify_coxeter_equivariance()
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["checked"], 30_628)

    def test_1920_seed_kernel_reconstructs_every_root_root_bracket(self):
        receipt = self.algebra.verify_coxeter_kernel()
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["checked"], 57_600)
        self.assertEqual(receipt["seed_brackets"], 1_920)
        # A caller cannot mutate the cached certificate through the public copy.
        kernel = self.algebra.orbit_kernel()
        kernel.clear()
        self.assertEqual(len(self.algebra.orbit_kernel()), 1_920)

    def test_polynomial_variable_is_automorphism_not_scalar_multiplication(self):
        a = self.algebra
        x, y = a.simple_e(0), a.simple_f(0)
        bracket = a.bracket(x, y)
        self.assertEqual(a.bracket(a.coxeter(x), a.coxeter(y)), a.coxeter(bracket))
        self.assertNotEqual(a.bracket(a.coxeter(x), a.coxeter(y)), a.coxeter(bracket, 2))

    def test_json_safe_receipt_and_fraction_encoding(self):
        receipt = e8_receipt()
        self.assertTrue(receipt["passed"], receipt)
        self.assertIn('"passed": true', json.dumps(receipt))
        self.assertEqual(encode_vector({3: Fraction(2, 7), 1: Fraction(-3), 9: 0}),
                         [[1, "-3"], [3, "2/7"]])


if __name__ == "__main__":
    unittest.main()
