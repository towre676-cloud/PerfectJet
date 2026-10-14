import unittest
from fractions import Fraction as Q
from perfectjet.parametric import evaluate
from perfectjet.invariants import clebsch,slice_form,same_weighted_point
from perfectjet.polynomial import Poly
from perfectjet.incidence import (random_line,line_probe,identify_hypersurface,QuotientRing,clebsch_over,
                                  slice_coefficients,degree5_classification,slice_jump,degenerate_profile,
                                  minimal_polynomial,degenerate_forms,s_form,correction_matrix,_rank)

x,y=Poly.variable(0),Poly.variable(1)


class SymbolicCovariantTests(unittest.TestCase):
    def test_clebsch_over_free_ring_specializes(self):
        ring=QuotientRing([],3)
        inv=clebsch_over(ring,slice_coefficients())
        for pt in [(Q(1),Q(2),Q(-3)),(Q(0),Q(1,2),Q(5)),(Q(-2),Q(0),Q(1))]:
            self.assertEqual([evaluate(p,pt) for p in inv],list(clebsch(slice_form(*pt))))

    def test_minimal_polynomial(self):
        self.assertEqual(minimal_polynomial([[Q(2),Q(0)],[Q(0),Q(2)]]),[Q(-2),Q(1)])
        self.assertEqual(minimal_polynomial([[Q(0),Q(1)],[Q(-1),Q(0)]]),[Q(1),Q(0),Q(1)])


class HypersurfaceTests(unittest.TestCase):
    def test_line_probe_finds_the_two_hypersurfaces(self):
        line=random_line(1)
        for n,rel in [(3,{"A^2":Q(1),"B^1":Q(-1,6)}),(12,{"A^2":Q(1),"B^1":Q(-25,96)})]:
            pr=line_probe(n,line);self.assertEqual(pr["hypersurface_degree"],4)
            ident=identify_hypersurface(pr["locus"],line)
            self.assertEqual(ident["relation"],rel);self.assertTrue(ident["restriction_equals_locus"])
        for n in (5,7,8,9,10):self.assertEqual(line_probe(n,line)["hypersurface_degree"],0)
        self.assertEqual(line_probe(4,line)["generic_kernel"],1)


class ClassificationTests(unittest.TestCase):
    def test_quintic_partners_are_the_c3_orbit(self):
        r=degree5_classification()
        self.assertEqual(r["slice_points_with_multiplicity"],20)
        self.assertTrue(all(r["relations_hold"].values()));self.assertTrue(r["A_is_unit"])

    def test_small_degree_jumps(self):
        d3=slice_jump(3,2)["classification"];self.assertEqual(d3["B/A^2"]["rational_values"],["6"])
        self.assertTrue(same_weighted_point(clebsch(x**6+y**6),(Q(1),Q(6),Q(-36),Q(0))))
        d4=slice_jump(4,2)["classification"];self.assertEqual(d4["B/A^2"]["rational_values"],["0"])
        self.assertEqual(slice_jump(5,2)["dimension"],-1)

    def test_degenerate_forms(self):
        prof=degenerate_profile(range(3,9))
        kern5={k:[r["kernel"] for r in v if r["degree"]==5] for k,v in prof["fixed"].items()}
        self.assertEqual({k for k,v in kern5.items() if v},{"x^6","x^5y","x^4y^2","x^4y(x-y)"})
        s5=[r for r in prof["x^2y^2(x-y)(x-sy)"] if r["degree"]==5][0]
        self.assertEqual((s5["generic_kernel"],s5["jumps"]),(0,[]))
        # x^2y^2(x-y)(x-sy) at s=-1 is not on the degree-5 locus; (x-y)^4(x^2+4xy+y^2) is (fourfold root).
        self.assertEqual(_rank(correction_matrix(s_form(-1),5),6),6)
        f=(x-y)**4*(x*x+4*x*y+y*y);self.assertLess(_rank(correction_matrix(f,5),6),6)


if __name__=="__main__":unittest.main()
