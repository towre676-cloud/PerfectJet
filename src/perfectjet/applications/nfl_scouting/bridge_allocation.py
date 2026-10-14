"""Connect a frozen fitted movement/get-off loading to exact measurement planning.

The supplied loading is a conditional fitted-model derivative, potentially a
local Jacobian of source features -> NFL movement -> get-off. It is not a
physiological law. Rationalization makes the finite allocation arithmetic
replayable; it does not make the learned loading exactly true.

The wrapper preserves provenance, checks declared training/evaluation separation,
records every coefficient's rationalization error, and bounds how much rounding
can change the finite-package objective. Correlated channels from one attempt
must be provided as MeasurementBlockCandidate, with their joint noise covariance.
"""
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from fractions import Fraction as Q
from hashlib import sha256
import json
from numbers import Integral

from .allocation import (
    MAX_EXACT_CANDIDATES, TargetInformationModel, allocate_contenders,
)

LOADING_SCHEMA = "pj-nfl-fitted-loading/1"


def _q(value):
    if isinstance(value, Q):
        return value
    if isinstance(value, Integral):
        return Q(int(value))
    try:
        return Q(str(value))
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError("finite numeric fitted loading coefficients are required") from exc


def _ids(values, name):
    ids = []
    for value in values:
        text = str(value).strip()
        if not text or text.lower() in ("none", "nan", "inf", "+inf", "-inf", "infinity"):
            raise ValueError(f"{name} must contain distinct, nonempty athlete IDs")
        # CSV joins can turn an integral NFL ID into 123.0; canonicalize that
        # spelling so floating/integer/string variants cannot conceal leakage.
        try:
            number = Q(text)
            if number.denominator == 1:
                text = str(number.numerator)
        except (ValueError, ZeroDivisionError):
            pass
        ids.append(text)
    ids = tuple(ids)
    if len(set(ids)) != len(ids):
        raise ValueError(f"{name} must contain distinct, nonempty athlete IDs")
    return ids


def _cutoff(value):
    if isinstance(value, Integral) and not isinstance(value, bool):
        kind, result = "NFL season", int(value)
        if not 1900 <= result <= 3000:
            raise ValueError("season cutoff must be a plausible four-digit year")
        return kind, result
    text = str(value)
    if len(text) == 4 and text.isdigit():
        return _cutoff(int(text))
    try:
        return "calendar date", date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError("outcome cutoff must be an NFL season year or ISO calendar date") from exc


@dataclass(frozen=True)
class FrozenTrainingReceipt:
    """Caller-provided lineage for the fitted loading, copied and checked.

    An integer cutoff means maximum NFL season, not December 31 of that year.
    An ISO date denotes a calendar-date cutoff. Optional latest_training_outcome
    must use the same convention and cannot exceed the cutoff. This record is
    auditable provenance, not independent verification of the training data.
    """
    training_athlete_ids: tuple
    outcome_cutoff: object
    held_out_athlete_ids: tuple = ()
    model_id: str = "caller-declared frozen fitted bridge"
    loading_source: str = "conditional fitted source-to-movement-to-getoff Jacobian"
    latest_training_outcome: object = None

    def __post_init__(self):
        training = _ids(self.training_athlete_ids, "training_athlete_ids")
        held = _ids(self.held_out_athlete_ids, "held_out_athlete_ids")
        if not training:
            raise ValueError("the frozen loading needs nonempty training_athlete_ids")
        if set(training).intersection(held):
            raise ValueError("held-out athletes cannot be used to learn the frozen loading")
        kind, cutoff = _cutoff(self.outcome_cutoff)
        if self.latest_training_outcome is not None:
            latest_kind, latest = _cutoff(self.latest_training_outcome)
            if latest_kind != kind or latest > cutoff:
                raise ValueError("latest training outcome must respect the declared cutoff convention")
        if not str(self.model_id).strip() or not str(self.loading_source).strip():
            raise ValueError("model_id and loading_source must be explicit")
        object.__setattr__(self, "training_athlete_ids", training)
        object.__setattr__(self, "held_out_athlete_ids", held)
        object.__setattr__(self, "outcome_cutoff", cutoff if kind == "NFL season" else cutoff.isoformat())
        if self.latest_training_outcome is not None:
            object.__setattr__(self, "latest_training_outcome",
                               latest if kind == "NFL season" else latest.isoformat())
        object.__setattr__(self, "model_id", str(self.model_id))
        object.__setattr__(self, "loading_source", str(self.loading_source))

    def audit(self, evaluation_athlete_ids=()):
        evaluation = _ids(evaluation_athlete_ids, "evaluation_athlete_ids")
        if set(self.training_athlete_ids).intersection(evaluation):
            raise ValueError("evaluated athletes cannot be in the frozen loading's training set")
        kind, _ = _cutoff(self.outcome_cutoff)
        receipt = {"schema": LOADING_SCHEMA,
                   "model_id": self.model_id, "loading_source": self.loading_source,
                   "training_athlete_ids": self.training_athlete_ids,
                   "held_out_athlete_ids": self.held_out_athlete_ids,
                   "evaluation_athlete_ids": evaluation,
                   "outcome_cutoff": self.outcome_cutoff, "cutoff_kind": kind,
                   "latest_training_outcome": self.latest_training_outcome,
                   "declared_training_evaluation_disjointness_checked": True,
                   "latest_training_outcome_checked": self.latest_training_outcome is not None,
                   "training_chronology_independently_verified": False}
        receipt["receipt_sha256"] = sha256(json.dumps(receipt, sort_keys=True,
                                                      separators=(",", ":")).encode()).hexdigest()
        return receipt


