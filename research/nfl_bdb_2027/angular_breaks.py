"""Sustained route-break alignment on an angular-progress clock, WR only."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.signal import savgol_filter
import turn_transfer as T,repo_predict as R

ROUTES={'IN':(45,130),'OUT':(45,130),'SLANT':(25,90)}

def measure(g,route,game=False):
    g=g.sort_values('time');time=pd.to_datetime(g.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9;time-=time[0]
    if len(g)<19 or not np.allclose(np.diff(time),.1,atol=.015):raise ValueError('short_irregular')
    p=savgol_filter(g[['x','y']].to_numpy(float),7,3,axis=0);v=np.gradient(p,.1,axis=0);speed=g.s.to_numpy(float);th=np.unwrap(np.arctan2(v[:,1],v[:,0]));ps=np.linalg.norm(v,axis=1);candidates=[]
    if not np.isfinite(p).all() or not np.isfinite(speed).all():raise ValueError('nonfinite')
    for c in range(8,len(g)-8):
        before=float(np.mean(th[c-7:c-3]));after=float(np.mean(th[c+3:c+7]));signed=after-before;angle=abs(signed);entry=float(speed[c-7:c-3].mean())
        if not ROUTES[route][0]<=np.rad2deg(angle)<=ROUTES[route][1] or entry<2.5 or min(ps[c-5],ps[c+5])<1.5:continue
        if np.std(th[c-7:c-3])>np.deg2rad(15) or np.std(th[c+3:c+7])>np.deg2rad(15):continue
        if game and not .8<=time[c]<=6:continue
        progress=np.maximum.accumulate((th[c-7:c+8]-before)/signed)
        i20=np.flatnonzero(progress>=.2);i80=np.flatnonzero(progress>=.8)
        if not len(i20) or not len(i80):continue
        lo=c-7+int(i20[0]);hi=c-7+int(i80[0])
        if hi<=lo or hi+4>=len(g):continue
        candidates.append((angle*entry,c,lo,hi,entry,angle))
    if not candidates:raise ValueError('no_sustained_break')
    _,c,lo,hi,entry,angle=max(candidates,key=lambda x:(x[0],-x[1]));arc=np.linalg.norm(np.diff(p[lo:hi+1],axis=0),axis=1).sum();q=p[lo:hi+1]-p[lo];area=.5*np.sum(q[:-1,0]*q[1:,1]-q[:-1,1]*q[1:,0])
    f={'entry':entry,'angle':angle,'impulse':float(2*entry*np.sin(angle/2)),'cut_time':float(time[c]),'burden':float(np.trapezoid(np.maximum(0,1-speed[lo:hi+1]/entry),dx=.1)),'retention':float(speed[lo:hi+1].min()/entry),'exit_ratio':float(speed[hi+2:hi+5].mean()/entry),'area':float(abs(area)/max(arc*arc,1e-9)),'rotation_duration':float(time[hi]-time[lo])}
    diag={'time':(time[lo-2:hi+5]-time[c]).tolist(),'xy':(p[lo-2:hi+5]-p[c]).tolist(),'speed':speed[lo-2:hi+5].tolist(),'progress_start':float(time[lo]-time[c]),'progress_end':float(time[hi]-time[c]),'angle_deg':float(np.rad2deg(angle))};return f,diag

def prepare(data,out):
    data,out=Path(data),Path(out);out.mkdir(exist_ok=True);p=pd.read_csv(data/'players.csv');phys=pd.read_csv(data/'combine_results.csv');ids=set(p.loc[p.nfl_position.eq('WR'),'nfl_id']);tr=pd.read_csv(data/'combine_tracking.csv');tr=tr[tr.nfl_id.isin(ids)&tr.entity_type.eq('PLAYER')];tr['drill_name']=tr.drill_name.replace({'SPEED_OUT_LEFT':'SPEED_OUT_ROUTE_LEFT'});mapping={v:k for k,values in T.MAP.items() if k in ROUTES for v in values};source=[];reject={};examples={}
    for key,g in tr.groupby(['nfl_id','draft_year','event_id'],sort=True):
        drill=g.drill_name.iloc[0]
        if drill not in mapping:continue
        try:f,diag=measure(g,mapping[drill])
        except ValueError as e:reject['source_'+str(e)]=reject.get('source_'+str(e),0)+1;continue
        source.append(dict(nfl_id=key[0],draft_year=key[1],event_id=key[2],route_ran=mapping[drill],drill_name=drill,**f))
        if 'source' not in examples:examples['source']=diag
    source=pd.DataFrame(source).merge(phys[['nfl_id','draft_year']+R.PHYS],on=['nfl_id','draft_year'],validate='many_to_one');source.to_pickle(out/'private_source.pkl')
    d=pd.read_csv(data/'player_play.csv').merge(p[['nfl_id','draft_year','nfl_position']],on='nfl_id',validate='many_to_one').merge(pd.read_csv(data/'games.csv'),on='game_id',validate='many_to_one');d=d[d.nfl_position.eq('WR')&d.season.eq(d.draft_year)&d.season_type.eq('REG')&d.play_nullified_by_penalty.eq('N')&d.route_ran.isin(ROUTES)&d.nfl_id.isin(source.nfl_id)].copy();d['defense_team']=np.where(d.team_abbr.eq(d.home_team_abbr),d.visitor_team_abbr,d.home_team_abbr);rows=[]
    for year in [2023,2024,2025]:
        meta=d[d.draft_year.eq(year)].set_index(['game_id','play_id','nfl_id']);keys=meta.reset_index()[['game_id','play_id','nfl_id']];parts=[]
        for chunk in pd.read_csv(data/f'game_tracking_{year}.csv',chunksize=250000):
            q=chunk[chunk.nfl_id.isin(ids)].merge(keys,on=['game_id','play_id','nfl_id'],validate='many_to_one')
            if len(q):parts.append(q)
        for key,g in pd.concat(parts).groupby(['game_id','play_id','nfl_id'],sort=True):
            g=g.sort_values('time');snap=g[g.event.eq('ball_snap')];arrival=g[g.event.isin(['pass_arrived','pass_outcome_caught','pass_outcome_incomplete','pass_outcome_interception'])];release=g[g.event.eq('pass_forward')]
            if len(snap)!=1 or len(release)!=1:reject['game_missing_snap_release']=reject.get('game_missing_snap_release',0)+1;continue
            end=arrival.time.min() if len(arrival) else release.time.iloc[0]
            q=g[g.time.ge(snap.time.iloc[0])&g.time.le(end)]
            try:f,diag=measure(q,meta.loc[key].route_ran,True)
            except ValueError as e:reject['game_'+str(e)]=reject.get('game_'+str(e),0)+1;continue
            rows.append(dict(game_id=key[0],play_id=key[1],nfl_id=key[2],**f))
            if 'game' not in examples and year==2023:examples['game']=diag
        print('Angular breaks',year,len(rows),flush=True)
    d=d.merge(pd.DataFrame(rows),on=['game_id','play_id','nfl_id'],validate='one_to_one').merge(phys,on=['nfl_id','draft_year'],validate='many_to_one');counts=d.groupby('nfl_id').size();d=d[d.nfl_id.isin(counts[counts>=10].index)].rename(columns={'entry':'game_entry','angle':'game_angle','impulse':'game_impulse'}).reset_index(drop=True);d.to_pickle(out/'private_rows.pkl');(out/'private_examples.json').write_text(json.dumps(examples));audit={'source_attempts':len(source),'source_players':int(source.nfl_id.nunique()),'players_by_year':{str(k):int(v) for k,v in d.groupby('draft_year').nfl_id.nunique().items()},'turns_by_year':{str(k):int(v) for k,v in d.groupby('draft_year').size().items()},'rejections':reject,'target':'Exit speed ratio after 80% rotation, conditional on observed NFL entry speed/angle/context. Not a pre-snap prediction.','selection':'Largest angle-times-entry sustained qualifying break before pass arrival; fixed route-specific angle gates, angular-progress response; not hand-labeled playbook truth.'};(out/'population.json').write_text(json.dumps(audit,indent=2));return d,source,audit

if __name__=='__main__':
    d,s,a=prepare('data','private_angular_breaks')
    if min(d.groupby('draft_year').nfl_id.nunique().reindex([2023,2024,2025],fill_value=0))>=10:T.experiment(d,s,'private_angular_breaks/exit',target='exit_ratio',seed=T.SEED+2200)
    else:print('Angular population below the unchanged minimum: no predictive fit',flush=True)
