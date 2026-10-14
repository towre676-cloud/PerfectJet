import unittest
import numpy as np
from perfectpower.movement_features import trajectory,attempt_features,ensemble_features

class Features(unittest.TestCase):
    def source(self):
        t=np.arange(61)*.1;s=3+np.sin(t*1.3);theta=.5*np.sin(t);xy=np.c_[np.cumsum(s*np.cos(theta))*.1,np.cumsum(s*np.sin(theta))*.1];return t,xy,s
    def test_translation_rotation(self):
        t,p,s=self.source();f,_=attempt_features(t,p,s);g,_=attempt_features(t,p@np.array([[0,-1],[1,0]])+np.array([12,-7]),s)
        for key in f:self.assertAlmostEqual(f[key],g[key],places=7)
    def test_summary_partition(self):
        t,p,s=self.source();f,a=attempt_features(t,p,s)
        self.assertAlmostEqual(sum(f['phase_duration_'+str(k)] for k in range(4)),6.1)
        for row in a['phase']['occupancy']:self.assertAlmostEqual(sum(row),1,places=8)
        self.assertTrue(all(np.isfinite(v) for v in f.values()));self.assertGreater(int(a['population']),1)
    def test_gaps_and_duplicates(self):
        t,p,s=self.source();t[30:]+=.5
        with self.assertRaises(ValueError):trajectory(t,p,s)
        t,p,s=self.source();t[1]=0
        with self.assertRaises(ValueError):trajectory(t,p,s)
    def test_ensemble(self):
        t,p,s=self.source();f,a=ensemble_features(t,p,s)
        self.assertEqual(f['onset_scenarios'],3);self.assertEqual(len(a['scenarios']),3)
        self.assertEqual(f['onset_range_recovery_accel'],0)

if __name__=='__main__':unittest.main()
