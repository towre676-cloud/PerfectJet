import unittest,random
from fractions import Fraction as Q
from perfectjet.exact import rank
from perfectjet.parametric import evaluate,var,const,sub,mul,add,polynomial_matrix,sextic_family
from perfectjet.loci import rational_roots,_isolated_rational_roots,pmul,trim
from perfectjet.strata import (bareiss_det,discriminant_resultant,surface_discriminant,strata,sample_points,
                               partner_witness,point_profile,curve_points,root_structure,small_rationals)
from perfectjet.transvectants import gate_matrix
from perfectjet.polynomial import Poly


class DeterminantTests(unittest.TestCase):
    def test_bareiss_matches_pointwise_determinant(self):
        rng=random.Random(5);a,b=var(0,2),var(1,2)
        for _ in range(10):
            m=[[add(mul(const(rng.randint(-3,3),2),a),add(mul(const(rng.randint(-3,3),2),b),const(rng.randint(-3,3),2)))
                for _ in range(4)] for _ in range(4)]
            det=bareiss_det(m,2)
            for pt in [(Q(1),Q(2)),(Q(-3),Q(1,2)),(Q(0),Q(0))]:
                num=[[evaluate(p,pt) for p in row] for row in m]
                full=rank(num)==4
                self.assertEqual(evaluate(det,pt)!=0,full)

    def test_discriminant_detects_repeated_roots(self):
        d=surface_discriminant()
        for pt,repeated in [((16,-9),True),((-16,-9),True),((0,3),True),((4,-3),True),
                            ((0,15),False),((0,-5),False),((1,1),False),((11,6),False)]:
            self.assertEqual(evaluate(d,pt)==0,repeated,pt)

    def test_root_structure(self):
        self.assertEqual(root_structure(16,-9),[{"multiplicity":1,"roots":2},{"multiplicity":4,"roots":1}])
        self.assertEqual(root_structure(0,3),[{"multiplicity":3,"roots":2}])
        self.assertEqual(root_structure(1,1),[{"multiplicity":1,"roots":6}])


class RationalRootTests(unittest.TestCase):
    def test_sturm_route_matches_candidate_enumeration(self):
        rng=random.Random(9)
        from math import lcm
        for _ in range(150):
            p=[Q(1)]
            for _ in range(rng.randint(0,3)):p=pmul(p,[-Q(rng.randint(-40,40),rng.randint(1,7)),Q(1)])
            p=pmul(p,trim([Q(rng.randint(-9,9)) for _ in range(3)]+[Q(rng.randint(1,4))]))
            den=lcm(*(x.denominator for x in p));ints=[int(x*den) for x in p]
            if not ints or ints[0]==0:continue
            self.assertEqual(sorted(_isolated_rational_roots(ints)),rational_roots(p))

    def test_large_constant_term(self):
        p=pmul(pmul([-Q(123456789),Q(1)],[Q(987654321,7),Q(1)]),[Q(1),Q(0),Q(1)])
        self.assertEqual(rational_roots(p),[Q(-987654321,7),Q(123456789)])


class StrataTests(unittest.TestCase):
    def test_strata_partition_and_match_pointwise_ranks(self):
        for n in (3,4,6):
            cells=strata(n)
            for a in range(-3,4):
                for b in range(-3,4):
                    pt=(Q(a),Q(b))
                    hits=[c for c in cells if all(evaluate(p,pt)==0 for p in c["equations"])
                          and all(evaluate(q,pt)!=0 for q in c["inequations"])]
                    self.assertEqual(len(hits),1,(n,pt))
                    w=partner_witness(*pt,n)
                    self.assertEqual(hits[0]["kernel_dimension"],w["kernel_dimension"])
                    self.assertEqual(hits[0]["active_dimension"],w["active_dimension"])

    def test_witnesses_replay_and_split_kernel(self):
        for pt,n in [((16,-9),6),((0,3),8),((0,15),3),((11,6),8),((Q(32,25),Q(-9,5)),12)]:
            w=partner_witness(Q(pt[0]),Q(pt[1]),n)
            self.assertTrue(w["replayed"])
            self.assertEqual(w["active_dimension"]+w["commuting_dimension"],w["kernel_dimension"])

    def test_perfect_cube_exceptionality_is_commuting(self):
        prof={r["degree"]:r for r in point_profile(0,3)["nonzero_kernels"]}
        for n in (4,6,8,10):self.assertEqual((prof[n]["active"],prof[n]["commuting"]),(0,1))
        # The commuting partner in degree 4 is (x^2+y^2)^2, a rotation invariant.
        w=partner_witness(Q(0),Q(3),4);g=w["commuting_partners"][0]
        x,y=Poly.variable(0),Poly.variable(1);target=(x*x+y*y)**2
        scale=g[0]/Q(1);self.assertEqual([c/scale for c in g],[target.terms.get((4-j,j),Q(0)) for j in range(5)])

    def test_new_squarefree_points_have_active_partners(self):
        for pt,n in [((24,-9),3),((4,6),3),((11,6),8),((Q(32,25),Q(-9,5)),12)]:
            prof=point_profile(*pt)
            self.assertTrue(prof["squarefree"])
            self.assertIn(n,[r["degree"] for r in prof["nonzero_kernels"] if r["active"]>0])

    def test_curve_points_lie_on_curve(self):
        cells=[c for c in strata(8) if c["equations"] and len(c["equations"])==1 and c["kernel_dimension"]==1]
        curve=[c for c in cells if any(sum(e)==3 for e in c["equations"][0])][0]
        pts=curve_points(curve,8)
        self.assertIn((Q(11),Q(6)),pts)
        for pt in pts:self.assertEqual(evaluate(curve["equations"][0],pt),0)

    def test_small_rationals(self):
        r=small_rationals(2);self.assertEqual(len(r),len(set(r)));self.assertIn(Q(-1,2),r)


if __name__=="__main__":unittest.main()
