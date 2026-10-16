import itertools
import unittest
from fractions import Fraction as Q

from perfectjet.workflow import decision_pipeline, receipt


class WorkflowTests(unittest.TestCase):
    def test_full_path_recovers_counts_and_certifies(self):
        out = decision_pipeline({})
        self.assertEqual(out["status"], "settled")
        self.assertEqual(out["feasible_count"], 5)
        self.assertEqual(out["selected_bits"], (0, 0, 1))
        self.assertEqual(out["selected_value"], 28)
        self.assertEqual(out["decision"]["margin"], 8)
        costs, values = [(2, 1), (1, 2), (2, 2)], [12, 8, 28]
        feasible = [bits for bits in itertools.product((0, 1), repeat=3)
                    if all(sum(bits[i]*costs[i][j] for i in range(3)) <= 3 for j in range(2))]
        self.assertEqual(len(feasible), out["feasible_count"])
        self.assertEqual(max(sum(v*b for v, b in zip(values, bits)) for bits in feasible), out["selected_value"])
        self.assertEqual(feasible[out["selected_rank"]], out["selected_bits"])

    def test_hidden_information_requires_actual_new_observation(self):
        out = receipt()["hidden"]
        self.assertEqual(out["status"], "needs_measurement")
        self.assertFalse(out["settled"])
        self.assertEqual(out["repair"]["candidate_indices"], [1])
        self.assertEqual(out["repair"]["cost"], 1)
        witness = out["recovery"]["hidden_vector"]
        self.assertEqual(sum(witness), 0)
        self.assertTrue(any(out["recovery"]["target_response"]))

    def test_shared_observation_bounds_are_conservative(self):
        out = decision_pipeline({"observation_errors": ["1/4", "1/2"]})
        self.assertEqual(out["item_error_bounds"], [Q(1, 4), Q(1, 2), Q(5, 4)])
        for dx, dy in itertools.product((-1, 1), repeat=2):
            x, y = 12 + dx*Q(1, 4), 8 + dy*Q(1, 2)
            self.assertGreater(x+2*y, x+y)
        self.assertTrue(out["settled"])
        self.assertFalse(receipt()["uncertain"]["settled"])

    def test_no_fractional_resource_settings_or_inconsistent_data(self):
        for spec in ({"capacities": [True, 3]}, {"observation_errors": [-1, 0]},
                     {"observation": [[1, 0], [2, 0]], "observed": [1, 3]},
                     {"observed": [float('nan'), 1]}):
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                decision_pipeline(spec)

    def test_zero_error_tie_is_a_tie_not_a_precision_request(self):
        out = decision_pipeline({'targets': [[1, 0], [0, 1], [1, 1]]})
        self.assertEqual(out['status'], 'exact_tie')
        self.assertEqual(out['exact_optimal_tie_count'], 2)
        self.assertEqual(set(map(tuple, out['exact_optimal_portfolios'])), {(1, 1, 0), (0, 0, 1)})


if __name__ == '__main__':
    unittest.main()
