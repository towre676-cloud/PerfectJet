"""Exploratory route-conditioned observation of Combine movement state."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedGroupKFold
import analysis as A,repo_predict as R
MAP={'IN':['DAGGER_ROUTE_LEFT'],'OUT':['SPEED_OUT_ROUTE_LEFT'],'SLANT':['SLANT_ROUTE_LEFT'],'HITCH':['CURL_ROUTE_RIGHT','COMEBACK_ROUTE_RIGHT']}

class RouteEncoder(R.ProspectEncoder):
    def __init__(self,motion=(),k=4):super().__init__((),k);self.motion=motion
    def vector(self,x,route):
        names=sorted({c.split('__')[-1] for c in self.motion});blocks=[]
        for drill in MAP[route]:
            blocks.append(x[[f'motion__{drill}__{name}' for name in names]].to_numpy(float))
        total=np.zeros_like(blocks[0]);count=np.zeros_like(total)
        for block in blocks:total+=np.nan_to_num(block);count+=np.isfinite(block)
        return np.divide(total,count,out=np.full_like(total,np.nan),where=count>0)
    def fit(self,x,y=None):
        selected=self.motion;self.motion=();super().fit(x,y);self.motion=selected
        players=x.drop_duplicates('nfl_id');m=np.concatenate([self.vector(players,r) for r in MAP],axis=0)
        self.lo=np.nan_to_num(np.nanquantile(m,.01,axis=0));self.hi=np.nan_to_num(np.nanquantile(m,.99,axis=0));self.mi=SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True);m=self.mi.fit_transform(np.clip(m,self.lo,self.hi));self.ms=StandardScaler();m=self.ms.fit_transform(m);self.pca=PCA(n_components=min(self.k,m.shape[0]-1,m.shape[1]),svd_solver='full');self.pca.fit(m);return self
    def transform(self,x):
        selected=self.motion;self.motion=();base=super().transform(x);self.motion=selected;m=np.empty((len(x),len({c.split('__')[-1] for c in selected})))
        for route in MAP:
            ix=np.flatnonzero(x.route_ran.eq(route).to_numpy());m[ix]=self.vector(x.iloc[ix],route)
        return np.column_stack([base,self.pca.transform(self.ms.transform(self.mi.transform(np.clip(m,self.lo,self.hi))))])

def prepare(root,out,data_root=None):
    root,out=Path(root),Path(out);data_root=Path(data_root) if data_root else root/'data';p=pd.read_csv(data_root/'players.csv');c=pd.read_csv(data_root/'combine_results.csv');g=pd.read_csv(data_root/'games.csv');d=pd.read_csv(data_root/'player_play.csv');panel=pd.read_csv(out/'private_motion_panel.csv')
    d=d.merge(p[['nfl_id','draft_year','nfl_position']],on='nfl_id',validate='many_to_one').merge(g[['game_id','season','season_type','home_team_abbr','visitor_team_abbr']],on='game_id',validate='many_to_one')
    d=d[d.nfl_position.eq('WR')&d.season.eq(d.draft_year)&d.season_type.eq('REG')&d.route_ran.isin(MAP)&d.play_nullified_by_penalty.eq('N')&np.isfinite(d.separation_at_pass_forward)&d.separation_at_pass_forward.ge(0)]
    counts=d.groupby('nfl_id').size();d=d[d.nfl_id.isin(counts[counts>=20].index)].merge(c,on=['nfl_id','draft_year'],validate='many_to_one').merge(panel,on='nfl_id',validate='many_to_one')
    d['defense_team']=np.where(d.team_abbr==d.home_team_abbr,d.visitor_team_abbr,d.home_team_abbr)
    return d,panel

def fit_predict(tr,te,panel,config,matched):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('player overlap')
    m=R.make(R.columns(panel,'all') if matched else (),config)
    if matched:m.steps[0]=('enc',RouteEncoder(R.columns(panel,'all'),config['k']))
    m.fit(tr,tr.separation_at_pass_forward,reg__sample_weight=A.weights(tr));return m.predict(te)

def run(root,out,data_root=None):
    root,out=Path(root),Path(out);d,panel=prepare(root,out,data_root);tr=d[d.draft_year.eq(2023)];va=d[d.draft_year.eq(2024)];dv=d[d.draft_year.isin([2023,2024])];te=d[d.draft_year.eq(2025)];chosen={};pred={};bank=[]
    for matched in [False,True]:
        name='route_matched' if matched else 'conventional';candidates=[]
        for ci,config in enumerate(R.CONFIGS):
            p=fit_predict(tr,va,panel,config,matched);loss=A.score(va,p);candidates.append((loss,ci));bank.append({'family':name,'config':ci,'validation_mse':loss})
        loss,ci=min(candidates);p=fit_predict(dv,te,panel,R.CONFIGS[ci],matched);pred[name]=p;chosen[name]={'config':R.CONFIGS[ci],'validation_mse':loss,'exploratory_2025_mse':A.score(te,p),'exploratory_2025_rmse':A.score(te,p)**.5};print(name,chosen[name],flush=True)
    result={'scope':'exploratory route-matched population; original 2025 inspection disclosed','mapping':MAP,'players_by_class':d.groupby('draft_year').nfl_id.nunique().to_dict(),'routes_by_class':d.groupby('draft_year').size().to_dict(),'selected':chosen,'paired_improvement':R.bootstrap(te,pred['conventional'],pred['route_matched']),'validation_bank':bank}
    # Earlier-data nested assessment with candidate selection repeated inside each outer fold.
    dv=dv.reset_index(drop=True);oof={k:np.zeros(len(dv)) for k in chosen};outer=StratifiedGroupKFold(n_splits=4,shuffle=True,random_state=A.SEED);folds=[]
    for fold,(a,b) in enumerate(outer.split(dv,dv.draft_year,dv.nfl_id)):
        a,b=dv.iloc[a],dv.iloc[b];inner=StratifiedGroupKFold(n_splits=3,shuffle=True,random_state=A.SEED+fold+1)
        for matched in [False,True]:
            name='route_matched' if matched else 'conventional';rank=[]
            for ci,config in enumerate(R.CONFIGS):
                losses=[]
                for i,j in inner.split(a,a.draft_year,a.nfl_id):losses.append(A.score(a.iloc[j],fit_predict(a.iloc[i],a.iloc[j],panel,config,matched)))
                rank.append((float(np.mean(losses)),ci))
            _,ci=min(rank);p=fit_predict(a,b,panel,R.CONFIGS[ci],matched);oof[name][b.index]=p;folds.append({'fold':fold,'family':name,'chosen_config':ci,'outer_mse':A.score(b,p)});print('matched nested',fold,name,round(A.score(b,p),6),flush=True)
    result['nested_earlier_data']={'players':dv.nfl_id.nunique(),'routes':len(dv),'conventional_mse':A.score(dv,oof['conventional']),'matched_mse':A.score(dv,oof['route_matched']),'paired_improvement':R.bootstrap(dv,oof['conventional'],oof['route_matched']),'folds':folds,'test_2025_outcomes_used':False,'drill_dictionary_scope':'fixed from all supplied Combine availability; 2025 outcome labels excluded from nested fitting'}
    (out/'route_matched_trial.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True);return result

if __name__=='__main__':
    import repo_motion
    root=Path(__file__).parent;out=root/'private_repo_matched';out.mkdir(exist_ok=True)
    if not (out/'private_motion_panel.csv').exists():repo_motion.build_features(root/'data',out,aliases=True)
    run(root,out)
