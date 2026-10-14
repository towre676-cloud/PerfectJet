"""Supporting recorded get-off response, retaining pressure as primary."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import pooled_transfer as P
def run():
    units,turns=P.prepare();rows=pd.read_pickle('private_front/private_rows.pkl')
    target=rows.groupby('nfl_id').player_get_off.mean()
    units['target']=units.nfl_id.map(target);units['outcome_kind']='player_get_off'
    for seed in [P.SEED,P.SEED+200,P.SEED+400]:
        result=P.evaluate(units,turns,f'private_pooled_getoff_{seed}',seed,seed==P.SEED)
        Path('receipts/pooled',f'getoff_{seed}.json').write_text(json.dumps(result,indent=2))
    rng=np.random.default_rng(83410);correlations=[]
    for repeat in range(200):
        a=[];b=[]
        for player,g in rows.groupby('nfl_id'):
            games=g.game_id.unique();rng.shuffle(games);cut=len(games)//2
            if cut<2 or len(games)-cut<2:continue
            a.append(g[g.game_id.isin(games[:cut])].player_get_off.mean());b.append(g[g.game_id.isin(games[cut:])].player_get_off.mean())
        correlations.append(float(spearmanr(a,b).statistic))
    Path('receipts/pooled/getoff_repeatability.json').write_text(json.dumps({'repeats':200,'rank_correlation_quantiles':np.quantile(correlations,[.025,.5,.975]).tolist(),'scope':'Recorded game-halves, conditional on actual roles/context and annotation. Supporting target, not a replacement for primary pressure or independently established causal get-off physiology.'},indent=2))
if __name__=='__main__':run()
