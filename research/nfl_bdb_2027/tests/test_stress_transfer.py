import unittest,tempfile
from unittest.mock import patch
import numpy as np,pandas as pd
import stress_transfer as T,front_transfer as F,repo_predict as R
from stress_diagnostics import phi,rank,minimum_plan
class StressTransferTests(unittest.TestCase):
    def rows(self):
        rng=np.random.default_rng(29);ids=np.repeat(np.arange(12),20);n=len(ids);d=pd.DataFrame({c:rng.normal(size=n) for c in F.NUM+R.PHYS});d['nfl_id']=ids;d['draft_year']=np.where(ids<5,2023,np.where(ids<10,2024,2025));d['combine_position']='DE';d['game_id']=1;d['play_id']=np.arange(n);d['pressure_event']=rng.integers(0,2,n).astype(float)
        for c in F.CAT:d[c]='A'
        return d
    def test_test_labels_cannot_construct_training_targets(self):
        d=self.rows();tr=d[d.nfl_id<10].reset_index(drop=True);te=d[d.nfl_id>=10].reset_index(drop=True);original=T.context_predict
        with tempfile.TemporaryDirectory() as folder,patch.object(T,'context_predict',side_effect=lambda a,b,c:original(a,b,c,cache=folder)):
            u,v=T.targets(tr,te,'pressure_event');altered=te.copy();altered.pressure_event=1-altered.pressure_event;u2,v2=T.targets(tr,altered,'pressure_event');np.testing.assert_array_equal(u.target,u2.target)
    def test_context_and_scouting_overlap_rejected(self):
        d=self.rows()
        with self.assertRaises(ValueError):T.context_predict(d,d,'pressure_event')
        u=T.unit_rows(d);u['target']=0
        with self.assertRaises(ValueError):T.predict(u,u,'conventional',10)
    def test_demand_rank_and_complete_plan(self):
        rows=[phi(3,1)];self.assertEqual(rank(rows),1);plan=minimum_plan(rows);self.assertEqual(plan['minimum_declared_cost'],3);self.assertGreater(plan['optimal_plan_count'],0)
if __name__=='__main__':unittest.main()
