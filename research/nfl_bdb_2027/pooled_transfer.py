"""Nested player-held-out comparison against the duration scouting lead."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import canonical_transfer as C
import front_transfer as F
from mechanism import player_splits
from pooled_recovery import PooledRecovery

SEED=C.SEED+21000
FAMILIES=['conventional','capacity','duration','pooled','duration_pooled']
def prepare():
    rows=pd.read_pickle('private_front/private_rows.pkl')
    units=pd.read_pickle('private_canonical_vendor/players.pkl').merge(rows[['nfl_id','combine_position']].drop_duplicates(),on='nfl_id',validate='one_to_one')
    caps=pd.read_pickle('private_stress_clock/private_capacity.pkl')
    units=units.merge(caps,on='nfl_id',how='left',validate='one_to_one')
    units['available__capacity']=units.sprint__ceiling.notna().astype(float)
    turns=pd.read_pickle('private_stress_clock/private_turns.pkl')
    for drill in F.DRILLS:
        counts=turns[turns.drill.eq(drill)].groupby('nfl_id').event_id.nunique()
        units['available__attempts_'+drill]=units.nfl_id.map(counts).fillna(0)
    return units,turns
def duration_columns(units):
    prefixes=sum(C.V.FAMILIES.values(),[])
    return [c for c in units if c.startswith('movement__') and any(c.split('__')[-1].startswith(p) for p in prefixes)]
def augment(tr,te,turns,penalty):
    model=PooledRecovery(turns,penalty).fit(tr)
    a=tr.merge(model.transform(tr),on='nfl_id',validate='one_to_one')
    b=te.merge(model.transform(te),on='nfl_id',validate='one_to_one')
    return a,b
def bank():
    specs=[('conventional',a,0,10.) for a in (1.,10.,100.)]
    for family in FAMILIES[1:]:
        for a in (10.,100.):
            for k in (2,4):
                for penalty in ((1.,10.,100.) if 'pooled' in family else (10.,)):
                    specs.append((family,a,k,penalty))
    return specs
def predict(a,b,spec):
    family,alpha,k,penalty=spec
    duration=duration_columns(a)
    pooled=[c for c in a if c.startswith('pool__') and '__b' in c]
    caps=[c for c in a if c.startswith('sprint__')]
    cols={'conventional':[],'capacity':caps,'duration':duration,'pooled':caps+pooled,'duration_pooled':duration+caps+pooled}[family]
    clip=not ('outcome_kind' in a and a.outcome_kind.iloc[0]=='player_get_off')
    return C.predict(a,b,cols,alpha,k,clip=clip)
def evaluate(units,turns,out='private_pooled',seed=SEED,forward=True):
    out=Path(out);out.mkdir(exist_ok=True)
    specs=bank();labels=FAMILIES+['selected'];dev=units[units.draft_year.lt(2025)].reset_index(drop=True);test=units[units.draft_year.eq(2025)].reset_index(drop=True)
    def panel(tr,te):
        model=PooledRecovery(turns).fit(tr);cache={}
        for p in (1.,10.,100.):
            model.penalty=p
            cache[p]=(tr.merge(model.transform(tr),on='nfl_id',validate='one_to_one'),te.merge(model.transform(te),on='nfl_id',validate='one_to_one'))
        return cache
    def predictions(cache):return [predict(*cache[s[3]],s) for s in specs]
    def choose(losses,name):
        options=range(len(specs)) if name=='selected' else [i for i,s in enumerate(specs) if s[0] in ['conventional',name]]
        return min(options,key=lambda i:losses[i])
    pp={n:np.zeros(len(dev)) for n in labels};selection=[]
    for fold,(i,j) in enumerate(player_splits(dev,4,seed)):
        tr=dev.iloc[i].reset_index(drop=True);te=dev.iloc[j]
        losses=np.zeros(len(specs))
        for a,b in player_splits(tr,3,seed+fold+1):
            cache=panel(tr.iloc[a],tr.iloc[b]);pred=predictions(cache)
            losses+=[float(np.mean((tr.iloc[b].target-p)**2))/3 for p in pred]
        pred=predictions(panel(tr,te))
        for name in labels:
            index=choose(losses,name);pp[name][j]=pred[index]
            selection.append({'fold':fold,'family':name,'spec':specs[index]})
        print('Pooled outer',seed,fold,flush=True)
    result={'seed':seed,'bank':specs,'outer_selection':selection,'prior_2025_inspection':True,'outcome':units.outcome_kind.iloc[0] if 'outcome_kind' in units else 'pressure_event','scope':'Equal-player conditional recorded rookie outcome. Whole-player nested choices; all source nuisance/geometry/noise and scouting transforms fitted within training folds. No unobserved individualized curve identification claim.'}
    reports=[('development',dev,pp)]
    if forward:
        tr=dev[dev.draft_year.eq(2023)];va=dev[dev.draft_year.eq(2024)]
        pred=predictions(panel(tr,va));losses=[float(np.mean((va.target-p)**2)) for p in pred]
        pred=predictions(panel(dev,test));tp={};chosen=[]
        for name in labels:
            index=choose(losses,name);tp[name]=pred[index];chosen.append({'family':name,'spec':specs[index]})
        result['forward_selection']=chosen;result['forward_validation_mse']=losses
        reports.append(('exploratory_2025',test,tp))
    for name,rows,pred in reports:
        result[name]={'players':len(rows),'mse':{f:float(np.mean((rows.target-p)**2)) for f,p in pred.items()},'versus_conventional':{f:C.V.compare(rows.target.to_numpy(),pred['conventional'],p) for f,p in pred.items() if f!='conventional'},'versus_duration':{f:C.V.compare(rows.target.to_numpy(),pred['duration'],pred[f]) for f in ['pooled','duration_pooled','selected']}}
        q=rows[['nfl_id','draft_year','target']].copy()
        for f,p in pred.items():q[f]=p
        q.to_pickle(out/f'private_{name}.pkl')
    (out/'results.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
    units,turns=prepare()
    for seed in [SEED,SEED+200,SEED+400]:
        r=evaluate(units,turns,f'private_pooled_{seed}',seed,seed==SEED)
        Path('receipts/pooled',f'results_{seed}.json').write_text(json.dumps(r,indent=2))
