"""Independent checks for the certified conductor-two Euler-product bounds."""
import json
import unittest
from fractions import Fraction as Q

from perfectjet.collision_constants import (
    constant_bounds, conductor_two_zeta_bounds, constants_receipt, primes_up_to,
)


class CollisionConstantTests(unittest.TestCase):
    def test_prime_inventory_and_exact_small_cutoff(self):
        self.assertEqual(primes_up_to(20), (2, 3, 5, 7, 11, 13, 17, 19))
        c = constant_bounds(2)
        self.assertEqual(c["upper"], Q(7, 9))
        self.assertEqual(c["lower"], Q(7, 27))
        z = conductor_two_zeta_bounds(2, 2)
        self.assertEqual(z["lower"], Q(368, 225))
        self.assertEqual(z["upper"], Q(1472, 225))

    def test_long_independent_prime_products_are_enclosed(self):
        # Trial division supplies an independent prime list and local formulas.
        primes = [n for n in range(2, 2001)
                  if all(n % d for d in range(2, int(n ** 0.5) + 1))]
        c_long = Q(1)
        z_long = {s: Q(1) for s in (2, 3, 5)}
        for p in primes:
            c_long *= Q(p * p + 2 * p - 1, (p + 1) ** 2)
            for s in z_long:
                r = p ** s
                z_long[s] *= Q(r * r * (r * r + 2 * r - 1), (r * r - 1) ** 2)
        for cutoff in (2, 7, 30, 100):
            c = constant_bounds(cutoff)
            self.assertLess(c["lower"], c_long)
            self.assertLess(c_long, c["upper"])
            for s in z_long:
                z = conductor_two_zeta_bounds(s, cutoff)
                self.assertLess(z["lower"], z_long[s])
                self.assertLess(z_long[s], z["upper"])

    def test_bounds_tighten_and_receipt_is_exact_json(self):
        c10, c100 = constant_bounds(10), constant_bounds(100)
        self.assertLess(c10["lower"], c100["lower"])
        self.assertLess(c100["upper"], c10["upper"])
        for s in (2, 4):
            z10, z100 = conductor_two_zeta_bounds(s, 10), conductor_two_zeta_bounds(s, 100)
            self.assertLess(z10["lower"], z100["lower"])
            self.assertLess(z100["upper"], z10["upper"])
        receipt = json.loads(json.dumps(constants_receipt(7, 3), allow_nan=False))
        c = receipt["leading_summatory_constant"]
        self.assertLessEqual(Q(c["lower"]), constant_bounds(7)["lower"])
        self.assertGreaterEqual(Q(c["upper"]), constant_bounds(7)["upper"])
        self.assertIn("outward", c["endpoint_rounding"])
        self.assertIn("not a finite-X error certificate", receipt["limits"])

    def test_domains_reject_nonintegral_and_bool_inputs(self):
        for invalid in (True, False, 0, 1, -1, 3.0, "10", None):
            with self.subTest(cutoff=invalid), self.assertRaises(ValueError):
                constant_bounds(invalid)
            with self.subTest(s=invalid), self.assertRaises(ValueError):
                conductor_two_zeta_bounds(invalid)
        with self.assertRaises(ValueError):
            conductor_two_zeta_bounds(2, True)
        for call in (lambda: constant_bounds(10_001),
                     lambda: primes_up_to(10**20),
                     lambda: conductor_two_zeta_bounds(33, 100),
                     lambda: conductor_two_zeta_bounds(32, 2000)):
            with self.assertRaises(ValueError):
                call()

    def test_large_allowed_receipt_has_compact_outward_endpoints(self):
        c = constant_bounds(2000)
        receipt = constants_receipt(2000, 2)
        saved = receipt["leading_summatory_constant"]
        self.assertLessEqual(Q(saved["lower"]), c["lower"])
        self.assertGreaterEqual(Q(saved["upper"]), c["upper"])
        self.assertLess(len(json.dumps(receipt)), 2500)


if __name__ == "__main__":
    unittest.main()
