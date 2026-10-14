"""WR pre-draft speed-ceiling transfer, prospect-level scouting task."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
import analysis as A,repo_predict as R,turn_transfer as T,observability as O
from mechanism import player_splits

SEED=A.SEED+4700
MOTION=['sensor_ceiling','sensor_late_speed','sensor_speed_shape']
CONFIGS=[('ridge',1),('ridge',10),('ridge',100),('forest',0)]

def prepare(data,out):
    data,out=Path(data),Path(out);out.mkdir(exist_ok=True);players=pd.read_csv(data/'players.csv');ids=set(players.loc[players.nfl_position.eq('WR'),'nfl_id']);tr=pd.read_csv(data/'combine_tracking.csv');tr=tr[tr.entity_type.eq('PLAYER')&tr.drill_name.eq('FORTY_YARD_DASH')&tr.nfl_id.isin(ids)];attempts=[]
    for key,g in tr.groupby(['nfl_id','draft_year','event_id'],sort=True):
        g=g.sort_values('time');time=pd.to_datetime(g.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9;time-=time[0];s=g.s.to_numpy(float)
        if len(g)<41 or not np.allclose(np.diff(time),.1,atol=.015) or not np.isfinite(s).all():continue
        ceiling=float(np.quantile(s[time<=4.5],.95));late=float(s[(time>=3)&(time<=4)].mean());early=float(s[(time>=.5)&(time<=1.5)].mean());attempts.append(dict(nfl_id=key[0],draft_year=key[1],event_id=key[2],sensor_ceiling=ceiling,sensor_late_speed=late,sensor_speed_shape=early/max(ceiling,1e-9)))
    attempts=pd.DataFrame(attempts);panel=attempts.groupby(['nfl_id','draft_year'])[MOTION].median().reset_index();pp=pd.read_csv(data/'player_play.csv').merge(players[['nfl_id','draft_year','nfl_position']],on='nfl_id',validate='many_to_one').merge(pd.read_csv(data/'games.csv'),on='game_id',validate='many_to_one');pp=pp[pp.nfl_position.eq('WR')&pp.season.eq(pp.draft_year)&pp.season_type.eq('REG')&pp.play_nullified_by_penalty.eq('N')&pp.route_ran.notna()&pp.route_ran.ne('NONE')&pp.nfl_id.isin(panel.nfl_id)];summaries=[];reject={}
    for year in [2023,2024,2025]:
        keys=pp.loc[pp.draft_year.eq(year),['game_id','play_id','nfl_id']];parts=[]
        for chunk in pd.read_csv(data/f'game_tracking_{year}.csv',chunksize=250000):
            q=chunk[chunk.nfl_id.isin(panel.nfl_id)].merge(keys,on=['game_id','play_id','nfl_id'],validate='many_to_one')
            if len(q):parts.append(q)
        for key,g in pd.concat(parts).groupby(['game_id','play_id','nfl_id'],sort=True):
            g=g.sort_values('time');snap=g[g.event.eq('ball_snap')];release=g[g.event.eq('pass_forward')]
            if len(snap)!=1 or len(release)!=1:reject['events']=reject.get('events',0)+1;continue
            time=pd.to_datetime(g.time,utc=True,format='ISO8601');elapsed=(time-pd.to_datetime(snap.time.iloc[0],utc=True)).dt.total_seconds();s=g.loc[elapsed.ge(1)&g.time.le(release.time.iloc[0]),'s'].to_numpy(float)
            if len(s)<5 or not np.isfinite(s).all():reject['short_nonfinite']=reject.get('short_nonfinite',0)+1;continue
            summaries.append({'nfl_id':key[2],'draft_year':year,'route_speed':float(np.quantile(s,.95))})
        print('Receiver route-speed windows',year,len(summaries),flush=True)
    routes=pd.DataFrame(summaries);n=routes.groupby(['nfl_id','draft_year']).size();valid=n[n>=30].index;target=routes.groupby(['nfl_id','draft_year']).route_speed.quantile(.9).loc[valid].rename('nfl_speed_capacity').reset_index();target['route_count']=[int(n.loc[(r.nfl_id,r.draft_year)]) for r in target.itertuples()];d=target.merge(panel,on=['nfl_id','draft_year'],validate='one_to_one').merge(pd.read_csv(data/'combine_results.csv'),on=['nfl_id','draft_year'],validate='one_to_one');d.to_pickle(out/'private_players.pkl');routes.to_pickle(out/'private_routes.pkl');attempts.to_pickle(out/'private_attempts.pkl');audit={'source_attempts':len(attempts),'source_players':int(panel.nfl_id.nunique()),'players_by_year':{str(k):int(v) for k,v in d.groupby('draft_year').nfl_id.nunique().items()},'routes_by_year':{str(k):int(v) for k,v in routes.groupby('draft_year').size().items()},'rejections':reject,'target':'Player 90th percentile of route 95th-percentile speeds, on rookie REG non-nullified charted routes from one second after snap through pass release; >=30 routes/player','scouting_inputs':'Only provided pre-draft conventional/NGS and Combine tracking; no NFL state, team, route mix, draft pick or route count predictor','limitation':'Capacity proxy depends on observed route opportunities and participating rookies; not separation, production, injury, draft-bust risk or a pure maximal physiological speed.'};(out/'population.json').write_text(json.dumps(audit,indent=2));return d,audit

def predict(tr,te,family,config):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('player leakage')
    def physical(d):
        q=d[R.PHYS].copy();den=d.forty-d.ten_yd_split;den=den.where(den.gt(.5)&den.lt(8));q['conventional_late_speed']=30/den;q['conventional_initial_acceleration']=20/d.ten_yd_split.where(d.ten_yd_split.gt(.5))**2;return q
    scale=T.numeric().fit(physical(tr));x,y=scale.transform(physical(tr)),scale.transform(physical(te))
    if family!='conventional':
        cols=['sensor_ceiling'] if family=='ceiling' else MOTION;motion=T.numeric().fit(tr[cols]);z=motion.transform(tr[cols]);nuisance=Ridge(alpha=10).fit(x,z);a=z-nuisance.predict(x).reshape(len(tr),z.shape[1]);b=motion.transform(te[cols])-nuisance.predict(y).reshape(len(te),z.shape[1]);x=np.c_[x,a];y=np.c_[y,b]
    reg=Ridge(alpha=config[1]) if config[0]=='ridge' else RandomForestRegressor(n_estimators=250,max_depth=3,min_samples_leaf=4,max_features=1.0,n_jobs=2,random_state=SEED)
    reg.fit(x,tr.nfl_speed_capacity);return reg.predict(y)

def experiment(d,out,seed=SEED,forward=True):
    out=Path(out);out.mkdir(exist_ok=True);dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);test=d[d.draft_year.eq(2025)].reset_index(drop=True);pred={k:np.zeros(len(dev)) for k in ['conventional','ceiling','shape']};tp={};folds=[];selection=[]
    for fold,(i,j) in enumerate(player_splits(dev,4,seed)):
        tr=dev.iloc[i].reset_index(drop=True);te=dev.iloc[j]
        for family in pred:
            loss=[np.mean([O.score(tr.iloc[b],predict(tr.iloc[a],tr.iloc[b],family,c),'nfl_speed_capacity') for a,b in player_splits(tr,3,seed+1+fold)]) for c in CONFIGS];ci=int(np.argmin(loss));pred[family][j]=predict(tr,te,family,CONFIGS[ci]);folds.append({'fold':fold,'family':family,'config':ci,'inner_loss':list(map(float,loss))});print('Speed capacity',fold,family,ci,flush=True)
    if forward:
        tr=dev[dev.draft_year.eq(2023)];va=dev[dev.draft_year.eq(2024)]
        for family in pred:
            loss=[O.score(va,predict(tr,va,family,c),'nfl_speed_capacity') for c in CONFIGS];ci=int(np.argmin(loss));tp[family]=predict(dev,test,family,CONFIGS[ci]);selection.append({'family':family,'config':ci,'validation_loss':loss})
    r={'target':'nfl_speed_capacity','seed':seed,'folds':folds,'selection':selection,'prior_2025_other_WR_targets_inspected':True,'inputs_pre_draft_only':True}
    for split,rows,pp in [('nested',dev,pred)]+([('exploratory_2025',test,tp)] if forward else []):
        r[split]={'mse':{k:O.score(rows,p,'nfl_speed_capacity') for k,p in pp.items()},'comparisons':{k:O.interval(rows,pp['conventional'],p,'nfl_speed_capacity') for k,p in pp.items() if k!='conventional'},'players':len(rows)};q=rows[['nfl_id','nfl_speed_capacity']].copy()
        for k,v in pp.items():q[k]=v
        q.to_pickle(out/f'private_{split}.pkl')
    (out/'results.json').write_text(json.dumps(r,indent=2));return r

if __name__=='__main__':d,a=prepare('data','private_speed_ceiling');experiment(d,'private_speed_ceiling')
