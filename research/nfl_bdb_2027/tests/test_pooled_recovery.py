import unittest
import numpy as np
import pandas as pd
import front_transfer as F
import repo_predict as R
from pooled_recovery import PooledRecovery
class PoolingTests(unittest.TestCase):
    def fixture(self):
        rng=np.random.default_rng(32);units=pd.DataFrame({'nfl_id':np.arange(12),'target':rng.normal(size=12)})
        for c in R.PHYS:units[c]=rng.normal(size=12)
        rows=[]
        for player in range(12):
            for drill in F.DRILLS:
                for event in range(3):
                    speed=2+rng.random()*3;angle=.6+rng.random()
                    rows.append({'nfl_id':player,'event_id':event,'center':12,'drill':drill,'entry':speed,'angle':angle,'eta':.4+.07*speed-.1*angle+.02*player,'retention':.8,'late_gain':.2,'eta_width':.1})
        return units,pd.DataFrame(rows)
    def test_held_players_and_nfl_labels_do_not_change_fit(self):
        u,t=self.fixture();a=u.iloc[:9];held=u.iloc[9:]
        m=PooledRecovery(t).fit(a);p=m.transform(a)
        altered=t.copy();altered.loc[altered.nfl_id.isin(held.nfl_id),'eta']+=100
        a=a.copy();a.target+=100
        n=PooledRecovery(altered).fit(a)
        np.testing.assert_allclose(p.select_dtypes('number'),n.transform(a).select_dtypes('number'))
    def test_more_shrinkage_reduces_coefficient_norm(self):
        u,t=self.fixture();m=PooledRecovery(t,1).fit(u.iloc[:9]);p=m.transform(u.iloc[9:]);cols=[c for c in p if '__b' in c]
        m.penalty=100;q=m.transform(u.iloc[9:])
        self.assertLess(np.linalg.norm(q[cols]),np.linalg.norm(p[cols]))
    def test_duplicate_turns_do_not_multiply_attempt_weight(self):
        u,t=self.fixture();m=PooledRecovery(t).fit(u.iloc[:9]);p=m.transform(u.iloc[9:]);extra=t[t.nfl_id.ge(9)].copy();extra.center+=1
        m.turns=pd.concat([t,extra],ignore_index=True);q=m.transform(u.iloc[9:])
        np.testing.assert_allclose(p.select_dtypes('number'),q.select_dtypes('number'),atol=1e-12)
if __name__=='__main__':unittest.main()
