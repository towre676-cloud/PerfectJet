"""Leakage-controlled context-adjusted recovery scouting experiments.

Context targets are rebuilt within each outer/inner split. No held-out player's
labels construct training targets or select scouting configurations.
"""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.impute import SimpleImputer
import front_transfer as F,analysis as A,repo_predict as R,turn_transfer as T
import stress_features as S
from mechanism import player_splits
SEED=F.SEED+15000
FAMILIES=['conventional','raw_motion','matched_recovery','stress_curve','robust_recovery']
ALPHAS=[10.,100.,1000.]

def context_predict(tr,te,target,cache='private_stress/context'):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('context player leakage')
    path=Path(cache);path.mkdir(parents=True,exist_ok=True);key=hashlib.sha256(json.dumps(['fixed_forest120_depth6_leaf30',target,sorted(map(int,tr.nfl_id.unique())),sorted(map(int,te.nfl_id.unique()))]).encode()).hexdigest();file=path/(key+'.pkl');ids=te[['game_id','play_id','nfl_id']]
    if file.exists():q=pd.read_pickle(file);assert q[['game_id','play_id','nfl_id']].reset_index(drop=True).equals(ids.reset_index(drop=True));return q.prediction.to_numpy()
    num=T.numeric().fit(tr[F.NUM]);cat=OneHotEncoder(handle_unknown='ignore',sparse_output=False).fit(tr[F.CAT].fillna('MISSING').astype(str))
    def matrix(x):return np.c_[num.transform(x[F.NUM]),cat.transform(x[F.CAT].fillna('MISSING').astype(str))]
    model=RandomForestRegressor(n_estimators=120,max_depth=6,min_samples_leaf=30,max_features=.8,n_jobs=2,random_state=SEED).fit(matrix(tr),tr[target],sample_weight=A.weights(tr));prediction=model.predict(matrix(te));q=ids.copy();q['prediction']=prediction;q.to_pickle(file);return prediction

def unit_rows(d):return d.drop_duplicates('nfl_id')[['nfl_id','draft_year','combine_position']+R.PHYS].reset_index(drop=True)

def targets(tr,te,target):
    prediction=np.zeros(len(tr))
    for i,j in player_splits(tr,3,SEED+1):prediction[j]=context_predict(tr.iloc[i],tr.iloc[j],target)
    future=context_predict(tr,te,target);a=pd.DataFrame({'nfl_id':tr.nfl_id,'target':tr[target]-prediction}).groupby('nfl_id').target.mean();b=pd.DataFrame({'nfl_id':te.nfl_id,'target':te[target]-future}).groupby('nfl_id').target.mean();u=unit_rows(tr);v=unit_rows(te);u['target']=a.reindex(u.nfl_id).to_numpy();v['target']=b.reindex(v.nfl_id).to_numpy();return u,v

def panels(tr,te,target,turns,capacity=None,share_capacity_availability=True):
    u,v=targets(tr,te,target)
    if capacity is not None:
        u=u.merge(capacity,on='nfl_id',how='left',validate='one_to_one');v=v.merge(capacity,on='nfl_id',how='left',validate='one_to_one')
        if share_capacity_availability:
            u['capacity_available']=u['sprint__ceiling'].notna().astype(float)
            v['capacity_available']=v['sprint__ceiling'].notna().astype(float)
    encoder=S.StressEncoder(turns).fit(u);x=encoder.transform(u);y=encoder.transform(v);u=u.merge(x,on='nfl_id',validate='one_to_one');v=v.merge(y,on='nfl_id',validate='one_to_one');return u,v

def feature_columns(d,family):
    metrics={'raw_motion':['eta','retention','late_gain','entry','angle'],'matched_recovery':['eta_r','retention_r','late_r'],'stress_curve':['eta_r','slope','late_r','retention_r'],'robust_recovery':['lower','upper','width','eta_r','attempt_dispersion']}
    if family=='conventional':return []
    caps=[c for c in d if c.startswith('sprint__')]
    return caps if family=='capacity_only' else caps+[c for c in d if c.startswith('stress__') and c.split('__')[-1] in metrics[family]]

def predict(tr,te,family,alpha):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('scouting player leakage')
    flags=[c for c in tr if c.startswith('stress__') and c.endswith('__count')]
    if 'capacity_available' in tr:flags+=['capacity_available']
    basecols=R.PHYS+flags
    imp=SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True);scale=StandardScaler();x=scale.fit_transform(imp.fit_transform(tr[basecols]));y=scale.transform(imp.transform(te[basecols]));enc=OneHotEncoder(handle_unknown='ignore',sparse_output=False);x=np.c_[x,enc.fit_transform(tr[['combine_position']].fillna('MISSING'))];y=np.c_[y,enc.transform(te[['combine_position']].fillna('MISSING'))]
    cols=feature_columns(tr,family)
    if cols:
        mi=SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True);z=mi.fit_transform(tr[cols]);zt=mi.transform(te[cols]);lo,hi=np.quantile(z,[.01,.99],axis=0);z=np.clip(z,lo,hi);zt=np.clip(zt,lo,hi);ms=StandardScaler().fit(z);z=ms.transform(z);zt=ms.transform(zt);mass=scale.transform(imp.transform(tr[basecols]))[:,R.PHYS.index('combine_weight')];mt=scale.transform(imp.transform(te[basecols]))[:,R.PHYS.index('combine_weight')]
        # One predeclared interaction: mean matched recovery × standardized mass.
        if family in ['matched_recovery','stress_curve']:
            indexes=[i for i,c in enumerate(cols) if c.endswith('__eta_r')];zm=z[:,indexes].mean(1);zmt=zt[:,indexes].mean(1);z=np.c_[z,zm*mass];zt=np.c_[zt,zmt*mt];final=StandardScaler().fit(z);z=final.transform(z);zt=final.transform(zt)
        x=np.c_[x,z];y=np.c_[y,zt]
    return Ridge(alpha=alpha).fit(x,tr.target).predict(y)

