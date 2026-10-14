"""Order-sensitive Combine channels; finite monotone phase-language adaptation.

No prime arithmetic or Pauli phases are interpreted as athlete physiology.
Only source tracking enters scouting features. All fitted transforms are fold-local.
"""
from pathlib import Path
import json,itertools
import numpy as np,pandas as pd
from scipy.special import logsumexp
from scipy.signal import savgol_filter
from sklearn.linear_model import Ridge
import turn_transfer as T,repo_predict as R,analysis as A
from mechanism import player_splits

def phase_channel(z):
    """Weighted accepting paths through approach/brake/redirect/recover.

    Each frame stays or advances one phase; start 0, finish 3. Forward-backward
    sums all admissible paths rather than choosing one noisy segmentation.
    """
    a,w=z[:,0],z[:,1]
    cost=np.c_[a*a+w*w,(a+1)**2+w*w,a*a+(w-1)**2,(a-1)**2+w*w]/2
    n=len(z);f=np.full((n,4),-np.inf);b=f.copy();f[0,0]=-cost[0,0];b[-1,3]=0
    for i in range(1,n):
        for k in range(4):f[i,k]=logsumexp(f[i-1,max(0,k-1):k+1])-cost[i,k]
    for i in range(n-2,-1,-1):
        for k in range(4):b[i,k]=logsumexp(-cost[i+1,k:min(4,k+2)]+b[i+1,k:min(4,k+2)])
    p=np.exp(f+b-f[-1,3]);occupancy=p.mean(axis=0)
    return np.r_[occupancy,(p*z[:,0,None]).sum(axis=0)/np.maximum(p.sum(axis=0),1e-9),f[-1,3]/n]

def signature(z):
    dz=np.diff(z,axis=0);mid=(z[:-1]+z[1:])/2
    area=np.array([np.sum(mid[:,i]*dz[:,j]-mid[:,j]*dz[:,i])/2 for i,j in itertools.combinations(range(z.shape[1]),2)])
    return np.r_[z.mean(axis=0),z.std(axis=0),z[-1]-z[0],area,phase_channel(z[:,1:3])]

def extract(data,out):
    source=pd.read_pickle(Path('private_post_release/private_source.pkl'));tr=pd.read_csv(Path(data)/'combine_tracking.csv');tr=tr[tr.nfl_id.isin(source.nfl_id)&tr.entity_type.eq('PLAYER')];lookup={key:g for key,g in tr.groupby(['nfl_id','event_id'])};rows=[]
    for row in source.itertuples():
        g=lookup[(row.nfl_id,row.event_id)].sort_values('time');c=int(round(row.cut_time*10));p=g[['x','y']].to_numpy(float);v=np.gradient(savgol_filter(p,7,3,axis=0),.1,axis=0);s=g.s.to_numpy(float);a=np.gradient(s,.1);theta=np.unwrap(np.arctan2(v[:,1],v[:,0]));w=np.abs(np.gradient(theta,.1));record={'nfl_id':row.nfl_id,'event_id':row.event_id}
        for radius in [6,10,14]:
            lo=max(0,c-radius);hi=min(len(g),c+radius+1);z=np.c_[s[lo:hi]/max(row.entry,1),a[lo:hi]/5,w[lo:hi],np.cumsum(s[lo:hi])*.1/max(row.entry,1)];feat=signature(z)
            record.update({f'order_{radius}_{j}':float(x) for j,x in enumerate(feat)})
        rows.append(record)
    source=source.merge(pd.DataFrame(rows),on=['nfl_id','event_id'],validate='one_to_one');Path(out).mkdir(exist_ok=True);source.to_pickle(Path(out)/'private_source.pkl');return source

def predict(tr,te,source,target,radius,alpha):
    if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('player leakage')
    if alpha is None:return np.zeros(len(te))
    enc=T.TurnEncoder(source,'source_demands').fit(tr);x,y=enc.transform(tr),enc.transform(te)
    if radius:
        cols=[c for c in source if c.startswith(f'order_{radius}_')];table=source.groupby(['nfl_id','route_ran'])[cols].median()
        def look(d):return table.reindex(pd.MultiIndex.from_frame(d[['nfl_id','route_ran']])).to_numpy(float)
        units=tr.drop_duplicates(['nfl_id','route_ran']);scale=T.numeric().fit(look(units));physical=T.numeric().fit(units[R.PHYS]);residual=Ridge(alpha=10).fit(physical.transform(units[R.PHYS]),scale.transform(look(units)),sample_weight=A.weights(units))
        def motion(d):
            z=scale.transform(look(d))-residual.predict(physical.transform(d[R.PHYS]));return np.c_[z,z*z]
        x=np.c_[x,motion(tr)];y=np.c_[y,motion(te)]
    model=Ridge(alpha=alpha).fit(x,tr[target],sample_weight=A.weights(tr));return model.predict(y)

