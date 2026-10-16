import json
import unittest
from fractions import Fraction as Q

from perfectjet.recovered_partners import (
    archived_r5_pair,archived_r5,cubic_partner,quartic_partner,
    degree12_partner_report,sextic_partners,evaluate,receipt,
)
from perfectjet.polynomial import Poly
from perfectjet.transvectants import transvectant


def from_record(records):
    return Poly({tuple(r["exponents"]):Q(r["coefficient"]) for r in records})


class RecoveredPartnerTests(unittest.TestCase):
    def test_archived_pair_is_active_exactly_not_only_numerically(self):
        f,g=archived_r5_pair();r=archived_r5()
        self.assertEqual(transvectant(f,g,3),0)
        self.assertEqual(transvectant(f,g,5),0)
        self.assertNotEqual(transvectant(f,g,1),0)
        self.assertEqual(r["dimensions"],{"degree":5,"kernel_dimension":1,"active_dimension":1})
        self.assertTrue(r["partner_squarefree"])
        self.assertEqual(from_record(r["form"]),f)
        self.assertEqual(from_record(r["partner"]),g)

    def test_eliminant_metadata_has_independently_evaluated_exact_product(self):
        r=archived_r5()["eliminant"]
        self.assertEqual(r["degree"],20)
        self.assertEqual(r["coefficients_ascending"][-1],3)
        self.assertFalse(r["maximal_minor_elimination_regenerated"])
        for b in (Q(-7,3),0,1,Q(3,2),7):
            expected=b**6*(b-1)**6*(b*b-3*b+3)*(b*b-b+1)*(b*b+b+1)*(3*b*b-3*b+1)
            actual=sum(c*b**i for i,c in enumerate(r["coefficients_ascending"]))
            self.assertEqual(actual,expected)
            self.assertEqual(Q(archived_r5(str(b))["eliminant"]["evaluation"]["value"]),expected)

    def test_cubic_criterion_constructs_replayed_kernel(self):
        x,y=Poly.variable(0),Poly.variable(1)
        for lam,exists in [(1,False),(20,True),(0,True)]:
            f=x**6+lam*x**3*y**3+y**6;r=cubic_partner(f)
            self.assertTrue(r["identity_replayed"])
            self.assertEqual(r["partner_exists"],exists)
            for item in r["kernel_basis"]:
                g=from_record(item["partner"])
                self.assertEqual(transvectant(f,g,3),0)
                self.assertEqual(transvectant(f,g,5),0)

    def test_quartic_distinguishes_commuting_from_active(self):
        x,y=Poly.variable(0),Poly.variable(1)
        active=quartic_partner(x**6+x**3*y**3+y**6)
        commuting=quartic_partner((x*x+y*y)**3)
        self.assertTrue(active["gates"]["active"])
        self.assertTrue(commuting["universal_gates_replayed"])
        self.assertFalse(commuting["gates"]["active"])
        self.assertEqual(commuting["dimensions"]["active_dimension"],0)

    def test_degree12_construction_replays_without_claiming_converse(self):
        r=degree12_partner_report()
        self.assertTrue(r["form_squarefree"])
        self.assertTrue(r["on_invariant_hypersurface"])
        self.assertTrue(r["partner_nonzero"] and r["gate_identities_replayed"])
        f,g=from_record(r["form"]),from_record(r["partner"])
        self.assertEqual(transvectant(f,g,3),0)
        self.assertEqual(transvectant(f,g,5),0)
        self.assertEqual(r["converse_status"],"open")
        self.assertFalse(r["full_grid_evaluated"])
        outside=sextic_partners()["degree12"]
        self.assertFalse(outside["on_invariant_hypersurface"])
        self.assertTrue(outside["gate_identities_replayed"])

    def test_dispatch_json_and_input_validation(self):
        json.dumps(receipt())
        r=evaluate("quartic",{"form":archived_r5()["form"]})
        self.assertTrue(r["universal_gates_replayed"])
        for operation,params in [("unknown",{}),("r5",{"parameter_b":0.2}),
                                 ("sextic",{"form":[{"exponents":[1,1],"coefficient":"1"}]})]:
            with self.assertRaises(ValueError):evaluate(operation,params)


if __name__=="__main__":unittest.main()
