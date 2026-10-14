"""Synthetic software checks only. Never used to infer NFL predictive improvement."""
from pathlib import Path
import json,sys,platform
import numpy as np,pandas as pd
import analysis as A
sys.path.insert(0,str(Path(__file__).parent/'tests'))
from test_analysis import trajectory
out=Path(__file__).parent/'receipts';out.mkdir(exist_ok=True)
f,diag=A.movement(trajectory());A.plot_motion(diag,out/'synthetic_geometry.png','SYNTHETIC SOFTWARE DEMONSTRATION · no NFL observations')
rng=np.random.default_rng(A.SEED);rows=[]
# No injected relationship between motion and outcomes. Full pipeline exercises a null fixture.
for year in (2023,2024,2025):
 for j in range(12):
  phys={k:float(rng.normal()) for k in A.BASE};phys['combine_weight']=float(rng.uniform(160,230));motion={k:float(rng.normal()) for k in A.MOTION}
  for play in range(24):
   context={k:float(rng.normal()) for k in A.CONTEXT}
   rows.append(dict(nfl_id=year*100+j,draft_year=year,season=year,game_id=year*10000+j,play_id=play,
     separation_at_pass_forward=3+.1*phys['forty']+rng.normal(0,.8),route_ran='OUT',team_coverage_man_zone='MAN_COVERAGE' if play%2 else 'ZONE_COVERAGE',offense_formation='SHOTGUN',in_motion_at_ball_snap=bool(play%3),ngs_college_production_score=float(rng.normal()),**phys,**motion,**context))
(out/'synthetic_geometry.html').write_text(A.motion_html(diag,'SYNTHETIC SOFTWARE DEMONSTRATION — no NFL observations'))
r=A.compare(pd.DataFrame(rows),out/'synthetic_null')
r['status']='synthetic_software_check_only';r['disclaimer']='Artificial random data; every score and CI is a software fixture, not an NFL finding.'
(out/'synthetic_null'/'experiment_results.json').write_text(json.dumps(r,indent=2))
(out/'software_validation.json').write_text(json.dumps({'status':'synthetic_software_check_only','motion_fixture':f,'null_fixture':r,'python':platform.python_version()},indent=2))
print(json.dumps({'status':r['status'],'players':36,'routes':864,'primary_null_fixture_delta':r['primary_delta_mse_yards_squared'],'ci':r['player_bootstrap_ci95']},indent=2))
