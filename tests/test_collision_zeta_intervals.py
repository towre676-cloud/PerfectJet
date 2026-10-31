"""Independent zeta references and explicit Euler--Maclaurin error checks."""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from math import comb
import unittest

from perfectjet.collision_zeta_intervals import zeta_two_constants


def _atan_inverse_bounds(denominator, terms=100):
    x = Q(1, denominator)
    partial = sum(((-1)**k * x**(2*k + 1) / (2*k + 1)
                   for k in range(terms)), Q(0))
    endpoint = partial + (-1)**terms * x**(2*terms + 1) / (2*terms + 1)
    return min(partial, endpoint), max(partial, endpoint)


def _eta_references():
    """Independent numerical reference, using Euler's alternating transform.

    This deliberately avoids Euler--Maclaurin and Bernoulli corrections.
    It is a numerical crosscheck; the explicit production remainder supplies
    the proof of inclusion, rather than this reference calculation.
    """
    with localcontext() as ctx:
        ctx.prec = 240
        terms = 320
        values = [Decimal(1) / Decimal(n*n) for n in range(1, terms + 1)]
        log_values = [Decimal(n).ln() * values[n-1] for n in range(1, terms + 1)]
        eta, eta_prime = Decimal(0), Decimal(0)
        for k in range(terms):
            weight = Decimal(2)**(-k - 1)
            eta += weight * sum((Decimal((-1)**j * comb(k, j)) * values[j]
                                 for j in range(k + 1)), Decimal(0))
            eta_prime -= weight * sum((Decimal((-1)**j * comb(k, j)) * log_values[j]
                                       for j in range(k + 1)), Decimal(0))
        return Q(2 * eta), Q(2 * eta_prime - 2 * Decimal(2).ln() * eta)


class ZetaIntervalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.eta_zeta, cls.eta_derivative = _eta_references()
        a, b = _atan_inverse_bounds(5), _atan_inverse_bounds(239)
        pi_lower, pi_upper = 16*a[0] - 4*b[1], 16*a[1] - 4*b[0]
        cls.zeta_machin = (pi_lower*pi_lower/6, pi_upper*pi_upper/6)

    def assertContains(self, interval, value):
        self.assertLessEqual(interval.lower, value)
        self.assertGreaterEqual(interval.upper, value)

    def test_zeta_two_against_rational_machin_identity(self):
        for bits in (32, 80, 128, 256):
            result = zeta_two_constants(bits)
            self.assertContains(result['zeta2'], self.zeta_machin[0])
            self.assertContains(result['zeta2'], self.zeta_machin[1])

    def test_independent_alternating_transform_derivative(self):
        for bits in (32, 80, 128, 256):
            result = zeta_two_constants(bits)
            self.assertContains(result['zeta2'], self.eta_zeta)
            self.assertContains(result['zeta2_derivative'], self.eta_derivative)
            self.assertLess(result['zeta2_derivative'].upper, 0)
            self.assertLess(result['zeta2'].width, Q(1024, 1 << bits))
            self.assertLess(result['zeta2_derivative'].width, Q(1024, 1 << bits))

    def test_absolute_remainders_cover_coarse_and_fine_formulas(self):
        for cutoff, order in ((1, 1), (2, 1), (3, 2), (10, 3), (32, 8), (128, 16)):
            result = zeta_two_constants(summation_cutoff=cutoff, order=order)
            self.assertContains(result['zeta2'], self.eta_zeta)
            self.assertContains(result['zeta2_derivative'], self.eta_derivative)
            evidence = result['evidence']
            self.assertGreater(evidence['zeta_remainder_upper'], 0)
            self.assertGreater(evidence['derivative_remainder_upper'], 0)
            self.assertEqual(evidence['summation_cutoff'], cutoff)
            self.assertEqual(evidence['order'], order)
        coarse = zeta_two_constants(summation_cutoff=4, order=2)
        fine = zeta_two_constants(summation_cutoff=64, order=12)
        for key in ('zeta2', 'zeta2_derivative'):
            self.assertLess(fine[key].width, coarse[key].width)

    def test_known_rational_bernoulli_remainder_coefficients(self):
        # Order one gives E=|B2|/N^3; order two gives E=|B4|/N^5.
        for cutoff in (1, 2, 10):
            first = zeta_two_constants(summation_cutoff=cutoff, order=1)
            second = zeta_two_constants(summation_cutoff=cutoff, order=2)
            self.assertEqual(first['evidence']['zeta_remainder_upper'], Q(1, 6*cutoff**3))
            self.assertEqual(second['evidence']['zeta_remainder_upper'], Q(1, 30*cutoff**5))

    def test_strict_preflight_work_budgets(self):
        for bits in (True, 0, 31, 257, '80', 80.0):
            with self.assertRaises(ValueError):
                zeta_two_constants(bits)
        for key, values in {'summation_cutoff':(True, 0, -1, 4097, 2.0, '64'),
                            'order':(True, 0, -1, 33, 12.0, '12')}.items():
            for value in values:
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    zeta_two_constants(**{key:value})


if __name__ == '__main__':
    unittest.main()
