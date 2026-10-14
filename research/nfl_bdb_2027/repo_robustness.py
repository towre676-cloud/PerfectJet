"""Team-cluster diagnostic for exploratory prediction gains."""
from pathlib import Path
import json
import pandas as pd,numpy as np
import analysis as A

def run(root,repo_out,analysis_out=None):
    root,repo_out=Path(root),Path(repo_out);analysis_out=Path(analysis_out) if analysis_out else root/'private_results';d=pd.read_csv(analysis_out/'private_analysis_rows.csv');d=d[d.draft_year.eq(2025)];p=pd.read_csv(repo_out/'private_cohort_predictions.csv');old=pd.read_csv(analysis_out/'private_test_predictions.csv');d=d.merge(p,on=['nfl_id','game_id','play_id'],validate='one_to_one').merge(old,on=['nfl_id','game_id','play_id'],validate='one_to_one')
    team=d.groupby('nfl_id').team_abbr.agg(lambda x:x.value_counts().index[0]);results={}
    for baseline in ['forest_conventional','baseline']:
        delta=(d.separation_at_pass_forward-d[baseline])**2-(d.separation_at_pass_forward-d['all'])**2
        players=pd.DataFrame({'id':d.nfl_id,'delta':delta}).groupby('id').delta.mean().to_frame();players['team']=team;groups=players.groupby('team').delta.agg(['sum','count']);rng=np.random.default_rng(A.SEED);ix=rng.integers(0,len(groups),(5000,len(groups)));s=groups['sum'].to_numpy();n=groups['count'].to_numpy();b=s[ix].sum(axis=1)/n[ix].sum(axis=1);results[baseline]={'delta_mse':float(players.delta.mean()),'team_cluster_ci95':np.quantile(b,[.025,.975]).tolist(),'teams':len(groups),'players':len(players)}
    result={'scope':'exploratory after 2025 inspection; dominant team clusters approximate dependence, not a season bootstrap','comparisons':results};(repo_out/'team_cluster_diagnostic.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
    root=Path(__file__).parent;print(json.dumps(run(root,root/'private_repo_results'),indent=2))
