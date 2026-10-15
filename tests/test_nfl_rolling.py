import unittest
from dataclasses import replace
import numpy as np
from perfectjet.applications.nfl_scouting.schema import Frame,Attempt,Athlete,Dataset,Play
from perfectjet.applications.nfl_scouting import rolling as R

class RollingTests(unittest.TestCase):
    def attempt(self):
        return Attempt('a','one','FORTY_YARD_DASH',[Frame(i/10,1+1.2*i/10+2*(i/10)**2,3) for i in range(31)],'2023-03-01')
    def dataset(self):
        a=Athlete('a','DE',2023,{},{});return Dataset({'a':a},[self.attempt()],[],{}, {'minimum_plays':30})
    def test_clipped_launch_is_allowed_but_not_invented(self):
        w=R.speed_window(self.attempt(),2);self.assertIsNotNone(w);self.assertGreater(w.entry_speed,2)
        self.assertAlmostEqual(w.area_acceleration,4,places=10)
        self.assertAlmostEqual(w.minimum_variance_acceleration,4,places=10)
        self.assertAlmostEqual(w.minimum_variance_jerk,0,places=8)
    def test_suffix_cannot_change_gate_or_readout(self):
        a=self.attempt();w=R.speed_window(a)
        a=replace(a,frames=a.frames[:w.endpoint_frame+1]+[Frame(999,float('nan'),float('nan'))])
        self.assertEqual(w,R.speed_window(a))
    def test_future_cannot_supply_threshold_history(self):
        a=self.attempt();a=replace(a,frames=[Frame(f.t,0,0) for f in a.frames[:9]])
        self.assertIsNone(R.speed_window(a))
    def test_prefix_gap_rejected(self):
        a=self.attempt();a=replace(a,frames=a.frames[:2]+a.frames[3:]);self.assertIsNone(R.speed_window(a))
    def test_endpoint_gap_rejected(self):
        a=self.attempt();w=R.speed_window(a);f=a.frames[:];f[w.gate_frame+1]=replace(f[w.gate_frame+1],t=99)
        self.assertIsNone(R.speed_window(replace(a,frames=f)))
    def test_rigid_coordinate_invariance(self):
        a=self.attempt();w=R.speed_window(a)
        b=replace(a,frames=[Frame(f.t+500,-f.y+80,f.x-100) for f in a.frames]);v=R.speed_window(b)
        for name in R.KINEMATICS+R.JETS:self.assertAlmostEqual(getattr(w,name),getattr(v,name),places=7)
    def test_reflection_invariance(self):
        a=self.attempt();w=R.speed_window(a);b=replace(a,frames=[Frame(f.t,f.x,-f.y) for f in a.frames]);v=R.speed_window(b)
        self.assertAlmostEqual(w.area_acceleration,v.area_acceleration)
    def test_predraft_guard(self):
        ds=self.dataset();ds.attempts=[replace(self.attempt(),recorded_on='2024-01-01')]
        self.assertEqual(R.source_windows(ds)[0],[])
    def test_duplicated_attempts_rejected(self):
        ds=self.dataset();ds.attempts*=2
        with self.assertRaises(ValueError):R.source_windows(ds)
    def test_source_features_do_not_read_nfl(self):
        ds=self.dataset();w,_=R.source_windows(ds);a=R.feature_frames(ds,['a'],w)
        ds.plays=[Play('a',2023,'bad',float('nan'),{'NFL_SECRET':'poison'})]
        b=R.feature_frames(ds,['a'],w)
        for key in a:self.assertTrue(a[key].equals(b[key]))
    def test_shared_support(self):
        ds=self.dataset();w,_=R.source_windows(ds);f=R.feature_frames(ds,['a'],w)
        cols=[c for c in f['conventional'] if '__v' in c]
        for key in f:self.assertTrue(f['conventional'][cols].equals(f[key][cols]))
    def test_no_source_is_missing_not_zero_response(self):
        ds=self.dataset();f=R.feature_frames(ds,['a'],[])
        self.assertTrue(f['jets'].filter(like='area_acceleration').isna().all().all())
    def test_original_group_guard(self):
        ds=self.dataset();ds.athletes['b']=replace(ds.athletes['a'],athlete_id='b',bootstrap_group='a')
        with self.assertRaises(ValueError):R.target_values(ds,['a'],['b'],2024,1)
    def test_future_training_guard(self):
        with self.assertRaises(ValueError):R.target_values(self.dataset(),['a'],[],2023,1)
    def test_synthetic_cannot_be_evidence(self):
        ds=self.dataset();ds.synthetic=True
        with self.assertRaises(ValueError):R.experiment(ds)

if __name__=='__main__':unittest.main()
