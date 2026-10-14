"""Common scouting-input comparison of both sessions with an optional baseline.

Source population identical; only Combine traits, Combine position and source
availability enter predictors. Outcomes remain conditional on rookie participation.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.decomposition import PCA
import front_transfer as F,phase_population as P
from mechanism import player_splits
DONOR=Path(__file__).resolve().parent/'vendor/perfectpower_movement'
sys.path.insert(0,str(DONOR/'scripts'))
import run_movement_transfer as V
SEED=F.SEED+11000

def prepare():
    unit=pd.read_pickle('private_canonical_vendor/players.pkl');own=pd.read_pickle('private_phase_population/private_rows.pkl');cols=P.columns(own)['summaries'];profile=own.drop_duplicates('nfl_id')[['nfl_id','combine_position']+cols];unit=unit.merge(profile,on='nfl_id',how='left',validate='one_to_one');unit['available__FORTY_YARD_DASH']=unit[[c for c in cols if c.startswith('motion__')]].notna().any(axis=1).astype(float)
    if unit.nfl_id.duplicated().any():raise ValueError('duplicate canonical athlete')
    allcols=[c for c in unit if c.startswith('movement__')];families={'conventional':[],'onset_summaries':cols}
    for name,prefixes in V.FAMILIES.items():families['duration_'+name]=[c for c in allcols if any(c.split('__')[-1].startswith(p) for p in prefixes)]
    families['duration_combined']=sorted(set(sum([families['duration_'+k] for k in V.FAMILIES],[])))
    families['merged']=cols+families['duration_combined']
    Path('private_canonical').mkdir(exist_ok=True);unit.to_pickle('private_canonical/private_players.pkl');return unit,families

def predict(tr,te,cols,alpha,k,clip=True):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('athlete leakage')
    basecols=V.PHYS+[c for c in tr if c.startswith('available__')];imp=SimpleImputer(strategy='median',keep_empty_features=True);scale=StandardScaler();b=scale.fit_transform(imp.fit_transform(tr[basecols]));bt=scale.transform(imp.transform(te[basecols]));enc=OneHotEncoder(handle_unknown='ignore',sparse_output=False);b=np.c_[b,enc.fit_transform(tr[['combine_position']].fillna('MISSING'))];bt=np.c_[bt,enc.transform(te[['combine_position']].fillna('MISSING'))]
    if cols and k:
        mi=SimpleImputer(strategy='median',keep_empty_features=True);ms=StandardScaler();z=ms.fit_transform(mi.fit_transform(tr[cols]));zt=ms.transform(mi.transform(te[cols]));nuisance=Ridge(alpha=10).fit(b,z);z-=nuisance.predict(b).reshape(z.shape);zt-=nuisance.predict(bt).reshape(zt.shape);pca=PCA(n_components=min(k,len(tr)-1,len(cols)),svd_solver='full');z=pca.fit_transform(z);zt=pca.transform(zt);b=np.c_[b,z];bt=np.c_[bt,zt]
    prediction=Ridge(alpha=alpha).fit(b,tr.target).predict(bt)
    return np.clip(prediction,0,1) if clip else prediction

def candidate_bank(families):
    bank=[('conventional',a,0) for a in (1.,10.,100.)]
    bank += [(family,a,k) for family in families if family!='conventional' for a in (1.,10.,100.) for k in (2,4)]
    return bank

def evaluate(unit,families,out='private_canonical',seed=SEED,forward=True):
    out=Path(out);out.mkdir(exist_ok=True);bank=candidate_bank(families);dev=unit[unit.draft_year.isin([2023,2024])].reset_index(drop=True);test=unit[unit.draft_year.eq(2025)].reset_index(drop=True);labels=list(families)+['selected'];pp={k:np.zeros(len(dev)) for k in labels};selection=[]
    def fitting(tr,te,spec):name,a,k=spec;return predict(tr,te,families[name],a,k)
    def choose(loss,family):
        options=range(len(bank)) if family=='selected' else [i for i,c in enumerate(bank) if c[0]=='conventional' or c[0]==family]
        return min(options,key=lambda i:loss[i])
    for fold,(i,j) in enumerate(player_splits(dev,4,seed)):
        tr=dev.iloc[i].reset_index(drop=True);te=dev.iloc[j];inner=list(player_splits(tr,3,seed+1+fold));loss=[float(np.mean([np.mean((tr.iloc[b].target-fitting(tr.iloc[a],tr.iloc[b],spec))**2) for a,b in inner])) for spec in bank];cache={}
        for family in labels:
            ci=choose(loss,family)
            if ci not in cache:cache[ci]=fitting(tr,te,bank[ci])
            pp[family][j]=cache[ci];selection.append({'fold':fold,'family':family,'selected':bank[ci]})
        (out/f'private_fold_{fold}.json').write_text(json.dumps({'loss':loss,'selected':selection[-len(labels):]}));print('Canonical outer',seed,fold,flush=True)
    result={'predictors':'Fifteen Combine physical/timed/NGS traits, Combine position and five common source-availability flags. No NFL snap/game covariates. Rookie-eligible cohort target remains conditional on observed NFL participation.','seed':seed,'candidate_bank':bank,'source_dimensions':{k:len(v) for k,v in families.items()},'baseline_fallback':True,'selection_scope':'Four class-stratified whole-player outer folds; three inner folds select all feature and ridge/PCA options. Selected family uses the entire declared bank, including conventional. No family selected using2025.','prior_2025_inspection':True,'outer_selection':selection}
    splitrows=[('development',dev,pp)]
    if forward:
        tr=dev[dev.draft_year.eq(2023)];va=dev[dev.draft_year.eq(2024)];loss=[float(np.mean((va.target-fitting(tr,va,spec))**2)) for spec in bank];tp={};cache={};chosen=[]
        for family in labels:
            ci=choose(loss,family)
            if ci not in cache:cache[ci]=fitting(dev,test,bank[ci])
            tp[family]=cache[ci];chosen.append({'family':family,'selected':bank[ci]})
        result['forward_selection']=chosen;result['forward_validation_losses']=loss;splitrows.append(('exploratory_2025',test,tp))
    for split,rows,pred in splitrows:
        base=pred['conventional'];result[split]={'baseline_mse':float(np.mean((rows.target-base)**2)),'players':len(rows),'comparisons':{family:V.compare(rows.target.to_numpy(),base,pred[family]) for family in labels if family!='conventional'}}
        q=rows[['nfl_id','draft_year','target']].copy()
        for k,v in pred.items():q[k]=v
        q.to_pickle(out/f'private_{split}.pkl')
    (out/'results.json').write_text(json.dumps(result,indent=2));return result

def run(repeats=True):
    unit,families=prepare();r=evaluate(unit,families)
    if repeats:
        for seed in [SEED+200,SEED+400]:evaluate(unit,families,f'private_canonical_repeat_{seed}',seed,forward=False)
    return r
if __name__=='__main__':run()
