"""Strong-reference YAC correction; raw sensor gains must beat provided expected YAC.

This follow-up is exploratory after initial YAC test inspection. Every family
gets the same zero-correction option in addition to the five candidate models.
"""
from pathlib import Path
import json
import numpy as np,pandas as pd
import turn_transfer as T,repo_predict as R
from mechanism import player_splits

def cohort(out):
    d=pd.read_pickle(Path(out)/'private_rows.pkl');q=d[d.target.eq(True)&np.isfinite(d.yards_after_catch)&np.isfinite(d.expected_yards_after_catch)].copy();n=q.groupby('nfl_id').size();q=q[q.nfl_id.isin(n[n>=3].index)].reset_index(drop=True);q['yac_residual']=q.yards_after_catch-q.expected_yards_after_catch;return q

def prediction(tr,te,source,family,ci):
    if ci==5:return np.zeros(len(te))
    return T.fit_predict(tr,te,source,family,R.CONFIGS[ci],'yac_residual')

def run(out):
    out=Path(out);q=cohort(out);source=pd.read_pickle(out/'private_source.pkl');dest=out/'yac_reference';dest.mkdir(exist_ok=True);audit={'players_by_year':{str(k):int(v) for k,v in q.groupby('draft_year').nfl_id.nunique().items()},'catches_by_year':{str(k):int(v) for k,v in q.groupby('draft_year').size().items()},'eligibility':'>=3 targeted catches per player with measured YAC and finite supplied expected YAC'}
    if min(q.groupby('draft_year').nfl_id.nunique().reindex([2023,2024,2025],fill_value=0))<10:
        r={'status':'complete_reference_population_feasibility_failure','population':audit};(dest/'results.json').write_text(json.dumps(r,indent=2));return r
    dev=q[q.draft_year.isin([2023,2024])].reset_index(drop=True);test=q[q.draft_year.eq(2025)].reset_index(drop=True);families=['conventional','source_demands','execution'];pred={k:np.zeros(len(dev)) for k in families};tp={};folds=[];selection=[];old=R.NUM
    try:
        R.NUM=old+['pass_length','expected_yards_after_catch']
        for fold,(a,b) in enumerate(player_splits(dev,4,T.SEED)):
            tr=dev.iloc[a].reset_index(drop=True);te=dev.iloc[b]
            for family in families:
                loss=[]
                for ci in range(6):
                    values=[T.score(tr.iloc[j],prediction(tr.iloc[i],tr.iloc[j],source,family,ci),'yac_residual') for i,j in player_splits(tr,3,T.SEED+1+fold)];loss.append(float(np.mean(values)))
                ci=int(np.argmin(loss));pred[family][b]=prediction(tr,te,source,family,ci);folds.append({'fold':fold,'family':family,'config':ci,'inner_mse':loss});print('Expected-YAC correction',fold,family,ci,flush=True)
        tr=dev[dev.draft_year.eq(2023)];va=dev[dev.draft_year.eq(2024)]
        for family in families:
            loss=[T.score(va,prediction(tr,va,source,family,ci),'yac_residual') for ci in range(6)];ci=int(np.argmin(loss));tp[family]=prediction(dev,test,source,family,ci);selection.append({'family':family,'config':ci,'validation_mse':loss})
            pd.DataFrame({'nfl_id':test.nfl_id,'game_id':test.game_id,'play_id':test.play_id,'truth':test.yards_after_catch,'prediction':test.expected_yards_after_catch+tp[family]}).to_pickle(dest/f'private_forward_{family}.pkl')
        r={'status':'completed_actual_data_reference_correction','population':audit,'prior_YAC_2025_inspection':True,'candidate_budget':'Same five fitted candidates plus zero correction; selection may retain supplied reference unchanged','folds':folds,'selection':selection}
        for key,rows,pp in [('nested',dev,pred),('exploratory_2025',test,tp)]:r[key]={'mse':{'provided_expected_YAC':T.score(rows,np.zeros(len(rows)),'yac_residual'),**{k:T.score(rows,p,'yac_residual') for k,p in pp.items()}},'execution_vs_source_demands':T.interval(rows,pp['source_demands'],pp['execution'],'yac_residual'),'execution_vs_reference':T.interval(rows,np.zeros(len(rows)),pp['execution'],'yac_residual'),'execution_vs_conventional':T.interval(rows,pp['conventional'],pp['execution'],'yac_residual')}
        (dest/'results.json').write_text(json.dumps(r,indent=2));return r
    finally:R.NUM=old
if __name__=='__main__':run(Path(__file__).parent/'private_post_release')
