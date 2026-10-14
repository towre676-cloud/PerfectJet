"""Archive every stress trial and aggregate repeated capacity comparisons."""
from pathlib import Path
import json,numpy as np,pandas as pd
import stress_transfer as T

def summarize():
    out=Path('receipts/stress');out.mkdir(exist_ok=True)
    for label,folder in [('initial','private_stress'),('capacity_pilot','private_stress_clock'),('capacity_controlled','private_stress_capacity_controlled')]:
        for target in ['pressure_event','player_get_off']:
            r=json.loads(Path(folder,target,'results.json').read_text());out.joinpath(label+'_'+target+'.json').write_text(json.dumps(r,indent=2))
    panels=[];reports=[]
    for seed in [T.SEED,T.SEED+200,T.SEED+400]:
        folder='private_stress_capacity_controlled/pressure_event' if seed==T.SEED else f'private_stress_capacity_repeat_{seed}';p=Path(folder);q=pd.concat([pd.read_pickle(p/f'private_outer_{i}.pkl') for i in range(4)]).set_index('nfl_id').sort_index();panels.append(q);reports.append(json.loads((p/'results.json').read_text()));out.joinpath(f'controlled_repeat_{seed}.json').write_text(json.dumps(reports[-1],indent=2))
    rng=np.random.default_rng(T.SEED+50);result={}
    for f in reports[0]['development']['comparisons']:
        delta=np.mean([((p.target-p.conventional)**2-(p.target-p[f])**2).to_numpy() for p in panels],axis=0);base=np.mean([r['development']['mse']['conventional'] for r in reports]);result[f]={'relative_gain':float(delta.mean()/base),'absolute_gain':float(delta.mean()),'conditional_ci95':np.quantile(rng.choice(delta,(5000,len(delta)),replace=True).mean(1),[.025,.975]).tolist(),'split_gains':[r['development']['comparisons'][f]['relative_gain'] for r in reports]}
    out.joinpath('controlled_repeated_partitions.json').write_text(json.dumps({'partitions':3,'players':45,'families':result,'scope':'Same45players, context references refitted per partition; resampling fixed averaged player errors. Not three independent studies or full training uncertainty.'},indent=2));return result
if __name__=='__main__':print(json.dumps(summarize(),indent=2))
