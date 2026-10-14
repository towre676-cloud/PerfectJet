"""Exploratory scouting-rate aggregation, stability and profile-identity controls."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.stats import spearmanr
import front_transfer as F,analysis as A,observability as O

def player_rates(q,target='pressure_event'):
    p=q.groupby('nfl_id').mean(numeric_only=True).reset_index();families=['conventional','sprint','skills','combined'];return {'mse':{k:O.score(p,p[k],target) for k in families},'comparisons':{k:O.interval(p,p.conventional,p[k],target) for k in families if k!='conventional'},'players':len(p),'definition':'Squared error of each player observed pressure-event frequency versus mean predicted probability over that player actual charted rush workload. Secondary metric added after play-level inspection; conditional on NFL workload/context, not unconditional pre-draft production.'}

def run(out='private_front_strong',repeats=True):
    out=Path(out);d=pd.read_pickle('private_front/private_rows.pkl');cols=json.loads(Path('private_front/population.json').read_text())['source_features'];result={'scouting_rates':{split:player_rates(pd.read_pickle(out/'pressure_event'/f'private_{split}.pkl')) for split in ['nested','exploratory_2025']},'secondary_metric_post_hoc':True}
    if repeats:
        for seed in [F.SEED+200,F.SEED+400]:F.experiment(d,cols,out/f'repeat_{seed}','pressure_event',seed=seed,forward=False)
    panels=[pd.read_pickle(out/'pressure_event/private_nested.pkl')]+[pd.read_pickle(out/f'repeat_{seed}/pressure_event/private_nested.pkl') for seed in [F.SEED+200,F.SEED+400]];delta=[];detail=[]
    for q in panels:
        detail.append(player_rates(q));p=q.groupby('nfl_id').mean(numeric_only=True);delta.append((p.pressure_event-p.conventional)**2-(p.pressure_event-p.combined)**2)
    v=pd.concat(delta,axis=1).mean(axis=1).to_numpy();rng=np.random.default_rng(A.SEED);result['development_repeated_partitions']={'details':detail,'mean_player_rate_delta':float(v.mean()),'conditional_ci95':np.quantile(rng.choice(v,(5000,len(v)),replace=True).mean(1),[.025,.975]).tolist(),'scope':'Same earlier players in all partitions; not three independent replications.'}
    r=json.loads((out/'pressure_event/results.json').read_text());ci=next(x['config'] for x in r['selection'] if x['family']=='combined');tr=d[d.draft_year.isin([2023,2024])];te=d[d.draft_year.eq(2025)].reset_index(drop=True);predict=F.fit_predict(tr,te,cols,F.CONFIGS[ci],'pressure_event',return_predictor=True);units=te.drop_duplicates('nfl_id').set_index('nfl_id');shuffles=[];rng=np.random.default_rng(F.SEED+800);original=predict(te)
    for repeat in range(30):
        table=units[cols].copy()
        for _,g in units.groupby('nfl_position'):
            table.loc[g.index,cols]=units.loc[rng.permutation(g.index),cols].to_numpy()
        q=te.copy();q[cols]=table.reindex(q.nfl_id).to_numpy();prediction=predict(q);p=pd.DataFrame({'nfl_id':q.nfl_id,'truth':q.pressure_event,'prediction':prediction}).groupby('nfl_id').mean();shuffles.append(float(np.mean((p.truth-p.prediction)**2)))
    p=pd.DataFrame({'nfl_id':te.nfl_id,'truth':te.pressure_event,'prediction':original}).groupby('nfl_id').mean();result['profile_controls']={'real_mse':float(np.mean((p.truth-p.prediction)**2)),'within_position_shuffled_mse':shuffles,'shuffles_better_than_real':int(np.sum(np.array(shuffles)<=np.mean((p.truth-p.prediction)**2))),'scope':'Fixed trained earlier-class model; whole held-out player profiles permuted within NFL position. No reselection. Diagnostic, not an exchangeability-certified p-value; permutations can break physical/profile dependence and availability.'}
    delta=((p.truth-p.prediction)**2).to_numpy();q=pd.read_pickle(out/'pressure_event/private_exploratory_2025.pkl').groupby('nfl_id').mean(numeric_only=True);v=(q.pressure_event-q.conventional)**2-(q.pressure_event-q.combined)**2;result['leave_one_player_out_delta_range']=[float((v.sum()-x)/(len(v)-1)) for x in v];teams=te.groupby('nfl_id').team_abbr.first();team_delta=v.groupby(teams).sum();team_n=v.groupby(teams).size();values=[]
    for _ in range(5000):i=rng.integers(0,len(team_delta),len(team_delta));values.append(float(team_delta.iloc[i].sum()/team_n.iloc[i].sum()))
    result['team_cluster_forward']={'teams':len(team_delta),'delta_mse':float(v.mean()),'conditional_ci95':np.quantile(values,[.025,.975]).tolist(),'scope':'Team resampling over fixed player-mean errors; model and cohort fixed.'};(out/'scouting_diagnostics.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':run()

def refit_bootstrap(out='private_front_strong',repetitions=80,max_steps=None):
    out=Path(out);d=pd.read_pickle('private_front/private_rows.pkl');cols=json.loads(Path('private_front/population.json').read_text())['source_features'];r=json.loads((out/'pressure_event/results.json').read_text());configs={row['family']:row['config'] for row in r['selection']};tr=d[d.draft_year.isin([2023,2024])];te=d[d.draft_year.eq(2025)].reset_index(drop=True);rng=np.random.default_rng(F.SEED+1600);fixed=[];joint=[]
    groups={k:g for k,g in tr.groupby('nfl_id')};units=tr[['nfl_id','draft_year']].drop_duplicates();
    checkpoint=out/'refit_checkpoint.json';start=0
    if checkpoint.exists():
        saved=json.loads(checkpoint.read_text())
        if saved['repetitions']!=repetitions:raise ValueError('Bootstrap checkpoint count mismatch')
        fixed=saved['fixed'];joint=saved['joint'];rng.bit_generator.state=saved['rng'];start=len(fixed)
    for iteration in range(start,min(repetitions,start+max_steps) if max_steps else repetitions):
        blocks=[];replica=0
        for _,g in units.groupby('draft_year'):
            for player in rng.choice(g.nfl_id.to_numpy(),len(g),replace=True):
                q=groups[player].copy();q['nfl_id']=-1-replica;replica+=1;blocks.append(q)
        boot=pd.concat(blocks,ignore_index=True);p0=F.fit_predict(boot,te,[],F.CONFIGS[configs['conventional']],'pressure_event');p1=F.fit_predict(boot,te,cols,F.CONFIGS[configs['combined']],'pressure_event');q=pd.DataFrame({'nfl_id':te.nfl_id,'truth':te.pressure_event,'p0':p0,'p1':p1}).groupby('nfl_id').mean();v=((q.truth-q.p0)**2-(q.truth-q.p1)**2).to_numpy();fixed.append(float(v.mean()));joint.append(float(rng.choice(v,len(v),replace=True).mean()))
        if iteration%10==0:print('Training-player model refits',iteration,flush=True)
        checkpoint.write_text(json.dumps({'repetitions':repetitions,'fixed':fixed,'joint':joint,'rng':rng.bit_generator.state}))
    if len(fixed)<repetitions:return {'status':'checkpointed_incomplete','completed':len(fixed),'required':repetitions}
    result={'replicates':repetitions,'training_resampling':'Player bootstrap separately within 2023/2024; replica IDs preserve multiplicity in fitting and training transforms','selected_configs_fixed':configs,'fixed_forward_players_delta':fixed,'joint_training_and_forward_player_delta':joint,'fixed_forward_ci95':np.quantile(fixed,[.025,.975]).tolist(),'joint_ci95':np.quantile(joint,[.025,.975]).tolist(),'scope':'Refits scaling, physical residualization, PCA and models. Earlier selected configurations remain fixed; does not repeat full model selection or correct adaptive secondary-outcome searching.'};(out/'refit_bootstrap.json').write_text(json.dumps(result,indent=2));return result
