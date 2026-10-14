# Data contract

The loader reads three CSV files through a column mapping (`schema.DEFAULT_MAPPING`; override with `--mapping mapping.json`). `synthetic.export_csv` writes the layout by example.

| File | Required columns | Meaning |
|---|---|---|
| `tracking.csv` | athlete_id, attempt_id, drill, t (s), x (yd), y (yd), recorded_on (ISO date) | Combine tracking frames, one row per frame |
| `athletes.csv` | athlete_id, position, draft_year, measured_on, measurement columns | Pre-draft measurements; `measured_on` is the availability date |
| `plays.csv` | athlete_id, season, play_id, outcome column, context columns | Eligible NFL plays; outcome and context only define the target |

Rules enforced in code:

- A measurement enters a predictor only if its availability date is on or before the decision date (April 20 of the draft year). Rejected measurements are recorded per athlete.
- The predictor builder (`validate.Featurizer`) never receives plays; a test inspects its source for any reference to plays, outcomes or context.
- `schema.audit_joins` reports unmatched ids, plays before the draft year, and attempts recorded after it.
- Every run records the SHA-256 of each source file, the code revision, the extraction version, the configuration and its hash, the folds, and the model-selection rule.
- Every derived event carries athlete, attempt, drill, frame range, time range, units, extraction version, availability date and extraction branch.

Example mapping (column names on the right are whatever the source uses):

```json
{
  "tracking": {"file": "tracking.csv", "athlete_id": "nflId", "attempt_id": "attemptId", "drill": "drill",
               "t": "time_s", "x": "x", "y": "y", "recorded_on": "date"},
  "athletes": {"file": "players.csv", "athlete_id": "nflId", "position": "position", "draft_year": "draftYear",
               "measurements": ["weight", "forty", "vertical", "three_cone"], "available_on": "combineDate"},
  "plays": {"file": "getoff.csv", "athlete_id": "nflId", "season": "season", "play_id": "playKey",
            "outcome": "get_off", "context": ["alignment", "pass_play"]},
  "outcome_definition": {"name": "get_off", "units": "seconds", "meaning": "CONFIRM BEFORE USE",
                         "eligible_play": "defensive-front snap with tracked first movement",
                         "minimum_plays": 20, "lower_is_better": true}
}
```
