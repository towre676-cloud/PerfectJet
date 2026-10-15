import unittest
from fractions import Fraction as Q
from perfectjet.launch_ambiguity import ambiguity_receipt,state

class LaunchAmbiguityTests(unittest.TestCase):
    def test_exact_boundaries(self):
        r=ambiguity_receipt();self.assertEqual(r['common_starting_position'],'-5/12')
    def test_entire_polynomial_tail_and_stationary_start(self):
        for t in (Q(0),Q(1,5),Q(1),Q(100)):
            for k in range(3):self.assertEqual(state('early',t,k),state('late',t,k))
        self.assertEqual(state('early',-3),state('late',-3))
        self.assertGreater(state('early',Q(-3,2),1),0)
        self.assertEqual(state('late',Q(-3,2),1),0)
    def test_positive_acceleration_sanity(self):
        for k in range(100):
            t=Q(k-100,50)
            for name in ('early','late'):
                self.assertGreaterEqual(state(name,t,1),0);self.assertGreaterEqual(state(name,t,2),0)
    def test_invalid_input(self):
        with self.assertRaises(ValueError):state('other',0)
        with self.assertRaises(ValueError):state('early',0,3)
if __name__=='__main__':unittest.main()
