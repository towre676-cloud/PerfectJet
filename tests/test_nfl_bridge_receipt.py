"""Independent expectations for the analytic math-bridge receipt, not NFL data."""

import importlib.util
import json
import unittest
from fractions import Fraction as Q


NUMPY = importlib.util.find_spec("numpy") is not None
if NUMPY:
    import numpy as np
    from perfectjet.applications.nfl_scouting.bridge_receipt import build_bridge_receipt


@unittest.skipUnless(NUMPY, "Optional scouting NumPy dependency is unavailable")
class BridgeReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = build_bridge_receipt()

    def test_full_receipt_is_losslessly_json_serializable_and_disclaims_nfl_evidence(self):
        encoded = json.dumps(self.receipt, allow_nan=False)
        self.assertEqual(json.loads(encoded), self.receipt)
        self.assertFalse(self.receipt["real_nfl_experiment_executed"])
        self.assertFalse(self.receipt["raw_competition_data_required"])
        self.assertIn("no NFL prediction improvement", self.receipt["evidence_scope"])
        for key in ("exact_history_bridge", "numerical_predictive_state_bridge",
                    "readout_identifiability_bridge", "finite_quotient_bridge",
                    "joint_measurement_allocation_bridge"):
            self.assertTrue(self.receipt[key]["equations"])
            self.assertTrue(self.receipt[key]["assumptions"])
            self.assertTrue(self.receipt[key]["scope"])

    def test_exact_hidden_history_counterexample_has_correct_next_values(self):
        result = self.receipt["exact_history_bridge"]
        pair = result["same_current_different_future"]
        self.assertEqual(Q(pair["current_a"]), Q(pair["current_b"]))
        self.assertEqual(Q(pair["next_a"]), Q(3, 2))
        self.assertEqual(Q(pair["next_b"]), 0)
        closure = result["closure_report"]
        self.assertTrue(closure["answer"]["closed"])
        self.assertEqual(closure["answer"]["minimal_dimension"], 2)
        self.assertEqual(closure["history"][0]["missing"], 1)
        self.assertEqual(closure["history"][-1]["missing"], 0)
        obstruction = result["instantaneous_observation_report"]
        self.assertEqual(obstruction["obstruction"]["class"], "structural_invisibility")
        self.assertEqual(obstruction["next"]["add_sensors"], [0])

    def test_numerical_forecasts_match_independent_rational_recurrence(self):
        result = self.receipt["numerical_predictive_state_bridge"]["noiseless_report"]
        self.assertEqual(result["representation"]["state_count"], 2)
        self.assertEqual(result["representation"]["history_steps"], 2)
        self.assertEqual(result["answer"]["heldout_athletes"], 6)
        self.assertLess(result["answer"]["heldout_delay_mse"], 1e-20)
        self.assertGreater(result["answer"]["heldout_instantaneous_mse"], 0.01)
        # Independent exact recurrence, rather than reading fitted parameters.
        for name, initial in (("forecast_a", [Q(0), Q(1)]), ("forecast_b", [Q(2), Q(1)])):
            values = list(initial)
            for _ in range(3):
                values.append(Q(3, 2) * values[-1] - Q(3, 4) * values[-2])
            expected = np.asarray([[float(value)] for value in values[2:]])
            np.testing.assert_allclose(result["answer"][name], expected, atol=1e-10, rtol=0)

    def test_noisy_fixture_has_positive_error_and_declared_finite_tolerance(self):
        result = self.receipt["numerical_predictive_state_bridge"]["noisy_fixture"]
        self.assertTrue(result["inner_meets_declared_tolerance"])
        self.assertGreater(result["unseen_player_rmse"], 0.001)
        self.assertLess(result["unseen_player_rmse"], result["declared_standardized_rmse_tolerance"])
        self.assertLess(result["inner_rmse"], result["instantaneous_inner_rmse"])
        self.assertEqual(result["heldout_players"], 6)

    def test_positive_duration_fits_have_equal_crossing_but_different_onset(self):
        result = self.receipt["readout_identifiability_bridge"]
        fits = result["two_positive_duration_fits"]
        a, b = map(lambda key: [Q(value) for value in fits[key]], ("components_a", "components_b"))
        self.assertTrue(all(value > 0 for value in a + b))
        self.assertEqual(sum(a), sum(b))
        self.assertNotEqual(a[0], b[0])
        witness = [Q(value) for value in result["exact_witness"]]
        self.assertEqual(sum(witness), 0)
        self.assertNotEqual(witness[0], 0)
        self.assertEqual(result["repair"]["rows"], [1])
        self.assertEqual(result["repair"]["needed"], 1)

    def test_quotient_replays_and_separates_equal_initial_readouts(self):
        result = self.receipt["finite_quotient_bridge"]
        report = result["engine_report"]
        self.assertEqual(report["representation"]["original_states"], 4)
        self.assertEqual(report["representation"]["quotient_states"], 2)
        self.assertEqual(report["answer"]["blocks"], [[0, 1], [2, 3]])
        self.assertTrue(all(identity["replayed"] for identity in report["identities"]))
        pair = result["same_initial_different_future"]
        self.assertEqual(pair["initial_output_a"], pair["initial_output_b"])
        self.assertNotEqual(pair["next_output_a"], pair["next_output_b"])
        self.assertEqual(len(pair["quotient_blocks"]), 3)

    def test_joint_package_values_match_independent_two_by_two_inverse(self):
        result = self.receipt["joint_measurement_allocation_bridge"]
        actual = result["result"]
        # Posterior precision for mixed+nuisance is [[11,10],[10,21]],
        # hence target posterior variance 21/(11*21-100).  For direct+mixed
        # it is [[12,10],[10,11]], hence target variance 11/(12*11-100).
        exact_optimum = 1 - Q(21, 11 * 21 - 100)
        exact_greedy = 1 - Q(11, 12 * 11 - 100)
        self.assertEqual(Q(actual["optimal_joint_reduction"]), exact_optimum)
        self.assertEqual(Q(actual["greedy_joint_reduction"]), exact_greedy)
        self.assertEqual(exact_optimum, Q(110, 131))
        self.assertEqual(exact_greedy, Q(21, 32))
        self.assertEqual(Q(actual["isolated_reductions"]["nuisance"]), 0)
        self.assertEqual(actual["optimal_selected"], ["mixed", "nuisance"])
        self.assertEqual(actual["feasible_packages"], 7)
        self.assertEqual(Q(result["exact_gain_over_isolated_greedy"]), Q(769, 4192))


if __name__ == "__main__":
    unittest.main()
