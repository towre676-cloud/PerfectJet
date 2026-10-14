"""Aggregate source repeatability diagnostics, no predictive selection."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.stats import spearmanr
def run(source,out):
    pairs=[]
    for key,g in source.sort_values('event_id').groupby(['nfl_id','drill_name']):
        if len(g)>=2:pairs.append((key[0],g.iloc[0],g.iloc[-1]))
    selected={'speed_acceleration_area':12,'speed_turn_rate_area':13,'acceleration_turn_rate_area':15,'approach_occupancy':18,'brake_occupancy':19,'redirect_occupancy':20,'recover_occupancy':21};r={'repeat_attempt_pairs':len(pairs),'players':len(set(x[0] for x in pairs)),'selection':'Seven predesignated radius-1-second descriptors; no outcome-dependent ranking','metrics':{}}
    for name,j in selected.items():
        a=np.array([x[1][f'order_10_{j}'] for x in pairs]);b=np.array([x[2][f'order_10_{j}'] for x in pairs]);r['metrics'][name]={'spearman':float(spearmanr(a,b).statistic)}
    Path(out).write_text(json.dumps(r,indent=2));return r
if __name__=='__main__':print(json.dumps(run(pd.read_pickle('private_ordered_motion/private_source.pkl'),'private_ordered_motion/repeatability.json'),indent=2))
