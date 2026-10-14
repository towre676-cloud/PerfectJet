"""Artificial cross-domain fixtures; these tests are not NFL performance data."""
import copy
import importlib.util
from dataclasses import replace
import unittest
from unittest.mock import patch

SCIENTIFIC = all(importlib.util.find_spec(name) for name in ("numpy", "pandas", "sklearn"))
if SCIENTIFIC:
    import numpy as np
    from perfectjet.applications.nfl_scouting import bridges
    from perfectjet.applications.nfl_scouting.movement_targets import MovementTargetRecord
    from perfectjet.applications.nfl_scouting.official import MEASUREMENT_COLUMNS
    from perfectjet.applications.nfl_scouting.schema import Athlete, Attempt, Dataset, Frame, Play


def fixture():
    rng = np.random.default_rng(991)
    athletes, attempts, plays, records = {}, [], [], []
    for i in range(18):
        aid = str(1000+i)
        year = 2023 if i < 12 else 2024
        trait = (i%12-5.5)/4
        measurements = {name: float(10+j+((i*(j+3))%7)/8)
                        for j, name in enumerate(MEASUREMENT_COLUMNS.values())}
        athletes[aid] = Athlete(aid, "DE", year, measurements,
                                {name: f"{year}-03-01" for name in measurements})
        for repeat in range(2):
            acceleration = 3.5+trait+repeat*0.1
            frames = []
            for k in range(36):
                t = k/10
                dt = max(t-0.7, 0)
                frames.append(Frame(t, acceleration*dt*dt/2,
                                    0.03*dt*dt))
            attempts.append(Attempt(aid, f"{aid}-forty-{repeat}", "FORTY_YARD_DASH",
                                    frames, f"{year}-03-01"))
        for p in range(6):
            gid = f"{year}{p//3+1}"
            pid = f"{gid}:{p+1}"
            depth = 0.3+0.1*(p%3)
            context = {"snap_depth": depth, "snap_speed": 0.05, "snap_width": float(p%2),
                       "down": float(p%3+1), "yards_to_go": float(p+2),
                       "lined_up_position": "DE", "offense_formation": "SHOTGUN"}
            q = [0.65+0.15*trait+0.07*depth+float(rng.normal(0,0.01)),
                 0.8-0.12*trait+0.08*depth+float(rng.normal(0,0.01))]
            outcome = 1.1-0.09*trait+0.15*depth+float(rng.normal(0,0.015))
            play = Play(aid, year, pid, outcome, context)
            plays.append(play)
            # A damped launch gives history dependence and a finite NFL horizon.
            frames = [Frame(k/10, (1.2+0.25*trait)*(max(k/10-0.2,0)-
                                (1-np.exp(-2*max(k/10-0.2,0)))/2),
                            0.02*np.sin(max(k/10,0))) for k in range(-5,26)]
            records.append(MovementTargetRecord(aid, year, pid, gid, outcome, dict(context),
                channels={"forward_displacement_05": q[0], "motion_to_los": q[1], "onset_delay": 0.2},
                frames=frames, usable=True, usable_for_post_snap_onset=True))
    ds = Dataset(athletes, attempts, plays, {"fixture": "artificial-test-only"},
                 {"minimum_plays": 3}, synthetic=True)
    config = bridges.BridgeConfig(state_history_steps=(1,3), state_ranks=(1,),
        state_penalties=(0.1,), state_horizon_steps=2, state_inner_folds=2,
        maximum_nfl_sequences_per_athlete=2, minimum_training_athletes=4,
        minimum_movement_plays=2, minimum_movement_athletes=2,
        stack_folds=2, decoder_penalties=(100.0,), outer_inner_folds=2)
    tr = sorted(a for a,v in athletes.items() if v.draft_year == 2023)
    te = sorted(a for a,v in athletes.items() if v.draft_year == 2024)
    return ds, records, tr, te, config


