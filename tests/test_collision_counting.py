"""Separate finite integer oracles for conductor-two summatory counts."""
import unittest

from perfectjet.collision import kappa
from perfectjet.collision_counting import (
    coefficient_sieve, divisor_summatory, exact_count, exact_counts,
    powerful_coefficients,
)
from perfectjet.collision_zeta import conductor_two_values


class CollisionCountingTests(unittest.TestCase):
    def test_prime_power_sieve_against_original_signed_factor_pairs(self):
        values = coefficient_sieve(300)
        self.assertEqual(values[0], 0)
        for n in range(1, 301):
            direct = sum((-1) ** kappa(d, n // d)
                         for d in range(1, n + 1) if n % d == 0)
            self.assertEqual(values[n], direct, n)

    def test_sieve_agrees_with_existing_least_prime_recurrence(self):
        self.assertEqual(list(coefficient_sieve(100_000)), conductor_two_values(100_000))

    def test_exact_hyperbola_against_divisor_loops(self):
        for n in range(301):
            self.assertEqual(divisor_summatory(n), sum(n // k for k in range(1, n + 1)))

    def test_sparse_h_support_and_local_convolution(self):
        rows = list(powerful_coefficients(1000))
        self.assertEqual(len(rows), len(dict(rows)))
        h = dict(rows)
        self.assertEqual({n: h[n] for n in (1, 4, 8, 9, 16, 36)},
                         {1: 1, 4: -2, 8: 4, 9: -2, 16: -6, 36: 4})
        values = coefficient_sieve(1000)
        for n in range(1, 1001):
            convolution = sum(c * sum(1 for d in range(1, n // m + 1) if (n // m) % d == 0)
                              for m, c in rows if n % m == 0)
            self.assertEqual(convolution, values[n], n)

    def test_cumulative_methods_agree_across_many_inputs(self):
        points = list(range(101)) + [127, 128, 255, 256, 999, 1000, 9999, 10000, 100000]
        expected = exact_counts(points)
        for n in points:
            self.assertEqual(exact_count(n), expected[n], n)
        self.assertEqual(exact_count(1_000_000), exact_count(1_000_000, method="sieve"))
        self.assertEqual(exact_counts([0, 2, 2, 1], "convolution"), {0: 0, 1: 1, 2: 3})
        self.assertEqual(exact_counts([]), {})

    def test_preflight_domains_and_work_budgets(self):
        for value in (True, False, -1, 1.0, "10", None):
            for call in (coefficient_sieve, divisor_summatory, exact_count):
                with self.subTest(value=value, call=call.__name__), self.assertRaises(ValueError):
                    call(value)
        for call in (lambda: coefficient_sieve(10_000_001),
                     lambda: exact_count(1_000_000_000_001),
                     lambda: exact_count(1, "other"),
                     lambda: exact_counts(range(10)),
                     lambda: exact_counts([1] * 1025),
                     lambda: exact_counts([True]),
                     lambda: exact_counts([10_000_001]),
                     lambda: exact_counts([1], "other")):
            with self.assertRaises(ValueError):
                call()


if __name__ == "__main__":
    unittest.main()
