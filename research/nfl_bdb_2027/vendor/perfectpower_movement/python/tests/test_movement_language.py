import unittest,random,math,itertools
from fractions import Fraction
from perfectpower.movement_language import Edge,MovementLanguage,segment_channel,phase_summary,tensor_signature

class LanguageTests(unittest.TestCase):
    def test_exhaustive_reference(self):
        rng=random.Random(417)
        for n in range(4,11):
            costs=[[rng.randrange(0,6)/3 for _ in range(3)] for _ in range(n)]
            c=segment_channel(costs,[1]*3,[n]*3)
            paths=[c.unrank(i) for i in range(c.population)]
            self.assertEqual(c.population,math.comb(n-1,2))
            z=0;mean=[0.]*3;second=[0.]*3;edge=[0.]*len(c.edges)
            for rank,path in enumerate(paths):
                self.assertEqual(c.rank(path),rank)
                self.assertEqual(c.conditional_count(path),1)
                weight=math.exp(sum(c.edges[i].log_weight for i in path));z+=weight
                reward=[sum(c.edges[i].reward[j] for i in path) for j in range(3)]
                for j,r in enumerate(reward):mean[j]+=weight*r;second[j]+=weight*r*r
                for i in path:edge[i]+=weight
            m=c.moments();self.assertAlmostEqual(math.log(z),c.log_partition,places=11)
            for j in range(3):
                self.assertAlmostEqual(m['mean'][j],mean[j]/z,places=10)
                self.assertAlmostEqual(m['variance'][j],second[j]/z-(mean[j]/z)**2,places=9)
            for p,q in zip(c.edge_posterior(),edge):self.assertAlmostEqual(p,q/z,places=11)
            s=phase_summary(c)
            for row in s['occupancy']:self.assertAlmostEqual(sum(row),1.,places=11)
            for bank in s['boundary_probability']:self.assertAlmostEqual(sum(bank.values()),1.,places=11)
    def test_duration_windows(self):
        c=segment_channel([[0,0,0]]*9,[2,2,2],[4,4,4],boundary_windows=[(2,3),(5,6),(9,9)])
        expected=[]
        for x in itertools.product(range(2,5),repeat=3):
            if sum(x)==9 and 2<=x[0]<=3 and 5<=sum(x[:2])<=6:expected.append(x)
        self.assertEqual(c.population,len(expected))
        for i in range(c.population):self.assertIn(tuple(c.edges[j].label[2]-c.edges[j].label[1] for j in c.unrank(i)),expected)
    def test_exact_rational(self):
        c=MovementLanguage(4,[Edge(0,1,math.log(.5),(2,)),Edge(0,2,math.log(.25),(3,)),Edge(1,3,0.,(4,)),Edge(2,3,0.,(-2,))],0,[3])
        r=c.exact_weighted([Fraction(1,2),Fraction(1,4),1,1]);self.assertEqual(r['partition'],Fraction(3,4));self.assertEqual(r['mean'],[Fraction(13,3)]);self.assertEqual(r['variance'],[Fraction(50,9)])
        self.assertAlmostEqual(c.moments()['mean'][0],float(r['mean'][0]))
        with self.assertRaises(ValueError):c.exact_weighted([.5,.25,1,1])
    def test_huge_language(self):
        c=segment_channel([[0]*12]*150,[1]*12,[150]*12,max_edges=200000)
        self.assertEqual(c.population,math.comb(149,11))
        self.assertGreater(c.population,2**53)
        for r in (0,2**53+7,c.population-1):self.assertEqual(c.rank(c.unrank(r)),r)
    def test_empty(self):
        c=segment_channel([[0,0]]*3,[2,2],[3,3]);self.assertEqual(c.population,0)
        self.assertEqual(c.edge_posterior(),[0.]*len(c.edges))
        for fn in (c.sample,c.map_path,c.moments):
            with self.assertRaises(ValueError):fn()
    def test_budgets_and_validation(self):
        with self.assertRaises(ValueError):MovementLanguage(2,[Edge(1,0)],0,[1])
        with self.assertRaises(ValueError):MovementLanguage(2,[Edge(0,1,float('nan'))],0,[1])
        with self.assertRaises(ValueError):segment_channel([[0,0]]*20,[1,1],[20,20],max_edges=1)
        with self.assertRaises(ValueError):segment_channel([[0,0]]*3,[True,1],[3,3])
        with self.assertRaises(ValueError):segment_channel([[0,0]]*3,[1,1],[3,3],temperature=0)
    def test_map_and_sampler(self):
        c=MovementLanguage(3,[Edge(0,2,-1000,(0,)),Edge(0,1,1000,(1,)),Edge(1,2,1000,(2,))],0,[2])
        self.assertEqual(c.map_path(),[1,2]);self.assertEqual(c.sample(10),[1,2]);self.assertEqual(c.sample(10),c.sample(10))
        self.assertEqual(c.moments()['mean'],[3.])
    def test_variance_large_offset(self):
        c=MovementLanguage(2,[Edge(0,1,0.,(10**12-1,)),Edge(0,1,0.,(10**12+1,))],0,[1])
        self.assertEqual(c.moments()['variance'],[1.])
    def test_support(self):
        c=segment_channel([[0,0]]*10,[1,1],[9,9]);m=c.moments()
        self.assertEqual(m['support_min'],[1.,1.]);self.assertEqual(m['support_max'],[9.,9.]);self.assertAlmostEqual(m['entropy_nats'],math.log(9))
    def test_signature_chen_and_order(self):
        a=tensor_signature([(0,0),(1,0),(1,1)]);b=tensor_signature([(0,0),(0,1),(1,1)])
        self.assertEqual(a[1],b[1]);self.assertEqual(a[2][(0,1)],1.);self.assertEqual(b[2][(0,1)],0.)
        self.assertEqual(a[2][(1,0)],0.);self.assertEqual(b[2][(1,0)],1.)
        left=tensor_signature([(0,0),(1,0)]);right=tensor_signature([(1,0),(1,1)])
        for k in range(4):
            for w in a[k]:self.assertAlmostEqual(a[k][w],sum(left[j][w[:j]]*right[k-j][w[j:]] for j in range(k+1)))
    def test_signature_translation_resampling(self):
        a=tensor_signature([(0,0),(1,2)]);b=tensor_signature([(3,7),(3.5,8),(4,9)])
        for k in range(4):
            for w in a[k]:self.assertAlmostEqual(a[k][w],b[k][w])

if __name__=='__main__':unittest.main()
