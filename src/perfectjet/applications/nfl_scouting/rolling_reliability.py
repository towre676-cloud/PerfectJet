"""Training-repeat calibrated acceleration transfer, an exploratory refinement.

Only the three area-acceleration speed gates enter. Their correlated noise is
estimated jointly from distinct attempts. The returned features stay in physical
coordinates, so no eigenbasis from one player fold is mixed with another.
"""
from collections import defaultdict
import numpy as np
import pandas as pd
from perfectjet.reliable_modes import ReliableModes
from . import rolling as R
from . import burst_transfer as BT

PROTOCOL={'schema':'perfectjet/reliable-stopped-flow/1',
    'status':'exploratory refinement declared after the initial stopped-flow outcome run',
    'source':'forty area acceleration at speed gates 2,3,4 yd/s',
    'measurement_groups':'complete three-gate vectors; distinct attempts, never independent gates',
    'noise_ridge_fraction':.05,'signal_estimator':'athlete mean covariance minus average mean-noise covariance; generalized nonpositive modes clipped',
    'features':'three physical-coordinate posterior deviations; no latent-axis mixing',
    'controls':['strong conventional','raw three-gate acceleration means'],
    'model_selection':'inner original-player folds, penalties 10/100/1000; source covariance rebuilt in every fold',
    'claim_limit':'working independent-attempt Gaussian model and estimated covariances; inspected cohorts, no prospective confirmation'}


def vector_groups(windows):
    by=defaultdict(dict)
    for w in windows:
        if w.drill=='FORTY_YARD_DASH':
            key=(w.athlete_id,w.attempt_id)
            if w.gate in by[key]:raise ValueError('duplicate window in a source attempt')
            by[key][w.gate]=w.area_acceleration
    groups=defaultdict(list)
    for (aid,attempt),v in sorted(by.items()):
        if all(g in v for g in R.GATES):groups[aid].append([v[g] for g in R.GATES])
    return dict(groups)


def _frames(base,ids,groups,model):
    raw=base.loc[ids].copy();posterior=base.loc[ids].copy()
    for k in range(3):
        raw[f'area_raw_{k}']=[np.mean(groups[a],axis=0)[k]-model.mean[k] if a in groups else 0. for a in ids]
        posterior[f'area_posterior_{k}']=[model.posterior(groups.get(a,[]))[0][k]-model.mean[k] for a in ids]
    return {'conventional':base.loc[ids],'raw':raw,'reliable':posterior}


def _fit(base,groups,train_ids,test_ids,y,*,alphas=(10.,100.,1000.)):
    model=ReliableModes.fit(groups,training_groups=train_ids)
    tr=[a for a in train_ids if a in y];te=[a for a in test_ids if a in y]
    if len(tr)<4 or not te:raise ValueError('insufficient target players')
    a=_frames(base,tr,groups,model);b=_frames(base,te,groups,model)
    predictions={}
    for family in ('conventional','quadratic','raw','reliable'):
        key='conventional' if family=='quadratic' else family
        for alpha in alphas:
            reg=R._regressor(a[key],alpha,family).fit(a[key],[y[i] for i in tr])
            predictions[family,alpha]=reg.predict(b[key])
    return predictions,tr,te,model.receipt()


def nested_fold(ds,base,groups,train_ids,test_ids,cutoff,seed=141014):
    train_ids,test_ids=sorted(train_ids),sorted(test_ids);mapping=BT._groups(ds,train_ids,3,seed)
    losses=defaultdict(float);n=0
    for k in range(3):
        a=[i for i in train_ids if mapping[i]!=k];b=[i for i in train_ids if mapping[i]==k]
        y=R.target_values(ds,a,b,cutoff,seed+20+k)
        pp,tr,te,_=_fit(base,groups,a,b,y)
        yy=np.asarray([y[i] for i in te]);n+=len(te)
        for key,p in pp.items():losses[key]+=float(np.sum((yy-p)**2))
    losses={k:v/n for k,v in losses.items()}
    chosen={'conventional':R._best(losses,('conventional','quadratic')),
        'raw':R._best(losses,('raw',)),'reliable':R._best(losses,('reliable',))}
    y=R.target_values(ds,train_ids,test_ids,cutoff,seed+90)
    predictions,tr,te,receipt=_fit(base,groups,train_ids,test_ids,y)
    sign=1 if ds.outcome_definition.get('lower_is_better',True) else -1
    return {'year':cutoff,'ids':te,'y':[sign*y[a] for a in te],
        **{name:(sign*predictions[key]).tolist() for name,key in chosen.items()},
        'training_target_quartile':float(np.quantile([sign*y[a] for a in tr],.25)),
        'selected':{k:{'family':v[0],'penalty':v[1]} for k,v in chosen.items()},
        'inner_mse':{f'{k[0]}:{k[1]:g}':v for k,v in losses.items()},
        'source_calibration':receipt,'training_players':len(tr),'model_fits':48}


