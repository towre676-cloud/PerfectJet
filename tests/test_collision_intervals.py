"""Independent series and endpoint tests for certified interval arithmetic."""
import json
from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from math import factorial, gcd, isqrt
import unittest

from perfectjet.collision_intervals import (
    Interval, asymptotic_constants, euler_gamma_bounds, exp_bounds, log_bounds,
    power_bounds,
)


def decimal_fraction(value):
    """Exact rational representation of an independently rounded decimal."""
    return Q(str(value))


class CollisionIntervalTests(unittest.TestCase):
    def assertContains(self, interval, value):
        self.assertLessEqual(interval.lower, value)
        self.assertGreaterEqual(interval.upper, value)

    def test_signed_outward_rounding_and_immutability(self):
        for value in (Q(1, 3), Q(-1, 3), Q(12345, 127), Q(-100, 7)):
            a = Interval(value, bits=32)
            self.assertContains(a, value)
            self.assertLessEqual(a.width, Q(1, 1 << 32))
        with self.assertRaises(FrozenInstanceError):
            Interval(1).lower = Q(2)
        saved = json.loads(json.dumps(Interval(Q(1, 3)).record()))
        self.assertLessEqual(Q(saved['lower']), Q(1, 3))
        self.assertGreaterEqual(Q(saved['upper']), Q(1, 3))

    def test_interval_arithmetic_all_endpoint_combinations(self):
        for a in (Interval(-3, -2), Interval(-1, 2), Interval(Q(1, 3), Q(7, 3))):
            for b in (Interval(-4, -1), Interval(Q(1, 5), Q(3, 2))):
                for x in (a.lower, a.midpoint, a.upper):
                    for y in (b.lower, b.midpoint, b.upper):
                        self.assertContains(a + b, x + y)
                        self.assertContains(a - b, x - y)
                        self.assertContains(a * b, x * y)
                        self.assertContains(a / b, x / y)
                for exponent in (-3, -2, -1, 0, 1, 2, 3):
                    if exponent < 0 and a.lower <= 0 <= a.upper:
                        continue
                    for x in (a.lower, a.midpoint, a.upper):
                        self.assertContains(a ** exponent, x ** exponent)
        self.assertEqual((Interval(-3, 2) ** 2).lower, 0)
        with self.assertRaises(ValueError):
            Interval(1) / Interval(-1, 1)

    def test_log_two_against_independent_binary_series(self):
        # Independent formula log(2)=sum_(k>=1)1/(k*2^k).
        # After N terms the positive tail is < 1/((N+1)*2^N).
        n = 300
        partial = sum((Q(1, k * 2 ** k) for k in range(1, n + 1)), Q(0))
        tail = Q(1, (n + 1) * 2 ** n)
        for bits in (32, 80, 128, 256):
            a = log_bounds(2, bits=bits)
            self.assertLessEqual(a.lower, partial)
            self.assertGreaterEqual(a.upper, partial + tail)
        self.assertEqual(log_bounds(1).width, 0)
        self.assertContains(log_bounds(Q(1, 2)) + log_bounds(2), 0)

    def test_exp_against_independent_factorial_series(self):
        # e=sum 1/k!; the omitted tail after N is bounded by its first term
        # times 1/(1-1/(N+2)).  The reference interval is independently rational.
        n = 100
        partial = sum((Q(1, factorial(k)) for k in range(n + 1)), Q(0))
        tail = Q(1, factorial(n + 1)) / (1 - Q(1, n + 2))
        for bits in (32, 80, 128, 256):
            a = exp_bounds(1, bits=bits)
            self.assertLessEqual(a.lower, partial)
            self.assertGreaterEqual(a.upper, partial + tail)
            inverse = exp_bounds(-1, bits=bits)
            self.assertLessEqual(inverse.lower, 1 / (partial + tail))
            self.assertGreaterEqual(inverse.upper, 1 / partial)
        self.assertEqual(exp_bounds(0).lower, 1)
        self.assertContains(exp_bounds(Interval(-1, 2)), 1)

    def test_transcendentals_against_separate_decimal_implementation(self):
        # Decimal is a separate high precision observational oracle; it is not
        # used to construct any certified endpoint in the production code.
        with localcontext() as ctx:
            ctx.prec = 100
            for x in (Q(1, 1000), Q(2, 7), Q(3), Q(101), Q(10 ** 30)):
                d = Decimal(x.numerator) / Decimal(x.denominator)
                self.assertContains(log_bounds(x), decimal_fraction(d.ln()))
            for x in (Q(-20), Q(-3, 2), Q(1, 7), Q(20)):
                d = Decimal(x.numerator) / Decimal(x.denominator)
                self.assertContains(exp_bounds(x), decimal_fraction(d.exp()))
            for x in (2, 97, 10000):
                for exponent in (Q(-3, 4), Q(3, 5), Q(7, 8)):
                    d = Decimal(x) ** (Decimal(exponent.numerator) / Decimal(exponent.denominator))
                    self.assertContains(power_bounds(x, exponent), decimal_fraction(d))

    def test_gamma_precision_and_known_decimal(self):
        # A 90-digit reference is narrower than all tested certified intervals.
        value = Q('0.577215664901532860606512090082402431042159335939923598805767234884867726777664670936960063')
        for bits in (32, 80, 128, 256):
            a = euler_gamma_bounds(bits)
            self.assertContains(a, value)
            self.assertLess(a.width, Q(32, 1 << bits))
        # Independent elementary H_n-log(n)-1/n < gamma < H_n-log(n).
        n = 1000
        h = sum((Q(1, k) for k in range(1, n + 1)), Q(0))
        logarithm = log_bounds(n)
        a = euler_gamma_bounds()
        self.assertLess(h - logarithm.upper - Q(1, n), a.lower)
        self.assertGreater(h - logarithm.lower, a.upper)

    def test_constants_against_longer_independent_prime_sums(self):
        # Trial division and Decimal logarithms are independent of the sieve
        # and atanh implementation used by the certificate.
        primes = [n for n in range(2, 20001)
                  if all(n % d for d in range(2, isqrt(n) + 1))]
        with localcontext() as ctx:
            ctx.prec = 100
            c = Decimal(1)
            d = Decimal(0)
            for p in primes:
                c *= Decimal(p * p + 2 * p - 1) / Decimal((p + 1) ** 2)
                d += Decimal(4 * p) * Decimal(p).ln() / Decimal((p + 1) * (p * p + 2 * p - 1))
            c, d = decimal_fraction(c), decimal_fraction(d)
        for cutoff in (2, 7, 100, 1000):
            a = asymptotic_constants(cutoff)
            self.assertContains(a['C'], c)
            self.assertContains(a['D'], d)
            # The evidence field encloses the missing tail itself, including
            # at P<7, rather than only enclosing a formula for its upper bound.
            self.assertLessEqual(a['D_tail_bound'].lower, d - a['partial_D'].upper)
            self.assertGreaterEqual(a['D_tail_bound'].upper, d - a['partial_D'].lower)
            self.assertEqual(a['K'], a['C'] * (2 * a['gamma'] - 1 + a['D']))
            self.assertGreater(a['K'].lower, 0)
            self.assertLess(a['C_tail_loss_bound'], 1)
        a100, a1000 = asymptotic_constants(100), asymptotic_constants(1000)
        for key in ('C', 'D', 'K'):
            self.assertLess(a1000[key].width, a100[key].width)
        self.assertLess(a1000['C_tail_loss_bound'], Q(2, 1001))
        self.assertIn('modulo-210', a1000['tail_method'])

    def test_constant_wheel_tails_dominate_direct_integer_residue_sums(self):
        # Every wheel term used by production is f(first)+integral_first^inf f/M.
        # Explicit long progression sums must lie below the bound even though
        # primes are only a subset of the chosen progression population.
        p = 100
        a = asymptotic_constants(p)
        explicit = sum((Q(2, (n + 1) ** 2) for n in range(p + 1, 100000)
                        if gcd(n, 210) == 1), Q(0))
        self.assertLess(explicit, a['C_tail_loss_bound'])

    def test_strict_domains_and_work_guards(self):
        for value in (True, False, 0.5, '1', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Interval(value)
        for bits in (True, 0, 31, 257, 80.0, '80'):
            with self.assertRaises(ValueError):
                log_bounds(2, bits=bits)
        for value in (0, -1, Interval(-1, 1)):
            with self.assertRaises(ValueError):
                log_bounds(value)
            with self.assertRaises(ValueError):
                power_bounds(value, Q(1, 2))
        for call in (lambda: Interval(2, 1), lambda: exp_bounds(4097),
                     lambda: Interval(2) ** 16385,
                     lambda: Interval(2) ** Q(1, 2),
                     lambda: power_bounds(2, Q(16385)),
                     lambda: Interval(2 ** 16385),
                     lambda: asymptotic_constants(10001)):
            with self.assertRaises(ValueError):
                call()


if __name__ == '__main__':
    unittest.main()
