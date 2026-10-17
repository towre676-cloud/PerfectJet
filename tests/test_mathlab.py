import hashlib
import json
from pathlib import Path
import unittest

from perfectjet.mathlab import LABS, catalogue, evaluate
from perfectjet.recovered_requests import schemas


class IntegratedMathLabTests(unittest.TestCase):
    def test_installed_catalogue_retains_original_records_and_evidence(self):
        cat = catalogue()
        root = Path(__file__).resolve().parents[1]
        original = json.loads((root/'data/equation_id_contract.json').read_text())['sha256_of_canonical_records']
        source = json.loads((root/'data/equations.json').read_text())['equations']
        for row in source:
            if row['id'] in original:
                digest = hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
                self.assertEqual(digest, original[row['id']], row['id'])
        self.assertEqual(len(cat['equations']), 464)
        self.assertEqual(len({row['id'] for row in cat['equations']}), 464)
        self.assertEqual(len(cat['families']), 24)
        self.assertEqual({e['status'] for e in cat['equations'] if e['id'] in ('PJ-E122','PJ-E194')}, {'rejected'})

    def test_every_tool_computes_json_and_references_real_equations(self):
        known = {e['id'] for e in catalogue()['equations']}
        for lab in LABS:
            with self.subTest(lab=lab['id']):
                result = evaluate({'operation':'math-lab','lab':lab['id'],'params':lab['example']['params']})
                json.dumps(result, allow_nan=False)
                self.assertEqual(result['lab'], lab['id'])
                self.assertTrue(result['summary'])
                self.assertTrue(result['scope'])
                self.assertTrue(set(result['equation_ids']).issubset(known))

    def test_real_custom_recovered_inputs_are_honored(self):
        for name, schema in schemas().items():
            with self.subTest(lab=name):
                result = evaluate({'lab':name,'params':schema['sample_params']})
                self.assertTrue(result['details'])
                with self.assertRaises(ValueError):
                    evaluate({'lab':name,'params':{'unsupported_never_ignored':1}})

    def test_hidden_pipeline_does_not_promise_an_unavailable_repair(self):
        result = evaluate({'lab':'pipeline','params':{'observation':[[1,1]],'observed':[20]}})
        self.assertFalse(result['details']['repair']['possible'])
        self.assertIn('none of the supplied', result['summary'])

    def test_recover_candidate_search_is_bounded_before_exhaustion(self):
        with self.assertRaises(ValueError):
            evaluate({'lab':'recover','params':{'candidates':[[1,1]]*13}})
        result = evaluate({'lab':'recover','params':{'repair':True}})
        self.assertEqual(result['metrics'][-1]['value'], True)
        with self.assertRaises(ValueError):
            evaluate({'lab':'count','params':{'capacities':[True,3]}})


if __name__ == '__main__':
    unittest.main()
