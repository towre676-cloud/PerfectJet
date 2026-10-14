import unittest,random
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


if __name__=="__main__":unittest.main()
