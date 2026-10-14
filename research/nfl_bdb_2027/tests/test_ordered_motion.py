import itertools,unittest
import numpy as np
from scipy.special import logsumexp
from ordered_motion import phase_channel,signature

class OrderedMotionTests(unittest.TestCase):
    def test_language_matches_independent_enumeration(self):
        z=np.array([[.2,.1],[-.5,.2],[-1,.4],[.1,1],[.6,.2],[1,.1]])
        a,w=z.T;cost=np.c_[a*a+w*w,(a+1)**2+w*w,a*a+(w-1)**2,(a-1)**2+w*w]/2
        words=[];weights=[]
        for jumps in itertools.combinations(range(1,len(z)),3):
            word=np.array([sum(i>=j for j in jumps) for i in range(len(z))]);words.append(word);weights.append(-cost[np.arange(len(z)),word].sum())
        logz=logsumexp(weights);weights=np.exp(np.array(weights)-logz);p=sum(weight*np.eye(4)[word] for weight,word in zip(weights,words));expected=np.r_[p.mean(0),(p*a[:,None]).sum(0)/p.sum(0),logz/len(z)]
        np.testing.assert_allclose(phase_channel(z),expected,atol=1e-12)
    def test_signed_order_area_changes_under_reversal(self):
        z=np.array([[0,0,0,0],[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,0,0,0]],float)
        np.testing.assert_allclose(signature(z)[12:18],-signature(z[::-1])[12:18])

if __name__=='__main__':unittest.main()
