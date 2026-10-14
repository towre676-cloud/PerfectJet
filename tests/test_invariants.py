import unittest,random
from fractions import Fraction as Q
from perfectjet.polynomial import Poly
from perfectjet.parametric import sextic_family,sub,mul,scale,divide
from perfectjet.invariants import (clebsch,same_weighted_point,substitute,absolute,cubic_gate_identity,
                                   quartic_covariant_partner,family_invariants,invariant_relations,orbit_classes,
                                   weighted_monomials,covariant_count)
from perfectjet.strata import strata,point_profile

x,y=Poly.variable(0),Poly.variable(1)


def rand_sextic(rng):
    return Poly({(6-i,i):Q(rng.randint(-5,5)) for i in range(7)})


class InvariantTests(unittest.TestCase):
    def test_gl2_scaling(self):
        rng=random.Random(1)
        for _ in range(6):
            f=rand_sextic(rng);m=[[Q(rng.randint(-3,3)) for _ in range(2)] for _ in range(2)]
            det=m[0][0]*m[1][1]-m[0][1]*m[1][0]
            if not det:continue
            a,b=clebsch(f),clebsch(substitute(f,m))
            for k,deg in enumerate((2,4,6,10)):self.assertEqual(b[k],a[k]*det**(3*deg))
            self.assertTrue(same_weighted_point(a,b))

    def test_distinct_orbits_are_separated(self):
        self.assertFalse(same_weighted_point(clebsch(x**6+y**6),clebsch(x*y*(x**4-y**4))))
        self.assertEqual(weighted_monomials(2),[(0,1,0,0),(2,0,0,0)])

    def test_cayley_sylvester_counts(self):
        # Invariants of the binary sextic: degrees 2,4,6,10,15 generate; degree 4 has A^2 and B.
        self.assertEqual([covariant_count(6,d,0) for d in (1,2,3,4,5,6)],[0,1,0,2,0,3])
        self.assertEqual(covariant_count(6,3,4),0)
        self.assertEqual(covariant_count(6,2,4),1)  # (f,f)_4
        self.assertEqual(covariant_count(4,2,0),1)  # binary quartic: invariant of degree 2
        self.assertEqual(covariant_count(4,3,0),1)  # and of degree 3

    def test_cubic_gate_theorem(self):
        rng=random.Random(2)
        for _ in range(15):self.assertTrue(cubic_gate_identity(rand_sextic(rng))["identity"])

    def test_quartic_covariant_partner(self):
        rng=random.Random(3)
        for _ in range(15):
            r=quartic_covariant_partner(rand_sextic(rng));self.assertTrue(r["gates_vanish"])
        self.assertFalse(quartic_covariant_partner(sextic_family(Q(0),Q(3)))["active"])  # (x^2+y^2)^3

    def test_named_equivalences_explain_exceptional_points(self):
        self.assertTrue(same_weighted_point(clebsch(sextic_family(Q(0),Q(15))),clebsch(x**6+y**6)))
        self.assertTrue(same_weighted_point(clebsch(sextic_family(Q(0),Q(-5))),clebsch(x*y*(x**4-y**4))))
        # Equivalent sextics have equal partner profiles.
        self.assertEqual(point_profile(0,15)["nonzero_kernels"],point_profile(0,0)["nonzero_kernels"])
        classes,_=orbit_classes([(Q(4),Q(6)),(Q(-4),Q(6)),(Q(24),Q(-9))],sextic_family)
        self.assertEqual(len(classes),2)

    def test_drop_curves_are_invariant_loci(self):
        inv=family_invariants();A,B=inv[0],inv[1]
        c3=[c for c in strata(3) if len(c["equations"])==1 and c["kernel_dimension"]==1][0]["equations"][0]
        self.assertIsNotNone(divide(sub(mul(A,A),scale(B,Q(1,6))),c3))
        rel=invariant_relations([c3],4,inv)
        self.assertEqual(rel[0]["relation"],{"B^1":Q(-1,6),"A^2":Q(1)})


if __name__=="__main__":unittest.main()
