"""Post-primary diagnostics; cannot be used to choose a new winning test model."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import analysis as A
def run_checks(data,out):
    data=Path(data);out=Path(out);d=pd.read_csv(out/'private_analysis_rows.csv');audit=json.loads((out/'population_audit.json').read_text());report=json.loads((out/'experiment_results.json').read_text());drill=audit['selected_drill']
    tracks=pd.read_csv(data/'combine_tracking.csv');tracks=tracks[tracks.entity_type.eq('PLAYER')&tracks.drill_name.eq(drill)&tracks.nfl_id.isin(d.nfl_id)]
    results=[]
    for window in (5,7,9):
     f=[]
     for key,g in tracks.groupby(['nfl_id','draft_year','event_id']):
      try:
       row,_=A.movement(g,window);f.append(dict(nfl_id=key[0],draft_year=key[1],**row))
      except ValueError:pass
     agg=pd.DataFrame(f).groupby(['nfl_id','draft_year'])[A.MOTION].median().reset_index();z=d.drop(columns=A.MOTION).merge(agg,on=['nfl_id','draft_year'],validate='many_to_one')
     if len(z)!=len(d):raise ValueError('smoothing changed population; do not silently change comparison')
     dev=z[z.draft_year.isin([2023,2024])];test=z[z.draft_year.eq(2025)];m=A.model(dev,A.BASE+A.CONTEXT+A.MOTION,'ridge',report['selection']['ridge_tracking']['alpha']);m.fit(dev,dev.separation_at_pass_forward,reg__sample_weight=A.weights(dev));mse=A.score(test,m.predict(test));results.append({'smoothing_frames':window,'test_mse':mse,'test_rmse_yards':mse**.5,'delta_vs_primary_baseline':report['results'][0]['test_player_balanced_mse']-mse})
    # Player-block permutation in development cohorts only; labels, context and conventional predictors fixed.
    # Evaluate on the original locked test without selecting a model from the resulting distribution.
    dev=d[d.draft_year.isin([2023,2024])].copy();test=d[d.draft_year.eq(2025)];rng=np.random.default_rng(A.SEED);null=[]
    for rep in range(30):
     z=dev.copy()
     for year in (2023,2024):
      mask=z.draft_year.eq(year);by=z.loc[mask].groupby('nfl_id')[A.MOTION].first();values=by.to_numpy()[rng.permutation(len(by))]
      shuffled=pd.DataFrame(values,index=by.index,columns=A.MOTION)
      for c in A.MOTION:z.loc[mask,c]=z.loc[mask,'nfl_id'].map(shuffled[c])
     m=A.model(z,A.BASE+A.CONTEXT+A.MOTION,'ridge',report['selection']['ridge_tracking']['alpha']);m.fit(z,z.separation_at_pass_forward,reg__sample_weight=A.weights(z));null.append(A.score(test,m.predict(test)))
    # Calibration by player means, fit solely to test predictions as descriptive diagnostics.
    p=pd.read_csv(out/'private_test_predictions.csv');q=test.merge(p,on=['nfl_id','game_id','play_id'],validate='one_to_one')
    cal={}
    for name in ('ridge_conventional','ridge_tracking','forest_conventional','forest_tracking'):
     by=q.groupby('nfl_id')[[name,'separation_at_pass_forward']].mean();v=by[name].to_numpy();y=by.separation_at_pass_forward.to_numpy();slope=float(np.cov(v,y,ddof=0)[0,1]/np.var(v)) if np.var(v)>0 else None
     cal[name]={'player_mean_prediction_bias_yards':float(np.mean(v-y)),'player_mean_rmse_yards':float(np.sqrt(np.mean((v-y)**2))),'descriptive_calibration_slope':slope}
    summary={'status':'actual_data_post_primary_diagnostics','test_reuse_disclosed':True,'smoothing_sensitivity':results,'development_player_block_permutation':{'repetitions':30,'test_mse_values':null,'mean_test_mse':float(np.mean(null)),'scope':'diagnostic only; not a null-test p-value or model-selection criterion'},'player_mean_calibration':cal}
    (out/'followup_checks.json').write_text(json.dumps(summary,indent=2));return summary

if __name__=='__main__':
    root=Path(__file__).parent
    print(json.dumps(run_checks(root/'data',root/'private_results'),indent=2))
