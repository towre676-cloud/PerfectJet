import itertools
import random
import unittest
from fractions import Fraction as Q

from perfectjet.applications.nfl_scouting.allocation import (
    MeasurementCandidate, MeasurementBlockCandidate, TargetInformationModel, allocate_contenders,
    allocation_receipt, scouting_decision,
)
from perfectjet.readout import inverse, posterior_covariance


def independent_package_variance(prior, loading, selected):
    """Independent precision-matrix reference, not the sequential update implementation."""
    precision = inverse(prior)
    for candidate in selected:
        for i in range(len(prior)):
            for j in range(len(prior)):
                precision[i][j] += (candidate.repetitions * candidate.row[i]
                                    * candidate.row[j] / candidate.noise_variance)
    cov = inverse(precision)
    return sum((loading[i] * cov[i][j] * loading[j]
                for i in range(len(prior)) for j in range(len(prior))), Q(0))


class TargetInformationTests(unittest.TestCase):
    def test_zero_transfer_loading_has_no_scouting_value_despite_source_precision(self):
        model = TargetInformationModel([[1]], [0], training_receipt="training-fold-1")
        candidate = MeasurementCandidate("repeat", (1,), 1, 1, repetitions=2)
        receipt = model.package_information([candidate])
        self.assertEqual(receipt["source_variance_reduction"], Q(2, 3))
        self.assertEqual(receipt["target_variance_reduction"], 0)
        result = model.optimize_package([candidate], 1)
        self.assertEqual(result["candidate_ids"], ())
        self.assertEqual(result["tie_count"], 2)
        self.assertEqual(result["feasible_count"], 2)

    def test_repetitions_improve_precision_but_not_rank_or_identification(self):
        model = TargetInformationModel([[1, 0], [0, 1]], [1, 0], design=[[1, 0]])
        receipt = model.package_information([
            MeasurementCandidate("repeat", (1, 0), 1, 1, repetitions=2)])
        self.assertEqual(receipt["target_variance_before"], Q(1, 2))
        self.assertEqual(receipt["target_variance_after"], Q(1, 4))
        self.assertEqual(receipt["design_rank_before"], receipt["design_rank_after"])
        self.assertTrue(receipt["measurements"][0]["repeat_of_observed_row"])
        self.assertEqual(receipt["measurements"][0]["classification"], "precision_only")
        other = TargetInformationModel([[1, 0], [0, 1]], [0, 1], design=[[1, 0]])
        report = other.package_information([MeasurementCandidate("repeat", (1, 0), 1, 1)])
        self.assertFalse(report["readouts"][0]["after"]["identified"])
        self.assertIsNone(report["readouts"][0]["repair_from_this_package"]["needed"])

    def test_correlated_prior_and_heterogeneous_noise_match_independent_precision(self):
        prior = [[2, Q(1, 2)], [Q(1, 2), 3]]
        model = TargetInformationModel(prior, [1, -2], design=[[1, 1], [1, 0]],
                                       noise_variance=[Q(2, 3), Q(5, 4)])
        candidates = [MeasurementCandidate("a", (2, 1), Q(7, 3), 1),
                      MeasurementCandidate("b", (0, 1), Q(3, 5), 2, repetitions=2)]
        selected = [MeasurementCandidate("old1", (1, 1), Q(2, 3), 0),
                    MeasurementCandidate("old2", (1, 0), Q(5, 4), 0)] + candidates
        expected = independent_package_variance(prior, [1, -2], selected)
        report = model.package_information(candidates)
        self.assertEqual(report["target_variance_after"], expected)
        self.assertEqual(report["source_covariance_after"][0][1],
                         report["source_covariance_after"][1][0])

    def test_general_update_matches_existing_readout_core(self):
        prior = [[3, Q(4, 5)], [Q(4, 5), 2]]
        model = TargetInformationModel(prior, [1, 1])
        row = (Q(2, 3), -2)
        got = model.package_information([MeasurementCandidate("one", row, Q(5, 7), 1)])
        expected = tuple(tuple(r) for r in posterior_covariance([row], Q(5, 7), prior))
        self.assertEqual(got["source_covariance_after"], expected)

    def test_multiple_targets_and_weights_preserve_covariance(self):
        model = TargetInformationModel([[1, 0], [0, 1]], [[1, 0], [0, 2]],
                                       target_weights=[1, Q(1, 4)])
        report = model.package_information([MeasurementCandidate("second", (0, 1), 1, 1)])
        self.assertEqual(report["target_covariance_before"], ((Q(1), Q(0)), (Q(0), Q(4))))
        self.assertEqual(report["target_variance_before"], 2)
        self.assertEqual(report["target_variance_reduction"], Q(1, 2))

    def test_target_loadings_are_snapshotted_without_fitting_on_evaluation_data(self):
        source, target = [[1, 0], [0, 1]], [[1, 2]]
        model = TargetInformationModel(source, target, training_receipt="outer-fold-2")
        source[0][0] = 100
        target[0][0] = 100
        self.assertEqual(model.target_loadings, ((Q(1), Q(2)),))
        self.assertEqual(model.prior_covariance[0][0], 1)
        self.assertEqual(model.package_information([])["training_receipt"], "outer-fold-2")

    def test_nuisance_measurement_unlocks_a_complementary_package(self):
        receipt = allocation_receipt()
        self.assertEqual(receipt["isolated_reductions"]["nuisance"], 0)
        self.assertEqual(receipt["isolated_reductions"]["mixed"], Q(10, 21))
        self.assertEqual(receipt["optimal_joint_reduction"], Q(110, 131))
        self.assertGreater(receipt["optimal_joint_reduction"], sum(
            (receipt["isolated_reductions"][key] for key in ("mixed", "nuisance")), Q(0)))
        model = TargetInformationModel([[1, 0], [0, 1]], [1, 0])
        report = model.package_information([MeasurementCandidate("mixed", (1, 1), Q(1, 10), 1),
                                            MeasurementCandidate("nuisance", (0, 1), Q(1, 10), 1)])
        self.assertFalse(report["readouts"][0]["before"]["identified"])
        self.assertTrue(report["readouts"][0]["after"]["identified"])
        self.assertEqual(report["readouts"][0]["repair_from_this_package"]["needed"], 2)

    def test_independent_attempt_ids_reject_branches_disguised_as_repeats(self):
        with self.assertRaises(ValueError):
            MeasurementCandidate("branch", (1,), 1, 1, repetitions=2,
                                 attempt_ids=("attempt-a", "attempt-a"))
        model = TargetInformationModel([[1]], [1], design=[[1]], observation_ids=["existing"])
        with self.assertRaises(ValueError):
            model.package_information([MeasurementCandidate("copy", (1,), 1, 1,
                                                              attempt_ids=("existing",))])
        with self.assertRaises(ValueError):
            model.optimize_package([MeasurementCandidate("a", (1,), 1, 1, attempt_ids=("new",)),
                                    MeasurementCandidate("b", (1,), 1, 1, attempt_ids=("new",))], 2)
        report = model.package_information([MeasurementCandidate("valid", (1,), 1, 1,
                                                                  repetitions=2,
                                                                  attempt_ids=("new1", "new2"))])
        self.assertIn("original attempt", report["measurements"][0]["independence_provenance"])

    def test_invalid_gaussian_models_and_candidates_are_rejected(self):
        for prior in ([[1, 2], [0, 1]], [[1, 2], [2, 1]], [[1, 1], [1, 1]], []):
            with self.assertRaises(ValueError):
                TargetInformationModel(prior, [1, 0])
        for noise in (0, -1):
            with self.assertRaises(ValueError):
                MeasurementCandidate("x", (1,), noise, 1)
        for cost in (-1, Q(1, 2), True):
            with self.assertRaises(ValueError):
                MeasurementCandidate("x", (1,), 1, cost)
        with self.assertRaises(ValueError):
            TargetInformationModel([[1]], [1], target_weights=[-1])
        with self.assertRaises(ValueError):
            TargetInformationModel([[1]], [1], design=[[1]], noise_variance=[])


