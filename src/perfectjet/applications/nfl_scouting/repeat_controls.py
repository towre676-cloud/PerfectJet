"""Strong, source-only controls for independent-attempt prediction.

This is an exploratory analysis declared after the first rolling-motion study.
No NFL target is used. Every calibration and inner choice uses older players;
all orientations of a player's repeat pair stay in that player's fold.
"""
from collections import Counter
from dataclasses import replace
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from perfectjet.reliable_modes import ReliableModes
from . import rolling as R
from .rolling_reliability import vector_groups

PROTOCOL = {
    'schema': 'perfectjet/repeat-controls/1',
    'status': 'exploratory strong-control follow-up after stopped-flow results',
    'target': 'second distinct-attempt three-gate area acceleration vector',
    'features': 'first distinct-attempt vector, no NFL measurements or labels',
    'ordering': 'source attempt ID order, not claimed chronological order',
    'calibration': 'earlier classes only; player-grouped symmetric repeat pairs in inner folds',
    'controls': ['prior', 'raw', 'scalar_shrinkage', 'diagonal_reliability', 'ridge', 'reliable'],
    'ridge_penalties': [.1, 1., 10., 100., 1000.],
    'scalar_grid': [0., .25, .5, .75, 1.],
    'uncertainty': 'paired class-stratified fixed errors and whole original-player refits',
    'limits': 'repeat prediction, not NFL prediction; reused cohorts and adaptive methodology'
}


def _pairs(groups, ids):
    # Equal original-player weight, including both pair orientations. This is
    # exchangeable-repeat augmentation, not twice as many independent players.
    ids = [a for a in ids if a in groups and len(groups[a]) >= 2]
    x = np.asarray([groups[a][j] for a in ids for j in (0, 1)])
    y = np.asarray([groups[a][1-j] for a in ids for j in (0, 1)])
    return x, y


def _ridge(alpha):
    return make_pipeline(StandardScaler(), Ridge(alpha=alpha))


def _fold(groups, train, test, original, seed):
    tr = sorted(a for a in train if a in groups)
    te = sorted(a for a in test if a in groups and len(groups[a]) >= 2)
    if not te or len(tr) < 6: raise ValueError('insufficient repeat players')
    if {original(a) for a in tr} & {original(a) for a in te}:
        raise ValueError('original-player leakage')
    originals = sorted({original(a) for a in tr})
    rng = np.random.default_rng(seed)
    shuffled = rng.permutation(originals)
    assignment = {a: i % 3 for i, a in enumerate(shuffled)}
    losses = {('ridge', a): 0. for a in PROTOCOL['ridge_penalties']}
    losses.update({('scalar', a): 0. for a in PROTOCOL['scalar_grid']})
    n = 0; fits = 0
    for k in range(3):
        a = [i for i in tr if assignment[original(i)] != k]
        b = [i for i in tr if assignment[original(i)] == k]
        x, y = _pairs(groups, a); vx, vy = _pairs(groups, b)
        if len(x) < 4 or not len(vx): raise ValueError('insufficient inner repeats')
        m = ReliableModes.fit(groups, training_groups=a)
        for alpha in PROTOCOL['ridge_penalties']:
            p = _ridge(alpha).fit(x, y).predict(vx); fits += 1
            losses['ridge', alpha] += float(np.sum((vy-p)**2))
        for alpha in PROTOCOL['scalar_grid']:
            p = m.mean + alpha * (vx-m.mean)
            losses['scalar', alpha] += float(np.sum((vy-p)**2))
        n += vy.size
    chosen = {f: min((v, a) for (family, a), v in losses.items() if family == f)[1]
              for f in ('ridge', 'scalar')}
    m = ReliableModes.fit(groups, training_groups=tr)
    truth = np.asarray([groups[a][1] for a in te]); raw = np.asarray([groups[a][0] for a in te])
    x, y = _pairs(groups, tr)
    ridge = _ridge(chosen['ridge']).fit(x, y); fits += 1
    weights = np.diag(m.signal)/(np.diag(m.signal)+np.diag(m.noise))
    pred = {'prior': np.tile(m.mean, (len(te), 1)), 'raw': raw,
            'scalar_shrinkage': m.mean + chosen['scalar']*(raw-m.mean),
            'diagonal_reliability': m.mean + weights*(raw-m.mean),
            'ridge': ridge.predict(raw),
            'reliable': np.asarray([m.posterior([groups[a][0]])[0] for a in te])}
    return {'ids': te, 'loss': {k: np.mean((truth-v)**2, axis=1).tolist() for k,v in pred.items()},
            'chosen': chosen, 'ridge_model_fits': fits,
            'training_players': len(tr), 'calibration': m.receipt()}


