import math
import random
import unittest
from dataclasses import replace

from perfectjet.applications.nfl_scouting.burst import (
    BurstObservation, BurstProtocol, FORTY, IntegratedScoutCorrection,
    ScalarReliabilityModel, SourcePosterior, burst_functional, extract_burst, integrated_nll,
)
from perfectjet.applications.nfl_scouting.schema import Attempt, Frame, Lineage


def accelerating_attempt(acceleration=4.0, angle=0.0, offset=(0.0, 0.0), irregular=False):
    times = [(i - 1) * 0.1 for i in range(20)]
    if irregular:
        times = [t + (0.01 if i % 2 else 0.0) for i, t in enumerate(times)]
    frames = []
    for t in times:
        x = 0.5 * acceleration * t * t if acceleration else t
        frames.append(Frame(t, offset[0] + math.cos(angle) * x,
                            offset[1] + math.sin(angle) * x))
    return Attempt("A", "attempt", FORTY, frames, "2024-03-01")


def observation(athlete, attempt, value, drill=FORTY, branches=None):
    lineage = Lineage(athlete, attempt, drill, (0, 10), (0.0, 1.0), "yards/s^2", "test", "2024-03-01")
    return BurstObservation(athlete, attempt, drill, value,
                            branches or {"raw": value}, 0.2, 0.7, 1.0, 0.0, lineage)


class BurstMeasurementTests(unittest.TestCase):
    def test_constant_acceleration_is_exact_without_forward_difference_bias(self):
        b = extract_burst(accelerating_attempt())
        self.assertIsNotNone(b)
        self.assertAlmostEqual(b.value, 4.0, places=9)
        self.assertTrue(all(abs(v - 4.0) < 1e-8 for v in b.branches.values()))
        self.assertAlmostEqual(b.initial_speed, 4.0 * b.onset_time, places=9)

    def test_rotation_translation_and_irregular_quadratic_sampling(self):
        b = extract_burst(accelerating_attempt(angle=1.37, offset=(123.0, -51.0), irregular=True))
        self.assertIsNotNone(b)
        self.assertAlmostEqual(b.value, 4.0, places=8)
        self.assertLess(b.sensitivity, 1e-7)

    def test_constant_velocity_has_zero_burst(self):
        a = accelerating_attempt(acceleration=0.0)
        path = [(f.t, f.x, f.y) for f in a.frames]
        self.assertAlmostEqual(burst_functional(path, 3), 0.0, places=10)
        self.assertIsNone(extract_burst(a))  # already moving, no observed launch

    def test_no_history_gap_or_nonforty_is_not_silently_repaired(self):
        a = accelerating_attempt()
        self.assertIsNone(extract_burst(replace(a, drill="PASS_RUSH_DRILL")))
        self.assertIsNone(extract_burst(replace(a, frames=a.frames[:6])))
        broken = list(a.frames)
        broken[4] = replace(broken[4], t=broken[3].t)
        self.assertIsNone(extract_burst(replace(a, frames=broken)))
        sparse = [f for i, f in enumerate(a.frames) if i not in (4, 5)]
        self.assertIsNone(extract_burst(replace(a, frames=sparse)))

    def test_turning_first_start_is_rejected(self):
        a = accelerating_attempt()
        frames = [replace(f, y=3 * max(0.0, f.t - 0.25) ** 2) for f in a.frames]
        self.assertIsNone(extract_burst(replace(a, frames=frames)))

    def test_sensitivity_width_and_lineage_do_not_claim_sensor_probability(self):
        a = accelerating_attempt()
        rng = random.Random(41)
        frames = [replace(f, x=f.x + rng.gauss(0, 0.005)) for f in a.frames]
        b = extract_burst(replace(a, frames=frames))
        self.assertIsNotNone(b)
        self.assertGreater(b.sensitivity, 0.0)
        self.assertEqual(b.lineage.available_on, "2024-03-01")
        self.assertFalse(b.lineage.branch["branch_width_is_probability_interval"])


class ReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.obs = [observation(str(i), f"{i}-{j}", i + (-0.2 if j == 0 else 0.2))
                    for i in range(6) for j in range(2)]

    def test_empirical_repeat_variance_and_posterior_formula(self):
        model = ScalarReliabilityModel.fit(self.obs)
        self.assertTrue(model.calibrated)
        self.assertAlmostEqual(model.within_variance[FORTY], 0.08)
        p = model.posterior(self.obs, "5")
        expected = 1.0 / (1.0 / model.prior_variance + 2.0 / 0.08)
        self.assertAlmostEqual(p.variance, expected)
        self.assertAlmostEqual(p.mean, expected * 2.0 * (5.0 - 2.5) / 0.08)
        self.assertEqual(p.repeat_count, 1)

    def test_more_actual_attempts_increase_information_not_branch_count(self):
        model = ScalarReliabilityModel.fit(self.obs)
        one = model.posterior([self.obs[-1]])
        two = model.posterior(self.obs[-2:])
        self.assertLess(two.variance, one.variance)
        many_branches = replace(self.obs[-1], branches={str(i): float(i) for i in range(50)})
        self.assertEqual(model.posterior([many_branches]), one)
        with self.assertRaisesRegex(ValueError, "Duplicate attempt"):
            model.posterior([self.obs[-1], many_branches])

    def test_missing_repeat_evidence_is_unavailable_not_perfect_reliability(self):
        singles = self.obs[::2]
        model = ScalarReliabilityModel.fit(singles)
        self.assertFalse(model.calibrated)
        p = model.posterior(singles, "0")
        self.assertFalse(p.available)
        self.assertEqual(p.information_fraction, 0.0)
        self.assertEqual(p.prior_reliance, 1.0)

    def test_training_filter_prevents_heldout_source_values_changing_calibration(self):
        model = ScalarReliabilityModel.fit(self.obs, train_ids={"0", "1", "2"})
        changed = [replace(o, value=10000.0) if o.athlete_id == "5" else o for o in self.obs]
        other = ScalarReliabilityModel.fit(changed, train_ids={"0", "1", "2"})
        self.assertEqual(model, other)
        missing = model.posterior([], athlete_id="new")
        self.assertFalse(missing.available)
        self.assertEqual(missing.variance, model.prior_variance)


class IntegratedLikelihoodTests(unittest.TestCase):
    def test_integrated_likelihood_includes_source_and_outcome_variance(self):
        p = SourcePosterior(2.0, 0.3, 0.7, 2, 1, True)
        total = 0.4 + 0.2 + 1.5 ** 2 * 0.3
        expected = 0.5 * (math.log(total) + (4.0 - 1.5 * 2.0) ** 2 / total)
        self.assertAlmostEqual(integrated_nll(1.5, 0.4, [p], [4.0], [0.2]), expected)

    def test_fitted_loading_recovers_analytic_noiseless_mean_relation(self):
        rng = random.Random(4)
        ps = [SourcePosterior((i - 15) / 10, 0.0, 1.0, 2, 1, True) for i in range(31)]
        outcomes = [1.7 * p.mean + rng.gauss(0, 0.03) for p in ps]
        model = IntegratedScoutCorrection.fit(ps, outcomes, penalty=0.01)
        self.assertAlmostEqual(model.loading, 1.7, delta=0.03)
        self.assertLess(model.training_nll, model.baseline_nll)
        self.assertAlmostEqual(model.predict(ps[0]), model.loading * ps[0].mean)

    def test_unobserved_traits_cannot_generate_an_athlete_specific_correction(self):
        ps = [SourcePosterior(0.0, 1.0, 0.0, 0, 0, False) for _ in range(5)]
        model = IntegratedScoutCorrection.fit(ps, [-1.0, 0.5, 0.0, 1.0, -0.5])
        self.assertEqual(model.loading, 0.0)
        self.assertEqual(model.predict_many(ps), [0.0] * 5)

    def test_likelihood_rejects_misaligned_or_negative_uncertainty(self):
        p = SourcePosterior(1.0, 0.5, 0.5, 1, 0, True)
        with self.assertRaises(ValueError):
            integrated_nll(1, 1, [p], [1, 2])
        with self.assertRaises(ValueError):
            integrated_nll(1, 1, [p], [1], [-0.1])


if __name__ == "__main__":
    unittest.main()
