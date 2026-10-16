import itertools
import json
import unittest
from fractions import Fraction as Q

from perfectjet.algebra_bridges import (
    quadratic_population, quadratic_history_bridge, pell_history_bridge,
    bounded_invariant_laws, parameter_integer_analysis, evaluate, receipt,
)
from perfectjet.invariants import clebsch
from perfectjet.parametric import sextic_family


def multiply(p,q,d):
    return p[0]*q[0]+d*p[1]*q[1],p[0]*q[1]+p[1]*q[0]


def relation_value(relation,invariants):
    total=Q(0)
    for monomial,coefficient in relation.items():
        term=Q(coefficient)
        for factor in monomial.split("*"):
            if factor!="1":
                name,power=factor.split("^");term*=invariants["ABCD".index(name)]**int(power)
        total+=term
    return total


class AlgebraBridgeTests(unittest.TestCase):
    def test_original_quadratic_witnesses_match_direct_search(self):
        for p in [(2,1,0,7),(1,0,3,1),(1,-1,10,0),(1,1,0,5)]:
            r=quadratic_population(*p,nmax=100)
            k,a,b,c=p
            direct=[n for n in range(101) if any(k*y*y==a*n*n+b*n+c for y in range(200))]
            self.assertEqual([int(w["n"]) for w in r["witnesses"]],direct)
            self.assertTrue(all(w["original_replayed"] and w["norm_replayed"] for w in r["witnesses"]))
        r=quadratic_population(2,1,0,7,nmax=10**12)
        self.assertEqual(r["count"],31)
        self.assertEqual(r["orbit_structure"]["asymptotic"]["logarithmic_weight"],"2")

    def test_quadratic_histories_match_word_enumeration_in_original_domain(self):
        for p in [(2,1,0,7),(1,2,1,-1)]:
            for horizon in (0,1,6,7):
                r=quadratic_history_bridge(*p,horizon=horizon,modulus=3,accepted_n=[1,2],costs=[2,1],budget=10)
                k,a,b,c=p;accepted=[]
                for word in itertools.product((0,1),repeat=horizon):
                    point=tuple(r["seed"]);cost=0
                    for action in word:
                        point=multiply(point,(r["unit"][0],r["unit"][1]*(1 if action==0 else -1)),r["D"])
                        cost+=2 if action==0 else 1
                    X,Y=point
                    if (X-b)%(2*a):continue
                    n=(X-b)//(2*a)
                    if n>=0 and n%3 in (1,2) and cost<=10:
                        self.assertEqual(k*Y*Y,a*n*n+b*n+c);accepted.append(word)
                self.assertEqual(int(r["count"]),len(accepted))
                self.assertTrue(r["binomial_replayed"])
                if accepted:
                    w=r["witness"]
                    self.assertEqual(w["actions"],["advance" if a==0 else "retreat" for a in accepted[0]])
                    self.assertTrue(w["rank_replayed"] and w["endpoint"]["original_replayed"] and w["endpoint"]["nonnegative"])

    def test_modular_pell_histories_retain_words_and_exact_rank(self):
        r=pell_history_bridge(2,[3,2],[1,0],35,horizon=100,accepted_x=[1])
        self.assertEqual(r["count"],"422550200076076467165567735126")
        self.assertEqual(r["count"],r["independent_binomial_count"])
        self.assertTrue(r["witness"]["rank_replayed"])
        r=pell_history_bridge(2,[3,2],[1,0],5,horizon=8,accepted_x=[1],costs=[3,1],budget=12,word_rank=1)
        words=[]
        for word in itertools.product((0,1),repeat=8):
            point=(1,0)
            for action in word:point=multiply(point,(3,2 if action==0 else -2),2)
            if point[0]%5==1 and sum(3 if a==0 else 1 for a in word)<=12:words.append(word)
        self.assertEqual(int(r["count"]),len(words))
        self.assertEqual(r["witness"]["actions"],["advance" if a==0 else "retreat" for a in words[1]])

    def test_bounded_law_is_specific_to_cell_and_not_a_fitted_sample(self):
        inv=[{(1,0):1},{(2,0):1,(0,1):1},{(3,0):1},{(5,0):1}]
        r=bounded_invariant_laws([{(0,1):1}],max_weight=2,invariants=inv)
        self.assertEqual(len(r["relations"]),1)
        law=r["relations"][0]["relation"]
        for t in (-100,Q(2,3),0,17):self.assertEqual(relation_value(law,[t,t*t,t**3,t**5]),0)
        self.assertNotEqual(relation_value(law,[2,5,8,32]),0)
        self.assertEqual(bounded_invariant_laws([],2,invariants=inv)["relations"],[])
        with self.assertRaises(ValueError):bounded_invariant_laws([{(0,1):1}],2,inequations=[{(0,1):1}],invariants=inv)

    def test_default_clebsch_law_replays_on_exact_sextics(self):
        curve={(4,0):1,(2,2):Q(-16,3),(0,4):Q(256,81),(0,3):Q(-2560,27),(2,0):-400,(0,2):Q(6400,9)}
        r=bounded_invariant_laws([curve],2)
        self.assertTrue(r["relations"])
        law=r["relations"][0]["relation"]
        for a,b in [(0,0),(20,0),(4,6),(24,-9)]:self.assertEqual(relation_value(law,clebsch(sextic_family(a,b))),0)
        self.assertNotEqual(relation_value(law,clebsch(sextic_family(1,1))),0)

    def test_same_rank_cell_can_have_different_integer_answers(self):
        matrix=[[{(1,):1},0],[0,2]]
        yes=parameter_integer_analysis(matrix,[1],rhs=[1,2])
        no=parameter_integer_analysis(matrix,[2],rhs=[1,2])
        zero=parameter_integer_analysis(matrix,[0],rhs=[1,2])
        self.assertEqual(yes["matching_cell"],no["matching_cell"])
        self.assertEqual(yes["rank"],no["rank"])
        self.assertTrue(yes["integer_solution"]["solvable"])
        self.assertFalse(no["integer_solution"]["solvable"])
        self.assertTrue(no["integer_solution"]["rational"])
        self.assertFalse(zero["integer_solution"]["rational"])
        for r in (yes,no,zero):self.assertTrue(r["integer_solution"]["certificate_replayed"])
        y=list(map(Q,no["integer_solution"]["certificate"]))
        self.assertTrue(all(x.denominator==1 for x in (2*y[0],2*y[1])))
        self.assertNotEqual((y[0]+2*y[1]).denominator,1)
        fractional=parameter_integer_analysis(matrix,["1/2"],rhs=[1,2])
        self.assertEqual(fractional["integer_status"],"nonintegral specialization")
        self.assertIsNone(fractional["smith"])

    def test_json_dispatch_and_explicit_input_limits(self):
        r=receipt();json.dumps(r)
        self.assertTrue(r["quadratic_histories"]["binomial_replayed"])
        out=evaluate("parameter_smith",{"matrix":[[[{"exponents":[1],"coefficient":"1"}]]],"point":[2],"rhs":[1]})
        self.assertFalse(out["integer_solution"]["solvable"])
        for name,params in [("unknown",{}),("quadratic",{"k":1,"a":0,"b":0,"c":1,"nmax":100,"max_scan":10}),
                            ("quadratic_histories",{"k":1,"a":1,"b":0,"c":5}),
                            ("parameter_smith",{"matrix":[[0.5]],"point":[0]})]:
            with self.assertRaises(ValueError):evaluate(name,params)


if __name__=="__main__":unittest.main()
