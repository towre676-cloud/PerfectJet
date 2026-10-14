"""Pipeline isolation checks on explicitly synthetic fixtures, never NFL evidence."""
import copy
import importlib.util
import unittest
from dataclasses import replace
from unittest.mock import patch

SCIENTIFIC = all(importlib.util.find_spec(name) is not None for name in ("numpy", "pandas", "sklearn"))
if SCIENTIFIC:
    import numpy as np
    import pandas as pd
    from perfectjet.applications.nfl_scouting import burst_transfer as transfer
    from perfectjet.applications.nfl_scouting.burst import BurstObservation, FORTY
    from perfectjet.applications.nfl_scouting.official import FRONT_DRILLS, MEASUREMENT_COLUMNS
    from perfectjet.applications.nfl_scouting.schema import Attempt, Lineage, Play
    from perfectjet.applications.nfl_scouting.synthetic import generate


def fixture():
    """Synthetic labels with official-shaped covariates; keep synthetic=True."""
    ds = generate(n_athletes=36, years=(2023, 2024), seed=581, plays_range=(36, 36))
    for i, athlete in enumerate(ds.athletes.values()):
        for j, name in enumerate(MEASUREMENT_COLUMNS.values()):
            if name not in athlete.measurements:
                athlete.measurements[name] = 10.0 + 0.7 * j + ((i * (j + 3)) % 11) / 10
                athlete.available_on[name] = f"{athlete.draft_year}-03-01"
    ds.attempts = []
    observations = []
    for i, (aid, athlete) in enumerate(ds.athletes.items()):
        trait = ds.manifest["synthetic"]["latent"][aid]
        for j in range(2):
            attempt_id = f"{aid}:forty:{j}"
            ds.attempts.append(Attempt(aid, attempt_id, FORTY, [], f"{athlete.draft_year}-03-01"))
            lineage = Lineage(aid, attempt_id, FORTY, (0, 9), (0.0, 0.9),
                              "yards/s^2", "synthetic-test-only", f"{athlete.draft_year}-03-01")
            value = 3.0 + 0.6 * trait + (0.12 if j else -0.12)
            observations.append(BurstObservation(aid, attempt_id, FORTY, value,
                                                {"raw": value}, 0.2, 0.7, 0.7, 0.0, lineage))
        if i % 2:
            ds.attempts.append(Attempt(aid, f"{aid}:other", FRONT_DRILLS[0], [],
                                      f"{athlete.draft_year}-03-01"))
    plays = []
    for i, p in enumerate(ds.plays):
        year = ds.athletes[p.athlete_id].draft_year
        ctx = {
            "down": float(i % 4 + 1), "yards_to_go": float(i % 12 + 1),
            "yardline_number": float(i % 50), "quarter": float(i % 4 + 1),
            "pre_snap_home_score": float(i % 4 * 7), "pre_snap_visitor_score": float(i % 3 * 7),
            "snap_depth": 0.2 + (i % 7) / 10, "snap_width": float(i % 6), "snap_speed": 0.05,
            "lined_up_position": "wide" if i % 2 else "interior",
            "offense_formation": "shotgun", "blitzing": str(i % 2),
            "team_abbr": "T1", "possession_team": "T2",
        }
        plays.append(replace(p, season=year, play_id=f"game-{i % 4}:{p.play_id}", context=ctx))
    ds.plays = plays
    ds.outcome_definition["minimum_plays"] = 5
    tr = sorted(a for a, p in ds.athletes.items() if p.draft_year == 2023)
    te = sorted(a for a, p in ds.athletes.items() if p.draft_year == 2024)
    return ds, observations, tr, te


