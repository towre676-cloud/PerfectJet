import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from test_analysis import trajectory
import mechanism as M

class MechanismTests(unittest.TestCase):
    def test_rigid_and_reflection_invariance(self):
        g=trajectory();f,diag=M.trajectory(g)
        self.assertEqual(diag['q'].shape,(31,2))
        h=g.copy();h[['x','y']]=g[['x','y']].to_numpy()@np.array([[0,1],[1,0]])+40
        f2,_=M.trajectory(h)
        for k in f:self.assertAlmostEqual(f[k],f2[k],places=7,msg=k)
    def test_reject_gap(self):
        with self.assertRaises(ValueError):M.trajectory(trajectory().drop(index=25))
    def test_crossfit_rejects_overlap(self):
        import pandas as pd
        d=pd.DataFrame({'nfl_id':[1]})
        with self.assertRaises(AssertionError):M.crossfit(d,d,1)
    def test_player_partitions_change_and_keep_routes_together(self):
        import pandas as pd
        d=pd.DataFrame([{'nfl_id':i,'draft_year':2023+i%2} for i in range(30) for j in range(i+1)])
        folds=list(M.player_splits(d,3,1));other=list(M.player_splits(d,3,2))
        self.assertFalse(np.array_equal(folds[0][1],other[0][1]))
        for a,b in folds:self.assertFalse(set(d.iloc[a].nfl_id)&set(d.iloc[b].nfl_id))
