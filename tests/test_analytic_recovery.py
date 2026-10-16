import cmath
import json
import math
import unittest
from fractions import Fraction as Q

from perfectjet.analytic_recovery import (
    CircularLogPeriod, Cyclotomic, DirichletCharacter, LogDivisor,
    cyclotomic_polynomial, dirichlet_l_ratio_coefficients, isolated_circle_period,
    principal_local_factor, progression_residue_factor, progression_via_characters,
    progression_visible_coefficients, receipt, totient, twisted_visible_coefficients,
)


class AnalyticRecoveryTests(unittest.TestCase):
    def test_circular_period_exact_charge_radius_and_orientation(self):
        geometry = [LogDivisor("target", (2, -1), 3), LogDivisor("other", (3, -1), -1)]
        result = isolated_circle_period(geometry, (2, -1), "1/10")
        self.assertIsInstance(result, CircularLogPeriod)
        self.assertEqual(result.coefficient_of_two_pi_i, Q(3, 10))
        self.assertEqual(result.other_divisor_clearance_squared, Q(99, 100))
        reverse = isolated_circle_period(geometry, (2, -1), "1/10", -1)
        self.assertEqual(reverse.coefficient_of_two_pi_i, -result.coefficient_of_two_pi_i)
        doubled_radius = isolated_circle_period(geometry, (2, -1), "1/5")
        self.assertEqual(doubled_radius.coefficient_of_two_pi_i, 2 * result.coefficient_of_two_pi_i)

    def test_period_against_independent_branch_tracked_midpoint_quadrature(self):
        radius, charge, samples = 0.13, -2, 20000
        for orientation in (-1, 1):
            step = orientation * 2 * math.pi / samples
            integral = sum(charge * (math.log(radius) + 1j * ((j + 0.5) * step))
                           * 1j * radius * cmath.exp(1j * ((j + 0.5) * step)) * step
                           for j in range(samples))
            exact = isolated_circle_period([LogDivisor("pole", (0, 0), charge)], (0, 0), "13/100", orientation)
            self.assertLess(abs(integral - 2j * math.pi * float(exact.coefficient_of_two_pi_i)), 1e-7)

    def test_isolation_checks_enclosed_boundary_missing_and_duplicate_divisors(self):
        base = LogDivisor("base", (0, 0), 1)
        for other in (LogDivisor("nearby", ("1/10", 0), -1), LogDivisor("boundary", ("1/5", 0), 1)):
            with self.assertRaises(ValueError):
                isolated_circle_period([base, other], (0, 0), "1/5")
        for divisors in ([], [LogDivisor("away", (1, 0), 1)],
                         [base, LogDivisor("same point", (0, 0), 1)],
                         [base, LogDivisor("base", (1, 0), 1)]):
            with self.assertRaises(ValueError):
                isolated_circle_period(divisors, (0, 0), "1/10")
        for radius in (0, -1):
            with self.assertRaises(ValueError):
                isolated_circle_period([base], (0, 0), radius)
        for orientation in (0, True, 1.0):
            with self.assertRaises(ValueError):
                isolated_circle_period([base], (0, 0), 1, orientation)

    def test_cyclotomic_exact_roots_and_canonical_cancellation(self):
        self.assertEqual(cyclotomic_polynomial(1), (-1, 1))
        self.assertEqual(cyclotomic_polynomial(4), (1, 0, 1))
        self.assertEqual(cyclotomic_polynomial(6), (1, -1, 1))
        for order in range(1, 25):
            root = Cyclotomic.root(order, 1)
            power = Cyclotomic.scalar(order, 1)
            for _ in range(order):
                power *= root
            self.assertEqual(power.rational(), 1)
            self.assertEqual((root * root.conjugate()).rational(), 1)
            if order > 1:
                self.assertTrue(sum((Cyclotomic.root(order, j) for j in range(order)),
                                    Cyclotomic.scalar(order, 0)).is_zero())
        with self.assertRaises(ValueError):
            Cyclotomic.root(4, 1).rational()

    def test_visible_ray_coefficients_against_direct_gcd_enumeration(self):
        characters = [DirichletCharacter.principal(1), DirichletCharacter.principal(6),
                      DirichletCharacter(3, (None, 0, 1), 2),
                      DirichletCharacter(5, (None, 0, 1, 3, 2), 4)]
        for character in characters:
            direct = twisted_visible_coefficients(character, 120)
            quotient = dirichlet_l_ratio_coefficients(character, 120)
            self.assertEqual(direct, quotient)
            for n, coefficient in enumerate(quotient, 1):
                primitive_rays = sum(math.gcd(a, n) == 1 for a in range(1, n + 1))
                self.assertEqual(totient(n), primitive_rays)
                self.assertEqual(coefficient, primitive_rays * character(n))

    def test_nonreal_character_orthogonality_and_progression(self):
        exponents = (None, 0, 1, 3, 2)
        table = [DirichletCharacter(5, tuple(None if e is None else k * e for e in exponents), 4)
                 for k in range(4)]
        for residue in (1, 2, 3, 4, -1):
            decomposed = progression_via_characters(table, residue, 100)
            direct = progression_visible_coefficients(5, residue, 100)
            self.assertEqual(tuple(x.rational() for x in decomposed), direct)
            for n, value in enumerate(direct, 1):
                expected = sum(math.gcd(a, n) == 1 for a in range(1, n + 1)) if n % 5 == residue % 5 else 0
                self.assertEqual(value, expected)
        with self.assertRaises(ValueError):
            progression_via_characters(table[:-1], 1, 10)
        with self.assertRaises(ValueError):
            progression_via_characters([table[0]] * 4, 1, 10)

    def test_progression_residue_includes_principal_local_factors(self):
        self.assertEqual(progression_residue_factor(1, 0), 1)
        self.assertEqual(progression_residue_factor(3, 1), Q(3, 8))
        self.assertEqual(progression_residue_factor(3, 2), Q(3, 8))
        self.assertEqual(progression_residue_factor(6, 1), Q(1, 4))
        for modulus in (1, 2, 3, 4, 6, 9, 12, 35):
            self.assertEqual(progression_residue_factor(modulus, 1), principal_local_factor(modulus, 2) / totient(modulus))
        with self.assertRaises(ValueError):
            progression_residue_factor(6, 2)

    def test_invalid_character_tables_and_json_receipt(self):
        for args in ((3, (0, 0, 1), 2), (3, (None, 1, 0), 2),
                     (5, (None, 0, 1, 1, 0), 4), (3, (None, 0), 2)):
            with self.assertRaises(ValueError):
                DirichletCharacter(*args)
        for limit in (0, -1, True):
            with self.assertRaises(ValueError):
                twisted_visible_coefficients(DirichletCharacter.principal(3), limit)
        json.dumps(receipt())


if __name__ == "__main__":
    unittest.main()
