"""Numerical movement fixtures establish behavior, never NFL scouting lift."""

import importlib.util
import unittest
from dataclasses import replace
from unittest.mock import patch


NUMPY = importlib.util.find_spec("numpy") is not None
if NUMPY:
    import numpy as np
    from perfectjet.applications.nfl_scouting import predictive_state as ps


def oscillator_sequences(players=18, frames=45, noise=0.0, seed=441):
    """Exactly observable two-state AR(2), observed through one movement channel."""
    rng = np.random.default_rng(seed)
    sequences = []
    for i in range(players):
        values = np.zeros(frames)
        values[:2] = rng.normal(size=2)
        for t in range(2, frames):
            values[t] = 1.5 * values[t - 1] - 0.75 * values[t - 2]
        channels = (values + rng.normal(scale=noise, size=frames))[:, None]
        sequences.append(ps.MovementSequence(f"player-{i:02d}", f"attempt-{i}",
                                             np.arange(frames) * 0.1, channels))
    return sequences


@unittest.skipUnless(NUMPY, "Optional scouting NumPy dependency is unavailable")
class PredictiveStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sequences = oscillator_sequences()
        cls.fit = ps.discover_predictive_state(
            cls.sequences[:12], history_steps=(1, 2, 3), ranks=(1, 2, 3),
            horizon_steps=3, ridge_penalties=(0.0,), inner_folds=3,
            selection_tolerance=0.01, forecast_tolerance=1e-7,
            channel_names=("forward_velocity",), output_names=("forward_velocity",),
        )

    def test_known_observable_two_state_response_is_recovered(self):
        model = self.fit.model
        self.assertEqual(model.state_count, 2)
        self.assertEqual(model.history_steps, 2)
        self.assertTrue(self.fit.meets_declared_tolerance)
        self.assertLess(self.fit.selected_cv_mse, 1e-20)
        self.assertGreater(self.fit.instantaneous_cv_mse, 0.01)
        diagnostics = ps.continuation_diagnostics(model, self.sequences[12:])
        self.assertLess(diagnostics["standardized_mse"], 1e-20)
        self.assertEqual(diagnostics["independent_athletes"], 6)
        self.assertEqual(len(diagnostics["per_horizon_standardized_mse"]), 3)

    def test_same_current_value_different_history_gives_different_future(self):
        # AR(2) hidden direction: both current values are 1; previous values
        # differ, so the true next values are 1.5 and 0.0 respectively.
        model = self.fit.model
        a, b = np.array([[0.0], [1.0]]), np.array([[2.0], [1.0]])
        self.assertAlmostEqual(model.forecast(a)[0, 0], 1.5, places=10)
        self.assertAlmostEqual(model.forecast(b)[0, 0], 0.0, places=10)
        instantaneous = self.fit.instantaneous_model
        np.testing.assert_allclose(instantaneous.forecast(a[-1:]), instantaneous.forecast(b[-1:]), atol=0, rtol=0)

    def test_one_dimensional_multichannel_response_stays_small(self):
        sequences = []
        for i in range(12):
            z = (i - 5.5) * 0.85 ** np.arange(28)
            channels = np.column_stack((z, 2 * z, -0.5 * z))
            sequences.append(ps.MovementSequence(str(i), str(i), np.arange(len(z)) * 0.1, channels))
        fitted = ps.discover_predictive_state(sequences, history_steps=(1, 3), ranks=(1, 2, 3),
                                              horizon_steps=3, ridge_penalties=(0.0,))
        self.assertEqual(fitted.model.state_count, 1)
        self.assertEqual(fitted.model.history_steps, 1)
        self.assertLess(fitted.selected_cv_mse, 1e-20)

    def test_outer_athlete_values_cannot_change_scaling_or_selection(self):
        training = [s.athlete_id for s in self.sequences[:12]]
        kwargs = dict(train_athlete_ids=training, history_steps=(1, 2), ranks=(1, 2),
                      horizon_steps=3, ridge_penalties=(0.0, 0.01), seed=137)
        a = ps.discover_predictive_state(self.sequences, **kwargs)
        changed = [s if s.athlete_id in training else replace(s, channels=np.asarray(s.channels) * 1e9,
                                                            outputs=np.asarray(s.channels) - 1e7)
                   for s in self.sequences]
        b = ps.discover_predictive_state(changed, **kwargs)
        self.assertEqual(a.selection_scores, b.selection_scores)
        self.assertEqual(a.fold_groups, b.fold_groups)
        self.assertEqual(len(a.excluded_athlete_ids), 6)
        for name in ("input_mean", "input_scale", "output_mean", "output_scale", "state_map", "decoder",
                     "support_precision", "observed_past_basis"):
            np.testing.assert_allclose(getattr(a.model, name), getattr(b.model, name), atol=0, rtol=0)

    def test_inner_scalers_and_models_are_refitted_without_validation_players(self):
        calls = []
        real_fit = ps._fit
        real_score = ps._score
        def fit(*args, **kwargs):
            model = real_fit(*args, **kwargs)
            calls.append((set(model.training_group_ids), None))
            return model
        def score(model, arrays):
            held = {r[0].group for r in arrays}
            self.assertFalse(held & set(model.training_group_ids))
            calls[-1] = (calls[-1][0], held)
            return real_score(model, arrays)
        with patch.object(ps, "_fit", side_effect=fit), patch.object(ps, "_score", side_effect=score):
            fitted = ps.discover_predictive_state(self.sequences[:9], history_steps=(1, 2), ranks=(1, 2),
                                                  horizon_steps=2, ridge_penalties=(0.0,), inner_folds=3)
        inner = [pair for pair in calls if pair[1] is not None]
        self.assertEqual(len(inner), len(fitted.selection_scores) * 3)
        self.assertTrue(all(len(train | held) == 9 for train, held in inner))

    def test_bootstrap_copies_share_folds_and_outer_overlap_is_rejected(self):
        original = self.sequences[0]
        clone = replace(original, athlete_id="bootstrap-copy", original_athlete_id=original.athlete_id)
        sequences = self.sequences[:9] + [clone]
        fitted = ps.discover_predictive_state(sequences, history_steps=(1, 2), ranks=(1,),
                                              horizon_steps=2, ridge_penalties=(0.01,))
        self.assertEqual(len(fitted.fold_groups), 9)
        self.assertTrue(all(s["independent_athletes"] == 9 for s in fitted.selection_scores))
        self.assertTrue(all(s["sampled_athletes"] == 10 for s in fitted.selection_scores))
        # Isolation groups cannot cancel bootstrap multiplicity.  Every sampled
        # athlete gets equal total weight even when two share an original ID.
        means = [float(np.mean(s.channels)) for s in sequences]
        self.assertAlmostEqual(float(fitted.model.input_mean[0]), float(np.mean(means)), places=13)
        self.assertGreater(abs(float(fitted.model.input_mean[0]) -
                               float(np.mean(means[:-1]))), 1e-4)
        with self.assertRaisesRegex(ValueError, "Original-athlete leakage"):
            ps.discover_predictive_state(sequences, train_athlete_ids=[s.athlete_id for s in self.sequences[:9]])

    def test_noisy_continuations_have_empirical_tolerance_not_exact_guarantee(self):
        sequences = oscillator_sequences(players=24, frames=50, noise=0.015, seed=982)
        fitted = ps.discover_predictive_state(sequences[:18], history_steps=(1, 3, 5), ranks=(1, 2),
                                              horizon_steps=3, ridge_penalties=(1e-6, 0.01),
                                              forecast_tolerance=0.1)
        diagnostics = ps.continuation_diagnostics(fitted.model, sequences[18:])
        self.assertTrue(fitted.meets_declared_tolerance)
        self.assertLess(diagnostics["standardized_rmse"], 0.1)
        self.assertGreater(diagnostics["standardized_rmse"], 0.001)
        self.assertGreater(fitted.continuation_gain, 0.8)

    def test_missing_or_duplicate_frames_and_duplicate_attempts_are_rejected(self):
        sequence = self.sequences[0]
        times = np.asarray(sequence.times).copy()
        times[4] = times[3]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            ps.discover_predictive_state([replace(sequence, times=times)] + self.sequences[1:6])
        times = np.asarray(sequence.times).copy()
        times[10:] += 0.1
        with self.assertRaisesRegex(ValueError, "Gaps"):
            ps.discover_predictive_state([replace(sequence, times=times)] + self.sequences[1:6])
        with self.assertRaisesRegex(ValueError, "Duplicate athlete/attempt"):
            ps.discover_predictive_state(self.sequences[:6] + [sequence])

    def test_outputs_can_differ_from_channels_but_remain_movement_coordinates(self):
        records = [replace(s, outputs=np.column_stack((s.channels[:, 0], 3 * s.channels[:, 0])))
                   for s in self.sequences[:12]]
        fitted = ps.discover_predictive_state(records, history_steps=(1, 2), ranks=(1, 2),
                                              horizon_steps=3, ridge_penalties=(0.0,))
        prediction = fitted.model.forecast(records[0].channels[4:6])
        self.assertEqual(prediction.shape, (3, 2))
        np.testing.assert_allclose(prediction[:, 1], 3 * prediction[:, 0], atol=1e-10)

    def test_forecast_features_ignore_future_frames_and_outputs(self):
        sequence = self.sequences[-1]
        origin = 8
        a = ps.forecast_features(self.fit.model, sequence=sequence, origin_index=origin)
        channels = np.asarray(sequence.channels).copy()
        channels[origin + 1:] = np.nan
        changed = replace(sequence, channels=channels, outputs=np.full_like(channels, np.nan))
        b = ps.forecast_features(self.fit.model, sequence=changed, origin_index=origin)
        np.testing.assert_allclose(a, b, atol=0, rtol=0)
        self.assertEqual(a.shape, (3,))
        np.testing.assert_allclose(a, self.fit.model.forecast(sequence.channels[7:9]).reshape(-1))

    def test_cross_domain_history_has_explicit_descriptive_support_distance(self):
        history = self.sequences[-1].channels[4:6]
        ordinary = self.fit.model.support(history)
        unfamiliar = self.fit.model.support(history + 1e4)
        self.assertGreater(unfamiliar["mahalanobis_distance"], ordinary["mahalanobis_distance"] + 100)
        self.assertTrue(unfamiliar["outside_training_p95"])
        # A rank-one three-channel corpus exposes an unobserved direction.
        records = []
        for i in range(9):
            z = (i - 4) * 0.9 ** np.arange(20)
            records.append(ps.MovementSequence(str(i), str(i), np.arange(20) * 0.1,
                                                np.column_stack((z, 2 * z, z))))
        model = ps.discover_predictive_state(records, history_steps=(1,), ranks=(1,),
                                             horizon_steps=2, ridge_penalties=(0.0,)).model
        self.assertLess(model.support([[1.0, 2.0, 1.0]])["orthogonal_design_distance"], 1e-10)
        self.assertGreater(model.support([[1.0, -2.0, 1.0]])["orthogonal_design_distance"], 0.1)

    def test_instantaneous_defect_can_propose_history_without_adding_it(self):
        model = self.fit.instantaneous_model
        diagnostics = ps.continuation_diagnostics(model, self.sequences[12:], max_candidates=20)
        names = {item["history_function"] for item in diagnostics["defect_candidates"]}
        self.assertTrue(any(name.startswith("recent_difference:") for name in names))
        self.assertEqual(model.history_steps, 1)
        self.assertTrue(all("fresh player-held" in item["status"] for item in diagnostics["defect_candidates"]))

    def test_forecast_horizon_and_heldout_diagnostic_scope_are_enforced(self):
        model = self.fit.model
        with self.assertRaisesRegex(ValueError, "finite horizon"):
            model.forecast([[0.0], [1.0]], steps=4)
        with self.assertRaisesRegex(ValueError, "unseen original athletes"):
            ps.continuation_diagnostics(model, self.sequences[:2])
        with self.assertRaisesRegex(ValueError, "trailing shape"):
            model.transform([[0.0]])
        with self.assertRaisesRegex(ValueError, "common history"):
            ps.discover_predictive_state([replace(s, times=s.times[:5], channels=s.channels[:5])
                                         for s in self.sequences[:6]])


if __name__ == "__main__":
    unittest.main()
