import unittest,random
from fractions import Fraction as Q
from perfectjet.polynomial import Poly
from perfectjet.exact import rank,nullspace
from perfectjet.readout import (identify,demand_readout,repair,adds_direction,posterior_covariance,readout_variance,
                                value_of_information,pooling_reliance,inverse,readout_receipt)
from perfectjet.decisions import certified_choice,refine_until_settled,defect_split,decisions_receipt
from perfectjet.engine import adaptive_closure,sensing,readout_problem,integer_problem,partner_problem,engine_receipt

phi=lambda d:[Q(1),Q(d[0]),Q(d[1]),Q(d[0])*Q(d[1])]


class ReadoutTests(unittest.TestCase):
    def test_identify_weights_and_witness(self):
        rng=random.Random(2)
        for _ in range(60):
            x=[[Q(rng.randint(-3,3)) for _ in range(4)] for _ in range(rng.randint(1,4))]
            h=[Q(rng.randint(-3,3)) for _ in range(4)]
            r=identify(x,h)
            inspan=rank(x+[h],4)==rank(x,4)
            self.assertEqual(r["identified"],inspan)
            if inspan:
                self.assertEqual([sum(c*row[k] for c,row in zip(r["weights"],x)) for k in range(4)],h)
            else:
                n=r["witness"]
                self.assertTrue(all(sum(a*b for a,b in zip(row,n))==0 for row in x))
                self.assertNotEqual(sum(a*b for a,b in zip(h,n)),0)

    def test_two_fits_disagree_on_readout(self):
        x=[phi((5,a)) for a in (30,60,90)]
        h=demand_readout(phi,[(1,(4,45)),(1,(6,90))])
        r=identify(x,h);self.assertFalse(r["identified"])
        beta=[Q(1),Q(2),Q(3),Q(4)];beta2=[b+v for b,v in zip(beta,r["witness"])]
        fit=lambda b:[sum(p*q for p,q in zip(row,b)) for row in x]
        self.assertEqual(fit(beta),fit(beta2))
        self.assertNotEqual(sum(p*q for p,q in zip(h,beta)),sum(p*q for p,q in zip(h,beta2)))

    def test_repeats_never_repair_identification(self):
        x=[phi((5,a)) for a in (30,60,90)];h=demand_readout(phi,[(1,(4,45)),(1,(6,90))])
        repeats=[phi((5,a)) for a in (10,20,120,150)]
        self.assertTrue(all(not adds_direction(x,r) for r in repeats))
        self.assertIsNone(repair(x,h,repeats,max_new=3)["needed"])
        fix=repair(x,h,repeats+[phi((7,60)),phi((7,120))])
        self.assertEqual(fix["needed"],2);self.assertEqual(fix["rows"],[4,5])

    def test_minimality_of_repair(self):
        rng=random.Random(4)
        for _ in range(20):
            x=[[Q(rng.randint(-2,2)) for _ in range(4)] for _ in range(2)]
            h=[Q(rng.randint(-2,2)) for _ in range(4)]
            cands=[[Q(rng.randint(-2,2)) for _ in range(4)] for _ in range(4)]
            fix=repair(x,h,cands)
            if fix["needed"]:
                self.assertTrue(identify(x+[cands[i] for i in fix["rows"]],h)["identified"])
                from itertools import combinations
                for k in range(fix["needed"]):
                    for idx in combinations(range(4),k):
                        self.assertFalse(identify(x+[cands[i] for i in idx],h)["identified"])

    def test_posterior_and_voi(self):
        prior=[[Q(int(i==j))*4 for j in range(4)] for i in range(4)]
        x=[phi((5,a)) for a in (30,60,90)];h=demand_readout(phi,[(1,(4,45)),(1,(6,90))])
        cov=posterior_covariance(x,Q(1),prior)
        p=inverse(cov)
        self.assertEqual([[sum(a*b for a,b in zip(r,c)) for c in zip(*cov)] for r in p],
                         [[Q(int(i==j)) for j in range(4)] for i in range(4)])
        voi=value_of_information(x,h,[phi((5,120)),phi((7,60))],Q(1),prior)
        self.assertEqual(voi["candidates"][0]["candidate"],1)
        self.assertTrue(all(c["reduction"]>=0 for c in voi["candidates"]))
        self.assertGreater(pooling_reliance(x,h,Q(1),prior),pooling_reliance(x+[phi((7,60)),phi((7,120))],h,Q(1),prior))

    def test_receipt(self):
        r=readout_receipt()
        self.assertFalse(r["unsupported_readout"]["identified"])
        self.assertTrue(r["supported_readout_identified"])
        self.assertEqual(r["repair"]["needed"],2)