class FiniteAllocationTests(unittest.TestCase):
    def test_greedy_is_strictly_worse_than_global_package(self):
        receipt = allocation_receipt()
        self.assertEqual(receipt["greedy_joint_reduction"], Q(21, 32))
        self.assertEqual(receipt["optimal_selected"], ("mixed", "nuisance"))
        self.assertGreater(receipt["optimal_joint_reduction"], receipt["greedy_joint_reduction"])
        self.assertEqual(receipt["feasible_packages"], 7)

    def test_optimizer_matches_independent_bruteforce_and_population_rank(self):
        rng = random.Random(921)
        for trial in range(12):
            prior = [[2, Q(1, 2)], [Q(1, 2), 1]]
            loading = [rng.randrange(-2, 3), rng.randrange(-2, 3)]
            model = TargetInformationModel(prior, loading)
            candidates = [MeasurementCandidate(str(k), (rng.randrange(-2, 3), rng.randrange(-2, 3)),
                                               Q(rng.randrange(1, 5), rng.randrange(1, 4)),
                                               rng.randrange(0, 3), repetitions=rng.randrange(1, 3))
                          for k in range(5)]
            budget = 3
            feasible = []
            for bits in itertools.product((0, 1), repeat=len(candidates)):
                selected = [candidate for bit, candidate in zip(bits, candidates) if bit]
                if sum(candidate.cost for candidate in selected) <= budget:
                    variance = independent_package_variance(prior, loading, selected)
                    feasible.append((bits, model.target_variance - variance))
            maximum = max(value for _, value in feasible)
            result = model.optimize_package(candidates, budget)
            self.assertEqual(result["objective_reduction"], maximum)
            self.assertEqual(result["feasible_count"], len(feasible))
            self.assertEqual(result["evaluated_packages"], len(feasible))
            self.assertEqual(result["tie_count"], sum(value == maximum for _, value in feasible))
            self.assertEqual(result["tie_ranks"], tuple(i for i, (_, value) in enumerate(feasible)
                                                       if value == maximum))
            self.assertEqual(feasible[result["population_rank"]][0], result["bits"])

    def test_empty_budget_zero_costs_and_objective_ties(self):
        model = TargetInformationModel([[1]], [1])
        result = model.optimize_package([], 0)
        self.assertEqual(result["feasible_count"], 1)
        self.assertEqual(result["tie_count"], 1)
        result = model.optimize_package([MeasurementCandidate("free", (1,), 1, 0),
                                         MeasurementCandidate("unaffordable", (1,), 1, 1)], 0)
        self.assertEqual(result["candidate_ids"], ("free",))
        self.assertEqual(result["feasible_count"], 2)
        zero = TargetInformationModel([[1]], [0])
        tied = zero.optimize_package([MeasurementCandidate("costly", (1,), 1, 1),
                                      MeasurementCandidate("free", (1,), 1, 0)], 1)
        self.assertEqual(tied["tie_count"], 4)
        self.assertEqual(tied["cost"], 0)
        self.assertEqual(tied["bits"], (0, 0))

    def test_candidate_limit_is_explicit_and_duplicates_rejected(self):
        model = TargetInformationModel([[1]], [1])
        with self.assertRaises(ValueError):
            model.optimize_package([MeasurementCandidate(str(k), (1,), 1, 1) for k in range(19)], 3)
        with self.assertRaises(ValueError):
            model.optimize_package([], 3, max_candidates=100)
        with self.assertRaises(ValueError):
            model.optimize_package([MeasurementCandidate("same", (1,), 1, 1),
                                     MeasurementCandidate("same", (1,), 1, 1)], 1)


