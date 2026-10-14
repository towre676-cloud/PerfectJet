import unittest
from fractions import Fraction as Q
from perfectjet.parametric import polynomial_matrix,var,add,const,mul,sub,groebner,is_unit_ideal
from perfectjet.invariants import slice_form
from perfectjet.incidence import correction_matrix
from perfectjet.modular import (groebner_mod,is_unit,to_mod,det_mod,ideal_of_minors,saturated_unit,
                                quotient_length,interreduce_linear,P)


class ModularTests(unittest.TestCase):
    def test_groebner_matches_rational_on_small_ideals(self):
        x,y=var(0,2),var(1,2);one=const(1,2)
        gens=[sub(mul(x,x),y),sub(mul(x,y),one)]
        g=groebner_mod([to_mod(p) for p in gens])
        self.assertEqual(quotient_length(g,2),len([1 for _ in range(3)]))  # x^3=1: three points
        self.assertTrue(is_unit(groebner_mod([to_mod(x),to_mod(sub(x,one))])))
        self.assertFalse(is_unit(g))

    def test_det_and_interreduction(self):
        x,y=var(0,2),var(1,2)
        m=[[to_mod(x),to_mod(y)],[to_mod(y),to_mod(x)]]
        d=det_mod(m,2)
        self.assertEqual(d,to_mod(sub(mul(x,x),mul(y,y))))
        self.assertEqual(len(interreduce_linear([d,{e:2*c%P for e,c in d.items()}])),1)

    def test_slice_emptiness_agrees_with_exact_results(self):
        p,q,r=var(0,3),var(1,3),var(2,3)
        avoid=to_mod(mul(r,add(add(add(p,q),r),const(1,3))))
        def locus_empty(n,kernel):
            m=polynomial_matrix(lambda a,b,c:correction_matrix(slice_form(a,b,c),n),3,1)
            return saturated_unit(ideal_of_minors(m,n+2-kernel,3),avoid,3)
        self.assertFalse(locus_empty(4,2))   # octahedral orbit
        self.assertTrue(locus_empty(5,2))    # no two-dimensional quintic kernel


if __name__=="__main__":unittest.main()
