import unittest
import numpy as np
from fractions import Fraction as Q
from vendor.pp import exact_linear as E
from turn_observability_design import row

class DemandDesignTests(unittest.TestCase):
    def test_same_angle_leaves_an_exact_invisible_direction(self):
        source=tuple(row(s,np.deg2rad(30)) for s in [3,4.5,6,7.5]);witness=(Q(-1,3),Q(0),Q(1),Q(0),Q(0),Q(0));target=(row(6,np.deg2rad(90)),)
        self.assertEqual(E.apply(source,witness),(Q(0),)*4);self.assertEqual(E.apply(target,witness),(Q(2,3),));self.assertEqual(E.rank(source),3);self.assertEqual(E.target_factor(source,target)['status'],'AMBIGUOUS')
    def test_six_triangle_conditions_complete_quadratic_family(self):
        conditions=[(3,30),(4.5,30),(6,30),(3,60),(4.5,60),(3,90)];source=tuple(row(s,np.deg2rad(a)) for s,a in conditions);target=(row(7.5,np.deg2rad(120)),)
        self.assertEqual(E.rank(source),6);self.assertEqual(E.target_factor(source,target)['status'],'EXACT_TARGET_FACTOR')

if __name__=='__main__':unittest.main()