@unittest.skipUnless(SCIENTIFIC, "Optional scouting scientific dependencies are unavailable")
class BurstTransferIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds, cls.obs, cls.tr, cls.te = fixture()
        cls.reference = transfer.fit_split(cls.ds, cls.obs, cls.tr, cls.te, 2024, 100.0, seed=411)

    def test_heldout_nfl_labels_cannot_change_scout_predictions_or_training_calibration(self):
        ds = copy.deepcopy(self.ds)
        heldout = set(self.te)
        ds.plays = [replace(p, outcome=p.outcome + 100.0) if p.athlete_id in heldout else p for p in ds.plays]
        changed = transfer.fit_split(ds, self.obs, self.tr, self.te, 2024, 100.0, seed=411)
        self.assertGreater(max(abs(a - b) for a, b in zip(changed["y"], self.reference["y"])), 90)
        for field in ("baseline", "movement"):
            np.testing.assert_allclose(changed[field], self.reference[field], rtol=0, atol=1e-12)
        self.assertEqual(changed["calibration"], self.reference["calibration"])
        self.assertEqual(changed["loading"], self.reference["loading"])

    def test_heldout_nfl_context_is_only_outcome_reference_never_scout_input(self):
        ds = copy.deepcopy(self.ds)
        heldout = set(self.te)
        ds.plays = [replace(p, context={**p.context, "snap_depth": 5000.0,
                                       "team_abbr": "NEVER_SEEN", "yards_to_go": 9000.0})
                    if p.athlete_id in heldout else p for p in ds.plays]
        pd.testing.assert_frame_equal(transfer.predictor_frame(ds, self.te),
                                      transfer.predictor_frame(self.ds, self.te))
        changed = transfer.fit_split(ds, self.obs, self.tr, self.te, 2024, 100.0, seed=411)
        np.testing.assert_allclose(changed["baseline"], self.reference["baseline"], rtol=0, atol=1e-12)
        np.testing.assert_allclose(changed["movement"], self.reference["movement"], rtol=0, atol=1e-12)
        self.assertNotEqual(changed["y"], self.reference["y"])

    def test_strong_baseline_has_all_fifteen_measurements_and_shared_raw_counts(self):
        frame = transfer.predictor_frame(self.ds, self.te)
        self.assertTrue(set(MEASUREMENT_COLUMNS.values()).issubset(frame.columns))
        self.assertEqual(len(MEASUREMENT_COLUMNS), 15)
        self.assertTrue(all("count__" + d in frame and "available__" + d in frame for d in FRONT_DRILLS))
        self.assertFalse(any("snap" in c or "outcome" in c or "get_off" in c for c in frame))
        # Source event usability and NFL outcomes cannot change raw-attempt flags.
        ds = copy.deepcopy(self.ds)
        ds.plays = []
        ds.attempts = [replace(a, frames=[]) for a in ds.attempts]
        pd.testing.assert_frame_equal(frame, transfer.predictor_frame(ds, self.te))
        without = transfer.predictor_frame(ds, self.te, include_ngs=False)
        self.assertEqual(set(frame) - set(without), {c for c in MEASUREMENT_COLUMNS.values() if c.startswith("ngs_")})

    def test_late_measurements_and_late_raw_attempts_are_excluded(self):
        ds = copy.deepcopy(self.ds)
        aid = self.te[0]
        athlete = ds.athletes[aid]
        athlete.measurements["height"] = 1000000.0
        athlete.available_on["height"] = "2024-05-01"
        ds.attempts.append(Attempt(aid, "late", FORTY, [], "2024-05-01"))
        row = transfer.predictor_frame(ds, [aid]).iloc[0]
        self.assertTrue(np.isnan(row.height))
        self.assertEqual(row["count__" + FORTY], 2)

    def test_original_bootstrap_groups_are_indivisible_and_overlap_rejected(self):
        ds = copy.deepcopy(self.ds)
        original = self.tr[0]
        clone = original + "-copy"
        ds.athletes[clone] = replace(ds.athletes[original], athlete_id=clone, bootstrap_group=original)
        mapping = transfer._groups(ds, self.tr + [clone], 3, seed=27)
        self.assertEqual(mapping[original], mapping[clone])
        with self.assertRaisesRegex(ValueError, "original-athlete leakage"):
            transfer.fit_split(ds, self.obs, self.tr, [clone], 2024, 100.0)

    def test_inner_selection_uses_whole_players_and_never_outer_test_labels(self):
        # Spy on real fits: verifies every rebuilding boundary, not a mocked score.
        calls = []
        real_fit = transfer.fit_split
        def observed_fit(ds, obs, tr, te, *args, **kwargs):
            calls.append((set(tr), set(te)))
            return real_fit(ds, obs, tr, te, *args, **kwargs)
        with patch.object(transfer, "fit_split", side_effect=observed_fit):
            reference = transfer.nested_fold(self.ds, self.obs, self.tr, self.te, 2024, True, 97)
        self.assertTrue(all(not a & b for a, b in calls))
        inner = [(a, b) for a, b in calls if b != set(self.te)]
        self.assertEqual(len(inner), 9)
        self.assertTrue(all((a | b) == set(self.tr) for a, b in inner))
        ds = copy.deepcopy(self.ds)
        ds.plays = [replace(p, outcome=p.outcome - 50.0) if p.athlete_id in set(self.te) else p for p in ds.plays]
        changed = transfer.nested_fold(ds, self.obs, self.tr, self.te, 2024, True, 97)
        self.assertEqual(reference["chosen_penalties"], changed["chosen_penalties"])
        self.assertEqual(reference["inner_scores"], changed["inner_scores"])
        np.testing.assert_allclose(reference["movement"], changed["movement"], rtol=0, atol=1e-12)

    def test_outcome_cluster_variance_matches_play_weighted_target(self):
        ds = copy.deepcopy(self.ds)
        aid = self.te[0]
        # Two games with unequal exposure: one zero residual and nine residuals
        # equal to 2. Player target is 1.8, not the equal-game mean of 1.0.
        ds.plays = [p for p in ds.plays if p.athlete_id != aid]
        ds.plays.extend(Play(aid, 2024, f"g{int(i > 0)}:{i}", 0.0 if i == 0 else 2.0, {})
                        for i in range(10))
        with patch.object(transfer, "_context_predict", side_effect=lambda a, b: np.zeros(len(b))):
            y, noise, _ = transfer.targets(ds, self.tr, [aid], 2024, 11)
        self.assertAlmostEqual(y[aid], 1.8)
        expected = 2.0 * ((-1.8 / 10) ** 2 + ((18.0 - 9 * 1.8) / 10) ** 2)
        self.assertAlmostEqual(noise[aid], expected)

    def test_top_level_experiment_rejects_synthetic_evidence(self):
        with self.assertRaisesRegex(ValueError, "official real inputs"):
            transfer.experiment(self.ds)


if __name__ == "__main__":
    unittest.main()
