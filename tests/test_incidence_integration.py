"""Cross-branch contracts: stable catalogue and exact public Math Lab behavior."""
import json
import unittest
from pathlib import Path
from perfectjet.mathlab import evaluate
from perfectjet.recovered_partners import incidence_report

class IntegrationTests(unittest.TestCase):
    def test_public_lab_custom_quintic_and_activity(self):
        r=evaluate({'lab':'partners','params':{'operation':'incidence','degree':5,'form':[{'exponents':[6,0],'coefficient':1},{'exponents':[3,3],'coefficient':'40/7'},{'exponents':[0,6],'coefficient':1}]}})['details']
        self.assertEqual(r['kernel_dimension'],1)
        self.assertTrue(r['kernel_basis'][0]['gates']['active'])
        self.assertFalse(r['external_solvers_rerun'])
        json.dumps(r)
    def test_commuting_sextic_is_not_active(self):
        r=incidence_report([{'exponents':[3,3],'coefficient':1}],6)
        self.assertGreaterEqual(r['kernel_dimension'],1)
        self.assertTrue(any(not p['gates']['active'] for p in r['kernel_basis']))
    def test_degree_boundary(self):
        for n in (True,2,21,'5',5.0):
            with self.assertRaises(ValueError):incidence_report(degree=n)
    def test_all_original_records_bound_by_contract(self):
        root=Path(__file__).resolve().parents[1]
        import hashlib
        original=json.loads((root/'data/equation_id_contract.json').read_text())['sha256_of_canonical_records']
        current=json.loads((root/'data/equations.json').read_text())['equations']
        byid={e['id']:e for e in current}
        self.assertEqual(len(current),len(byid))
        for eid,digest in original.items():
            self.assertEqual(hashlib.sha256(json.dumps(byid[eid],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),digest)
