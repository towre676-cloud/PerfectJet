"""Expand the canonical duration audit; diagnose game-sample target stability."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import pooled_transfer as P
import canonical_transfer as C
from mechanism import player_splits

def run():
    units,turns=P.prepare();rows=pd.read_pickle('private_front/private_rows.pkl')
    # Restore the canonical five-availability baseline, rather than silently
    # equating it to the new count-controlled benchmark.
    units=units.drop(columns=[c for c in units if c.startswith('available__attempts_') or c=='available__capacity'])
    sp=pd.read_pickle('private_front/private_sprints.pkl');units['available__FORTY_YARD_DASH']=units.nfl_id.isin(sp.nfl_id).astype(float)
    families={'conventional':[],'duration_combined':P.duration_columns(units)}
    results=[]
    for k in range(12):
        seed=C.SEED+200*k
        r=C.evaluate(units,families,out=f'private_pooled_canonical_{seed}',seed=seed,forward=k==0)
        results.append(r)
    comparison={'design':'Twelve nested player partitions of the same45earlier athletes, using restored five-availability baseline. Not twelve independent studies. Includes original three seeds. All retained; no favorable-seed selection.','results':results}
    Path('receipts/pooled/canonical_stability.json').write_text(json.dumps(comparison,indent=2))
    rng=np.random.default_rng(83410);correlations=[];half_sizes=[]
    for repeat in range(200):
        a=[];b=[]
        for player,g in rows.groupby('nfl_id'):
            games=g.game_id.unique();rng.shuffle(games);cut=len(games)//2
            if cut<2 or len(games)-cut<2:continue
            left=g[g.game_id.isin(games[:cut])];right=g[g.game_id.isin(games[cut:])]
            a.append(left.pressure_event.mean());b.append(right.pressure_event.mean());half_sizes.append(min(len(left),len(right)))
        correlations.append(float(spearmanr(a,b).statistic))
    diag={'repeats':200,'players':int(rows.nfl_id.nunique()),'rank_correlation_quantiles':np.quantile(correlations,[.025,.5,.975]).tolist(),'smaller_half_records_quantiles':np.quantile(half_sizes,[.05,.5,.95]).tolist(),'scope':'Random halves of recorded games; direct pressure-rate reproducibility, conditional on workload, contexts and annotation. No classical reliability correction, no independent ability ground truth and no predictive accuracy ceiling.'}
    Path('receipts/pooled/outcome_repeatability.json').write_text(json.dumps(diag,indent=2))
if __name__=='__main__':run()
