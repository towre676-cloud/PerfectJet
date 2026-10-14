import unittest
import numpy as np
from pooled_schur_blend import schur
from pooled_safe_blend import choose,WEIGHTS
class SchurTests(unittest.TestCase):
    def test_matches_joint_block_ridge(self):
        rng=np.random.default_rng(23);x=rng.normal(size=(30,5));z=rng.normal(size=(30,3));y=rng.normal(size=30);xt=rng.normal(size=(8,5));zt=rng.normal(size=(8,3))
        p,base=schur(x,z,y,xt,zt,1000.)
        design=np.c_[np.ones(30),x,z];test=np.c_[np.ones(8),xt,zt]
        penalty=np.diag([0.]+[100.]*5+[1000.]*3)
        joint=test@np.linalg.solve(design.T@design+penalty,design.T@y)
        np.testing.assert_allclose(p,joint,atol=1e-12)
    def test_zero_motion_is_exact_baseline(self):
        rng=np.random.default_rng(91);x=rng.normal(size=(20,4));y=rng.normal(size=20);xt=rng.normal(size=(5,4))
        p,b=schur(x,np.zeros((20,2)),y,xt,np.zeros((5,2)),1000.)
        np.testing.assert_array_equal(p,b)
    def test_guard_rejects_uniformly_harmful_motion(self):
        y=np.zeros(12);base=np.zeros(12);motion=np.ones((12,3));classes=np.repeat([2023,2024],6)
        index,score=choose(y,base,motion,classes)
        np.testing.assert_array_equal(WEIGHTS[index],np.zeros(3));self.assertEqual(score,0)