class DecisionTests(unittest.TestCase):
    def test_certified_choice(self):
        self.assertTrue(certified_choice({"a":(10,1),"b":(7,1)})["settled"])
        d=certified_choice({"a":(10,2),"b":(7,2)});self.assertFalse(d["settled"]);self.assertEqual(d["contenders"],["a","b"])
        self.assertEqual(certified_choice({"a":(10,1),"b":(7,1)},maximize=False)["choice"],"b")

    def test_refinement_never_flips_true_order(self):
        rng=random.Random(8)
        for _ in range(30):
            truth={i:Q(rng.randint(-100,100),7) for i in range(5)}
            if len(set(truth.values()))<5:continue
            ev=lambda a,k:(truth[a]+Q(rng.choice([-1,1]),2**(k+2)),Q(1,2**(k+1)))
            out=refine_until_settled(list(truth),ev)
            self.assertTrue(out["settled"]);self.assertEqual(out["choice"],max(truth,key=truth.get))
            self.assertLessEqual(out["evaluations"],out["uniform_evaluations"])

    def test_defect_split_exact_for_true_reduction(self):
        # V spans an invariant subspace: A V = V G and B = V H, so the error stays zero.
        a=[[2,1],[0,3]];v=[[1],[0]];g=[[2]];b=[[1],[0]];h=[[1]]
        out=defect_split(a,b,v,g,h,[1,0],[1],[[1],[2],[3]])
        self.assertTrue(out["exact_reduction"]);self.assertTrue(all(s["error"]==0 for s in out["steps"]))
        self.assertTrue(all(s["error"]<=s["bound"] for s in decisions_receipt()["defect_split"]["steps"]))


class EngineTests(unittest.TestCase):
    def test_closure_finds_missing_monomial_and_minimal_space(self):
        x,y=Poly.variable(0),Poly.variable(1)
        r=adaptive_closure([x*Q(1,2),y*Q(1,3)+x*x],[y])
        self.assertTrue(r["answer"]["closed"]);self.assertEqual(r["representation"]["features"],[[0,1],[2,0]])
        eig=adaptive_closure([x*Q(1,2),y*Q(1,3)+x*x],[y+12*x*x])
        self.assertEqual(eig["answer"]["minimal_dimension"],1)

    def test_degree_growth_stops(self):
        x,y=Poly.variable(0),Poly.variable(1)
        r=adaptive_closure([x*x+y,y],[x],max_degree=6)
        self.assertEqual(r["obstruction"]["class"],"degree_growth");self.assertIsNone(r["answer"])

    def test_adapters(self):
        s=sensing([[1,1,0]],[[1,-1,0]],candidates=[[0,0,1],[1,0,0]])
        self.assertEqual(s["obstruction"]["class"],"structural_invisibility");self.assertEqual(s["next"],{"add_sensors":[1]})
        self.assertTrue(sensing([[1,0],[0,1]],[[1,1]])["answer"]["recoverable"])
        self.assertEqual(integer_problem([[2,0],[0,3]],[1,3])["obstruction"]["class"],"divisibility")
        self.assertEqual(integer_problem([[2,0],[0,3]],[4,3])["answer"]["solution"],[2,1])
        p=partner_problem(16,-9,6);self.assertIsNotNone(p["answer"])
        self.assertEqual(partner_problem(0,3,8)["obstruction"]["class"],"no_active_partner")
        keys={"question","representation","preserved","identities","answer","obstruction","obligations","next","history"}
        for rep in engine_receipt().values():self.assertEqual(set(rep),keys)


if __name__=="__main__":unittest.main()
