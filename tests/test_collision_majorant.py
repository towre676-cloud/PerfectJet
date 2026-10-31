"""Independent algebra, convexity tails and absolute-coefficient norm checks."""
from fractions import Fraction as Q
from math import gcd
import unittest

from perfectjet.collision_majorant import (
    majorant_bounds, wheel_power_tail, zeta_real_bounds,
)


def rational_power_bracket(base, exponent, bits=100):
    """Independent integer-bisection oracle for positive rational powers.

    Used here only for base**(-a/b), avoiding the production log/exp series.
    """
    a, b = -exponent.numerator, exponent.denominator
    scale = 1 << bits
    low, high = 0, scale
    target = scale ** b
    multiplier = base ** a
    while low + 1 < high:
        middle = (low + high) // 2
        if middle ** b * multiplier <= target:
            low = middle
        else:
            high = middle
    return Q(low, scale), Q(high, scale)


class CollisionMajorantTests(unittest.TestCase):
    def test_extracted_factor_identity_is_exact(self):
        for x in (Q(1, 2), Q(1, 3), Q(2, 7), Q(3, 5), Q(1, 100)):
            local = 1 + 2 * x * x / (1 - x) ** 2
            self.assertEqual(local * (1 - x * x) ** 2, 1 + 4 * x ** 3 + 3 * x ** 4)

    def test_wheel_tail_encloses_independent_long_residue_sum(self):
        # Integer powers make this oracle entirely rational, including its
        # independently bounded remainder beyond the finite comparison range.
        for cutoff in (2, 5, 7, 30, 211):
            bound = wheel_power_tail(2, cutoff)
            partial = sum((Q(1, n * n) for n in range(cutoff + 1, 5001)
                           if gcd(n, 210) == 1 or n in (2, 3, 5, 7)), Q(0))
            self.assertGreater(bound, partial)
            self.assertLess(bound, Q(1, cutoff))
        # Beyond a full wheel the leading density saves more than a factor 3.
        self.assertLess(wheel_power_tail(2, 1000), Q(1, 3000))

    def test_zeta_convexity_interval_against_root_bisection(self):
        exponent = Q(3, 2)
        lower_sum = upper_sum = Q(0)
        for n in range(1, 2001):
            lo, hi = rational_power_bracket(n, -exponent, bits=80)
            lower_sum += lo
            upper_sum += hi
        # Integral test bounds the remaining infinite tail independently.
        tail_lo = rational_power_bracket(2001, Q(-1, 2), bits=80)[0] * 2
        tail_hi = rational_power_bracket(2000, Q(-1, 2), bits=80)[1] * 2
        independent_lower, independent_upper = lower_sum + tail_lo, upper_sum + tail_hi
        zeta = zeta_real_bounds(exponent, 64)
        self.assertLess(zeta.lower, independent_upper)
        self.assertGreater(zeta.upper, independent_lower)
        self.assertLess(zeta.width, Q(1, 100000))

    def test_norm_encloses_independent_prime_product(self):
        sigma = Q(3, 4)
        # A separate trial-division inventory and root bisection form the
        # direct absolute local product, independently of the extraction.
        lower = upper = Q(1)
        for p in range(2, 1001):
            if any(p % d == 0 for d in range(2, int(p ** 0.5) + 1)):
                continue
            lo, hi = rational_power_bracket(p, -sigma, bits=64)
            lower *= 1 + 2 * lo ** 2 / (1 - lo) ** 2
            upper *= 1 + 2 * hi ** 2 / (1 - hi) ** 2
        bound = majorant_bounds(sigma, 100)
        self.assertGreater(bound["upper"], upper)
        self.assertGreater(bound["lower"], lower)
        self.assertGreater(bound["lower"], 27)
        self.assertLess(bound["upper"], 29)

    def test_narrower_prime_and_zeta_cutoffs(self):
        coarse = majorant_bounds(Q(3, 5), 30, zeta_cutoff=16)
        fine = majorant_bounds(Q(3, 5), 1000, zeta_cutoff=128)
        self.assertLess(coarse["lower"], fine["lower"])
        self.assertLess(fine["upper"], coarse["upper"])
        self.assertLess(fine["upper"], 290)
        self.assertGreater(fine["lower"], 280)
        tiny = majorant_bounds(Q(3, 4), 2)
        self.assertEqual(tiny["effective_prime_cutoff"], 7)
        self.assertEqual(tiny["prime_cutoff"], 2)

    def test_input_budgets_reject_before_evaluation(self):
        for bad in (True, False, .75, "3/4", Q(1, 2), 1, -1, None):
            with self.subTest(sigma=bad), self.assertRaises(ValueError):
                majorant_bounds(bad)
        for kwargs in ({"prime_cutoff": 10001}, {"prime_cutoff": True},
                       {"bits": 12}, {"zeta_cutoff": 0}, {"zeta_cutoff": 4097},
                       {"sigma": Q((1 << 200) + 1, (1 << 201))}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                majorant_bounds(**kwargs)
        for exponent in (1, True, "2", 17):
            with self.assertRaises(ValueError):
                wheel_power_tail(exponent, 100)


if __name__ == "__main__":
    unittest.main()
