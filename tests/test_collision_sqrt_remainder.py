"""Independent checks of the square-supported remainder calculation."""
from fractions import Fraction as Q
from math import isqrt
import unittest

from perfectjet.collision_counting import exact_count, coefficient_sieve
from perfectjet.collision_intervals import Interval, asymptotic_constants, euler_gamma_bounds
from perfectjet.collision_majorant import majorant_bounds
from perfectjet.collision_sqrt_remainder import g_half_bounds, sqrt_remainder_bound


class SquareRootRemainderTests(unittest.TestCase):
    def test_residual_product_against_independent_longer_prime_product(self):
        # Trial division and algebraic sqrt intervals are independent of the
        # production sieve and its exp/log rational powers.
        primes = [n for n in range(2, 20001)
                  if all(n % d for d in range(2, isqrt(n) + 1))]
        partial = Interval(1)
        for p in primes:
            denominator = 1 << 80
            root_floor = isqrt(p * denominator * denominator)
            root = Interval(Q(root_floor, denominator), Q(root_floor + 1, denominator))
            partial *= 1 + 4 / (p * root) + Q(3, p * p)
        for cutoff in (2, 7, 100, 1000):
            bounds = g_half_bounds(cutoff)
            self.assertLessEqual(bounds['lower'], partial.lower)
            self.assertGreaterEqual(bounds['upper'], partial.upper)

    def test_remainder_encloses_independent_small_populations(self):
        values = coefficient_sieve(10000)
        constants = asymptotic_constants(1000)
        total, samples = 0, {1, 2, 3, 4, 8, 9, 16, 25, 64, 100, 997, 1000, 9999, 10000}
        for n, value in enumerate(values):
            total += value
            if n not in samples:
                continue
            for x in (Q(n), Q(n) + Q(1, 3)):
                argument = Interval(x)
                main = constants['C'] * argument * argument.log() + constants['K'] * argument
                result = sqrt_remainder_bound(x, 1000)
                self.assertLessEqual(total - main.lower, result['remainder_upper'])
                self.assertLessEqual(main.upper - total, result['remainder_upper'])

    def test_large_exact_replay_and_improvement_over_sigma_bound(self):
        X = 10**12
        exact = exact_count(X)
        constants = asymptotic_constants(10000)
        x = Interval(X)
        main = constants['C'] * x * x.log() + constants['K'] * x
        result = sqrt_remainder_bound(X, 10000)
        self.assertLessEqual(exact - main.lower, result['remainder_upper'])
        self.assertLessEqual(main.upper - exact, result['remainder_upper'])
        sigma = Q(3, 5)
        a = 1 - sigma
        c = 2 * euler_gamma_bounds() - 1
        coefficient = max(Q(6, 5), ((-1 - a*c).exp() / a).upper)
        old = (x.pow(sigma) * majorant_bounds(sigma, 10000)['upper'] * coefficient).upper
        self.assertLess(result['remainder_upper'], old)

    def test_divisor_harmonic_lemma_against_direct_enumeration(self):
        c = 2 * euler_gamma_bounds() - 1
        k = Q(6, 5)
        for denominator in (1, 3):
            for numerator in range(denominator, 120 * denominator, 7):
                T = Q(numerator, denominator)
                actual = sum((Q(sum(1 for d in range(1, n+1) if n % d == 0), n)
                              for n in range(1, numerator//denominator + 1)), Q(0))
                t = Interval(T)
                bound = t.log()**2 / 2 + (1+c)*t.log() + c + 2*k - k/t.pow(Q(1,2))
                self.assertLessEqual(actual, bound.lower)

    def test_strict_preflight(self):
        for bad in (True, False, 0, -1, 1.0, '100', None, 1 << 1025):
            with self.subTest(X=bad), self.assertRaises(ValueError):
                sqrt_remainder_bound(bad)
        for kwargs in ({'prime_cutoff':10001}, {'bits':31}, {'bits':True}):
            with self.assertRaises(ValueError):
                sqrt_remainder_bound(100, **kwargs)


if __name__ == '__main__':
    unittest.main()
