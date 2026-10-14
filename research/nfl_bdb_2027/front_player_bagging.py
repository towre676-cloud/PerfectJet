"""Variance adaptation: bag whole training athletes, not only rush records."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import front_transfer as F,front_diagnostics as D
from mechanism import player_splits

def ensemble(tr,te,cols,configs,seed,count=16):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('original player leakage before bootstrap replicas')
    rng=np.random.default_rng(seed);units=tr[['nfl_id','draft_year']].drop_duplicates();groups={k:g for k,g in tr.groupby('nfl_id')};pred={k:np.zeros(len(te)) for k in ['conventional','combined']}
    for iteration in range(count):
        blocks=[];replica=0
        for _,g in units.groupby('draft_year'):
            for player in rng.choice(g.nfl_id.to_numpy(),len(g),replace=True):
                q=groups[player].copy();q['nfl_id']=-1-replica;replica+=1;blocks.append(q)
        boot=pd.concat(blocks,ignore_index=True)
        for family in pred:pred[family]+=F.fit_predict(boot,te,[] if family=='conventional' else cols,F.CONFIGS[configs[family]],'pressure_event')/count
    return pred

def run(folder,out,count=16,phase=None):
    d=pd.read_pickle(Path(folder)/'private_rows.pkl' if folder=='private_front_bouts' else 'private_front/private_rows.pkl');cols=[c for c in d if c.startswith(('motion__','skill__'))];r=json.loads((Path(folder)/'pressure_event/results.json').read_text());dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);test=d[d.draft_year.eq(2025)].reset_index(drop=True);pp={k:np.zeros(len(dev)) for k in ['conventional','combined']};out=Path(out);out.mkdir(exist_ok=True)
    for fold,(i,j) in enumerate(player_splits(dev,4,F.SEED)):
        checkpoint=out/f'private_fold_{fold}.pkl'
        if checkpoint.exists():
            q=pd.read_pickle(checkpoint);assert q.nfl_id.tolist()==dev.iloc[j].nfl_id.tolist()
            for k in pp:pp[k][j]=q[k].to_numpy()
            continue
        if phase is not None and phase!=fold:continue
        configs={k:next(row['config'] for row in r['folds'] if row['fold']==fold and row['family']==k) for k in pp};p=ensemble(dev.iloc[i],dev.iloc[j],cols,configs,F.SEED+2300+fold,count)
        for k in p:pp[k][j]=p[k]
        q=dev.iloc[j][['nfl_id','pressure_event']].copy()
        for k,v in p.items():q[k]=v
        q.to_pickle(checkpoint)
        print('Player-bagging outer',folder,fold,flush=True)
    if phase is not None and phase!='forward':return {'status':'outer_checkpoint_completed','fold':phase}
    if not all((out/f'private_fold_{fold}.pkl').exists() for fold in range(4)):raise ValueError('All outer folds required before bagging forward evaluation')
    configs={k:next(row['config'] for row in r['selection'] if row['family']==k) for k in pp};tp=ensemble(dev,test,cols,configs,F.SEED+2400,count);result={'bagged_models_per_family':count,'configs':'Earlier-player / 2024 selected unbagged configurations retained; both conventional and combined receive identical athlete bagging','adaptive_followup':True,'source_folder':folder}
    for split,rows,p in [('nested',dev,pp),('exploratory_2025',test,tp)]:
        q=rows[['nfl_id','pressure_event']].copy()
        for k,v in p.items():q[k]=v
        # Compatibility for the aggregate scoring adapter; not extra fitted models.
        q['sprint']=q.combined;q['skills']=q.combined;v=D.player_rates(q);result[split]={'mse':{k:v['mse'][k] for k in ['conventional','combined']},'combined':v['comparisons']['combined'],'players':v['players']};q.drop(columns=['sprint','skills']).to_pickle(out/f'private_{split}.pkl')
    (out/'results.json').write_text(json.dumps(result,indent=2));return result

if __name__=='__main__':
    for folder,out in [('private_front_macro','private_front_bagged'),('private_front_bouts','private_front_bouts_bagged')]:run(folder,out)
