"""Operational onset/travel decomposition from actual contiguous 10 Hz traces.

The speed gate is not a snap cue or neurological reaction annotation. Travel
is smoothed geometric arc length, not time to contact or the line of scrimmage.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
import front_transfer as F

def burst(g,threshold=1.,window=7,snap=False):
    g=g.sort_values('time').reset_index(drop=True)
    time=pd.to_datetime(g.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9
    if len(g)<20 or not np.isfinite(g[['x','y','s']].to_numpy(float)).all():raise ValueError('short_nonfinite')
    if not np.allclose(np.diff(time),.1,atol=.002):raise ValueError('noncontiguous')
    origin=0
    if snap:
        hits=np.flatnonzero(g.event.eq('ball_snap'))
        if len(hits)!=1:raise ValueError('nonunique_snap')
        origin=int(hits[0])
        if origin+15>=len(g):raise ValueError('short_post_snap')
        if np.all(g.s.to_numpy()[origin:origin+3]>=threshold):raise ValueError('already_active_at_snap')
    s=g.s.to_numpy(float)
    start=next((i for i in range(origin,min(len(g)-12,origin+21 if snap else len(g)-12)) if np.all(s[i:i+3]>=threshold)),None)
    if start is None:raise ValueError('no_sustained_onset')
    p=savgol_filter(g[['x','y']].to_numpy(float),window,2,axis=0)
    end=min(len(g),start+21);arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p[start:end],axis=0),axis=1))]
    crossing=np.flatnonzero(arc>=1.)
    if not len(crossing):raise ValueError('no_one_yard_travel')
    k=int(crossing[0]);travel=float(.1*(k-1+(1-arc[k-1])/(arc[k]-arc[k-1])))
    onset=float(time[start]-time[origin]);speed05=float(np.linalg.norm(p[start+6]-p[start+4])/.2);speed1=float(np.linalg.norm(p[start+11]-p[start+9])/.2)
    return {'onset':onset,'travel1':travel,'total1':onset+travel,'speed05':speed05,'speed1':speed1,'accel05':float((speed05-s[start])/.5),'onset_frame':start,'origin_frame':origin}

def prepare(data='data',out='private_burst'):
    data=Path(data);out=Path(out);out.mkdir(exist_ok=True);base=pd.read_pickle('private_front/private_rows.pkl')
    source=pd.read_csv(data/'combine_tracking.csv');source=source[source.entity_type.eq('PLAYER')&source.nfl_id.isin(base.nfl_id)&source.drill_name.isin(F.DRILLS+['FORTY_YARD_DASH'])]
    profiles=[];reject={};attempts=[]
    for key,g in source.groupby(['nfl_id','draft_year','event_id']):
        branches=[]
        for threshold in [.5,1.,2.]:
            for window in [5,7,9]:
                try:branches.append(dict(threshold=threshold,window=window,**burst(g,threshold,window)))
                except ValueError as e:reject['source_'+str(e)]=reject.get('source_'+str(e),0)+1
        if len(branches)<5:continue
        m={c:float(np.median([b[c] for b in branches])) for c in ['travel1','speed05','speed1','accel05']}
        m['width']=max(b['travel1'] for b in branches)-min(b['travel1'] for b in branches)
        attempts.append(dict(nfl_id=key[0],draft_year=key[1],event_id=key[2],drill=g.drill_name.iloc[0],**m))
    events=pd.DataFrame(attempts);panel=events.groupby(['nfl_id','drill'])[['travel1','speed05','speed1','accel05','width']].median().unstack('drill');panel.columns=['burst__'+drill+'__'+metric for metric,drill in panel.columns]
    counts=events.groupby(['nfl_id','drill']).size().unstack('drill').fillna(0)
    for drill in F.DRILLS+['FORTY_YARD_DASH']:panel['available__'+drill]=counts[drill] if drill in counts else 0
    panel.reset_index().to_pickle(out/'private_source.pkl');events.to_pickle(out/'private_attempts.pkl')
    frames=[]
    for year in [2023,2024,2025]:
        keys=base[base.draft_year.eq(year)][['game_id','play_id','nfl_id']]
        for chunk in pd.read_csv(data/f'game_tracking_{year}.csv',usecols=['game_id','play_id','nfl_id','time','x','y','s','event'],chunksize=250000):
            match=chunk.merge(keys,on=['game_id','play_id','nfl_id'],validate='many_to_one')
            if len(match):frames.append(match)
        print('Burst game extraction',year,flush=True)
    frames=pd.concat(frames,ignore_index=True);results=[]
    for key,g in frames.groupby(['game_id','play_id','nfl_id']):
        for threshold in [.5,1.,2.]:
            try:results.append(dict(game_id=key[0],play_id=key[1],nfl_id=key[2],threshold=threshold,**burst(g,threshold,7,snap=True)))
            except ValueError as e:reject['game_'+str(threshold)+'_'+str(e)]=reject.get('game_'+str(threshold)+'_'+str(e),0)+1
    records=pd.DataFrame(results);records.to_pickle(out/'private_game_bursts.pkl')
    population={}
    for threshold in [.5,1.,2.]:
        d=base.merge(records[records.threshold.eq(threshold)],on=['game_id','play_id','nfl_id'],validate='one_to_one')
        n=d.groupby('nfl_id').size();d=d[d.nfl_id.isin(n[n>=20].index)].reset_index(drop=True)
        for c in ['travel1','onset','total1']:d['burst_'+c]=d[c]
        d.to_pickle(out/f'private_rows_{threshold}.pkl')
        population[str(threshold)]={'records':len(d),'players':int(d.nfl_id.nunique()),'by_class':d.groupby('draft_year').nfl_id.nunique().to_dict(),'median_onset':float(d.onset.median()),'median_travel1':float(d.travel1.median()),'rank_getoff_onset':float(d[['player_get_off','onset']].corr(method='spearman').iloc[0,1]),'rank_getoff_total':float(d[['player_get_off','total1']].corr(method='spearman').iloc[0,1])}
    receipt={'source_attempts':len(events),'source_players':int(events.nfl_id.nunique()),'population':population,'rejects':reject,'target':'Operational snap-to-sustained-speed onset plus post-onset one-yard smoothed geometric arc travel; no supplied get-off/reaction/LOS/contact equivalence assumed.','branches':'Source nine speed/smoothing scenarios; >=5valid. Primary NFL1yd/s gate, with.5/2supporting; game smoothing7. Whole pre/post-snap traces must be contiguous.'}
    Path('receipts/burst').mkdir(exist_ok=True);Path('receipts/burst/population.json').write_text(json.dumps(receipt,indent=2));return receipt
if __name__=='__main__':prepare()
