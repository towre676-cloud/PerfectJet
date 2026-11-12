import unittest
from fractions import Fraction as Q

from perfectjet.observation_design import certify_l1_sensor_global_optimum
from perfectjet.cubic_certificate_search import (
    maximal_power_order_pattern, scout_cubics, translate, eisenstein)


class DiscoveryEngineTests(unittest.TestCase):
    def test_l1_dual_certificate(self):
        polys = [{0: 1, 1: 1}, {0: 1, 1: -1}]
        result = certify_l1_sensor_global_optimum(polys, [0, 1], 0)
        self.assertTrue(result["global_optimal"])
        self.assertEqual(result["global_optimal_gain"], "1")
        self.assertEqual(result["dual_objective"], "1")

    def test_reject_noncritical_coordinate(self):
        polys = [{0: 1, 1: 1}, {0: 1, 1: -1}]
        with self.assertRaises(ValueError):
            certify_l1_sensor_global_optimum(polys, [0, 1], 2)

    def test_cubic_37_101_197(self):
        for coefficients, disc in [
            ([1, -1, -3, 1], 148),
            ([2, 0, -4, 1], 404),
            ([2, -2, -4, 1], 788),
            ([11, -9, -1, 1], 1556),
        ]:
            result = maximal_power_order_pattern(coefficients)
            self.assertEqual(result["status"], "certified_pattern")
            self.assertEqual(result["discriminant"], disc)
            self.assertTrue(result["maximal_power_order"])

    def test_nonmaximal_order_rejected(self):
        # Z[sqrt(5)] has discriminant 20 but is not maximal at 2.
        result = maximal_power_order_pattern([-5, 0, 1, 1])
        self.assertNotEqual(result["status"], "certified_pattern")

    def test_small_scout(self):
        report = scout_cubics(a_bound=4, b_bound=5, c_bound=3, max_results=5)
        self.assertTrue(report["results"])
        self.assertTrue(all(row["maximal_power_order"] for row in report["results"]))


if __name__ == "__main__":
    unittest.main()
