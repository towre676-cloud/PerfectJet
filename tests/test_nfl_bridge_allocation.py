import itertools
import unittest
from fractions import Fraction as Q

from perfectjet.applications.nfl_scouting.allocation import (
    MeasurementCandidate, MeasurementBlockCandidate, TargetInformationModel,
)
from perfectjet.applications.nfl_scouting.bridge_allocation import (
    FrozenTrainingReceipt, plan_contender_measurements, plan_from_fitted_loading, plan_from_bridge_fit,
    rationalize_fitted_loading,
)


def training_receipt():
    return FrozenTrainingReceipt(("train-a", "train-b"), 2024,
                                 held_out_athlete_ids=("eval-a", "eval-b"),
                                 model_id="frozen physical bridge outer fold",
                                 latest_training_outcome=2024)


class LoadingProvenanceTests(unittest.TestCase):
    def test_receipt_checks_athletes_and_distinguishes_season_from_calendar_cutoff(self):
        audit = training_receipt().audit(("eval-a",))
        self.assertEqual(audit["cutoff_kind"], "NFL season")
        self.assertEqual(audit["outcome_cutoff"], 2024)
        self.assertTrue(audit["declared_training_evaluation_disjointness_checked"])
        self.assertFalse(audit["training_chronology_independently_verified"])
        self.assertEqual(len(audit["receipt_sha256"]), 64)
        dated = FrozenTrainingReceipt((1, 2), "2024-09-01", latest_training_outcome="2024-08-31")
        self.assertEqual(dated.audit()["cutoff_kind"], "calendar date")
        self.assertEqual(dated.training_athlete_ids, ("1", "2"))
        with self.assertRaises(ValueError):
            FrozenTrainingReceipt((1,), 2024, held_out_athlete_ids=("1",))
        with self.assertRaises(ValueError):
            FrozenTrainingReceipt((1.0,), 2024, held_out_athlete_ids=("1",))
        with self.assertRaises(ValueError):
            training_receipt().audit(("train-a",))
        with self.assertRaises(ValueError):
            FrozenTrainingReceipt(("a",), 2023, latest_training_outcome=2024)
        with self.assertRaises(ValueError):
            FrozenTrainingReceipt(("a",), 2024, latest_training_outcome="2024-08-31")
        with self.assertRaises(ValueError):
            FrozenTrainingReceipt((), 2024)

    def test_rationalization_reports_visible_snapshot_error_and_version(self):
        receipt = rationalize_fitted_loading([0.3333334, -0.2], max_denominator=10,
                                             max_abs_error="0.000001")
        self.assertEqual(receipt["rational_loadings"], ((Q(1, 3), Q(-1, 5)),))
        self.assertEqual(receipt["original_decimal_snapshot"], ((Q("0.3333334"), Q(-1, 5)),))
        self.assertEqual(receipt["coefficient_absolute_errors"][0][0], Q(1, 15000000))
        self.assertFalse(receipt["exact_learned_truth_claim"])
        self.assertEqual(receipt["schema"], "pj-nfl-fitted-loading/1")
        with self.assertRaises(ValueError):
            rationalize_fitted_loading([0.3333334], max_denominator=10, max_abs_error="1e-9")
        for values in ([float("nan")], [float("inf")], [], [[1], [1, 2]]):
            with self.assertRaises(ValueError):
                rationalize_fitted_loading(values)


