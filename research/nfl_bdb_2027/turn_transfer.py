"""Demand-adjusted Combine-to-NFL WR turn translation.

Source nuisance maps and physical innovations use training players only. NFL turn
demands are descriptive outcome-side conditioning, not real-time covariates.
"""
from pathlib import Path
import json,hashlib,time
import numpy as np,pandas as pd
from scipy.signal import savgol_filter,find_peaks
from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor,ExtraTreesRegressor
import analysis as A,repo_predict as R
from mechanism import player_splits
from observability import score,interval

MAP={'IN':['DAGGER_ROUTE_LEFT'],'OUT':['SPEED_OUT_ROUTE_LEFT'],'SLANT':['SLANT_ROUTE_LEFT'],'HITCH':['CURL_ROUTE_RIGHT','COMEBACK_ROUTE_RIGHT']}
STYLE=['burden','retention','exit_ratio','area']
DEMAND=['entry','angle','impulse','source_count']
GAME=['game_entry','game_angle','game_impulse','cut_time']
SEED=A.SEED+1200

def first_turn(g,game=False):
    g=g.sort_values('time').reset_index(drop=True);t=pd.to_datetime(g.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9;t-=t[0]
    if len(g)<12 or not np.allclose(np.diff(t),.1,atol=.015):raise ValueError('short_or_irregular')
    p=g[['x','y']].to_numpy(float);s=g.s.to_numpy(float)
    if not np.isfinite(p).all() or not np.isfinite(s).all():raise ValueError('nonfinite')
    smooth=savgol_filter(p,7,3,axis=0);v=np.gradient(smooth,.1,axis=0);ps=np.linalg.norm(v,axis=1);th=np.unwrap(np.arctan2(v[:,1],v[:,0]))
    kk=np.arange(5,len(g)-3);turn=np.abs(th[kk+3]-th[kk-3]);peaks=find_peaks(np.r_[0.,turn,0.],height=np.deg2rad(25),distance=10)[0]-1;peaks=peaks[(peaks>=0)&(peaks<len(kk))]
    eligible=[]
    for j in peaks:
        c=int(kk[j]);entry=float(s[c-5:c-2].mean());angle=float(turn[j])
        if entry<2.5 or angle>np.deg2rad(150) or min(ps[c-3],ps[c+3])<1:continue
        if game and not .5-1e-5<=t[c]<=3.+1e-5:continue
        eligible.append((c,entry,angle))
    if not eligible:raise ValueError('no_qualifying_first_turn')
    c,entry,angle=eligible[0];stop=min(len(g)-1,c+15);local=s[c-3:c+4];imin=c-3+int(np.argmin(local));event=False;recovery=float(t[stop]-t[c])
    if local.min()>=.9*entry:event=True;recovery=0.
    else:
        for i in range(max(c,imin),stop):
            if s[i]>=.9*entry and s[i+1]>=.9*entry:event=True;recovery=float(t[i]-t[c]);break
    record={'entry':entry,'angle':angle,'impulse':float(2*entry*np.sin(angle/2)),'cut_time':float(t[c]),'recovery_time':recovery,'recovery_event':event,'complete_half_second':c+5<len(g)}
    if c+5<len(g):
        deficit=np.maximum(0,1-s[c:c+6]/entry);q=p[c-3:c+6]-p[c-3];u=v[c-3]/max(ps[c-3],1e-9);q=q@np.array([[u[0],-u[1]],[u[1],u[0]]]);q[:,1]*=1 if th[c+3]>=th[c-3] else -1;arc=np.linalg.norm(np.diff(q,axis=0),axis=1).sum()
        record.update(burden=float(np.trapezoid(deficit,dx=.1)),retention=float(local.min()/entry),exit_ratio=float(s[c+3:c+6].mean()/entry),area=float(.5*np.sum(q[:-1,0]*q[1:,1]-q[:-1,1]*q[1:,0])/max(arc**2,1e-9)))
    else:record.update({k:np.nan for k in STYLE})
    diagnostic={'q':(p[max(0,c-5):stop+1]-p[c]).tolist(),'speed':s[max(0,c-5):stop+1].tolist(),'t':(t[max(0,c-5):stop+1]-t[c]).tolist(),'entry':entry,'cut':c,'angle':angle}
    return record,diagnostic

def recovery_bounds(d,horizon=.5):
    recovered=d.recovery_event&d.recovery_time.le(horizon);unresolved=~d.recovery_event&d.recovery_time.lt(horizon)
    return {'rows':len(d),'observed_recovered_fraction':float(recovered.mean()),'recovered_fraction_lower':float(recovered.mean()),'recovered_fraction_upper':float((recovered|unresolved).mean()),'unresolved_before_horizon':int(unresolved.sum()),'right_censored_total':int((~d.recovery_event).sum()),'horizon_seconds':horizon,'scope':'Distribution-free bounds over observed records; no independent-censoring assumption. Not player balanced.'}

def prepare(data,out):
    data,out=Path(data),Path(out);out.mkdir(parents=True,exist_ok=True);p=pd.read_csv(data/'players.csv');phys=pd.read_csv(data/'combine_results.csv');ids=set(p.loc[p.nfl_position.eq('WR'),'nfl_id'])
    tr=pd.read_csv(data/'combine_tracking.csv');tr=tr[tr.nfl_id.isin(ids)&tr.entity_type.eq('PLAYER')&tr.drill_type.eq('SKILL_DRILLS_WR')].copy();tr['drill_name']=tr.drill_name.replace({'SPEED_OUT_LEFT':'SPEED_OUT_ROUTE_LEFT'});drill_route={v:k for k,values in MAP.items() for v in values};source=[];source_reject={};source_example=None
    for key,g in tr.groupby(['nfl_id','draft_year','event_id'],sort=True):
        drill=g.drill_name.iloc[0]
        if drill not in drill_route:continue
        try:f,diag=first_turn(g)
        except ValueError as e:source_reject[str(e)]=source_reject.get(str(e),0)+1;continue
        if not f['complete_half_second']:source_reject['short_response_window']=source_reject.get('short_response_window',0)+1;continue
        source.append(dict(nfl_id=key[0],draft_year=key[1],event_id=key[2],drill_name=drill,route_ran=drill_route[drill],**f))
        if source_example is None:source_example=diag
    source=pd.DataFrame(source).merge(phys[['nfl_id','draft_year']+R.PHYS],on=['nfl_id','draft_year'],validate='many_to_one');source.to_pickle(out/'private_source.pkl')
    pp=pd.read_csv(data/'player_play.csv').merge(p[['nfl_id','draft_year','nfl_position']],on='nfl_id',validate='many_to_one');games=pd.read_csv(data/'games.csv');pp=pp.merge(games,on='game_id',validate='many_to_one')
    pp=pp[pp.nfl_position.eq('WR')&pp.season.eq(pp.draft_year)&pp.season_type.eq('REG')&pp.route_ran.isin(MAP)&pp.play_nullified_by_penalty.eq('N')].copy();pp['defense_team']=np.where(pp.team_abbr.eq(pp.home_team_abbr),pp.visitor_team_abbr,pp.home_team_abbr)
    keys=pp[['game_id','play_id','nfl_id']];rows=[];reject={};game_example=None
    for year in [2023,2024,2025]:
        selected=keys[keys.game_id.isin(pp.loc[pp.season.eq(year),'game_id'])];parts=[]
        for chunk in pd.read_csv(data/f'game_tracking_{year}.csv',chunksize=200000):
            q=chunk[chunk.nfl_id.isin(ids)].merge(selected,on=['game_id','play_id','nfl_id'],validate='many_to_one')
            if len(q):parts.append(q)
        frames=pd.concat(parts,ignore_index=True)
        for key,g in frames.groupby(['game_id','play_id','nfl_id'],sort=True):
            g=g.sort_values('time');snap=g[g.event.eq('ball_snap')];release=g[g.event.eq('pass_forward')]
            if len(snap)!=1 or len(release)!=1:reject['missing_or_nonunique_events']=reject.get('missing_or_nonunique_events',0)+1;continue
            q=g[g.time.ge(snap.time.iloc[0])&g.time.le(release.time.iloc[0])]
            try:f,diag=first_turn(q,game=True)
            except ValueError as e:reject[str(e)]=reject.get(str(e),0)+1;continue
            rows.append(dict(game_id=key[0],play_id=key[1],nfl_id=key[2],**f))
            if game_example is None and f['complete_half_second']:game_example=diag
        print('Turn extraction',year,len(rows),flush=True)
    allrows=pp.merge(pd.DataFrame(rows),on=['game_id','play_id','nfl_id'],validate='one_to_one').merge(phys,on=['nfl_id','draft_year'],validate='many_to_one');allrows.to_pickle(out/'private_all_turns.pkl')
    d=allrows[allrows.complete_half_second].copy();counts=d.groupby('nfl_id').size();d=d[d.nfl_id.isin(counts[counts>=10].index)].rename(columns={'entry':'game_entry','angle':'game_angle','impulse':'game_impulse'}).reset_index(drop=True);d.to_pickle(out/'private_rows.pkl')
    audit={'source_attempts':len(source),'source_players':int(source.nfl_id.nunique()),'source_rejections':source_reject,'eligible_route_records':len(pp),'game_rejections':reject,'all_qualifying_game_turns':len(allrows),'incomplete_half_second_turns':int((~allrows.complete_half_second).sum()),'primary_players_by_year':{str(k):int(v) for k,v in d.groupby('draft_year').nfl_id.nunique().items()},'primary_turns_by_year':{str(k):int(v) for k,v in d.groupby('draft_year').size().items()},'source_missing_player_route_fraction':float(pd.MultiIndex.from_frame(d[['nfl_id','route_ran']]).isin(pd.MultiIndex.from_frame(source[['nfl_id','route_ran']])).mean()),'recovery_bounds_all_turns':recovery_bounds(allrows),'measured_separation_fraction':float(np.isfinite(d.separation_at_pass_forward).mean()),'primary_target':'burden: observed half-second normalized speed deficit in seconds','prior_2025_inspection':True}
    audit['source_available_player_route_fraction']=audit.pop('source_missing_player_route_fraction');(out/'population.json').write_text(json.dumps(audit,indent=2));(out/'private_examples.json').write_text(json.dumps({'source':source_example,'game':game_example}));return d,source,audit

def numeric():return Pipeline([('impute',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)),('scale',StandardScaler())])
def source_demand(x):
    a=x.entry.to_numpy();b=x.angle.to_numpy();return np.c_[a,b,a*b,a*a,b*b]

