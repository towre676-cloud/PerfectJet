import unittest
import numpy as np,pandas as pd
import turn_transfer as T,post_release_transfer as P,repo_predict as R
from test_turn_transfer import example

class FollowupTests(unittest.TestCase):
    def test_same_anchor_extended_response(self):
        g=example();anchor,_=T.first_turn(g);c=int(round(anchor['cut_time']/.1));short=g.iloc[:c+4];old,_=T.first_turn(short);extended,_=P.measure(g,pd.Series(old))
        self.assertFalse(old['complete_half_second']);self.assertTrue(extended['complete_half_second']);self.assertEqual(old['cut_time'],extended['cut_time']);self.assertEqual(old['entry'],extended['entry']);self.assertTrue(np.isfinite(extended['burden']))
    def test_source_fit_excludes_test_players(self):
        rng=np.random.default_rng(313);n=20;d=pd.DataFrame({'nfl_id':np.arange(n),'route_ran':['IN']*n})
        for c in set(R.PHYS+R.NUM+T.GAME):d[c]=rng.normal(size=n)
        for c in R.CAT:
            if c!='route_ran':d[c]='A'
        source=pd.DataFrame({'nfl_id':np.arange(n),'route_ran':['IN']*n,'entry':rng.uniform(3,7,n),'angle':rng.uniform(.6,2,n),'impulse':rng.uniform(3,8,n)})
        for c in T.STYLE:source[c]=rng.normal(size=n)
        tr=d.iloc[:15];enc=T.TurnEncoder(source,'execution').fit(tr);self.assertEqual(enc.source_fit_ids_,set(tr.nfl_id))
        changed=source.copy();changed.loc[changed.nfl_id.ge(15),T.STYLE]=1e9;other=T.TurnEncoder(changed,'execution').fit(tr);np.testing.assert_allclose(enc.transform(tr),other.transform(tr),atol=1e-12)
    def test_response_cannot_move_anchor(self):
        g=example();anchor,_=T.first_turn(g);a,_=P.measure(g,pd.Series(anchor));g.loc[g.index>int(round(a['cut_time']/.1)),['x','y']]+=200;b,_=P.measure(g,pd.Series(anchor));self.assertEqual(a['cut_time'],b['cut_time']);self.assertEqual(a['angle'],b['angle'])

if __name__=='__main__':unittest.main()
