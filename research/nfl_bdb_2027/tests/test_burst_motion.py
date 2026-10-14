import unittest
import numpy as np
import pandas as pd
from burst_motion import burst
from burst_support import row,average,identify
class BurstTests(unittest.TestCase):
    def trace(self):
        t=np.arange(40)*.1
        return pd.DataFrame({'time':pd.to_datetime('2023-02-01T12:00:00Z')+pd.to_timedelta(t,unit='s'),'x':3*t,'y':0.,'s':3.,'event':['ball_snap']+['']*39})
    def test_constant_speed_one_yard_time(self):
        result=burst(self.trace());self.assertAlmostEqual(result['travel1'],1/3,places=12);self.assertAlmostEqual(result['speed05'],3,places=12)
    def test_geometric_rigid_motion_invariance(self):
        g=self.trace();angle=.73;p=g[['x','y']].to_numpy();rotation=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
        h=g.copy();h[['x','y']]=p@rotation+[32.,-7.]
        a=burst(g);b=burst(h)
        for metric in ['travel1','speed05','speed1','accel05']:self.assertAlmostEqual(a[metric],b[metric],places=11)
    def test_already_active_and_gaps_rejected(self):
        with self.assertRaisesRegex(ValueError,'already_active'):burst(self.trace(),snap=True)
        with self.assertRaisesRegex(ValueError,'noncontiguous'):burst(self.trace().drop(index=10))
    def test_supported_scalar_and_hidden_witness(self):
        rows=[row(3,a*np.pi/180) for a in [45,90,135]]
        self.assertTrue(identify(rows,average(rows))['identified'])
        foreign=identify(rows,row(5,np.pi/2));self.assertFalse(foreign['identified'])
        witness=foreign['witness'];self.assertTrue(all(sum(a*b for a,b in zip(r,witness))==0 for r in rows))
    def test_valid_snap_decomposition(self):
        g=self.trace();g['s']=np.r_[np.zeros(5),np.repeat(3.,35)];g['x']=np.r_[np.zeros(5),np.arange(35)*.3]
        r=burst(g,snap=True);self.assertAlmostEqual(r['onset'],.5,places=5);self.assertAlmostEqual(r['total1'],r['onset']+r['travel1'],places=12)
if __name__=='__main__':unittest.main()
