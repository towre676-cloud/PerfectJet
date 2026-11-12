import unittest
from fractions import Fraction as Q

from perfectjet.quotient_algebra import MonogenicQuotient


class QuotientAlgebraTests(unittest.TestCase):
    def setUp(self):
        # beta^3 - beta^2 - 9 beta + 11 = 0
        self.K = MonogenicQuotient([11, -9, -1, 1])
        self.beta = self.K.basis(1)

    def test_389_cubic_relation(self):
        self.assertEqual(self.K.power(self.beta, 3), (Q(-11), Q(9), Q(1)))

    def test_389_trace_matrix_and_discriminant(self):
        self.assertEqual(
            self.K.trace_matrix(),
            [[Q(3), Q(1), Q(19)],
             [Q(1), Q(19), Q(-5)],
             [Q(19), Q(-5), Q(155)]])
        self.assertEqual(self.K.discriminant(), Q(1556))

    def test_389_norm_witnesses(self):
        self.assertEqual(self.K.norm([-3, 1]), Q(-2))
        self.assertEqual(self.K.norm([-2, 1]), Q(3))

    def test_trace_formula(self):
        for a, b, c in [(1, 2, 3), (-4, 5, -7), (0, 0, 1)]:
            self.assertEqual(self.K.trace([a, b, c]), 3*a+b+19*c)

    def test_contracts(self):
        with self.assertRaises(ValueError):
            MonogenicQuotient([1, 2])
        with self.assertRaises(ValueError):
            self.K.element([1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
