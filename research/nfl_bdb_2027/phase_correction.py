"""Adaptive baseline-preserving source correction, fixed shrinkage budget.

Response is whole-athlete residual from player-cross-fitted conventional models.
Alpha100 and latent rank4 locked after concat inspection, before correction results.
"""
from pathlib import Path
import json
import numpy as np,pandas as pd
from sklearn.linear_model import Ridge
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import phase_population as P,front_transfer as F,repo_predict as R
from mechanism import player_splits

ALPHA=100

def conventional_bag(tr,te,config,seed,count=16):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('original player overlap')
    rng=np.random.default_rng(seed);units=tr[['nfl_id','draft_year']].drop_duplicates();groups={k:g for k,g in tr.groupby('nfl_id')};prediction=np.zeros(len(te))
    for _ in range(count):
        blocks=[];replica=0
        for _,g in units.groupby('draft_year'):
            for player in rng.choice(g.nfl_id.to_numpy(),len(g),replace=True):
                q=groups[player].copy();q['nfl_id']=-1-replica;replica+=1;blocks.append(q)
        prediction+=F.fit_predict(pd.concat(blocks,ignore_index=True),te,[],F.CONFIGS[config],'pressure_event')/count
    return prediction

def correction(tr,te,residual,cols,scaled=False):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('player overlap in source correction')
    scale=F.T.numeric().fit(tr[cols]);phys=F.T.numeric().fit(tr[R.PHYS]);nuisance=Ridge(alpha=10).fit(phys.transform(tr[R.PHYS]),scale.transform(tr[cols]));z=scale.transform(tr[cols])-nuisance.predict(phys.transform(tr[R.PHYS]));pca=PCA(n_components=min(4,len(tr)-1,z.shape[1]),svd_solver='full').fit(z)
    def features(d):
        z=pca.transform(scale.transform(d[cols])-nuisance.predict(phys.transform(d[R.PHYS])));mass=phys.transform(d[R.PHYS])[:,R.PHYS.index('combine_weight')];return np.c_[z,z*z,z*mass[:,None]]
    # Zero intercept keeps the correction anchored to the unchanged baseline.
    x,y=features(tr),features(te)
    if scaled:
        # Fold-local support restriction and equal penalty scales for nonlinear terms.
        lo,hi=np.quantile(x,[.01,.99],axis=0);x=np.clip(x,lo,hi);y=np.clip(y,lo,hi)
        final_scale=StandardScaler().fit(x);x=final_scale.transform(x);y=final_scale.transform(y)
    return Ridge(alpha=ALPHA,fit_intercept=False).fit(x,residual).predict(y)

def run(out='private_phase_correction',scaled=False):
    out=Path(out);out.mkdir(exist_ok=True);d=pd.read_pickle('private_phase_population/private_rows.pkl');cols=P.columns(d);old=json.loads(Path('private_front_macro/pressure_event/results.json').read_text());dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);test=d[d.draft_year.eq(2025)].reset_index(drop=True);stages=[(str(fold),dev.iloc[i].reset_index(drop=True),dev.iloc[j].reset_index(drop=True),next(x['config'] for x in old['folds'] if x['family']=='conventional' and x['fold']==fold)) for fold,(i,j) in enumerate(player_splits(dev,4,F.SEED))];stages.append(('forward',dev,test,next(x['config'] for x in old['selection'] if x['family']=='conventional')))
    for label,tr,te,config in stages:
        residual_prediction=np.zeros(len(tr))
        for inner,(i,j) in enumerate(player_splits(tr,3,F.SEED+9700)):
            checkpoint=out/f'private_inner_{label}_{inner}.pkl'
            original=Path('private_phase_correction')/checkpoint.name
            if scaled and not checkpoint.exists() and original.exists():checkpoint.write_bytes(original.read_bytes())
            if checkpoint.exists():q=pd.read_pickle(checkpoint);assert q.nfl_id.tolist()==tr.iloc[j].nfl_id.tolist();prediction=q.prediction.to_numpy()
            else:
                prediction=conventional_bag(tr.iloc[i],tr.iloc[j],config,F.SEED+9800+inner)
                q=tr.iloc[j][['nfl_id']].copy();q['prediction']=prediction;q.to_pickle(checkpoint)
            residual_prediction[j]=prediction;print('Cross-fitted correction baseline',label,inner,flush=True)
        residual=pd.DataFrame({'nfl_id':tr.nfl_id,'error':tr.pressure_event-residual_prediction}).groupby('nfl_id').error.mean();units=tr.drop_duplicates('nfl_id').copy();validation=te.drop_duplicates('nfl_id').copy();base=pd.read_pickle(Path('private_phase_population')/f'private_predictions_{label}.pkl');assert base.nfl_id.tolist()==te.nfl_id.tolist();q=te[['nfl_id','pressure_event']].copy();q['conventional']=base.conventional.to_numpy()
        for family in P.FAMILIES[1:]:
            change=correction(units,validation,residual.reindex(units.nfl_id).to_numpy(),cols[family],scaled=scaled);lookup=pd.Series(change,index=validation.nfl_id);q[family]=np.clip(q.conventional.to_numpy()+lookup.reindex(te.nfl_id).to_numpy(),0,1)
        q.to_pickle(out/f'private_predictions_{label}.pkl')
    result={'adaptive_after_phase_concat_and_prior_2025_inspection':True,'method':'Fixed unchanged outer conventional16-athlete-ensemble plus player-level Ridge100 source correction; rank4 physical-conditioned PCA, squared components and mass interactions; intercept zero. Training residuals from three player-separated conventional16-athlete-ensemble fits. No hyperparameter selection or choosing among reported families.','scaled_and_support_limited':scaled,'scaling_rule':'Training 1st/99th percentile feature clipping, then train-fitted standardization of nonlinear correction coordinates; adaptive after unscaled correction inspection.' if scaled else 'Unscaled nonlinear coordinates retained as failed first correction.','alpha':ALPHA,'nested':P.evaluate(pd.concat([pd.read_pickle(out/f'private_predictions_{k}.pkl') for k in range(4)])),'exploratory_2025':P.evaluate(pd.read_pickle(out/'private_predictions_forward.pkl'))}
    (out/'results.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
