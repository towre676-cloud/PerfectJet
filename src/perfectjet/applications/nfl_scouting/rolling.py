"""Speed-landmark movement and exact stopped-position readouts.

No unseen launch is reconstructed. Positions after an observed speed gate produce
kinematics, nuisance-annihilating jets and an explicit full-history control.
All NFL measurements are labels; all prospect predictors are pre-draft Combine.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import Ridge
from perfectjet.stopped_jets import area_acceleration_weights, minimum_variance_jet
from .schema import Attempt, Dataset, Play, available
from . import burst_transfer as BT
from .official import FRONT_DRILLS

GATES = (2.0, 3.0, 4.0)
KINEMATICS = ('entry_speed','forward_displacement','terminal_speed','path_length','lateral_displacement_abs')
JETS = ('area_acceleration','minimum_variance_acceleration','minimum_variance_jerk')
TIMES = tuple(Q(i,10) for i in range(6))
AREA = np.asarray(area_acceleration_weights(TIMES),float)
BLUE = np.asarray(minimum_variance_jet(TIMES,2,3)['weights'],float)
JERK = np.asarray(minimum_variance_jet(TIMES,3,3)['weights'],float)
EXTRA_CONTEXT = ('rolling_entry_speed','rolling_gate_time','rolling_gate_depth','rolling_heading_to_los')

@dataclass(frozen=True)
class RollingWindow:
    athlete_id: str
    attempt_id: str
    drill: str
    gate: float
    gate_frame: int
    endpoint_frame: int
    gate_time: float
    endpoint_time: float
    entry_speed: float
    forward_displacement: float
    terminal_speed: float
    path_length: float
    lateral_displacement_abs: float
    area_acceleration: float
    minimum_variance_acceleration: float
    minimum_variance_jerk: float
    forward_positions: tuple
    lateral_positions: tuple
    axis: tuple
    available_on: str


def speed_window(attempt, gate=2.0, *, not_before=None):
    """First observed causal two-sample speed gate, then a fixed half-second.

    A trailing 0.2 s speed uses only already observed positions. The two speeds
    overlap and are NOT treated as independent repeats. Invalid sampling before
    the gate or through its endpoint rejects the window. Frames afterwards cannot
    affect selection or readout. No interpolation or NFL-conditioned filtering.
    """
    if not np.isfinite(gate) or gate<=0:
        raise ValueError('positive finite gate required')
    f = attempt.frames
    if len(f)<9:
        return None
    selected=None
    speeds={}
    for i in range(1,len(f)):
        a,b=f[i-1],f[i]
        vals=(a.t,a.x,a.y,b.t,b.x,b.y)
        if not np.isfinite(vals).all() or abs((b.t-a.t)-.1)>1e-5:
            return None
        if i<2:
            continue
        delta=np.asarray([b.x-f[i-2].x,b.y-f[i-2].y],float)
        speeds[i]=float(np.linalg.norm(delta)/.2)
        if i>=3 and (not_before is None or b.t>=not_before) and speeds[i]>=gate-1e-9 and speeds[i-1]>=gate-1e-9:
            selected=i
            break
    if selected is None or selected+5>=len(f):
        return None
    i=selected
    for j in range(i+1,i+6):
        a,b=f[j-1],f[j]
        if not np.isfinite((a.t,a.x,a.y,b.t,b.x,b.y)).all() or abs((b.t-a.t)-.1)>1e-5:
            return None
    delta=np.asarray([f[i].x-f[i-2].x,f[i].y-f[i-2].y],float)
    axis=delta/np.linalg.norm(delta)
    perpendicular=np.asarray([-axis[1],axis[0]])
    positions=np.asarray([[v.x-f[i].x,v.y-f[i].y] for v in f[i:i+6]],float)
    x,y=positions@axis,positions@perpendicular
    steps=np.diff(positions,axis=0)
    return RollingWindow(attempt.athlete_id,attempt.attempt_id,attempt.drill,float(gate),
        i,i+5,float(f[i].t),float(f[i+5].t),speeds[i],float(x[-1]),
        float(np.linalg.norm(positions[-1]-positions[-3])/.2),
        float(np.linalg.norm(steps,axis=1).sum()),abs(float(y[-1])),
        float(AREA@x),float(BLUE@x),float(JERK@x),
        tuple(float(v) for v in x),tuple(float(v) for v in y),tuple(float(v) for v in axis),attempt.recorded_on)


def source_windows(ds, drills=('FORTY_YARD_DASH',)):
    output=[]; rejected=Counter()
    seen=set()
    for a in ds.attempts:
        key=(a.athlete_id,a.attempt_id)
        if key in seen:
            raise ValueError('duplicate source athlete/attempt identity')
        seen.add(key)
        if a.drill not in drills:
            continue
        if not available(a.recorded_on,f'{ds.athletes[a.athlete_id].draft_year}-04-20'):
            rejected['not_predraft']+=1
            continue
        for gate in GATES:
            w=speed_window(a,gate)
            if w is None:rejected[f'no_window_at_{gate:g}']+=1
            else:output.append(w)
    return output,dict(rejected)


def feature_frames(ds, ids, windows, *, include_ngs=True, drills=('FORTY_YARD_DASH',)):
    """Extract once, but imputation/scaling/model fitting remain split-specific."""
    ids=list(ids)
    if len(ids)!=len(set(ids)):
        raise ValueError('duplicate athlete rows')
    base=BT.predictor_frame(ds,ids,include_ngs)
    groups=defaultdict(list)
    for w in windows:
        if w.athlete_id in ds.athletes and available(w.available_on,f'{ds.athletes[w.athlete_id].draft_year}-04-20'):
            groups[w.athlete_id,w.drill,w.gate].append(w)
    source={key:{} for key in ('kinematics','jets','history')}
    for drill in drills:
        for gate in GATES:
            prefix=f'{drill}__v{gate:g}'
            base[prefix+'__count']=[float(len(groups[a,drill,gate])) for a in ids]
            base[prefix+'__available']=[float(bool(groups[a,drill,gate])) for a in ids]
            for name in KINEMATICS+JETS:
                values=[float(np.mean([getattr(w,name) for w in groups[a,drill,gate]])) if groups[a,drill,gate] else np.nan for a in ids]
                family='kinematics' if name in KINEMATICS else 'jets'
                source[family][prefix+'__'+name]=values
            for k in range(1,6):
                for coordinate in ('forward','lateral_abs'):
                    def value(w):
                        return w.forward_positions[k] if coordinate=='forward' else abs(w.lateral_positions[k])
                    source['history'][f'{prefix}__{coordinate}_{k}']=[float(np.mean([value(w) for w in groups[a,drill,gate]])) if groups[a,drill,gate] else np.nan for a in ids]
    kin=pd.DataFrame(source['kinematics'],index=ids)
    return {'conventional':base,
        'kinematics':pd.concat([base,kin],axis=1),
        'jets':pd.concat([base,kin,pd.DataFrame(source['jets'],index=ids)],axis=1),
        'history':pd.concat([base,kin,pd.DataFrame(source['history'],index=ids)],axis=1)}


def coverage(ds, windows):
    counts=Counter(p.athlete_id for p in ds.plays)
    eligible={a for a,n in counts.items() if n>=ds.outcome_definition.get('minimum_plays',30)}
    rows=[]
    for drill in sorted({a.drill for a in ds.attempts}):
        for gate in GATES:
            w=[w for w in windows if w.drill==drill and w.gate==gate]
            by=Counter(v.athlete_id for v in w)
            rows.append({'drill':drill,'gate':gate,'accepted_attempts':len(w),
                'players':len(by),'eligible_target_players':len(set(by)&eligible),
                'players_with_independent_repeat_attempts':sum(n>=2 for n in by.values())})
    return {'source_players':len(ds.athletes),'eligible_primary_players':len(eligible),'by_drill_gate':rows}


def attempt_repeatability(windows,seed=141014):
    """Disjoint attempt first-vs-second means; no overlapping-gate replication."""
    from scipy.stats import spearmanr
    rows=[]
    for drill in sorted({w.drill for w in windows}):
        for gate in GATES:
            groups=defaultdict(list)
            for w in windows:
                if (w.drill,w.gate)==(drill,gate):groups[w.athlete_id].append(w)
            groups={a:sorted(v,key=lambda w:w.attempt_id) for a,v in groups.items() if len(v)>=2}
            for name in KINEMATICS+JETS:
                x=np.asarray([np.mean([getattr(w,name) for w in v[::2]]) for v in groups.values()])
                y=np.asarray([np.mean([getattr(w,name) for w in v[1::2]]) for v in groups.values()])
                rho=float(spearmanr(x,y).statistic) if len(x)>2 and np.ptp(x)>0 and np.ptp(y)>0 else None
                within=float(np.mean((x-y)**2)/2) if len(x) else None
                rows.append({'drill':drill,'gate':gate,'readout':name,'paired_players':len(x),
                    'spearman':rho,'half_squared_difference':within,
                    'scope':'descriptive disjoint-attempt repeatability; no independence across gate/readout rows; not innate ability'})
    return rows


def movement_dataset(ds, movement, *, gate=2.0, minimum_plays=20):
    """Separate same-functional NFL motor target; no held-player NFL predictors."""
    plays=[];audit=Counter()
    records=getattr(movement,'records',movement)
    for r in records:
        audit['input_records']+=1
        if not r.usable:
            audit['upstream_unusable']+=1;continue
        a=Attempt(r.athlete_id,r.play_id,'NFL_ROLLING',r.frames,f'{r.season}-12-31')
        w=speed_window(a,gate,not_before=0.)
        if w is None:
            audit['gate_unavailable']+=1;continue
        c=dict(r.context)
        c.update(rolling_entry_speed=w.entry_speed,rolling_gate_time=w.gate_time,
                 rolling_gate_depth=float(r.context.get('snap_depth',0))-r.frames[w.gate_frame].x,
                 rolling_heading_to_los=w.axis[0])
        plays.append(Play(r.athlete_id,r.season,r.play_id,w.forward_displacement,c))
        audit['accepted_plays']+=1
    counts=Counter(p.athlete_id for p in plays)
    audit['accepted_players']=len(counts)
    audit['players_minimum_plays']=sum(n>=minimum_plays for n in counts.values())
    return Dataset(ds.athletes,ds.attempts,plays,ds.manifest,
        {'name':'rolling_forward_displacement_05','units':'yards','minimum_plays':minimum_plays,
         'meaning':'half-second displacement along observed velocity after speed-2 NFL landmark; context residualized','lower_is_better':False},ds.synthetic),dict(audit)


def _context(plays):
    f=BT.context_frame(plays)
    for col in EXTRA_CONTEXT:
        f[col]=[float(p.context[col]) if BT._finite(p.context.get(col)) else np.nan for p in plays]
    return f


def _context_predict(train,test):
    f=_context(train);model=BT._regressor(f,100.)
    counts=Counter(p.athlete_id for p in train)
    weights=np.asarray([1/counts[p.athlete_id] for p in train]);weights*=len(weights)/weights.sum()
    model.fit(f,[p.outcome for p in train],ridge__sample_weight=weights)
    return model.predict(_context(test))


def target_values(ds,train_ids,test_ids,cutoff,seed):
    train_ids,test_ids=set(train_ids),set(test_ids)
    original=lambda aid: ds.athletes[aid].bootstrap_group or aid
    if train_ids&test_ids or {original(a) for a in train_ids}&{original(a) for a in test_ids}:
        raise ValueError('original-player leakage')
    if any(ds.athletes[a].draft_year>=cutoff for a in train_ids):
        raise ValueError('training class reaches temporal cutoff')
    train=[p for p in ds.plays if p.athlete_id in train_ids and p.season<cutoff and p.season==ds.athletes[p.athlete_id].draft_year]
    test=[p for p in ds.plays if p.athlete_id in test_ids and p.season==ds.athletes[p.athlete_id].draft_year]
    groups=BT._groups(ds,sorted(train_ids),3,seed)
    residuals=[]
    for k in range(3):
        a=[p for p in train if groups[p.athlete_id]!=k]
        b=[p for p in train if groups[p.athlete_id]==k]
        if a and b:residuals.extend((p,float(p.outcome-v)) for p,v in zip(b,_context_predict(a,b)))
    if train and test:residuals.extend((p,float(p.outcome-v)) for p,v in zip(test,_context_predict(train,test)))
    by=defaultdict(list)
    for p,v in residuals:by[p.athlete_id].append(v)
    return {a:float(np.mean(v)) for a,v in by.items() if len(v)>=ds.outcome_definition['minimum_plays']}


def _regressor(frame,alpha,kind):
    linear=BT._regressor(frame,alpha)
    if kind=='quadratic':
        return make_pipeline(linear.steps[0][1],PolynomialFeatures(2,include_bias=False),StandardScaler(),Ridge(alpha=alpha))
    return linear


def _fit_candidates(frames,tr,te,y,alphas):
    output={}
    for family in ('conventional','quadratic','kinematics','jets','history'):
        key='conventional' if family=='quadratic' else family
        a=frames[key].loc[tr];b=frames[key].loc[te]
        for alpha in alphas:
            reg=_regressor(a,alpha,family).fit(a,[y[i] for i in tr])
            output[family,alpha]=reg.predict(b)
    return output


def _best(losses,families):
    choices=[(value,key) for key,value in losses.items() if key[0] in families]
    return min(choices,key=lambda v:(v[0],v[1]))[1]


def nested_fold(ds,frames,train_ids,test_ids,cutoff,*,seed=141014,alphas=(10.,100.,1000.)):
    train_ids,test_ids=sorted(train_ids),sorted(test_ids)
    mapping=BT._groups(ds,train_ids,3,seed)
    losses=defaultdict(float);samples=0
    for k in range(3):
        a=[i for i in train_ids if mapping[i]!=k];b=[i for i in train_ids if mapping[i]==k]
        y=target_values(ds,a,b,cutoff,seed+20+k)
        a=[i for i in a if i in y];b=[i for i in b if i in y]
        if len(a)<4 or not b:raise ValueError('insufficient inner target players')
        predictions=_fit_candidates(frames,a,b,y,alphas)
        yy=np.asarray([y[i] for i in b]);samples+=len(b)
        for key,p in predictions.items():losses[key]+=float(np.sum((yy-p)**2))
    losses={k:v/samples for k,v in losses.items()}
    choices={'conventional':_best(losses,('conventional','quadratic')),
        'tracking':_best(losses,('kinematics','jets','history')),
        'jets':_best(losses,('jets',)),
        'kinematics':_best(losses,('kinematics',)),
        'history':_best(losses,('history',)),
        'strong_control':_best(losses,('conventional','quadratic','kinematics','history'))}
    y=target_values(ds,train_ids,test_ids,cutoff,seed+90)
    tr=[a for a in train_ids if a in y];te=[a for a in test_ids if a in y]
    if len(tr)<6 or not te:raise ValueError('insufficient outer target players')
    predictions=_fit_candidates(frames,tr,te,y,alphas)
    raw={name:predictions[choice].tolist() for name,choice in choices.items()}
    # Conform to paired_summary convention: lower is better. For motor
    # displacement both target and prediction are negated, without changing MSE.
    sign=1. if ds.outcome_definition.get('lower_is_better',True) else -1.
    return {'year':cutoff,'ids':te,'y':(sign*np.asarray([y[a] for a in te])).tolist(),
        **{k:(sign*np.asarray(v)).tolist() for k,v in raw.items()},
        'baseline':(sign*np.asarray(raw['conventional'])).tolist(),
        'movement':(sign*np.asarray(raw['tracking'])).tolist(),
        'training_target_quartile':float(np.quantile(sign*np.asarray([y[a] for a in tr]),.25)),
        'selected':{name:{'family':k[0],'penalty':k[1]} for name,k in choices.items()},
        'inner_mse':{f'{k[0]}:{k[1]:g}':v for k,v in losses.items()},
        'train_ids':tr,'training_original_ids':sorted({ds.athletes[a].bootstrap_group or a for a in tr}),
        'test_original_ids':sorted({ds.athletes[a].bootstrap_group or a for a in te}),
        'target_sign_for_shortlist':sign,'model_fits':4*len(predictions)}


def paired_summary(folds,baseline='conventional',candidate='tracking',*,seed=141014,draws=4000):
    """Class-stratified paired player uncertainty, fixed fitted models only."""
    rows=[{**f,'baseline':f[baseline],'movement':f[candidate]} for f in folds]
    out=BT.paired_summary(rows,draws=0,seed=seed)
    out.pop('largest_influences',None)
    rng=np.random.default_rng(seed);gains=[]
    by=[]
    for f in rows:
        y=np.asarray(f['y']);lb=(y-np.asarray(f['baseline']))**2;lc=(y-np.asarray(f['movement']))**2
        by.append((lb,lc))
    for _ in range(draws):
        bs=[];cs=[]
        for lb,lc in by:
            idx=rng.integers(0,len(lb),len(lb));bs.extend(lb[idx]);cs.extend(lc[idx])
        denom=float(np.mean(bs))
        if denom>0:gains.append(1-float(np.mean(cs))/denom)
    out['fixed_prediction_interval_90']=np.quantile(gains,[.05,.95]).tolist() if gains else None
    out['fixed_prediction_interval_95']=np.quantile(gains,[.025,.975]).tolist() if gains else None
    out['interval_scope']='class-stratified paired-player resampling of fixed predictions; excludes model selection/refit and adaptive-research uncertainty'
    out['comparison']={'baseline':baseline,'candidate':candidate}
    out['by_class']=[{'year':f['year'],'players':len(f['ids']),
        'baseline_mse':float(np.mean(b)),'candidate_mse':float(np.mean(c)),
        'gain':float(1-np.mean(c)/np.mean(b)) if np.mean(b)>0 else None} for f,(b,c) in zip(rows,by)]
    return out


def experiment(ds,*,windows=None,drills=('FORTY_YARD_DASH',),include_ngs=True,seed=141014,draws=4000):
    if ds.synthetic:raise ValueError('real-data experiment refuses synthetic evidence')
    if windows is None:windows,_=source_windows(ds,drills)
    frames=feature_frames(ds,sorted(ds.athletes),windows,include_ngs=include_ngs,drills=drills)
    years=sorted({a.draft_year for a in ds.athletes.values()});folds=[]
    for year in years[1:]:
        tr=sorted(a for a,v in ds.athletes.items() if v.draft_year<year)
        te=sorted(a for a,v in ds.athletes.items() if v.draft_year==year)
        folds.append(nested_fold(ds,frames,tr,te,year,seed=seed))
    comparisons={name:paired_summary(folds,base,candidate,seed=seed,draws=draws) for name,base,candidate in (
        ('tracking_vs_conventional','conventional','tracking'),
        ('jets_vs_conventional','conventional','jets'),
        ('jets_vs_full_history','history','jets'),
        ('jets_vs_strong_control','strong_control','jets'),
        ('kinematics_vs_conventional','conventional','kinematics'))}
    return {'schema':'perfectjet/stopped-flow-experiment/1','status':'real-data development evidence',
        'include_ngs':include_ngs,'source_drills':list(drills),'target':ds.outcome_definition,
        'comparisons':comparisons,'folds':folds,'model_fits':sum(f['model_fits'] for f in folds),
        'source_features':{k:len(v.columns) for k,v in frames.items()},
        'prediction_rule':'Combine only; no held-player NFL frames or labels in predictors'}


def public_result(result):
    """Public result is a positive aggregate allowlist, never a recursive dump."""
    out={k:result[k] for k in ('schema','status','include_ngs','source_drills','target','comparisons','model_fits','source_features','prediction_rule')}
    out['folds']=[{'year':f['year'],'evaluated_players':len(f['ids']),'training_players':len(f['train_ids']),
        'selected':f['selected'],'inner_mse':f['inner_mse'],'model_fits':f['model_fits']} for f in result['folds']]
    return out


def bootstrap_dataset(ds,rng):
    attempts=defaultdict(list);plays=defaultdict(list)
    for a in ds.attempts:attempts[a.athlete_id].append(a)
    for p in ds.plays:plays[p.athlete_id].append(p)
    aa={};at=[];pl=[]
    for year in sorted({a.draft_year for a in ds.athletes.values()}):
        ids=sorted(a for a,v in ds.athletes.items() if v.draft_year==year)
        count=Counter()
        for a in rng.choice(ids,len(ids),replace=True):
            count[a]+=1;name=f'{a}#rollingboot{count[a]}'
            aa[name]=replace(ds.athletes[a],athlete_id=name,bootstrap_group=ds.athletes[a].bootstrap_group or a)
            at.extend(replace(v,athlete_id=name,attempt_id=f'{v.attempt_id}#rollingboot{count[a]}') for v in attempts[a])
            pl.extend(replace(v,athlete_id=name) for v in plays[a])
    return Dataset(aa,at,pl,ds.manifest,ds.outcome_definition,False)


def full_refits(ds,*,draws=32,include_ngs=True,drills=('FORTY_YARD_DASH',),seed=141014):
    if draws<1:raise ValueError('positive refit count required')
    rng=np.random.default_rng(seed+1901);rows=[];failures=[]
    for k in range(draws):
        try:
            boot=bootstrap_dataset(ds,rng)
            run=experiment(boot,include_ngs=include_ngs,drills=drills,seed=seed,draws=0)
            rows.append({'draw':k,**{name:v['gain'] for name,v in run['comparisons'].items()}})
        except ValueError as exc:failures.append({'draw':k,'reason':str(exc)})
        print(f'Complete stopped-flow refit {k+1}/{draws}',flush=True)
    intervals={name:np.quantile([r[name] for r in rows],[.05,.95]).tolist() for name in rows[0] if name!='draw'} if rows else {}
    return {'requested_draws':draws,'successful_draws':len(rows),'failed_draws':len(failures),
        'failures':failures,'gains':rows,'intervals_90':intervals,
        'scope':'full original-player class-stratified empirical bootstrap; reextract source and refit context, transformations, model family and penalties; not prospective coverage or protection against prior adaptive use'}
