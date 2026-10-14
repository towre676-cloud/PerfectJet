import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import analysis as A
import numpy as np,pandas as pd

def trajectory():
    t=np.arange(61)*.1;theta=(np.pi/2)/(1+np.exp(-(t-3)*5));speed=5-2*np.exp(-((t-3)/.4)**2)
    v=speed[:,None]*np.c_[np.cos(theta),np.sin(theta)];p=np.cumsum(v*.1,axis=0)
    return pd.DataFrame({'time':pd.Timestamp('2025-03-01',tz='UTC')+pd.to_timedelta(t,unit='s'),'x':p[:,0],'y':p[:,1]})

class MotionTests(unittest.TestCase):
    def test_rigid_invariance(self):
        g=trajectory();f,_=A.movement(g);q=g.copy();p=q[['x','y']].to_numpy();r=np.array([[0,-1],[1,0]]);q[['x','y']]=p@r+np.array([40,20]);h,_=A.movement(q)
        for k in f:self.assertAlmostEqual(f[k],h[k],places=8)
    def test_reflection(self):
        g=trajectory();f,_=A.movement(g);g.y=-g.y;h,_=A.movement(g)
        for k in f:self.assertAlmostEqual(f[k],h[k],places=8)
    def test_duplicate(self):
        g=trajectory();g.loc[20,'time']=g.loc[19,'time']
        with self.assertRaises(ValueError):A.movement(g)
    def test_gap(self):
        with self.assertRaises(ValueError):A.movement(trajectory().drop(index=22))
    def test_straight(self):
        g=trajectory();g.x=np.arange(len(g))*.5;g.y=0
        with self.assertRaises(ValueError):A.movement(g)
    def test_weight(self):
        d=pd.DataFrame({'nfl_id':[1,1,1,2]});w=A.weights(d)
        self.assertAlmostEqual(w[:3].sum(),w[3])
    def test_cut(self):
        f,d=A.movement(trajectory());self.assertLess(f['speed_retention'],1);self.assertGreater(f['turn_angle'],.4);self.assertEqual(d['q'].shape,(11,2))

if __name__=='__main__':unittest.main()