class FittedLoadingPlanningTests(unittest.TestCase):
    def test_model_loading_connects_to_exact_joint_package_without_claiming_physiology(self):
        candidates = [MeasurementCandidate("direct", (1, 0), 1, 1),
                      MeasurementCandidate("mixed", (1, 1), Q(1, 10), 1),
                      MeasurementCandidate("nuisance", (0, 1), Q(1, 10), 1)]
        result = plan_from_fitted_loading([1.0, 0.0], [[1, 0], [0, 1]], candidates, 2,
                                          training_receipt(), evaluation_athlete_ids=("eval-a",))
        self.assertEqual(result["allocation"]["candidate_ids"], ("mixed", "nuisance"))
        self.assertEqual(result["allocation"]["objective_reduction"], Q(110, 131))
        self.assertEqual(result["original_snapshot_selected_objective"], Q(110, 131))
        self.assertEqual(result["rationalization_guarantee"]["original_snapshot_optimality_gap_bound"], 0)
        self.assertIn("not a physiological law", result["loading_scope"])
        self.assertIn("not established NFL", result["evidence_scope"])

    def test_multihypothesis_robust_planning_and_zero_hypothesis(self):
        candidates = [MeasurementCandidate("one", (1, 0), Q(1, 10), 1),
                      MeasurementCandidate("both", (1, 1), 1, 1)]
        result = plan_from_fitted_loading([[1.0, 0.0], [0.0, 1.0]], [[1, 0], [0, 1]],
                                          candidates, 1, training_receipt())
        self.assertEqual(result["allocation"]["candidate_ids"], ("both",))
        self.assertEqual(result["allocation"]["objective"], "worst_target")
        zero = plan_from_fitted_loading([[1.0, 0.0], [0.0, 0.0]], [[1, 0], [0, 1]],
                                        candidates, 1, training_receipt())
        self.assertEqual(zero["allocation"]["objective_reduction"], 0)
        self.assertEqual(zero["allocation"]["candidate_ids"], ())

    def test_exact_rationalization_regret_bound_covers_independent_snapshot_optimum(self):
        prior = [[1, Q(1, 3)], [Q(1, 3), 2]]
        candidates = [MeasurementCandidate("x", (1, 0), Q(1, 4), 1),
                      MeasurementCandidate("mixed", (1, 1), Q(1, 3), 1),
                      MeasurementCandidate("y", (0, 1), Q(1, 2), 1)]
        raw = [[0.3333334, 0.2222223], [0.5000002, -0.1666668]]
        result = plan_from_fitted_loading(raw, prior, candidates, 1, training_receipt(),
                                          max_denominator=12, max_abs_error="0.000001")
        original = TargetInformationModel(prior, result["rationalization"]["original_decimal_snapshot"])
        maximum = original.optimize_package(candidates, 1, objective="worst_target")["objective_reduction"]
        gap = maximum - result["original_snapshot_selected_objective"]
        self.assertGreaterEqual(gap, 0)
        self.assertLessEqual(gap, result["rationalization_guarantee"]["original_snapshot_optimality_gap_bound"])
        bound = result["rationalization_guarantee"]["uniform_objective_error_bound"]
        quantized = TargetInformationModel(prior, result["rationalization"]["rational_loadings"])
        for bits in itertools.product((0, 1), repeat=3):
            selected = [candidate for bit, candidate in zip(bits, candidates) if bit]
            raw_package = original.package_information(selected)
            rounded_package = quantized.package_information(selected)
            raw_score = original._objective(raw_package["source_covariance_after"], "worst_target")
            rounded_score = quantized._objective(rounded_package["source_covariance_after"], "worst_target")
            self.assertLessEqual(abs(raw_score - rounded_score), bound)

    def test_correlated_block_attempts_reach_bridge_and_duplicate_guards(self):
        block = MeasurementBlockCandidate("block", ((1, 0), (0, 1)),
                                           ((1, Q(1, 2)), (Q(1, 2), 1)), 1,
                                           attempt_ids=("new-attempt",))
        result = plan_from_fitted_loading([1.0, 1.0], [[1, 0], [0, 1]], [block], 1,
                                          training_receipt())
        self.assertEqual(result["allocation"]["objective_reduction"], Q(4, 5))
        duplicate = MeasurementCandidate("frame-branch", (1, 0), 1, 1,
                                         attempt_ids=("new-attempt",))
        with self.assertRaises(ValueError):
            plan_from_fitted_loading([1, 1], [[1, 0], [0, 1]], [block, duplicate], 2,
                                      training_receipt())

    def test_dictionary_receipt_and_existing_observations(self):
        receipt = {"training_athlete_ids": ["a", "b"], "outcome_cutoff": "2024",
                   "model_id": "frozen-fold", "held_out_athlete_ids": ["eval"]}
        result = plan_from_fitted_loading([1.0], [[1]], [MeasurementCandidate("new", (1,), 1, 1)],
                                          1, receipt, evaluation_athlete_ids=("eval",),
                                          design=[[1]], observation_ids=("old",))
        self.assertEqual(result["allocation"]["objective_reduction"], Q(1, 6))
        self.assertFalse(result["training"]["latest_training_outcome_checked"])
        with self.assertRaises(ValueError):
            plan_from_fitted_loading([1], [[1]], [], 0, receipt, evaluation_athlete_ids=("a",))

    def test_contender_wrapper_excludes_training_players_and_preserves_uncertainty_scope(self):
        candidates = [MeasurementCandidate("a", (1, 0), 1, 1, athlete_id="eval-a"),
                      MeasurementCandidate("b", (0, 1), 1, 1, athlete_id="eval-b")]
        result = plan_contender_measurements([[1.0, 0.0], [0.0, 1.0]], [[1, 0], [0, 1]],
                                             candidates, 1, training_receipt(),
                                             {"eval-a": (0, 2), "eval-b": (1, 3)},
                                             target_ids=("eval-a", "eval-b"),
                                             empirical_uncertainty={"eval-a": (-10, 10)})
        self.assertEqual(result["decision_allocation"]["allocation"]["objective_reduction"], Q(1, 2))
        self.assertEqual(result["original_snapshot_selected_objective"], Q(1, 2))
        decision = result["decision_allocation"]["decision"]
        self.assertEqual(decision["empirical_uncertainty"]["eval-a"], (-10, 10))
        self.assertIsNone(decision["statistical_confidence_claim"])
        with self.assertRaises(ValueError):
            plan_contender_measurements([[1, 0], [0, 1]], [[1, 0], [0, 1]], candidates, 1,
                                         training_receipt(), {"train-a": (0, 2)},
                                         target_ids=("train-a", "eval-b"))


