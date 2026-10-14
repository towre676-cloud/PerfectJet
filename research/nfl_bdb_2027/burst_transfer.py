"""Fold-local scouting tests of observed burst transport, not hypothetical curves."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
import canonical_transfer as C
import stress_transfer as T
import repo_predict as R
from turn_transfer import numeric
from mechanism import player_splits

SEED=C.SEED+31000
FAMILIES=['conventional','burst','repeat_precision']
class RepeatPrecision:
    def __init__(self,events):self.events=events
    def fit(self,units):
        self.phys=numeric().fit(units[R.PHYS]);self.reference={};self.tau={};self.noise={}
        for column in [c for c in units if c.startswith('burst__') and not c.endswith('__width')]:
            _,drill,metric=column.split('__');present=units[column].notna();x=self.phys.transform(units.loc[present,R.PHYS]);y=units.loc[present,column].to_numpy()
            self.reference[column]=Ridge(alpha=10.).fit(x,y)
            ev=self.events[self.events.nfl_id.isin(units.nfl_id)&self.events.drill.eq(drill)]
            variance=ev.groupby('nfl_id')[metric].var().dropna();noise=float(variance.median()) if len(variance) else float(np.var(y))
            self.noise[column]=max(noise,1e-6)
            residual=y-self.reference[column].predict(x);n=units.loc[present,'available__'+drill].to_numpy()
            self.tau[column]=max(float(np.var(residual,ddof=1))-self.noise[column]*np.mean(1/np.maximum(n,1)),0.)
        return self
    def transform(self,units):
        result=units.copy();x=self.phys.transform(units[R.PHYS])
        for column,model in self.reference.items():
            _,drill,metric=column.split('__');reference=model.predict(x);n=units['available__'+drill].fillna(0).to_numpy();tau=self.tau[column];rho=tau/(tau+self.noise[column]/np.maximum(n,1)) if tau>0 else np.zeros(len(units))
            result['precision__'+drill+'__'+metric]=reference+rho*(units[column].fillna(pd.Series(reference,index=units.index)).to_numpy()-reference)
            result['reference__'+drill+'__'+metric]=reference
            result['increment__'+drill+'__'+metric]=rho*(units[column].fillna(pd.Series(reference,index=units.index)).to_numpy()-reference)
        return result

def panels(tr,te,target,source,events):
    a,b=T.targets(tr,te,target)
    a=a.merge(source,on='nfl_id',how='left',validate='one_to_one');b=b.merge(source,on='nfl_id',how='left',validate='one_to_one')
    precision=RepeatPrecision(events).fit(a);return precision.transform(a),precision.transform(b)
def predict(a,b,spec):
    family,alpha,k=spec
    prefix={'conventional':None,'burst':'burst__','repeat_precision':'precision__','physics_reference':'reference__','repeat_increment':'increment__'}[family]
    cols=[c for c in a if prefix and c.startswith(prefix) and not c.endswith('__width')]
    return C.predict(a,b,cols,alpha,k,clip=False)
def run(target='burst_travel1',threshold=1.,seed=SEED,forward=True,family_list=None,tag=''):
    families=family_list or FAMILIES
    out=Path(f'private_burst_model{tag}_{target}_{threshold}_{seed}');out.mkdir(exist_ok=True)
    rows=pd.read_pickle(f'private_burst/private_rows_{threshold}.pkl');source=pd.read_pickle('private_burst/private_source.pkl');events=pd.read_pickle('private_burst/private_attempts.pkl');dev=rows[rows.draft_year.lt(2025)].reset_index(drop=True);test=rows[rows.draft_year.eq(2025)].reset_index(drop=True)
    specs=[('conventional',a,0) for a in (10.,100.,1000.)]+[(f,a,k) for f in families[1:] for a in (10.,100.,1000.) for k in (2,4)];labels=families+['selected'];predictions=[];selection=[]
    def chosen(losses,f):return min([i for i,s in enumerate(specs) if f=='selected' or s[0] in ['conventional',f]],key=lambda i:losses[i])
    for fold,(i,j) in enumerate(player_splits(dev,4,seed)):
        tr=dev.iloc[i].reset_index(drop=True);te=dev.iloc[j].reset_index(drop=True);losses=np.zeros(len(specs))
        for a,b in player_splits(tr,3,seed+fold+1):
            u,v=panels(tr.iloc[a].reset_index(drop=True),tr.iloc[b].reset_index(drop=True),target,source,events)
            losses+=[float(np.mean((v.target-predict(u,v,s))**2))/3 for s in specs]
        u,v=panels(tr,te,target,source,events);q=v[['nfl_id','target']].copy()
        for f in labels:
            index=chosen(losses,f);q[f]=predict(u,v,specs[index]);selection.append({'fold':fold,'family':f,'spec':specs[index]})
        q.to_pickle(out/f'private_fold_{fold}.pkl');predictions.append(q);print('Burst outer',target,threshold,seed,fold,flush=True)
    result={'target':target,'threshold':threshold,'seed':seed,'bank':specs,'outer_selection':selection,'prior_2025_inspection':True,'target_scope':'Operational geometric burst outcome, residualized by training-only NFL context reference. Actual game situations define target only. Not a verified neurological reaction, LOS crossing, contact or causal ability.','predictors':'15conventional body/timed/NGS attributes, Combine position and shared source attempt counts; source1yard travel/speed/acceleration summaries. Repeat-precision moments fit inside every inner and outer split.','context_scope':'Every inner/outer split rebuilds crossfitted training target and train-only evaluated target; fixed120tree reference from prior study. No held-out labels construct training target.'}
    result['development']=T.comparison(pd.concat(predictions,ignore_index=True))
    if forward:
        tr=dev[dev.draft_year.eq(2023)].reset_index(drop=True);va=dev[dev.draft_year.eq(2024)].reset_index(drop=True)
        u,v=panels(tr,va,target,source,events);losses=[float(np.mean((v.target-predict(u,v,s))**2)) for s in specs]
        u,v=panels(dev,test,target,source,events);q=v[['nfl_id','target']].copy();choice=[]
        for f in labels:
            index=chosen(losses,f);q[f]=predict(u,v,specs[index]);choice.append({'family':f,'spec':specs[index]})
        q.to_pickle(out/'private_forward.pkl');result['exploratory_2025']=T.comparison(q);result['forward_selection']=choice
    result['adaptive_control']=bool(tag)
    (out/'results.json').write_text(json.dumps(result,indent=2));Path('receipts/burst',f'{tag.lstrip('_')+'_' if tag else ''}{target}_{threshold}_{seed}.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
    for seed in [SEED,SEED+200,SEED+400]:run(seed=seed,forward=seed==SEED)
    run(target='burst_onset')
    for threshold in [.5,2.]:run(threshold=threshold)
