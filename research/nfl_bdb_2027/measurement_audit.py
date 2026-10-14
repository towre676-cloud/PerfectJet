"""Reproduce the derivative/reported-speed agreement audit without NFL outcomes."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

def run(data,out):
    data,out=Path(data),Path(out);out.mkdir(parents=True,exist_ok=True)
    p=pd.read_csv(data/'players.csv');d=pd.read_csv(data/'combine_tracking.csv')
    d=d[d.entity_type.eq('PLAYER')&d.nfl_id.isin(p.loc[p.nfl_position.eq('WR'),'nfl_id'])&d.drill_type.eq('SKILL_DRILLS_WR')]
    pairs=[];rejected=0
    for key,g in d.groupby(['nfl_id','event_id']):
        g=g.sort_values('time');t=pd.to_datetime(g.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9
        if len(g)<7 or not np.allclose(np.diff(t),.1,atol=.015):rejected+=1;continue
        v=np.gradient(savgol_filter(g[['x','y']].to_numpy(float),7,3,axis=0),.1,axis=0)
        s=np.linalg.norm(v,axis=1);reported=g.s.to_numpy(float)
        mask=np.isfinite(s)&np.isfinite(reported)&(reported>1);mask[:3]=False;mask[-3:]=False
        pairs.append(np.c_[s[mask],reported[mask]])
    a=np.concatenate(pairs)
    q={'scope':'measurement consistency only; no predictive outcomes used',
       'interior_active_wr_frames':len(a),'rejected_attempts_time_quality':rejected,
       'coordinate_derived_vs_reported_speed_correlation':float(np.corrcoef(a.T)[0,1]),
       'median_absolute_difference':float(np.median(np.abs(a[:,0]-a[:,1]))),
       'median_ratio':float(np.median(a[:,0]/a[:,1])),
       'interpretation':'Agreement supports the coordinate derivative scale; neither signal is independent ground truth. No predictive-value claim.'}
    (out/'speed_consistency.json').write_text(json.dumps(q,indent=2));return q

if __name__=='__main__':
    root=Path(__file__).parent;print(json.dumps(run(root/'data',root/'receipts/mechanism_push'),indent=2))
