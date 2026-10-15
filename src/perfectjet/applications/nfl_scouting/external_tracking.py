"""External, real NFL tracking tests; these are not Combine scouting tests.

The public 2021 regional-event source supplies NFL/PFF pass-rush roles.  Tracking
is aligned to metadata LOS and the defensive forward direction, without absolute
value flips of invalid snap depths.  Velocities use backwards differences only.
Learned continuation representations are selected on whole training players.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from hashlib import sha256
from math import sqrt
from pathlib import Path

import numpy as np
import pandas as pd

from .crossing import extract_crossing
from .predictive_state import MovementSequence, discover_predictive_state, _validated, _fit, _score
from .schema import Frame


VERSION = "external-nfl-tracking/1"


@dataclass
class ExternalTracking:
    records: list = field(default_factory=list)
    sequences: list = field(default_factory=list)
    audit: dict = field(default_factory=dict)


def is_pass_rush_role(value):
    """The source CSV capitalizes Rush; its prose documentation does not."""
    return isinstance(value, str) and value.strip().casefold() == "pass rush"


def defensive_geometry(play_direction, absolute_yardline, snap_x):
    """Metadata LOS in field coordinates; defender forward axis points at offense.

    A negative depth is a rejected geometry observation, never rectified by abs.
    """
    if play_direction not in ("left", "right"):
        raise ValueError("Unknown offensive play direction")
    los, x = float(absolute_yardline), float(snap_x)
    if not np.isfinite([los, x]).all() or not 0 <= los <= 120:
        raise ValueError("Finite field-coordinate LOS and snap position required")
    axis = -1.0 if play_direction == "right" else 1.0
    depth = (los-x)*axis
    if depth <= 0:
        raise ValueError("Player is not strictly on defensive side of metadata LOS")
    return axis, depth


def causal_velocity_sequence(athlete_id, attempt_id, frames, *, interval=0.1):
    """Uniform forward/lateral velocity channels from causal first differences.

    No provided s/a/direction channel or centered smoother enters this test.
    The first frame cannot supply a velocity and is omitted.
    """
    if len(frames) < 9:
        raise ValueError("Insufficient tracking for common five-frame history")
    t = np.asarray([f.t for f in frames], dtype=float)
    xy = np.asarray([[f.x, f.y] for f in frames], dtype=float)
    if not np.isfinite(t).all() or not np.isfinite(xy).all():
        raise ValueError("Finite tracking required")
    if not np.allclose(np.diff(t), interval, atol=1e-6, rtol=0):
        raise ValueError("Missing or nonuniform tracking intervals")
    v = np.diff(xy, axis=0)/interval
    return MovementSequence(str(athlete_id), str(attempt_id), t[1:].tolist(), v.tolist())


def relative_frame_clock(frame_ids, timestamps, snap_frame, *, interval=0.1):
    """Use 10 Hz frame IDs after checking the supplied timestamp resolution.

    Regional timestamps are whole seconds: repeated times are not repeated
    frames. A single unknown clock phase must explain every frame within the
    one-second quantization cell. Fractional timestamps require tighter checks.
    The 0.1 s interval is declared and corroborated by whole-clock transitions;
    the source does not preserve subframe event timing.
    """
    ids = np.asarray(frame_ids, dtype=float)
    stamps = pd.to_datetime(pd.Series(timestamps), utc=True, format="ISO8601")
    nanos = stamps.astype("int64").to_numpy()
    if stamps.isna().any() or not np.isfinite(ids).all():
        raise ValueError("Invalid frame clocks")
    expected = (ids-float(snap_frame))*interval
    observed = (nanos-nanos[0])/1e9
    residual = observed-expected
    whole_second = np.all(nanos % 1_000_000_000 == 0)
    tolerance = 1.0+1e-6 if whole_second else 1e-5
    if np.ptp(residual) > tolerance:
        raise ValueError("Frame IDs disagree with declared 10 Hz clock")
    return expected, "whole_second_quantized" if whole_second else "fractional_seconds"


def _at(frames, when):
    t = np.asarray([f.t for f in frames])
    if when < t[0]-1e-8 or when > t[-1]+1e-8:
        return None
    return np.asarray([np.interp(when, t, [f.x for f in frames]),
                       np.interp(when, t, [f.y for f in frames])])


def directional_interval(frames, start, horizon=0.5, maximum_gap=0.15):
    """Useful forward progress and path arc over the same observed interval."""
    a, b = _at(frames, start), _at(frames, start+horizon)
    if a is None or b is None:
        return None
    middle = [f for f in frames if start < f.t < start+horizon]
    t = [start]+[f.t for f in middle]+[start+horizon]
    if any(y-x > maximum_gap+1e-8 for x, y in zip(t, t[1:])):
        return None
    xy = np.asarray([a]+[[f.x, f.y] for f in middle]+[b])
    arc = float(np.linalg.norm(np.diff(xy, axis=0), axis=1).sum())
    forward = float(b[0]-a[0])
    return {"forward_displacement_05": forward, "path_arc_05": arc,
            "forward_path_fraction_05": None if arc <= 0 else forward/arc}


def first_passage(frames, level, *, after=0.0, maximum=2.5):
    """First observed forward crossing with no extrapolation or censored fill."""
    for a, b in zip(frames, frames[1:]):
        if b.t < after or a.t > maximum or b.t-a.t > 0.15+1e-8:
            continue
        if a.x < level <= b.x:
            when = a.t+(level-a.x)/(b.x-a.x)*(b.t-a.t)
            if after <= when <= maximum:
                return float(when)
    return None


def extract_regional(root, *, maximum_sequences_per_player=4, maximum_sequence_players=320, game_ids=None):
    """Read each compressed public game once and retain bounded velocity panels.

    All pass-rush records are retained for LOS mechanism analysis.  Forecast
    sequences are capped deterministically by player/play hashes, independently
    of movement/outcomes.  NFL role annotations select the analysis cohort and
    are not claimed available as pre-draft prospect features.
    """
    root = Path(root)
    base = root/"data" if (root/"data").exists() else root
    pff = pd.read_csv(base/"pffScoutingData.csv.gz")
    pff = pff[pff.pff_role.map(is_pass_rush_role)].copy()
    if pff.empty:
        raise ValueError("The input has no recognized Pass Rush role annotations")
    plays = pd.read_csv(base/"plays.csv.gz")
    games = pd.read_csv(base/"games.csv.gz")
    player_table = pd.read_csv(base/"players.csv.gz")
    names = {str(int(row.nflId)): row.displayName for row in player_table.itertuples()}
    weeks = dict(zip(games.gameId, games.week))
    play_meta = {(int(r.gameId), int(r.playId)): r for r in plays.itertuples()}
    rush_meta = {(int(r.gameId), int(r.playId), int(r.nflId)): r for r in pff.itertuples()}
    ids = sorted({str(k[2]) for k in rush_meta}, key=lambda x: sha256(x.encode()).digest())
    sequence_ids = set(ids[:maximum_sequence_players])
    selected_plays = defaultdict(list)
    for game, play, athlete in rush_meta:
        if str(athlete) in sequence_ids:
            selected_plays[str(athlete)].append((game, play))
    keep_sequences = set()
    for athlete, keys in selected_plays.items():
        keys.sort(key=lambda key: sha256(f"{athlete}:{key}".encode()).digest())
        keep_sequences.update((g, p, int(athlete)) for g, p in keys[:maximum_sequences_per_player])
    records, sequences, counts, flags = [], [], Counter(), Counter()
    files = sorted((base/"tracking").glob("tracking_*.csv.gz"))
    if game_ids is not None:
        allowed = {int(x) for x in game_ids}
        files = [path for path in files if int(path.name.split('_')[1].split('.')[0]) in allowed]
    if not files:
        raise ValueError("No public regional tracking games found")
    for path in files:
        tracking = pd.read_csv(path)
        counts["tracking_rows"] += len(tracking)
        game = int(tracking.gameId.iloc[0])
        snaps = tracking[tracking.event == "ball_snap"].groupby("playId").frameId.agg(["min", "max"])
        for play, block in tracking.groupby("playId", sort=False):
            counts["tracked_plays"] += 1
            if play not in snaps.index or snaps.loc[play, "min"] != snaps.loc[play, "max"]:
                flags["missing_or_inconsistent_snap"] += 1
                continue
            snap_frame = int(snaps.loc[play, "min"])
            meta = play_meta.get((game, int(play)))
            if meta is None:
                flags["missing_play_metadata"] += 1
                continue
            # Frame IDs are 10 Hz. Real timestamps must agree before accepting.
            block = block[(block.frameId >= snap_frame-5) & (block.frameId <= snap_frame+25)].copy()
            try:
                block["relative_time"], clock = relative_frame_clock(block.frameId, block.time, snap_frame)
                counts[f"clock_{clock}_plays"] += 1
            except ValueError:
                flags["frame_clock_disagreement"] += 1
                continue
            for raw_id, athlete in block[block.nflId.notna()].groupby("nflId", sort=False):
                key = game, int(play), int(raw_id)
                role = rush_meta.get(key)
                if role is None:
                    continue
                counts["pass_rush_records"] += 1
                athlete = athlete.sort_values("frameId")
                snap = athlete[athlete.frameId == snap_frame]
                if len(snap) != 1:
                    flags["missing_or_duplicate_player_snap"] += 1
                    continue
                try:
                    axis, depth = defensive_geometry(snap.playDirection.iloc[0], meta.absoluteYardlineNumber,
                                                       snap.x.iloc[0])
                except ValueError:
                    flags["invalid_defensive_depth"] += 1
                    continue
                sx, sy = float(snap.x.iloc[0]), float(snap.y.iloc[0])
                frames = [Frame(float(r.relative_time), axis*(float(r.x)-sx), float(r.y)-sy)
                          for r in athlete.itertuples()]
                cross = extract_crossing(frames, 0.0, depth, maximum_post_snap=2.5)
                flags.update(cross["flags"])
                row = {"athlete_id": str(int(raw_id)), "name": names.get(str(int(raw_id))),
                       "game_id": game, "play_id": int(play), "week": int(weeks[game]),
                       "position_lined_up": role.pff_positionLinedUp, "depth": depth,
                       "snap_width": abs(sy-26.65), "down": int(meta.down), "yards_to_go": int(meta.yardsToGo),
                       "pressure": int(any(getattr(role, x) == 1 for x in ("pff_hit", "pff_hurry", "pff_sack"))),
                       "onset_delay": cross["onset_delay"], "snap_to_los": cross["snap_to_los"],
                       "motion_to_los": cross["motion_to_los"], "usable": cross["usable"],
                       "onset_post_snap": cross["usable_for_post_snap_onset"], "flags": cross["flags"],
                       "formation": meta.offenseFormation, "play_action": int(meta.pff_playAction)}
                onset = cross["motion_onset_time"]
                if onset is not None:
                    interval = directional_interval(frames, onset)
                    if interval:
                        row.update(interval)
                    at_onset = _at(frames, onset)
                    row["remaining_depth_at_onset"] = depth-float(at_onset[0])
                    for distance in (0.25, 0.5, 1.0, 2.0):
                        row[f"onset_forward_arrival_{distance:g}"] = first_passage(
                            frames, float(at_onset[0])+distance, after=onset)
                records.append(row)
                if key in keep_sequences:
                    try:
                        sequences.append(causal_velocity_sequence(str(int(raw_id)), f"{game}:{play}", frames))
                    except ValueError:
                        flags["sequence_nonuniform_or_short"] += 1
    return ExternalTracking(records, sequences,
                            {"version": VERSION, "games": len(files), "counts": dict(counts),
                             "flags": dict(flags), "players_with_geometry": len({r['athlete_id'] for r in records}),
                             "sequence_players": len({s.athlete_id for s in sequences}),
                             "sequence_cap_per_player": maximum_sequences_per_player,
                             "sequence_player_cap": maximum_sequence_players,
                             "raw_inputs_are_real": True, "combine_transfer_test": False})


def _player_metrics(predictions):
    per_player = defaultdict(list)
    for athlete, error in predictions:
        per_player[athlete].append(error)
    errors = {player: np.mean(values, axis=0) for player, values in per_player.items()}
    values = np.asarray(list(errors.values()))
    return {"players": len(errors), "rmse": float(np.sqrt(values.mean())),
            "channel_rmse": np.sqrt(values.mean(axis=0)).tolist(),
            "player_mse": {key: float(np.mean(value)) for key, value in errors.items()}}


def history_extrapolation(history, steps=3, *, degree=1, interval=0.1):
    """Ordinary least-squares time polynomial fitted to the supplied past only."""
    history = np.asarray(history, dtype=float)
    if history.ndim != 2 or not np.isfinite(history).all() or len(history)<=degree:
        raise ValueError("Finite history longer than polynomial degree required")
    times = np.arange(1-len(history),1)*interval
    design = np.vander(times,degree+1,increasing=True)
    future = np.vander(np.arange(1,steps+1)*interval,degree+1,increasing=True)
    return future@np.linalg.lstsq(design,history,rcond=None)[0]


def _uncompressed_ridge(sequences, train_ids, fold_groups):
    """Matched five-frame ridge without output-rank truncation.

    This calls the same internal weighted numerical fit to isolate compression;
    penalties are selected within the same training-player inner partitions.
    No held-player observations enter these fits or scores.
    """
    arrays,interval,_=_validated([s for s in sequences if s.athlete_id in train_ids],0.1)
    options=[]
    for penalty in (1e-4,0.01,0.1):
        errors={}
        for fold in range(3):
            tr=[row for row in arrays if fold_groups[row[0].group]!=fold]
            te=[row for row in arrays if fold_groups[row[0].group]==fold]
            model=_fit(tr,interval,5,3,6,penalty,5,("forward_velocity_yd_s","lateral_velocity_yd_s"),
                       ("forward_velocity_yd_s","lateral_velocity_yd_s"))
            errors.update(_score(model,te))
        options.append((float(np.mean(list(errors.values()))),penalty))
    score,penalty=min(options)
    model=_fit(arrays,interval,5,3,6,penalty,5,("forward_velocity_yd_s","lateral_velocity_yd_s"),
               ("forward_velocity_yd_s","lateral_velocity_yd_s"))
    return model,score,penalty


def evaluate_predictive_state(sequences, *, seed=2718, train_fraction=0.8):
    """Frozen 0.3 s direct horizon, outer held players and nested inner selection."""
    sequences = list(sequences)
    ids = sorted({s.athlete_id for s in sequences})
    if len(ids) < 10:
        raise ValueError("At least ten distinct players required")
    rng = np.random.default_rng(seed)
    rng.shuffle(ids)
    train_ids = ids[:int(len(ids)*train_fraction)]
    fit = discover_predictive_state(sequences, train_athlete_ids=train_ids,
                                   history_steps=(1, 3, 5), ranks=(1, 2, 3, 4),
                                   ridge_penalties=(1e-4, 0.01, 0.1), horizon_steps=3,
                                   inner_folds=3, seed=seed, sample_interval=0.1,
                                   channel_names=("forward_velocity_yd_s", "lateral_velocity_yd_s"))
    uncompressed,uncompressed_score,uncompressed_penalty=_uncompressed_ridge(sequences,train_ids,fit.fold_groups)
    models = {"history": fit.model, "instantaneous": fit.instantaneous_model,"uncompressed_history_ridge":uncompressed}
    errors = {key: [] for key in (*models, "persistence","linear_trend_history5","quadratic_trend_history5","last_difference_acceleration")}
    count = 0
    for sequence in sequences:
        if sequence.athlete_id in train_ids:
            continue
        values = np.asarray(sequence.channels)
        for origin in range(4, len(values)-3):
            target = values[origin+1:origin+4]
            for key, model in models.items():
                prediction = model.forecast(values[origin-model.history_steps+1:origin+1])
                errors[key].append((sequence.athlete_id, ((prediction-target)**2).mean(axis=0)))
            errors["persistence"].append((sequence.athlete_id, ((values[origin]-target)**2).mean(axis=0)))
            for name,degree in (("linear_trend_history5",1),("quadratic_trend_history5",2)):
                prediction=history_extrapolation(values[origin-4:origin+1],degree=degree)
                errors[name].append((sequence.athlete_id,((prediction-target)**2).mean(axis=0)))
            prediction=values[origin]+np.arange(1,4)[:,None]*(values[origin]-values[origin-1])
            errors["last_difference_acceleration"].append((sequence.athlete_id,((prediction-target)**2).mean(axis=0)))
            count += 1
    metrics = {key: _player_metrics(value) for key, value in errors.items()}
    held_errors = metrics["history"]["player_mse"]
    instant_errors = metrics["instantaneous"]["player_mse"]
    players = sorted(held_errors)
    differences = np.asarray([instant_errors[p]-held_errors[p] for p in players])
    boot = [float(rng.choice(differences, len(players), replace=True).mean()) for _ in range(2000)]
    return {"protocol": "Outer unseen player; train-player-only scaling and 3-fold rank/history/penalty selection",
            "units": "yards/second", "horizon_seconds": 0.3, "origin_count": count,
            "train_players": len(train_ids), "test_players": len(players),
            "train_ids": sorted(train_ids), "test_ids": players,
            "selected": {"history_steps": fit.model.history_steps, "state_count": fit.model.state_count,
                         "ridge_penalty": fit.model.ridge_penalty},
            "inner_selected_standardized_mse": fit.selected_cv_mse,
            "inner_instantaneous_standardized_mse": fit.instantaneous_cv_mse,
            "inner_uncompressed_standardized_mse":uncompressed_score,
            "uncompressed_ridge_penalty":uncompressed_penalty,
            "outer": metrics,
            "outer_relative_mse_improvement": 1-metrics["history"]["rmse"]**2/metrics["instantaneous"]["rmse"]**2,
            "paired_player_mse_reduction_interval_95": np.quantile(boot, [0.025, 0.975]).tolist(),
            "scope": "Same-domain NFL finite-horizon movement forecast; no Combine transfer or scouting advantage established"}


def repeatability(records, *, minimum_games_per_half=2, minimum_plays_per_half=10):
    """Chronological game halves per player; same play population for each readout."""
    data = pd.DataFrame(records)
    columns = ["onset_delay", "motion_to_los", "forward_displacement_05", "path_arc_05", "forward_path_fraction_05"]
    data = data[data.usable & data.onset_post_snap].dropna(subset=columns)
    halves = defaultdict(lambda: [[], []])
    for player, rows in data.groupby("athlete_id"):
        games = sorted(rows.game_id.unique())
        if len(games) < 2*minimum_games_per_half:
            continue
        split = len(games)//2
        left, right = rows[rows.game_id.isin(games[:split])], rows[rows.game_id.isin(games[split:])]
        if min(len(left), len(right)) < minimum_plays_per_half:
            continue
        for key in columns:
            halves[key][0].append(float(left[key].mean()))
            halves[key][1].append(float(right[key].mean()))
    result = {}
    for key in columns:
        a, b = halves[key]
        result[key] = {"players": len(a), "spearman_game_half": None if len(a)<3 else float(pd.Series(a).corr(pd.Series(b),method="spearman"))}
    return {"common_support": True, "post_snap_observed_onset_only": True,
            "minimum_games_per_half": minimum_games_per_half, "minimum_plays_per_half": minimum_plays_per_half,
            "readouts": result, "scope": "Repeatability of observed game demand; not demand-standardized ability or prediction gain"}


def arrival_benchmarks(records, *, seed=2718):
    """Test the simple arrival law against held players and later NFL games.

    Nonlinear dynamics and tactical effects are allowed to falsify the law.
    All models share exact accepted-play support. Future role/pressure outcomes
    are never predictors. Temporal player effects are known-player analyses.
    """
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from scipy.sparse import hstack
    data = pd.DataFrame(records)
    data = data[data.usable & data.onset_post_snap].dropna(subset=["snap_to_los", "remaining_depth_at_onset"])
    data = data[data.remaining_depth_at_onset > 0].copy()
    data["sqrt_depth"] = np.sqrt(data.remaining_depth_at_onset)
    data["sqrt_snap_depth"] = np.sqrt(data.depth)
    ids = sorted(data.athlete_id.unique())
    np.random.default_rng(seed).shuffle(ids)
    held = set(ids[int(len(ids)*0.8):])
    plans = {"unseen_players": (~data.athlete_id.isin(held), data.athlete_id.isin(held)),
             "later_games_known_players": (data.week<=6, data.week>=7)}
    output = {}
    for name, (train_mask, test_mask) in plans.items():
        train, test = data[train_mask].copy(), data[test_mask].copy()
        if name == "later_games_known_players":
            test = test[test.athlete_id.isin(set(train.athlete_id))]
        if len(train)<10 or len(test)<10:
            continue
        # Inverse player frequency gives every training athlete equal total mass.
        count = train.athlete_id.value_counts()
        weight = np.asarray([1/count[p] for p in train.athlete_id])
        weight *= len(weight)/weight.sum()
        numeric = ["sqrt_snap_depth", "snap_width", "down", "yards_to_go", "play_action"]
        categorical = ["position_lined_up", "formation"]
        variants = {"constant": ([], []), "sqrt_snap_depth": (["sqrt_snap_depth"], []),
                    "context": (numeric, categorical)}
        if name == "later_games_known_players":
            variants["context_plus_player"] = (numeric, categorical+["athlete_id"])
            variants["context_plus_player_depth"] = (numeric, categorical+["athlete_id"])
        scores = {}
        for variant, (num, cat) in variants.items():
            if not num and not cat:
                prediction = np.repeat(np.average(train.snap_to_los,weights=weight), len(test))
                coefs = None
            else:
                preprocess = ColumnTransformer([
                    ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")),("scale", StandardScaler())]), num),
                    ("category", OneHotEncoder(handle_unknown="ignore"), cat)], remainder="drop")
                if variant == "context_plus_player_depth":
                    # Train-only player categories; random slopes for the
                    # observed-demand sqrt-distance response are ridge pooled.
                    base_train = preprocess.fit_transform(train)
                    base_test = preprocess.transform(test)
                    player_code = OneHotEncoder(handle_unknown="ignore")
                    a = player_code.fit_transform(train[["athlete_id"]])
                    b = player_code.transform(test[["athlete_id"]])
                    mean, scale = train.sqrt_snap_depth.mean(), train.sqrt_snap_depth.std(ddof=0)
                    scale = max(float(scale),1e-10)
                    a = a.multiply(((train.sqrt_snap_depth.to_numpy()-mean)/scale)[:,None])
                    b = b.multiply(((test.sqrt_snap_depth.to_numpy()-mean)/scale)[:,None])
                    xtrain, xtest = hstack([base_train,a]).tocsr(), hstack([base_test,b]).tocsr()
                    ridge = Ridge(alpha=10.0,solver="lsqr")
                    ridge.fit(xtrain,train.snap_to_los,sample_weight=weight)
                    prediction = ridge.predict(xtest)
                    coefs = {"scaled_intercept":float(ridge.intercept_),
                             "numeric_scaled_coefficients":ridge.coef_[:len(num)].tolist(),
                             "player_depth_slope_count":int(a.shape[1]),
                             "training_depth_range_yards":[float(train.depth.min()),float(train.depth.max())]}
                else:
                    model = Pipeline([("preprocess", preprocess), ("ridge", Ridge(alpha=10.0,solver="lsqr"))])
                    model.fit(train, train.snap_to_los, ridge__sample_weight=weight)
                    prediction = model.predict(test)
                    coefs = {"scaled_intercept":float(model['ridge'].intercept_),
                             "numeric_scaled_coefficients": model['ridge'].coef_[:len(num)].tolist()}
            per_player = test.assign(square_error=(prediction-test.snap_to_los)**2).groupby("athlete_id").square_error.mean()
            scores[variant] = {"equal_player_rmse_seconds": float(np.sqrt(per_player.mean())),
                               "equal_play_rmse_seconds": float(np.sqrt(np.mean((prediction-test.snap_to_los)**2))),
                               "coefficients": coefs}
        # A stronger falsification conditions on the *observed* onset. This is
        # an NFL mechanism diagnostic, never a deployable pre-snap predictor.
        x = train.sqrt_depth.to_numpy()
        y = train.motion_to_los.to_numpy()
        design = np.column_stack([np.ones(len(x)),x])
        beta = np.linalg.solve(design.T@(weight[:,None]*design)+1e-8*np.eye(2), design.T@(weight*y))
        predicted = test.onset_delay.to_numpy()+beta[0]+beta[1]*test.sqrt_depth.to_numpy()
        residual = predicted-test.snap_to_los.to_numpy()
        per_player = test.assign(square_error=residual**2).groupby("athlete_id").square_error.mean()
        scores["observed_onset_plus_sqrt_remaining_depth_diagnostic"] = {
            "equal_player_rmse_seconds":float(np.sqrt(per_player.mean())),
            "intercept_seconds":float(beta[0]), "sqrt_distance_coefficient":float(beta[1]),
            "deployment_feature":False}
        strict_beta = float(np.sum(weight*x*y)/np.sum(weight*x*x))
        strict_prediction = test.onset_delay.to_numpy()+strict_beta*test.sqrt_depth.to_numpy()
        strict_errors = test.assign(square_error=(strict_prediction-test.snap_to_los)**2).groupby("athlete_id").square_error.mean()
        scores["observed_onset_plus_zero_intercept_sqrt_depth_diagnostic"] = {
            "equal_player_rmse_seconds":float(np.sqrt(strict_errors.mean())),
            "sqrt_distance_coefficient":strict_beta,
            "effective_acceleration_yards_s2":2/strict_beta**2,
            "deployment_feature":False,
            "assumptions":"Common constant acceleration after observed onset and negligible initial forward speed"}
        output[name] = {"train_plays":len(train),"test_plays":len(test),
                        "train_players":int(train.athlete_id.nunique()),"test_players":int(test.athlete_id.nunique()),
                        "scores":scores,"penalty":10.0,"penalty_selected_on_test":False}
    return {"tests":output, "selection_scope":"Complete observed LOS crossings with post-snap onset; censored/noncrossing rushes are not imputed",
            "model_scope":"Conditional-on-crossing NFL timing. This does not establish Combine-to-NFL transfer or full pass-rush value."}
