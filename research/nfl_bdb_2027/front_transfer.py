"""Defensive-front scouting transfer: drill geometry beyond timed/body baselines."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from scipy.signal import savgol_filter
from sklearn.linear_model import Ridge
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor,ExtraTreesRegressor
import analysis as A,repo_predict as R,observability as O,turn_transfer as T
from mechanism import player_splits

POSITIONS=['DE','DT','NT','OLB']
DRILLS=['PASS_RUSH_DRILL','RUN_THE_HOOP_DRILL','FOUR_BAG_AGILITY_DRILL','FRONT_START_WAVE_DRILL_AND_LATERAL_REACTION']
NUM=['down','yards_to_go','yardline_number','pre_snap_home_score','pre_snap_visitor_score','quarter','snap_depth','snap_width','snap_speed']
CAT=['nfl_position','lined_up_position','offense_formation','blitzing','team_abbr','possession_team']
SEED=A.SEED+3300

def skill_features(g,onset_speed=.5):
    g=g.sort_values('time');t=pd.to_datetime(g.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9;t-=t[0];s=g.s.to_numpy(float)
    if len(g)<16 or not np.allclose(np.diff(t),.1,atol=.015) or not np.isfinite(s).all():raise ValueError('short_irregular_nonfinite')
    # Fixed sustained motion onset, not a presumed official start cue.
    on=next((i for i in range(len(s)-2) if np.all(s[i:i+3]>onset_speed)),None)
    if on is None or len(s)-on<16:raise ValueError('no_complete_active_window')
    stop=min(len(s),on+51);p=g[['x','y']].to_numpy(float)[on:stop]
    if not np.isfinite(p).all():raise ValueError('nonfinite_xy')
    p=savgol_filter(p,7,3,axis=0);v=np.gradient(p,.1,axis=0);sp=s[on:stop];a=np.gradient(sp,.1);length=np.linalg.norm(np.diff(p,axis=0),axis=1);arc=np.r_[0,np.cumsum(length)];theta=np.unwrap(np.arctan2(v[:,1],v[:,0]));w=np.gradient(theta,.1);valid=np.linalg.norm(v,axis=1)>1
    first=min(16,len(sp));z=sp[:first];at=a[:first];mid=(z[:-1]+z[1:])/2;da=np.diff(at);ma=(at[:-1]+at[1:])/2;ds=np.diff(z)
    f={'speed_05':float(sp[5]),'speed_10':float(sp[10]),'speed_15':float(sp[15]),'accel_early':float(np.mean(a[1:6])),'peak_speed':float(np.quantile(sp,.95)),'braking':float(np.trapezoid(np.maximum(-a,0),dx=.1)),'turn_work':float(np.sum(np.abs(w[valid])*sp[valid])*.1),'bend_energy':float(np.sum(w[valid]**2/np.maximum(sp[valid],1))*.1),'straightness':float(np.linalg.norm(p[-1]-p[0])/max(arc[-1],1e-9)),'speed_accel_area':float(np.sum(mid*da-ma*ds)/2),'jerk_rms':float(np.sqrt(np.mean(np.gradient(a,.1)**2)))}
    for dist in [1,3,5]:f['time_'+str(dist)+'yd']=float(np.interp(dist,arc,np.arange(len(arc))*.1)) if arc[-1]>=dist else np.nan
    return f

def prepare(data,out):
    data,out=Path(data),Path(out);out.mkdir(exist_ok=True);p=pd.read_csv(data/'players.csv');phys=pd.read_csv(data/'combine_results.csv');ids=set(p.loc[p.nfl_position.isin(POSITIONS),'nfl_id']);tr=pd.read_csv(data/'combine_tracking.csv');tr=tr[tr.nfl_id.isin(ids)&tr.entity_type.eq('PLAYER')];sprints=[];skills=[];reject={}
    for key,g in tr.groupby(['nfl_id','draft_year','event_id'],sort=True):
        drill=g.drill_name.iloc[0]
        try:
            if drill=='FORTY_YARD_DASH':f,_=O.sprint_features(g);sprints.append(dict(nfl_id=key[0],draft_year=key[1],event_id=key[2],**f))
            elif drill in DRILLS:f=skill_features(g);skills.append(dict(nfl_id=key[0],draft_year=key[1],event_id=key[2],drill_name=drill,**f))
        except ValueError as e:reject[str(e)]=reject.get(str(e),0)+1
    sp=pd.DataFrame(sprints);sk=pd.DataFrame(skills);sprintcols=[c for c in sp if c.startswith('motion__')];panel=sp.groupby(['nfl_id','draft_year'])[sprintcols].median()
    values=[c for c in sk if c not in ['nfl_id','draft_year','event_id','drill_name']];wide=sk.groupby(['nfl_id','draft_year','drill_name'])[values].median().unstack('drill_name');wide.columns=['skill__'+drill+'__'+name for name,drill in wide.columns];panel=wide.join(panel,how='outer').reset_index();motioncols=sprintcols+list(wide.columns)
    d=pd.read_csv(data/'player_play.csv').merge(p[['nfl_id','draft_year','nfl_position']],on='nfl_id',validate='many_to_one').merge(pd.read_csv(data/'games.csv'),on='game_id',validate='many_to_one').merge(phys,on=['nfl_id','draft_year'],validate='many_to_one').merge(panel,on=['nfl_id','draft_year'],validate='many_to_one')
    d=d[d.nfl_position.isin(POSITIONS)&d.season.eq(d.draft_year)&d.season_type.eq('REG')&d.play_nullified_by_penalty.eq('N')&np.isfinite(d.player_get_off)&d.nfl_id.isin(panel.nfl_id)].copy();counts=d.groupby('nfl_id').size();d=d[d.nfl_id.isin(counts[counts>=30].index)].reset_index(drop=True)
    snaps=[]
    for year in [2023,2024,2025]:
        keys=d.loc[d.draft_year.eq(year),['game_id','play_id','nfl_id']]
        for chunk in pd.read_csv(data/f'game_tracking_{year}.csv',chunksize=250000):
            q=chunk[chunk.event.eq('ball_snap')].merge(keys,on=['game_id','play_id','nfl_id'],validate='many_to_one')
            if len(q):snaps.append(q[['game_id','play_id','nfl_id','x','y','s']])
        print('Front snap extraction',year,flush=True)
    snap=pd.concat(snaps);counts=snap.groupby(['game_id','play_id','nfl_id']).size();unique=counts[counts.eq(1)].index;snap=snap.set_index(['game_id','play_id','nfl_id']).loc[unique].reset_index();d=d.merge(snap,on=['game_id','play_id','nfl_id'],validate='one_to_one');yards=np.where(d.yardline_side.eq(d.possession_team),d.yardline_number,100-d.yardline_number);right=d.play_direction.eq('right');los=np.where(right,10+yards,110-yards);d['snap_depth']=(d.x-los)*np.where(right,1,-1);d['snap_width']=np.abs(d.y-80/3);d['snap_speed']=d.s;d['pressure_event']=d.time_to_pressure.notna().astype(float)
    # Reapply the same threshold after missing/nonunique snap exclusion.
    counts=d.groupby('nfl_id').size();d=d[d.nfl_id.isin(counts[counts>=30].index)].reset_index(drop=True);d.to_pickle(out/'private_rows.pkl');sp.to_pickle(out/'private_sprints.pkl');sk.to_pickle(out/'private_skills.pkl')
    audit={'positions':POSITIONS,'sprint_attempts':len(sp),'skill_attempts':len(sk),'source_rejections':reject,'source_features':motioncols,'players_by_year':{str(k):int(v) for k,v in d.groupby('draft_year').nfl_id.nunique().items()},'rush_records_by_year':{str(k):int(v) for k,v in d.groupby('draft_year').size().items()},'pressure_observed_fraction':float(d.pressure_event.mean()),'snap_depth_range':d.snap_depth.quantile([0,.01,.5,.99,1]).to_dict(),'eligibility':'Rookie REG, non-nullified, finite charted player_get_off, source profile, unique ball_snap and >=30 records/player','target_scope':'Charted get-off and observed time_to_pressure indicator among charted get-off records. Not an unconditional pass-rush survival model.'};(out/'population.json').write_text(json.dumps(audit,indent=2));return d,motioncols,audit

def fit_predict(tr,te,cols,config,target,availability=True,return_predictor=False):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('player leakage')
    units=tr.drop_duplicates('nfl_id');phys=T.numeric().fit(units[R.PHYS]);num=T.numeric().fit(tr[NUM]);cat=T.OneHotEncoder(handle_unknown='ignore',sparse_output=False).fit(tr[CAT].fillna('MISSING').astype(str))
    sourcegroups=[['motion__'],*[[f'skill__{name}__'] for name in DRILLS]]
    def presence(x):return np.c_[[x[[c for c in x if any(c.startswith(prefix) for prefix in group)]].notna().any(axis=1).to_numpy(float) for group in sourcegroups]].T
    def base(x):
        b=np.c_[phys.transform(x[R.PHYS]),num.transform(x[NUM]),cat.transform(x[CAT].fillna('MISSING').astype(str))]
        return np.c_[b,presence(x)] if availability else b
    x,y=base(tr),base(te)
    if cols:
        scaler=T.numeric().fit(units[cols]);z=scaler.transform(units[cols]);residual=Ridge(alpha=10).fit(phys.transform(units[R.PHYS]),z);z-=residual.predict(phys.transform(units[R.PHYS]));pca=PCA(n_components=min(config['k'],len(units)-1,z.shape[1]),svd_solver='full').fit(z)
        def motion(d):
            z=pca.transform(scaler.transform(d[cols])-residual.predict(phys.transform(d[R.PHYS])));mass=phys.transform(d[R.PHYS])[:,R.PHYS.index('combine_weight')];return np.c_[z,z*z,z*mass[:,None]]
        x=np.c_[x,motion(tr)];y=np.c_[y,motion(te)]
    if config['reg']=='ridge':reg=Ridge(alpha=config['alpha'])
    elif config['reg']=='forest':reg=RandomForestRegressor(n_estimators=120,max_depth=6,min_samples_leaf=30,max_features=.8,n_jobs=2,random_state=SEED)
    else:reg=ExtraTreesRegressor(n_estimators=120,max_depth=8,min_samples_leaf=30,max_features=.8,n_jobs=2,random_state=SEED)
    reg.fit(x,tr[target],sample_weight=A.weights(tr))
    def fitted_predict(d):
        z=base(d)
        if cols:z=np.c_[z,motion(d)]
        p=reg.predict(z);return np.clip(p,0,1) if target=='pressure_event' else p
    return fitted_predict if return_predictor else fitted_predict(te)

CONFIGS=[{'reg':'ridge','alpha':a,'k':k} for a,k in [(1,4),(10,4),(100,6)]]+[{'reg':'forest','alpha':0,'k':4},{'reg':'extra','alpha':0,'k':6}]

def selection_score(rows,p,target,objective):
    if objective=='play':return O.score(rows,p,target)
    q=pd.DataFrame({'nfl_id':rows.nfl_id,'truth':rows[target],'prediction':p}).groupby('nfl_id').mean();return float(np.mean((q.truth-q.prediction)**2))

def experiment(d,cols,out,target,seed=SEED,forward=True,availability=True,objective='play'):
    out=Path(out)/target;out.mkdir(parents=True,exist_ok=True);dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);test=d[d.draft_year.eq(2025)].reset_index(drop=True);families={'conventional':[],'sprint':[c for c in cols if c.startswith('motion__')],'skills':[c for c in cols if c.startswith('skill__')],'combined':cols};pred={k:np.zeros(len(dev)) for k in families};tp={};folds=[];selection=[]
    for fold,(i,j) in enumerate(player_splits(dev,4,seed)):
        tr=dev.iloc[i].reset_index(drop=True);te=dev.iloc[j]
        for family,cc in families.items():
            loss=[np.mean([selection_score(tr.iloc[b],fit_predict(tr.iloc[a],tr.iloc[b],cc,c,target,availability),target,objective) for a,b in player_splits(tr,3,seed+1+fold)]) for c in CONFIGS];ci=int(np.argmin(loss));pred[family][j]=fit_predict(tr,te,cc,CONFIGS[ci],target,availability);folds.append({'fold':fold,'family':family,'config':ci,'inner_loss':list(map(float,loss)),'train_player_hash':hashlib.sha256(json.dumps(sorted(map(int,tr.nfl_id.unique()))).encode()).hexdigest()});print(target,objective,fold,family,ci,flush=True)
    r={'target':target,'seed':seed,'selection_objective':objective,'folds':folds,'source_availability_in_every_baseline':availability,'conditional_player_weighting':True,'prior_global_2025_WR_DB_inspection':True,'DL_model_selection_2025_used':False}
    if forward:
        tr=dev[dev.draft_year.eq(2023)];va=dev[dev.draft_year.eq(2024)]
        for family,cc in families.items():
            loss=[selection_score(va,fit_predict(tr,va,cc,c,target,availability),target,objective) for c in CONFIGS];ci=int(np.argmin(loss));tp[family]=fit_predict(dev,test,cc,CONFIGS[ci],target,availability);selection.append({'family':family,'config':ci,'validation_loss':loss})
        r['selection']=selection
    for label,rows,pp in [('nested',dev,pred)]+([('exploratory_2025',test,tp)] if forward else []):
        r[label]={'mse':{k:O.score(rows,p,target) for k,p in pp.items()},'comparisons':{k:O.interval(rows,pp['conventional'],p,target) for k,p in pp.items() if k!='conventional'},'players':int(rows.nfl_id.nunique()),'rows':len(rows)}
        q=rows[['nfl_id','game_id','play_id',target]].copy()
        for k,v in pp.items():q[k]=v
        q.to_pickle(out/f'private_{label}.pkl')
    (out/'results.json').write_text(json.dumps(r,indent=2));return r

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--data',default='data');p.add_argument('--out',default='private_front');args=p.parse_args();d,cols,audit=prepare(args.data,args.out)
    for target in ['player_get_off','pressure_event']:experiment(d,cols,args.out,target)
