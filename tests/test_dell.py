"""Independent checks of theta jets, shell completeness and finite DELL replay."""
from fractions import Fraction as Q
from itertools import product
import unittest

from perfectjet.dell import (ClassicalDELL,Series,shift_shells,
                            theta_value_derivative,theta_ratio)


class ClassicalDellTests(unittest.TestCase):
    def test_shell_bound_is_complete_against_larger_enumerator(self):
        for n,m in ((2,3),(3,2),(4,1)):
            for a in range(n):
                expected={(sum(v*(v-1)//2 for v in s),s)
                          for s in product(range(-4,5),repeat=n)
                          if sum(s)==a and sum(v*(v-1)//2 for v in s)<=m}
                self.assertEqual(set(shift_shells(n,m,a)),expected)
        self.assertEqual([sum(d==k for d,_ in shift_shells(3,3,0))
                          for k in range(4)],[1,6,0,6])

    def test_theta_jet_through_first_coordinate_nome(self):
        for z in (Q(2),Q(3,5),Q(1)):
            value,derivative=theta_value_derivative(z,1)
            self.assertEqual(value,(1-z,-(1-z)*(z+1/z)))
            self.assertEqual(derivative,(-z,2*z*z-z+1/z))
        value,derivative=theta_ratio(Q(1,2),2,2)
        self.assertFalse(any(value))
        self.assertTrue(any(derivative))

    def test_rectangular_inverse_keeps_mixed_terms(self):
        a=Series(2,3,{(0,0):2,(1,0):3,(0,1):-5,(2,2):7})
        self.assertEqual((a*a.inverse()).terms,{(0,0):Q(1)})
        with self.assertRaises(ValueError):
            Series(2,3,{(1,0):1}).inverse()

    def test_known_global_first_order_identity_at_independent_point(self):
        s=ClassicalDELL(coordinate_order=0,momentum_order=1)
        self.assertEqual(s.poisson(s.current(1),s.current(2)).terms,
                         {(1,0):Q(8356261,901120)})
        self.assertFalse(s.poisson(s.hamiltonian(1),s.hamiltonian(2)).terms)

    def test_genuine_two_nome_and_numerator_negative_control(self):
        r=ClassicalDELL(coordinate_order=2,momentum_order=3).replay()
        self.assertTrue(r['passed'])
        self.assertTrue(r['pairs'][0]['raw_nonzero'])
        self.assertTrue(all(t['passed'] for t in r['charge_translation']))
        self.assertEqual(r['truncation'],{'P':2,'W':3})

    def test_free_coupling_and_theta_numerator_zeros(self):
        for coupling in (1,2):
            r=ClassicalDELL((1,2,5),(2,3,7),coupling,
                            coordinate_order=2,momentum_order=2).replay()
            self.assertTrue(r['passed'])
            if coupling==1:
                self.assertFalse(r['pairs'][0]['raw_nonzero'])

    def test_scalar_symbol_agrees_with_independent_quantum_compiler(self):
        from perfectjet.dell_quantum import QuantumDellBoundary
        s=ClassicalDELL(coordinate_order=2,momentum_order=3)
        q=QuantumDellBoundary(s.x,coupling=s.t,quantum=1,order=s.w,
                             coordinate_order=s.p)
        for a in (1,2):
            expected={}
            for w in range(s.w+1):
                for shift,v in q.normalized(a,w).items():
                    factor=Q(1)
                    for y,e in zip(s.y,shift):
                        factor*=y**e
                    for p,value in enumerate(v.coefficients):
                        expected[w,p]=expected.get((w,p),Q(0))+factor*value
            self.assertEqual(s.hamiltonian(a).value.terms,{k:v for k,v in expected.items() if v})

    def test_exact_input_contract(self):
        for kwargs in ({'coupling':2.0},{'x':(1,1,3)},{'y':(1,0,3)},
                       {'coordinate_order':True},{'momentum_order':-1}):
            with self.assertRaises(ValueError):
                ClassicalDELL(**kwargs)


if __name__=='__main__':
    unittest.main()
