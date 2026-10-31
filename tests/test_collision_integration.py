"""Public JSON routes, catalogue preservation, CLI and installed resources."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from perfectjet.collision_research import evaluate, json_value
from perfectjet.mathlab import catalogue, evaluate as lab

ROOT = Path(__file__).resolve().parents[1]


class CollisionIntegrationTests(unittest.TestCase):
    def test_all_724_prior_equations_preserved_and_new_records_callable(self):
        extension = json.loads((ROOT/'data/collision_equations.json').read_text())
        source = json.loads((ROOT/'data/equations.json').read_text())['equations']
        canonical = json.dumps(source[:724],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
        self.assertEqual(hashlib.sha256(canonical).hexdigest(),extension['preserved_prefix']['sha256_of_canonical_records'])
        self.assertEqual(source[724:],extension['equations'])
        self.assertEqual([r['id'] for r in source[724:]],[f'PJ-C{i:03d}' for i in range(1,21)])
        indexed = {r['id']:r for r in catalogue()['equations']}
        for row in extension['equations']:
            self.assertEqual(indexed[row['id']]['callable_labs'],['collision'])
        self.assertEqual(json.loads((ROOT/'src/perfectjet/resources/equations.json').read_text())['equations'],source)

    def test_every_editable_sample_and_original_cli_route(self):
        card = next(x for x in catalogue()['labs'] if x['id']=='collision')
        shapes = card['request_schema']
        for sample in [shapes['sample_params']]+shapes['additional_samples']:
            result = lab({'lab':'collision','params':sample})
            json.dumps(result,allow_nan=False)
            self.assertEqual(result['lab'],'collision')
        completed = subprocess.run([sys.executable,'-m','perfectjet','collision','--conductor','2','--index','7'],capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(completed.stdout)['coefficient'],['8'])

    def test_decimal_strings_and_large_exact_pell_serialize_without_global_changes(self):
        old_limit = sys.get_int_max_str_digits() if hasattr(sys,'get_int_max_str_digits') else None
        result = evaluate({'operation':'pell','index':12000})
        encoded = result['unit_power']['rational']
        self.assertGreater(len(encoded),4300)
        self.assertTrue(encoded.isdigit())
        self.assertEqual(json_value(-(10**5000+1)),'-'+'1'+'0'*4999+'1')
        if old_limit is not None:
            self.assertEqual(sys.get_int_max_str_digits(),old_limit)
        with self.assertRaises(ValueError):
            json_value(1<<262145)

    def test_finite_exception_global_residue_and_request_domains(self):
        projection = evaluate({'operation':'projection','conductor':4,'order':12})
        self.assertEqual(projection['formal_zeta_exponents'],[2,-1,0,1]+[0]*8)
        factored = evaluate({'operation':'population','factorization':[[2,4],[3,3],[5,2]],'conductor':6,'residue':0,'rank':7})
        self.assertEqual(factored['residue_histogram'],[16,6,8,12,8,10])
        self.assertTrue(factored['rank_replayed'])
        four = evaluate({'operation':'four','a':[4,1],'b':[2,4]})
        self.assertTrue(four['roundtrip_verified'])
        self.assertTrue(four['size_verified'])
        inverse = evaluate({'operation':'four','u':four['u'],'v':four['v'],'w':four['w']})
        self.assertEqual((inverse['a'],inverse['b']),([4,1],[2,4]))
        for request in ({'operation':[]},{'operation':'norm','unknown':1},{'operation':'constants','prime_cutoff':10001},{'operation':'pell','index':True},{'operation':'population','factorization':[[4,2]]}):
            with self.assertRaises((ValueError,TypeError)):
                evaluate(request)


if __name__=='__main__':
    unittest.main()
