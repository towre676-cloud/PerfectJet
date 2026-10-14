"""Predeclared exploratory NFL situation interactions; fixed scouting penalty."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import stress_transfer as T,stress_features as S
from mechanism import player_splits

def run():
    d=pd.read_pickle('private_stress_clock/private_rows.pkl');tr=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);te=d[d.draft_year.eq(2025)].reset_index(drop=True);turns=pd.read_pickle('private_stress_clock/private_turns.pkl');capacity=pd.read_pickle('private_stress_clock/private_capacity.pkl');u,v=T.panels(tr,te,'pressure_event',turns,capacity);p=np.zeros(len(tr))
    for a,b in player_splits(tr,3,T.SEED+1):p[b]=T.context_predict(tr.iloc[a],tr.iloc[b],'pressure_event')
    future=T.context_predict(tr,te,'pressure_event');groups={}
    masks={'third_and_long':lambda x:x.down.eq(3)&x.yards_to_go.ge(5),'blitz_charted':lambda x:x.blitzing.astype(str).str.lower().isin(['true','y','1'])}
    for name,mask in masks.items():
        def response(rows,reference):
            choose=mask(rows);z=pd.DataFrame({'nfl_id':rows.nfl_id,'target':rows.pressure_event-reference})[choose.to_numpy()];counts=z.groupby('nfl_id').size();return z.groupby('nfl_id').target.mean().loc[counts[counts>=10].index]
        a=response(tr,p);b=response(te,future);x=u[u.nfl_id.isin(a.index)].copy();y=v[v.nfl_id.isin(b.index)].copy();x['target']=a.reindex(x.nfl_id).to_numpy();y['target']=b.reindex(y.nfl_id).to_numpy()
        if len(x)<8 or len(y)<5:groups[name]={'training_players':len(x),'test_players':len(y),'status':'insufficient_conditional_population'};continue
        q=y[['nfl_id','target']].copy()
        for family in ['conventional','capacity_only','raw_motion','matched_recovery','stress_curve','robust_recovery']:q[family]=T.predict(x,y,family,1000)
        Path('private_stress_contexts').mkdir(exist_ok=True);q.to_pickle(Path('private_stress_contexts')/f'private_{name}.pkl');groups[name]={'training_players':len(x),**T.comparison(q)}
    r={'fixed_alpha':1000,'minimum_records_per_conditional_player':10,'groups':groups,'scope':'Exploratory situation comparisons using fixed strongest shrinkage; no group-specific tuning or best-context selection. Source adjustment trained only on earlier players; target reference excludes heldout player labels. Outcomes condition on observed NFL context/opportunities; groups are not controlled causal interventions.'};Path('receipts/stress/situation_interactions.json').write_text(json.dumps(r,indent=2));return r
if __name__=='__main__':print(json.dumps(run(),indent=2))
