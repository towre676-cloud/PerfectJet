"""Primary capacity uncertainty refits the context reference and scout model."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import stress_transfer as T,capacity_stress as C
from mechanism import player_splits

def run(count=64):
    out=Path('private_stress_refits');out.mkdir(exist_ok=True);d=pd.read_pickle('private_stress_clock/private_rows.pkl');tr=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);te=d[d.draft_year.eq(2025)].reset_index(drop=True);turns=pd.read_pickle('private_stress_clock/private_turns.pkl');caps=pd.read_pickle('private_stress_clock/private_capacity.pkl');base=T.unit_rows(d).merge(caps,on='nfl_id',how='left');base['capacity_available']=base['sprint__ceiling'].notna().astype(float)
    for drill in C.S.F.DRILLS:base['stress__'+drill+'__count']=base.nfl_id.map(turns[turns.drill.eq(drill)].groupby('nfl_id').size())
    base=base.set_index('nfl_id');groups={k:g for k,g in tr.groupby('nfl_id')};units=tr[['nfl_id','draft_year']].drop_duplicates();r=json.loads(Path('private_stress_capacity_controlled/pressure_event/results.json').read_text());configs={f:next(x['specification'] for x in r['forward_selection'] if x['family']==f) for f in ['conventional','capacity_only']};rng=np.random.default_rng(T.SEED+1900);fixed=[];joint=[];checkpoint=out/'private_checkpoint.json'
    if checkpoint.exists():v=json.loads(checkpoint.read_text());assert v['count']==count;fixed=v['fixed'];joint=v['joint'];rng.bit_generator.state=v['rng']
    for iteration in range(len(fixed),count):
        blocks=[];meta=[];replica=0
        for _,g in units.groupby('draft_year'):
            for player in rng.choice(g.nfl_id.to_numpy(),len(g),replace=True):
                row=groups[player].copy();row['origin_id']=player;row['nfl_id']=-1-replica;record=base.loc[[player]].reset_index();record['nfl_id']=-1-replica;replica+=1;blocks.append(row);meta.append(record)
        boot=pd.concat(blocks,ignore_index=True);reference=np.zeros(len(boot));original=boot.copy();original['nfl_id']=original.origin_id;cache=out/f'context_{iteration}'
        for i,j in player_splits(original,3,T.SEED+2):
            assert not set(boot.iloc[i].origin_id)&set(boot.iloc[j].origin_id)
            reference[j]=T.context_predict(boot.iloc[i],boot.iloc[j],'pressure_event',cache=cache)
        future=T.context_predict(boot,te,'pressure_event',cache=cache);u=pd.concat(meta,ignore_index=True);v=base.loc[te.nfl_id.unique()].reset_index();targets=pd.DataFrame({'nfl_id':boot.nfl_id,'target':boot.pressure_event-reference}).groupby('nfl_id').target.mean();u['target']=targets.reindex(u.nfl_id).to_numpy();target_test=pd.DataFrame({'nfl_id':te.nfl_id,'target':te.pressure_event-future}).groupby('nfl_id').target.mean();v['target']=target_test.reindex(v.nfl_id).to_numpy();pred={f:T.predict(u,v,*config) for f,config in configs.items()};delta=(v.target-pred['conventional'])**2-(v.target-pred['capacity_only'])**2;fixed.append(float(delta.mean()));joint.append(float(rng.choice(delta,len(delta),replace=True).mean()));checkpoint.write_text(json.dumps({'count':count,'fixed':fixed,'joint':joint,'rng':rng.bit_generator.state}))
        if iteration%8==0:print('Context and capacity refits',iteration,flush=True)
    result={'replicates':count,'configs_fixed':configs,'fixed_forward_ci95':np.quantile(fixed,[.025,.975]).tolist(),'joint_training_test_ci95':np.quantile(joint,[.025,.975]).tolist(),'fixed_forward_gain':fixed,'joint_gain':joint,'scope':'Class-stratified athlete bootstrap; replica multiplicity preserved. Context target-reference and scout transforms/models refitted. Training residual crossfits group original players so duplicate copies do not cross folds. Configurations fixed; no complete selection or adaptive-search correction.64replicates give coarse tail estimates.'};Path('receipts/stress/capacity_refits.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
