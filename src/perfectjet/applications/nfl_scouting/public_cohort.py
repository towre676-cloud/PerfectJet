"""Public Combine-to-rookie NFL benchmark with strict IDs and temporal folds.

This is an external test of mathematical feature engineering on existing Combine
measurements. It does not contain Combine tracking or establish a sensor/get-off
advantage. All transformations use exactly the conventional source information.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math
import re
from typing import Any

BASE_NUMERIC = ('height_inches','wt','forty','bench','vertical','broad_jump','cone','shuttle','measured_count')
MECHANICAL_NUMERIC = ('a40_proxy','v40_average','shuttle_forty_ratio','cone_forty_ratio','vertical_speed_proxy','broad_height_ratio','weight_height_ratio','shuttle_cone_ratio')
DL_POSITIONS = frozenset(('DE','DT','DL','EDGE','NT'))
FRONT7_POSITIONS = DL_POSITIONS | frozenset(('OLB','ILB','LB'))
TARGETS = ('rookie_defense_snaps','rookie_sacks','rookie_qb_hits','rookie_pressures','rookie_pressures_per_100_defense_snaps')

@dataclass
class PublicCohort:
    frame: Any
    audit: dict[str, Any]
    source_files: list[dict[str, Any]]


def height_inches(value: Any) -> float:
    if value is None:return float('nan')
    match=re.fullmatch(r'(\d+)-(\d+)',str(value).strip())
    return 12*int(match[1])+int(match[2]) if match else float('nan')


def source_features(frame: Any, *, mechanical: bool = False):
    import numpy as np
    import pandas as pd
    f=frame.copy()
    if 'height_inches' not in f:f['height_inches']=f['ht'].map(height_inches)
    for c in BASE_NUMERIC[:-1]:f[c]=pd.to_numeric(f[c],errors='coerce')
    f['measured_count']=f[list(BASE_NUMERIC[:-1])].notna().sum(axis=1)
    # Constant acceleration and ballistic jump formulas are PROXIES. Timing,
    # launch, friction and technique make these nonliteral physical parameters.
    if mechanical:
        positive=lambda x:x.where(x>0)
        t=positive(f['forty']);height=positive(f['height_inches'])
        f['a40_proxy']=80/t**2
        f['v40_average']=40/t
        f['shuttle_forty_ratio']=positive(f['shuttle'])/t
        f['cone_forty_ratio']=positive(f['cone'])/t
        f['vertical_speed_proxy']=np.sqrt(2*32.174*positive(f['vertical'])/12)
        f['broad_height_ratio']=positive(f['broad_jump'])/height
        f['weight_height_ratio']=positive(f['wt'])/height
        f['shuttle_cone_ratio']=positive(f['shuttle'])/positive(f['cone'])
    cols=list(BASE_NUMERIC)+(['combine_position'])
    if mechanical:cols=list(BASE_NUMERIC)+list(MECHANICAL_NUMERIC)+['combine_position']
    return f[cols]


def _unique_mapping(players, audit):
    p=players.dropna(subset=['pfr_id','gsis_id'])[['pfr_id','gsis_id']].drop_duplicates()
    ambiguous=p.loc[p.duplicated('pfr_id',keep=False),'pfr_id'].unique()
    ambiguous_gsis=p.loc[p.duplicated('gsis_id',keep=False),'gsis_id'].unique()
    audit['ambiguous_player_crosswalk_ids']=list(ambiguous)
    audit['ambiguous_gsis_crosswalk_ids']=list(ambiguous_gsis)
    return p.loc[~p.pfr_id.isin(ambiguous) & ~p.gsis_id.isin(ambiguous_gsis)]


def _pressure_totals(pressure, audit):
    import pandas as pd
    if pressure is None or pressure.empty:return pd.DataFrame(columns=['pfr_id','season','rookie_pressures'])
    f=pressure.copy();f['prss']=pd.to_numeric(f.prss,errors='coerce')
    # Some source rows attach identical name/team/stat lines to multiple PFR IDs.
    # A public URL does not resolve that ambiguity: exclude these identities.
    signature=['season','player','tm','prss','g','sk']
    counts=f.groupby(signature,dropna=False).pfr_id.nunique()
    bad_signature=set(counts[counts>1].index)
    bad=set()
    for row in f.itertuples(index=False):
        sig=tuple(getattr(row,c) for c in signature)
        if sig in bad_signature:bad.add((row.pfr_id,row.season))
    audit['ambiguous_pressure_player_seasons_excluded']=len(bad)
    rows=[];conflicts=0
    for (pfr,season),g in f.groupby(['pfr_id','season']):
        if (pfr,season) in bad:continue
        total=g[g.tm.astype(str).str.match(r'^(?:[2-9]TM|TOT)$')]
        if not total.empty:
            if len(total)>1 and total.prss.nunique(dropna=False)>1:conflicts+=1;continue
            value=total.prss.iloc[0]
        elif len(g)==1:value=g.prss.iloc[0]
        else:
            if g.tm.duplicated().any():conflicts+=1;continue
            value=g.prss.sum(min_count=len(g))
        rows.append({'pfr_id':pfr,'season':season,'rookie_pressures':value})
    audit['conflicting_pressure_player_seasons_excluded']=conflicts
    return pd.DataFrame(rows,columns=['pfr_id','season','rookie_pressures'])


def build_cohort(combine, players, stats, snaps=None, pressure=None, *, max_complete_season=2025):
    """Join real source frames without name matching or filling absent outcomes.

    Repeated/ambiguous Combine identities are excluded. A player present with an
    explicit zero NFL count retains zero; an absent outcome remains unknown.
    Eligibility uses Combine position, never post-draft NFL role labels.
    """
    import pandas as pd
    audit={'combine_rows':len(combine),'max_complete_season':max_complete_season,
           'missing_outcomes_are_zero':False,'identity_join':'PFR ID to unique GSIS ID; no name joins',
           'outcome_window':'same-calendar-year rookie REG season',
           'outcome_scope':'conditional on explicit observed NFL outcome; absent players remain unknown',
           'predictor_availability':'Combine numeric traits and Combine position; no draft pick/career/updated NFL role'}
    c=combine.copy();c['season']=pd.to_numeric(c.season,errors='coerce')
    audit['combine_missing_pfr_id']=int(c.pfr_id.isna().sum())
    c=c.dropna(subset=['pfr_id','season']);c=c[c.season<=max_complete_season]
    # Even identical IDs attached to different positions may be two different
    # humans incorrectly linked by an upstream name match. Do not pick one.
    ambiguous=c.loc[c.duplicated('pfr_id',keep=False),'pfr_id'].unique()
    audit['ambiguous_combine_ids_excluded']=list(ambiguous)
    c=c[~c.pfr_id.isin(ambiguous)]
    c=c.merge(_unique_mapping(players,audit),on='pfr_id',how='left',validate='one_to_one')
    audit['combine_unlinked_gsis']=int(c.gsis_id.isna().sum())
    c['combine_position']=c.pos.fillna('UNKNOWN').astype(str).str.upper()
    c['height_inches']=c.ht.map(height_inches)
    s=stats[stats.season<=max_complete_season].copy()
    if 'season_type' in s:s=s[s.season_type.eq('REG')]
    if s.duplicated(['player_id','season']).any():raise ValueError('duplicate GSIS regular-season outcome')
    s=s[['player_id','season','def_sacks','def_qb_hits']].rename(columns={'player_id':'gsis_id','def_sacks':'rookie_sacks','def_qb_hits':'rookie_qb_hits'})
    if c.dropna(subset=['gsis_id']).duplicated(['gsis_id','season']).any():raise ValueError('duplicate linked original athlete')
    c=c.merge(s,on=['gsis_id','season'],how='left',validate='many_to_one')
    if snaps is not None and not snaps.empty:
        q=snaps.copy();q=q[q.season<=max_complete_season]
        if 'game_type' in q:q=q[q.game_type.eq('REG')]
        key=['pfr_player_id','pfr_game_id','team']
        if q.duplicated(key).any():raise ValueError('duplicate player/game/team snap rows')
        q['defense_snaps']=pd.to_numeric(q.defense_snaps,errors='coerce')
        q=q.groupby(['pfr_player_id','season'],as_index=False).defense_snaps.agg(lambda x:x.sum(min_count=len(x)))
        q=q.rename(columns={'pfr_player_id':'pfr_id','defense_snaps':'rookie_defense_snaps'})
        c=c.merge(q,on=['pfr_id','season'],how='left',validate='one_to_one')
    else:c['rookie_defense_snaps']=float('nan')
    p=_pressure_totals(pressure,audit)
    c=c.merge(p,on=['pfr_id','season'],how='left',validate='one_to_one')
    c['rookie_pressures_per_100_defense_snaps']=100*c.rookie_pressures/c.rookie_defense_snaps.where(c.rookie_defense_snaps>0)
    audit['linked_cohort_rows']=len(c)
    audit['observed_target_counts']={t:int(c[t].notna().sum()) for t in TARGETS}
    audit['dl_observed_target_counts']={t:int(c.loc[c.combine_position.isin(DL_POSITIONS),t].notna().sum()) for t in TARGETS}
    return PublicCohort(c,audit,[])


def load_public_cohort(root, *, max_complete_season=2025, verify_hashes=True):
    import pandas as pd
    r=Path(root);manifest=json.loads((r/'manifest.json').read_text())
    files={x['path']:x for x in manifest['files'] if 'error' not in x}
    used=[]
    def read(path):
        p=r/path
        if path not in files:raise ValueError(f'unmanifested source: {path}')
        if verify_hashes and hashlib.sha256(p.read_bytes()).hexdigest()!=files[path]['sha256']:raise ValueError(f'source hash mismatch: {path}')
        used.append(files[path]);return pd.read_csv(p,low_memory=False)
    combine=read('combine/combine.csv');players=read('players/players.csv')
    stats=pd.concat([read(p) for p in sorted(files) if re.fullmatch(r'stats_player_reg/stats_player_reg_\d{4}\.csv.gz',p) and int(p[-11:-7])<=max_complete_season],ignore_index=True)
    snap_paths=[p for p in sorted(files) if re.fullmatch(r'snap_counts/snap_counts_\d{4}\.csv.gz',p) and int(p[-11:-7])<=max_complete_season]
    snaps=pd.concat([read(p) for p in snap_paths],ignore_index=True) if snap_paths else None
    pressure=read('pfr_advstats/advstats_season_def.csv') if 'pfr_advstats/advstats_season_def.csv' in files else None
    cohort=build_cohort(combine,players,stats,snaps,pressure,max_complete_season=max_complete_season)
    cohort.source_files=used
    return cohort


def _pipeline(kind, alpha, *, draft_sensitivity=False):
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler, PolynomialFeatures
    numeric=list(BASE_NUMERIC)+(list(MECHANICAL_NUMERIC) if kind=='mechanical' else [])
    if draft_sensitivity:numeric+=['draft_ovr']
    num=[('impute',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)),('scale',StandardScaler())]
    prep=ColumnTransformer([('numeric',Pipeline(num),numeric),('position',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['combine_position'])])
    steps=[('prepare',prep)]
    # Full conventional quadratic includes numeric-by-position interactions.
    # Omitting these would make a mixed-role gain too easy to misinterpret.
    if kind=='quadratic':steps += [('quadratic',PolynomialFeatures(degree=2,include_bias=False)),('scale2',StandardScaler())]
    return Pipeline(steps+[('ridge',Ridge(alpha=float(alpha)))])


def _select(x,y,years,kind,alphas,minimum_train,minimum_test, *, draft_sensitivity=False):
    import numpy as np
    inner_years=[int(v) for v in sorted(set(years)) if sum(years<v)>=minimum_train and sum(years==v)>=minimum_test][-3:]
    if not inner_years:return float(max(alphas)),None,[]
    receipts=[]
    for alpha in alphas:
        errors=[]
        for year in inner_years:
            tr=years<year;te=years==year
            model=_pipeline(kind,alpha,draft_sensitivity=draft_sensitivity).fit(x.loc[tr],y[tr])
            pred=np.maximum(0,model.predict(x.loc[te]));errors.extend(((pred-y[te])**2).tolist())
        receipts.append((float(np.mean(errors)),float(alpha)))
    mse,alpha=min(receipts,key=lambda p:(p[0],-p[1]))
    return alpha,mse,inner_years


def _metrics(y,pred,threshold):
    import numpy as np
    from scipy.stats import spearmanr
    mse=float(np.mean((y-pred)**2));k=max(1,math.ceil(len(y)*.25))
    order=np.argsort(-pred,kind='stable')[:k]
    rank=float(spearmanr(y,pred).statistic) if np.ptp(y)>0 and np.ptp(pred)>0 else None
    return {'mse':mse,'rmse':math.sqrt(mse),'mae':float(np.mean(abs(y-pred))), 'spearman':rank,
            'shortlist_k':k,'shortlist_precision_at_training_top_quartile':float(np.mean(y[order]>=threshold)),
            'shortlist_mean_actual_outcome':float(np.mean(y[order]))}


def run_public_benchmark(cohort, *, targets=TARGETS, position_scope='DL', test_min_year=2016,
                         minimum_train=100,minimum_test=15,alphas=(.1,1,10,100,1000),
                         bootstrap_draws=1000,seed=271828,draft_sensitivity=False):
    """Expanding draft-class holdouts; all tuning uses earlier draft classes.

    Main baseline is picked between raw and quadratic conventional models by
    inner temporal MSE, never by outer-test performance. Mechanical transforms
    add no source information. Each athlete contributes one paired error.
    """
    import numpy as np
    from sklearn.metrics import mean_squared_error
    f=cohort.frame.copy()
    if position_scope=='DL':f=f[f.combine_position.isin(DL_POSITIONS)]
    elif position_scope=='FRONT7':f=f[f.combine_position.isin(FRONT7_POSITIONS)]
    elif position_scope!='ALL':raise ValueError('position_scope must be DL, FRONT7 or ALL')
    if f.pfr_id.duplicated().any():raise ValueError('an original athlete occurs more than once')
    conventional=source_features(f)
    mechanical=source_features(f,mechanical=True)
    if draft_sensitivity:
        # Draft position is post-Combine information. Undrafted is missing, not
        # pick 999. This sensitivity is explicitly separate from predraft use.
        conventional['draft_ovr']=f.draft_ovr;mechanical['draft_ovr']=f.draft_ovr
    out={'schema':'perfectjet-public-cohort/1','source':'REAL public NFL/nflverse observations',
         'new_sensor_information':False,'mechanical_features_are_deterministic_functions_of_baseline':True,
         'claim_scope':'external Combine feature-engineering benchmark; not a get-off or tracking-transfer advantage',
         'position_scope':position_scope,'draft_pick_sensitivity':draft_sensitivity,'audit':cohort.audit,
         'protocol':{'test_min_year':test_min_year,'minimum_train':minimum_train,'minimum_test':minimum_test,
                     'alphas':list(alphas),'inner_folds':'last three eligible earlier draft classes',
                     'baseline_selection':'earlier-class raw vs quadratic MSE','quadratic_basis':'degree-two expansion across scaled numeric traits, missingness indicators and Combine-position one-hot indicators; includes numeric-by-position interactions','missing_target_policy':'exclude unknown; retain explicit zero',
                     'bootstrap':'fixed-prediction class-plus-player paired resampling; does not refit models','bootstrap_draws':bootstrap_draws},
         'source_files':cohort.source_files,'targets':{}}
    for target in targets:
        if target not in TARGETS:raise ValueError('undeclared target')
        observed=f[target].notna().to_numpy();g=f.loc[observed].copy()
        x=conventional.loc[observed];xm=mechanical.loc[observed]
        y=g[target].to_numpy(float);years=g.season.to_numpy(int)
        folds=[];predictions=[]
        for year in sorted(set(years)):
            if year<test_min_year:continue
            tr=years<year;te=years==year
            if sum(tr)<minimum_train or sum(te)<minimum_test:continue
            selections={}
            for kind in ('raw','quadratic','mechanical'):
                frame=xm if kind=='mechanical' else x
                selections[kind]=_select(frame.loc[tr],y[tr],years[tr],kind,alphas,minimum_train,minimum_test,draft_sensitivity=draft_sensitivity)
            # A missing inner estimate carries no evidence against the stronger
            # nonlinear conventional control: default to quadratic.
            rawcv=selections['raw'][1];quadcv=selections['quadratic'][1]
            chosen='raw' if rawcv is not None and quadcv is not None and rawcv<quadcv else 'quadratic'
            preds={}
            for kind in ('raw','quadratic','mechanical'):
                frame=xm if kind=='mechanical' else x
                model=_pipeline(kind,selections[kind][0],draft_sensitivity=draft_sensitivity).fit(frame.loc[tr],y[tr])
                preds[kind]=np.maximum(0,model.predict(frame.loc[te]))
            threshold=float(np.quantile(y[tr],.75));metrics={kind:_metrics(y[te],p,threshold) for kind,p in preds.items()}
            metrics['selected_baseline']=metrics[chosen]
            bm=metrics[chosen]['mse'];gain=1-metrics['mechanical']['mse']/bm if bm else None
            folds.append({'year':int(year),'train_players':int(sum(tr)),'test_players':int(sum(te)),
                          'training_target_75pct':threshold,'selected_baseline':chosen,'metrics':metrics,
                          'mechanical_mse_gain':gain,'selected_alpha':{k:v[0] for k,v in selections.items()},
                          'inner_cv_mse':{k:v[1] for k,v in selections.items()},'inner_years':{k:v[2] for k,v in selections.items()}})
            for j,(pfr,truth) in enumerate(zip(g.loc[te,'pfr_id'],y[te])):
                predictions.append({'pfr_id':pfr,'year':int(year),'actual':float(truth),
                                    'baseline':float(preds[chosen][j]),'raw':float(preds['raw'][j]),
                                    'quadratic':float(preds['quadratic'][j]),'mechanical':float(preds['mechanical'][j])})
        if not predictions:
            out['targets'][target]={'observed_players':len(g),'status':'insufficient temporal support','folds':[]};continue
        actual=np.array([r['actual'] for r in predictions]);b=np.array([r['baseline'] for r in predictions]);m=np.array([r['mechanical'] for r in predictions])
        bm=float(mean_squared_error(actual,b));mm=float(mean_squared_error(actual,m))
        e=(actual-b)**2-(actual-m)**2;labels=np.array([r['year'] for r in predictions]);classes=sorted(set(labels));rng=np.random.default_rng(seed)
        draws=[]
        for _ in range(bootstrap_draws):
            indices=np.concatenate([rng.choice(np.flatnonzero(labels==year),sum(labels==year),replace=True) for year in rng.choice(classes,len(classes),replace=True)])
            bd=float(np.mean((actual[indices]-b[indices])**2));md=float(np.mean((actual[indices]-m[indices])**2))
            if bd>0:draws.append(1-md/bd)
        ci=[float(v) for v in np.quantile(draws,[.025,.975])] if draws else None
        out['targets'][target]={'observed_players':len(g),'evaluated_players':len(predictions),'evaluated_classes':len(classes),
                               'baseline_mse':bm,'mechanical_mse':mm,'mse_gain':1-mm/bm if bm else None,
                               'fixed_prediction_paired_bootstrap_95pct_gain':ci,
                               'positive_classes':sum((v['mechanical_mse_gain'] or 0)>0 for v in folds),
                               'mean_paired_squared_error_reduction':float(np.mean(e)),
                               'folds':folds,'predictions':predictions}
    return out
