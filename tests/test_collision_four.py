import json
import unittest
from unittest.mock import patch

from perfectjet.collision_four import (
    collision_four_forward, collision_four_inverse,
    collision_four_forward_vectors, collision_four_inverse_vectors,
    collision_four_size_count, receipt,
)
from perfectjet.collision_projection import collision_projection


class CollisionFourTests(unittest.TestCase):
    def test_exhaustive_original_domain_and_exact_inverse(self):
        count = 0
        for a in range(81):
            for b in range(81):
                if a * b % 4:
                    with self.assertRaises(ValueError):
                        collision_four_forward(a, b)
                    continue
                u, v, w = collision_four_forward(a, b)
                self.assertEqual(u * v, 0)
                self.assertEqual(a + b, u + v + 4 * w)
                self.assertEqual(collision_four_inverse(u, v, w), (a, b))
                count += 1
        self.assertEqual(count, 3361)

    def test_independent_target_census_surjectivity_and_zero_orientation(self):
        self.assertEqual(collision_four_inverse(0, 0, 7), (14, 14))
        self.assertEqual(collision_four_forward(14, 14), (0, 0, 7))
        for h in range(81):
            for w in range(41):
                targets = ((0, 0, w),) if h == 0 else ((h, 0, w), (0, h, w))
                for target in targets:
                    a, b = collision_four_inverse(*target)
                    self.assertEqual(a * b % 4, 0)
                    self.assertEqual(collision_four_forward(a, b), target)
                    self.assertEqual(a + b, h + 4 * w)

    def test_local_count_agrees_with_projection_and_unordered_census(self):
        projection = collision_projection(4)
        for e in range(321):
            count = collision_four_size_count(e)
            self.assertEqual(count, sum(1 for a in range(e + 1) if a * (e - a) % 4 == 0))
            self.assertEqual(count, projection.coefficient(e))
        huge = 10 ** 100 + 2
        self.assertEqual(collision_four_size_count(huge), 2 * (huge // 4) + 2)

    def test_vectors_preserve_actual_integer_product_and_coprimality(self):
        primes = (2, 3, 5, 7)
        a, b = (6, 5, 0, 8), (2, 4, 7, 8)
        u, v, w = collision_four_forward_vectors(a, b)
        self.assertEqual(collision_four_inverse_vectors(u, v, w), (a, b))
        self.assertTrue(all(x * y == 0 for x, y in zip(u, v)))
        source = target = 1
        for p, x, y, r, s, t in zip(primes, a, b, u, v, w):
            source *= p ** (x + y)
            target *= p ** r * p ** s * (p ** t) ** 4
        self.assertEqual(source, target)
        self.assertEqual(collision_four_forward_vectors((), ()), ((), (), ()))
        self.assertEqual(collision_four_inverse_vectors((), (), ()), ((), ()))

    def test_size_coefficients_via_independent_global_divisor_formula(self):
        # Count original pairs directly for each product, then compare the
        # coprime residual/fourth-power coefficient formula without the map.
        def factors(n):
            result = {}
            p = 2
            while p * p <= n:
                while n % p == 0:
                    result[p] = result.get(p, 0) + 1
                    n //= p
                p += 1
            if n > 1:
                result[n] = result.get(n, 0) + 1
            return result
        for n in range(1, 501):
            original = 0
            for m in range(1, n + 1):
                if n % m:
                    continue
                left, right = factors(m), factors(n // m)
                if all(left.get(p, 0) * right.get(p, 0) % 4 == 0 for p in left.keys() | right.keys()):
                    original += 1
            expected = 0
            d = 1
            while d ** 4 <= n:
                if n % (d ** 4) == 0:
                    expected += 2 ** len(factors(n // (d ** 4)))
                d += 1
            self.assertEqual(original, expected)

    def test_strict_validation_and_vector_preflight(self):
        for bad in (True, False, -1, 1.0, "1", None):
            for call in (lambda: collision_four_forward(bad, 0),
                         lambda: collision_four_inverse(0, 0, bad),
                         lambda: collision_four_size_count(bad)):
                with self.assertRaises(ValueError):
                    call()
        with self.assertRaises(ValueError):
            collision_four_inverse(2, 3, 1)
        for call in (lambda: collision_four_forward_vectors((0,), ()),
                     lambda: collision_four_forward_vectors("0", "0"),
                     lambda: collision_four_forward_vectors(range(10 ** 100), range(10 ** 100)),
                     lambda: collision_four_inverse_vectors((0,), (0,), (True,)),
                     lambda: collision_four_forward_vectors((), (), max_primes=False)):
            with self.assertRaises(ValueError):
                call()
        with patch("perfectjet.collision_four.collision_four_forward", side_effect=AssertionError("computed")):
            with self.assertRaises(ValueError):
                collision_four_forward_vectors((0, 0), (0, 0), max_primes=1)

    def test_receipt_json_scope_and_exact_example(self):
        self.assertEqual(collision_four_forward(1, 4), (1, 0, 1))
        self.assertEqual(collision_four_forward(4, 2), (2, 0, 1))
        row = json.loads(json.dumps(receipt()))
        self.assertTrue(row["finite_checks"]["roundtrip_and_size"])
        self.assertIn("at each prime", row["local_domain"])


if __name__ == "__main__":
    unittest.main()