def _training_receipt(value):
    if isinstance(value, FrozenTrainingReceipt):
        return value
    if isinstance(value, Mapping):
        return FrozenTrainingReceipt(**dict(value))
    raise TypeError("an auditable FrozenTrainingReceipt or matching mapping is required")


def rationalize_fitted_loading(loadings, max_denominator=10**9, max_abs_error="1e-9"):
    """Rational snapshot of numeric H, with explicit per-coefficient error receipts."""
    if isinstance(max_denominator, bool) or not isinstance(max_denominator, Integral) or max_denominator < 1:
        raise ValueError("max_denominator must be a positive integer")
    tolerance = _q(max_abs_error)
    if tolerance < 0:
        raise ValueError("max_abs_error must be nonnegative")
    rows = tuple(loadings)
    if not rows:
        raise ValueError("at least one frozen fitted loading is required")
    if not isinstance(rows[0], Iterable) or isinstance(rows[0], (str, bytes)):
        rows = (rows,)
    snapshots = tuple(tuple(_q(value) for value in row) for row in rows)
    width = len(snapshots[0])
    if not width or any(len(row) != width for row in snapshots):
        raise ValueError("loading rows must be a nonempty rectangular matrix")
    rational = tuple(tuple(value.limit_denominator(int(max_denominator)) for value in row)
                     for row in snapshots)
    errors = tuple(tuple(abs(a - b) for a, b in zip(raw, rounded))
                   for raw, rounded in zip(snapshots, rational))
    if any(error > tolerance for row in errors for error in row):
        raise ValueError("the requested denominator limit cannot meet the loading error tolerance")
    return {"schema": LOADING_SCHEMA, "original_decimal_snapshot": snapshots,
            "rational_loadings": rational, "coefficient_absolute_errors": errors,
            "max_denominator": int(max_denominator), "max_abs_error": tolerance,
            "largest_absolute_error": max(error for row in errors for error in row),
            "interpretation": "exact allocation for a declared rational approximation of a conditional fitted loading",
            "exact_learned_truth_claim": False}


def _uniform_objective_error(source_covariance, raw, rounded, weights, objective):
    """Exact error bound for every measurement package, including unselected ones.

    Its covariance reduction D satisfies 0 <= D <= S. Consequently
    |D_ij| <= sqrt(S_ii S_jj) <= (S_ii+S_jj)/2. Apply that rational bound
    to h_i h_j - q_i q_j, then combine rows by weighted mean or minimum.
    """
    row_bounds = tuple(sum((abs(a[i] * a[j] - b[i] * b[j])
                           * (source_covariance[i][i] + source_covariance[j][j]) / 2
                           for i in range(len(a)) for j in range(len(a))), Q(0))
                       for a, b in zip(raw, rounded))
    if objective == "worst_target":
        bound = max(row_bounds)
    else:
        total = sum(weights, Q(0))
        bound = sum((w * value for w, value in zip(weights, row_bounds)), Q(0)) / total if total else Q(0)
    return {"per_loading_uniform_objective_error_bounds": row_bounds,
            "uniform_objective_error_bound": bound,
            "original_snapshot_optimality_gap_bound": 2 * bound,
            "scope": "rationalization error only, over the declared finite package population",
            "proof": "0 <= covariance reduction <= source posterior covariance; "
                     "quantized optimal selection has original-snapshot regret at most twice the uniform score error"}


