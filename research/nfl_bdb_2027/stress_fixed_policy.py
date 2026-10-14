"""Adaptive fixed maximal-shrinkage audit, all families retained without search."""
from pathlib import Path
import json
import pandas as pd
import stress_transfer as T,capacity_stress as C
from mechanism import player_splits

def run(seed=T.SEED,forward=True):
    out=Path(f'private_stress_fixed_{seed}');out.mkdir(exist_ok=True);d=pd.read_pickle('private_stress_clock/private_rows.pkl');turns=pd.read_pickle('private_stress_clock/private_turns.pkl');caps=pd.read_pickle('private_stress_clock/private_capacity.pkl');dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);test=d[d.draft_year.eq(2025)].reset_index(drop=True);panels=[]
    for fold,(a,b) in enumerate(player_splits(dev,4,seed)):
        u,v=T.panels(dev.iloc[a].reset_index(drop=True),dev.iloc[b].reset_index(drop=True),'pressure_event',turns,caps);q=v[['nfl_id','target']].copy()
        for f in C.FAMILIES:q[f]=T.predict(u,v,f,1000)
        q.to_pickle(out/f'private_fold_{fold}.pkl');panels.append(q)
    r={'alpha':1000,'adaptive_after_primary_and_situation_inspection':True,'no_family_selection':True,'seed':seed,'development':T.comparison(pd.concat(panels,ignore_index=True))}
    if forward:
        u,v=T.panels(dev,test,'pressure_event',turns,caps);q=v[['nfl_id','target']].copy()
        for f in C.FAMILIES:q[f]=T.predict(u,v,f,1000)
        q.to_pickle(out/'private_forward.pkl');r['exploratory_2025']=T.comparison(q)
    (out/'results.json').write_text(json.dumps(r,indent=2));Path('receipts/stress',f'fixed_policy_{seed}.json').write_text(json.dumps(r,indent=2));return r
if __name__=='__main__':
    for seed in [T.SEED,T.SEED+200,T.SEED+400]:run(seed,seed==T.SEED)
