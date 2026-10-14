"""Repeat player partitions and test physical interactions under matched budgets.

Only earlier seasons are accessed. These repetitions are correlated diagnostics,
not new independent studies and not a fresh 2025 test.
"""
from pathlib import Path
import json
import numpy as np,pandas as pd
import observability as O
import analysis as A
from mechanism import player_splits

def run(out):
    out=Path(out);rows=pd.read_pickle(out/'private_rows.pkl');dev=rows[rows.draft_year.isin([2023,2024])].reset_index(drop=True);records=[];deltas=[]
    for seed in [A.SEED+710,A.SEED+910]:
        pred={k:np.zeros(len(dev)) for k in ['conventional','target_motion']};folds=[]
        for fold,(a,b) in enumerate(player_splits(dev,4,seed)):
            tr=dev.iloc[a].reset_index(drop=True);te=dev.iloc[b]
            for family in pred:
                loss=[]
                for config in O.CONFIGS:
                    vals=[]
                    for i,j in player_splits(tr,3,seed+1+fold):vals.append(O.score(tr.iloc[j],O.fit_predict(tr.iloc[i],tr.iloc[j],'future_speed',family,True,config,seed+1+fold),'future_speed'))
                    loss.append(float(np.mean(vals)))
                ci=int(np.argmin(loss));pred[family][b]=O.fit_predict(tr,te,'future_speed',family,True,O.CONFIGS[ci],seed+1+fold);folds.append({'family':family,'fold':fold,'chosen_config':ci,'inner_mse':loss})
            print('Partition check',seed,fold,flush=True)
        delta=pd.DataFrame({'id':dev.nfl_id,'delta':(dev.future_speed-pred['conventional'])**2-(dev.future_speed-pred['target_motion'])**2}).groupby('id').delta.mean();deltas.append(delta)
        record={'seed':seed,'baseline_mse':O.score(dev,pred['conventional'],'future_speed'),'motion_mse':O.score(dev,pred['target_motion'],'future_speed'),'increment':O.interval(dev,pred['conventional'],pred['target_motion'],'future_speed'),'folds':folds};records.append(record)
        for k,v in pred.items():pd.DataFrame({'nfl_id':dev.nfl_id,'prediction':v}).to_pickle(out/f'private_stability_{seed}_{k}.pkl')
        (out/'stability_progress.json').write_text(json.dumps(records,indent=2))
    initial=json.loads((out/'absolute_speed/results.json').read_text())['nested']['comparisons']['target_motion_increment']
    p0=pd.read_pickle(out/'absolute_speed/private_nested_conventional_with_state.pkl');p1=pd.read_pickle(out/'absolute_speed/private_nested_target_motion_with_state.pkl');first=pd.DataFrame({'id':p0.nfl_id,'delta':(p0.truth-p0.prediction)**2-(p1.truth-p1.prediction)**2}).groupby('id').delta.mean()
    average=pd.concat([first,*deltas],axis=1).mean(axis=1).to_numpy();rng=np.random.default_rng(A.SEED);ci=np.quantile(rng.choice(average,(5000,len(average)),replace=True).mean(axis=1),[.025,.975])
    result={'status':'completed_actual_data_repeated_partition_check','initial_seed_increment':initial,'repeated_partitions':records,'three_partition_mean_player_delta_mse':float(average.mean()),'conditional_ci95':ci.tolist(),'scope':'All repetitions reuse the same 44 earlier-season players. Conditional bootstrap averages each player over partitions; no independent-replication claim.'};(out/'stability.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':run(Path(__file__).parent/'private_observability')