def _models(frozen_loadings, prior_covariance, receipt, evaluation_athlete_ids,
            design, noise_variance, observation_ids, target_weights, target_ids,
            max_denominator, max_abs_error):
    audit = _training_receipt(receipt).audit(evaluation_athlete_ids)
    rationalization = rationalize_fitted_loading(frozen_loadings, max_denominator, max_abs_error)
    # Snapshot generators too: both rational and original-decimal models must
    # see exactly the same observations, weights and identities.
    design = tuple(tuple(row) for row in design)
    if isinstance(noise_variance, Iterable) and not isinstance(noise_variance, (str, bytes)):
        noise_variance = tuple(noise_variance)
    observation_ids = tuple(observation_ids) if observation_ids is not None else None
    target_weights = tuple(target_weights) if target_weights is not None else None
    target_ids = tuple(target_ids) if target_ids is not None else None
    common = dict(design=design, noise_variance=noise_variance,
                  observation_ids=observation_ids, target_weights=target_weights,
                  target_ids=target_ids, training_receipt=audit["receipt_sha256"])
    model = TargetInformationModel(prior_covariance, rationalization["rational_loadings"], **common)
    raw_model = TargetInformationModel(model.prior_covariance, rationalization["original_decimal_snapshot"], **common)
    return model, raw_model, rationalization, audit


def plan_from_fitted_loading(frozen_loadings, prior_covariance, candidates, budget,
                             training_receipt, *, objective="worst_target",
                             max_denominator=10**9, max_abs_error="1e-9",
                             evaluation_athlete_ids=(), design=(), noise_variance=1,
                             observation_ids=None, target_weights=None,
                             max_candidates=MAX_EXACT_CANDIDATES):
    """Plan measurements from frozen fitted source-to-football loading hypotheses.

    Several H rows represent explicitly supplied training/refit hypotheses for
    worst_target planning, not a statistical confidence region. Costs, source
    covariance and measurement-noise models are caller supplied. Nothing here
    fits H on evaluated athletes, invents new observations or claims NFL lift.
    """
    candidates = tuple(candidates)
    model, raw_model, rationalization, audit = _models(
        frozen_loadings, prior_covariance, training_receipt, evaluation_athlete_ids,
        design, noise_variance, observation_ids, target_weights, None,
        max_denominator, max_abs_error)
    plan = model.optimize_package(candidates, budget, max_candidates, objective)
    selected = tuple(candidate for candidate in candidates if candidate.candidate_id in plan["candidate_ids"])
    raw_package = raw_model.package_information(selected)
    raw_score = raw_model._objective(raw_package["source_covariance_after"], objective)
    rounding = _uniform_objective_error(model.source_covariance,
                                       raw_model.target_loadings, model.target_loadings,
                                       model.target_weights, objective)
    return {"allocation": plan, "training": audit, "rationalization": rationalization,
            "rationalization_guarantee": rounding,
            "original_snapshot_selected_objective": raw_score,
            "selected_objective_rationalization_difference": plan["objective_reduction"] - raw_score,
            "loading_scope": "conditional fitted-model loading or local Jacobian; not a physiological law",
            "covariance_scope": "caller-provided source covariance and attempt-noise model",
            "evidence_scope": "conditional measurement planning, not established NFL scouting advantage"}


def plan_contender_measurements(frozen_loadings, prior_covariance, candidates, budget,
                                training_receipt, scenario_bounds, target_ids, *,
                                empirical_uncertainty=None, maximize=True,
                                objective="worst_target", max_denominator=10**9,
                                max_abs_error="1e-9", design=(), noise_variance=1,
                                observation_ids=None,
                                max_candidates=MAX_EXACT_CANDIDATES):
    """Use per-athlete frozen loadings to plan unresolved prospect comparisons.

    Compared players are checked against declared training IDs. This wrapper's
    worst_target means worst unresolved comparison; refit-hypothesis planning
    uses plan_from_fitted_loading instead. Supplied scenario bounds stay distinct
    from empirical uncertainty and are not assigned a confidence level.
    """
    candidates = tuple(candidates)
    model, raw_model, rationalization, audit = _models(
        frozen_loadings, prior_covariance, training_receipt, scenario_bounds.keys(),
        design, noise_variance, observation_ids, None, target_ids,
        max_denominator, max_abs_error)
    result = allocate_contenders(model, candidates, budget, scenario_bounds,
                                 empirical_uncertainty, maximize, max_candidates, objective)
    index = {athlete: i for i, athlete in enumerate(model.target_ids)}
    pairs = result["comparison_pairs"]
    raw_rows = [tuple(a - b for a, b in zip(raw_model.target_loadings[index[left]],
                                          raw_model.target_loadings[index[right]]))
                for left, right in pairs]
    rounded_rows = [tuple(a - b for a, b in zip(model.target_loadings[index[left]],
                                              model.target_loadings[index[right]]))
                    for left, right in pairs]
    if not pairs:
        raw_rows = rounded_rows = [(Q(0),) * model.width]
    weights = (Q(1, len(raw_rows)),) * len(raw_rows)
    raw_comparison = TargetInformationModel(model.prior_covariance, raw_rows,
                                            design=model.design,
                                            noise_variance=model.observation_noise_variances,
                                            observation_ids=model.observation_ids,
                                            target_weights=weights,
                                            training_receipt=audit["receipt_sha256"])
    selected_ids = result["allocation"]["candidate_ids"]
    selected = tuple(candidate for candidate in candidates if candidate.candidate_id in selected_ids)
    raw_package = raw_comparison.package_information(selected)
    raw_score = raw_comparison._objective(raw_package["source_covariance_after"], objective)
    rounding = _uniform_objective_error(model.source_covariance, raw_rows, rounded_rows, weights, objective)
    return {"decision_allocation": result, "training": audit, "rationalization": rationalization,
            "rationalization_guarantee": rounding,
            "original_snapshot_selected_objective": raw_score,
            "selected_objective_rationalization_difference": result["allocation"]["objective_reduction"] - raw_score,
            "loading_scope": "conditional fitted-model loading or local Jacobian; not a physiological law",
            "evidence_scope": "conditional comparison planning; scenario settlement requires observed results "
                              "and recomputed valid bounds"}


