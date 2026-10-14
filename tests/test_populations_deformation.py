import unittest,random,itertools
from fractions import Fraction as Q
from perfectjet.populations import SelectionPopulation
from perfectjet.polynomial import Poly
from perfectjet.deformation import stationary_response,relation_response,protection,deformation_receipt


def feasible(costs,caps,bits):
    return all(sum(c[k] for c,b in zip(costs,bits) if b)<=caps[k] for k in range(len(caps)))


class PopulationTests(unittest.TestCase):
    def test_attribution_and_inclusion_match_enumeration(self):
        rng=random.Random(3)
        for _ in range(25):
            n=rng.randint(2,7);m=rng.randint(1,3)
            costs=[tuple(rng.randint(0,3) for _ in range(m)) for _ in range(n)]
            caps=tuple(rng.randint(0,6) for _ in range(m));prof=[rng.randint(0,4) for _ in range(n)]
            p=SelectionPopulation(costs,caps,prof)
            allb=list(itertools.product((0,1),repeat=n));feas=[b for b in allb if feasible(costs,caps,b)]
            att=p.attribution()
            self.assertEqual(att["feasible"],len(feas))
            for row in att["constraints"]:
                k=row["constraint"]
                only=[b for b in allb if not feasible(costs,caps,b)
                      and all(sum(c[j] for c,x in zip(costs,b) if x)<=caps[j] for j in range(m) if j!=k)]
                self.assertEqual(row["removed_only_by_this"],len(only))
            best=max(sum(pr for pr,x in zip(prof,b) if x) for b in feas)
            opt=[b for b in feas if sum(pr for pr,x in zip(prof,b) if x)==best]
            for r in p.inclusion_profile():
                i=r["project"]
                self.assertEqual(r["feasible_share"],Q(sum(b[i] for b in feas),len(feas)))
                self.assertEqual(r["optimal_share"],Q(sum(b[i] for b in opt),len(opt)))


class DeformationTests(unittest.TestCase):
    def test_response_matches_finite_difference_root(self):
        # V = x^3/3 - x + t x: stationary x = sqrt(1 - t); dx/dt at t=0 is -1/2.
        x,t=Poly.variable(0,2),Poly.variable(1,2)
        v=x**3*Q(1,3)-x+t*x
        dx,h=stationary_response(v,1,(Q(1),0))
        self.assertEqual(dx,[[Q(-1,2)]]);self.assertEqual(h,[[Q(2)]])

    def test_mirror_relation_is_symmetry_protected(self):
        r=deformation_receipt()
        self.assertTrue(r["mirror_relation"]["symmetry_protects"])
        self.assertEqual(r["mirror_relation"]["dR_dtheta"],[Q(-1),Q(-3),Q(0)])
        self.assertFalse(r["location_relation"]["symmetry_protects"])
        self.assertIn("accidental",r["location_relation"]["verdict"])

    def test_degenerate_point_rejected(self):
        x,t=Poly.variable(0,2),Poly.variable(1,2)
        with self.assertRaises(ValueError):stationary_response(x**4+t*x,1,(Q(0),0))
        with self.assertRaises(ValueError):stationary_response(x**2+t*x,1,(Q(1),0))


if __name__=="__main__":unittest.main()
