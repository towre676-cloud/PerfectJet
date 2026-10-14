"""Source identity controls, matched reference comparisons, and paired geometry."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.stats import spearmanr
import turn_transfer as T,post_release_transfer as P,repo_predict as R

def run(out,data):
    out,data=Path(out),Path(data);d=pd.read_pickle(out/'private_rows.pkl');source=pd.read_pickle(out/'private_source.pkl');raw=json.loads((out/'yac/results.json').read_text());q=d[d.target.eq(True)&np.isfinite(d.yards_after_catch)].copy();count=q.groupby('nfl_id').size();q=q[q.nfl_id.isin(count[count>=3].index)];dev=q[q.draft_year.isin([2023,2024])].reset_index(drop=True);test=q[q.draft_year.eq(2025)].reset_index(drop=True);ci=next(x['config'] for x in raw['forward_selection'] if x['family']=='execution');p=pd.read_pickle(out/'yac/private_forward_execution.pkl').prediction.to_numpy();mask=np.isfinite(test.expected_yards_after_catch);comparison=T.interval(test[mask],test.loc[mask,'expected_yards_after_catch'].to_numpy(),p[mask],'yards_after_catch');rng=np.random.default_rng(T.A.SEED+3300);values=[];old=R.NUM
    try:
        R.NUM=old+['pass_length','expected_yards_after_catch']
        players=dev[['nfl_id','draft_year']].drop_duplicates()
        for repeat in range(30):
            swapped=source.copy();mapping={}
            for _,g in players.groupby('draft_year'):
                ids=g.nfl_id.to_numpy();mapping.update(dict(zip(ids,rng.permutation(ids))))
            swapped['nfl_id']=swapped.nfl_id.map(lambda x:mapping.get(x,x));pred=T.fit_predict(dev,test,swapped,'execution',R.CONFIGS[ci],'yards_after_catch');values.append(T.score(test,pred,'yards_after_catch'));print('YAC source identity control',repeat+1,values[-1],flush=True)
    finally:R.NUM=old
    pairs=[(g.iloc[0],g.iloc[-1]) for _,g in source.sort_values('event_id').groupby(['nfl_id','drill_name']) if len(g)>=2];repeatability={c:float(spearmanr([a[c] for a,b in pairs],[b[c] for a,b in pairs]).statistic) if len(pairs)>2 else None for c in ['entry','angle']+T.STYLE}
    loo=[]
    for player in test.nfl_id.unique():
        keep=test.nfl_id.ne(player);loo.append(T.interval(test[keep],np.asarray(pd.read_pickle(out/'yac/private_forward_source_demands.pkl').prediction)[keep],p[keep],'yards_after_catch')['delta_mse'])
    support={}
    for route in T.MAP:
        s=source[source.draft_year.isin([2023,2024])&source.route_ran.eq(route)];g=d[d.draft_year.eq(2025)&d.route_ran.eq(route)]
        if len(s) and len(g):
            lo=s[['entry','angle']].quantile(.05).to_numpy();hi=s[['entry','angle']].quantile(.95).to_numpy();z=g[['game_entry','game_angle']].to_numpy();support[route]={'game_turns':len(g),'inside_earlier_source_5_95_rectangle_fraction':float(((z>=lo)&(z<=hi)).all(axis=1).mean())}
    # Select one paired development example without looking at NFL responses.
    available=pd.MultiIndex.from_frame(source[['nfl_id','route_ran']]);candidate=d[d.draft_year.eq(2023)].copy();candidate=candidate[pd.MultiIndex.from_frame(candidate[['nfl_id','route_ran']]).isin(available)].sort_values(['nfl_id','route_ran','game_id','play_id']).iloc[0];attempt=source[source.nfl_id.eq(candidate.nfl_id)&source.route_ran.eq(candidate.route_ran)].sort_values('event_id').iloc[0]
    st=pd.read_csv(data/'combine_tracking.csv');sg=st[st.event_id.eq(attempt.event_id)&st.nfl_id.eq(attempt.nfl_id)&st.entity_type.eq('PLAYER')];sf,sd=T.first_turn(sg);parts=[]
    for chunk in pd.read_csv(data/'game_tracking_2023.csv',chunksize=200000):
        g=chunk[chunk.game_id.eq(candidate.game_id)&chunk.play_id.eq(candidate.play_id)&chunk.nfl_id.eq(candidate.nfl_id)]
        if len(g):parts.append(g)
    g=pd.concat(parts).sort_values('time');snap=g[g.event.eq('ball_snap')];g=g[g.time.ge(snap.time.iloc[0])];anchor=candidate.copy();anchor['entry']=candidate.game_entry;anchor['angle']=candidate.game_angle;anchor['impulse']=candidate.game_impulse;gf,gd=P.measure(g,anchor)
    release=g[g.event.eq('pass_forward')];release_relative=float((pd.to_datetime(release.time.iloc[0],utc=True)-pd.to_datetime(snap.time.iloc[0],utc=True)).total_seconds()-candidate.cut_time)
    (out/'private_paired_example.json').write_text(json.dumps({'source':sd,'game':gd,'route':candidate.route_ran,'source_metrics':sf,'game_metrics':gf,'release_relative_seconds':release_relative}))
    result={'status':'completed_actual_data_diagnostics','raw_yac_identity_shuffles':{'mse':values,'mean_mse':float(np.mean(values)),'real_profile_mse':raw['exploratory_2025']['mse']['execution'],'selected_config':ci,'scope':'Whole training-player profiles swapped within class; selected configuration fixed; no reselection-based p-value.'},'raw_YAC_vs_provided_reference_same_finite_subset':{'catches':int(mask.sum()),'reference_mse':T.score(test[mask],test.loc[mask,'expected_yards_after_catch'].to_numpy(),'yards_after_catch'),'execution_mse':T.score(test[mask],p[mask],'yards_after_catch'),'paired':comparison},'leave_one_player_out_raw_YAC_delta_range':[float(min(loo)),float(max(loo))],'same_drill_repeat_pairs':len(pairs),'same_drill_first_last_spearman':repeatability,'source_game_demand_overlap_2025':support,'interpretation':'Support mismatch, small player counts and profile controls constrain transfer claims. LOO ranges are sensitivity diagnostics, not independent studies.'};(out/'diagnostics.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':run(Path(__file__).parent/'private_post_release',Path(__file__).parent/'data')
