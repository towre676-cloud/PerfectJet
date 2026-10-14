"""Correct response follow-up while keeping the original pre-release turn anchor.

Revision motivated by 2023 development tracking timeline, never by selecting a
better-looking 2025 target. Original negative experiment remains retained.
"""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
import turn_transfer as T
import repo_predict as R

def measure(g,anchor):
    g=g.sort_values('time').reset_index(drop=True);tt=pd.to_datetime(g.time,utc=True,format='ISO8601');t=(tt-tt.iloc[0]).dt.total_seconds().to_numpy();c=int(round(float(anchor.cut_time)/.1))
    if c<5 or c+3>=len(g) or abs(t[c]-anchor.cut_time)>.015:raise ValueError('anchor_not_reconstructed')
    stop=min(c+15,len(g)-1)
    if not np.allclose(np.diff(t[c-5:stop+1]),.1,atol=.015):raise ValueError('irregular_followup')
    s=g.s.to_numpy(float);p=g[['x','y']].to_numpy(float);entry=float(anchor.entry)
    if not np.isfinite(s[c-5:stop+1]).all() or not np.isfinite(p[c-5:stop+1]).all():raise ValueError('nonfinite_followup')
    local=s[c-3:c+4];imin=c-3+int(np.argmin(local));event=False;recovery=float(t[stop]-t[c])
    if local.min()>=.9*entry:event=True;recovery=0.
    else:
        for i in range(max(c,imin),stop):
            if s[i]>=.9*entry and s[i+1]>=.9*entry:event=True;recovery=float(t[i]-t[c]);break
    f={'entry':entry,'angle':float(anchor.angle),'impulse':float(anchor.impulse),'cut_time':float(anchor.cut_time),'recovery_time':recovery,'recovery_event':event,'complete_half_second':c+5<len(g)}
    if f['complete_half_second']:
        q=p[c-3:c+6]-p[c-3];arc=np.linalg.norm(np.diff(q,axis=0),axis=1).sum();signedarea=.5*np.sum(q[:-1,0]*q[1:,1]-q[:-1,1]*q[1:,0]);f.update(burden=float(np.trapezoid(np.maximum(0,1-s[c:c+6]/entry),dx=.1)),retention=float(local.min()/entry),exit_ratio=float(s[c+3:c+6].mean()/entry),area=float(abs(signedarea)/max(arc**2,1e-9)))
    else:f.update({k:np.nan for k in T.STYLE})
    diag={'q':(p[c-5:stop+1]-p[c]).tolist(),'speed':s[c-5:stop+1].tolist(),'t':(t[c-5:stop+1]-t[c]).tolist(),'entry':entry,'angle':float(anchor.angle)};return f,diag

def prepare(data,original,out):
    data,original,out=Path(data),Path(original),Path(out);out.mkdir(parents=True,exist_ok=True);anchors=pd.read_pickle(original/'private_all_turns.pkl');source=pd.read_pickle(original/'private_source.pkl');keys=['game_id','play_id','nfl_id'];rows=[];rejected={};example=None
    for year in [2023,2024,2025]:
        anchor=anchors[anchors.draft_year.eq(year)];index=anchor.set_index(keys);parts=[]
        for chunk in pd.read_csv(data/f'game_tracking_{year}.csv',chunksize=200000):
            q=chunk[chunk.nfl_id.isin(anchor.nfl_id)].merge(anchor[keys],on=keys,validate='many_to_one')
            if len(q):parts.append(q)
        frames=pd.concat(parts,ignore_index=True)
        for key,g in frames.groupby(keys,sort=True):
            a=index.loc[key];snap=g[g.event.eq('ball_snap')]
            if len(snap)!=1:rejected['nonunique_snap']=rejected.get('nonunique_snap',0)+1;continue
            g=g[g.time.ge(snap.time.iloc[0])]
            try:f,diag=measure(g,a)
            except ValueError as e:rejected[str(e)]=rejected.get(str(e),0)+1;continue
            rows.append(dict(game_id=key[0],play_id=key[1],nfl_id=key[2],**f))
            if example is None:example=diag
        print('Extended follow-up',year,len(rows),flush=True)
    outcomes=pd.DataFrame(rows);drop=['entry','angle','impulse','cut_time','recovery_time','recovery_event','complete_half_second']+T.STYLE;allrows=anchors.drop(columns=drop).merge(outcomes,on=keys,validate='one_to_one');allrows.to_pickle(out/'private_all_turns.pkl')
    d=allrows[allrows.complete_half_second].copy();counts=d.groupby('nfl_id').size();d=d[d.nfl_id.isin(counts[counts>=10].index)].rename(columns={'entry':'game_entry','angle':'game_angle','impulse':'game_impulse'}).reset_index(drop=True);d.to_pickle(out/'private_rows.pkl');source.to_pickle(out/'private_source.pkl')
    originals=json.loads((original/'private_examples.json').read_text());(out/'private_examples.json').write_text(json.dumps({'source':originals['source'],'game':example}));audit={'anchor_scope':'Exact original pre-release first-turn anchors; only response follow-up extended','anchors':len(anchors),'extended_turns':len(allrows),'rejected_followup':rejected,'incomplete_half_second':int((~allrows.complete_half_second).sum()),'players_by_year':{str(k):int(v) for k,v in d.groupby('draft_year').nfl_id.nunique().items()},'turns_by_year':{str(k):int(v) for k,v in d.groupby('draft_year').size().items()},'recovery_bounds':T.recovery_bounds(allrows),'target_catches_by_year':{str(k):int(v) for k,v in d[d.target.eq(True)&np.isfinite(d.yards_after_catch)].groupby('draft_year').size().items()},'prior_2025_inspection':True,'limitations':'NFL post-release movement may include catching or route termination; lower deficit is not universally better, especially on intentional stop routes.'};(out/'population.json').write_text(json.dumps(audit,indent=2));return d,source,audit

