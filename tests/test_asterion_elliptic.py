"""Exact elliptic E8 CDYBE, normalization and degeneration controls."""
from fractions import Fraction as Q
import json
import unittest

from perfectjet.asterion_e8 import E8LieAlgebra
from perfectjet.asterion_elliptic import (
    DEFAULT_MULTIPLIERS, EllipticE8R, ThetaKernel, elliptic_receipt,
    rational_cdybe, rational_e8_tensor, trig_to_rational_series,
)


class AsterionEllipticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = E8LieAlgebra()
        cls.model = EllipticE8R(1, cls.g)

    def test_independent_first_nome_coefficients_and_additive_derivative(self):
        kernel = ThetaKernel(2)
        x, y = Q(3), Q(7)
        self.assertEqual(kernel.product_factor(1), (1, 0, 0))
        self.assertEqual(kernel.rho(x), (Q(1), 1 / x - x,
                                         1 / x - x + 1 / x ** 2 - x ** 2))
        p = (x * y - 1) / ((x - 1) * (y - 1))
        dp = -y / (y - 1) ** 2
        correction = -2 - x * y - 1 / (x * y) + x + 1 / x + y + 1 / y
        dcorrection = -x * y + 1 / (x * y) + y - 1 / y
        self.assertEqual(kernel.phi(x, y)[:2], (p, p * correction))
        self.assertEqual(kernel.dphi(x, y)[:2], (dp, dp * correction + p * dcorrection))
        self.assertNotEqual(kernel.phi(x, y)[1], 0)
        # An equal-valued float must not bypass exact-input checks via a cache hit.
        for function in (kernel.phi, kernel.dphi):
            with self.assertRaises(ValueError):
                function(3.0, Q(7))
        for function in (kernel.rho, kernel.product_factor, kernel.log_product_derivative):
            function(Q(3))
            with self.assertRaises(ValueError):
                function(3.0)
        # A zero of the numerator is regular, and its derivative need not vanish.
        self.assertEqual(kernel.phi(2, Q(1, 2)), (0, 0, 0))
        self.assertEqual(kernel.dphi(2, Q(1, 2))[0], -2)

    def test_fay_and_all_opposite_root_slots_through_fourth_nome_order(self):
        kernel = ThetaKernel(4)
        for u, v, a, b in ((2, 3, 5, 7), (3, 5, Q(2, 3), 11),
                            (2, 3, Q(1, 2), 7)):
            self.assertEqual(kernel.root_fay_residual(u, v, a, b), (0,) * 5)
            for residual in kernel.opposite_root_residuals(u, v, a):
                self.assertEqual(residual, (0,) * 5)
        for residual in kernel.opposite_root_residuals(2, 3, Q(1, 3)):
            self.assertEqual(residual, (0,) * 5)

    def test_actual_invariant_metric_and_eight_dynamical_coordinates(self):
        model = self.model
        certificate = model.metric_certificate()
        self.assertTrue(certificate['passed'])
        self.assertEqual(certificate['simple_generator_invariance_checks'], 16)
        self.assertEqual(certificate['casimir_terms'], 304)
        for i in range(8):
            for j in range(8):
                self.assertEqual(sum(self.g.cartan_matrix[i][k] * model.inverse_cartan[k][j]
                                     for k in range(8)), int(i == j))
        tensor = model.tensor()
        self.assertEqual(len(tensor), 304)
        derivatives = model.derivatives()
        for root, a, b in model.root_pairs:
            value = Q(1)
            for multiplier, power in zip(DEFAULT_MULTIPLIERS, root):
                value *= Q(multiplier) ** power
            dphi = model.kernel.dphi(23, value)
            for i in range(8):
                self.assertEqual(derivatives[i].get((a, b), (0, 0)),
                                 tuple(root[i] * coefficient for coefficient in dphi))
            self.assertEqual(self.g.index_root[b], tuple(-coefficient for coefficient in root))

    def test_full_tensor_cdybe_requires_dynamical_derivative(self):
        positive = self.model.cdybe()
        negative = self.model.cdybe(derivative_scale=0)
        self.assertTrue(positive['passed'])
        self.assertEqual(positive['nonzero_bracket_products'], 84816)
        self.assertEqual(positive['residual_components'], 0)
        self.assertFalse(negative['passed'])
        self.assertEqual(negative['residual_components'], 4290)
        self.assertEqual(negative['residual_witness'], positive['ordinary_cybe_witness'])
        self.assertTrue(any(negative['residual_witness'][1]))

    def test_sequential_rational_degeneration_and_independent_tensor(self):
        limit = trig_to_rational_series(2, 3, 6)
        self.assertTrue(limit['passed'])
        self.assertEqual(limit['rho_series'], (Q(1, 2), 0, Q(1, 6), 0,
                                               -Q(1, 90), 0, Q(1, 945)))
        self.assertEqual(limit['phi_series'][0], Q(5, 6))
        u, v = Q(3, 107), Q(5, 109)
        result = rational_cdybe(u, v, algebra=self.g)
        self.assertTrue(result['passed'])
        self.assertEqual(result['residual_components'], 0)
        self.assertGreater(result['ordinary_cybe_nonzero_components'], 0)
        # The rational kernel depends on the root, rather than scaling one bracket.
        tensor = rational_e8_tensor(u, algebra=self.g)
        root = self.g.simple_roots[0]
        a, b = self.g.root_index[root], self.g.root_index[tuple(-x for x in root)]
        self.assertEqual(tensor[a, b], 1 / u + 1)
        self.assertEqual(tensor[b, a], 1 / u - 1)

    def test_exhaustive_receipt_and_domains(self):
        result = elliptic_receipt(exhaustive=True)
        self.assertTrue(result['passed'])
        self.assertEqual(result['p_order'], 2)
        reduction = result['complete_root_fay_reduction']
        self.assertEqual(reduction['ordered_three_root_fay_checks'], 13440)
        self.assertEqual(reduction['opposite_root_tensor_arrangement_checks'], 720)
        self.assertEqual(reduction['zero_weight_tensor_components'], 19712)
        self.assertTrue(result['degenerations']['rational_cdybe']['passed'])
        self.assertFalse(result['quantum_r_matrix_constructed'])
        json.dumps(result)
        for bad in (-1, 5, True, 1.0):
            with self.assertRaises(ValueError):
                ThetaKernel(bad)
        for spectral in (0, 1, 2.0):
            with self.assertRaises(ValueError):
                self.model.tensor(spectral)
        for multipliers in ((1,) * 8, (2,) * 7, (2.0,) + DEFAULT_MULTIPLIERS[1:]):
            with self.assertRaises(ValueError):
                self.model.tensor(multipliers=multipliers)
        with self.assertRaises(ValueError):
            ThetaKernel(1).root_fay_residual(2, 3, 5, 0)
        with self.assertRaises(ValueError):
            rational_cdybe(2, -2)
        with self.assertRaises(ValueError):
            rational_e8_tensor(lambdas=(0,) * 8)
        with self.assertRaises(ValueError):
            trig_to_rational_series(0, 2)
        with self.assertRaises(ValueError):
            elliptic_receipt(exhaustive=1)


if __name__ == '__main__':
    unittest.main()
