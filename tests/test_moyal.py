import json
import unittest
from fractions import Fraction as F

from perfectjet.moyal import (GI, I, PolyH, star_product, poisson_bracket,
                             scaled_moyal_bracket, egorov_defect, classify_defect,
                             pullback, covariance_defect, covariance_example,
                             monomials_total_degree, scan_phase_diagram, receipt)


class MoyalTests(unittest.TestCase):
    def setUp(self):
        self.q, self.p, self.h = PolyH.q(), PolyH.p(), PolyH.hbar()

    def test_exact_gaussian_rationals_and_input_validation(self):
        self.assertEqual(GI(F(1, 3), F(2, 7)) * GI(F(1, 3), -F(2, 7)), GI(F(85, 441)))
        self.assertEqual(I * I, GI(-1))
        self.assertEqual((GI(2, 3) / GI(2, 3)), GI(1))
        with self.assertRaises(ZeroDivisionError):
            GI(1) / GI(0)
        with self.assertRaises(TypeError):
            GI(0.1)
        for operation in (lambda: PolyH(0), lambda: PolyH(1, {(0, (-1, 0)): 1}),
                          lambda: PolyH.q(1, 1), lambda: self.q**-1,
                          lambda: self.q + PolyH.q(2), lambda: self.q.derivative((1,))):
            with self.assertRaises(ValueError):
                operation()

    def test_canonical_commutation_and_known_second_order_product(self):
        q, p, h = self.q, self.p, self.h
        self.assertEqual(star_product(q, p), q*p + h.scale(GI(0, F(1, 2))))
        self.assertEqual(star_product(p, q), q*p - h.scale(GI(0, F(1, 2))))
        self.assertEqual(scaled_moyal_bracket(q, p), PolyH.one(1))
        # Independent three-term differentiation of q^2 star p^2.
        self.assertEqual(star_product(q*q, p*p), q*q*p*p + (h*q*p).scale(GI(0, 2)) - h*h*F(1, 2))
        self.assertEqual(poisson_bracket(q*q, p*p), 4*q*p)

    def test_known_cubic_and_quintic_obstruction_coefficients(self):
        q, p, h = self.q, self.p, self.h
        cubic = egorov_defect(q**3, p**3)
        self.assertEqual(cubic, -h*h*F(3, 2))
        self.assertEqual(classify_defect(cubic), "CENTRAL_DEFECT")
        quintic = egorov_defect(q**5, p**5)
        self.assertEqual(quintic, -150*h*h*q*q*p*p + F(15, 2)*h**4)
        self.assertEqual(classify_defect(quintic), "NONCENTRAL_DEFECT")
        self.assertEqual(quintic.first_hbar_power(), 2)
        hamiltonian = p*p*F(1, 2) + q*q*F(1, 2) + q**4*F(1, 4)
        self.assertEqual(egorov_defect(hamiltonian, p**3), -F(3, 2)*h*h*q)

    def test_multidimensional_lie_sector_and_independent_coordinates(self):
        q1, q2 = PolyH.q(2, 0), PolyH.q(2, 1)
        p1, p2 = PolyH.p(2, 0), PolyH.p(2, 1)
        self.assertEqual(scaled_moyal_bracket(q1, p2), PolyH.zero(2))
        self.assertEqual(scaled_moyal_bracket(q1*p2, q2*p1), q2*p2-q1*p1)
        symbols = monomials_total_degree(2, 2)
        self.assertEqual(len(symbols), 15)
        for _, f in symbols:
            for _, g in symbols:
                self.assertTrue(egorov_defect(f, g).is_zero())
        # Exactness for a quadratic generator applies to high-degree observables.
        self.assertTrue(egorov_defect(q1*q1+p1*p1, q1**7*p1**4+q2**3).is_zero())
        self.assertEqual(star_product(q1*q1, p1*p1).coefficient((2, 0, 2, 0)), GI(1))

    def test_associativity_and_antisymmetry_beyond_safe_sector(self):
        q, p, h = self.q, self.p, self.h
        f, g, k = q**3+2*p, p**3+q*q, q*p+1+h
        self.assertEqual(star_product(star_product(f, g), k), star_product(f, star_product(g, k)))
        self.assertEqual(scaled_moyal_bracket(f, g), -scaled_moyal_bracket(g, f))
        self.assertEqual(star_product(f, PolyH.one(1)), f)

    def test_pullback_composition_and_nonlinear_covariance_boundary(self):
        q, p, h = self.q, self.p, self.h
        phi, psi = (q+p+1, p+2), (q, p+q*q)
        f = q**3+p*p+h
        composed = tuple(pullback(coordinate, psi) for coordinate in phi)
        self.assertEqual(pullback(pullback(f, phi), psi), pullback(f, composed))
        symbols = monomials_total_degree(1, 3)
        for _, a in symbols:
            for _, b in symbols:
                self.assertTrue(covariance_defect(a, b, phi).is_zero())
        a, b = p*p, p
        self.assertEqual(poisson_bracket(pullback(a, psi), pullback(b, psi)), pullback(poisson_bracket(a, b), psi))
        self.assertEqual(covariance_defect(a, b, psi), -h*h*F(1, 2))
        self.assertEqual(pullback(h, psi), h)
        with self.assertRaises(ValueError):
            pullback(f, [q])

    def test_finite_census_and_serializable_receipt(self):
        self.assertEqual(scan_phase_diagram(5), {
            "max_total_degree": 5, "pair_count": 441,
            "counts": {"EXACT": 327, "CENTRAL_DEFECT": 4, "NONCENTRAL_DEFECT": 110}})
        self.assertTrue(covariance_example()["affine_covariance_exact"])
        r = receipt()
        json.dumps(r)
        for key in ("cubic_matches", "quintic_matches", "quartic_matches", "quadratic_2d_exact"):
            self.assertTrue(r[key], key)
        self.assertEqual(r["quadratic_2d_tested_pairs"], 225)


if __name__ == "__main__":
    unittest.main()
