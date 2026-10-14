"""Same-player repeated-split summaries and selected-config training refits."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import canonical_transfer as C

def repeated():
    folders=['private_canonical']+[f'private_canonical_repeat_{s}' for s in [C.SEED+200,C.SEED+400]];reports=[json.loads(Path(f,'results.json').read_text()) for f in folders];panels=[pd.read_pickle(Path(f,'private_development.pkl')).set_index('nfl_id').sort_index() for f in folders];rng=np.random.default_rng(C.SEED+900);result={}
    for family in reports[0]['development']['comparisons']:
        delta=np.mean([((p.target-p.conventional)**2-(p.target-p[family])**2).to_numpy() for p in panels],axis=0);base=float(np.mean([r['development']['baseline_mse'] for r in reports]));result[family]={'mean_baseline_mse':base,'mean_candidate_mse':base-float(delta.mean()),'relative_gain':float(delta.mean()/base),'absolute_gain':float(delta.mean()),'fixed_prediction_ci95':np.quantile(rng.choice(delta,(5000,len(delta)),replace=True).mean(1),[.025,.975]).tolist(),'split_relative_gains':[r['development']['comparisons'][family]['relative_gain'] for r in reports]}
    out={'players':45,'partitions':3,'scope':'Player-paired average errors over three reused partitions; no independent replication, model refits or adaptive-search correction.','families':result};Path('receipts/canonical/repeated_partitions.json').write_text(json.dumps(out,indent=2));return out

def refits(count=512):
    unit,families=C.prepare();tr=unit[unit.draft_year.isin([2023,2024])];te=unit[unit.draft_year.eq(2025)].reset_index(drop=True);r=json.loads(Path('private_canonical/results.json').read_text());configs={f:next(x['selected'] for x in r['forward_selection'] if x['family']==f) for f in ['conventional','duration_combined']};rng=np.random.default_rng(C.SEED+1200);fixed=[];joint=[];checkpoint=Path('private_canonical/private_refits.json')
    if checkpoint.exists():saved=json.loads(checkpoint.read_text());assert saved['count']==count;fixed=saved['fixed'];joint=saved['joint'];rng.bit_generator.state=saved['rng']
    for iteration in range(len(fixed),count):
        boot=pd.concat([g.iloc[rng.integers(0,len(g),len(g))] for _,g in tr.groupby('draft_year')],ignore_index=True);pred={}
        for label,(family,a,k) in configs.items():pred[label]=C.predict(boot,te,families[family],a,k)
        delta=(te.target-pred['conventional'])**2-(te.target-pred['duration_combined'])**2;fixed.append(float(delta.mean()));joint.append(float(rng.choice(delta,len(delta),replace=True).mean()));checkpoint.write_text(json.dumps({'count':count,'fixed':fixed,'joint':joint,'rng':rng.bit_generator.state}))
        if iteration%64==0:print('Canonical training-player refits',iteration,flush=True)
    result={'replicates':count,'family_focus':'duration_combined; exploratory lead supported by positive point gains in all three earlier partitions, not selected as best2025score','configs_fixed':configs,'fixed_forward_ci95':np.quantile(fixed,[.025,.975]).tolist(),'joint_training_test_ci95':np.quantile(joint,[.025,.975]).tolist(),'fixed_forward_delta':fixed,'joint_training_test_delta':joint,'scope':'Class-stratified player resampling refits imputers, scalers, position encoder, physical residualizer, PCA and ridge. Earlier selected configs fixed; does not repeat complete selection or adjust adaptive hypothesis choice. Not a guarantee of generalization.'};Path('receipts/canonical/refits.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':repeated();refits()