class TurnEncoder(BaseEstimator,TransformerMixin):
    def __init__(self,source,family='conventional'):self.source=source;self.family=family
    def fit(self,x,y=None):
        players=x.drop_duplicates('nfl_id');self.fit_ids_=set(players.nfl_id);self.phys=numeric().fit(players[R.PHYS]);self.num=numeric().fit(x[R.NUM+GAME]);self.cat=OneHotEncoder(handle_unknown='ignore',sparse_output=False).fit(x[R.CAT].astype(str).where(x[R.CAT].notna(),'MISSING'))
        if self.family!='conventional':
            train_source=self.source[self.source.nfl_id.isin(self.fit_ids_)];self.source_fit_ids_=set(train_source.nfl_id)
            self.demand_scale=StandardScaler().fit(source_demand(train_source));self.source_model=Ridge(alpha=10).fit(self.demand_scale.transform(source_demand(train_source)),train_source[STYLE],sample_weight=A.weights(train_source))
            allsource=self.source.copy();prediction=self.source_model.predict(self.demand_scale.transform(source_demand(allsource)))
            for j,k in enumerate(STYLE):allsource['innovation_'+k]=allsource[k]-prediction[:,j]
            table=allsource.groupby(['nfl_id','route_ran'])[['entry','angle','impulse']+['innovation_'+k for k in STYLE]].median();table['source_count']=allsource.groupby(['nfl_id','route_ran']).size();self.table=table
            units=x.drop_duplicates(['nfl_id','route_ran']);dm=self.lookup(units,DEMAND);self.source_demands=numeric().fit(dm)
            if self.family=='execution':
                z=self.lookup(units,['innovation_'+k for k in STYLE]);self.style=numeric().fit(z);z=self.style.transform(z);self.physical_innovation=Ridge(alpha=10).fit(self.phys.transform(units[R.PHYS]),z,sample_weight=A.weights(units));z-=self.physical_innovation.predict(self.phys.transform(units[R.PHYS]));self.style_scale=StandardScaler().fit(z)
        return self
    def lookup(self,x,cols):return self.table.reindex(pd.MultiIndex.from_frame(x[['nfl_id','route_ran']]))[cols].to_numpy(float)
    def transform(self,x):
        physical=self.phys.transform(x[R.PHYS]);event=self.num.transform(x[R.NUM+GAME]);base=np.c_[physical,event,self.cat.transform(x[R.CAT].astype(str).where(x[R.CAT].notna(),'MISSING'))]
        if self.family=='conventional':return base
        base=np.c_[base,self.source_demands.transform(self.lookup(x,DEMAND))]
        if self.family=='source_demands':return base
        z=self.style.transform(self.lookup(x,['innovation_'+k for k in STYLE]));z-=self.physical_innovation.predict(physical);z=self.style_scale.transform(z);entry=event[:,len(R.NUM)];angle=event[:,len(R.NUM)+1];mass=physical[:,R.PHYS.index('combine_weight')]
        return np.c_[base,z,z*z,z*entry[:,None],z*angle[:,None],z*mass[:,None]]

