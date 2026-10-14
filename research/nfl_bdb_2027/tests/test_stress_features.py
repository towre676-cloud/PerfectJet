import unittest,numpy as np,pandas as pd
import stress_features as S
class StressFeaturesTests(unittest.TestCase):
    def trace(self):
        t=np.arange(100)*.1;angle=np.clip((t-3)*2,0,np.pi/2);speed=4-1.5*np.exp(-((t-3.4)/.25)**2);p=np.cumsum(np.c_[np.cos(angle),np.sin(angle)]*speed[:,None]*.1,axis=0);return pd.DataFrame({'time':pd.date_range('2023-01-01',periods=len(t),freq='100ms').astype(str),'x':p[:,0],'y':p[:,1],'s':speed})
    def test_geometry_and_declared_box(self):
        g=self.trace();a=S.event_turns(g);self.assertTrue(a);h=g.copy();phi=.7;h[['x','y']]=h[['x','y']].to_numpy()@np.array([[np.cos(phi),-np.sin(phi)],[np.sin(phi),np.cos(phi)]])+[30,-9];b=S.event_turns(h);self.assertEqual(len(a),len(b))
        for left,right in zip(a,b):
            for k in ['entry','angle','eta','eta_min','eta_max']:self.assertAlmostEqual(left[k],right[k],places=7)
            self.assertLessEqual(left['box_eta_min'],left['eta_min']+1e-10);self.assertGreaterEqual(left['box_eta_max'],left['eta_max']-1e-10)
    def test_sampling_gap_rejected(self):
        with self.assertRaises(ValueError):S.event_turns(self.trace().drop(index=5))
    def test_progress_clock_has_complete_bounded_recovery(self):
        turns=S.event_turns(self.trace(),clock=True);self.assertTrue(turns)
        for turn in turns:
            for branch in turn['branches']:self.assertEqual(len(branch['normalized_trace']),6)
            self.assertLessEqual(turn['box_eta_min'],turn['eta_min']+1e-10)
            self.assertGreaterEqual(turn['box_eta_max'],turn['eta_max']-1e-10)
    def test_quantization_error_bound(self):
        rng=np.random.default_rng(4);z=rng.normal(size=(100,6));coarse=np.round(z*20)/20;error=np.abs((z-coarse)@(S.TRAP/.5));self.assertTrue((error<=.025+1e-12).all())
if __name__=='__main__':unittest.main()
