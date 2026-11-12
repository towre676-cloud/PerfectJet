import json
import unittest

from perfectjet.kernel_tower import matrix_kernel_tower, polynomial_kernel_tower
from perfectjet.polynomial import Poly
from perfectjet.transvectants import transvectant

q, p = Poly.variable(0), Poly.variable(1)


class KernelTowerTests(unittest.TestCase):
    def test_matrix_observability_tower(self):
        result = matrix_kernel_tower([[1, 0]], [[0, 1], [0, 0]])
        self.assertTrue(result["stabilized"])
        self.assertEqual(result["stabilization_depth"], 1)
        self.assertEqual([r["kernel_dimension"] for r in result["history"]], [1, 0])
        self.assertEqual(result["persistent_kernel_dimension"], 0)
        self.assertTrue(result["observable_row_space_closed"])
        json.dumps(result)

    def test_four_one_one_sextic_dies_at_second_refinement(self):
        h = q**4*p**2 + q**6
        basis = [q**2, q*p, p**2]
        result = polynomial_kernel_tower(
            basis,
            evolution=lambda g: transvectant(h, g, 1),
            constraints=[
                lambda g: transvectant(h, g, 3),
                lambda g: transvectant(h, g, 5),
            ],
        )
        # depth 0 = static gates, depth 1 = first refinement, depth 2 = second.
        self.assertEqual([r["kernel_dimension"] for r in result["history"]], [3, 1, 0])
        self.assertEqual(result["history"][1]["kernel_basis"], [["0", "1", "0"]])
        self.assertEqual(result["stabilization_depth"], 2)
        self.assertEqual(result["persistent_kernel_dimension"], 0)

    def test_sixfold_root_stabilizes_immediately_after_static_gate(self):
        h = q**6
        basis = [q**4, q**3*p, q**2*p**2, q*p**3, p**4]
        result = polynomial_kernel_tower(
            basis,
            evolution=lambda g: transvectant(h, g, 1),
            constraints=[
                lambda g: transvectant(h, g, 3),
                lambda g: transvectant(h, g, 5),
            ],
        )
        self.assertTrue(result["stabilized"])
        self.assertEqual(result["stabilization_depth"], 0)
        self.assertEqual([r["kernel_dimension"] for r in result["history"]], [3, 3])
        self.assertEqual(
            result["persistent_kernel_basis"],
            [["1", "0", "0", "0", "0"],
             ["0", "1", "0", "0", "0"],
             ["0", "0", "1", "0", "0"]],
        )

    def test_contracts(self):
        with self.assertRaises(ValueError):
            matrix_kernel_tower([], [[1]])
        with self.assertRaises(ValueError):
            polynomial_kernel_tower([], lambda x: x, [lambda x: x])


if __name__ == "__main__":
    unittest.main()
