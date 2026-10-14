"""Exact identifiability and minimum extra measurements for a supplied surrogate.

This is an illustrative linear-in-parameters quadratic response model, not a
certification that athlete biomechanics follow it. It deliberately pools routes;
route-specific intent would require further parameters. Noise remains separate.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import json
import numpy as np,pandas as pd
from vendor.pp import exact_linear as E

def row(speed,angle):
    u=Q(int(round(float(speed)*10)),80);v=Q(int(round(float(angle)*180/np.pi)),90)
    return (Q(1),u,v,u*v,u*u,v*v)

def run(out):
    out=Path(out);source=pd.read_pickle(out/'private_source.pkl');games=pd.read_pickle(out/'private_rows.pkl');candidates=[(s,a) for s in [3.,4.5,6.,7.5] for a in [30.,60.,90.,120.]];candidate_rows=[row(s,np.deg2rad(a)) for s,a in candidates];rankhist={};neededhist={};records=[];ambiguous=0;fullrank=0;improvement=[]
    for player,g in games.groupby('nfl_id',sort=True):
        s=source[source.nfl_id.eq(player)];S=tuple(row(a.entry,a.angle) for a in s.itertuples());G=tuple(dict.fromkeys(row(a.game_entry,a.game_angle) for a in g.itertuples()))
        if not S:continue
        r=E.rank(S);rankhist[str(r)]=rankhist.get(str(r),0)+1;need=6-r;neededhist[str(need)]=neededhist.get(str(need),0)+1;factor=E.target_factor(S,G);ambiguous+=factor['status']=='AMBIGUOUS';fullrank+=r==6
        if factor['status']=='AMBIGUOUS':
            witness=factor['invisible_vector'];assert all(v==0 for v in E.apply(S,witness));assert any(v!=0 for v in E.apply(G,witness))
        sf=np.array(S,float);gf=np.array(G,float);best=None
        # Rank lower bound: one scalar measurement can raise rank by at most one.
        # Search only subsets meeting that minimum, optimizing noise amplification.
        for indices in combinations(range(len(candidates)),need):
            expanded=np.r_[sf,np.array([candidate_rows[i] for i in indices],float).reshape(-1,6)]
            if np.linalg.matrix_rank(expanded)<6:continue
            covariance=np.linalg.inv(expanded.T@expanded);amplification=float(np.einsum('ij,jk,ik->i',gf,covariance,gf).mean())
            if best is None or amplification<best[0]:best=(amplification,indices)
        if best is None:raise ValueError('Candidate grid cannot complete supplied model.')
        extended=S+tuple(candidate_rows[i] for i in best[1]);assert E.rank(extended)==6;assert E.target_factor(extended,G)['status']=='EXACT_TARGET_FACTOR'
        records.append({'nfl_id':int(player),'source_rank':r,'minimum_additional_scalar_measurements':need,'selected_conditions':[[candidates[i][0],candidates[i][1]] for i in best[1]],'unit_noise_average_target_variance':best[0],'condition_number_after':float(np.linalg.cond(np.array(extended,float)))})
    pd.DataFrame(records).to_pickle(out/'private_observability_plans.pkl');result={'status':'completed_exact_surrogate_design','model':'B(v,angle)=beta0+beta1*u+beta2*w+beta3*u*w+beta4*u^2+beta5*w^2; u=v/8,w=angle_degrees/90; speeds quantized 0.1 yd/s, angles 1 degree','players_with_source_and_game_demands':len(records),'source_design_rank_histogram':rankhist,'minimum_additional_measurement_histogram':neededhist,'ambiguous_NFL_target_maps':int(ambiguous),'full_rank_source_designs':int(fullrank),'after_selected_measurements_exact_target_factor':len(records),'candidate_conditions':{'speed_yd_per_s':[3,4.5,6,7.5],'angle_degrees':[30,60,90,120]},'optimality_scope':'Minimum cardinality for full six-parameter model by rank lower bound and exact completion; numerical noise criterion selects among minimum-cardinality candidate subsets. It is not an optimal biomechanical training program.','noise_scope':'Unit independent observation-noise model only; actual sensor noise and model misspecification not estimated by these algebraic calculations.','trust_boundary':'Exact rational statements hold for supplied quantized design matrices and chosen quadratic surrogate. Actual athletes need not follow this model. Pooling route intent is deliberately optimistic. No real-world predictive gain or causal intervention benefit inferred.'};(out/'observability_design.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':run(Path(__file__).parent/'private_post_release')