def repeats(out):
    out=Path(out);d=pd.read_pickle(out/'private_rows.pkl');source=pd.read_pickle(out/'private_source.pkl');result=[];deltas=[]
    for seed in [T.SEED+200,T.SEED+400]:
        r=T.experiment(d,source,out/f'repeat_{seed}',seed=seed,forward=False);result.append(r)
        p0=pd.read_pickle(out/f'repeat_{seed}/private_nested_source_demands.pkl');p1=pd.read_pickle(out/f'repeat_{seed}/private_nested_execution.pkl');deltas.append(pd.DataFrame({'id':p0.nfl_id,'delta':(p0.truth-p0.prediction)**2-(p1.truth-p1.prediction)**2}).groupby('id').delta.mean())
    p0=pd.read_pickle(out/'burden/private_nested_source_demands.pkl');p1=pd.read_pickle(out/'burden/private_nested_execution.pkl');first=pd.DataFrame({'id':p0.nfl_id,'delta':(p0.truth-p0.prediction)**2-(p1.truth-p1.prediction)**2}).groupby('id').delta.mean();v=pd.concat([first,*deltas],axis=1).mean(axis=1).to_numpy();rng=np.random.default_rng(T.A.SEED);aggregate={'repeated_nested_results':result,'three_partition_mean_delta_mse':float(v.mean()),'conditional_ci95':np.quantile(rng.choice(v,(5000,len(v)),replace=True).mean(axis=1),[.025,.975]).tolist(),'scope':'Same earlier-season players across all repeats; not independent studies.'};(out/'stability.json').write_text(json.dumps(aggregate,indent=2));return aggregate

def yac_experiment(d,source,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);q=d[d.target.eq(True)&np.isfinite(d.yards_after_catch)].copy();counts=q.groupby('nfl_id').size();q=q[q.nfl_id.isin(counts[counts>=3].index)];audit={'players_by_year':{str(k):int(v) for k,v in q.groupby('draft_year').nfl_id.nunique().items()},'catches_by_year':{str(k):int(v) for k,v in q.groupby('draft_year').size().items()},'eligibility':'>=3 targeted catches with measured YAC per player; original turn cohort retained'};(out/'population.json').write_text(json.dumps(audit,indent=2))
    if min(q.groupby('draft_year').nfl_id.nunique().reindex([2023,2024,2025],fill_value=0))<10:
        r={'status':'frozen_YAC_population_feasibility_failure','population':audit};(out/'results.json').write_text(json.dumps(r,indent=2));return r
    original=R.NUM
    try:
        R.NUM=original+['pass_length','expected_yards_after_catch'];r=T.experiment(q,source,out,target='yards_after_catch');r['catch_context_baseline']='Includes pass length and supplied expected YAC, an outcome-side vendor catch-context reference; not a pre-draft unconditional forecast.';r['population']=audit;test=q[q.draft_year.eq(2025)];mask=np.isfinite(test.expected_yards_after_catch)
        if mask.any():r['provided_expected_YAC_reference_mse']=T.score(test[mask],test.loc[mask,'expected_yards_after_catch'].to_numpy(),'yards_after_catch')
        (out/'results.json').write_text(json.dumps(r,indent=2));return r
    finally:R.NUM=original

def run(data,original,out):
    out=Path(out);d,source,audit=prepare(data,original,out);primary=T.experiment(d,source,out/'burden');separation=T.experiment(d,source,out/'separation',target='separation_at_pass_forward');yac=yac_experiment(d,source,out/'yac');return primary,separation,yac
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--data',default='data');p.add_argument('--original',default='private_turn_transfer');p.add_argument('--out',default='private_post_release');p.add_argument('--repeats',action='store_true');a=p.parse_args()
    if a.repeats:repeats(a.out)
    else:run(a.data,a.original,a.out)
