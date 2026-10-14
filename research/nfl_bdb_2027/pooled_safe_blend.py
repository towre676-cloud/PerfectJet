"""Adaptive, predeclared finite convex corrections with class consistency.

Exact enumeration of a small weight grid. Choosing zero correction is valid.
This is a robustness experiment, not a claim of a PerfectPower speed advantage.
"""
from pathlib import Path
import itertools,json
import numpy as np
import pandas as pd
import pooled_transfer as P
from mechanism import player_splits

VALUES=(0.,.1,.25,.5,1.)
WEIGHTS=np.array([w for w in itertools.product(VALUES,repeat=3) if sum(w)<=1.])
SPECS=[('capacity',1000.,2,10.),('duration',1000.,2,10.),('pooled',1000.,2,10.)]
def choose(truth,base,motion,classes,guard=True):
    correction=motion-base[:,None]
    losses=(truth[:,None]-base[:,None]-correction@WEIGHTS.T)**2
    gains=(truth-base)[:,None]**2-losses
    # Require a lower one-standard-error gain in each training class.
    # This is a conservative selection heuristic, not a calibrated confidence test.
    scores=[]
    for year in sorted(set(classes)):
        g=gains[classes==year]
        scores.append(g.mean(0)-(g.std(0,ddof=1)/np.sqrt(len(g)) if guard else 0))
    score=np.min(scores,axis=0)
    best=int(np.argmax(score));return best,float(score[best])
def fit(tr,te,turns):
    a,b=P.augment(tr,te,turns,10.)
    base=P.predict(a,b,('conventional',100.,0,10.))
    candidates=np.column_stack([P.predict(a,b,s) for s in SPECS])
    return base,candidates
def run(units,turns,seed=P.SEED,forward=True,prefix='blend'):
    out=Path(f'private_{prefix}_{seed}');out.mkdir(exist_ok=True)
    dev=units[units.draft_year.lt(2025)].reset_index(drop=True);test=units[units.draft_year.eq(2025)].reset_index(drop=True)
    pp={k:np.zeros(len(dev)) for k in ['conventional','capacity','duration','pooled','mean_guard','class_guard','class_mean']};selection=[]
    for fold,(i,j) in enumerate(player_splits(dev,4,seed)):
        tr=dev.iloc[i].reset_index(drop=True);te=dev.iloc[j];bp=np.zeros(len(tr));mp=np.zeros((len(tr),3))
        for a,b in player_splits(tr,3,seed+fold+1):bp[b],mp[b]=fit(tr.iloc[a],tr.iloc[b],turns)
        base,motion=fit(tr,te,turns);pp['conventional'][j]=base
        for k,name in enumerate(['capacity','duration','pooled']):pp[name][j]=motion[:,k]
        for name,classes,guard in [('mean_guard',np.zeros(len(tr)),True),('class_guard',tr.draft_year.to_numpy(),True),('class_mean',tr.draft_year.to_numpy(),False)]:
            index,score=choose(tr.target.to_numpy(),bp,mp,classes,guard)
            pp[name][j]=base+(motion-base[:,None])@WEIGHTS[index]
            selection.append({'fold':fold,'family':name,'weights':WEIGHTS[index].tolist(),'training_selection_score':score})
        print('Blend outer',seed,fold,flush=True)
    result={'seed':seed,'adaptive_after_pooled_scores':True,'grid_population':len(WEIGHTS),'component_specs':SPECS,'selection':selection,'guard_scope':'Lower-one-standard-error heuristic; no calibrated selection-adjusted confidence guarantee. All choices from training players.'}
    splits=[('development',dev,pp)]
    if forward:
        bp=np.zeros(len(dev));mp=np.zeros((len(dev),3))
        for a,b in player_splits(dev,4,seed):bp[b],mp[b]=fit(dev.iloc[a],dev.iloc[b],turns)
        base,motion=fit(dev,test,turns);fp={'conventional':base,**{name:motion[:,k] for k,name in enumerate(['capacity','duration','pooled'])}}
        chosen=[]
        for name,classes,guard in [('mean_guard',np.zeros(len(dev)),True),('class_guard',dev.draft_year.to_numpy(),True),('class_mean',dev.draft_year.to_numpy(),False)]:
            index,score=choose(dev.target.to_numpy(),bp,mp,classes,guard);fp[name]=base+(motion-base[:,None])@WEIGHTS[index]
            chosen.append({'family':name,'weights':WEIGHTS[index].tolist(),'training_selection_score':score})
        result['forward_selection']=chosen;splits.append(('exploratory_2025',test,fp))
    for label,rows,pred in splits:
        result[label]={'mse':{name:float(np.mean((rows.target-p)**2)) for name,p in pred.items()},'comparisons':{name:P.C.V.compare(rows.target.to_numpy(),pred['conventional'],p) for name,p in pred.items() if name!='conventional'}}
        q=rows[['nfl_id','draft_year','target']].copy()
        for name,p in pred.items():q[name]=p
        q.to_pickle(out/f'private_{label}.pkl')
    (out/'results.json').write_text(json.dumps(result,indent=2));Path('receipts/pooled',f'{prefix}_{seed}.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
    units,turns=P.prepare()
    for seed in [P.SEED,P.SEED+200,P.SEED+400]:run(units,turns,seed,seed==P.SEED)
