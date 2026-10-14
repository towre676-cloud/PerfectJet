#!/usr/bin/env python3
"""Private-data adapter and honest player-held-out movement transfer experiment.

Writes athlete-level data only to --private-out. Public aggregate receipt is
separate. Existing parallel experiments are read-only inputs, never overwritten.
"""
import argparse,json,sys,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
import numpy as np,pandas as pd
from perfectpower.movement_features import ensemble_features
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold

DRILLS=['PASS_RUSH_DRILL','RUN_THE_HOOP_DRILL','FOUR_BAG_AGILITY_DRILL','FRONT_START_WAVE_DRILL_AND_LATERAL_REACTION']
PHYS=['combine_height','combine_weight','hand_size','arm_length','wing_span','ten_yd_split','forty','vertical','broad_jump','three_cone','short_shuttle','bench_reps','ngs_athleticism_score','ngs_college_production_score','ngs_final_score']
FAMILIES={'kinematic':['path_length','peak_speed','speed_gain','mean_acceleration','braking_impulse','turn_work'],
          'ordered':['order_area_','order_triple_'],
          'uncertain':['recovery_accel','brake_accel','redirect_turn','phase_duration_','phase_sd_','phase_boundary_width_','phase_entropy_per_frame','onset_range_']}


def extract(data,cohort,dest):
    started=time.perf_counter();dest.mkdir(parents=True,exist_ok=True);x=pd.read_pickle(cohort)
    if not {'nfl_id','draft_year','pressure_event','nfl_position'}<=set(x):raise ValueError('cohort schema')
    tracking=pd.read_csv(data/'combine_tracking.csv');tracking=tracking[tracking.nfl_id.isin(x.nfl_id)&tracking.entity_type.eq('PLAYER')&tracking.drill_name.isin(DRILLS)]
    rows=[];reject={};attempts=0;populations=[]
    for key,g in tracking.groupby(['nfl_id','draft_year','event_id'],sort=True):
        attempts+=1;g=g.sort_values('time');t=pd.to_datetime(g.time);seconds=(t-t.iloc[0]).dt.total_seconds().to_numpy()
        try:f,a=ensemble_features(seconds,g[['x','y']].to_numpy(),g.s.to_numpy())
        except ValueError as error:reject[str(error)]=reject.get(str(error),0)+1;continue
        rows.append({'nfl_id':key[0],'draft_year':key[1],'event_id':key[2],'drill_name':g.drill_name.iloc[0],**f})
        populations.extend(int(s['population']) for s in a['scenarios'] if 'population' in s)
        if len(rows)%50==0:print(json.dumps({'attempts':attempts,'accepted':len(rows),'seconds':time.perf_counter()-started}),flush=True)
    if not rows:raise ValueError('no eligible attempts')
    events=pd.DataFrame(rows);events.to_pickle(dest/'events.pkl')
    featurecols=[c for c in events if c not in ('nfl_id','draft_year','event_id','drill_name')]
    wide=events.groupby(['nfl_id','draft_year','drill_name'])[featurecols].median().unstack('drill_name');wide.columns=[f'movement__{drill}__{name}' for name,drill in wide.columns]
    unit=x.groupby(['nfl_id','draft_year'],sort=True).pressure_event.agg(['mean','count']).rename(columns={'mean':'target','count':'exposure'}).reset_index()
    numeric=[c for c in PHYS if c in x and pd.api.types.is_numeric_dtype(x[c])]
    for c in numeric:unit[c]=unit.set_index(['nfl_id','draft_year']).index.map(x.groupby(['nfl_id','draft_year'])[c].first()).to_numpy()
    unit=unit.merge(x[['nfl_id','draft_year','nfl_position']].drop_duplicates(),on=['nfl_id','draft_year'],validate='one_to_one').merge(wide.reset_index(),on=['nfl_id','draft_year'],how='left',validate='one_to_one')
    for drill in DRILLS:
        cols=[c for c in unit if c.startswith('movement__'+drill+'__')];unit['available__'+drill]=unit[cols].notna().any(axis=1).astype(float) if cols else 0.
    unit.to_pickle(dest/'players.pkl')
    receipt={'input_cohort_sha256':hashlib.sha256(cohort.read_bytes()).hexdigest(),'source_tracking_sha256':hashlib.sha256((data/'combine_tracking.csv').read_bytes()).hexdigest(),
        'source_attempts':attempts,'accepted_attempts':len(events),'source_rejections':reject,'players':len(unit),'players_by_year':{str(k):int(v) for k,v in unit.groupby('draft_year').size().items()},
        'phase_populations_min':str(min(populations)),'phase_populations_max':str(max(populations)),'scenarios':len(populations),'extract_seconds':time.perf_counter()-started,
        'target':'Mean observed pressure indicator in the supplied eligible rookie rush cohort; conditional, not unconditional career success.',
        'onset_weights':'Equal source-only sensitivity scenarios .5,1,2 yd/s; not calibrated phase probabilities','frame_scope':'Up to first 61 contiguous 10Hz active frames. Gaps rejected. Four operational ordered phase templates, not labeled physiology.'}
    (dest/'extraction.json').write_text(json.dumps(receipt,indent=2)+'\n');return unit,receipt


