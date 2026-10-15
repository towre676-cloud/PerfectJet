import unittest
from fractions import Fraction as Q
from itertools import product
from math import isinf
import numpy as np
from perfectjet.replication_geometry import (calibration_requirement, calibrate, ellipsoid_scores,
    linear_interval, interval_ranks, repeat_covariance, scalar_repeat_budget)


class ReplicationGeometryTests(unittest.TestCase):
    def test_exact_calibration_resolution(self):
        for alpha in (Q(1,10),Q(1,20),Q(1,3)):
            for family in (1,2,29):
                n = calibration_requirement(alpha,family)
                self.assertTrue(isinf(calibrate(range(n-1),alpha=alpha,family_size=family).radius))
                self.assertFalse(isinf(calibrate(range(n),alpha=alpha,family_size=family).radius))
        self.assertEqual(calibration_requirement('0.1',29),289)

    def test_duplicates_do_not_create_calibration_information(self):
        r = calibrate([1]*500,group_ids=['same']*500)
        self.assertEqual(r.groups,1); self.assertTrue(isinf(r.radius))
        r = calibrate(list(range(10))*2,group_ids=list(range(10))*2)
        self.assertEqual(r.groups,10); self.assertEqual(r.radius,9)

    def test_group_maximum(self):
        r = calibrate([1,8,2,3],group_ids=['a','a','b','c'],alpha='0.5')
        self.assertEqual(r.groups,3); self.assertEqual(r.radius,3)

    def test_empty_calibration(self):
        r = calibrate([])
        self.assertTrue(isinf(r.radius)); self.assertIsNone(r.receipt()['radius'])

    def test_bad_calibration_inputs(self):
        cases = [dict(scores=[-1]),dict(scores=[float('nan')]),dict(scores=[1],group_ids=[]),
                 dict(scores=[1],group_ids=[[]]),dict(scores=[1],group_ids=[None]),
                 dict(scores=[1],group_ids=[float('nan')]),dict(scores=[],alpha=1),
                 dict(scores=[],alpha=0),dict(scores=[],family_size=True)]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                calibrate(**args)

    def test_exchangeable_rank_identity_without_simulation(self):
        # Exhaust every possible test rank among m+1 distinct scores. This is
        # the discrete rank argument, not a Monte Carlo coverage assertion.
        for m in range(1,41):
            for a in (Q(1,10),Q(1,4),Q(1,2)):
                covered = sum(t <= calibrate([x for x in range(m+1) if x != t],alpha=a).radius for t in range(m+1))
                self.assertGreaterEqual(Q(covered,m+1),1-a)

    def test_sharp_support(self):
        rng = np.random.default_rng(91)
        for _ in range(40):
            a = rng.normal(size=(3,3)); c = a@a.T+np.eye(3); h = rng.normal(size=3); mu = rng.normal(size=3)
            lo,hi = linear_interval(mu,c,2,h)
            point = mu+2*c@h/np.sqrt(h@c@h)
            self.assertAlmostEqual(float(h@point),hi,places=10)
            self.assertAlmostEqual(float(ellipsoid_scores([point],[mu],c)[0]),2,places=10)
            self.assertAlmostEqual(lo+hi,2*float(h@mu),places=10)

    def test_affine_transport(self):
        rng = np.random.default_rng(42)
        for _ in range(30):
            a = rng.normal(size=(3,3))+3*np.eye(3); c = np.eye(3)+np.ones((3,3))*.2
            y = rng.normal(size=(5,3)); mu = rng.normal(size=(5,3)); b = rng.normal(size=3)
            np.testing.assert_allclose(ellipsoid_scores(y,mu,c),ellipsoid_scores(y@a.T+b,mu@a.T+b,a@c@a.T),rtol=1e-8,atol=1e-8)

    def test_zero_loading_and_infinity(self):
        self.assertEqual(linear_interval([1,2],np.eye(2),float('inf'),[0,0]),(0.,0.))
        self.assertEqual(linear_interval([1,2],np.eye(2),float('inf'),[1,0]),(-float('inf'),float('inf')))

    def test_invalid_geometry(self):
        for c in ([[1,2],[0,1]], [[1,0],[0,-1]], [[1,0],[0,0]]):
            with self.assertRaises(ValueError): ellipsoid_scores([[1,2]],[[0,0]],c)
        with self.assertRaises(ValueError): linear_interval([1,2],np.eye(2),-1,[1,0])
        with self.assertRaises(ValueError): ellipsoid_scores([[1]],[[1,2]],np.eye(1))

    def test_interval_ranks_match_all_box_vertices_with_ties(self):
        rng = np.random.default_rng(89)
        for _ in range(80):
            pairs = np.sort(rng.integers(-3,4,size=(4,2)),axis=1)
            bounds = {str(i):tuple(map(float,p)) for i,p in enumerate(pairs)}
            r = interval_ranks(bounds,top_k=2)['ranks']
            vertices = list(product(*pairs))
            for i in range(4):
                best = min(1+sum(x[j]>x[i] for j in range(4) if i!=j) for x in vertices)
                worst = max(1+sum(x[j]>=x[i] for j in range(4) if i!=j) for x in vertices)
                self.assertEqual((r[str(i)]['best_rank'],r[str(i)]['worst_rank']),(best,worst))

    def test_invalid_ranks(self):
        for b,k in [({},1),({'a':(2,1)},1),({'a':(0,1)},2),({'a':(0,1)},True)]:
            with self.assertRaises(ValueError): interval_ranks(b,top_k=k)

    def test_covariance_limits_and_monotonicity(self):
        s = np.array([[2.,.2],[.2,1.]]); n = np.array([[.7,-.1],[-.1,.5]])
        previous = repeat_covariance(s,n,0)
        for m in (1,2,3,10,100,1000000):
            c = repeat_covariance(s,n,m)
            self.assertGreaterEqual(np.linalg.eigvalsh(previous-c).min(),-1e-10)
            self.assertGreaterEqual(np.linalg.eigvalsh(c-n).min(),-1e-10); previous = c
        np.testing.assert_allclose(previous,n,atol=1e-6)
        np.testing.assert_allclose(repeat_covariance(s,n,1000000,target='latent'),np.zeros((2,2)),atol=1e-6)

    def test_singular_signal(self):
        s = np.diag([1.,0.]); n = np.eye(2)
        np.testing.assert_allclose(repeat_covariance(s,n,2),np.diag([1+1/3,1.]))

    def test_invalid_repeat_count(self):
        for v in (-1,1.5,True):
            with self.assertRaises(ValueError): repeat_covariance(np.eye(2),np.eye(2),v)

    def test_scalar_budget_exact_boundaries(self):
        self.assertIsNone(scalar_repeat_budget(1,1,2,1)['repeats'])
        self.assertEqual(scalar_repeat_budget(1,1,'2.3',1)['repeats'],3)
        self.assertEqual(scalar_repeat_budget(1,1,1,1,target='latent')['repeats'],4)
        self.assertIsNone(scalar_repeat_budget(0,0,0,0)['repeats'])

    def test_scalar_budget_against_fraction_brute_force(self):
        rng = np.random.default_rng(63)
        for _ in range(1200):
            s,n,g,q = [Q(int(rng.integers(0,12)),int(rng.integers(1,5))) for _ in range(4)]
            target = 'next_attempt' if rng.integers(2) else 'latent'
            result = scalar_repeat_budget(s,n,g,q,target=target)['repeats']
            def good(m):
                v = (s*n/(n+m*s) if s and n else Q(0))+(n if target=='next_attempt' else 0)
                return g>0 and g*g>4*q*q*v
            brute = next((m for m in range(1,201) if good(m)),None)
            if result is None:
                self.assertIsNone(brute)
            else:
                self.assertTrue(good(result))
                if result>1:self.assertFalse(good(result-1))
                self.assertEqual(result if result<=200 else None,brute)

if __name__ == '__main__': unittest.main()