class ActualBridgeFitConnectionTests(unittest.TestCase):
    @staticmethod
    def fitted_result(synthetic=True):
        return {"ids": ["eval-a"], "year": 2025, "synthetic": synthetic,
                "frozen_jacobian": {"source_features": ["displacement", "retention"],
                                    "source_to_movement": [[1.0, 1.0], [0.0, 1.0]],
                                    "movement_to_outcome": [1.0, -1.0],
                                    "source_to_outcome": [1.0, 0.0],
                                    "scope": "conditional frozen affine fitted sensitivity"},
                "full_stage_audit": {"training_ids": ["train-a", "train-b"],
                                     "training_group_ids": ["train-a", "train-b"],
                                     "evaluated_ids": ["eval-a"],
                                     "state_training_ids": ["train-a"],
                                     "movement_training_ids": ["train-a", "train-b"]}}

    def test_actual_fit_schema_routes_learned_physical_loading_to_exact_package(self):
        candidates = [MeasurementCandidate("direct", (1, 0), 1, 1),
                      MeasurementCandidate("mixed", (1, 1), Q(1, 10), 1),
                      MeasurementCandidate("nuisance", (0, 1), Q(1, 10), 1)]
        result = plan_from_bridge_fit(self.fitted_result(), [[1, 0], [0, 1]], candidates, 2)
        self.assertEqual(result["allocation"]["candidate_ids"], ("mixed", "nuisance"))
        self.assertEqual(result["allocation"]["objective_reduction"], Q(110, 131))
        self.assertEqual(result["source_feature_order"], ("displacement", "retention"))
        self.assertEqual(result["training"]["outcome_cutoff"], 2024)
        self.assertEqual(result["training"]["training_athlete_ids"], ("train-a", "train-b"))
        self.assertTrue(result["jacobian_composition_audit"]["passed"])
        self.assertFalse(result["jacobian_composition_audit"]["loading_override_allowed"])
        self.assertIn("synthetic", result["evidence_scope"])
        with self.assertRaises(TypeError):
            plan_from_bridge_fit(self.fitted_result(), [[1, 0], [0, 1]], [], 0, frozen_loadings=[0, 1])

    def test_nested_actual_receipt_uses_original_athletes_and_preserves_latest_outcome(self):
        fit = self.fitted_result()
        fit["full_stage_audit"]["training_ids"] = ["train-a#copy0", "train-b#copy0"]
        fit["full_stage_audit"]["evaluated_ids"] = ["eval-a#copy0"]
        fit["ids"] = ["eval-a#copy0"]
        fit["frozen_jacobian"]["training_receipt"] = {
            "training_athlete_ids": ["train-a", "train-b"],
            "held_out_athlete_ids": ["eval-a"], "outcome_cutoff": 2024,
            "latest_training_outcome": 2023, "model_id": "actual nested fitted receipt"}
        fit["frozen_jacobian"]["training_cutoff_exclusive"] = 2025
        result = plan_from_bridge_fit(fit, [[1, 0], [0, 1]], [], 0)
        self.assertEqual(result["training"]["training_athlete_ids"], ("train-a", "train-b"))
        self.assertEqual(result["training"]["latest_training_outcome"], 2023)
        self.assertEqual(result["training"]["model_id"], "actual nested fitted receipt")
        self.assertTrue(result["training"]["latest_training_outcome_checked"])
        self.assertEqual(set(result["training"]["held_out_athlete_ids"]), {"eval-a", "eval-a#copy0"})
        self.assertEqual(result["fitted_training_ids"], ("train-a#copy0", "train-b#copy0"))

    def test_corrupted_composition_and_training_provenance_are_rejected(self):
        fit = self.fitted_result(False)
        fit["frozen_jacobian"]["source_to_outcome"] = [0.0, 1.0]
        with self.assertRaises(ValueError):
            plan_from_bridge_fit(fit, [[1, 0], [0, 1]], [], 0)
        fit = self.fitted_result()
        fit["full_stage_audit"]["training_ids"].append("eval-a")
        with self.assertRaises(ValueError):
            plan_from_bridge_fit(fit, [[1, 0], [0, 1]], [], 0)
        fit = self.fitted_result()
        fit["frozen_jacobian"]["source_to_outcome"][0] = float("inf")
        with self.assertRaises(ValueError):
            plan_from_bridge_fit(fit, [[1, 0], [0, 1]], [], 0)
        fit = self.fitted_result()
        fit["full_stage_audit"]["state_training_ids"].append("eval-a")
        with self.assertRaises(ValueError):
            plan_from_bridge_fit(fit, [[1, 0], [0, 1]], [], 0)

    def test_supplied_receipt_respects_exclusive_fit_cutoff_and_exact_training_ids(self):
        fit = self.fitted_result(False)
        receipt = training_receipt()
        result = plan_from_bridge_fit(fit, [[1, 0], [0, 1]], [], 0, training_receipt=receipt)
        self.assertEqual(result["training"]["model_id"], receipt.model_id)
        self.assertEqual(result["cutoff_conversion"]["inclusive_outcome_cutoff"], 2024)
        self.assertIn("explicit", result["cutoff_conversion"]["rule"])
        wrong_ids = FrozenTrainingReceipt(("different-training",), 2024)
        with self.assertRaises(ValueError):
            plan_from_bridge_fit(fit, [[1, 0], [0, 1]], [], 0, training_receipt=wrong_ids)
        wrong_year = FrozenTrainingReceipt(("train-a", "train-b"), 2025)
        with self.assertRaises(ValueError):
            plan_from_bridge_fit(fit, [[1, 0], [0, 1]], [], 0, training_receipt=wrong_year)


if __name__ == "__main__":
    unittest.main()
