"""Explicit artificial geometry/schema fixtures; no empirical scouting claims."""
import csv
import math
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from perfectjet.applications.nfl_scouting.movement_targets import (
    DEFAULT_CHANNELS, MovementTargetRecord, extract_movement_record,
    load_movement_targets, select_target_plays, summarize_movement_targets,
)
from perfectjet.applications.nfl_scouting.schema import Athlete, Dataset, Frame, Play


def write_csv(root, name, rows, headers):
    with (Path(root)/name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def trajectory(axis=(-1, 0), origin=(41.28, 26), onset=0.2, acceleration=4):
    return [Frame(i/10, origin[0]+axis[0]*acceleration*max(i/10-onset, 0)**2/2,
                  origin[1]+axis[1]*acceleration*max(i/10-onset, 0)**2/2)
            for i in range(-5, 26)]


def fixture(root, *, duplicate_snap=False, missing_time=False,
            gaps=(), season_type="REG", metadata_year=2023,
            future=False, overflow=False, january=False):
    aid = "9007199254740993"
    year = 2025 if future else 2023
    players = {aid: Athlete(aid, "DE", year, {"forty": 4.8}, {"forty": f"{year}-03-01"})}
    play = Play(aid, year, "1:7", 1.0, {"snap_depth": 1.28, "down": 2})
    dataset = Dataset(players, [], [play], {}, {"name": "player_get_off"}, synthetic=True)
    write_csv(root, "games.csv", [{"game_id": 1, "season": year if future else metadata_year,
                                   "season_type": season_type}],
              ["game_id", "season", "season_type"])
    metadata = {"game_id": "1", "play_id": "7", "nfl_id": aid,
                "play_nullified_by_penalty": "N", "yardline_number": 30,
                "yardline_side": "HOME", "possession_team": "HOME", "play_direction": "right"}
    write_csv(root, "player_play.csv", [metadata], list(metadata))
    base = datetime(year+1, 1, 10, 18, tzinfo=timezone.utc) if january else datetime(year, 9, 10, 18, tzinfo=timezone.utc)
    rows = []
    for f in trajectory():
        if f.t in gaps:
            continue
        row = {"game_id": 1, "play_id": 7, "nfl_id": aid,
               "event": "ball_snap" if f.t == 0 else "",
               "time": (base+timedelta(seconds=f.t)).isoformat(), "x": f.x, "y": f.y}
        rows.append(row)
        if f.t == 0 and duplicate_snap:
            rows.append(dict(row))
    # Same athlete and timestamp in another play must not enter the window.
    rows.append({"game_id": 1, "play_id": 8, "nfl_id": aid, "event": "ball_snap",
                 "time": base.isoformat(), "x": -999, "y": 100})
    # Selected athlete/play outside the declared window must not enter memory.
    for offset in (-10, 10):
        rows.append({"game_id": 1, "play_id": 7, "nfl_id": aid, "event": "",
                     "time": (base+timedelta(seconds=offset)).isoformat(), "x": -999, "y": 100})
    # An unrelated player and football can have unparseable time: filter first.
    for other in ("111", ""):
        rows.append({"game_id": 1, "play_id": 7, "nfl_id": other, "event": "ball_snap",
                     "time": "not a timestamp", "x": -999, "y": 100})
    if overflow:
        rows += [dict(rows[1]) for _ in range(150)]
    headers = ["game_id", "play_id", "nfl_id", "event", "time", "x", "y"]
    if missing_time:
        headers.remove("time")
        rows = [{key: value for key, value in row.items() if key != "time"} for row in rows]
    for season in (2023, 2024, 2025):
        write_csv(root, f"game_tracking_{season}.csv", rows if season == year else [], headers)
    return dataset


class MovementGeometryTests(unittest.TestCase):
    def setUp(self):
        self.play = Play("101", 2023, "1:7", 1.0, {"down": 2})

    def test_decomposition_and_channels_have_correct_units_and_identity(self):
        record = extract_movement_record(self.play, trajectory(), 0, (40, 26), (-1, 0))
        self.assertTrue(record.usable)
        self.assertTrue(record.usable_for_post_snap_onset)
        self.assertAlmostEqual(record.channels["onset_delay"], 0.3)
        self.assertAlmostEqual(record.channels["motion_to_los"], 0.7)
        self.assertAlmostEqual(record.channels["forward_displacement_05"], 0.7)
        self.assertAlmostEqual(record.channels["directional_retention_05"], 1)
        self.assertAlmostEqual(record.channels["forward_path_fraction_05"], 1)
        self.assertAlmostEqual(record.channels["onset_delay"]+record.channels["motion_to_los"],
                               record.channels["tracked_snap_to_los"])
        self.assertFalse(record.lineage["reaction_time_interpretation"])
        self.assertTrue(record.lineage["target_only"])
        self.assertEqual(record.lineage["channel_units"]["forward_displacement_05"], "yards")
        self.assertEqual(record.supplied_get_off, 1)
        self.assertEqual(record.context, self.play.context)
        self.assertIsNot(record.context, self.play.context)

    def test_rotation_translation_and_reflection_covariance(self):
        base_frames = trajectory()
        base = extract_movement_record(self.play, base_frames, 0, (40, 26), (-1, 0))
        angle = 0.731
        c, s = math.cos(angle), math.sin(angle)
        def transform(x, y):
            return c*x-s*y+123, s*x+c*y-48
        rotated = [Frame(f.t, *transform(f.x, f.y)) for f in base_frames]
        result = extract_movement_record(self.play, rotated, 0, transform(40, 26), (-c, -s))
        reflected = [Frame(f.t, -f.x+5, f.y-3) for f in base_frames]
        mirror = extract_movement_record(self.play, reflected, 0, (-35, 23), (1, 0))
        for candidate in (result, mirror):
            self.assertTrue(candidate.usable)
            for channel, value in base.channels.items():
                self.assertAlmostEqual(candidate.channels[channel], value, 10)
            for expected, actual in zip(base.frames, candidate.frames):
                self.assertAlmostEqual(actual.x, expected.x, 10)

    def test_lateral_motion_changes_retention_without_rotation_artifact(self):
        frames = [Frame(f.t, f.x, f.y+max(f.t-0.2, 0)) for f in trajectory()]
        result = extract_movement_record(self.play, frames, 0, (40, 26), (-1, 0))
        self.assertTrue(result.usable)
        self.assertLess(result.channels["directional_retention_05"], 1)
        self.assertGreater(result.channels["directional_retention_05"], 0)

    def test_nonpositive_depth_is_not_absolute_flipped(self):
        result = extract_movement_record(self.play, trajectory(origin=(39, 26)),
                                          0, (40, 26), (-1, 0))
        self.assertFalse(result.usable)
        self.assertEqual(result.channels, {})
        self.assertIn("snap_not_on_defensive_side_of_los", result.flags)
        self.assertEqual(result.supplied_get_off, 1)

    def test_missing_gap_duplicate_and_missing_snap_rejected(self):
        frames = trajectory()
        duplicate = frames+[frames[8]]
        self.assertIn("duplicate_tracking_timestamp", extract_movement_record(
            self.play, duplicate, 0, (40, 26), (-1, 0)).flags)
        missing = [f for f in frames if f.t not in (0.9, 1.0)]
        result = extract_movement_record(self.play, missing, 0, (40, 26), (-1, 0))
        self.assertFalse(result.usable)
        self.assertIn("crossing_in_missing_interval", result.flags)
        self.assertIn("missing_or_nonunique_snap_frame", extract_movement_record(
            self.play, [f for f in frames if f.t != 0], 0, (40, 26), (-1, 0)).flags)

    def test_anticipation_remains_diagnostic_not_reaction_time(self):
        frames = trajectory(onset=-0.2)
        result = extract_movement_record(self.play, frames, 0, (40, 26), (-1, 0))
        self.assertTrue(result.usable)
        self.assertFalse(result.usable_for_post_snap_onset)
        self.assertLessEqual(result.channels["onset_delay"], 0)
        self.assertFalse(result.lineage["reaction_time_interpretation"])

    def test_semantic_overrides_cannot_change_named_horizon_or_geometry(self):
        for options in ({"post_onset_horizon": 0.7}, {"direction": -1}):
            with self.assertRaises(ValueError):
                extract_movement_record(self.play, trajectory(), 0, (40, 26), (-1, 0), options)


class MovementStreamingTests(unittest.TestCase):
    def test_january_games_remain_in_their_prior_nfl_season(self):
        with tempfile.TemporaryDirectory() as root:
            dataset = fixture(root, january=True)
            result = load_movement_targets(root, dataset)
        self.assertTrue(result.records[0].usable)
        self.assertEqual(result.records[0].season, 2023)
        self.assertTrue(result.records[0].lineage["raw_snap_timestamp"].startswith("2024-01-"))

    def test_exact_ids_two_pass_window_and_primary_outcome_retained(self):
        with tempfile.TemporaryDirectory() as root:
            dataset = fixture(root)
            result = load_movement_targets(root, dataset)
        self.assertEqual(len(result.records), 1)
        record = result.records[0]
        self.assertEqual(record.athlete_id, "9007199254740993")
        self.assertEqual(record.play_id, "1:7")
        self.assertTrue(record.usable)
        self.assertEqual(len(record.frames), 31)
        self.assertEqual(record.frames[0].t, -0.5)
        self.assertEqual(record.frames[-1].t, 2.5)
        self.assertEqual(result.audit["retained_window_frames"], 31)
        self.assertEqual(result.audit["rows_scanned_pass1"], result.audit["rows_scanned_pass2"])
        self.assertTrue(result.manifest["synthetic"])
        self.assertTrue(result.manifest["target_only"])
        self.assertEqual(dataset.athletes[record.athlete_id].measurements, {"forty": 4.8})
        self.assertEqual(dataset.plays[0].outcome, 1)

    def test_nonunique_snap_is_recorded_as_failure(self):
        with tempfile.TemporaryDirectory() as root:
            dataset = fixture(root, duplicate_snap=True)
            result = load_movement_targets(root, dataset)
        self.assertFalse(result.records[0].usable)
        self.assertIn("nonunique_or_invalid_snap_record", result.records[0].flags)
        self.assertEqual(result.audit["usable_records"], 0)
        self.assertEqual(result.records[0].supplied_get_off, 1)

    def test_metadata_regular_season_and_rookie_rechecks(self):
        for options, reason in (({"season_type": "PRE"}, "not_regular_season"),
                                ({"metadata_year": 2024}, "not_rookie_season")):
            with tempfile.TemporaryDirectory() as root:
                dataset = fixture(root, **options)
                result = load_movement_targets(root, dataset)
            self.assertIn(reason, result.records[0].flags)
            self.assertEqual(result.audit["metadata_rejections"][reason], 1)

    def test_missing_tracking_schema_is_not_synthetic_fallback(self):
        with tempfile.TemporaryDirectory() as root:
            dataset = fixture(root, missing_time=True)
            with self.assertRaisesRegex(ValueError, "missing movement tracking columns"):
                load_movement_targets(root, dataset)
        with tempfile.TemporaryDirectory() as root:
            dataset = fixture(root)
            (Path(root)/"game_tracking_2023.csv").unlink()
            with self.assertRaisesRegex(FileNotFoundError, "game_tracking_2023"):
                load_movement_targets(root, dataset)

    def test_frame_limit_prevents_duplicate_heavy_accumulation(self):
        with tempfile.TemporaryDirectory() as root:
            dataset = fixture(root, overflow=True)
            result = load_movement_targets(root, dataset, maximum_frames_per_record=35)
        self.assertIn("tracking_window_frame_limit_exceeded", result.records[0].flags)
        self.assertEqual(result.records[0].frames, [])
        self.assertLessEqual(result.audit["retained_window_frames"], 35)

    def test_training_cutoff_filters_all_and_rejects_explicit_future_ids(self):
        with tempfile.TemporaryDirectory() as root:
            dataset = fixture(root, future=True)
            result = load_movement_targets(root, dataset, season_before=2025)
            self.assertEqual(result.records, [])
            self.assertEqual(result.audit["cutoff_excluded_records"], 1)
            with self.assertRaisesRegex(ValueError, "training cutoff"):
                load_movement_targets(root, dataset, athlete_ids=list(dataset.athletes), season_before=2025)

    def test_duplicate_official_play_key_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            dataset = fixture(root)
            dataset.plays.append(dataset.plays[0])
            with self.assertRaisesRegex(ValueError, "duplicate target"):
                select_target_plays(dataset)


def summary_record(game, play, value, *, missing=False, usable=True):
    channels = dict(zip(DEFAULT_CHANNELS, [value, value*2, value*3]))
    if missing:
        channels.pop(DEFAULT_CHANNELS[-1])
    return MovementTargetRecord("101", 2023, f"{game}:{play}", str(game), 1,
                                {}, channels=channels, usable=usable,
                                usable_for_post_snap_onset=usable)


class MovementSummaryTests(unittest.TestCase):
    def test_game_cluster_covariance_does_not_treat_plays_as_independent(self):
        records = [summary_record(1, 1, 1), summary_record(1, 2, 1),
                   summary_record(2, 1, 3), summary_record(2, 2, 3)]
        result = summarize_movement_targets(records)["101"]
        self.assertEqual(result["mean"], [2, 4, 6])
        self.assertEqual(result["covariance"], [[1, 2, 3], [2, 4, 6], [3, 6, 9]])
        self.assertEqual(result["n_games"], 2)
        self.assertTrue(result["precision_identified"])
        # Duplicating all plays inside each game does not create new games.
        copies = records+[summary_record(int(r.game_id), 10+i, r.channels["onset_delay"])
                          for i, r in enumerate(records)]
        self.assertEqual(summarize_movement_targets(copies)["101"]["covariance"], result["covariance"])

    def test_single_game_precision_is_unknown_not_zero(self):
        result = summarize_movement_targets([summary_record(1, 1, 2)])["101"]
        self.assertIsNone(result["covariance"])
        self.assertFalse(result["precision_identified"])
        self.assertFalse(result["eligible"])
        self.assertEqual(result["mean"], [2, 4, 6])

    def test_joint_support_and_marginal_coverage_are_both_reported(self):
        records = [summary_record(1, 1, 1), summary_record(2, 1, 3),
                   summary_record(3, 1, 20, missing=True)]
        result = summarize_movement_targets(records)["101"]
        self.assertEqual(result["mean"], [2, 4, 6])
        self.assertEqual(result["n_plays"], 2)
        self.assertEqual(result["requested_plays"], 3)
        self.assertEqual(result["channel_available_counts"],
                         {"onset_delay": 3, "motion_to_los": 3, "forward_displacement_05": 2})

    def test_weighted_residual_summary_matches_declared_estimand(self):
        records = [summary_record(1, 1, 1), summary_record(2, 1, 3)]
        weights = {("101", "1:1"): 3, ("101", "2:1"): 1}
        residuals = {("101", "1:1"): {"onset_delay": 2},
                     ("101", "2:1"): {"onset_delay": 4}}
        result = summarize_movement_targets(records, channels=("onset_delay",),
                                             weights=weights, residuals=residuals)["101"]
        self.assertEqual(result["mean"], [2.5])
        self.assertEqual(result["covariance"], [[0.5625]])
        self.assertAlmostEqual(result["effective_play_count"], 1.6)
        self.assertTrue(result["context_adjusted"])

    def test_invalid_weights_and_duplicate_records_are_rejected(self):
        record = summary_record(1, 1, 1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            summarize_movement_targets([record, record])
        for weight in (-1, math.nan):
            with self.assertRaisesRegex(ValueError, "weights"):
                summarize_movement_targets([record], weights={("101", "1:1"): weight})


if __name__ == "__main__":
    unittest.main()
