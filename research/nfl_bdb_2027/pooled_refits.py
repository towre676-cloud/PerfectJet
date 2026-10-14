"""Training-subset sensitivity; deliberately not a bootstrap confidence interval."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import pooled_transfer as P
def run(repeats=64):
    units,turns=P.prepare();rows=pd.read_pickle('private_front/private_rows.pkl');getoff=rows.groupby('nfl_id').player_get_off.mean();rng=np.random.default_rng(90026);gains={k:[] for k in ['pressure_event','player_get_off']};specs={}
    for outcome,prefix in [('pressure_event','results'),('player_get_off','getoff')]:
        r=json.loads(Path('receipts/pooled',f'{prefix}_{P.SEED}.json').read_text())
        specs[outcome]={x['family']:x['spec'] for x in r['forward_selection'] if x['family'] in ['conventional','pooled']}
    for repeat in range(repeats):
        dev=units[units.draft_year.lt(2025)];test=units[units.draft_year.eq(2025)].copy();parts=[]
        for year,g in dev.groupby('draft_year'):
            parts.append(g.iloc[rng.choice(len(g),int(np.ceil(.8*len(g))),replace=False)])
        train=pd.concat(parts).reset_index(drop=True)
        for outcome in gains:
            a=train.copy();b=test.copy();a['outcome_kind']=outcome;b['outcome_kind']=outcome
            if outcome=='player_get_off':a['target']=a.nfl_id.map(getoff);b['target']=b.nfl_id.map(getoff)
            alpha=specs[outcome]['pooled'][3];a,b=P.augment(a,b,turns,alpha)
            base=P.predict(a,b,specs[outcome]['conventional']);motion=P.predict(a,b,specs[outcome]['pooled'])
            error0=(b.target.to_numpy()-base)**2;error1=(b.target.to_numpy()-motion)**2;delta=error0-error1
            sampled=rng.choice(len(b),len(b),replace=True)
            gains[outcome].append({'baseline_mse':float(error0.mean()),'pooled_mse':float(error1.mean()),'relative_gain':float(delta.mean()/error0.mean()),'resampled_test_absolute_gain':float(delta[sampled].mean())})
        if repeat%16==15:print('Training-subset refits',repeat+1,flush=True)
    result={'refits_per_outcome':repeats,'training_fraction':.8,'selected_configs_fixed':specs,'scope':'Class-stratified80%subsamples without replacement refit source nuisance, demand/noise summaries and scouting pipeline. Evaluated-player bootstrap added as sensitivity. Quantile ranges are not calibrated95%confidence intervals and do not repeat selection or adaptive searches.2025already inspected.','results':{}}
    for outcome,g in gains.items():
        result['results'][outcome]={'runs':g,'relative_gain_quantiles':np.quantile([x['relative_gain'] for x in g],[.025,.5,.975]).tolist(),'test_resampled_absolute_gain_quantiles':np.quantile([x['resampled_test_absolute_gain'] for x in g],[.025,.5,.975]).tolist(),'positive_refits':sum(x['relative_gain']>0 for x in g)}
    Path('receipts/pooled/refit_sensitivity.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':run()
