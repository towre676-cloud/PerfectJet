"""Independent finite certificates for the actual change of E8 charts."""

import json
import unittest
from fractions import Fraction
from itertools import permutations

from perfectjet.asterion_jordan import Cyclotomic5, ONE, ZETA, a4_bracket
from perfectjet.asterion_transport import E8ChartTransport, transport_receipt


class E8ChartTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.transport = E8ChartTransport()

    def test_rational_root_columns_are_monomial_and_cartan_has_rank_eight(self):
        t = self.transport
        self.assertEqual(len(t.images), 248)
        self.assertTrue(all(len(image) == 1 for image in t.images[8:]))
        self.assertEqual(len({next(iter(image)) for image in t.images[8:]}), 240)
        self.assertTrue(all(isinstance(value, Fraction)
                            for image in t.images for value in image.values()))
        self.assertEqual(len(t._cartan_inverse), 8)
        self.assertTrue(t.simple_cartan_verified)
        for image in t.images[:8]:
            for copy in range(2):
                self.assertEqual(sum(image.get(("m", copy, i, i), 0) for i in range(5)), 0)

    def test_intertwines_all_30628_basis_brackets(self):
        receipt = self.transport.verify_intertwining()
        self.assertTrue(receipt["passed"], receipt)
        self.assertTrue(receipt["exhaustive"])
        self.assertEqual(receipt["basis_pairs_checked"], 30_628)

    def test_all_three_basis_roundtrips(self):
        receipt = self.transport.verify_roundtrips()
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["chevalley_a4_basis_roundtrips"], 248)
        self.assertEqual(receipt["chevalley_jordan_basis_roundtrips"], 248)
        self.assertEqual(receipt["jordan_chevalley_basis_roundtrips"], 248)

    def test_general_field_vectors_transport_brackets_between_all_charts(self):
        t = self.transport
        x = {0: 2-ZETA, 27: (1+ZETA**2)/7, 201: -3}
        y = {3: ZETA**3, 90: Fraction(2, 5), 227: 1+ZETA}
        bracket = t.chevalley_bracket(x, y)
        self.assertEqual(t.chevalley_to_a4(bracket),
                         a4_bracket(t.chevalley_to_a4(x), t.chevalley_to_a4(y)))
        self.assertEqual(t.chevalley_to_jordan(bracket),
                         t.jordan.bracket(t.chevalley_to_jordan(x), t.chevalley_to_jordan(y)))
        self.assertEqual(t.jordan_to_chevalley(t.chevalley_to_jordan(x)),
                         {index: Cyclotomic5(value) for index, value in x.items()})

    def test_rejects_traceful_or_unknown_ambient_input(self):
        t = self.transport
        with self.assertRaises(ValueError):
            t.a4_to_chevalley({("m", 0, 0, 0): 1})
        with self.assertRaises(ValueError):
            t.a4_to_chevalley({("w", 0, (), ()): 1})
        with self.assertRaises(IndexError):
            t.chevalley_to_a4({248: 1})

    def test_transport_checker_rejects_a_corrupted_root_column(self):
        t = E8ChartTransport()
        corrupted = list(t.images)
        index = next(iter(t.chevalley.simple_e(0)))
        corrupted[index] = {token: -value for token, value in corrupted[index].items()}
        t.images = tuple(corrupted)
        receipt = t.verify_intertwining(exhaustive=False)
        self.assertFalse(receipt["passed"], receipt)

    def test_rational_core_bracket_agrees_with_field_extension(self):
        t = self.transport
        x, y = {0: Fraction(1, 3), 81: 2}, {7: -2, 97: Fraction(3, 11)}
        self.assertEqual(t.chevalley_bracket(x, y),
                         {i: Cyclotomic5(c) for i, c in t.chevalley.bracket(x, y).items()})

    def test_receipt_is_exact_json_safe_and_scope_explicit(self):
        receipt = transport_receipt(exhaustive=False, include_columns=True)
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["construction_field"], "Q")
        self.assertFalse(receipt["intertwining"]["exhaustive"])
        self.assertFalse(receipt["new_simple_lie_algebra_claim"])
        self.assertEqual(receipt["cartan_transport_determinant"], "1/5")
        self.assertTrue(receipt["cartan_inverse_integral"])
        self.assertTrue(receipt["root_columns_have_unit_coefficients"])
        self.assertEqual(receipt["cartan_lattice"][
            "standard_a4_cartan_lattice_index_in_chevalley_cartan"], 5)
        self.assertFalse(receipt["cartan_lattice"][
            "jordan_fourier_basis_unimodular_over_Z_claim"])
        self.assertEqual(len(receipt["rational_ambient_columns"]), 248)
        json.dumps(receipt)

    def test_index_five_cartan_lattice_with_independent_determinants(self):
        t = self.transport

        # Leibniz expansion is independent of the implementation's Gaussian
        # elimination determinant. Skip zero terms before computing their sign.
        def determinant(matrix):
            value = Fraction(0)
            for permutation in permutations(range(8)):
                term = Fraction(1)
                for row, col in enumerate(permutation):
                    term *= matrix[row][col]
                    if not term:
                        break
                if term:
                    inversions = sum(permutation[i] > permutation[j]
                                     for i in range(8) for j in range(i+1, 8))
                    value += (-1 if inversions % 2 else 1)*term
            return value

        self.assertEqual(determinant(t.cartan_coordinate_matrix), Fraction(1, 5))
        self.assertEqual(determinant(t.standard_a4_cartan_in_chevalley), 5)
        self.assertTrue(all(value.denominator == 1 for row in t._cartan_inverse for value in row))
        self.assertTrue(all(value.denominator == 1
                            for row in t.standard_a4_cartan_in_chevalley for value in row))
        # The asserted smaller lattice really is the span of the eight
        # standard A4 simple coroots, with the exact declared basis.
        for copy in range(2):
            for col in range(4):
                column = 4*copy+col
                coordinates = {row: t.standard_a4_cartan_in_chevalley[row][column]
                               for row in range(8) if t.standard_a4_cartan_in_chevalley[row][column]}
                self.assertEqual(t.chevalley_to_a4(coordinates),
                    {("m", copy, col, col): ONE, ("m", copy, col+1, col+1): -ONE})


if __name__ == "__main__":
    unittest.main()
