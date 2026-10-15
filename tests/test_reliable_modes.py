import unittest
import numpy as np
from perfectjet.reliable_modes import ReliableModes

class ReliableModeTests(unittest.TestCase):
    def groups(self):
        rng=np.random.default_rng(13)
        return {str(i):np.asarray([np.array([i/10,2*i/10])+rng.normal(0,.1,2) for _ in range(3)]) for i in range(30)}
    def test_training_isolation(self):
        g=self.groups();a=ReliableModes.fit(g,training_groups=['0','1','2','3'])
        g['29']=np.full((3,2),999.)
        b=ReliableModes.fit(g,training_groups=['0','1','2','3'])
        np.testing.assert_array_equal(a.signal,b.signal)
    def test_posterior_noise_decreases_with_repeats(self):
        g=self.groups();m=ReliableModes.fit(g,training_groups=list(g))
        a=m.posterior(g['1'][:1])[1];b=m.posterior(g['1'])[1]
        self.assertTrue(np.linalg.eigvalsh(a-b).min()>-1e-10)
    def test_covariance_psd(self):
        m=ReliableModes.fit(self.groups(),training_groups=list(self.groups()))
        self.assertGreaterEqual(np.linalg.eigvalsh(m.signal).min(),-1e-10)
        self.assertGreaterEqual(np.linalg.eigvalsh(m.posterior([[0.,0.]])[1]).min(),-1e-10)
    def test_no_repeat_not_calibrated(self):
        m=ReliableModes.fit({'a':[[1,2]],'b':[[2,3]],'c':[[3,4]]},training_groups=['a','b','c'])
        self.assertFalse(m.calibrated)
    def test_no_observation_is_prior(self):
        m=ReliableModes.fit(self.groups(),training_groups=list(self.groups()))
        np.testing.assert_array_equal(m.posterior([])[0],m.mean)
    def test_rotation_covariance(self):
        g=self.groups();rot=np.array([[0.,-1.],[1.,0.]])
        m=ReliableModes.fit(g,training_groups=list(g))
        r=ReliableModes.fit({k:v@rot.T for k,v in g.items()},training_groups=list(g))
        np.testing.assert_allclose(r.posterior(g['1']@rot.T)[0],rot@m.posterior(g['1'])[0],atol=1e-10)
    def test_equal_width_required(self):
        with self.assertRaises(ValueError):ReliableModes.fit({'a':[[1]],'b':[[1,2]]},training_groups=['a','b'])

if __name__=='__main__':unittest.main()
