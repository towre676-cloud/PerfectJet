"""Public, data-free replay of exact repeat-plan population mathematics."""
import argparse
import hashlib
import json
import random
import time
from pathlib import Path
from perfectjet.repeat_allocation import RepeatPlanPopulation
from perfectjet.replication_geometry import calibration_requirement, scalar_repeat_budget


def replay():
    started = time.perf_counter()
    small = RepeatPlanPopulation.build(1,1,1,1,'2.3',1,budget=12)
    # Independent exhaustive enumeration of the small rational comparison.
    from fractions import Fraction as Q
    brute = []
    for a in range(1,14):
        for b in range(1,14):
            va,vb = 1+Q(1,a+1),1+Q(1,b+1)
            d = Q(23,10)**2-va-vb
            if a+b<=14 and d>0 and d*d>4*va*vb:
                brute.append((a,b))
    assert small.count()==len(brute)==81
    assert [small.unrank(i) for i in range(small.count())]==brute
    assert [small.rank(p) for p in brute]==list(range(len(brute)))
    budget = 10**30
    large = RepeatPlanPopulation.build(1,1,1,1,'2.3',1,budget=budget)
    # The ten excluded cells are (1,1..5),(2,1..2),(3,1),(4,1),(5,1).
    assert large.count()==(budget+1)*(budget+2)//2-10
    assert large.minimum()=={'additional_cost':3,'plans':[(2,3),(3,2)]}
    rng = random.Random(141015)
    ranks = [0,1,large.count()-1]+[rng.randrange(large.count()) for _ in range(64)]
    assert all(large.rank(large.unrank(r))==r for r in ranks)
    equal = scalar_repeat_budget(1,1,'2.3',1)['repeats']
    assert equal==3
    root = Path(__file__).resolve().parents[1]
    paths = [Path(__file__).resolve(),root/'src/perfectjet/repeat_allocation.py',root/'src/perfectjet/replication_geometry.py']
    return {'schema':'perfectjet/repeat-population-replay/1',
            'example':'constructed scalar model, not football measurements',
            'model':{'signal_a':'1','noise_a':'1','signal_b':'1','noise_b':'1','gap':'23/10','radius':'1'},
            'small':small.receipt(),'large':large.receipt(),
            'large_rank_roundtrips':len(ranks),'small_exhaustive_plans':len(brute),
            'equal_replication_additional_cost':2*(equal-1),
            'optimal_asymmetric_additional_cost':large.minimum()['additional_cost'],
            'cost_reduction_in_constructed_example':0.25,
            'calibration_requirements_90':{str(k):calibration_requirement('0.1',k) for k in (1,2,29)},
            'elapsed_seconds':time.perf_counter()-started,
            'source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=replay();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
