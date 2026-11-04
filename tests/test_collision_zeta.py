"""Independent arithmetic, finite factorization, and resource-bound checks."""
from fractions import Fraction as Q
from math import gcd
import unittest

from perfectjet.collision import kappa
from perfectjet.collision_zeta import (
    CONDUCTOR_TWO, RationalEulerFactor, conductor_two_coefficient,
    conductor_two_values, pell_pair, pell_lucas,
)


class CollisionPellTests(unittest.TestCase):
    def test_direct_signed_splits_and_remote_indices(self):
        a = CONDUCTOR_TWO.coefficients(100)
        for n, value in enumerate(a):
            self.assertEqual(value, sum((-1)**(j*(n-j)) for j in range(n+1)))
            self.assertEqual(value, conductor_two_coefficient(n))
        self.assertEqual(conductor_two_coefficient(10**100), 1)
        self.assertEqual(conductor_two_coefficient(10**100+1), 10**100+2)

    def test_original_integer_pairs_and_sieve(self):
        values = conductor_two_values(500)
        for n in range(1, 501):
            direct = sum((-1)**kappa(d, n//d) for d in range(1, n+1) if n % d == 0)
            self.assertEqual(values[n], direct, n)
            self.assertGreater(values[n], 0)
        for m in range(1, 20):
            for n in range(1, 20):
                if gcd(m, n) == 1:
                    self.assertEqual(values[m*n], values[m]*values[n])

    def test_pell_powering_against_iteration_and_norm(self):
        u, v = 1, 0
        for n in range(200):
            self.assertEqual(pell_pair(n), (u, v))
            self.assertEqual(u*u-2*v*v, (-1)**n)
            self.assertEqual(pell_lucas(n), 2*u)
            for modulus in (2, 12, 1009):
                self.assertEqual(pell_pair(n, modulus), (u % modulus, v % modulus))
            u, v = u+2*v, u+v
        n = 10**100
        # Unit multiplication composes remote powers without exact expansion.
        a, b = pell_pair(n, 1009), pell_pair(n+1, 1009)
        self.assertEqual(b, ((a[0]+2*a[1]) % 1009, (a[0]+a[1]) % 1009))

    def test_log_coefficients_have_exact_pell_formula(self):
        c = CONDUCTOR_TWO.logarithmic_coefficients(100)
        for n in range(1, 101):
            self.assertEqual(c[n], (-1)**(n+1)*pell_lucas(n)+4*(n % 2 == 0))
        b = CONDUCTOR_TWO.zeta_exponents(24)
        self.assertEqual(b[1:13], [2,-2,4,-7,16,-34,68,-140,308,-680,1476,-3248])
        for n in range(1, 25):
            self.assertEqual(c[n], sum(d*b[d] for d in range(1, n+1) if n % d == 0))

    def test_finite_extraction_is_an_actual_rational_identity(self):
        for factor in (CONDUCTOR_TWO, RationalEulerFactor((1,2,1)), RationalEulerFactor((1,), (1,-1))):
            for order in range(6):
                packet = factor.extract(order)
                p, q = packet['residual_numerator'], packet['residual_denominator']
                for x in (Q(1,11), Q(-1,13), Q(2,17)):
                    def evaluate(poly):
                        return sum(c*x**i for i,c in enumerate(poly))
                    residual = evaluate(p)/evaluate(q)
                    expected = residual
                    for n, b in enumerate(packet['zeta_exponents'], 1):
                        expected *= (1-x**n)**(-b)
                    self.assertEqual(expected, factor.evaluate(x))
        exact = RationalEulerFactor((1,), (1,-1)).extract(1)
        self.assertIsNone(exact['residual_first_degree'])

    def test_invalid_domains_and_work_rejection(self):
        for n in (True, -1, 1.0, '2.5'):
            with self.assertRaises(ValueError):
                conductor_two_coefficient(n)
        for args in ((True,), ((1,True),), ((2,1),), ((1,), (0,1))):
            with self.assertRaises((ValueError, TypeError)):
                RationalEulerFactor(*args)
        with self.assertRaises(ValueError):
            CONDUCTOR_TWO.extract(100)
        with self.assertRaises(ValueError):
            pell_pair(10**100)
        with self.assertRaises(ValueError):
            pell_pair(3, True)
        with self.assertRaises(ValueError):
            conductor_two_values(1000001)


if __name__ == '__main__':
    unittest.main()
