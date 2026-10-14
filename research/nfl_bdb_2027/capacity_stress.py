"""Adaptive progress-aligned recovery beyond tracked straight-line capacity."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import stress_features as S,stress_transfer as T
FAMILIES=['conventional','capacity_only','raw_motion','matched_recovery','stress_curve','robust_recovery']

def capacity(data='data',out='private_stress_clock'):
    ids=set(pd.read_pickle('private_front/private_rows.pkl').nfl_id);tr=pd.read_csv(Path(data)/'combine_tracking.csv');tr=tr[tr.entity_type.eq('PLAYER')&tr.nfl_id.isin(ids)&tr.drill_name.eq('FORTY_YARD_DASH')];rows=[]
    for key,g in tr.groupby(['nfl_id','event_id']):
        g=g.sort_values('time');s=g.s.to_numpy(float);time=pd.to_datetime(g.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9
        if len(s)<35 or not np.isfinite(s).all() or not np.allclose(np.diff(time),.1,atol=.002):continue
        start=next((i for i in range(len(s)-2) if np.all(s[i:i+3]>2)),None)
        if start is None or start+30>=len(s):continue
        rows.append({'nfl_id':key[0],'sprint__ceiling':float(np.quantile(s[start:min(len(s),start+51)],.95)),'sprint__speed1':float(s[start+10]),'sprint__speed3':float(s[start+30])})
    panel=pd.DataFrame(rows).groupby('nfl_id').median().reset_index();Path(out).mkdir(exist_ok=True);panel.to_pickle(Path(out)/'private_capacity.pkl');Path(out,'capacity_population.json').write_text(json.dumps({'attempts':len(rows),'players':len(panel),'rule':'Median attempt p95 speed over firstup-to5s after three sustained speeds>2yd/s; speed at1/3s. Operational source capacity, not physiological maximum or official timed start.'},indent=2));return panel

def run(target='pressure_event',seed=T.SEED,forward=True,out=None,share_capacity_availability=True):
    panel=pd.read_pickle('private_stress_clock/private_capacity.pkl');return T.run(target,seed,forward,out,source_folder='private_stress_clock',capacity=panel,family_list=FAMILIES,share_capacity_availability=share_capacity_availability)
if __name__=='__main__':
    S.prepare(out='private_stress_clock',clock=True);capacity()
    for target in ['pressure_event','player_get_off']:run(target,out=f'private_stress_capacity_controlled/{target}')
