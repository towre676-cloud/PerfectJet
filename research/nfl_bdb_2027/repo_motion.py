"""Multi-drill ordered geometry and observable velocity-state summaries.

The rational surrogate is checked exactly; the measured trajectory and its
regression relationship remain numerical empirical questions.
"""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
import analysis as A
from vendor.pp import observable_machine as O


def signature3(path):
    path=np.asarray(path,float);dim=path.shape[1];s1=np.zeros(dim);s2=np.zeros((dim,dim));s3=np.zeros((dim,dim,dim))
    for inc in np.diff(path,axis=0):
        inc2=np.outer(inc,inc)/2
        s3=s3+np.einsum('ij,k->ijk',s2,inc)+np.einsum('i,jk->ijk',s1,inc2)+np.einsum('i,j,k->ijk',inc,inc,inc)/6
        s2=s2+np.outer(s1,inc)+inc2;s1=s1+inc
    return np.r_[s1,s2.ravel(),s3.ravel()]


def descriptors(g):
    base,diag=A.movement(g);q=diag['q'];s=diag['speed'];arc=float(np.linalg.norm(np.diff(q,axis=0),axis=1).sum());entry=base['entry_speed']
    path=np.c_[diag['t']+.5,q/max(arc,1e-6),s/max(entry,1e-6)]
    sig=signature3(path);features=dict(base)
    for i,v in enumerate(sig):features[f'sig_{i:03d}']=float(v)
    grid=np.linspace(-1,1,len(s));profile=s/max(entry,1e-6)
    for i,v in enumerate(np.polynomial.legendre.legfit(grid,profile,4)):features[f'profile_{i}']=float(v)
    H=np.stack([profile[i:i+7] for i in range(5)]);sv=np.linalg.svd(H,compute_uv=False);p=sv/sv.sum();features['hankel_entropy']=float(-np.sum(p*np.log(np.maximum(p,1e-12))))
    for i,v in enumerate(p):features[f'hankel_{i}']=float(v)
    # Ridge-fit two-state recurrence to normalized measured speed.
    X=np.c_[profile[1:-1],profile[:-2]];y=profile[2:];coef=np.linalg.solve(X.T@X+1e-3*np.eye(2),X.T@y)
    fitted=X@coef;features['memory_a1']=float(coef[0]);features['memory_a2']=float(coef[1]);features['memory_residual']=float(np.sqrt(np.mean((y-fitted)**2)))
    features['memory_radius']=float(np.max(np.abs(np.roots([1,-coef[0],-coef[1]]))))
    aq=[f'{v:.4f}' for v in coef];seed=[f'{profile[1]:.6f}',f'{profile[0]:.6f}']
    packet=O.minimal_machine([[[aq[0],aq[1]],[1,0]]],seed,[[1,0]])
    if not O.verify_machine(packet):raise ValueError('surrogate certificate rejected')
    # Check original and quotient forecasts agree exactly over twelve readouts.
    for k in range(12):
        if O.power_outputs(packet,k)!=O.power_outputs(packet,k,original=True):raise ValueError('source/quotient readout mismatch')
    return features,packet


def build_features(root,out,aliases=False):
    root,out=Path(root),Path(out);out.mkdir(exist_ok=True,parents=True);players=pd.read_csv(root/'players.csv');ids=set(players.loc[players.nfl_position.eq('WR'),'nfl_id']);d=pd.read_csv(root/'combine_tracking.csv');d=d[d.entity_type.eq('PLAYER')&d.nfl_id.isin(ids)&d.drill_type.eq('SKILL_DRILLS_WR')]
    if aliases:d['drill_name']=d.drill_name.replace({'SPEED_OUT_LEFT':'SPEED_OUT_ROUTE_LEFT'})
    rows=[];rejects=0;orders={};example=None
    for key,g in d.groupby(['nfl_id','draft_year','event_id']):
        try:f,packet=descriptors(g)
        except ValueError:rejects+=1;continue
        if example is None:example=packet
        order=packet['minimal_dimension'];orders[str(order)]=orders.get(str(order),0)+1
        rows.append(dict(nfl_id=key[0],draft_year=key[1],event_id=key[2],drill_name=g.drill_name.iloc[0],**f))
    attempts=pd.DataFrame(rows);features=[c for c in attempts.columns if c not in ['nfl_id','draft_year','event_id','drill_name']]
    availability=attempts.groupby(['drill_name','draft_year']).nfl_id.nunique().unstack(fill_value=0).reindex(columns=[2023,2024,2025],fill_value=0)
    drills=sorted(availability.index[availability.min(axis=1)>=5]);attempts=attempts[attempts.drill_name.isin(drills)]
    panel=attempts.groupby(['nfl_id','drill_name'])[features].median().unstack('drill_name');panel.columns=[f'motion__{drill}__{feature}' for feature,drill in panel.columns];panel=panel.reset_index()
    panel.to_csv(out/'private_motion_panel.csv',index=False)
    (out/'private_surrogate_example.json').write_text(json.dumps(example,default=str,indent=2))
    audit={'qualifying_attempts_all_drills':len(rows),'qualifying_shared_attempts':len(attempts),'shared_drills':drills,'players_with_features':len(panel),'feature_columns':len(panel.columns)-1,'rejected_no_cut_attempts':rejects,'surrogate_order_counts':orders,'exact_surrogate_certificates_replayed':len(rows),'certified_readouts_per_surrogate':12,'name_alias_applied':aliases,'scope':'quantized supplied surrogate only; measured trajectories and predictive skill not certified'}
    (out/'feature_audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2),flush=True)
    return panel,audit

if __name__=='__main__':
    root=Path(__file__).parent;build_features(root/'data',root/'private_repo_results')
