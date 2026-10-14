"""Exploratory, player-cross-fitted context residuals and three-second mechanics.

No 2025 labels select features, regularization, or nuisance specifications.
Earlier experiments already inspected 2025, so transport remains exploratory.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
import analysis as A
import repo_predict as R

MAP={'IN':['DAGGER_ROUTE_LEFT'],'OUT':['SPEED_OUT_ROUTE_LEFT'],
     'SLANT':['SLANT_ROUTE_LEFT'],'HITCH':['CURL_ROUTE_RIGHT','COMEBACK_ROUTE_RIGHT']}
FEATURES=['entry','retention','recovery','braking','propulsion','turn','bend',
          'area','speed_mode_1','speed_mode_2','speed_mode_3','speed_mode_4']
ALPHAS=[10.,100.,1000.]

def trajectory(g):
    _,diag=A.movement(g)
    g=g.sort_values('time');c=diag['cut_index']
    if c<15 or c+15>=len(g):raise ValueError('insufficient three-second turn window')
    p=savgol_filter(g[['x','y']].to_numpy(float),7,3,axis=0)
    v=np.gradient(p,.1,axis=0);s=np.linalg.norm(v,axis=1)
    th=np.unwrap(np.arctan2(v[:,1],v[:,0]));sl=slice(c-15,c+16)
    tangent=v[c-5]/max(s[c-5],1e-9);normal=np.array([-tangent[1],tangent[0]])
    q=(p[sl]-p[c-15])@np.stack([tangent,normal],axis=1)
    turn=th[c+5]-th[c-5];q[:,1]*=1 if turn>=0 else -1
    speed=s[sl];acc=np.gradient(speed,.1);entry=float(speed[5:11].mean())
    if entry<1:raise ValueError('insufficient approach speed')
    arc=np.linalg.norm(np.diff(q,axis=0),axis=1).sum()
    mode=np.polynomial.legendre.legfit(np.linspace(-1,1,31),speed/entry,4)
    area=.5*np.sum(q[:-1,0]*q[1:,1]-q[:-1,1]*q[1:,0])/max(arc**2,1e-9)
    vals=[entry,float(speed[10:21].min()/entry),float(speed[21:27].mean()/entry),
          float(np.trapezoid(np.maximum(-acc[5:21],0),dx=.1)/entry),
          float(np.trapezoid(np.maximum(acc[15:27],0),dx=.1)/entry),abs(float(turn)),
          float(np.trapezoid(np.gradient(th,.1)[sl]**2/np.maximum(speed,1),dx=.1)),
          area,*mode[1:]]
    return dict(zip(FEATURES,map(float,vals))),{'q':q,'speed':speed,'t':np.arange(-15,16)*.1}

def prepare(data,out):
    data,out=Path(data),Path(out);out.mkdir(parents=True,exist_ok=True)
    players=pd.read_csv(data/'players.csv');tr=pd.read_csv(data/'combine_tracking.csv')
    tr=tr[tr.nfl_id.isin(players.loc[players.nfl_position.eq('WR'),'nfl_id'])&tr.entity_type.eq('PLAYER')&tr.drill_type.eq('SKILL_DRILLS_WR')].copy()
    tr['drill_name']=tr.drill_name.replace({'SPEED_OUT_LEFT':'SPEED_OUT_ROUTE_LEFT'})
    attempts=[];rejections={};example=None
    for key,g in tr.groupby(['nfl_id','draft_year','event_id'],sort=True):
        if g.drill_name.iloc[0] not in {x for v in MAP.values() for x in v}:continue
        try:f,diag=trajectory(g)
        except ValueError as e:rejections[str(e)]=rejections.get(str(e),0)+1;continue
        if example is None:example=diag
        attempts.append(dict(nfl_id=key[0],drill_name=g.drill_name.iloc[0],**f))
    feats=pd.DataFrame(attempts).groupby(['nfl_id','drill_name'])[FEATURES].median()
    blocks=[]
    for route,drills in MAP.items():
        b=feats.loc[feats.index.get_level_values('drill_name').isin(drills)].groupby('nfl_id').mean().reset_index();b['route_ran']=route;blocks.append(b)
    panel=pd.concat(blocks,ignore_index=True)
    d=pd.read_csv(data/'player_play.csv').merge(players[['nfl_id','draft_year','nfl_position']],on='nfl_id',validate='many_to_one')
    games=pd.read_csv(data/'games.csv');d=d.merge(games[['game_id','season','season_type','home_team_abbr','visitor_team_abbr']],on='game_id',validate='many_to_one')
    eligible=d[d.nfl_position.eq('WR')&d.season.eq(d.draft_year)&d.season_type.eq('REG')&d.route_ran.isin(MAP)&d.play_nullified_by_penalty.eq('N')].copy()
    missing=eligible.groupby(['draft_year','team_coverage_man_zone']).separation_at_pass_forward.apply(lambda x:float(x.isna().mean()))
    d=eligible[np.isfinite(eligible.separation_at_pass_forward)&eligible.separation_at_pass_forward.ge(0)].copy()
    counts=d.groupby('nfl_id').size();d=d[d.nfl_id.isin(counts[counts>=20].index)]
    d=d.merge(pd.read_csv(data/'combine_results.csv'),on=['nfl_id','draft_year'],validate='many_to_one').merge(panel,on=['nfl_id','route_ran'],how='left',validate='many_to_one')
    d['defense_team']=np.where(d.team_abbr.eq(d.home_team_abbr),d.visitor_team_abbr,d.home_team_abbr)
    d=d.reset_index(drop=True);d.to_pickle(out/'private_rows.pkl')
    audit={'players_by_class':{str(k):int(v) for k,v in d.groupby('draft_year').nfl_id.nunique().items()},'routes_by_class':{str(k):int(v) for k,v in d.groupby('draft_year').size().items()},'accepted_attempts':len(attempts),'rejected_attempts':rejections,'missing_movement_fraction':float(d.entry.isna().mean()),'missing_separation_by_class_coverage':{str(k):v for k,v in missing.items()},'movement_window_seconds':3,'features':FEATURES,'mapping':MAP,'feature_selection':'fixed mechanics and drill mapping; no outcome-directed selection'}
    (out/'mechanism_population.json').write_text(json.dumps(audit,indent=2))
    if example:
        import matplotlib;matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(1,2,figsize=(12,4),layout='constrained')
        q=example['q'];sc=ax[0].scatter(q[:,0],q[:,1],c=example['speed'],cmap='viridis');ax[0].plot(q[:,0],q[:,1],alpha=.4);ax[0].set_aspect('equal');ax[0].set(xlabel='Entry direction · yards',ylabel='Across entry · yards',title='Three-second measured turn');fig.colorbar(sc,ax=ax[0],label='Speed · yd/s')
        ax[1].plot(example['t'],example['speed'],lw=3);ax[1].axvline(0,ls=':',color='gray');ax[1].set(xlabel='Seconds from detected cut',ylabel='Speed · yd/s',title='Approach, brake and recover')
        fig.savefig(out/'mechanism_geometry.png',dpi=160);plt.close(fig)
    return d,audit

def nuisance():
    num=make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler())
    cat=make_pipeline(SimpleImputer(strategy='most_frequent'),OneHotEncoder(handle_unknown='ignore',sparse_output=False))
    pre=ColumnTransformer([('num',num,R.NUM),('cat',cat,R.CAT)])
    return make_pipeline(pre,ExtraTreesRegressor(n_estimators=100,max_depth=6,min_samples_leaf=20,max_features=.8,random_state=A.SEED,n_jobs=2))

def crossfit(tr,te,seed):
    assert not(set(tr.nfl_id)&set(te.nfl_id))
    oof=np.zeros(len(tr));folds=StratifiedGroupKFold(n_splits=3,shuffle=True,random_state=seed)
    for a,b in folds.split(tr,tr.draft_year,tr.nfl_id):
        m=nuisance();m.fit(tr.iloc[a],tr.iloc[a].separation_at_pass_forward,extratreesregressor__sample_weight=A.weights(tr.iloc[a]));oof[b]=m.predict(tr.iloc[b])
    m=nuisance();m.fit(tr,tr.separation_at_pass_forward,extratreesregressor__sample_weight=A.weights(tr))
    z=tr.copy();z['residual']=z.separation_at_pass_forward-oof
    # Equal total influence per prospect; multiple route/coverage means are partial pooling units.
    cols=R.PHYS+FEATURES
    groups=z.groupby(['nfl_id','route_ran','team_coverage_man_zone'],dropna=False)
    agg=groups[cols+['residual']].mean().reset_index()
    return agg,m.predict(te)

def correction(agg,te,alpha,motion):
    cols=R.PHYS+(FEATURES if motion else [])
    # Fit scaling only on one record per player/route/coverage; no held-out features.
    p=make_pipeline(SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True),StandardScaler())
    x=p.fit_transform(agg[cols]);xt=p.transform(te[cols])
    cats=OneHotEncoder(handle_unknown='ignore',sparse_output=False);c=cats.fit_transform(agg[['route_ran','team_coverage_man_zone']].fillna('MISSING'));ct=cats.transform(te[['route_ran','team_coverage_man_zone']].fillna('MISSING'))
    if motion:
        # Predefined physical and coverage interactions, after train-only scaling.
        j=cols.index('combine_weight');k=len(R.PHYS);man=agg.team_coverage_man_zone.eq('MAN_COVERAGE').to_numpy()[:,None];mant=te.team_coverage_man_zone.eq('MAN_COVERAGE').to_numpy()[:,None]
        x=np.c_[x,x[:,k:k+len(FEATURES)]*x[:,j,None],x[:,k:k+len(FEATURES)]*man]
        xt=np.c_[xt,xt[:,k:k+len(FEATURES)]*xt[:,j,None],xt[:,k:k+len(FEATURES)]*mant]
    m=Ridge(alpha=alpha);m.fit(np.c_[x,c],agg.residual,sample_weight=A.weights(agg));return m.predict(np.c_[xt,ct])

def run(data,out):
    out=Path(out);d,audit=prepare(data,out);dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);test=d[d.draft_year.eq(2025)].reset_index(drop=True)
    preds={k:np.zeros(len(dev)) for k in ['context','physical','motion']};records=[]
    outer=StratifiedGroupKFold(n_splits=4,shuffle=True,random_state=A.SEED+80)
    for fold,(a,b) in enumerate(outer.split(dev,dev.draft_year,dev.nfl_id)):
        tr,te=dev.iloc[a].reset_index(drop=True),dev.iloc[b];losses={k:np.zeros(len(ALPHAS)) for k in ['physical','motion']}
        inner=StratifiedGroupKFold(n_splits=3,shuffle=True,random_state=A.SEED+81+fold)
        for i,j in inner.split(tr,tr.draft_year,tr.nfl_id):
            ti,vi=tr.iloc[i].reset_index(drop=True),tr.iloc[j];agg,base=crossfit(ti,vi,A.SEED+90+fold)
            for family in losses:
                for ci,alpha in enumerate(ALPHAS):losses[family][ci]+=A.score(vi,base+correction(agg,vi,alpha,family=='motion'))/3
        agg,base=crossfit(tr,te,A.SEED+100+fold);preds['context'][b]=base
        for family in losses:
            ci=int(np.argmin(losses[family]));p=base+correction(agg,te,ALPHAS[ci],family=='motion');preds[family][b]=p;records.append({'fold':fold,'family':family,'alpha':ALPHAS[ci],'inner_mse':losses[family].tolist(),'outer_mse':A.score(te,p)})
        print('Mechanism outer',fold,{k:round(A.score(te,preds[k][b]),6) for k in preds},flush=True)
    nested={'mse':{k:A.score(dev,p) for k,p in preds.items()},'paired_motion_increment':R.bootstrap(dev,preds['physical'],preds['motion']),'folds':records,'players':int(dev.nfl_id.nunique()),'routes':len(dev)}
    # Forward-cohort selection, then refit earlier years; no 2025 tuning.
    tr=dev[dev.draft_year.eq(2023)].reset_index(drop=True);va=dev[dev.draft_year.eq(2024)];agg,base=crossfit(tr,va,A.SEED+200);chosen={}
    for family in ['physical','motion']:
        losses=[A.score(va,base+correction(agg,va,alpha,family=='motion')) for alpha in ALPHAS];ci=int(np.argmin(losses));chosen[family]={'alpha':ALPHAS[ci],'validation_mse':losses}
    agg,base=crossfit(dev,test,A.SEED+201);tp={'context':base}
    for family in chosen:tp[family]=base+correction(agg,test,chosen[family]['alpha'],family=='motion')
    transport={'mse':{k:A.score(test,p) for k,p in tp.items()},'paired_motion_increment':R.bootstrap(test,tp['physical'],tp['motion']),'selection':chosen,'players':int(test.nfl_id.nunique()),'routes':len(test)}
    subsets={}
    for label,rows,pp in [('nested',dev,preds),('exploratory_2025',test,tp)]:
        mask=rows.team_coverage_man_zone.eq('MAN_COVERAGE');n=rows[mask].groupby('nfl_id').size();mask&=rows.nfl_id.isin(n[n>=5].index)
        subsets[label]={'man_coverage_players':int(rows[mask].nfl_id.nunique()),'man_coverage_routes':int(mask.sum()),'paired_motion_increment':R.bootstrap(rows[mask],pp['physical'][mask],pp['motion'][mask])}
    result={'status':'completed_actual_data_exploratory','population':audit,'nested_development':nested,'exploratory_2025':transport,'predefined_man_subset':subsets,'limitations':['2025 previously inspected; no fresh holdout','Residual targets are cross-fitted by player, not causal receiver effects','Context-only nuisance fixed before this run; identical three-alpha selection budgets','No correction for unmeasured quarterback, defender ability, or missing-not-at-random outcomes','Earlier nested folds overlap prior research; this is corroboration, not independent confirmatory evidence']}
    (out/'mechanism_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
    plot(result,out/'mechanism_results.png')
    return result

def plot(result,path):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(1,2,figsize=(14,5),layout='constrained')
    for i,(name,key) in enumerate([('Earlier nested players','nested_development'),('Exploratory 2025','exploratory_2025')]):
        vals=result[key]['mse'];ax[0].bar(np.arange(3)+i*.36,[np.sqrt(vals[k]) for k in ['context','physical','motion']],width=.34,label=name)
    ax[0].set_xticks(np.arange(3)+.18,['Context only','+ Conventional','+ Mechanics']);ax[0].set(ylabel='Player-balanced RMSE · yards',title='Cross-fitted receiver contribution');ax[0].legend()
    vals=[result['nested_development']['paired_motion_increment'],result['exploratory_2025']['paired_motion_increment'],result['predefined_man_subset']['nested']['paired_motion_increment'],result['predefined_man_subset']['exploratory_2025']['paired_motion_increment']]
    for i,v in enumerate(vals):ax[1].plot(v['ci95'],[i,i],lw=4);ax[1].scatter(v['delta_mse'],i,s=70)
    ax[1].set_yticks(range(4),['Nested · all coverage','2025 · all coverage','Nested · man coverage','2025 · man coverage']);ax[1].axvline(0,color='gray',ls=':');ax[1].set(xlabel='Conventional − mechanics MSE · yd²',title='Positive favors mechanics; intervals are exploratory')
    fig.savefig(path,dpi=160);plt.close(fig)

def player_splits(rows,n_splits,seed):
    """Randomize unique players within class, rather than near-fixed route counts."""
    players=rows[['nfl_id','draft_year']].drop_duplicates().reset_index(drop=True)
    if players.nfl_id.duplicated().any():raise ValueError('player spans multiple classes')
    split=StratifiedKFold(n_splits=n_splits,shuffle=True,random_state=seed)
    for a,b in split.split(players,players.draft_year):
        yield np.flatnonzero(rows.nfl_id.isin(players.iloc[a].nfl_id)),np.flatnonzero(rows.nfl_id.isin(players.iloc[b].nfl_id))

def split_stability(data,out):
    """Repeat full nested selection; report conditional intervals and split variation."""
    out=Path(out);d=pd.read_pickle(out/'private_rows.pkl');dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True)
    results=[];deltas=[];partition_hashes=[]
    for repeat in range(3):
        seed=A.SEED+80+200*repeat;pred={k:np.zeros(len(dev)) for k in ['context','physical','motion']}
        folds=list(player_splits(dev,4,seed))
        import hashlib
        partition_hashes.append(hashlib.sha256(json.dumps([sorted(map(int,dev.iloc[b].nfl_id.unique())) for a,b in folds]).encode()).hexdigest())
        for fold,(a,b) in enumerate(folds):
            tr,te=dev.iloc[a].reset_index(drop=True),dev.iloc[b];loss={k:np.zeros(3) for k in ['physical','motion']}
            for i,j in player_splits(tr,3,seed+1+fold):
                agg,base=crossfit(tr.iloc[i].reset_index(drop=True),tr.iloc[j],seed+10+fold)
                for family in loss:
                    for ci,alpha in enumerate(ALPHAS):loss[family][ci]+=A.score(tr.iloc[j],base+correction(agg,tr.iloc[j],alpha,family=='motion'))/3
            agg,base=crossfit(tr,te,seed+20+fold);pred['context'][b]=base
            for family in loss:pred[family][b]=base+correction(agg,te,ALPHAS[int(np.argmin(loss[family]))],family=='motion')
        delta=pd.DataFrame({'id':dev.nfl_id,'delta':(dev.separation_at_pass_forward-pred['physical'])**2-(dev.separation_at_pass_forward-pred['motion'])**2}).groupby('id').delta
        deltas.append(delta.mean().to_numpy());results.append({'outer_seed':seed,'mse':{k:A.score(dev,p) for k,p in pred.items()},'paired_motion_increment':R.bootstrap(dev,pred['physical'],pred['motion'])})
        print('Split stability',repeat,results[-1],flush=True)
    x=np.mean(deltas,axis=0);rng=np.random.default_rng(A.SEED);ci=np.quantile(rng.choice(x,(5000,len(x)),replace=True).mean(axis=1),[.025,.975])
    if len(set(partition_hashes))!=3:raise ValueError('repeat partitions did not change')
    result={'repeated_nested_results':results,'partition_hashes':partition_hashes,'split_method':'Stratify unique players by draft year, then map all their routes to each fold','mean_player_delta_mse':float(x.mean()),'conditional_player_ci95':ci.tolist(),'positive_split_count':int(sum(r['paired_motion_increment']['delta_mse']>0 for r in results)),'scope':'Repeated folds share players; these are not three independent studies. Bootstrap averages each player across splits and conditions on fitted folds.'}
    (out/'mechanism_split_stability.json').write_text(json.dumps(result,indent=2));return result

if __name__=='__main__':
    root=Path(__file__).parent;run(root/'data',root/'private_mechanism')
