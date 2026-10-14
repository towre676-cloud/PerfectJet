import unittest,itertools
import numpy as np
from scipy.special import logsumexp
import phase_population as P
from test_front_angular import trace

class PhasePopulationTests(unittest.TestCase):
    def test_exact_enumeration(self):
        z=np.array([[.3,.1,.1],[.4,-.2,.1],[.2,-.1,.6],[.3,.3,.2],[.5,.4,.1]])
        _,p,logz=P.phase_population(z)
        a,w=z[:,1],z[:,2];c=np.c_[a*a+w*w,(a+.5)**2+w*w,a*a+(w-.5)**2,(a-.5)**2+w*w]/2
        paths=[q for q in itertools.product(range(4),repeat=len(z)) if q[0]==0 and q[-1]==3 and all(y-x in (0,1) for x,y in zip(q,q[1:]))]
        weights=np.array([-sum(c[i,k] for i,k in enumerate(q)) for q in paths]);exact=np.zeros_like(p)
        for q,weight in zip(paths,np.exp(weights-logsumexp(weights))):
            for i,k in enumerate(q):exact[i,k]+=weight
        np.testing.assert_allclose(p,exact,atol=1e-13);self.assertAlmostEqual(logz,logsumexp(weights));np.testing.assert_allclose(p.sum(1),1)
    def test_rigid_geometry(self):
        g=trace();a,_=P.pooled(g,8);q=g.copy();q[['x','y']]=q[['x','y']].to_numpy()*[-1,1]+[40,-12];b,_=P.pooled(q,8)
        for k in a:self.assertAlmostEqual(a[k],b[k],places=6)
    def test_order_and_histogram(self):
        z=np.array([[.1,.2,0],[.4,-.3,.1],[.2,-.1,.9],[.5,.4,.2],[.6,.3,0]])
        q=z[[0,3,1,2,4]];np.testing.assert_allclose(q.mean(0),z.mean(0));self.assertFalse(np.allclose(P.sequence_features(z,1),P.sequence_features(q,1)))
    def test_irregular_rejected(self):
        with self.assertRaises(ValueError):P.channels(trace().drop(index=5),.5)
if __name__=='__main__':unittest.main()
