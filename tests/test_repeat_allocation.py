import unittest
import random
from fractions import Fraction as Q
from perfectjet.repeat_allocation import RepeatPlanPopulation, floor_sum

class RepeatAllocationTests(unittest.TestCase):
    def test_floor_sum_brute(self):
        rng = random.Random(44)
        for _ in range(3000):
            n,m,a,b = rng.randrange(100),rng.randrange(1,100),rng.randrange(200),rng.randrange(200)
            self.assertEqual(floor_sum(n,m,a,b),sum((a*i+b)//m for i in range(n)))

    def test_floor_sum_extreme(self):
        n = 10**100
        self.assertEqual(floor_sum(n,1,1,0),n*(n-1)//2)
        self.assertEqual(floor_sum(n,7,0,21),3*n)

    def test_population_matches_exhaustive(self):
        rng = random.Random(72)
        for _ in range(360):
            sa,na,sb,nb,g,q = [Q(rng.randrange(0,12),rng.randrange(1,5)) for _ in range(6)]
            budget = rng.randrange(0,21); ka,kb,ca,cb = [rng.randrange(1,4) for _ in range(4)]
            target = rng.choice(['latent','next_attempt'])
            p = RepeatPlanPopulation.build(sa,na,sb,nb,g,q,budget=budget,known_a=ka,known_b=kb,cost_a=ca,cost_b=cb,target=target)
            def var(s,n,k):return (s*n/(n+k*s) if s and n else Q(0))+(n if target=='next_attempt' else 0)
            def good(a,b):
                if not g:return False
                if not q:return True
                va,vb = var(sa,na,a),var(sb,nb,b)
                d = (g/q)**2-va-vb
                return d>0 and d*d>4*va*vb
            plans = [(a,b) for a in range(ka,ka+budget//ca+1) for b in range(kb,kb+budget//cb+1)
                     if ca*(a-ka)+cb*(b-kb)<=budget and good(a,b)]
            self.assertEqual(p.count(),len(plans))
            for i,plan in enumerate(plans):
                self.assertEqual(p.unrank(i),plan);self.assertEqual(p.rank(plan),i)
            if plans:
                costs = [ca*(a-ka)+cb*(b-kb) for a,b in plans]; best = min(costs)
                self.assertEqual(p.minimum(),{'additional_cost':best,'plans':[x for x,c in zip(plans,costs) if c==best]})
            else:self.assertIsNone(p.minimum()['additional_cost'])

    def test_strict_floor_is_impossible(self):
        p = RepeatPlanPopulation.build(1,1,1,1,2,1,budget=10**100)
        self.assertEqual(p.count(),0)
        with self.assertRaises(ValueError):p.unrank(0)

    def test_large_population_with_tiny_frontier(self):
        b = 10**30
        p = RepeatPlanPopulation.build(1,1,1,1,'2.3',1,budget=b)
        self.assertEqual(p.minimum(),{'additional_cost':3,'plans':[(2,3),(3,2)]})
        self.assertEqual(p.count(),(b+1)*(b+2)//2-10)
        self.assertEqual(len(p.frontier),5)
        rng = random.Random(4)
        for r in [0,1,p.count()-1]+[rng.randrange(p.count()) for _ in range(50)]:
            self.assertEqual(p.rank(p.unrank(r)),r)
        self.assertGreaterEqual(p.rank(p.sample(rng)),0)

    def test_zero_radius(self):
        p = RepeatPlanPopulation.build(2,3,4,5,1,0,budget=10**30)
        self.assertEqual(p.count(),(10**30+1)*(10**30+2)//2)
        self.assertEqual(p.minimum()['additional_cost'],0)

    def test_bad_inputs(self):
        for args in (dict(budget=-1),dict(budget=1,cost_a=0),dict(budget=True),dict(budget=2,target='wrong')):
            with self.assertRaises(ValueError):RepeatPlanPopulation.build(1,1,1,1,1,1,**args)
        p = RepeatPlanPopulation.build(1,1,1,1,3,1,budget=10)
        for r in (-1,p.count(),True):
            with self.assertRaises(ValueError):p.unrank(r)
        with self.assertRaises(ValueError):p.rank((0,0))
        with self.assertRaises(ValueError):floor_sum(1,0,1,1)

if __name__ == '__main__': unittest.main()