class ScoutingDecisionTests(unittest.TestCase):
    def test_strict_scenario_margin_and_touching_intervals(self):
        settled = scouting_decision({"a": (3, 4), "b": (1, 2)})
        self.assertTrue(settled["settled"])
        self.assertEqual(settled["choice"], "a")
        self.assertEqual(settled["margin"], 1)
        tied = scouting_decision({"a": (2, 3), "b": (1, 2)})
        self.assertFalse(tied["settled"])
        self.assertEqual(tied["unresolved_comparisons"][0]["difference_bounds"], (0, 2))
        low = scouting_decision({"a": (3, 4), "b": (1, 2)}, maximize=False)
        self.assertEqual(low["choice"], "b")

    def test_empirical_uncertainty_is_kept_separate(self):
        result = scouting_decision({"a": (3, 4), "b": (1, 2)},
                                    empirical_uncertainty={"a": (-100, 100), "b": (-100, 100)})
        self.assertTrue(result["settled"])
        self.assertEqual(result["empirical_uncertainty"]["a"], (-100, 100))
        self.assertIsNone(result["statistical_confidence_claim"])
        self.assertIn("fixed-fit", result["guarantee_scope"])

    def test_contender_allocation_targets_differences_without_unsafe_candidate_pruning(self):
        model = TargetInformationModel([[1, Q(1, 2), 0], [Q(1, 2), 1, 0], [0, 0, 1]],
                                       [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                                       target_ids=("a", "b", "c"), training_receipt="training-only")
        candidates = [MeasurementCandidate("a-test", (1, 0, 0), 1, 1, athlete_id="a"),
                      MeasurementCandidate("b-test", (0, 1, 0), 1, 1, athlete_id="b"),
                      MeasurementCandidate("c-test", (0, 0, 1), Q(1, 100), 1, athlete_id="c"),
                      MeasurementCandidate("unknown", (1, 0, 0), 1, 1)]
        result = allocate_contenders(model, candidates, 1,
                                     {"a": (2, 4), "b": (3, 5), "c": (-5, -4)})
        self.assertEqual(set(result["comparison_pairs"][0]), {"a", "b"})
        self.assertEqual(result["allocation"]["feasible_count"], 5)
        self.assertEqual(result["allocation"]["objective_reduction"], Q(1, 8))
        self.assertEqual(result["excluded_candidates"], ())
        settled = allocate_contenders(model, candidates, 1,
                                      {"a": (10, 11), "b": (3, 5), "c": (-5, -4)})
        self.assertEqual(settled["allocation"]["candidate_ids"], ())
        self.assertEqual(settled["allocation"]["feasible_count"], 1)

    def test_outside_athlete_can_be_optimal_through_source_cross_covariance(self):
        model = TargetInformationModel([[1, 0, Q(1, 2)], [0, 1, 0], [Q(1, 2), 0, 1]],
                                       [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                                       target_ids=("a", "b", "outside"))
        candidates = [MeasurementCandidate("a", (1, 0, 0), 10, 1, athlete_id="a"),
                      MeasurementCandidate("b", (0, 1, 0), 10, 1, athlete_id="b"),
                      MeasurementCandidate("outside", (0, 0, 1), 1, 1, athlete_id="outside")]
        result = allocate_contenders(model, candidates, 1, {"a": (0, 2), "b": (1, 3)})
        self.assertEqual(result["allocation"]["candidate_ids"], ("outside",))
        self.assertEqual(result["allocation"]["objective_reduction"], Q(1, 8))
        self.assertEqual(result["allocation"]["feasible_count"], 4)

    def test_zero_isolated_value_outsider_unlocks_a_joint_contender_package(self):
        model = TargetInformationModel([[1, 0], [0, 1]], [[1, 0], [0, 0], [0, 1]],
                                       target_ids=("a", "b", "outside"))
        candidates = [MeasurementCandidate("direct", (1, 0), 1, 1, athlete_id="a"),
                      MeasurementCandidate("mixed", (1, 1), Q(1, 10), 1, athlete_id="a"),
                      MeasurementCandidate("nuisance", (0, 1), Q(1, 10), 1, athlete_id="outside")]
        result = allocate_contenders(model, candidates, 2, {"a": (0, 2), "b": (1, 3)})
        self.assertEqual(result["allocation"]["candidate_ids"], ("mixed", "nuisance"))
        self.assertEqual(result["allocation"]["objective_reduction"], Q(110, 131))

    def test_target_ids_are_required_and_invalid_bounds_rejected(self):
        model = TargetInformationModel([[1]], [1])
        with self.assertRaises(ValueError):
            allocate_contenders(model, [], 1, {"a": (0, 1)})
        for bounds in ({}, {"a": (2, 1)}, {"a": (1, 2, 3)}):
            with self.assertRaises(ValueError):
                scouting_decision(bounds)
        with self.assertRaises(ValueError):
            scouting_decision({"a": (1, 2)}, {"unknown": (0, 1)})


class BlockMeasurementAndRobustAllocationTests(unittest.TestCase):
    def test_joint_channels_preserve_correlated_attempt_noise(self):
        model = TargetInformationModel([[1, 0], [0, 1]], [1, 1])
        block = MeasurementBlockCandidate("one-attempt", ((1, 0), (0, 1)),
                                           ((1, Q(1, 2)), (Q(1, 2), 1)), 2,
                                           attempt_ids=("original-attempt",))
        result = model.package_information([block])
        self.assertEqual(result["source_covariance_after"],
                         ((Q(7, 15), Q(2, 15)), (Q(2, 15), Q(7, 15))))
        self.assertEqual(result["target_variance_reduction"], Q(4, 5))
        independent = model.package_information([MeasurementCandidate("x", (1, 0), 1, 1),
                                                 MeasurementCandidate("y", (0, 1), 1, 1)])
        self.assertEqual(independent["target_variance_reduction"], 1)
        self.assertLess(result["target_variance_reduction"], independent["target_variance_reduction"])
        self.assertEqual(result["readouts"][0]["repair_from_this_package"]["needed"], 1)
        self.assertEqual(result["readouts"][0]["row_repair"]["needed"], 2)
        self.assertEqual(result["measurements"][0]["channels"], 2)
        allocated = model.optimize_package([block], 2)
        self.assertEqual(allocated["feasible_count"], 2)
        self.assertEqual(allocated["candidate_ids"], ("one-attempt",))
        self.assertEqual(model.optimize_package([block], 1)["candidate_ids"], ())

    def test_block_matches_independent_precision_reference(self):
        prior = [[3, Q(1, 3)], [Q(1, 3), 2]]
        rows = ((1, 2), (2, -1))
        noise = ((2, Q(1, 4)), (Q(1, 4), 1))
        model = TargetInformationModel(prior, [[1, 0], [0, 1]])
        block = MeasurementBlockCandidate("block", rows, noise, 1, repetitions=2,
                                           attempt_ids=("attempt-1", "attempt-2"))
        precision = inverse(prior)
        noise_inverse = inverse(noise)
        for i in range(2):
            for j in range(2):
                precision[i][j] += sum((2 * rows[a][i] * noise_inverse[a][b] * rows[b][j]
                                        for a in range(2) for b in range(2)), Q(0))
        expected = tuple(tuple(row) for row in inverse(precision))
        result = model.package_information([block])
        self.assertEqual(result["source_covariance_after"], expected)
        self.assertEqual(result["design_rank_after"], 2)
        self.assertEqual(result["measurements"][0]["repetitions"], 2)

    def test_block_noise_and_attempt_provenance_validation(self):
        for noise in (((1, 1), (1, 1)), ((1, 2), (0, 1)), ((1,),)):
            with self.assertRaises(ValueError):
                MeasurementBlockCandidate("bad", ((1, 0), (0, 1)), noise, 1)
        block = MeasurementBlockCandidate("block", ((1, 0), (0, 1)), ((1, 0), (0, 1)), 1,
                                           attempt_ids=("same-original-attempt",))
        scalar = MeasurementCandidate("branch", (1, 0), 1, 1,
                                       attempt_ids=("same-original-attempt",))
        with self.assertRaises(ValueError):
            TargetInformationModel([[1, 0], [0, 1]], [1, 1]).optimize_package([block, scalar], 2)

    def test_worst_target_protects_all_declared_loading_scenarios(self):
        model = TargetInformationModel([[1, 0], [0, 1]], [[1, 0], [0, 1]],
                                       training_receipt="two declared training-refit loadings")
        candidates = [MeasurementCandidate("one-direction", (1, 0), Q(1, 10), 1),
                      MeasurementCandidate("balanced", (1, 1), 1, 1)]
        mean = model.optimize_package(candidates, 1)
        robust = model.optimize_package(candidates, 1, objective="worst_target")
        self.assertEqual(mean["candidate_ids"], ("one-direction",))
        self.assertEqual(mean["objective_reduction"], Q(5, 11))
        self.assertEqual(robust["candidate_ids"], ("balanced",))
        self.assertEqual(robust["objective_reduction"], Q(1, 3))
        self.assertIn("not a confidence region", robust["objective_scope"])

    def test_zero_loading_scenario_prevents_a_positive_robust_claim(self):
        model = TargetInformationModel([[1]], [[1], [0]])
        candidates = [MeasurementCandidate("source", (1,), Q(1, 10), 1)]
        result = model.optimize_package(candidates, 1, objective="worst_target")
        self.assertEqual(result["objective_reduction"], 0)
        self.assertEqual(result["candidate_ids"], ())
        self.assertEqual(result["tie_count"], 2)
        self.assertGreater(model.optimize_package(candidates, 1)["objective_reduction"], 0)
        with self.assertRaises(ValueError):
            model.optimize_package(candidates, 1, objective="invented")


if __name__ == "__main__":
    unittest.main()