def model_predict(train,test,cols,alpha,k):
    if set(train.nfl_id)&set(test.nfl_id):raise ValueError('athlete leakage')
    basecols=[c for c in PHYS if c in train]+[c for c in train if c.startswith('available__')]
    imp=SimpleImputer(strategy='median',keep_empty_features=True);sc=StandardScaler();b=sc.fit_transform(imp.fit_transform(train[basecols]));bt=sc.transform(imp.transform(test[basecols]))
    enc=OneHotEncoder(handle_unknown='ignore',sparse_output=False);b=np.c_[b,enc.fit_transform(train[['nfl_position']])];bt=np.c_[bt,enc.transform(test[['nfl_position']])]
    if cols and k:
        mi=SimpleImputer(strategy='median',keep_empty_features=True);ms=StandardScaler();m=ms.fit_transform(mi.fit_transform(train[cols]));mt=ms.transform(mi.transform(test[cols]))
        # Residualize measured movement against conventional traits inside fold.
        nuisance=Ridge(alpha=10).fit(b,m);m-=nuisance.predict(b).reshape(m.shape);mt-=nuisance.predict(bt).reshape(mt.shape)
        pca=PCA(n_components=min(k,len(train)-1,len(cols)),svd_solver='full');m=pca.fit_transform(m);mt=pca.transform(mt)
        b=np.c_[b,m];bt=np.c_[bt,mt]
    fitted=Ridge(alpha=alpha).fit(b,train.target)
    return np.clip(fitted.predict(bt),0,1)


def bank():return [(a,k) for a in (1.,10.,100.) for k in (0,2,4)]

def select(train,cols,seed):
    folds=list(KFold(n_splits=min(3,len(train)),shuffle=True,random_state=seed).split(train))
    losses=[]
    for a,k in bank():losses.append(float(np.mean([np.mean((train.iloc[j].target-model_predict(train.iloc[i],train.iloc[j],cols,a,k))**2) for i,j in folds])))
    ix=int(np.argmin(losses));return bank()[ix],losses


def compare(truth,base,candidate,seed=717):
    d=(truth-base)**2-(truth-candidate)**2;rng=np.random.default_rng(seed);b=rng.integers(0,len(d),size=(4000,len(d)));samples=d[b].mean(axis=1)
    bm=float(np.mean((truth-base)**2));cm=float(np.mean((truth-candidate)**2))
    return {'baseline_mse':bm,'candidate_mse':cm,'relative_gain':(bm-cm)/bm if bm else None,'absolute_gain':float(d.mean()),'athlete_bootstrap_95':np.quantile(samples,[.025,.975]).tolist(),'interval_scope':'Conditional on retained fitted predictions; does not include refitting or multiplicity across adaptive prior experiments','players':len(d)}


def evaluate(unit,out):
    if not set(PHYS)<=set(unit):raise ValueError('complete conventional baseline columns required')
    allcols=[c for c in unit if c.startswith('movement__')];families={'conventional':[]}
    for name,prefixes in FAMILIES.items():families[name]=[c for c in allcols if any(c.split('__')[-1].startswith(p) for p in prefixes)]
    families['combined']=sorted(set(sum([families[k] for k in FAMILIES],[])))
    dev=unit[unit.draft_year.isin([2023,2024])].reset_index(drop=True);test=unit[unit.draft_year.eq(2025)].reset_index(drop=True)
    if len(dev)<12 or not len(test):raise ValueError('insufficient cohort for declared splits')
    predictions={name:np.zeros(len(dev)) for name in families};selection=[]
    for fold,(i,j) in enumerate(KFold(n_splits=4,shuffle=True,random_state=714).split(dev)):
        for name,cols in families.items():
            config,loss=select(dev.iloc[i],cols,800+fold);predictions[name][j]=model_predict(dev.iloc[i],dev.iloc[j],cols,*config)
            selection.append({'outer_fold':fold,'family':name,'config':config,'inner_mse':loss});print(json.dumps({'fold':fold,'family':name}),flush=True)
    future={};forward=[];tr=dev[dev.draft_year.eq(2023)];va=dev[dev.draft_year.eq(2024)]
    for name,cols in families.items():
        losses=[float(np.mean((va.target-model_predict(tr,va,cols,*c))**2)) for c in bank()];ix=int(np.argmin(losses));future[name]=model_predict(dev,test,cols,*bank()[ix]);forward.append({'family':name,'config':bank()[ix],'validation_mse':losses})
    results={'schema':'pp-movement-transfer/1','baseline_columns':PHYS,'families':{k:len(v) for k,v in families.items()},'nested_selection':selection,'forward_selection':forward,
        'split_scope':'Entire athletes held out. Imputation, scales, residualization, PCA and alpha selected within training folds. Forward choices use 2023→2024 only.',
        '2025_scope':'Exploratory reuse: this draft class has already been inspected in parallel experiments. No untouched external-test or competition-win claim.',
        'baseline_fallback':True,'model_scope':'Equal-player conditional pressure-rate regression. Known NFL position and Combine/source availability included. No NFL-derived movement covariate or outcome enters extraction.'}
    for label,rows,pp in [('nested_2023_2024',dev,predictions),('exploratory_2025',test,future)]:
        results[label]={name:compare(rows.target.to_numpy(),pp['conventional'],p) for name,p in pp.items() if name!='conventional'}
        q=rows[['nfl_id','draft_year','target','exposure']].copy()
        for name,p in pp.items():q[name]=p
        q.to_pickle(out/(label+'.pkl'))
    return results


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--cohort',type=Path,required=True);p.add_argument('--private-out',type=Path,required=True);p.add_argument('--aggregate',type=Path,required=True);p.add_argument('--reuse',action='store_true');a=p.parse_args()
    if a.reuse:unit=pd.read_pickle(a.private_out/'players.pkl');ex=json.loads((a.private_out/'extraction.json').read_text())
    else:unit,ex=extract(a.data,a.cohort,a.private_out)
    result=evaluate(unit,a.private_out);result['extraction']=ex;a.aggregate.parent.mkdir(parents=True,exist_ok=True);a.aggregate.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('nested_2023_2024','exploratory_2025')}))
if __name__=='__main__':main()
