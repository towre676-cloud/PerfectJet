import json
import unittest
from fractions import Fraction as Q

from perfectjet.polynomial import Poly
from perfectjet.partner_structure import (affine_gate, high_multiplicity_basis,
    indicial, monomial_dimension, monomial_partner_exponents,
    polynomial_certificate, possible_valuations, receipt)
from perfectjet.transvectants import partner_dimensions, transvectant

x, y = Poly.variable(0), Poly.variable(1)


class PartnerStructureTests(unittest.TestCase):
    def test_symbolic_factorizations_and_resultants(self):
        rows = polynomial_certificate()
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(r['third_factorization'] and r['fifth_factorization']
                            and r['resultant_identity'] for r in rows))
        self.assertTrue(all(e['exponents'][1] == 0 for r in rows for e in r['resultant']))

    def test_affine_identity_against_mixed_derivatives(self):
        f = x**6+2*x**5*y-3*x**3*y**3+Q(2, 3)*y**6
        for n in (3, 4, 5, 12, 23):
            g = x**n-2*x**(n-2)*y**2+3*y**n
            for r in (1, 3, 5):
                mixed = transvectant(f, g, r)
                dehom = Poly({(e[0],): c for e, c in mixed.terms.items()}, 1)
                self.assertEqual(affine_gate(f, g, n, r), dehom)

    def test_indicial_coefficients_against_actual_monomials(self):
        for n in (3, 7, 22):
            for k in range(7):
                for s in range(n+1):
                    f, g = x**k*y**(6-k), x**s*y**(n-s)
                    for r in (3, 5):
                        value = indicial(r, k, n, s)
                        result = transvectant(f, g, r)
                        expected = Poly({(k+s-r, n+6-k-s-r): value}) if value else Poly()
                        self.assertEqual(result, expected)

    def test_uniform_valuation_table_and_large_degrees(self):
        for n in tuple(range(13, 45))+(100, 101):
            for k in range(7):
                # For monomial f, the local obstruction is sufficient too.
                self.assertEqual(monomial_partner_exponents(k, n), possible_valuations(k, n))

    def test_complete_high_root_kernels_beyond_degree_twenty(self):
        for k, n in ((4, 7), (5, 5), (6, 3), (4, 23), (5, 24), (6, 25)):
            h = (x*x+x*y+2*y*y) if k == 4 else (x+2*y if k == 5 else Poly.constant(1))
            f = x**k*h
            basis = high_multiplicity_basis(x, k, n)
            self.assertEqual(len(basis), k-3)
            self.assertEqual(partner_dimensions(f, n)['kernel_dimension'], k-3)
            self.assertTrue(all(transvectant(f, g, 3) == 0 and transvectant(f, g, 5) == 0 for g in basis))

    def test_coordinate_transport_and_activity(self):
        ell, m = x-y, x+2*y
        f = ell**4*(m*m+ell*m+2*ell*ell)
        for g in high_multiplicity_basis(ell, 4, 21):
            self.assertEqual(transvectant(f, g, 3), 0)
            self.assertEqual(transvectant(f, g, 5), 0)
            self.assertNotEqual(transvectant(f, g, 1), 0)
        self.assertEqual(transvectant(ell**6, ell**21, 1), 0)

    def test_all_degree_pure_power_iff(self):
        for n in (3, 4, 12, 27):
            g = x**n
            for k in range(7):
                f = x**k*y**(6-k)
                self.assertEqual(transvectant(f, g, 3) == 0 and transvectant(f, g, 5) == 0, k >= 4)

    def test_two_triple_roots_and_dimension_series(self):
        f = x**3*y**3
        for n in (13, 14, 21, 22):
            result = partner_dimensions(f, n)
            self.assertEqual(result['kernel_dimension'], int(n % 2 == 0))
            self.assertEqual(result['active_dimension'], 0)
        for k in range(7):
            for n in tuple(range(3, 45))+(100, 101):
                self.assertEqual(len(monomial_partner_exponents(k, n)), monomial_dimension(k, n))
        for k, n, expected in ((5, 4, 3), (4, 6, 2), (3, 12, 3)):
            self.assertEqual(partner_dimensions(x**k*y**(6-k), n)['kernel_dimension'], expected)

    def test_finite_jet_dimensions_on_concrete_strata(self):
        for n in (7, 21):
            self.assertLessEqual(partner_dimensions(x**6+y**6, n)['kernel_dimension'], 2)
            self.assertLessEqual(partner_dimensions(x*x*(x**4+y**4), n)['kernel_dimension'], 1)

    def test_contracts_and_serializable_receipt(self):
        for k, n in ((4, 6), (5, 4), (6, 2)):
            with self.assertRaises(ValueError):
                high_multiplicity_basis(x, k, n)
        with self.assertRaises(ValueError):
            possible_valuations(3, 12)
        with self.assertRaises(ValueError):
            high_multiplicity_basis(x*x, 4, 21)
        packet = receipt()
        json.dumps(packet)
        self.assertIn('squarefree', packet['unresolved'])
        self.assertIn('no new Lean', packet['formal_status'])


if __name__ == '__main__':
    unittest.main()
