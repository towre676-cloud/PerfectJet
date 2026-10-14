"""Source repeatability, observational floors and exact small trial-design plans."""
from pathlib import Path
import json,itertools
from fractions import Fraction as Q
import numpy as np,pandas as pd
from scipy.stats import spearmanr
import stress_features as S,stress_transfer as T
from dynacomp.rational import rref,nullspace

def phi(speed,angle):
    s,a=Q(str(round(float(speed),1))),Q(str(round(float(angle),1)));return (Q(1),s,a,s*a)

def rank(rows):return len(rref(rows)[1])

def minimum_plan(rows):
    choices=[phi(s,a) for s in [2.5,3.5,4.5] for a in [.8,1.6,2.4]];costs=[1+(i//3==2) for i in range(9)];best=None;winners=[]
    for mask in range(512):
        selected=[i for i in range(9) if mask>>i&1];cost=sum(costs[i] for i in selected)
        if best is not None and cost>best:continue
        if rank(rows+[choices[i] for i in selected])==4:
            if best is None or cost<best:best=cost;winners=[selected]
            elif cost==best:winners.append(selected)
    return {'minimum_declared_cost':best,'optimal_plan_count':len(winners),'one_plan':[{'speed_yd_s':float(choices[i][1]),'angle_rad':float(choices[i][2]),'cost':costs[i]} for i in winners[0]],'complete_plan_population':512,'scope':'Exact finite candidate-design enumeration for declared bilinear response model. Cost1 per candidate trial, cost2 at4.5yd/s, chosen illustrative workload. Does not establish physiological feasibility or NFL value.'}

def run():
    out=Path('receipts/stress');out.mkdir(exist_ok=True);old=pd.read_pickle('private_stress/private_turns.pkl');turns=pd.read_pickle('private_stress_clock/private_turns.pkl');d=pd.read_pickle('private_stress_clock/private_rows.pkl');units=T.unit_rows(d).merge(pd.read_pickle('private_stress_clock/private_capacity.pkl'),on='nfl_id',how='left');train=units[units.draft_year.isin([2023,2024])];encoder=S.StressEncoder(turns).fit(train);profiles=encoder.transform(units);events=turns.copy();p=encoder.model.predict(encoder.scale.transform(encoder._unscaled(events,units)));events['adjusted_recovery']=events.eta-p[:,0];repeat={}
    for drill,g in events.groupby('drill'):
        attempt=g.groupby(['nfl_id','event_id'])[['eta','adjusted_recovery']].mean().reset_index();pairs=[a.sort_values('event_id').iloc[:2] for _,a in attempt.groupby('nfl_id') if len(a)>=2]
        if len(pairs)>=5:
            first=pd.DataFrame([p.iloc[0] for p in pairs]);second=pd.DataFrame([p.iloc[1] for p in pairs]);repeat[drill]={'paired_players':len(pairs),'raw_recovery_spearman':float(spearmanr(first.eta,second.eta).statistic),'demand_adjusted_spearman':float(spearmanr(first.adjusted_recovery,second.adjusted_recovery).statistic)}
    z=old[['nfl_id','event_id','center','eta_width']].merge(turns[['nfl_id','event_id','center','eta_width']],on=['nfl_id','event_id','center'],suffixes=('_initial','_clock'));oldmedian=float(z.eta_width_initial.median());newmedian=float(z.eta_width_clock.median());measurement={'matched_turns':len(z),'initial_median_width':oldmedian,'clock_median_width':newmedian,'median_width_reduction':1-newmedian/oldmedian,'repeatability':repeat,'scope':'Branches are processing/clock scenarios, not a sensor-error posterior. Repeats can differ in drill demands; source adjustment fitted on earlier45players only.'};(out/'measurement.json').write_text(json.dumps(measurement,indent=2))
    floors=[];plans=[]
    for (player,drill),g in turns.groupby(['nfl_id','drill']):
        rows=[phi(s,a) for s,a in zip(g.entry,g.angle)];r=rank(rows);null=nullspace(rows);h=phi(4,1.6);blind=any(sum(x*y for x,y in zip(h,v)) for v in null)
        speed=g.entry.to_numpy();angle=g.angle.to_numpy();numeric_rank=int(np.linalg.matrix_rank(np.c_[np.ones(len(g)),speed,angle,speed*angle]))
        floors.append({'drill':drill,'turns':len(g),'rank':r,'numeric_rank':numeric_rank,'target_blind':bool(blind)})
        if r<4 and len(plans)<12:plans.append({'drill':drill,'observed_rank':r,**minimum_plan(rows)})
    f=pd.DataFrame(floors);observability={'player_drill_panels':len(f),'rank_counts':{str(k):int(v) for k,v in f['rank'].value_counts().sort_index().items()},'unrounded_numeric_rank_counts':{str(k):int(v) for k,v in f.numeric_rank.value_counts().sort_index().items()},'unrounded_numeric_fraction_not_full_rank':float(f.numeric_rank.lt(4).mean()),'fraction_not_full_rank':float(f['rank'].lt(4).mean()),'fraction_reference_target_not_identified':float(f.target_blind.mean()),'by_drill':{name:{'panels':len(g),'not_full_rank_fraction':float(g['rank'].lt(4).mean()),'reference_blind_fraction':float(g.target_blind.mean())} for name,g in f.groupby('drill')},'reference_demand':{'speed':4,'angle_rad':1.6},'minimum_plans':plans,'scope':'Exact rational rank/nullspace on entry speed andangle rounded0.1. Bilinear coefficients1,s,angle,s*angle. Blind target means alternative coefficient vectors fit those design rows but differ at reference demand. No claim about noise calibration or all nonlinear athlete models. Priors/regularization can choose a curve but do not make it data-identified.'};(out/'observability.json').write_text(json.dumps(observability,indent=2))
    flips={};meta=units.set_index('nfl_id');profiles=profiles.set_index('nfl_id')
    for drill in S.F.DRILLS:
        lower='stress__'+drill+'__lower';upper='stress__'+drill+'__upper';eta='stress__'+drill+'__eta_r';pairs=0;stable=0
        ids=profiles.index[profiles[lower].notna()]
        for a,b in itertools.combinations(ids,2):
            x,y=meta.loc[a],meta.loc[b]
            if x.combine_position!=y.combine_position or not np.isfinite([x.forty,y.forty,x.combine_weight,y.combine_weight]).all() or abs(x.forty-y.forty)>.1 or abs(x.combine_weight-y.combine_weight)>20:continue
            pairs+=1;stable+=bool(profiles.loc[a,lower]>profiles.loc[b,upper] or profiles.loc[b,lower]>profiles.loc[a,upper])
        flips[drill]={'matched_pairs':pairs,'disjoint_branch_intervals':stable,'fraction_ambiguous':1-stable/pairs if pairs else None}
    (out/'rank_ambiguity.json').write_text(json.dumps({'drills':flips,'scope':'Same Combine position,forty within0.10s andweight within20lb. Adjusted-recovery branch intervals under earlier-trained source reference. Overlap is sensitivity ambiguity, not probability of misranking or evidence of NFL talent.'},indent=2))
    annotation=[]
    for row in turns.itertuples():
        b=pd.DataFrame(row.branches);full=b.eta.max()-b.eta.min();center=max(g.eta.max()-g.eta.min() for _,g in b.groupby('shift'));smoothing=max(g.eta.max()-g.eta.min() for _,g in b.groupby('window'));annotation.append({'drill':row.drill,'full':full,'center_resolved':center,'smoothing_resolved':smoothing})
    ann=pd.DataFrame(annotation);(out/'annotation_value.json').write_text(json.dumps({'by_drill':ann.groupby('drill').median().to_dict(),'scope':'Hypothetical worst-case remaining recovery range after revealing a declared center/smoothing branch. Not a measured annotation benefit or physiological sensor probability.'},indent=2))
    S.finite_audit(turns,out);return measurement,observability
if __name__=='__main__':
    m,o=run();print(json.dumps(m,indent=2));print(json.dumps({k:v for k,v in o.items() if k!='minimum_plans'},indent=2))
