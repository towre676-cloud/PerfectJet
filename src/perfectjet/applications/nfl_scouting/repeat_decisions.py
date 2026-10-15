"""Source-only decision geometry study, separate from NFL transfer experiments.

Fit 2023, calibrate 2024, evaluate 2025. Previously inspected classes remain
DEVELOPMENT data. Three overlapping speed windows are ONE attempt vector.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from itertools import combinations
from math import gamma, isfinite, pi
import numpy as np
from scipy.stats import chi2
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from perfectjet.reliable_modes import ReliableModes
from perfectjet.replication_geometry import (calibrate, calibration_requirement,
    ellipsoid_scores, interval_ranks, linear_interval, repeat_covariance)
from . import rolling as R
from .rolling_reliability import vector_groups

PROTOCOL = {
    'schema': 'perfectjet/repeat-decision-geometry/1',
    'status': 'parallel source-only development declared after v0.14; no new holdout',
    'split': {'fit': 2023, 'calibration': 2024, 'evaluation': 2025},
    'target': 'second distinct forty attempt area-acceleration vector at gates 2,3,4 yd/s',
    'units': 'yd/s^2; inherited frame positions are yards, not metres',
    'ordering': 'source attempt-ID order; not claimed chronological order',
    'target_not': ['latent talent', 'NFL get-off', 'NFL success'],
    'calibration_unit': 'original athlete; joint score; duplicate identities collapsed',
    'alpha': '0.1', 'loading': [1/3, 1/3, 1/3],
    'methods': ['raw', 'reliable', 'ridge_joint', 'ridge_diagonal', 'ridge_isotropic'],
    'ridge_penalties': [.1, 1., 10., 100., 1000.], 'seed': 141015,
    'guarantee_limit': 'coverage requires exchangeable original calibration/test groups; different classes do not automatically satisfy it',
    'selection_limit': 'marginal intervals do not certify an adaptively selected whole board',
    'replication_limit': 'working-model projections, not observed benefits of third or later attempts',
}

@dataclass(frozen=True)
class Pair:
    key: str
    original: str
    year: int
    first: tuple
    second: tuple


def source_pairs(ds):
    if ds.synthetic:
        raise ValueError('real-data decision study refuses synthetic evidence')
    windows, rejected = R.source_windows(ds); grouped = vector_groups(windows)
    pairs = [Pair(a, ds.athletes[a].bootstrap_group or a, ds.athletes[a].draft_year,
                  tuple(v[0]), tuple(v[1])) for a, v in sorted(grouped.items()) if len(v) >= 2]
    return pairs, {'complete_source_players': len(grouped), 'paired_source_players': len(pairs),
                   'accepted_windows': len(windows), 'source_rejections': rejected,
                   'source_attempt_order': PROTOCOL['ordering']}


def _xy(records, both=True):
    x = [v for r in records for v in (r.first, r.second)] if both else [r.first for r in records]
    y = [v for r in records for v in (r.second, r.first)] if both else [r.second for r in records]
    return np.asarray(x, float), np.asarray(y, float)


def _ridge(alpha):
    return make_pipeline(StandardScaler(), Ridge(alpha=alpha))


def fit_models(records, seed=141015):
    originals = sorted({r.original for r in records})
    if len(originals) < 6:
        raise ValueError('at least six original fit athletes required')
    if len({r.key for r in records}) != len(records):
        raise ValueError('fit row keys must be unique; preserve original IDs separately')
    assignment = {a: i % 3 for i, a in enumerate(np.random.default_rng(seed).permutation(originals))}
    losses = {a: 0. for a in PROTOCOL['ridge_penalties']}; residuals = {a: [] for a in losses}
    fits = 0
    for k in range(3):
        train = [r for r in records if assignment[r.original] != k]
        valid = [r for r in records if assignment[r.original] == k]
        if len(train) < 2 or not valid:
            raise ValueError('insufficient original-player inner split')
        x, y = _xy(train); vx, vy = _xy(valid)
        for alpha in losses:
            e = vy-_ridge(alpha).fit(x, y).predict(vx); fits += 1
            losses[alpha] += float(np.sum(e*e)); residuals[alpha].append(e)
    alpha = min(losses, key=lambda a: (losses[a], a))
    x, y = _xy(records); ridge = _ridge(alpha).fit(x, y); fits += 1
    residual = np.concatenate(residuals[alpha])
    # Geometry and penalty use FIT partition only. Selection of this OOF
    # geometry may be optimistic internally; independent calibration rescales.
    shape = residual.T@residual/len(residual)
    shape = (shape+shape.T)/2 + .05*max(float(np.trace(shape)/len(shape)), 1e-10)*np.eye(len(shape))
    groups = {r.key: np.asarray([r.first, r.second], float) for r in records}
    reliable = ReliableModes.fit(groups, training_groups=tuple(groups))
    covariance = {'raw': 2*reliable.noise,
                  'reliable': repeat_covariance(reliable.signal, reliable.noise, 1),
                  'ridge_joint': shape, 'ridge_diagonal': np.diag(np.diag(shape)),
                  'ridge_isotropic': np.eye(3)*float(np.trace(shape)/3)}
    return {'ridge': ridge, 'reliable': reliable, 'covariance': covariance,
            'ridge_penalty': alpha, 'ridge_fits': fits,
            'fit_originals': len(originals), 'fit_weighted_rows': len(records)}


def predict(models, records):
    x, y = _xy(records, both=False); reg = models['ridge'].predict(x)
    return y, {'raw': x, 'reliable': np.asarray([models['reliable'].posterior([v])[0] for v in x]),
               'ridge_joint': reg, 'ridge_diagonal': reg, 'ridge_isotropic': reg}


def _comparisons(bounds, predicted, truth):
    correct = settled = point_correct = non_ties = 0
    for i, j in combinations(range(len(truth)), 2):
        dy, dp = truth[i]-truth[j], predicted[i]-predicted[j]
        if dy != 0:
            non_ties += 1; point_correct += int(dy*dp > 0)
        li, ui = bounds[str(i)]; lj, uj = bounds[str(j)]
        if li > uj or lj > ui:
            settled += 1; correct += int((li > uj and dy > 0) or (lj > ui and dy < 0))
    return {'settled_pairs': settled, 'correct_settled_pairs': correct,
            'settled_accuracy': correct/settled if settled else None,
            'all_point_pair_accuracy': point_correct/non_ties if non_ties else None,
            'all_pairs': len(truth)*(len(truth)-1)//2, 'independent_evaluation_players': len(truth),
            'interpretation': 'dependent descriptive comparisons; marginal-card selection is not familywise-certified'}


def evaluate(records, *, seed=141015, include_private=True):
    fit, calibration, test = ([r for r in records if r.year == y] for y in (2023, 2024, 2025))
    if not calibration or not test:
        raise ValueError('fit/calibration/evaluation classes must all be present')
    originals = [{r.original for r in v} for v in (fit, calibration, test)]
    if any(originals[i] & originals[j] for i in range(3) for j in range(i+1, 3)):
        raise ValueError('original-athlete leakage across fit/calibration/evaluation')
    models = fit_models(fit, seed); cy, cp = predict(models, calibration); ty, tp = predict(models, test)
    h = np.asarray(PROTOCOL['loading']); unique = {}
    for i, r in enumerate(test):
        unique.setdefault(r.original, i)
    indices = list(unique.values()); truth = ty[indices]@h
    ids = [r.original for r in calibration]; family = len(originals[2]); outputs = {}; private = {}
    for name in PROTOCOL['methods']:
        covariance = models['covariance'][name]
        cs = ellipsoid_scores(cy, cp[name], covariance); ts = ellipsoid_scores(ty, tp[name], covariance)
        radius = calibrate(cs, group_ids=ids, alpha=PROTOCOL['alpha'])
        pair_radius = calibrate(cs, group_ids=ids, alpha=PROTOCOL['alpha'], family_size=2)
        board_radius = calibrate(cs, group_ids=ids, alpha=PROTOCOL['alpha'], family_size=family)
        scalar = calibrate(np.abs((cy-cp[name])@h), group_ids=ids, alpha=PROTOCOL['alpha'])
        bounds = {str(i): linear_interval(mu, covariance, radius.radius, h) for i, mu in enumerate(tp[name][indices])}
        board_bounds = {str(i): linear_interval(mu, covariance, board_radius.radius, h) for i, mu in enumerate(tp[name][indices])}
        scalar_bounds = {str(i): (float(mu@h)-scalar.radius, float(mu@h)+scalar.radius) for i, mu in enumerate(tp[name][indices])}
        volume = pi**1.5/gamma(2.5)*radius.radius**3*float(np.sqrt(np.linalg.det(covariance)))
        br = interval_ranks(board_bounds, top_k=min(5, len(indices)))
        outputs[name] = {
            'mse': float(np.mean((ty-tp[name])**2)),
            'gaussian_nominal_90_covered': int(np.sum(ts <= np.sqrt(chi2.ppf(.9, 3)))),
            'joint_calibrated_covered': int(np.sum(ts <= radius.radius)),
            'joint_calibrated_coverage': float(np.mean(ts <= radius.radius)),
            'calibration': radius.receipt(), 'fixed_pair_calibration': pair_radius.receipt(),
            'board_calibration': board_radius.receipt(), 'ellipsoid_volume': volume if isfinite(volume) else None,
            'mean_acceleration_halfwidth': float((bounds['0'][1]-bounds['0'][0])/2) if isfinite(radius.radius) else None,
            'fixed_mean_scalar_halfwidth': scalar.radius if isfinite(scalar.radius) else None,
            'fixed_mean_scalar_covered': int(np.sum(np.abs((ty-tp[name])@h) <= scalar.radius)),
            'covariance': covariance.tolist(),
            'marginal_card_comparisons': _comparisons(bounds, tp[name][indices]@h, truth),
            'fixed_mean_scalar_comparisons': _comparisons(scalar_bounds, tp[name][indices]@h, truth),
            'whole_board': {'settled_pairs': br['settled_pairs'], 'total_pairs': br['total_pairs'],
                            'guaranteed_top_5': sum(r['guaranteed_top_k'] for r in br['ranks'].values()),
                            'possible_top_5': sum(r['possible_top_k'] for r in br['ranks'].values())}}
        if include_private:
            private[name] = {'ids': [r.original for r in test], 'truth': ty.tolist(), 'predictions': tp[name].tolist(),
                             'calibration_ids': ids, 'calibration_scores': cs.tolist(), 'test_scores': ts.tolist()}
    m = models['reliable']; replication = []
    for name, loading in [('average', h), ('low_gate', np.array([1., 0., 0.])),
                          ('high_gate', np.array([0., 0., 1.])), ('high_minus_low', np.array([-1., 0., 1.]))]:
        noise_floor = float(loading@m.noise@loading)
        variances = {str(n): float(loading@repeat_covariance(m.signal, m.noise, n)@loading) for n in (0, 1, 2, 3, 5, 10, 100)}
        replication.append({'readout': name, 'loading': loading.tolist(),
                            'next_attempt_variance_by_known_repeats': variances,
                            'next_attempt_irreducible_variance': noise_floor, 'latent_variance_limit': 0.,
                            'ceiling_gain_from_more_repeats_after_one': 1-noise_floor/variances['1'],
                            'scope': 'fitted Gaussian independent-repeat projection; not observed improvement or latent talent certification'})
    return {'protocol': PROTOCOL, 'fit_players': len(originals[0]), 'calibration_players': len(originals[1]),
            'evaluation_players': len(originals[2]), 'evaluation_weighted_rows': len(test),
            'ridge_penalty': models['ridge_penalty'], 'ridge_fits': models['ridge_fits'],
            'results': outputs, 'replication': replication,
            'calibration_requirements_90': {str(k): calibration_requirement('0.1', k) for k in (1, 2, family)},
            'exchangeability_across_classes_established': False, 'nfl_scouting_advantage_established': False}, private


def nominal_audit(ds):
    """Replay inherited earlier-class Gaussian covariance on new-class repeats."""
    windows, _ = R.source_windows(ds); groups = vector_groups(windows); rows = []
    for year in (2024, 2025):
        train = [a for a, v in ds.athletes.items() if v.draft_year < year]
        test = [a for a, v in ds.athletes.items() if v.draft_year == year and len(groups.get(a, [])) >= 2]
        model = ReliableModes.fit(groups, training_groups=train)
        truth = np.asarray([groups[a][1] for a in test])
        centers = np.asarray([model.posterior([groups[a][0]])[0] for a in test])
        scores = ellipsoid_scores(truth, centers, repeat_covariance(model.signal, model.noise, 1))
        rows.append({'year': year, 'players': len(test),
                     'covered_nominal_joint_90': int(np.sum(scores**2 <= chi2.ppf(.9, 3))),
                     'coverage': float(np.mean(scores**2 <= chi2.ppf(.9, 3))), 'source_calibration': model.receipt()})
    return {'scope': 'calibration audit of inherited Gaussian working covariance; no fit to test labels', 'folds': rows}


def refit_sensitivity(records, *, draws=128, seed=141015):
    """Original-player resampling sensitivity, NOT a claimed confidence interval.

    Fit frequencies retained; duplicate calibration identities collapse.
    """
    if isinstance(draws, bool) or not isinstance(draws, int) or draws < 1:
        raise ValueError('draws must be positive integer')
    rng = np.random.default_rng(seed+9127); rows = []; failures = []
    for k in range(draws):
        sampled = []
        for year in (2023, 2024, 2025):
            pool = [r for r in records if r.year == year]
            if not pool:
                raise ValueError('all three classes required')
            for j, i in enumerate(rng.integers(0, len(pool), len(pool))):
                sampled.append(replace(pool[i], key=f'bootstrap:{year}:{j}'))
        try:
            result, _ = evaluate(sampled, seed=seed, include_private=False)
            row = {'draw': k, 'fit_originals': result['fit_players'], 'calibration_originals': result['calibration_players'],
                   'evaluation_originals': result['evaluation_players']}
            for name, v in result['results'].items():
                row[name+'_coverage'] = v['joint_calibrated_coverage']; row[name+'_mse'] = v['mse']
                row[name+'_volume'] = v['ellipsoid_volume']
            rows.append(row)
        except ValueError as exc:
            failures.append({'draw': k, 'reason': str(exc)})
    summary = {}
    for key in rows[0] if rows else ():
        if key != 'draw':
            values = [r[key] for r in rows if r[key] is not None and isfinite(r[key])]
            summary[key] = {'q05_median_q95': np.quantile(values, [.05, .5, .95]).tolist() if values else None,
                            'finite_draws': len(values)}
    return {'requested_draws': draws, 'successful_draws': len(rows), 'failures': failures,
            'summary': summary, 'draws': rows,
            'scope': 'original-player resampling sensitivity; calibration identities collapsed; no prospective or confidence guarantee'}
