import unittest
import numpy as np,pandas as pd
import front_transfer as F,angular_breaks as B,speed_ceiling as C,repo_predict as R

def trace():
    n=70;t=np.arange(n)*.1;angle=np.clip((t-2)*2,0,np.pi/2);speed=5-1.5*np.exp(-((t-2.4)/.25)**2);p=np.cumsum(np.c_[np.cos(angle),np.sin(angle)]*speed[:,None]*.1,axis=0)
    return pd.DataFrame({'time':pd.date_range('2023-01-01',periods=n,freq='100ms').astype(str),'x':p[:,0],'y':p[:,1],'s':speed})

class FrontAngularTests(unittest.TestCase):
    def test_skill_geometry_rotation_translation(self):
        g=trace();a=F.skill_features(g);q=g.copy();phi=.8;xy=q[['x','y']].to_numpy();q[['x','y']]=xy@np.array([[np.cos(phi),-np.sin(phi)],[np.sin(phi),np.cos(phi)]])+[50,-8];b=F.skill_features(q)
        for k in a:self.assertAlmostEqual(a[k],b[k],places=7)
    def test_angular_break_rotation_reflection(self):
        g=trace();a,_=B.measure(g,'OUT');q=g.copy();q[['x','y']]=g[['x','y']].to_numpy()*[-1,1]+[40,-7];b,_=B.measure(q,'OUT')
        for k in a:self.assertAlmostEqual(a[k],b[k],places=7)
        self.assertGreater(a['rotation_duration'],0);self.assertLess(a['angle'],np.pi)
    def test_angular_gap_rejected(self):
        with self.assertRaises(ValueError):B.measure(trace().drop(index=8),'OUT')
    def test_front_player_overlap_rejected(self):
        d=pd.DataFrame({'nfl_id':[1]})
        with self.assertRaises(ValueError):F.fit_predict(d,d,[],F.CONFIGS[0],'player_get_off')
    def test_single_motion_channel_has_fixed_dimension(self):
        rng=np.random.default_rng(4);d=pd.DataFrame(rng.normal(size=(17,len(R.PHYS))),columns=R.PHYS);d['forty']=4.5;d['ten_yd_split']=1.5;d['nfl_id']=np.arange(17);d['sensor_ceiling']=10+rng.normal(size=17);d['nfl_speed_capacity']=9+rng.normal(size=17)
        p=C.predict(d.iloc[:12],d.iloc[12:],'ceiling',C.CONFIGS[0]);self.assertEqual(p.shape,(5,));self.assertTrue(np.isfinite(p).all())

if __name__=='__main__':unittest.main()
