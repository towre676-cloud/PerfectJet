"""Prospect-balanced compression and development-only model selection.

2025 was already inspected before this push; its results are exploratory.
"""
from pathlib import Path
import json,time
import numpy as np,pandas as pd
from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor,ExtraTreesRegressor
from sklearn.model_selection import StratifiedGroupKFold
import analysis as A

PHYS=A.BASE+['hand_size','arm_length','wing_span','bench_reps','ngs_athleticism_score','ngs_college_production_score','ngs_final_score']
NUM=A.CONTEXT+['quarter']
CAT=A.CATS+['team_coverage_type','receiver_alignment','team_abbr','defense_team']
CONFIGS=[{'reg':'ridge','alpha':1,'k':4},{'reg':'ridge','alpha':10,'k':4},{'reg':'ridge','alpha':100,'k':8},{'reg':'forest','alpha':0,'k':4},{'reg':'extra','alpha':0,'k':8}]

class ProspectEncoder(BaseEstimator,TransformerMixin):
    def __init__(self,motion=(),k=4):self.motion=motion;self.k=k
    def fit(self,x,y=None):
        players=x.drop_duplicates('nfl_id');self.fit_player_ids_=set(players.nfl_id)
        self.phys=Pipeline([('impute',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)),('scale',StandardScaler())]);self.phys.fit(players[PHYS])
        self.num=Pipeline([('impute',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)),('scale',StandardScaler())]);self.num.fit(x[NUM])
        self.cat=OneHotEncoder(handle_unknown='ignore',sparse_output=False);self.cat.fit(x[CAT].astype(str).where(x[CAT].notna(),'MISSING'))
        if self.motion:
            m=players[list(self.motion)].to_numpy(float);self.lo=np.nanquantile(m,.01,axis=0);self.hi=np.nanquantile(m,.99,axis=0)
            self.lo=np.nan_to_num(self.lo);self.hi=np.nan_to_num(self.hi)
            self.mi=SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True);m=self.mi.fit_transform(np.clip(m,self.lo,self.hi));self.ms=StandardScaler();m=self.ms.fit_transform(m)
            self.pca=PCA(n_components=min(self.k,len(players)-1,m.shape[1]),svd_solver='full');self.pca.fit(m)
        return self
    def transform(self,x):
        blocks=[self.phys.transform(x[PHYS]),self.num.transform(x[NUM]),self.cat.transform(x[CAT].astype(str).where(x[CAT].notna(),'MISSING'))]
        if self.motion:
            m=np.clip(x[list(self.motion)].to_numpy(float),self.lo,self.hi);blocks.append(self.pca.transform(self.ms.transform(self.mi.transform(m))))
        return np.column_stack(blocks)

def columns(panel,family):
    cols=[c for c in panel if c.startswith('motion__')]
    if family=='baseline':return ()
    if family=='summary':return tuple(c for c in cols if c.split('__')[-1] in A.MOTION)
    if family=='signature':return tuple(c for c in cols if c.split('__')[-1].startswith('sig_'))
    if family=='dynamics':return tuple(c for c in cols if c.split('__')[-1].startswith(('memory_','hankel_','profile_')))
    if family=='all':return tuple(cols)
    raise ValueError('family')

def make(motion,config):
    enc=ProspectEncoder(motion,config['k'])
    if config['reg']=='ridge':reg=Ridge(alpha=config['alpha'])
    elif config['reg']=='forest':reg=RandomForestRegressor(n_estimators=150,max_depth=6,min_samples_leaf=20,max_features=.8,n_jobs=2,random_state=A.SEED)
    else:reg=ExtraTreesRegressor(n_estimators=150,max_depth=8,min_samples_leaf=20,max_features=.8,n_jobs=2,random_state=A.SEED)
    return Pipeline([('enc',enc),('reg',reg)])

def fit_predict(train,test,motion,config):
    if set(train.nfl_id)&set(test.nfl_id):raise ValueError('player overlap')
    m=make(motion,config);m.fit(train,train.separation_at_pass_forward,reg__sample_weight=A.weights(train));return m,m.predict(test)

def prepare(root,out,data_root=None,analysis_out=None):
    root,out=Path(root),Path(out);data_root=Path(data_root) if data_root else root/'data';analysis_out=Path(analysis_out) if analysis_out else root/'private_results';d=pd.read_pickle(analysis_out/'private_analysis_rows.pkl') if (analysis_out/'private_analysis_rows.pkl').exists() else pd.read_csv(analysis_out/'private_analysis_rows.csv');panel=pd.read_csv(out/'private_motion_panel.csv');d=d.drop(columns=A.MOTION).merge(panel,on='nfl_id',validate='many_to_one')
    g=pd.read_csv(data_root/'games.csv').set_index('game_id');home=d.game_id.map(g.home_team_abbr);away=d.game_id.map(g.visitor_team_abbr);d['defense_team']=np.where(home==d.team_abbr,away,home)
    if d.nfl_id.nunique()!=64 or len(d)!=7348:raise ValueError('frozen population changed')
    return d,panel

def bootstrap(test,p0,p1):
    x=pd.DataFrame({'id':test.nfl_id,'delta':(test.separation_at_pass_forward-p0)**2-(test.separation_at_pass_forward-p1)**2}).groupby('id').delta.mean().to_numpy();rng=np.random.default_rng(A.SEED);boots=rng.choice(x,(5000,len(x)),replace=True).mean(axis=1)
    return {'delta_mse':float(x.mean()),'ci95':np.quantile(boots,[.025,.975]).tolist(),'players':len(x)}