def experiment(ds,*,include_ngs=True,seed=141014,draws=4000):
    if ds.synthetic:raise ValueError('real-data runner refuses synthetic evidence')
    w,_=R.source_windows(ds);groups=vector_groups(w)
    base=R.feature_frames(ds,sorted(ds.athletes),w,include_ngs=include_ngs)['conventional']
    base['complete_acceleration_attempts']=[float(len(groups.get(a,[]))) for a in base.index]
    years=sorted({a.draft_year for a in ds.athletes.values()});folds=[]
    for year in years[1:]:
        a=[i for i,v in ds.athletes.items() if v.draft_year<year]
        b=[i for i,v in ds.athletes.items() if v.draft_year==year]
        folds.append(nested_fold(ds,base,groups,a,b,year,seed))
    comparisons={name:R.paired_summary(folds,b,c,seed=seed,draws=draws) for name,b,c in (
        ('reliable_vs_conventional','conventional','reliable'),
        ('raw_vs_conventional','conventional','raw'),('reliable_vs_raw','raw','reliable'))}
    return {'protocol':PROTOCOL,'include_ngs':include_ngs,'target':ds.outcome_definition,
        'comparisons':comparisons,'folds':folds,'model_fits':96}


def public_result(run):
    return {k:run[k] for k in ('protocol','include_ngs','target','comparisons','model_fits')}|{
        'folds':[{k:f[k] for k in ('year','selected','inner_mse','source_calibration','training_players','model_fits')}|{
            'evaluated_players':len(f['ids'])} for f in run['folds']]}


def repeat_prediction(ds,seed=141014):
    """Older-class calibration predicts second attempt from first for new players."""
    w,_=R.source_windows(ds);groups=vector_groups(w);folds=[]
    years=sorted({v.draft_year for v in ds.athletes.values()})
    for year in years[1:]:
        ids=[a for a,v in ds.athletes.items() if v.draft_year<year]
        m=ReliableModes.fit(groups,training_groups=ids)
        te=sorted(a for a,v in ds.athletes.items() if v.draft_year==year and len(groups.get(a,[]))>=2)
        truth=np.asarray([groups[a][1] for a in te]);raw=np.asarray([groups[a][0] for a in te])
        post=np.asarray([m.posterior([groups[a][0]])[0] for a in te]);prior=np.tile(m.mean,(len(te),1))
        folds.append({'year':year,'players':len(te),'prior_mse':float(np.mean((truth-prior)**2)),
            'raw_first_attempt_mse':float(np.mean((truth-raw)**2)),
            'posterior_mse':float(np.mean((truth-post)**2)),'source_calibration':m.receipt()})
    total=sum(f['players'] for f in folds)
    mean=lambda k:sum(f[k]*f['players'] for f in folds)/total
    return {'schema':'perfectjet/held-class-repeat-prediction/1','players':total,'folds':folds,
        'raw_mse':mean('raw_first_attempt_mse'),'posterior_mse':mean('posterior_mse'),
        'prior_mse':mean('prior_mse'),'gain_vs_raw_first_attempt':1-mean('posterior_mse')/mean('raw_first_attempt_mse'),
        'scope':'equal-player mean across three correlated acceleration coordinates; calibration on earlier classes only; a repeat-measurement prediction, not an NFL outcome gain'}