def correction_predict(tr,te,source,target,radius,alpha):
    base_alpha=10 if target=='burden' else None
    baseline=predict(tr,te,source,target,0,base_alpha)
    if not radius:return baseline
    residual=tr[target].to_numpy().copy()
    for i,j in player_splits(tr.reset_index(drop=True),3,T.SEED+1800):residual[j]-=predict(tr.iloc[i],tr.iloc[j],source,target,0,base_alpha)
    cols=[c for c in source if c.startswith(f'order_{radius}_')];table=source.groupby(['nfl_id','route_ran'])[cols].median()
    def look(d):return table.reindex(pd.MultiIndex.from_frame(d[['nfl_id','route_ran']])).to_numpy(float)
    units=tr.drop_duplicates(['nfl_id','route_ran']);scale=T.numeric().fit(look(units));physical=T.numeric().fit(units[R.PHYS]);nuisance=Ridge(alpha=10).fit(physical.transform(units[R.PHYS]),scale.transform(look(units)),sample_weight=A.weights(units));demand=T.numeric().fit(tr[T.GAME])
    def features(d):
        z=scale.transform(look(d))-nuisance.predict(physical.transform(d[R.PHYS]));g=demand.transform(d[T.GAME]);mass=physical.transform(d[R.PHYS])[:,R.PHYS.index('combine_weight')];return np.c_[z,z*z,z*g[:,0,None],z*g[:,1,None],z*mass[:,None]]
    reg=Ridge(alpha=alpha,fit_intercept=False).fit(features(tr),residual,sample_weight=A.weights(tr));return baseline+reg.predict(features(te))

def catch_population(data,source):
    data=Path(data);p=pd.read_csv(data/'players.csv');phys=pd.read_csv(data/'combine_results.csv');games=pd.read_csv(data/'games.csv')
    d=pd.read_csv(data/'player_play.csv').merge(p[['nfl_id','draft_year','nfl_position']],on='nfl_id',validate='many_to_one').merge(games,on='game_id',validate='many_to_one').merge(phys,on=['nfl_id','draft_year'],validate='many_to_one')
    d=d[d.nfl_id.isin(source.nfl_id)&d.nfl_position.eq('WR')&d.season.eq(d.draft_year)&d.season_type.eq('REG')&d.play_nullified_by_penalty.eq('N')&d.target.eq(True)&np.isfinite(d.yards_after_catch)&np.isfinite(d.expected_yards_after_catch)].copy()
    counts=d.groupby('nfl_id').size();d=d[d.nfl_id.isin(counts[counts>=10].index)].reset_index(drop=True);d['defense_team']=np.where(d.team_abbr.eq(d.home_team_abbr),d.visitor_team_abbr,d.home_team_abbr);d['actual_route']=d.route_ran;d['route_ran']='ALL';d['yac_residual']=d.yards_after_catch-d.expected_yards_after_catch
    for c in T.GAME:d[c]=np.nan
    return d

def run(source,out,target,correction=False,rows=None):
    d=pd.read_pickle('private_post_release/private_rows.pkl') if rows is None else rows.copy()
    if target=='yac_residual' and rows is None:
        import yac_reference_correction as Y
        d=Y.cohort('private_post_release')
    dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);test=d[d.draft_year.eq(2025)].reset_index(drop=True);dest=Path(out)/target;dest.mkdir(exist_ok=True);base=[(0,a) for a in [10,100,1000,10000]];ordered=[(r,a) for r in [6,10,14] for a in [100,1000,10000]]
    if target=='yac_residual':base+=[(0,None)];ordered+=[(0,None)]
    predictor=predict
    if correction:
        predictor=correction_predict;base=[(0,None)];ordered=[(r,a) for r in [6,10,14] for a in [1,10,100]]
    pred={k:np.zeros(len(dev)) for k in ['baseline','ordered']};folds=[];selection=[];tp={};old=R.NUM
    if target=='yac_residual':R.NUM=old+['pass_length','expected_yards_after_catch']
    try:
        for fold,(i,j) in enumerate(player_splits(dev,4,T.SEED+900)):
            tr=dev.iloc[i].reset_index(drop=True);te=dev.iloc[j]
            for family,bank in [('baseline',base),('ordered',base+ordered)]:
                loss=[np.mean([T.score(tr.iloc[b],predictor(tr.iloc[a],tr.iloc[b],source,target,*spec),target) for a,b in player_splits(tr,3,T.SEED+901+fold)]) for spec in bank];ci=int(np.argmin(loss));pred[family][j]=predictor(tr,te,source,target,*bank[ci]);folds.append({'fold':fold,'family':family,'selected':bank[ci],'loss':list(map(float,loss))});print(target,fold,family,bank[ci],flush=True)
        tr=dev[dev.draft_year.eq(2023)];va=dev[dev.draft_year.eq(2024)]
        for family,bank in [('baseline',base),('ordered',base+ordered)]:
            loss=[T.score(va,predictor(tr,va,source,target,*s),target) for s in bank];ci=int(np.argmin(loss));selection.append({'family':family,'selected':bank[ci],'validation_loss':loss});tp[family]=predictor(dev,test,source,target,*bank[ci])
        result={'target':target,'baseline_preserving_correction':correction,'prior_2025_inspection':True,'folds':folds,'selection':selection,'source_attempts':len(source),'source_players':int(source.nfl_id.nunique())}
        for label,rows,pp in [('nested',dev,pred),('exploratory_2025',test,tp)]:
            result[label]={'mse':{k:T.score(rows,p,target) for k,p in pp.items()},'increment':T.interval(rows,pp['baseline'],pp['ordered'],target),'players':int(rows.nfl_id.nunique()),'rows':len(rows)}
            if target=='yac_residual':result[label]['mse']['provided_expected_YAC']=T.score(rows,np.zeros(len(rows)),target);result[label]['vs_reference']=T.interval(rows,np.zeros(len(rows)),pp['ordered'],target)
            pd.DataFrame({'nfl_id':rows.nfl_id,'truth':rows[target],'baseline':pp['baseline'],'ordered':pp['ordered']}).to_pickle(dest/f'private_{label}.pkl')
        (dest/'results.json').write_text(json.dumps(result,indent=2));return result
    finally:R.NUM=old

if __name__=='__main__':
    out='private_ordered_motion';source=extract('data',out)
    for target in ['burden','yac_residual']:run(source,out,target)
