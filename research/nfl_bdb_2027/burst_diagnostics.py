"""Outcome-blind partition diagnostics and explicitly posthoc shortlist audit."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import burst_transfer as B
def run():
    rows=pd.read_pickle('private_burst/private_rows_1.0.pkl');rng=np.random.default_rng(74123);correlations={k:[] for k in ['onset','travel1','total1','player_get_off']}
    for repeat in range(200):
        pairs={k:([],[]) for k in correlations}
        for player,g in rows.groupby('nfl_id'):
            games=g.game_id.unique();rng.shuffle(games);cut=len(games)//2
            if cut<2 or len(games)-cut<2:continue
            a=g[g.game_id.isin(games[:cut])];b=g[g.game_id.isin(games[cut:])]
            for metric in pairs:pairs[metric][0].append(a[metric].mean());pairs[metric][1].append(b[metric].mean())
        for metric,(a,b) in pairs.items():correlations[metric].append(float(spearmanr(a,b).statistic))
    diagnostic={'repeats':200,'same_primary_cohort':True,'game_half_rank_quantiles':{k:np.quantile(v,[.025,.5,.975]).tolist() for k,v in correlations.items()},'scope':'Random recorded-game halves; measurement/role/context sensitivity, not independent talent ground truth or an accuracy ceiling.'}
    Path('receipts/burst/repeatability.json').write_text(json.dumps(diagnostic,indent=2))
    # Secondary decision diagnostic, added after primary MSE inspection. Its
    # definition and all model results remain explicit; no winner selection.
    reports=[]
    for result in sorted(Path('receipts/burst').glob('burst_*.json')):
        if result.name in ['burst_design.json']:continue
        r=json.loads(result.read_text())
        if 'target' not in r or 'seed' not in r:continue
        directory=Path(f"private_burst_model_{r['target']}_{r['threshold']}_{r['seed']}")
        files=list(directory.glob('private_fold_*.pkl'))+list(directory.glob('private_forward.pkl'))
        for file in files:
            q=pd.read_pickle(file);n=int(np.ceil(len(q)/4));truth=set(q.nsmallest(n,'target').nfl_id);models={}
            for family in ['conventional','burst','repeat_precision','selected']:
                shortlisted=set(q.nsmallest(n,family).nfl_id);models[family]={'hits':len(truth&shortlisted),'selected':n}
            reports.append({'target':r['target'],'threshold':r['threshold'],'seed':r['seed'],'partition':file.stem.replace('private_',''),'players':len(q),'models':models})
    Path('receipts/burst/shortlist.json').write_text(json.dumps({'posthoc_after_primary_MSE':True,'rule':'Best predicted quarter versus best observed quarter within each held-out fold/class; lower operational time is better. Every family and fold retained.','scope':'Descriptive decision metric, not frozen unseen-class confirmation or selection-adjusted advantage. Context target differs by training fold.','reports':reports},indent=2))
    return diagnostic
if __name__=='__main__':run()
