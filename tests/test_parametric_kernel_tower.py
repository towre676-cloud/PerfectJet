import json
import unittest
from fractions import Fraction as Q

from perfectjet.parametric_kernel_tower import (
    parametric_kernel_tower, replay_point)
from perfectjet.polynomial import Poly
from perfectjet.transvectants import transvectant

q, p = Poly.variable(0), Poly.variable(1)


def family(delta):
    return q**4*p**2 + delta*q**6


def evolution(h):
    return lambda g: transvectant(h, g, 1)


def constraints(h):
    return [lambda g: transvectant(h, g, 3),
            lambda g: transvectant(h, g, 5)]


class ParametricKernelTowerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.basis = [q**2, q*p, p**2]
        cls.report = parametric_kernel_tower(
            family, cls.basis, evolution, constraints,
            nvars=1, parameter_degree=3, max_depth=2, names=["delta"])

    def test_exceptional_fourfold_family_is_detected(self):
        dims = [row["generic_kernel_dimension"] for row in self.report["depths"]]
        self.assertEqual(dims, [3, 1, 0])

    def test_boundary_delta_zero_is_a_rank_drop_at_depth_two(self):
        depth2 = self.report["depths"][2]
        # Flatten the one-dimensional rational-point lists.
        flat = [pt for c in depth2["drop_locus"]["drop_cells"]
                for pt in c.get("rational_points", [])]
        self.assertIn(["0"], flat)

    def test_report_is_json_serializable(self):
        json.dumps(self.report)

    def test_point_replay_matches_known_strata(self):
        zero = replay_point(self.report, [0], family, self.basis, evolution, constraints)
        one = replay_point(self.report, [1], family, self.basis, evolution, constraints)
        self.assertEqual([r["direct_kernel_dimension"] for r in zero["depths"]], [3, 1, 1])
        self.assertEqual([r["direct_kernel_dimension"] for r in one["depths"]], [3, 1, 0])


if __name__ == "__main__":
    unittest.main()
