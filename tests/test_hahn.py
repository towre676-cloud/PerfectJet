import json
import unittest
from fractions import Fraction as F

from perfectjet import hahn
from perfectjet.moyal import PolyH, egorov_defect


class HahnTests(unittest.TestCase):
    def test_falling_factorials_and_first_poisson_coefficient(self):
        self.assertEqual(hahn.falling_factorial(5, 3), 60)
        self.assertEqual(hahn.falling_factorial(5, 0), 1)
        self.assertEqual(hahn.falling_factorial(2, 3), 0)
        for a, b, c, d in ((3, 2, 4, 5), (0, 4, 7, 2), (2, 2, 2, 2)):
            self.assertEqual(hahn.S(a, b, c, d, 1), a*d-b*c)
        for operation in (lambda: hahn.S(-1, 0, 0, 1, 3), lambda: hahn.S(1, 0, 0, 1, 2.5),
                          lambda: hahn.higher_order_decoy(0), lambda: hahn.kappa4_ray_pairs(-1)):
            with self.assertRaises(ValueError):
                operation()

    def test_independent_known_obstruction_towers(self):
        self.assertEqual(hahn.S(3, 0, 0, 3, 3), 36)
        self.assertEqual(hahn.defect_terms(3, 0, 0, 3), [(2, 0, 0, -F(3, 2))])
        self.assertEqual(hahn.defect_terms(5, 0, 0, 5), [(2, 2, 2, F(-150)), (4, 0, 0, F(15, 2))])
        self.assertEqual(hahn.classify(3, 0, 0, 3), "CENTRAL_DEFECT")
        self.assertEqual(hahn.classify(5, 0, 0, 5), "NONCENTRAL_DEFECT")
        self.assertEqual(hahn.odd_coefficients(1, 3, 5, 1), {3: 0})
        self.assertTrue(hahn.exact(1, 3, 5, 1))
        self.assertTrue(hahn.exact(100, 100, 100, 100))

    def test_finite_layer_classifier_agrees_with_multidifferential_engine(self):
        # Independent algorithm: sparse multiderivatives vs falling-factorial sum.
        symbols = [(a, b) for a in range(5) for b in range(5-a)]
        for a, b in symbols:
            for c, d in symbols:
                exact_defect = egorov_defect(PolyH.monomial(1, (a, b)), PolyH.monomial(1, (c, d)))
                expected = PolyH.zero(1)
                for hp, qp, pp, coefficient in hahn.defect_terms(a, b, c, d):
                    expected += PolyH.monomial(1, (qp, pp), coefficient, hp)
                self.assertEqual(exact_defect, expected, (a, b, c, d))
                self.assertEqual(hahn.exact(a, b, c, d), exact_defect.is_zero())

    def test_all_active_layers_reject_cubic_decoys(self):
        for t in (1, 2, 3, 10, 37):
            pair = (1, 4, 3*t+2, 2*t)
            self.assertEqual(hahn.kappa(*pair), 5)
            self.assertEqual(hahn.odd_coefficients(*pair)[3], 0)
            self.assertEqual(hahn.odd_coefficients(*pair)[5], 720*t*t*(3*t-1)*(3*t+1)*(3*t+2))
            self.assertFalse(hahn.exact(*pair))
            self.assertTrue(hahn.higher_order_decoy(t)["S5_positive_identity"])

    def test_kappa4_rays_exhaust_small_bounded_sector(self):
        degree = 12
        generated = set(hahn.kappa4_ray_pairs(degree))
        symbols = [(a, b) for a in range(degree+1) for b in range(degree+1-a)]
        direct = {(a, b, c, d) for a, b in symbols for c, d in symbols
                  if hahn.kappa(a, b, c, d) == 4 and hahn.poisson_scalar(a, b, c, d)
                  and hahn.S(a, b, c, d, 3) == 0}
        self.assertEqual(generated, direct)
        self.assertTrue(all(hahn.is_kappa4_ray(*pair) and hahn.exact(*pair) for pair in generated))
        self.assertEqual(len(hahn.kappa4_ray_pairs(80)), 172)
        self.assertEqual(hahn.kappa4_ray_pairs(5), [])

    def test_order_reversal_and_serializable_scope(self):
        for pair in ((1, 3, 5, 1), (5, 0, 0, 5), (1, 4, 8, 4)):
            a, b, c, d = pair
            for k in range(1, hahn.kappa(*pair)+1, 2):
                self.assertEqual(hahn.S(a, b, c, d, k), -hahn.S(c, d, a, b, k))
        r = hahn.receipt()
        json.dumps(r)
        self.assertEqual(r["degree80_generated_ray_pairs"], 172)
        self.assertTrue(r["generated_rays_exact"])
        self.assertIn("conjectural", r["scope"])


if __name__ == "__main__":
    unittest.main()
