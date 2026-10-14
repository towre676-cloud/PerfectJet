import unittest
import numpy as np,pandas as pd
import turn_transfer as T
import repo_predict as R

def example():
    n=45;theta=np.r_[np.zeros(20),np.full(n-20,np.pi/3)];xy=np.cumsum(np.c_[np.cos(theta),np.sin(theta)]*.5,axis=0);s=np.full(n,5.);s[18:24]=3.;time=pd.date_range('2023-01-01',periods=n,freq='100ms',tz='UTC').astype(str)
    return pd.DataFrame({'time':time,'x':xy[:,0],'y':xy[:,1],'s':s})

class TurnTests(unittest.TestCase):
    def test_motion_frame_invariance(self):
        g=example();a,_=T.first_turn(g);q=g.copy();xy=g[['x','y']].to_numpy();phi=.73;rotation=np.array([[np.cos(phi),-np.sin(phi)],[np.sin(phi),np.cos(phi)]])
        q[['x','y']]=xy@rotation+np.array([18,-7]);b,_=T.first_turn(q)
        q[['x','y']]=xy*np.array([1,-1]);c,_=T.first_turn(q)
        for field in ['burden','retention','exit_ratio','area','entry','angle']:
            self.assertAlmostEqual(a[field],b[field],places=8);self.assertAlmostEqual(a[field],c[field],places=8)
    def test_censoring_bounds_keep_unknown(self):
        d=pd.DataFrame({'recovery_event':[True,False,False],'recovery_time':[.2,.3,1.]})
        b=T.recovery_bounds(d);self.assertEqual(b['right_censored_total'],2);self.assertAlmostEqual(b['recovered_fraction_lower'],1/3);self.assertAlmostEqual(b['recovered_fraction_upper'],2/3)
    def test_future_separation_not_in_turn_measurement(self):
        g=example();a,_=T.first_turn(g);g['separation_at_pass_forward']=999.;b,_=T.first_turn(g);self.assertEqual(a,b)
    def test_overlap_rejected(self):
        d=pd.DataFrame({'nfl_id':[1]})
        with self.assertRaises(ValueError):T.fit_predict(d,d,pd.DataFrame(),'execution',R.CONFIGS[0],'burden')
    def test_sampling_gap_rejected(self):
        with self.assertRaises(ValueError):T.first_turn(example().drop(index=4))
    def test_burden_is_measured_and_bounded(self):
        f,_=T.first_turn(example());self.assertTrue(f['complete_half_second']);self.assertGreaterEqual(f['burden'],0);self.assertLessEqual(f['burden'],.5)
    def test_short_followup_is_not_imputed(self):
        g=example();f,_=T.first_turn(g);short=g.iloc[:int(round(f['cut_time']/.1))+4].copy();result,_=T.first_turn(short);self.assertFalse(result['complete_half_second']);self.assertTrue(np.isnan(result['burden']));self.assertFalse(result['recovery_event'])

if __name__=='__main__':unittest.main()
