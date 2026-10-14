import unittest
import numpy as np
import pandas as pd
import observability as O
import repo_predict as R
from mechanism import player_splits

class ObservabilityTests(unittest.TestCase):
    def test_splits_keep_players_intact(self):
        d=pd.DataFrame({'nfl_id':np.repeat(np.arange(24),3),'draft_year':np.repeat([2023]*12+[2024]*12,3)})
        held=[]
        for a,b in player_splits(d,4,13):
            self.assertFalse(set(d.iloc[a].nfl_id)&set(d.iloc[b].nfl_id));held.extend(d.iloc[b].nfl_id.unique())
        self.assertEqual(sorted(held),list(range(24)))
    def test_nonlinear_response_limits(self):
        for order in [1,2]:
            s=O.response(np.array([-1.,0.,1.,100.]),12,1,0,order)
            self.assertEqual(s[0],0);self.assertEqual(s[1],0);self.assertAlmostEqual(s[-1],12)
            self.assertTrue(np.all(np.diff(s)>=0))
    def test_duplicate_timestamps_rejected(self):
        g=pd.DataFrame({'time':['2023-01-01T00:00:00Z']*31,'s':np.ones(31),'x':np.arange(31),'y':np.zeros(31)})
        with self.assertRaises(ValueError):O.sprint_features(g)
    def test_player_overlap_rejected_before_fit(self):
        d=pd.DataFrame({'nfl_id':[1]})
        with self.assertRaises(ValueError):O.fit_predict(d,d,'future_speed','conventional',True,R.CONFIGS[0],10)
    def test_player_balanced_loss(self):
        d=pd.DataFrame({'nfl_id':[1,1,1,2],'future_speed':[0,0,0,2]})
        self.assertAlmostEqual(O.score(d,np.zeros(4),'future_speed'),2)
    def test_motion_encoder_ignores_future_fields(self):
        rng=np.random.default_rng(12);n=24
        d=pd.DataFrame({'nfl_id':np.arange(n),'draft_year':[2023]*12+[2024]*12})
        for c in set(R.PHYS+R.NUM+O.PREFIX):d[c]=rng.normal(size=n)
        for c in R.CAT:d[c]='A'
        for c in range(6):d[f'motion__test{c}']=rng.normal(size=n)
        d['future_speed']=rng.normal(size=n);d['speed_gain']=rng.normal(size=n)
        for family in ['conventional','pca_motion','target_motion']:
            enc=O.Encoder(family,True,4,15).fit(d,d.future_speed);before=enc.transform(d)
            changed=d.copy();changed['future_speed']=1e8;changed['speed_gain']=-1e8
            np.testing.assert_allclose(before,enc.transform(changed))
            self.assertEqual(enc.fit_ids_,set(d.nfl_id))

if __name__=='__main__':unittest.main()
