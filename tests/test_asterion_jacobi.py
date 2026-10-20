"""Exact theta refinement must retain charge, heat normalization and anisotropy."""
from fractions import Fraction as Q
import unittest

from perfectjet.asterion_jacobi import (charge_population, elliptic_reindex,
    harmonic_theta_receipt,
    harmonic_projection_coefficients, in_lattice, inner, jacobi_receipt,
    lattice_degree, lattice_shells, shell_moment, spherical_moment, weyl_reflect)


class JacobiRefinementTests(unittest.TestCase):
    def test_complete_shell_enumeration_and_refined_character(self):
        result = jacobi_receipt(5)
        self.assertTrue(result["passed"])
        self.assertEqual(result["lattice_shell_counts"], (1,240,2160,6720,17520,30240))
        self.assertEqual(result["refined_character_totals"][-1], 1057504)
        self.assertFalse(any(result["heat_residual"]))

    def test_charge_multiplicities_distinguish_lattice_and_oscillators(self):
        root = (2,-2,0,0,0,0,0,0)
        self.assertEqual(charge_population(1, root), 1)
        self.assertEqual(charge_population(3, root), 44)
        self.assertEqual(charge_population(1, (0,)*8), 8)
        self.assertEqual(charge_population(1, tuple(2*x for x in root)), 0)
        self.assertEqual(charge_population(2, (2,0,0,0,0,0,0,0)), 0)

    def test_elliptic_reindex_is_untruncated_and_allows_negative_exponents(self):
        root = (2,-2,0,0,0,0,0,0)
        result = elliptic_reindex(tuple(-x for x in root), root)
        self.assertEqual(result["translated_charge"], (0,)*8)
        self.assertEqual(result["exponent"], -1)
        self.assertEqual(inner(root, root), 2)

    def test_weyl_reflection_preserves_charge_degree(self):
        root = (1,-1,-1,-1,-1,-1,-1,1)
        for vector in lattice_shells(2)[2]:
            image = weyl_reflect(vector, root)
            self.assertTrue(in_lattice(image))
            self.assertEqual(lattice_degree(image), 2)
            self.assertEqual(weyl_reflect(image, root), vector)

    def test_degree8_boundary_has_exact_ramanujan_sign(self):
        first, second = lattice_shells(2)[1:3]
        defect1 = shell_moment(first, (8,))-spherical_moment(len(first),1,(8,))
        defect2 = shell_moment(second, (8,))-spherical_moment(len(second),2,(8,))
        self.assertEqual(defect1, Q(-3,2))
        self.assertEqual(defect2, -24*defect1)
        # The all-odd tensor component cannot be recovered from axis sampling.
        self.assertEqual(shell_moment(first, (1,)*8), Q(1,2))
        self.assertEqual(shell_moment(second, (1,)*8), -12)

    def test_harmonic_projection_recurrence(self):
        a = harmonic_projection_coefficients()
        self.assertEqual(a, (Q(1),Q(-7,5),Q(7,12),Q(-7,96),Q(1,768)))
        for j in range(4):
            power = 8-2*j
            self.assertEqual(a[j]*power*(power-1)
                             +a[j+1]*2*(j+1)*(8+16-2*(j+1)-2), 0)

    def test_higher_angular_sectors_use_complete_modular_sturm_panels(self):
        result = harmonic_theta_receipt(5)
        self.assertTrue(result["passed"])
        sectors = {x["harmonic_degree"]:x for x in result["sectors"]}
        for degree in (2,4,6,10):
            self.assertEqual(sectors[degree]["cusp_dimension"],0)
            self.assertTrue(all(Q(x)==0 for x in sectors[degree]["axis_weighted_theta"]))
        self.assertEqual(sectors[8]["axis_specialized_coefficients"],("-3/2",))
        self.assertEqual(sectors[12]["axis_specialized_coefficients"],("441/416",))
        self.assertEqual(sectors[20]["cusp_dimension"],2)
        for row in result["sectors"]:
            self.assertTrue(all(Q(x)==0 for x in row["residual"]))

    def test_bounds_and_wrong_lattice_are_rejected(self):
        for degree in (-1, True, 9, 1.5):
            with self.assertRaises(ValueError):
                lattice_shells(degree)
        with self.assertRaises(ValueError):
            elliptic_reindex((2,0,0,0,0,0,0,0), (0,)*8)
        with self.assertRaises(ValueError):
            weyl_reflect((0,)*8, (0,)*8)
        with self.assertRaises(ValueError):
            inner((0,)*7, (0,)*8)


if __name__ == "__main__":
    unittest.main()
