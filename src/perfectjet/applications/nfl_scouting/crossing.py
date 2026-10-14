"""Separate a tracked motion-onset proxy from travel to the line of scrimmage.

NFL observations define targets here; nothing in this module is a Combine-only
predictor.  The onset is an explicitly thresholded tracking measurement, not a
physiological reaction time.  The line is perpendicular to ``axis`` and ``direction``
points toward it.  Distances and positions must share units, and times are seconds.

The constant-acceleration equation is a declared local model, not a claim that a
pass rusher accelerates constantly.  Its interval calculation brackets its roots
using exact rational sign checks on the supplied binary64 endpoints.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from math import hypot, isfinite, nextafter, inf

from ...readout import identify

EXTRACTION_VERSION = "nfl-crossing-2"


def _number(value, name):
    out = float(value)
    if not isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def travel_time(distance, initial_speed, acceleration):
    """Stable nonnegative root of d = v*t + a*t^2/2, for d,v>=0 and a>0.

    The form 2d/(v+sqrt(v^2+2ad)) avoids subtracting nearly equal quantities.
    Decimal intermediates also avoid overflow when a float discriminant would
    overflow despite a representable travel time. The returned point is rounded;
    use ``travel_time_bounds`` for an outward, polynomial-checked bracket.
    """
    d, v, a = (_number(distance, "distance"), _number(initial_speed, "initial_speed"),
               _number(acceleration, "acceleration"))
    if d < 0 or v < 0 or a <= 0:
        raise ValueError("distance and initial_speed must be nonnegative; acceleration must be positive")
    if d == 0:
        return 0.0
    with localcontext() as context:
        context.prec = 80
        dd, vv, aa = map(Decimal.from_float, (d, v, a))
        root = (2*dd)/(vv+(vv*vv+2*aa*dd).sqrt())
        out = float(root)
    if not isfinite(out):
        raise ValueError("travel time is outside the representable float range")
    return out


def _interval(value, name, strictly_positive=False):
    if len(value) != 2:
        raise ValueError(f"{name} requires a lower and upper endpoint")
    lo, hi = (_number(value[0], name), _number(value[1], name))
    if lo > hi or lo < 0 or (strictly_positive and lo <= 0):
        raise ValueError(f"invalid {name} interval")
    return lo, hi


def _root_bracket(d, v, a):
    """Outward bracket, justified by exact signs of a*t^2+2v*t-2d."""
    guess = travel_time(d, v, a)
    dd, vv, aa = map(Q.from_float, (d, v, a))

    def residual(t):
        tt = Q.from_float(t)
        return aa*tt*tt+2*vv*tt-2*dd

    lo = hi = guess
    for _ in range(64):
        if residual(lo) <= 0:
            break
        lo = nextafter(lo, -inf)
    else:
        raise ArithmeticError("could not establish a lower travel-time bound")
    for _ in range(64):
        if residual(hi) >= 0:
            break
        hi = nextafter(hi, inf)
        if not isfinite(hi):
            raise ValueError("upper travel-time bound is not representable")
    else:
        raise ArithmeticError("could not establish an upper travel-time bound")
    return lo, hi


def travel_time_bounds(distance, initial_speed, acceleration):
    """Sharp endpoint bounds over a declared independent box.

    Travel time increases with distance and decreases with initial speed and
    acceleration. Hence extrema occur at (d_lo,v_hi,a_hi) and (d_hi,v_lo,a_lo).
    This encloses the constant-acceleration model for every point in the box; it
    is not an empirical sensor confidence interval or a physiological guarantee.
    """
    dl, dh = _interval(distance, "distance")
    vl, vh = _interval(initial_speed, "initial_speed")
    al, ah = _interval(acceleration, "acceleration", strictly_positive=True)
    lo = _root_bracket(dl, vh, ah)[0]
    hi = _root_bracket(dh, vl, al)[1]
    return {"lower": lo, "upper": hi,
            "minimum_corner": (dl, vh, ah), "maximum_corner": (dh, vl, al),
            "endpoint_polynomial_signs_checked_exactly": True,
            "model": "d = v*t + a*t^2/2; independent nonnegative d,v box and positive a box"}


def los_confounding_receipt(distance=Q(1), initial_speed=Q(0), total_time=Q(1),
                            onset_pair=(Q(1, 5), Q(3, 10))):
    """Exact additive witness plus two distinct constant-acceleration explanations.

    Row-space analysis applies to the linear variables (onset, travel), not to
    acceleration. The two accelerations below are a separate nonlinear
    counterexample: the same observed LOS time does not uniquely determine them.
    """
    d, v, total = map(Q, (distance, initial_speed, total_time))
    if d <= 0 or v < 0 or total <= 0 or len(onset_pair) != 2:
        raise ValueError("positive distance/time, nonnegative speed and two onsets required")
    explanations = []
    for onset in map(Q, onset_pair):
        travel = total-onset
        if onset < 0 or travel <= 0 or d-v*travel <= 0:
            raise ValueError("onset does not admit positive travel time and acceleration")
        acceleration = 2*(d-v*travel)/(travel*travel)
        assert onset+travel == total
        assert v*travel+acceleration*travel*travel/2 == d
        explanations.append({"onset": onset, "travel": travel, "acceleration": acceleration,
                             "snap_to_los": total})
    if explanations[0]["onset"] == explanations[1]["onset"]:
        raise ValueError("two distinct onsets are required")
    return {"observation_design": [[Q(1), Q(1)]],
            "onset_identification": identify([[1, 1]], [1, 0]),
            "travel_identification": identify([[1, 1]], [0, 1]),
            "nonlinear_explanations": explanations,
            "identities_replayed": True,
            "scope": "linear witness concerns onset plus travel; acceleration nonuniqueness is exhibited separately"}


def _interpolate(times, values, when):
    if when < times[0] or when > times[-1]:
        return None, None
    for i, t in enumerate(times):
        if when == t:
            return values[i], (i, i)
        if t > when:
            left = i-1
            weight = (when-times[left])/(t-times[left])
            return values[left]+weight*(values[i]-values[left]), (left, i)
    return values[-1], (len(times)-1, len(times)-1)


def extract_crossing(frames_or_attempt, snap_time, distance_los, direction=1, axis=(1.0, 0.0),
                     velocity_threshold=0.5, sustained_frames=3, minimum_progress=0.05,
                     post_onset_horizon=0.5, maximum_gap=0.15, pre_snap_window=0.3,
                     maximum_post_snap=2.0, reversal_tolerance=0.10):
    """Tracking-only decomposition of snap-to-LOS into onset delay and travel.

    A motion run needs ``sustained_frames`` consecutive forward displacement
    intervals above the velocity threshold and the specified net progress.
    Its onset is the first interval's left timestamp: a frame-resolution proxy.
    LOS crossing is linearly interpolated between the first crossing pair.
    Significant recrossings, missing intervals in the relevant window, and
    absent onset/crossing observations make the primary decomposition unusable.
    Anticipation is retained and flagged rather than clamped into reaction time.
    ``post_onset_displacement`` measures forward travel over a fixed horizon.
    """
    snap = _number(snap_time, "snap_time")
    distance = _number(distance_los, "distance_los")
    if distance < 0 or direction not in (-1, 1):
        raise ValueError("distance_los must be nonnegative and direction must be -1 or 1")
    if velocity_threshold <= 0 or sustained_frames < 1 or minimum_progress < 0:
        raise ValueError("positive velocity threshold/frame count and nonnegative progress required")
    if post_onset_horizon <= 0 or maximum_gap <= 0 or pre_snap_window < 0 or maximum_post_snap <= 0:
        raise ValueError("invalid extraction horizons")
    ax, ay = (_number(axis[0], "axis"), _number(axis[1], "axis"))
    length = hypot(ax, ay)
    if length == 0:
        raise ValueError("axis must be nonzero")
    ax, ay = ax/length, ay/length
    frames = list(getattr(frames_or_attempt, "frames", frames_or_attempt))
    result = {"usable": False, "usable_for_post_snap_onset": False, "flags": [],
              "snap_time": snap, "motion_onset_time": None, "onset_delay": None,
              "los_crossing_time": None, "snap_to_los": None, "motion_to_los": None,
              "post_onset_displacement": None, "post_onset_horizon": post_onset_horizon,
              "crossing_interpolation_interval": None, "reconstruction_identity_error": None,
              "anticipation_or_moving_at_snap": False, "reaction_time_interpretation": False,
              "extraction_version": EXTRACTION_VERSION,
              "assumptions": {"velocity_threshold": velocity_threshold, "sustained_frames": sustained_frames,
                              "minimum_progress": minimum_progress, "maximum_gap": maximum_gap,
                              "axis": (ax, ay), "direction": direction, "distance_los": distance,
                              "onset_definition": "left edge of sustained forward-velocity run with an observed preceding below-threshold interval"}}
    if len(frames) < 2:
        result["flags"].append("insufficient_frames")
        return result
    try:
        times = [_number(f.t, "frame time") for f in frames]
        positions = [direction*(_number(f.x, "x")*ax+_number(f.y, "y")*ay) for f in frames]
    except (ValueError, TypeError, AttributeError):
        result["flags"].append("invalid_frames")
        return result
    if any(b <= a for a, b in zip(times, times[1:])):
        result["flags"].append("nonincreasing_frame_times")
        return result
    at_snap, snap_pair = _interpolate(times, positions, snap)
    if at_snap is None:
        result["flags"].append("snap_outside_tracking")
        return result
    progress = [p-at_snap for p in positions]
    if snap_pair[0] != snap_pair[1] and times[snap_pair[1]]-times[snap_pair[0]] > maximum_gap+1e-9:
        result["flags"].append("snap_in_missing_interval")
    if times[0] >= snap:
        result["flags"].append("pre_snap_motion_unobserved")
    velocity = [(b-a)/(tb-ta) for a, b, ta, tb in zip(progress, progress[1:], times, times[1:])]
    onset_index = None
    for i in range(len(velocity)-sustained_frames+1):
        if times[i] < snap-pre_snap_window-1e-9 or times[i] > snap+maximum_post_snap:
            continue
        if (all(v >= velocity_threshold for v in velocity[i:i+sustained_frames])
                and progress[i+sustained_frames]-progress[i] >= minimum_progress):
            # The beginning of an allowed scan window is not an observed
            # threshold transition. If motion was already active in the prior
            # interval (or no prior interval exists), onset is left censored;
            # do not manufacture one at that window boundary or seek a later
            # more favorable start. Crossing itself remains observable.
            if i == 0 or velocity[i-1] >= velocity_threshold:
                result["flags"].append("onset_left_censored")
                result["anticipation_or_moving_at_snap"] = times[i] <= snap
                break
            onset_index = i
            break
    if onset_index is None:
        result["flags"].append("motion_onset_not_observed")
    else:
        onset = times[onset_index]
        result["motion_onset_time"] = onset
        result["onset_delay"] = onset-snap
        result["anticipation_or_moving_at_snap"] = onset <= snap
        if onset <= snap:
            result["flags"].append("onset_at_or_before_snap")
        end_progress, end_pair = _interpolate(times, progress, onset+post_onset_horizon)
        if end_progress is None:
            result["flags"].append("post_onset_horizon_unobserved")
        else:
            result["post_onset_displacement"] = end_progress-progress[onset_index]

    crossing_pair = None
    crossing = snap if distance == 0 else None
    if distance == 0:
        result["flags"].append("at_los_at_snap")
    else:
        for i in range(len(times)-1):
            if times[i+1] < snap or times[i] > snap+maximum_post_snap:
                continue
            left_time, left_progress = max(snap, times[i]), progress[i]
            if times[i] < snap:
                left_progress = 0.0
            if left_progress < distance <= progress[i+1]:
                weight = (distance-left_progress)/(progress[i+1]-left_progress)
                candidate = left_time+weight*(times[i+1]-left_time)
                if candidate > snap+maximum_post_snap+1e-9:
                    continue
                crossing = candidate
                crossing_pair = (i, i+1)
                break
        if crossing is None:
            result["flags"].append("los_crossing_not_observed")
    if crossing is not None:
        result["los_crossing_time"] = crossing
        result["snap_to_los"] = crossing-snap
        if crossing_pair:
            result["crossing_interpolation_interval"] = (times[crossing_pair[0]], times[crossing_pair[1]])
            if times[crossing_pair[1]]-times[crossing_pair[0]] > maximum_gap+1e-9:
                result["flags"].append("crossing_in_missing_interval")
            # Ignore sub-tolerance wobble at the line, but reject a meaningful
            # return behind it within the declared extraction window.
            after = [p for t, p in zip(times, progress) if crossing <= t <= snap+maximum_post_snap]
            crossed_far = False
            for p in after:
                crossed_far = crossed_far or p >= distance+reversal_tolerance
                if crossed_far and p < distance-reversal_tolerance:
                    result["flags"].append("significant_los_recrossing")
                    break
        if onset_index is not None:
            onset = result["motion_onset_time"]
            if crossing < onset:
                result["flags"].append("crossing_precedes_detected_onset")
            else:
                result["motion_to_los"] = crossing-onset
                result["reconstruction_identity_error"] = abs(
                    result["onset_delay"]+result["motion_to_los"]-result["snap_to_los"])

    if onset_index is not None:
        end_time = max(result["motion_onset_time"]+post_onset_horizon, crossing or snap)
        start_time = min(snap, result["motion_onset_time"])
        if any(b-a > maximum_gap+1e-9 for a, b in zip(times, times[1:])
               if b > start_time and a < end_time):
            result["flags"].append("missing_interval_in_decomposition")
        if crossing is not None and any(progress[i+1]-progress[i] < -reversal_tolerance
                                       for i in range(len(times)-1)
                                       if result["motion_onset_time"] <= times[i] < crossing):
            result["flags"].append("significant_pre_crossing_reversal")
    fatal = {"snap_in_missing_interval", "motion_onset_not_observed", "onset_left_censored", "post_onset_horizon_unobserved",
             "at_los_at_snap", "los_crossing_not_observed", "crossing_in_missing_interval",
             "significant_los_recrossing", "crossing_precedes_detected_onset",
             "missing_interval_in_decomposition", "significant_pre_crossing_reversal"}
    result["usable"] = not bool(fatal.intersection(result["flags"]))
    result["usable_for_post_snap_onset"] = (result["usable"] and result["onset_delay"] > 0
                                             and "pre_snap_motion_unobserved" not in result["flags"])
    return result