def fit_predict(tr,te,source,family,config,target):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('player leakage')
    if config['reg']=='ridge':reg=Ridge(alpha=config['alpha'])
    elif config['reg']=='forest':reg=RandomForestRegressor(n_estimators=150,max_depth=6,min_samples_leaf=20,max_features=.8,n_jobs=2,random_state=A.SEED)
    else:reg=ExtraTreesRegressor(n_estimators=150,max_depth=8,min_samples_leaf=20,max_features=.8,n_jobs=2,random_state=A.SEED)
    model=Pipeline([('enc',TurnEncoder(source,family)),('reg',reg)]);model.fit(tr,tr[target],reg__sample_weight=A.weights(tr));return model.predict(te)

def experiment(d,source,out,target='burden',seed=SEED,forward=True):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if target=='separation_at_pass_forward':d=d[np.isfinite(d[target])&d[target].ge(0)].copy()
    counts=d.groupby('draft_year').nfl_id.nunique()
    if min(counts.reindex([2023,2024,2025],fill_value=0))<10:raise ValueError('Frozen minimum player count failed; do not relax after test.')
    dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);test=d[d.draft_year.eq(2025)].reset_index(drop=True);families=['conventional','source_demands','execution'];pred={k:np.zeros(len(dev)) for k in families};tp={};records=[];bank=[]
    for fold,(a,b) in enumerate(player_splits(dev,4,seed)):
        tr=dev.iloc[a].reset_index(drop=True);te=dev.iloc[b]
        for family in families:
            loss=[]
            for config in R.CONFIGS:
                values=[]
                for i,j in player_splits(tr,3,seed+1+fold):values.append(score(tr.iloc[j],fit_predict(tr.iloc[i],tr.iloc[j],source,family,config,target),target))
                loss.append(float(np.mean(values)))
            ci=int(np.argmin(loss));pred[family][b]=fit_predict(tr,te,source,family,R.CONFIGS[ci],target);records.append({'fold':fold,'family':family,'inner_mse':loss,'config':ci,'train_player_hash':hashlib.sha256(json.dumps(sorted(map(int,tr.nfl_id.unique()))).encode()).hexdigest(),'test_player_hash':hashlib.sha256(json.dumps(sorted(map(int,te.nfl_id.unique()))).encode()).hexdigest()});print(target,seed,fold,family,score(te,pred[family][b],target),flush=True)
    nested={'mse':{k:score(dev,p,target) for k,p in pred.items()},'execution_increment':interval(dev,pred['source_demands'],pred['execution'],target),'tracking_increment':interval(dev,pred['conventional'],pred['execution'],target),'players':int(dev.nfl_id.nunique()),'turns':len(dev)}
    for family in families:pd.DataFrame({'nfl_id':dev.nfl_id,'truth':dev[target],'prediction':pred[family]}).to_pickle(out/f'private_nested_{family}.pkl')
    result={'status':'completed_actual_data_exploratory','target':target,'seed':seed,'nested':nested,'folds':records,'prior_2025_inspection':True,'primary_contrast':'execution versus source_demands; conventional is secondary','scope':'Conditional mechanical transfer using measured NFL turn demands; not live deployment or causal training benefit.'}
    if forward:
        tr=dev[dev.draft_year.eq(2023)];va=dev[dev.draft_year.eq(2024)]
        for family in families:
            loss=[score(va,fit_predict(tr,va,source,family,c,target),target) for c in R.CONFIGS];ci=int(np.argmin(loss));tp[family]=fit_predict(dev,test,source,family,R.CONFIGS[ci],target);bank.append({'family':family,'validation_mse':loss,'config':ci});pd.DataFrame({'nfl_id':test.nfl_id,'game_id':test.game_id,'play_id':test.play_id,'truth':test[target],'prediction':tp[family]}).to_pickle(out/f'private_forward_{family}.pkl')
        result['exploratory_2025']={'mse':{k:score(test,p,target) for k,p in tp.items()},'execution_increment':interval(test,tp['source_demands'],tp['execution'],target),'tracking_increment':interval(test,tp['conventional'],tp['execution'],target),'players':int(test.nfl_id.nunique()),'turns':len(test)};result['forward_selection']=bank
    (out/'results.json').write_text(json.dumps(result,indent=2));return result

def run(data,out):
    out=Path(out);d,source,audit=prepare(data,out)
    try:
        primary=experiment(d,source,out/'burden');secondary=experiment(d,source,out/'separation',target='separation_at_pass_forward')
    except ValueError as e:
        (out/'feasibility_failure.json').write_text(json.dumps({'status':'frozen_protocol_feasibility_failure','reason':str(e),'population':audit},indent=2));raise
    return primary,secondary
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--data',default='data');p.add_argument('--out',default='private_turn_transfer');a=p.parse_args();run(a.data,a.out)
