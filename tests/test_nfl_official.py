import csv
import tempfile
import unittest
from pathlib import Path

from perfectjet.applications.nfl_scouting.official import (
    OFFICIAL_FILES, exact_id, load_official_directory, official_manifest,
)


def write_csv(root, name, rows, headers):
    with (Path(root) / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def official_fixture(root):
    # IDs above 2**53 ensure the adapter never joins through binary floats.
    a, b, c, wide = "9007199254740993", "9007199254740995", "103", "104"
    players = [{"nfl_id": aid, "draft_year": 2023, "nfl_position": pos}
               for aid, pos in ((a, "WR"), (b, "DT"), (c, "OLB"), (wide, "DE"))]
    write_csv(root, "players.csv", players, ["nfl_id", "draft_year", "nfl_position"])
    physical = [{"nfl_id": aid, "draft_year": 2023, "combine_position": pos,
                 "combine_weight": 270, "forty": 4.8, "ngs_final_score": 78}
                for aid, pos in ((a, "DE"), (b, "DT"), (c, "OLB"), (wide, "WR"))]
    write_csv(root, "combine_results.csv", physical,
              ["nfl_id", "draft_year", "combine_position", "combine_weight", "forty", "ngs_final_score"])
    source = []
    for aid in (a, b, c, wide):
        for index in range(3):
            source.append({"nfl_id": aid, "draft_year": 2023, "event_id": f"hoop-{aid}",
                           "entity_type": "PLAYER", "time": f"2023-03-02T15:00:00.{index * (200 if aid == b else 100):03d}Z",
                           "drill_name": "RUN_THE_HOOP_DRILL", "x": index * 0.4, "y": 1})
    source.append({"nfl_id": "999", "draft_year": 2023, "event_id": "unmatched", "entity_type": "PLAYER",
                   "time": "2023-03-02T15:00:00.000Z", "drill_name": "PASS_RUSH_DRILL", "x": 0, "y": 0})
    source.append({"nfl_id": a, "draft_year": 2023, "event_id": "late", "entity_type": "PLAYER",
                   "time": "2023-05-02T15:00:00.000Z", "drill_name": "PASS_RUSH_DRILL", "x": 0, "y": 0})
    source.append({"nfl_id": a, "draft_year": 2023, "event_id": "late", "entity_type": "PLAYER",
                   "time": "2023-05-02T15:00:00.100Z", "drill_name": "PASS_RUSH_DRILL", "x": 1, "y": 0})
    write_csv(root, "combine_tracking.csv", source,
              ["nfl_id", "draft_year", "event_id", "entity_type", "time", "drill_name", "x", "y"])
    games = [{"game_id": gid, "season": year, "season_type": st}
             for gid, year, st in ((1, 2023, "REG"), (2, 2023, "PRE"), (3, 2024, "REG"), (4, 2023, "POST"))]
    write_csv(root, "games.csv", games, ["game_id", "season", "season_type"])
    plays = []
    for pid, aid in ((1, a), (2, a), (3, a), (4, a), (5, c), (6, c), (7, wide)):
        plays.append({"game_id": 1, "play_id": pid, "nfl_id": aid, "player_get_off": pid / 10,
                      "play_nullified_by_penalty": "N", "yardline_number": 30 if pid == 1 else 40,
                      "yardline_side": "HOME" if pid == 1 else "AWAY", "possession_team": "HOME",
                      "play_direction": "right" if pid == 1 else "left", "down": 2,
                      "yards_to_go": 8, "lined_up_position": "DE"})
    for pid, gid, penalty, outcome in ((8, 2, "N", 0.3), (9, 3, "N", 0.3), (10, 4, "N", 0.3),
                                        (11, 1, "Y", 0.3), (12, 1, "N", "NaN"), (13, 1, "N", "inf")):
        plays.append({"game_id": gid, "play_id": pid, "nfl_id": a, "player_get_off": outcome,
                      "play_nullified_by_penalty": penalty})
    plays.append({"game_id": 100, "play_id": 14, "nfl_id": a, "player_get_off": 0.2,
                  "play_nullified_by_penalty": "N"})
    plays.append({"game_id": 1, "play_id": 15, "nfl_id": "999", "player_get_off": 0.2,
                  "play_nullified_by_penalty": "N"})
    write_csv(root, "player_play.csv", plays,
              ["game_id", "play_id", "nfl_id", "player_get_off", "play_nullified_by_penalty",
               "yardline_number", "yardline_side", "possession_team", "play_direction",
               "down", "yards_to_go", "lined_up_position"])
    snaps = [{"game_id": 1, "play_id": pid, "nfl_id": aid, "event": "ball_snap", "x": x, "y": 25, "s": 0.1}
             for pid, aid, x in ((1, a, 39), (2, a, 51), (2, a, 51), (4, a, 51), (5, c, 51))]
    headers = ["game_id", "play_id", "nfl_id", "event", "x", "y", "s"]
    write_csv(root, "game_tracking_2023.csv", snaps, headers)
    write_csv(root, "game_tracking_2024.csv", [], headers)
    write_csv(root, "game_tracking_2025.csv", [], headers)
    write_csv(root, "player_career_successes.csv", [{"nfl_id": a, "career_games_active": 999}],
              ["nfl_id", "career_games_active"])
    return a, b, c, wide


class OfficialAdapterTests(unittest.TestCase):
    def test_exact_ids_do_not_round_and_reject_nonintegral(self):
        self.assertEqual(exact_id("9007199254740993.0"), "9007199254740993")
        self.assertEqual(exact_id("1e3"), "1000")
        for value in ("1.5", "NaN", "", "-1"):
            with self.assertRaises(ValueError):
                exact_id(value)

    def test_official_cohort_joins_units_and_target_definition(self):
        with tempfile.TemporaryDirectory() as root:
            a, b, c, wide = official_fixture(root)
            ds = load_official_directory(root, minimum_plays=2, minimum_frames=2)
        self.assertFalse(ds.synthetic)
        self.assertEqual(set(ds.athletes), {a, c})
        self.assertEqual(ds.athletes[a].position, "DE")  # NFL metadata said WR.
        self.assertNotIn(wide, ds.athletes)  # NFL metadata said DE, Combine said WR.
        self.assertNotIn(b, ds.athletes)  # Its 5 Hz attempt is rejected.
        self.assertEqual([(p.athlete_id, p.play_id) for p in ds.plays], [(a, "1:1"), (a, "1:4")])
        self.assertEqual([p.outcome for p in ds.plays], [0.1, 0.4])
        self.assertEqual([p.context["snap_depth"] for p in ds.plays], [-1, -1])
        self.assertAlmostEqual(ds.plays[0].context["snap_width"], 5 / 3)
        self.assertEqual(ds.plays[0].context["snap_speed"], 0.1)
        self.assertEqual([f.t for f in ds.attempts[0].frames], [0, 0.1, 0.2])
        self.assertEqual(ds.attempts[0].recorded_on, "2023-03-02")
        self.assertEqual(ds.athletes[a].measurements["weight"], 270)
        self.assertEqual(ds.athletes[a].measurements["ngs_final_score"], 78)
        self.assertEqual(ds.athletes[a].available_on["forty"], "2023-03-02")
        self.assertTrue("not pure reaction time" in ds.outcome_definition["meaning"])
        self.assertTrue(all("career" not in key and "draft_pick" not in key and "nfl_position" not in key
                            for key in ds.athletes[a].measurements))
        audit = ds.manifest["official_adapter"]["audit"]
        self.assertEqual(audit["nonunique_snap_records"], 1)
        self.assertEqual(audit["missing_snap_records"], 2)
        self.assertEqual(audit["tracked_players_without_eligible_outcome"], 1)
        self.assertEqual(audit["unmatched_tracking_player_ids"], ["999"])
        self.assertEqual(audit["unmatched_play_player_ids"], ["999"])
        self.assertEqual(audit["unmatched_game_ids"], ["100"])
        self.assertEqual(audit["play_rejections"]["not_regular_season"], 2)
        self.assertEqual(audit["play_rejections"]["not_rookie_season"], 1)
        self.assertEqual(audit["source_rejections"]["source_not_predraft"], 1)
        self.assertEqual(len([name for name in ds.manifest if name in OFFICIAL_FILES]), 9)

    def test_threshold_is_reapplied_after_snap_exclusions(self):
        with tempfile.TemporaryDirectory() as root:
            official_fixture(root)
            ds = load_official_directory(root, minimum_plays=3, minimum_frames=2)
            self.assertEqual(ds.plays, [])
            self.assertGreater(len(ds.athletes), 0)  # Missing outcome never becomes zero.

    def test_duplicate_identity_rejected_and_hash_check_explicit(self):
        with tempfile.TemporaryDirectory() as root:
            official_fixture(root)
            manifest = official_manifest(root)
            self.assertEqual(len(manifest), 9)
            self.assertFalse(manifest["players.csv"]["matches_retained_official_snapshot"])
            with self.assertRaisesRegex(ValueError, "sha256"):
                official_manifest(root, verify_known_hashes=True)
            with (Path(root) / "players.csv").open("a") as handle:
                handle.write("9007199254740993,2023,DE\n")
            with self.assertRaisesRegex(ValueError, "duplicate identity"):
                load_official_directory(root, minimum_plays=2, minimum_frames=2)

    def test_missing_files_named_and_context_ablation_explicit(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(FileNotFoundError, "combine_tracking.csv"):
                load_official_directory(root)
            a, _, c, _ = official_fixture(root)
            ds = load_official_directory(root, minimum_plays=2, minimum_frames=2,
                                         include_snap_context=False)
            self.assertEqual(len(ds.plays), 6)
            self.assertEqual({p.athlete_id for p in ds.plays}, {a, c})
            self.assertNotIn("snap_depth", ds.plays[0].context)
            self.assertFalse(ds.manifest["official_adapter"]["include_snap_context"])


if __name__ == "__main__":
    unittest.main()
