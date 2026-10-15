import unittest
from fractions import Fraction as Q
from perfectjet.stopped_jets import (area_acceleration_weights,minimum_variance_jet,
    signature_area_weights,ordered_area,derivative_remainder_bound,readout_receipt)
from perfectjet.readout import dot

class StoppedJetTests(unittest.TestCase):
    def setUp(self):self.times=[Q(i,10) for i in range(6)]
    def test_area_quadratic_and_nuisance(self):
        w=area_acceleration_weights(self.times)
        for a in [-3,0,2,10]:
            for origin in [-100,7]:
                x=[origin+11*t+Q(a,2)*t*t for t in self.times]
                self.assertEqual(dot(w,x),a)
    def test_irregular_grid_exact(self):
        t=[Q(0),Q(1,20),Q(1,5),Q(1,2)]
        self.assertEqual(dot(area_acceleration_weights(t),[4+5*x+3*x*x for x in t]),6)
    def test_signature_streaming_equals_weights(self):
        t=self.times;x=[Q(i*i-3*i) for i in range(6)]
        self.assertEqual(ordered_area([(b-a,y-z) for a,b,z,y in zip(t,t[1:],x,x[1:])]),dot(signature_area_weights(t),x))
    def test_order_information(self):
        self.assertEqual(ordered_area([(1,1),(1,3)]),1)
        self.assertEqual(ordered_area([(1,3),(1,1)]),-1)
    def test_cubic_jet(self):
        c=Q(1,4);x=[5+2*(t-c)+3*(t-c)**2+Q(5,6)*(t-c)**3 for t in self.times]
        self.assertEqual(dot(minimum_variance_jet(self.times,2,3)['weights'],x),6)
        self.assertEqual(dot(minimum_variance_jet(self.times,3,3)['weights'],x),5)
    def test_insufficient_positions_return_witness(self):
        r=minimum_variance_jet([0,1],2,3)
        self.assertFalse(r['identified']);self.assertNotEqual(r['readout_shift'],0)
        self.assertTrue(all(dot(row,r['witness'])==0 for row in r['design']))
    def test_blue_optimality(self):
        w=minimum_variance_jet(self.times,2,3);a=area_acceleration_weights(self.times)
        self.assertLess(w['variance'],dot(a,a))
        self.assertEqual(dot([x-y for x,y in zip(a,w['weights'])],w['weights']),0)
    def test_correlated_covariance(self):
        c=[[Q(int(i==j))+Q(1,2) for j in range(6)] for i in range(6)]
        self.assertEqual(minimum_variance_jet(self.times,2,3,c)['variance'],Q(7500,7))
    def test_invalid_covariance(self):
        with self.assertRaises(ValueError):minimum_variance_jet(self.times,2,3,[[0]*6 for _ in range(6)])
    def test_remainder_bound(self):
        w=minimum_variance_jet(self.times,2,3)['weights']
        value=abs(dot(w,[(t-Q(1,4))**4 for t in self.times]))
        self.assertLessEqual(value,derivative_remainder_bound(self.times,w,3,24))
    def test_clock_translation(self):
        self.assertEqual(minimum_variance_jet(self.times)['weights'],minimum_variance_jet([t+500 for t in self.times])['weights'])
    def test_variance_ratio(self):self.assertEqual(readout_receipt()['blue_vs_naive_variance_ratio'],Q(1,56))
    def test_bad_time_grid(self):
        for t in ([0,0,1],[2,1],[0]):
            with self.assertRaises(ValueError):signature_area_weights(t)

if __name__=='__main__':unittest.main()