def cohort_trial(root,out,data_root=None,analysis_out=None):
    root,out=Path(root),Path(out);d,panel=prepare(root,out,data_root,analysis_out);train=d[d.draft_year.eq(2023)];val=d[d.draft_year.eq(2024)];dev=d[d.draft_year.isin([2023,2024])];test=d[d.draft_year.eq(2025)]
    bank=[];selected={};preds={};start=time.perf_counter()
    for family in ['baseline','summary','signature','dynamics','all']:
        cc=columns(panel,family);candidates=[]
        for i,config in enumerate(CONFIGS):
            m,p=fit_predict(train,val,cc,config);v=A.score(val,p);candidates.append((v,i));bank.append({'family':family,'config':i,'validation_mse':v});print('Validation',family,i,round(v,6),flush=True)
        v,i=min(candidates);m,p=fit_predict(dev,test,cc,CONFIGS[i]);preds[family]=p;selected[family]={'config':CONFIGS[i],'config_index':i,'validation_mse':v,'test_mse':A.score(test,p),'test_rmse_yards':A.score(test,p)**.5,'motion_input_columns':len(cc),'motion_latent_dimension':m.named_steps['enc'].pca.n_components_ if cc else 0}
    for family in ['summary','signature','dynamics','all']:selected[family]['paired_vs_strong_conventional']=bootstrap(test,preds['baseline'],preds[family])
    original=pd.read_csv((Path(analysis_out) if analysis_out else root/'private_results')/'private_test_predictions.csv');q=test[['nfl_id','game_id','play_id']].merge(original,on=['nfl_id','game_id','play_id'],validate='one_to_one')
    old=q.forest_conventional.to_numpy();selected['all']['paired_vs_original_forest']=bootstrap(test,old,preds['all'])
    result={'status':'exploratory_actual_data','test_previously_inspected':True,'selection':'2023 train; 2024 tune; refit 2023+2024; 2025 exploratory transport','primary_new_family':'all','selected':selected,'validation_bank':bank,'same_candidates_per_family':len(CONFIGS),'test_players':test.nfl_id.nunique(),'test_routes':len(test),'elapsed_seconds':time.perf_counter()-start,'interpretation':'Ablations exploratory; superiority requires stronger development-only corroboration and fresh future validation.'}
    (out/'cohort_trial.json').write_text(json.dumps(result,indent=2));p=test[['nfl_id','game_id','play_id']].copy()
    for k,v in preds.items():p[k]=v
    p.to_csv(out/'private_cohort_predictions.csv',index=False);print(json.dumps(result,indent=2),flush=True);return result

def nested_development(root,out,data_root=None,analysis_out=None):
    root,out=Path(root),Path(out);d,panel=prepare(root,out,data_root,analysis_out);dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);outer=StratifiedGroupKFold(n_splits=4,shuffle=True,random_state=A.SEED);preds={f:np.zeros(len(dev)) for f in ['baseline','all']};receipts=[]
    for fold,(ii,jj) in enumerate(outer.split(dev,dev.draft_year,dev.nfl_id)):
        tr,te=dev.iloc[ii],dev.iloc[jj];inner=StratifiedGroupKFold(n_splits=3,shuffle=True,random_state=A.SEED+fold+1)
        for family in ['baseline','all']:
            cc=columns(panel,family);rank=[]
            for ci,config in enumerate(CONFIGS):
                losses=[]
                for a,b in inner.split(tr,tr.draft_year,tr.nfl_id):
                    ti,vi=tr.iloc[a],tr.iloc[b];_,p=fit_predict(ti,vi,cc,config);losses.append(A.score(vi,p))
                rank.append((float(np.mean(losses)),ci))
            _,ci=min(rank);_,p=fit_predict(tr,te,cc,CONFIGS[ci]);preds[family][jj]=p;receipts.append({'outer_fold':fold,'family':family,'chosen_config':ci,'inner_scores':[v for v,i in rank],'outer_mse':A.score(te,p),'outer_players':te.nfl_id.nunique()});print('Nested',fold,family,'MSE',round(A.score(te,p),6),flush=True)
    result={'status':'development_only_nested_player_validation','years':[2023,2024],'test_2025_outcomes_used':False,'drill_dictionary_scope':'fixed using full supplied Combine drill availability, including 2025; no outcome-based selection','players':dev.nfl_id.nunique(),'routes':len(dev),'baseline_mse':A.score(dev,preds['baseline']),'motion_mse':A.score(dev,preds['all']),'paired_improvement':bootstrap(dev,preds['baseline'],preds['all']),'fold_receipts':receipts,'scope':'unseen players in pooled earlier seasons; complements but does not replace a future-season holdout'}
    (out/'nested_development.json').write_text(json.dumps(result,indent=2));p=dev[['nfl_id','game_id','play_id']].copy()
    for k,v in preds.items():p[k]=v
    p.to_csv(out/'private_nested_predictions.csv',index=False);print(json.dumps(result,indent=2),flush=True);return result

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--nested',action='store_true');args=ap.parse_args();root=Path(__file__).parent;out=root/'private_repo_results'
    if args.nested:nested_development(root,out)
    else:cohort_trial(root,out)