@unittest.skipUnless(SCIENTIFIC, "optional scouting scientific dependencies unavailable")
class BridgeIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds, cls.records, cls.tr, cls.te, cls.config = fixture()
        cls.reference = bridges.fit_split(cls.ds, cls.records, cls.tr, cls.te,
                                          2024, 100, seed=71, config=cls.config)

    def test_entire_heldout_nfl_state_and_labels_cannot_change_predictions(self):
        ds = copy.deepcopy(self.ds)
        held = set(self.te)
        ds.plays = [replace(p, outcome=p.outcome+50, context={**p.context, "snap_depth": 999})
                    if p.athlete_id in held else p for p in ds.plays]
        records = copy.deepcopy(self.records)
        for record in records:
            if record.athlete_id in held:
                record.channels = {name: value+100 for name,value in record.channels.items()}
                record.frames = [Frame(f.t, f.x*1000, f.y-100) for f in record.frames]
                record.context["snap_depth"] = 999
        result = bridges.fit_split(ds, records, self.tr, self.te, 2024, 100, seed=71, config=self.config)
        for key in ("baseline", "movement", "conventional_bridge", "movement_predictions", "loading"):
            np.testing.assert_allclose(result[key], self.reference[key], rtol=0, atol=1e-12)
        self.assertNotEqual(result["y"], self.reference["y"])
        self.assertNotEqual(result["movement_truth"], self.reference["movement_truth"])
        self.assertEqual(result["full_stage_audit"], self.reference["full_stage_audit"])

    def test_source_features_ignore_future_after_first_halfsecond(self):
        attempt = self.ds.attempts[0]
        prefix = bridges.source_prefix(attempt)
        self.assertIsNotNone(prefix)
        changed = replace(attempt, frames=[Frame(f.t, 9999, float("nan"))
                           if f.t > prefix["endpoint_time"]+1e-8 else f for f in attempt.frames])
        other = bridges.source_prefix(changed)
        np.testing.assert_array_equal(prefix["history"], other["history"])
        for key in ("displacement_05", "terminal_forward_speed", "endpoint_retention"):
            self.assertEqual(prefix[key], other[key])
        shortened = replace(attempt, frames=[f for f in attempt.frames
                                             if f.t <= prefix["endpoint_time"]+1e-8])
        np.testing.assert_array_equal(prefix["history"], bridges.source_prefix(shortened)["history"])

    def test_earliest_valid_prefix_needs_no_unused_extra_frames(self):
        attempt = Attempt("1000", "early", "FORTY_YARD_DASH",
            [Frame(i/10, max(i/10-0.1,0), 0) for i in range(7)], "2023-03-01")
        prefix = bridges.source_prefix(attempt)
        self.assertIsNotNone(prefix)
        self.assertAlmostEqual(prefix["endpoint_time"],0.6)

    def test_each_decoder_training_prediction_excludes_its_original_player(self):
        covered = set()
        for audit in self.reference["stacking_audit"]:
            held = set(audit["evaluated_ids"])
            train = set(audit["training_ids"])
            self.assertFalse(held & train)
            self.assertFalse(held & set(audit["state_training_ids"]))
            self.assertFalse(held & set(audit["movement_training_ids"]))
            self.assertFalse(audit["state_selection_uses_football_outcomes"])
            covered |= held
        self.assertEqual(covered, set(self.tr))
        self.assertFalse(set(self.te) & set(self.reference["full_stage_audit"]["state_training_ids"]))

    def test_primary_target_and_decomposition_have_exact_fixedfit_identity(self):
        self.assertEqual(self.reference["movement_channels"],
                         ["forward_displacement_05", "motion_to_los"])
        for y,p,receipt in zip(self.reference["y"],self.reference["movement"],
                               self.reference["error_decomposition"]):
            self.assertAlmostEqual(p-y, receipt["decoder_residual"]+receipt["transferred_movement_error"], 12)
            self.assertLess(receipt["identity_error"], 1e-12)
            self.assertIn("never a deployable", receipt["scope"])

    def test_frozen_jacobian_composes_and_all_baselines_share_coverage(self):
        jacobian = self.reference["frozen_jacobian"]
        expected = np.asarray(jacobian["movement_to_outcome"]) @ np.asarray(jacobian["source_to_movement"])
        np.testing.assert_allclose(expected, jacobian["source_to_outcome"], rtol=0, atol=1e-12)
        columns = self.reference["shared_baseline_columns"]
        self.assertTrue(set(MEASUREMENT_COLUMNS.values()).issubset(columns))
        self.assertIn("source_prefix_count", columns)
        self.assertIn("source_history_outside_training_support", columns)
        self.assertFalse(any(name.startswith("q__") or name.startswith("forecast__") for name in columns))
        self.assertTrue(all(self.reference["source_coverage"][a]["source_prefix_count"] == 2 for a in self.te))

    def test_bootstrap_original_group_overlap_is_rejected(self):
        ds = copy.deepcopy(self.ds)
        original = self.tr[0]
        clone = original+"#copy"
        ds.athletes[clone] = replace(ds.athletes[original], athlete_id=clone, bootstrap_group=original)
        with self.assertRaisesRegex(ValueError, "original-athlete leakage"):
            bridges.fit_split(ds, self.records, self.tr, [clone], 2024, config=self.config)

    def test_actual_fitted_loading_feeds_exact_measurement_planner(self):
        from perfectjet.applications.nfl_scouting.allocation import MeasurementCandidate
        from perfectjet.applications.nfl_scouting.bridge_allocation import plan_from_bridge_fit
        names = self.reference["frozen_jacobian"]["source_features"]
        width = len(names)
        prior = [[int(i == j) for j in range(width)] for i in range(width)]
        candidates = [MeasurementCandidate(f"synthetic-measure-{j}",
                      tuple(int(i == j) for i in range(width)), 1, 1,
                      attempt_ids=(f"new-independent-attempt-{j}",)) for j in range(3)]
        plan = plan_from_bridge_fit(self.reference, prior, candidates, budget=2)
        self.assertEqual(tuple(names), plan["source_feature_order"])
        self.assertTrue(plan["jacobian_composition_audit"]["passed"])
        self.assertFalse(plan["jacobian_composition_audit"]["loading_override_allowed"])
        self.assertEqual(plan["training"]["outcome_cutoff"], 2023)
        self.assertEqual(set(plan["training"]["training_athlete_ids"]), set(self.tr))
        self.assertIn("synthetic", plan["evidence_scope"])

    def test_future_training_records_cannot_enter_state_or_target(self):
        ds = copy.deepcopy(self.ds)
        aid = self.tr[0]
        ds.plays.append(Play(aid, 2026, "future:1", 1e9, {"snap_depth": 1e9}))
        future = replace(self.records[0], season=2026, play_id="future:1",
                          channels={"forward_displacement_05": 1e9, "motion_to_los": 1e9})
        result = bridges.fit_split(ds, self.records+[future], self.tr, self.te,
                                    2024, 100, seed=71, config=self.config)
        np.testing.assert_array_equal(result["movement"], self.reference["movement"])
        self.assertEqual(result["full_stage_audit"]["nfl_sequences"],
                         len(self.tr)*self.config.maximum_nfl_sequences_per_athlete)
        with self.assertRaisesRegex(ValueError, "temporal cutoff"):
            bridges.fit_split(self.ds, self.records, self.tr+[self.te[0]], self.te[1:],
                                2024, config=self.config)

    def test_synthetic_fixture_cannot_be_presented_as_official_experiment(self):
        with self.assertRaisesRegex(ValueError, "official real inputs"):
            bridges.experiment(self.ds, self.records, config=self.config)

    def test_nested_selection_rebuilds_whole_player_stages_without_test_data(self):
        calls = []
        real = bridges.fit_split
        def observed(ds, records, tr, te, *args, **kwargs):
            calls.append((set(tr),set(te)))
            return real(ds, records, tr, te, *args, **kwargs)
        with patch.object(bridges, "fit_split", side_effect=observed):
            result = bridges._nested_fold(self.ds, self.records, self.tr, self.te,
                                           2024, True, 71, self.config)
        self.assertEqual(len(calls), 3)
        for train, held in calls[:-1]:
            self.assertFalse(train & held)
            self.assertFalse(held & set(self.te))
            self.assertEqual(train | held, set(self.tr))
        self.assertEqual(result["chosen_penalties"],
                         {"baseline":100.0,"movement":100.0,"conventional_bridge":100.0})


if __name__ == "__main__":
    unittest.main()