def comparison(q):
    families=[c for c in q if c not in ['nfl_id','target']];base=(q.target-q.conventional)**2;rng=np.random.default_rng(SEED+30);r={'players':len(q),'mse':{f:float(np.mean((q.target-q[f])**2)) for f in families},'comparisons':{}}
    for f in families:
        if f=='conventional':continue
        delta=base-(q.target-q[f])**2;r['comparisons'][f]={'absolute_gain':float(delta.mean()),'relative_gain':float(delta.mean()/base.mean()),'conditional_ci95':np.quantile(rng.choice(delta,(5000,len(delta)),replace=True).mean(1),[.025,.975]).tolist()}
    if 'capacity_only' in q:
        cap=(q.target-q.capacity_only)**2;r['versus_capacity']={}
        for f in families:
            if f in ['conventional','capacity_only']:continue
            delta=cap-(q.target-q[f])**2;r['versus_capacity'][f]={'absolute_gain':float(delta.mean()),'relative_gain':float(delta.mean()/cap.mean()),'conditional_ci95':np.quantile(rng.choice(delta,(5000,len(delta)),replace=True).mean(1),[.025,.975]).tolist()}
    r['scope']='Paired fixed-prediction player bootstrap, omitting refitting and adaptive-search uncertainty; outcomes constructed by held-out context reference.';return r

def run(target='pressure_event',seed=SEED,forward=True,out=None,source_folder='private_stress',capacity=None,family_list=None,share_capacity_availability=True):
    names=family_list or FAMILIES
    out=Path(out or source_folder+'/'+target);out.mkdir(parents=True,exist_ok=True);d=pd.read_pickle(Path(source_folder)/'private_rows.pkl');turns=pd.read_pickle(Path(source_folder)/'private_turns.pkl');dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);test=d[d.draft_year.eq(2025)].reset_index(drop=True);reports=[];predictions=[];specs=[('conventional',a) for a in ALPHAS]+[(f,a) for f in names[1:] for a in ALPHAS]
    for fold,(i,j) in enumerate(player_splits(dev,4,seed)):
        tr=dev.iloc[i].reset_index(drop=True);te=dev.iloc[j].reset_index(drop=True);file=out/f'private_outer_{fold}.pkl';receipt=out/f'private_outer_{fold}.json'
        if file.exists():predictions.append(pd.read_pickle(file));reports.extend(json.loads(receipt.read_text()));continue
        losses=np.zeros(len(specs))
        for a,b in player_splits(tr,3,seed+1+fold):
            u,v=panels(tr.iloc[a].reset_index(drop=True),tr.iloc[b].reset_index(drop=True),target,turns,capacity,share_capacity_availability)
            for ix,(f,alpha) in enumerate(specs):losses[ix]+=np.mean((v.target-predict(u,v,f,alpha))**2)/3
        u,v=panels(tr,te,target,turns,capacity,share_capacity_availability);q=v[['nfl_id','target']].copy();chosen=[]
        for f in names+['selected']:
            options=range(len(specs)) if f=='selected' else [k for k,s in enumerate(specs) if s[0] in ['conventional',f]];best=min(options,key=lambda k:losses[k]);family,alpha=specs[best];q[f]=predict(u,v,family,alpha);chosen.append({'fold':fold,'family':f,'specification':specs[best],'inner_mse':losses.tolist()})
        q.to_pickle(file);receipt.write_text(json.dumps(chosen));predictions.append(q);reports.extend(chosen);print('Stress outer',target,seed,fold,flush=True)
    r={'target':target,'seed':seed,'outer_selection':reports,'source_folder':source_folder,'capacity_included':capacity is not None,'source_templates':'StressEncoder fitted inside every inner/outer training set; conventional traits and drill enter source-demand adjustment. All families share eligible-turn counts and Combine position.','context_reference':'Fixed120-tree forest, no Combine attributes. Training targets from three player-cross-fits within each split; evaluated-player reference fitted only on training players.','2025_prior_inspection':True,'candidate_specifications':len(specs),'design':'Baseline-only fallback; all choices inside training data. Final nonlinear coordinate scaling and1st/99th support clipping predeclared.','development':comparison(pd.concat(predictions,ignore_index=True))}
    if forward:
        tr=dev[dev.draft_year.eq(2023)].reset_index(drop=True);va=dev[dev.draft_year.eq(2024)].reset_index(drop=True);u,v=panels(tr,va,target,turns,capacity,share_capacity_availability);losses=[float(np.mean((v.target-predict(u,v,f,a))**2)) for f,a in specs];u,v=panels(dev,test,target,turns,capacity,share_capacity_availability);q=v[['nfl_id','target']].copy();selection=[]
        for f in names+['selected']:
            options=range(len(specs)) if f=='selected' else [k for k,s in enumerate(specs) if s[0] in ['conventional',f]];best=min(options,key=lambda k:losses[k]);family,alpha=specs[best];q[f]=predict(u,v,family,alpha);selection.append({'family':f,'specification':specs[best]})
        q.to_pickle(out/'private_forward.pkl');r['forward_selection']=selection;r['forward_validation_mse']=losses;r['exploratory_2025']=comparison(q)
    r['shared_capacity_availability']=share_capacity_availability if capacity is not None else None
    (out/'results.json').write_text(json.dumps(r,indent=2));return r
if __name__=='__main__':
    for target in ['pressure_event','player_get_off']:run(target)
