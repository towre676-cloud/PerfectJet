"""Stable equations, source-bound certificates and explicit public scope."""
import gzip
import hashlib
import json
from pathlib import Path
import unittest

from perfectjet.dell import evaluate,source_digests,structural_receipt
from perfectjet.mathlab import catalogue,evaluate as lab_evaluate

ROOT=Path(__file__).resolve().parents[1]


class DellPublicationTests(unittest.TestCase):
    def test_all_previous_equations_are_immutable_and_new_ids_are_callable(self):
        source=json.loads((ROOT/'data/equations.json').read_text())
        dedicated=json.loads((ROOT/'data/dell_equations.json').read_text())
        prefix=dedicated['preserved_prefix']
        self.assertEqual(prefix['equation_count'],640)
        raw=json.dumps(source['equations'][:640],sort_keys=True,ensure_ascii=False,
                       separators=(',',':')).encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),prefix['sha256_of_canonical_records'])
        self.assertEqual(source['equations'][640:675],dedicated['equations'])
        ids=[f'PJ-D{i:03d}' for i in range(1,36)]
        self.assertEqual([r['id'] for r in dedicated['equations']],ids)
        self.assertEqual(source,json.loads((ROOT/'src/perfectjet/resources/equations.json').read_text()))
        for row in catalogue()['equations'][640:675]:
            self.assertEqual(row['family_rank'],27)
            self.assertIn('dell',row['callable_labs'])
        result=lab_evaluate({'lab':'dell','params':{'operation':'obstructions'}})
        self.assertEqual(result['equation_ids'],ids)
        self.assertTrue(result['details']['passed'])

    def test_retained_evidence_matches_bytes_and_current_sources(self):
        folder=ROOT/'results/dell'
        manifest=json.loads((folder/'manifest.json').read_text())
        self.assertEqual(manifest['source_sha256'],source_digests())
        for name,info in manifest['files'].items():
            raw=(folder/name).read_bytes()
            self.assertEqual(len(raw),info['bytes'],name)
            self.assertEqual(hashlib.sha256(raw).hexdigest(),info['sha256'],name)
            if name.endswith('.gz'):
                self.assertEqual(raw[9],255)
                raw=gzip.decompress(raw)
            self.assertEqual(json.loads(raw)['source_sha256'],source_digests(),name)
        report=json.loads((folder/'validation.json').read_text())
        self.assertTrue(report['passed'])
        self.assertEqual(set(report['components']),{'normalization','second-normalization',
            'normalization-boundary','mixed-normalization','obstructions','classical','quantum','structure'})
        self.assertFalse(report['components']['quantum']['all_order_commutativity_proved'])
        self.assertFalse(report['components']['classical']['self_duality_proved'])
        self.assertTrue(all(c['leading_independence']['nonzero']
                            for c in report['components']['classical']['cases']))

    def test_proofs_and_research_gates_are_preserved_in_the_monograph(self):
        chapter=(ROOT/'docs/chapters/37_dell_research.md').read_text()
        self.assertIn(chapter,(ROOT/'docs/MONOGRAPH.md').read_text())
        for name in ('DELL_RESEARCH.md','DELL_NORMALIZATION.md',
                     'DELL_OBSTRUCTIONS.md','DELL_STRUCTURE.md'):
            self.assertIn((ROOT/'docs'/name).read_text().rstrip(),chapter)
        ledger=json.loads((ROOT/'docs/DELL_DISCOVERIES.json').read_text())
        self.assertFalse(ledger['worldwide_priority_verified'])
        self.assertEqual(len(ledger['results']),8)
        self.assertEqual(len(ledger['open_gates']),6)
        self.assertTrue(all(g['status']=='open' for g in ledger['open_gates']))

    def test_request_rejects_unknown_and_unused_parameters(self):
        for params in ({'operation':'invented'},{'operation':'normalization','exhaustive':False},
                       {'operation':'quantum','exhaustive':1},{'operation':'structure','positions':[1,2,3]}):
            with self.subTest(params=params),self.assertRaises(ValueError):
                evaluate(params)

    def test_all_rank_proof_replays_and_limits(self):
        result=structural_receipt()
        self.assertTrue(result['passed'])
        self.assertEqual([r['particles'] for r in result['finite_replays']],list(range(2,9)))
        self.assertFalse(result['commutativity_consequence_claimed'])
        self.assertFalse(result['analytic_convergence_claimed'])


if __name__=='__main__':
    unittest.main()
