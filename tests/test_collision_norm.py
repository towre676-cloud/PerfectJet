import json
import unittest
from fractions import Fraction as Q
from unittest.mock import patch

from perfectjet.collision import CyclotomicCollision
from perfectjet.collision_norm import collision_norm, norm_classification_theorem
from perfectjet.loci import _det


def evaluate(coefficients, x):
    result = Q(0)
    for coefficient in reversed(coefficients):
        result = result * x + coefficient
    return result


class CollisionNormTests(unittest.TestCase):
    def test_low_conductor_exact_polynomials_and_trace(self):
        expected = {
            1: (1,),
            2: (1, 2, -1),
            3: (1, 4, 7, 4, -2, -8, 4, -2, 1),
            4: (1, 4, 8, 8, 7, 0, -8, -8, 7, -4, 0, 0, 1),
        }
        for l, numerator in expected.items():
            norm = collision_norm(l)
            self.assertEqual(norm.numerator, numerator)
            self.assertEqual(norm.denominator_period, l)
            self.assertEqual(norm.denominator_power, 2 * norm.field_degree)
        self.assertEqual(collision_norm(3).trace_numerator, (2, 4, 3, -2, -1))

    def test_norm_against_independent_multiplication_determinant(self):
        # A field norm can independently be calculated as a determinant of
        # multiplication by N_L(x), without multiplying its conjugates.
        for l in range(2, 9):
            norm = collision_norm(l)
            c = CyclotomicCollision(l)
            ring = c.ring
            basis = [ring.generator ** j for j in range(ring.degree)]
            for x in (Q(-1), Q(1, 2), Q(1)):
                value = ring.zero
                for coefficient in reversed(c.numerator()):
                    value = value * x + coefficient
                columns = [(value * b).coefficients for b in basis]
                matrix = [[columns[j][i] for j in range(ring.degree)]
                          for i in range(ring.degree)]
                self.assertEqual(evaluate(norm.numerator, x), _det(matrix))

    def test_integer_checkpoints_and_reciprocal_obstruction(self):
        for l in range(1, 13):
            norm = collision_norm(l)
            checks = norm.report()["finite_checks"]
            self.assertEqual(checks["degree"], checks["expected_degree"])
            self.assertEqual(checks["numerator_at_one"], l ** norm.field_degree)
            self.assertEqual(checks["leading_coefficient"], checks["expected_leading_coefficient"])
            self.assertEqual(norm.numerator[0], 1)
            self.assertTrue(all(type(c) is int for c in norm.numerator))
            if l > 1:
                self.assertEqual(checks["first_coefficient"], checks["expected_first_coefficient"])
                self.assertEqual(checks["penultimate_coefficient"], checks["expected_penultimate_coefficient"])
                self.assertTrue(checks["reciprocal_necessity_fails"])
                self.assertTrue(norm.report()["classification"]["natural_boundary_re_s_zero"])

    def test_individual_phase_coefficient_obstruction(self):
        for l in range(2, 15):
            c = CyclotomicCollision(l)
            numerator = c.numerator()
            self.assertEqual(numerator[0], 1)
            self.assertEqual(numerator[1], 2)
            self.assertEqual(numerator[-1], c.zeta)
            self.assertEqual(numerator[-2], 2 * c.zeta ** 2)
            self.assertNotEqual(numerator[-2], 2 * c.zeta)

    def test_budget_rejection_happens_before_cyclotomic_construction(self):
        with patch("perfectjet.collision_norm.cyclotomic", side_effect=AssertionError("allocated")):
            for kwargs in ({"max_conductor": 3}, {"max_degree": 2}, {"max_work": 1}):
                with self.assertRaises(ValueError):
                    collision_norm(8, **kwargs)
            with self.assertRaises(ValueError):
                collision_norm(32)  # large exact field product requires explicit larger budget
        for invalid in (True, False, 0, -2, 2.0, "2", None):
            with self.assertRaises(ValueError):
                collision_norm(invalid)

    def test_immutable_result_and_scoped_serializable_theorem(self):
        norm = collision_norm(2)
        with self.assertRaises(AttributeError):
            norm.conductor = 3
        self.assertIsInstance(norm.numerator, tuple)
        report = json.loads(json.dumps(norm.report()))
        self.assertEqual(report["classification"]["scope"], "prime-local full Galois norm Euler product")
        theorem = json.loads(json.dumps(norm_classification_theorem()))
        self.assertIn("not classified", theorem["single_complex_phase_product"])
        self.assertIn("not Lean", theorem["status"])


if __name__ == "__main__":
    unittest.main()
