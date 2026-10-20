"""Exact theta-period checks with explicit nome and cusp precision tests."""
from fractions import Fraction as Q
import json
import unittest

from perfectjet.asterion_periods import (
    compose, embed_q_series, hypergeometric_period_coefficients, periods_receipt,
    power, reciprocal, theta_lambda_series,
)


class AsterionPeriodsTests(unittest.TestCase):
    def test_known_series_and_exact_hypergeometric_composition(self):
        result = periods_receipt(16)
        self.assertTrue(result['passed'])
        self.assertEqual(result['lambda_coefficients'][:7], [0, 16, -128, 704, -3072, 11488, -38400])
        self.assertEqual(hypergeometric_period_coefficients(4), (1, Q(1, 4), Q(9, 64), Q(25, 256), Q(1225, 16384)))
        self.assertEqual(result['composed_period_coefficients'][:6], [1, 4, 4, 0, 4, 8])
        self.assertEqual(result['normalized_character_cube_Q_coefficients'][:7], [1, 0, 744, 0, 196884, 0, 21493760])
        self.assertEqual(result['normalized_character_cube_Q_coefficients'],
                         result['period_cancelled_character_cube_Q_coefficients'])
        self.assertTrue(all(not any(row) for row in result['residuals'].values()))
        json.dumps(result)

    def test_nome_Q_and_character_q_cannot_be_interchanged(self):
        from perfectjet.asterion_currents import CurrentPopulations, e4_coefficients
        result = periods_receipt(6)
        wrong_e4 = embed_q_series(e4_coefficients(6), 6, q_power=1)
        right_e4 = embed_q_series(e4_coefficients(3), 6, q_power=2)
        self.assertEqual(wrong_e4[1], 240)
        self.assertEqual(right_e4[1], 0)
        self.assertNotEqual(list(wrong_e4), result['e4_Q_coefficients'])
        wrong_character = embed_q_series(CurrentPopulations(6).simple, 6, q_power=1)
        self.assertEqual(power(wrong_character, 3, 6)[1], 744)
        self.assertEqual(result['normalized_character_cube_Q_coefficients'][1], 0)
        self.assertEqual(result['nome_convention']['character_variable'], 'q=exp(2*pi*i*tau)=Q^2')

    def test_cusp_cancellation_uses_guard_orders_and_rejects_nonunits(self):
        low = periods_receipt(5)
        high = periods_receipt(12)
        self.assertEqual(low['internal_order'], 7)
        self.assertEqual(low['guard_orders_for_cusp_cancellation'], 2)
        self.assertEqual(low['period_cancelled_character_cube_Q_coefficients'],
                         high['period_cancelled_character_cube_Q_coefficients'][:6])
        lam = theta_lambda_series(8)['lambda']
        self.assertEqual(lam[0], 0)
        with self.assertRaises(ValueError):
            reciprocal(lam, 8)
        with self.assertRaises(ValueError):
            compose([1, 1], [1, 1], 4)

    def test_boundaries_and_maximum_precision_remain_exact(self):
        result = periods_receipt(40)
        self.assertTrue(result['passed'])
        self.assertEqual(result['checks']['character_cube_coefficients'], 41)
        self.assertEqual(result['checks']['period_coefficients'], 43)
        for bad in (-1, 41, True, 4.0):
            with self.assertRaises(ValueError):
                periods_receipt(bad)
        for bad in (0, -2, True):
            with self.assertRaises(ValueError):
                embed_q_series([1, 2], 4, q_power=bad)


if __name__ == '__main__':
    unittest.main()
