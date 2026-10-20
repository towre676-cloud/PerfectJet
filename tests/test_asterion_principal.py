"""Exact checks of the principal polynomial E8 arithmetic."""

import unittest
from fractions import Fraction as Q

from perfectjet.asterion_principal import (
    EXPONENTS, PrincipalE8Basis, coupling_slots, monomial_transvectant,
)


class PrincipalE8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.basis = PrincipalE8Basis()

    def test_actual_248_dimensional_basis_and_inverse(self):
        self.assertEqual(sum(2 * m + 1 for m in EXPONENTS), 248)
        self.assertEqual(len(self.basis.vectors), 248)
        for key, vector in self.basis.vectors.items():
            self.assertEqual(self.basis.to_principal(vector), {key: Q(1)})
        vector = {i: Q((-1) ** i, i + 1) for i in range(248)}
        self.assertEqual(self.basis.to_chevalley(self.basis.to_principal(vector)), vector)

    def test_all_170_allowed_slots_and_principal_normalization(self):
        values = self.basis.couplings()
        self.assertEqual(len(coupling_slots()), 170)
        self.assertEqual(len(values), 170)
        for m in EXPONENTS:
            self.assertEqual(values[1, m, m], Q(1, 2))
        self.assertEqual(sum(x != 0 for x in values.values()), 170)

    def test_transvectant_sign_and_known_sl2_brackets(self):
        self.assertEqual(monomial_transvectant(1, 0, 1, 2, 1), 4)
        self.assertEqual(monomial_transvectant(1, 2, 1, 0, 1), -4)
        # b_(1,0)=e, b_(1,1)=-h, b_(1,2)=-f.
        self.assertEqual(self.basis.polynomial_basis_bracket((1, 0), (1, 2)), {(1, 1): Q(1)})
        self.assertEqual(self.basis.polynomial_basis_bracket((1, 1), (1, 0)), {(1, 0): Q(-2)})

    def test_all_30876_unordered_basis_brackets(self):
        result = self.basis.verify(exhaustive=True)
        self.assertEqual(result["bracket_pairs_checked"], 30876)
        self.assertTrue(result["bracket_replay_exhaustive"])
        self.assertEqual(result["chain_relations_checked"], 744)
        self.assertTrue(result["all_checks_passed"])

    def test_mixed_polynomial_bracket_and_jacobi(self):
        left = {(7, 3): Q(3, 5), (29, 31): Q(-2), (1, 1): Q(7)}
        right = {(11, 17): Q(5, 7), (19, 9): Q(2), (23, 27): Q(-1, 3)}
        third = {(13, 16): Q(-1), (17, 1): Q(9, 2)}
        g = self.basis.algebra
        self.assertEqual(self.basis.to_chevalley(self.basis.polynomial_bracket(left, right)),
                         g.bracket(self.basis.to_chevalley(left), self.basis.to_chevalley(right)))
        a = self.basis.polynomial_bracket(left, self.basis.polynomial_bracket(right, third))
        b = self.basis.polynomial_bracket(right, self.basis.polynomial_bracket(third, left))
        c = self.basis.polynomial_bracket(third, self.basis.polynomial_bracket(left, right))
        keys = set(a) | set(b) | set(c)
        self.assertTrue(all(a.get(k, 0) + b.get(k, 0) + c.get(k, 0) == 0 for k in keys))

    def test_receipt_lattice_data_are_exact(self):
        receipt = self.basis.receipt()
        self.assertEqual(receipt["verification"]["basis_rank"], 248)
        self.assertEqual(receipt["allowed_coupling_slots"], 170)
        self.assertEqual(len(receipt["highest_seeds"]), 8)
        self.assertEqual(len(receipt["height_blocks"]), 59)
        self.assertGreaterEqual(int(receipt["primitive_integer_column_lattice_index"]), 1)
        self.assertEqual(receipt["basis_absolute_determinant"]["denominator"], "1")
        product = 1
        for prime, power in receipt["basis_absolute_determinant"]["prime_power_factors"]:
            product *= prime ** power
        determinant = Q(1)
        for block in receipt["height_blocks"]:
            determinant *= Q(block["determinant"])
        self.assertEqual(product, abs(determinant))


if __name__ == "__main__":
    unittest.main()
