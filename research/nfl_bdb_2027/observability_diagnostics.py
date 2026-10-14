"""Negative controls and stronger kinematic comparators on frozen model choices."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import observability as O
import analysis as A

def run(out):
    out=Path(out);d=pd.read_pickle(out/'private_rows.pkl');dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);te=d[d.draft_year.eq(2025)].reset_index(drop=True)
    results=json.loads((out/'absolute_speed/results.json').read_text());choices={x['family']:x['config'] for x in results['forward_selection']}
    pp={name:pd.read_pickle(out/f'absolute_speed/private_forward_{name}.pkl').prediction.to_numpy() for name in choices}
    controls={'early_speed_persistence':O.score(te,te.early_speed.to_numpy(),'future_speed'),'constant_early_acceleration':O.score(te,(te.early_speed+te.early_acceleration).to_numpy(),'future_speed')}
    # Profile swaps preserve each donor's complete source geometry and stay in class.
    rng=np.random.default_rng(A.SEED+2000);cols=[c for c in dev if c.startswith('motion__')];shuffles=[]
    for repeat in range(30):
        tr=dev.copy();panel=tr.drop_duplicates('nfl_id').set_index('nfl_id');shuffled=panel[cols].copy()
        for year in [2023,2024]:
            ids=panel.index[panel.draft_year.eq(year)];shuffled.loc[ids]=panel.loc[rng.permutation(ids),cols].to_numpy()
        for c in cols:tr[c]=tr.nfl_id.map(shuffled[c])
        pred=O.fit_predict(tr,te,'future_speed','target_motion',True,O.CONFIGS[choices['target_motion_with_state']],A.SEED+510);shuffles.append(O.score(te,pred,'future_speed'))
        print('Training-profile shuffle',repeat+1,shuffles[-1],flush=True)
    team=pd.DataFrame({'team':te.team_abbr,'delta':(te.future_speed-pp['conventional_without_state'])**2-(te.future_speed-pp['conventional_with_state'])**2,'weight':A.weights(te)})
    # Ratio bootstrap keeps equal original player weights within sampled team clusters.
    team['weighted_delta']=team.delta*team.weight;agg=team.groupby('team')[['weighted_delta','weight']].sum();ix=rng.integers(0,len(agg),(5000,len(agg)));num=agg.weighted_delta.to_numpy()[ix].sum(axis=1);den=agg.weight.to_numpy()[ix].sum(axis=1)
    subsets={}
    for label,mask in [('man',te.team_coverage_man_zone.eq('MAN_COVERAGE')),('zone',te.team_coverage_man_zone.eq('ZONE_COVERAGE'))]:
        if mask.any():subsets[label]=O.interval(te[mask],pp['conventional_without_state'][mask],pp['conventional_with_state'][mask],'future_speed')
    attempts=pd.read_pickle(out/'private_attempts.pkl');repeated=[]
    for _,g in attempts.sort_values('event_id').groupby('nfl_id'):
        if len(g)>=2:repeated.append((g.iloc[0],g.iloc[-1]))
    from scipy.stats import spearmanr
    repeatability={c:float(spearmanr([a[c] for a,b in repeated],[b[c] for a,b in repeated]).statistic) for c in ['motion__order2_V','motion__order2_tau','motion__speed_1.5','motion__speed_3']}
    diagnostic={'status':'completed_reconstructed_actual_data','kinematic_baselines_2025_mse':controls,'training_profile_shuffles':{'mse':shuffles,'mean_mse':float(np.mean(shuffles)),'real_profile_mse':results['exploratory_2025']['mse']['target_motion_with_state'],'scope':'Selected configuration fixed, training source profiles shuffled within class; held-out labels do not select settings. Diagnostic, not a reselection-based permutation p-value.'},'state_channel_team_cluster_ci95':np.quantile(num/den,[.025,.975]).tolist(),'team_clusters':len(agg),'coverage_subsets':subsets,'source_first_last_rank_correlation':repeatability,'repeat_players':len(repeated),'repeatability_scope':'Descriptive across all Combine classes, not used to select the model; alignment, effort and preprocessing contribute.'}
    (out/'diagnostics.json').write_text(json.dumps(diagnostic,indent=2));return diagnostic
if __name__=='__main__':run(Path(__file__).parent/'private_observability')
