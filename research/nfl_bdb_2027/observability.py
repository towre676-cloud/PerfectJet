"""Reconstructed movement-observability protocol. Prior WR 2025 results exploratory.

All transformations and model selection fit on training players only. Intermediate
player rows remain private. Reconstructed implementation is not byte-identical to
the lost implementation; population and prediction differences are reported.
"""
from pathlib import Path
import json, hashlib, time
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.signal import savgol_filter
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
import analysis as A
import repo_predict as R
from mechanism import player_splits

PREFIX=['snap_speed','early_speed','early_acceleration','early_distance']
CONFIGS=R.CONFIGS

def response(t,V,tau,delay,order):
    z=np.maximum((np.asarray(t)-delay)/tau,0)
    return V*(1-np.exp(-z)*(1+z if order==2 else 1))

def sprint_features(g):
    g=g.sort_values('time');t=pd.to_datetime(g.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9;t-=t[0]
    if len(t)<31 or not np.allclose(np.diff(t),.1,atol=.015):raise ValueError('short or irregular sprint')
    s=g.s.to_numpy(float)
    if not np.isfinite(s).all() or t[-1]<3:raise ValueError('invalid speed')
    s=savgol_filter(s,7,3);f={}
    for order in (1,2):
        fit=least_squares(lambda z:response(t,*z,order)-s,[12,1,-.1],bounds=([6,.1,-1],[20,4,1]),max_nfev=400)
        for name,value in zip(['V','tau','delay'],fit.x):f[f'motion__order{order}_{name}']=float(value)
        f[f'motion__order{order}_rmse']=float(np.sqrt(np.mean(fit.fun**2)))
        f[f'motion__order{order}_condition']=float(np.linalg.cond(fit.jac))
    for tt in [.5,1,1.5,2,2.5,3]:f[f'motion__speed_{tt}']=float(np.interp(tt,t,s))
    acceleration=np.gradient(s,.1)
    for tt in [.5,1,1.5,2]:f[f'motion__acceleration_{tt}']=float(np.interp(tt,t,acceleration))
    profile=np.interp(np.linspace(0,3,31),t,s)
    for i,value in enumerate(np.polynomial.legendre.legfit(np.linspace(-1,1,31),profile,4)):f[f'motion__legendre_{i}']=float(value)
    f['motion__speed_ratio']=float(np.interp(1,t,s)/max(np.interp(3,t,s),1e-9))
    return f,{'t':t.tolist(),'speed':s.tolist(),'xy':g[['x','y']].to_numpy(float).tolist()}

def prepare(data,out):
    data,out=Path(data),Path(out);out.mkdir(parents=True,exist_ok=True)
    players=pd.read_csv(data/'players.csv');ids=set(players.loc[players.nfl_position.eq('WR'),'nfl_id'])
    tr=pd.read_csv(data/'combine_tracking.csv');tr=tr[tr.nfl_id.isin(ids)&tr.entity_type.eq('PLAYER')&tr.drill_name.eq('FORTY_YARD_DASH')]
    attempts=[];rejected={};example=None
    for key,g in tr.groupby(['nfl_id','draft_year','event_id'],sort=True):
        try:f,diag=sprint_features(g)
        except ValueError as e:rejected[str(e)]=rejected.get(str(e),0)+1;continue
        attempts.append(dict(nfl_id=key[0],draft_year=key[1],event_id=key[2],**f))
        if example is None:example=diag
    if not attempts:raise ValueError('No forty-yard-dash tracking; inspect official drill identifiers')
    attempts=pd.DataFrame(attempts);motion=[c for c in attempts if c.startswith('motion__')]
    panel=attempts.groupby(['nfl_id','draft_year'])[motion].median().reset_index()
    pp=pd.read_csv(data/'player_play.csv').merge(players[['nfl_id','draft_year','nfl_position']],on='nfl_id',validate='many_to_one')
    games=pd.read_csv(data/'games.csv');pp=pp.merge(games,on='game_id',validate='many_to_one')
    pp=pp[pp.nfl_position.eq('WR')&pp.season.eq(pp.draft_year)&pp.season_type.eq('REG')&pp.play_nullified_by_penalty.eq('N')&pp.route_ran.notna()&pp.route_ran.ne('NONE')&pp.nfl_id.isin(panel.nfl_id)].copy()
    pp['defense_team']=np.where(pp.team_abbr.eq(pp.home_team_abbr),pp.visitor_team_abbr,pp.home_team_abbr)
    keys=pp[['game_id','play_id','nfl_id']];rows=[];reject={};eligible=len(pp)
    for year in (2023,2024,2025):
        selected=keys[keys.game_id.isin(pp.loc[pp.season.eq(year),'game_id'])];parts=[]
        for chunk in pd.read_csv(data/f'game_tracking_{year}.csv',chunksize=200000):
            q=chunk[chunk.nfl_id.isin(panel.nfl_id)].merge(selected,on=['game_id','play_id','nfl_id'],validate='many_to_one')
            if len(q):parts.append(q)
        frames=pd.concat(parts,ignore_index=True)
        for key,g in frames.groupby(['game_id','play_id','nfl_id'],sort=True):
            g=g.sort_values('time');snap=g[g.event.eq('ball_snap')];release=g[g.event.eq('pass_forward')]
            reason=None
            if len(snap)!=1 or len(release)!=1:reason='missing_or_nonunique_event'
            else:
                t=pd.to_datetime(g.time,utc=True,format='ISO8601');start=pd.to_datetime(snap.time.iloc[0],utc=True);end=pd.to_datetime(release.time.iloc[0],utc=True)
                if (end-start).total_seconds()<1.5-1e-5:reason='early_release'
                else:
                    q=g[(t-start).dt.total_seconds().between(-1e-5,1.5+1e-5)].copy();qt=pd.to_datetime(q.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9
                    if len(q)!=16 or not np.allclose(np.diff(qt),.1,atol=.015):reason='noncontinuous_window'
            if reason:reject[reason]=reject.get(reason,0)+1;continue
            s=q.s.to_numpy(float);xy=q[['x','y']].to_numpy(float)
            if not np.isfinite(s).all() or not np.isfinite(xy).all():reject['nonfinite']=reject.get('nonfinite',0)+1;continue
            early=float(s[3:6].mean());late=float(s[13:16].mean())
            rows.append(dict(game_id=key[0],play_id=key[1],nfl_id=key[2],snap_speed=float(s[0]),early_speed=early,early_acceleration=float((early-s[:3].mean())/.3),early_distance=float(np.linalg.norm(np.diff(xy[:6],axis=0),axis=1).sum()),future_speed=late,speed_gain=late-early))
        print('Extracted game windows',year,len(rows),flush=True)
    d=pp.merge(pd.DataFrame(rows),on=['game_id','play_id','nfl_id'],validate='one_to_one').merge(pd.read_csv(data/'combine_results.csv'),on=['nfl_id','draft_year'],validate='many_to_one').merge(panel,on=['nfl_id','draft_year'],validate='many_to_one')
    counts=d.groupby('nfl_id').size();d=d[d.nfl_id.isin(counts[counts>=20].index)].reset_index(drop=True)
    d.to_pickle(out/'private_rows.pkl');attempts.to_pickle(out/'private_attempts.pkl');(out/'private_source_example.json').write_text(json.dumps(example))
    audit={'status':'reconstructed_actual_data','attempts':len(attempts),'source_players':int(panel.nfl_id.nunique()),'source_features':motion,'rejected_source':rejected,'eligible_routes':eligible,'rejected_game':reject,'players_by_year':{str(k):int(v) for k,v in d.groupby('draft_year').nfl_id.nunique().items()},'routes_by_year':{str(k):int(v) for k,v in d.groupby('draft_year').size().items()},'time_scope':'input <=0.5 s; outcome mean speed 1.3–1.5 s; release >=1.5 s; rookie REG routes; minimum 20 windows/player','limitation':'Charted context and vendor speed may not be causally available online; eligibility conditions on future release.'}
    (out/'population.json').write_text(json.dumps(audit,indent=2));return d,audit

class Encoder(BaseEstimator,TransformerMixin):
    def __init__(self,family='conventional',prefix=True,k=4,seed=A.SEED):self.family=family;self.prefix=prefix;self.k=k;self.seed=seed
    def fit(self,x,y):
        p=x.drop_duplicates('nfl_id');self.fit_ids_=set(p.nfl_id);self.numcols=R.NUM+(PREFIX if self.prefix else [])
        def numeric():return Pipeline([('impute',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)),('scale',StandardScaler())])
        self.phys=numeric().fit(p[R.PHYS]);self.num=numeric().fit(x[self.numcols]);self.cat=OneHotEncoder(handle_unknown='ignore',sparse_output=False).fit(x[R.CAT].astype(str).where(x[R.CAT].notna(),'MISSING'))
        if self.family!='conventional':
            self.cols=[c for c in x if c.startswith('motion__')];v=p[self.cols].to_numpy(float);self.lo=np.nanquantile(v,.01,axis=0);self.hi=np.nanquantile(v,.99,axis=0)
            self.motion=numeric().fit(pd.DataFrame(np.clip(v,self.lo,self.hi)));z=self.motion.transform(pd.DataFrame(np.clip(v,self.lo,self.hi)))
            self.innovation=Ridge(alpha=10).fit(self.phys.transform(p[R.PHYS]),z);z-=self.innovation.predict(self.phys.transform(p[R.PHYS]));self.lift=StandardScaler().fit(np.c_[z,z*z]);z=self.lift.transform(np.c_[z,z*z])
            if self.family=='pca_motion':self.reducer=PCA(n_components=min(self.k,len(p)-1,z.shape[1]),svd_solver='full').fit(z)
            else:
                oof=np.zeros(len(x))
                for a,b in player_splits(x,3,self.seed):
                    # Nested train-only encoders prevent nuisance preprocessing leakage.
                    enc=Encoder('conventional',self.prefix,self.k,self.seed).fit(x.iloc[a],np.asarray(y)[a]);reg=Ridge(alpha=10).fit(enc.transform(x.iloc[a]),np.asarray(y)[a],sample_weight=A.weights(x.iloc[a]));oof[b]=reg.predict(enc.transform(x.iloc[b]))
                residual=pd.DataFrame({'id':x.nfl_id.to_numpy(),'r':np.asarray(y)-oof}).groupby('id').r.mean().reindex(p.nfl_id).to_numpy()
                self.reducer=PLSRegression(n_components=min(1 if self.k==4 else 2,len(p)-1,z.shape[1]),scale=False).fit(z,residual)
        return self
    def base(self,x):return np.c_[self.phys.transform(x[R.PHYS]),self.num.transform(x[self.numcols]),self.cat.transform(x[R.CAT].astype(str).where(x[R.CAT].notna(),'MISSING'))]
    def transform(self,x):
        b=self.base(x)
        if self.family=='conventional':return b
        z=self.motion.transform(pd.DataFrame(np.clip(x[self.cols].to_numpy(float),self.lo,self.hi)));z-=self.innovation.predict(self.phys.transform(x[R.PHYS]));z=self.lift.transform(np.c_[z,z*z]);return np.c_[b,self.reducer.transform(z)]

def fit_predict(tr,te,target,family,prefix,config,seed):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('Player leakage')
    if config['reg']=='ridge':reg=Ridge(alpha=config['alpha'])
    elif config['reg']=='forest':reg=RandomForestRegressor(n_estimators=150,max_depth=6,min_samples_leaf=20,max_features=.8,n_jobs=2,random_state=A.SEED)
    else:reg=ExtraTreesRegressor(n_estimators=150,max_depth=8,min_samples_leaf=20,max_features=.8,n_jobs=2,random_state=A.SEED)
    model=Pipeline([('enc',Encoder(family,prefix,config['k'],seed)),('reg',reg)]);model.fit(tr,tr[target],reg__sample_weight=A.weights(tr));return model.predict(te)

def score(d,p,target):return float(np.average((d[target].to_numpy()-p)**2,weights=A.weights(d)))
def interval(d,p0,p1,target):
    v=pd.DataFrame({'id':d.nfl_id,'delta':(d[target].to_numpy()-p0)**2-(d[target].to_numpy()-p1)**2}).groupby('id').delta.mean().to_numpy();rng=np.random.default_rng(A.SEED)
    return {'delta_mse':float(v.mean()),'ci95':np.quantile(rng.choice(v,(5000,len(v)),replace=True).mean(axis=1),[.025,.975]).tolist(),'players':len(v),'scope':'Conditional player bootstrap; not refitting uncertainty or a causal effect.'}

def experiment(d,out,target='future_speed',seed=A.SEED+510):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);test=d[d.draft_year.eq(2025)].reset_index(drop=True)
    specs=[('conventional_without_state','conventional',False),('conventional_with_state','conventional',True),('pca_with_state','pca_motion',True),('target_motion_with_state','target_motion',True),('pca_without_state','pca_motion',False),('target_motion_without_state','target_motion',False)]
    nested={};forward={};records=[];validation=[]
    for name,family,prefix in specs:
        oof=np.zeros(len(dev))
        for fold,(a,b) in enumerate(player_splits(dev,4,seed)):
            tr,te=dev.iloc[a].reset_index(drop=True),dev.iloc[b];loss=[]
            for ci,c in enumerate(CONFIGS):
                scores=[]
                for i,j in player_splits(tr,3,seed+1+fold):scores.append(score(tr.iloc[j],fit_predict(tr.iloc[i],tr.iloc[j],target,family,prefix,c,seed+1+fold),target))
                loss.append(float(np.mean(scores)))
            ci=int(np.argmin(loss));oof[b]=fit_predict(tr,te,target,family,prefix,CONFIGS[ci],seed+1+fold);records.append({'family':name,'fold':fold,'inner_mse':loss,'config':ci,'train_player_hash':hashlib.sha256(json.dumps(sorted(map(int,tr.nfl_id.unique()))).encode()).hexdigest(),'test_player_hash':hashlib.sha256(json.dumps(sorted(map(int,te.nfl_id.unique()))).encode()).hexdigest()})
            print(target,name,'outer',fold,'MSE',score(te,oof[b],target),flush=True)
        nested[name]=oof
        tr=dev[dev.draft_year.eq(2023)];va=dev[dev.draft_year.eq(2024)];loss=[score(va,fit_predict(tr,va,target,family,prefix,c,seed),target) for c in CONFIGS];ci=int(np.argmin(loss));forward[name]=fit_predict(dev,test,target,family,prefix,CONFIGS[ci],seed);validation.append({'family':name,'config':ci,'validation_mse':loss})
        # Persist complete per-family predictions before moving to another family.
        pd.DataFrame({'nfl_id':dev.nfl_id,'game_id':dev.game_id,'play_id':dev.play_id,'truth':dev[target],'prediction':oof}).to_pickle(out/f'private_nested_{name}.pkl')
        pd.DataFrame({'nfl_id':test.nfl_id,'game_id':test.game_id,'play_id':test.play_id,'truth':test[target],'prediction':forward[name]}).to_pickle(out/f'private_forward_{name}.pkl')
    comparisons={}
    for label,rows,preds in [('nested',dev,nested),('exploratory_2025',test,forward)]:
        pairs=[('state_channel','conventional_without_state','conventional_with_state'),('target_motion_increment','conventional_with_state','target_motion_with_state'),('pca_increment','conventional_with_state','pca_with_state'),('target_motion_scouting','conventional_without_state','target_motion_without_state')]
        comparisons[label]={'mse':{k:score(rows,p,target) for k,p in preds.items()},'comparisons':{k:interval(rows,preds[a],preds[b],target) for k,a,b in pairs},'players':int(rows.nfl_id.nunique()),'rows':len(rows)}
    result={'status':'completed_reconstructed_actual_data','target':target,'outer_seed':seed,'nested':comparisons['nested'],'exploratory_2025':comparisons['exploratory_2025'],'folds':records,'forward_selection':validation,'selection':'Unique-player class-stratified 4 outer / 3 inner folds; matched 5 candidate models. 2023 training/2024 tuning then 2025 exploratory transport. All transformations train-only.','prior_2025_inspection':True,'not_identical_to_lost_implementation':True}
    (out/'results.json').write_text(json.dumps(result,indent=2));return result

def run(data,out):
    out=Path(out);d,audit=prepare(data,out)
    return experiment(d,out/'absolute_speed')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--data',default='data');p.add_argument('--out',default='private_observability');a=p.parse_args();run(a.data,a.out)
