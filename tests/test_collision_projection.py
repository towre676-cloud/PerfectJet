import json
import unittest
from dataclasses import FrozenInstanceError

from perfectjet.collision_projection import (
    PrimeLocalCollisionProjection, classification_theorem, collision_projection,
    projection_classification_theorem,
)
from perfectjet.rings import QuotientRing, cyclotomic


class CollisionProjectionTests(unittest.TestCase):
    def test_character_average_is_exact_integer_projection(self):
        # Independent root-of-unity orthogonality, not another divisibility loop.
        for conductor in range(1, 10):
            ring = QuotientRing(cyclotomic(conductor))
            zeta = ring.generator
            actual = [ring.zero for _ in range(2 * conductor - 1)]
            for r in range(conductor):
                for s in range(conductor):
                    actual[r + s] += sum(
                        (zeta ** (a * r * s % conductor) for a in range(conductor)),
                        ring.zero) / conductor
            projection = PrimeLocalCollisionProjection(conductor)
            expected = list(projection.numerator)
            expected += [0] * (len(actual) - len(expected))
            self.assertTrue(all(a == b for a, b in zip(actual, expected)))

    def test_residue_splitting_agrees_with_unsplit_pair_counts(self):
        for conductor in (1, 2, 3, 4, 6, 9, 12):
            projection = PrimeLocalCollisionProjection(conductor)
            for index in range(4 * conductor + 5):
                self.assertEqual(projection.coefficient(index),
                                 projection.direct_coefficient(index))

    def test_exact_exceptions_and_remote_coefficients(self):
        one = PrimeLocalCollisionProjection(1)
        four = PrimeLocalCollisionProjection(4)
        self.assertEqual(one.numerator, (1,))
        self.assertEqual(one.finite_zeta_exponents, ((1, 2),))
        self.assertEqual(four.numerator, (1, 2, 2, 2, 1))
        self.assertEqual(four.finite_zeta_exponents, ((1, 2), (2, -1), (4, 1)))
        huge = 10 ** 100
        self.assertEqual(one.coefficient(huge), huge + 1)
        # At totals divisible by four, precisely the even first exponents qualify.
        self.assertEqual(four.coefficient(huge), huge // 2 + 1)
        self.assertEqual(four.coefficient(huge + 1), huge // 2 + 2)

    def test_four_finite_zeta_formula_by_local_cross_multiplication(self):
        # C4/(1-x4)^2 = (1-x2)/((1-x)^2*(1-x4)).
        def product(a, b):
            out = [0] * (len(a) + len(b) - 1)
            for i, x in enumerate(a):
                for j, y in enumerate(b):
                    out[i + j] += x * y
            return out
        four = PrimeLocalCollisionProjection(4)
        lhs = product(four.numerator, product((1, -2, 1), (1, 0, 0, 0, -1)))
        rhs = product((1, 0, -1), four.denominator)
        self.assertEqual(lhs, rhs)

    def test_all_conductor_proof_checks_separate_from_finite_census(self):
        for conductor in (1, 2, 3, 4, 6, 9, 16, 25, 36, 64, 100, 144):
            row = collision_projection(conductor).report()
            self.assertTrue(all(row["checks"].values()), row)
            self.assertEqual(row["classification"] == "finite_zeta_product",
                             conductor in (1, 4))
        theorem = classification_theorem()
        self.assertEqual(theorem["status"], "derived_written_proof_not_formalized")
        self.assertTrue(theorem["finite_sampling_is_not_the_proof"])
        self.assertEqual(theorem, projection_classification_theorem())

    def test_global_total_divisibility_is_a_different_question(self):
        projection = PrimeLocalCollisionProjection(2)
        # m=n=6: two primes each have exponent pair (1,1), so total kappa is 2.
        self.assertEqual((1 * 1 + 1 * 1) % 2, 0)
        self.assertFalse(projection.local_exponent_allowed(1, 1))
        self.assertIn("separately", projection.report()["global_semantics"])

    def test_invalid_inputs_and_preflight_resource_budgets(self):
        for value in (True, False, 0, -1, 2.0, "4", None):
            with self.assertRaises(ValueError):
                PrimeLocalCollisionProjection(value)
        for kwargs in ({"max_conductor": True}, {"max_conductor": 0},
                       {"max_terms": False}, {"max_terms": -1},
                       {"max_terms": 3.0}, {"max_conductor": 3},
                       {"max_terms": 15}):
            with self.assertRaises(ValueError):
                PrimeLocalCollisionProjection(4, **kwargs)
        with self.assertRaises(ValueError):
            PrimeLocalCollisionProjection(10 ** 100, max_conductor=10 ** 100)
        projection = PrimeLocalCollisionProjection(4)
        for value in (True, -1, 1.0, "1", None):
            with self.assertRaises(ValueError):
                projection.coefficient(value)
            with self.assertRaises(ValueError):
                projection.local_exponent_allowed(value, 0)
        with self.assertRaises(ValueError):
            projection.direct_coefficient(100, max_terms=100)
        with self.assertRaises(ValueError):
            projection.direct_coefficient(0, max_terms=True)

    def test_immutable_coefficients_and_json_report(self):
        projection = PrimeLocalCollisionProjection(4)
        with self.assertRaises(FrozenInstanceError):
            projection.conductor = 1
        self.assertIsInstance(projection.numerator, tuple)
        row = projection.report()
        row["numerator"][0] = 99
        self.assertEqual(projection.numerator[0], 1)
        self.assertEqual(json.loads(json.dumps(projection.report()))["numerator"][0], 1)


if __name__ == "__main__":
    unittest.main()
