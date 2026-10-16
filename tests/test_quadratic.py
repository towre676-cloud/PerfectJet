import unittest,random
from fractions import Fraction
from math import log, sqrt
from perfectjet.quadratic import QuadraticSquare,fundamental_unit,nagell_seeds,pell_solutions,quadratic_receipt
from perfectjet.engine import arithmetic_problem


def brute(q,n):return [m for m in range(n+1) if q.y_of(m) is not None]


class QuadraticTests(unittest.TestCase):
    def test_fundamental_units(self):
        for d,u in [(2,(3,2)),(3,(2,1)),(7,(8,3)),(13,(649,180)),(61,(1766319049,226153980))]:
            self.assertEqual(fundamental_unit(d),u)

    def test_nagell_seeds_reach_every_solution(self):
        for d,n0 in [(2,-7),(7,9),(13,-4),(5,11),(6,10),(2,1)]:
            sols,_,_=pell_solutions(d,n0,5000)
            box={(x,y) for y in range(-400,401) for x in range(-5000,5001) if x*x-d*y*y==n0}
            self.assertEqual({s for s in sols if abs(s[1])<=400},box)

    def test_compiled_hits_equal_brute_force(self):
        rng=random.Random(2)
        cases=[(2,1,0,7),(1,8,8,1),(1,1,0,5),(1,0,3,1),(1,-1,10,0),(2,0,0,8),(1,1,0,0),(1,0,-3,1)]
        cases+=[(rng.randint(1,4),rng.randint(-3,6),rng.randint(-6,6),rng.randint(-9,9)) for _ in range(150)]
        for c in cases:
            q=QuadraticSquare(*c);self.assertEqual(q.hits(1500),brute(q,1500),c)

    def test_remote_index_is_replayed(self):
        q=QuadraticSquare(2,1,0,7)
        for o in q.orbit_structure()["orbits"]:
            r=q.nth_on_orbit(o,300)
            if r:self.assertTrue(q.holds(*r))
        self.assertTrue(all(row[2] for row in quadratic_receipt()["pell7_remote_index_1000"]))

    def test_branches_and_report(self):
        self.assertEqual(QuadraticSquare(1,1,0,5).branch,"finite")
        self.assertEqual(QuadraticSquare(1,0,3,1).branch,"linear")
        self.assertEqual(QuadraticSquare(2,1,0,7).branch,"pell")
        self.assertEqual(QuadraticSquare(1,-1,10,0).branch,"finite")
        r=arithmetic_problem(1,8,8,1,10**6)
        self.assertEqual(r["answer"]["first_hits"][:4],[0,2,14,84])
        self.assertIn("Nagell",r["answer"]["completeness"])

    def test_positive_asymptotic_removes_signed_duplicate_tails(self):
        q=QuadraticSquare(2,1,0,7)
        s=q.orbit_structure(); a=s["asymptotic"]
        self.assertEqual(len(s["orbits"]),4)
        self.assertEqual(len(s["positive_orbits"]),2)
        self.assertEqual(a["logarithmic_weight"],"2")
        self.assertAlmostEqual(a["coefficient"],2/log(3+sqrt(8)))
        # Independently generated positive n sequences for n^2+7=2y^2.
        bound=10**12; hits=set()
        for n,y in ((1,2),(5,4)):
            while n<=bound:
                hits.add(n);n,y=3*n+4*y,2*n+3*y
        self.assertEqual(len(hits),31)
        self.assertEqual(q.hits(bound),sorted(hits))
        self.assertLess(abs(len(hits)-a["coefficient"]*log(bound)),1)

    def test_positive_unit_classes_deduplicate_endpoint_and_conjugate_seeds(self):
        # Norm +8 has conjugate Nagell representatives in the same unit class;
        # norm -8 has X=0 and duplicate sign choices. Each counts one n tail.
        for c in (-1,1):
            s=QuadraticSquare(1,2,0,c).orbit_structure()
            self.assertEqual(s["asymptotic"]["logarithmic_weight"],"1")
            self.assertEqual(len(s["positive_orbits"]),1)
        # Congruence filtering gives a rational weight, not an integer orbit count.
        q=QuadraticSquare(1,2,1,-1);s=q.orbit_structure()
        self.assertEqual(Fraction(s["asymptotic"]["logarithmic_weight"]),Fraction(1,2))
        self.assertEqual(q.hits(5000),brute(q,5000))

    def test_integer_coefficients_and_orbit_indices_are_required(self):
        for p in ((True,1,0,7),(2,1.0,0,7),(2,1,0,"7")):
            with self.assertRaises(ValueError):QuadraticSquare(*p)
        q=QuadraticSquare(2,1,0,7);o=q.orbit_structure()["orbits"][0]
        for index in (-1,1.5,True):
            with self.assertRaises(ValueError):q.nth_on_orbit(o,index)


if __name__=="__main__":unittest.main()
