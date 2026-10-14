"""Unchanged PerfectJet exact scalar-readout tests on actual turn conditions."""
from pathlib import Path
import sys,json
from fractions import Fraction as Q
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent/'vendor/perfectjet_scouting/src'))
from perfectjet.readout import identify,value_of_information,readout_variance,posterior_covariance
def row(s,a):
    # Round raw coordinates first; construct the product in exact arithmetic.
    # Independently rationalizing floating standardized products can spoil
    # structural row dependencies. These rows never do that.
    speed=Q(int(round(s*2)),8);angle=Q(int(round(a*180/np.pi/15)),6)
    return (Q(1),speed,angle,speed*angle)
def average(rows):return tuple(sum((r[k] for r in rows),Q(0))/len(rows) for k in range(4))
def run():
    turns=pd.read_pickle('private_burst_turns/private_turns.pkl');reports=[]
    for drill in sorted(turns.drill.unique()):
        ref=turns[turns.drill.eq(drill)&turns.draft_year.lt(2025)]
        h=average([row(r.entry,r.angle) for r in ref.itertuples()])
        for player,g in turns[turns.drill.eq(drill)].groupby('nfl_id'):
            x=list(dict.fromkeys(row(r.entry,r.angle) for r in g.itertuples()));own=identify(x,average(x));foreign=identify(x,h);assert own['identified']
            if not foreign['identified']:
                witness=foreign['witness'];assert all(sum(a*b for a,b in zip(r,witness))==0 for r in x)
                assert sum(a*b for a,b in zip(h,witness))!=0
            reports.append({'drill':drill,'own_readout_identified':own['identified'],'earlier_reference_identified':foreign['identified'],'distinct_directions':len(x)})
    # Small condition bank illustrates observation repair under a stated prior;
    # it is not a calibrated sensor model or a coaching intervention benefit.
    candidates=[row(s,a*np.pi/180) for s in [2.,3.5,5.] for a in [45.,90.,135.]]
    examples=[]
    for (player,drill),g in list(turns.groupby(['nfl_id','drill']))[:12]:
        x=list(dict.fromkeys(row(r.entry,r.angle) for r in g.itertuples()));h=average([row(r.entry,r.angle) for r in turns[turns.drill.eq(drill)&turns.draft_year.lt(2025)].itertuples()]);voi=value_of_information(x,h,candidates,Q(1,20),[[Q(i==j) for j in range(4)] for i in range(4)])
        examples.append({'variance_before':float(voi['variance_before']),'best_candidate':voi['candidates'][0]['candidate'],'reduction':float(voi['candidates'][0]['reduction']),'new_direction':voi['candidates'][0]['new_direction'],'resolves_readout':voi['candidates'][0]['resolves_identification']})
    r={'panels':len(reports),'own_empirical_mean_identified':sum(x['own_readout_identified'] for x in reports),'earlier_reference_identified':sum(x['earlier_reference_identified'] for x in reports),'reports':reports,'planning_examples':examples,'scope':'Exact rational row-space claims for declared bilinear response and rounded raw coordinates. Own mean is supported by construction. Earlier-reference demand weights learned from earlier source athletes only. Planning variance assumes isotropic coefficient prior and independent noise1/20, not a fitted biological posterior. No predictive advantage follows from these algebraic identities.'}
    Path('receipts/burst/readout_support.json').write_text(json.dumps(r,indent=2));return r
if __name__=='__main__':run()