def summarize(folds, draws=4000, seed=141014):
    keys = tuple(folds[0]['loss']); total = sum(len(f['ids']) for f in folds)
    losses = {k: np.concatenate([f['loss'][k] for f in folds]) for k in keys}
    mses = {k: float(np.mean(v)) for k,v in losses.items()}
    comparisons = {}
    rng = np.random.default_rng(seed)
    for base in ('raw','prior','scalar_shrinkage','diagonal_reliability','ridge'):
        samples=[]
        for _ in range(draws):
            b=[];c=[]
            for f in folds:
                idx=rng.integers(0,len(f['ids']),len(f['ids']))
                b.extend(np.asarray(f['loss'][base])[idx]);c.extend(np.asarray(f['loss']['reliable'])[idx])
            if np.mean(b)>0:samples.append(1-np.mean(c)/np.mean(b))
        comparisons['reliable_vs_'+base] = {'gain':1-mses['reliable']/mses[base],
            'fixed_interval_90':np.quantile(samples,[.05,.95]).tolist() if samples else None}
    return {'players':total,'mse':mses,'comparisons':comparisons,
            'folds':[{'year':f['year'],'players':len(f['ids']),'chosen':f['chosen'],
                'training_players':f['training_players'],
                'mse':{k:float(np.mean(v)) for k,v in f['loss'].items()},
                'calibration':f['calibration']} for f in folds],
            'ridge_model_fits':sum(f['ridge_model_fits'] for f in folds)}


def experiment(ds, *, draws=4000, seed=141014):
    w,_=R.source_windows(ds);groups=vector_groups(w);folds=[]
    for year in sorted({v.draft_year for v in ds.athletes.values()})[1:]:
        tr=[a for a,v in ds.athletes.items() if v.draft_year<year]
        te=[a for a,v in ds.athletes.items() if v.draft_year==year]
        original=lambda aid:ds.athletes[aid].bootstrap_group or aid
        f=_fold(groups,tr,te,original,seed);f['year']=year;folds.append(f)
    return {'protocol':PROTOCOL,**summarize(folds,draws,seed)},folds


def full_refits(ds, *, draws=64, seed=141014):
    if draws<1:raise ValueError('positive refit count required')
    rng=np.random.default_rng(seed+3241);rows=[];failures=[]
    for k in range(draws):
        try:
            boot=R.bootstrap_dataset(ds,rng)
            result,_=experiment(boot,draws=0,seed=seed)
            rows.append({'draw':k,**{n:c['gain'] for n,c in result['comparisons'].items()}})
        except ValueError as exc:failures.append({'draw':k,'reason':str(exc)})
    return {'requested_draws':draws,'successful_draws':len(rows),'failed_draws':len(failures),
        'failures':failures,'gains':rows,'intervals_90':{n:np.quantile([r[n] for r in rows],[.05,.95]).tolist()
            for n in rows[0] if n!='draw'} if rows else {},
        'scope':'whole original-player class-stratified refit of source covariance and strong-control tuning; adaptive development sensitivity, not a prospective guarantee'}
