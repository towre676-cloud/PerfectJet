"""Source-only alignment adaptation: sustained athletic onset instead of setup."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import front_transfer as F

def prepare(data,out):
    out=Path(out);out.mkdir(exist_ok=True);d=pd.read_pickle('private_front/private_rows.pkl');tr=pd.read_csv(Path(data)/'combine_tracking.csv');tr=tr[tr.entity_type.eq('PLAYER')&tr.nfl_id.isin(d.nfl_id)&tr.drill_name.isin(F.DRILLS)];rows=[];rejected={};audit=[]
    for key,g in tr.groupby(['nfl_id','draft_year','event_id'],sort=True):
        try:features=F.skill_features(g,onset_speed=2)
        except ValueError as e:rejected[str(e)]=rejected.get(str(e),0)+1;continue
        rows.append(dict(nfl_id=key[0],draft_year=key[1],event_id=key[2],drill_name=g.drill_name.iloc[0],**features));old=F.skill_features(g,.5);audit.append({'drill':g.drill_name.iloc[0],'old_speed_10':old['speed_10'],'new_speed_10':features['speed_10']})
    sk=pd.DataFrame(rows);values=[c for c in sk if c not in ['nfl_id','draft_year','event_id','drill_name']];wide=sk.groupby(['nfl_id','draft_year','drill_name'])[values].median().unstack('drill_name');wide.columns=['skill__'+drill+'__'+name for name,drill in wide.columns];cols=[c for c in d if c.startswith(('skill__','motion__'))];d=d.drop(columns=[c for c in d if c.startswith('skill__')]).merge(wide.reset_index(),on=['nfl_id','draft_year'],how='left',validate='many_to_one');d.to_pickle(out/'private_rows.pkl');sk.to_pickle(out/'private_skills.pkl');r={'onset_rule':'First three consecutive observed speeds above2yd/s; first5s thereafter. Source-only threshold revision after onset audit. Still an operational rule, not labeled official cue or whole-drill semantic segmentation.','same_NFL_cohort_as_initial':True,'athletic_source_attempts_in_NFL_cohort':len(sk),'rejections':rejected,'one_second_speed_comparison_by_drill':pd.DataFrame(audit).groupby('drill').median().to_dict(),'metric':'Player pressure-rate selection on earlier classes, baseline includes revised source availability','adaptive_after_prior_forward_inspection':True};(out/'population.json').write_text(json.dumps(r,indent=2));return d,cols,r

if __name__=='__main__':
    d,cols,r=prepare('data','private_front_bouts');F.experiment(d,cols,'private_front_bouts','pressure_event',objective='player')
