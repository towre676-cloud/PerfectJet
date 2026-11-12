import unittest
from fractions import Fraction as Q

from perfectjet.observation_design import (
    coefficient_matrix, invert_with_determinant, optimize_coefficient_panel)


class ObservationDesignTests(unittest.TestCase):
    def test_exact_optimizer(self):
        # Responses 1+x and 1-x. Degrees 0,1 give the only square panel.
        report = optimize_coefficient_panel(
            [{0: 1, 1: 1}, {0: 1, 1: -1}], names=["sum", "difference"])
        self.assertEqual(report["optimal_panel"], [0, 1])
        self.assertEqual(report["optimal_determinant"], "-2")
        self.assertEqual(report["inverse_infinity_norm"], "1")
        self.assertEqual(report["optimal_ties"], 1)

    def test_inverse_replay(self):
        matrix = coefficient_matrix(
            [{0: 1, 2: 2}, {0: 3, 2: 5}], (0, 2))
        inverse, det = invert_with_determinant(matrix)
        self.assertEqual(det, Q(-1))
        for i in range(2):
            for j in range(2):
                self.assertEqual(
                    sum(matrix[i][k]*inverse[k][j] for k in range(2)),
                    Q(i == j))

    def test_contracts(self):
        with self.assertRaises(ValueError):
            optimize_coefficient_panel([])
        with self.assertRaises(ValueError):
            coefficient_matrix([{0: 1}, {1: 1}], [0, 0])


if __name__ == "__main__":
    unittest.main()