def plan_from_bridge_fit(fit_result, prior_covariance, candidates, budget, *,
                         training_receipt=None, objective="worst_target",
                         max_denominator=10**9, max_abs_error="1e-9",
                         jacobian_abs_tolerance="1e-9", jacobian_relative_tolerance="1e-9",
                         design=(), noise_variance=1, observation_ids=None,
                         max_candidates=MAX_EXACT_CANDIDATES):
    """Consume the actual bridges.fit_split result without overriding its loading.

    The supplied source covariance and measurement rows must use the returned
    source_feature_order. This helper checks the frozen composition h=wF and
    audited training/evaluation IDs. fit_split's year is an *exclusive* NFL-season
    cutoff; absent an explicit inclusive receipt, the maximum included season is
    year-1. Synthetic fits remain labeled mathematical fixtures.
    """
    if not isinstance(fit_result, Mapping):
        raise TypeError("a frozen bridges.fit_split result mapping is required")
    jacobian = fit_result.get("frozen_jacobian")
    audit = fit_result.get("full_stage_audit")
    if not isinstance(jacobian, Mapping) or not isinstance(audit, Mapping):
        raise ValueError("fit needs frozen_jacobian and full_stage_audit records")
    try:
        feature_names = tuple(str(value) for value in jacobian["source_features"])
        h = tuple(_q(value) for value in jacobian["source_to_outcome"])
        w = tuple(_q(value) for value in jacobian["movement_to_outcome"])
        source_to_movement = tuple(tuple(_q(value) for value in row)
                                   for row in jacobian["source_to_movement"])
        training_ids = _ids(audit["training_ids"], "fit training_ids")
    except (KeyError, TypeError) as exc:
        raise ValueError("fit lacks complete physical Jacobian or training-ID provenance") from exc
    if not feature_names or len(set(feature_names)) != len(feature_names) or len(feature_names) != len(h):
        raise ValueError("distinct source feature labels must match the frozen outcome loading width")
    if not w or len(source_to_movement) != len(w) or any(len(row) != len(h) for row in source_to_movement):
        raise ValueError("frozen movement/output Jacobian dimensions do not compose")
    atol, rtol = _q(jacobian_abs_tolerance), _q(jacobian_relative_tolerance)
    if atol < 0 or rtol < 0:
        raise ValueError("Jacobian composition tolerances must be nonnegative")
    composed = tuple(sum((w[k] * source_to_movement[k][j] for k in range(len(w))), Q(0))
                     for j in range(len(h)))
    errors = tuple(abs(a - b) for a, b in zip(h, composed))
    tolerances = tuple(atol + rtol * abs(value) for value in composed)
    if any(error > tolerance for error, tolerance in zip(errors, tolerances)):
        raise ValueError("frozen source_to_outcome loading disagrees with movement_to_outcome @ source_to_movement")
    evaluated = tuple(dict.fromkeys(_ids(audit.get("evaluated_ids", ()), "fit evaluated_ids")
                                    + _ids(fit_result.get("ids", ()), "fit ids")))
    if set(training_ids).intersection(evaluated):
        raise ValueError("evaluated IDs overlap the fitted loading's training IDs")
    training_groups = _ids(audit.get("training_group_ids", ()), "fit training_group_ids")
    evaluated_groups = _ids(audit.get("evaluated_group_ids", ()), "fit evaluated_group_ids")
    if set(training_groups).intersection(set(evaluated_groups) | set(evaluated)):
        raise ValueError("evaluated athletes overlap the fitted loading's original training groups")
    allowed_training = set(training_ids) | set(training_groups)
    for key in ("state_training_ids", "movement_training_ids"):
        ids = _ids(audit.get(key, ()), key)
        if not set(ids).issubset(allowed_training):
            raise ValueError(f"{key} includes an athlete outside the declared training split")
    exclusive = fit_result.get("year")
    if not isinstance(exclusive, Integral) or isinstance(exclusive, bool):
        raise ValueError("fit.year must declare the exclusive NFL-season cutoff")
    exclusive = int(exclusive)
    if jacobian.get("training_cutoff_exclusive", exclusive) != exclusive:
        raise ValueError("frozen Jacobian cutoff disagrees with the fit's exclusive cutoff")
    supplied_receipt = (training_receipt if training_receipt is not None
                        else jacobian.get("training_receipt", fit_result.get("training_receipt")))
    if supplied_receipt is not None:
        supplied = _training_receipt(supplied_receipt)
        declared_training = set(supplied.training_athlete_ids)
        if declared_training != set(training_ids) and (not training_groups or declared_training != set(training_groups)):
            raise ValueError("supplied training receipt does not match fitted training IDs or original training groups")
        kind, cutoff = _cutoff(supplied.outcome_cutoff)
        if kind != "NFL season" or cutoff >= exclusive:
            raise ValueError("inclusive loading receipt must respect the fit's exclusive NFL-season cutoff")
        receipt = FrozenTrainingReceipt(supplied.training_athlete_ids, cutoff,
                                        tuple(dict.fromkeys(supplied.held_out_athlete_ids + evaluated_groups + evaluated)),
                                        supplied.model_id, supplied.loading_source,
                                        supplied.latest_training_outcome)
        conversion = "explicit supplied inclusive NFL-season receipt"
    else:
        inclusive = audit.get("outcome_cutoff", fit_result.get("outcome_cutoff", exclusive - 1))
        kind, cutoff = _cutoff(inclusive)
        if kind != "NFL season" or cutoff >= exclusive:
            raise ValueError("inclusive outcome cutoff contradicts the fit's exclusive NFL-season cutoff")
        receipt = FrozenTrainingReceipt(training_groups or training_ids, cutoff,
                                        tuple(dict.fromkeys(evaluated_groups + evaluated)),
                                        model_id="bridges.fit_split frozen physical movement bridge",
                                        loading_source="frozen_jacobian.source_to_outcome = movement_to_outcome @ source_to_movement",
                                        latest_training_outcome=audit.get("latest_training_outcome"))
        conversion = ("explicit fit/audit inclusive outcome cutoff" if "outcome_cutoff" in audit or "outcome_cutoff" in fit_result
                      else "maximum included NFL season = exclusive fit.year - 1")
    result = plan_from_fitted_loading(h, prior_covariance, candidates, budget, receipt,
                                      objective=objective, max_denominator=max_denominator,
                                      max_abs_error=max_abs_error, evaluation_athlete_ids=evaluated,
                                      design=design, noise_variance=noise_variance,
                                      observation_ids=observation_ids, max_candidates=max_candidates)
    synthetic = fit_result.get("synthetic")
    scope = ("synthetic fitted-bridge fixture; no NFL empirical scouting claim" if synthetic is True
             else "conditional planning from a fitted NFL bridge; scouting lift requires separate outcome evaluation"
             if synthetic is False else "fit evidence provenance unspecified; conditional planning only")
    result.update({"source_feature_order": feature_names,
                   "fitted_jacobian_scope": jacobian.get("scope", "caller-declared fixed fitted sensitivity"),
                   "jacobian_composition_audit": {"identity": "h = w @ F",
                                                  "source_to_outcome": h,
                                                  "composed_source_to_outcome": composed,
                                                  "absolute_errors": errors,
                                                  "per_coefficient_tolerances": tolerances,
                                                  "passed": True,
                                                  "loading_override_allowed": False},
                   "cutoff_conversion": {"exclusive_fit_cutoff": exclusive,
                                         "inclusive_outcome_cutoff": receipt.outcome_cutoff,
                                         "rule": conversion},
                   "fitted_training_ids": training_ids,
                   "fitted_training_group_ids": training_groups,
                   "fitted_evaluated_group_ids": evaluated_groups,
                   "evidence_scope": scope})
    return result
