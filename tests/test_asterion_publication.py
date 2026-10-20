"""Published equations and numerical certificates must match their sources."""
import gzip
import hashlib
import json
from pathlib import Path
import unittest

from perfectjet.asterion import source_digests
from perfectjet.asterion_basis import verify_certificate
from perfectjet.asterion_e8 import E8LieAlgebra
from perfectjet.mathlab import catalogue


ROOT = Path(__file__).resolve().parents[1]


class AsterionPublicationTests(unittest.TestCase):
    def test_archived_equation_prefix_is_unchanged_and_new_records_are_callable(self):
        extension = json.loads((ROOT/'data/asterion_equations.json').read_text())
        rows = json.loads((ROOT/'data/equations.json').read_text())['equations']
        prefix = extension['preserved_prefix']
        digest = hashlib.sha256(json.dumps(rows[:prefix['equation_count']], sort_keys=True,
            ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(prefix['equation_count'], 464)
        self.assertEqual(digest, prefix['sha256_of_canonical_records'])
        actual = [r for r in rows if r['id'].startswith('PJ-A')]
        self.assertEqual(actual, extension['equations'])
        self.assertEqual([r['id'] for r in actual], [f'PJ-A{i:03d}' for i in range(1,41)])
        source = json.loads((ROOT/'data/equations.json').read_text())
        self.assertEqual(source, json.loads((ROOT/'src/perfectjet/resources/equations.json').read_text()))
        installed = {r['id']: r for r in catalogue()['equations']}
        for row in actual:
            self.assertIn('asterion', installed[row['id']]['callable_labs'])
            self.assertIn(row['id'], (ROOT/'docs/EQUATION_ATLAS.md').read_text())
        chapter = (ROOT/'docs/chapters/34_asterion_basis.md').read_text()
        self.assertEqual(chapter, (ROOT/'docs/ASTERION_BASIS.md').read_text())
        self.assertIn(chapter, (ROOT/'docs/MONOGRAPH.md').read_text())

    def test_retained_receipts_have_exact_hashes_and_current_sources(self):
        folder = ROOT/'results/asterion'
        manifest = json.loads((folder/'manifest.json').read_text())
        for name, info in manifest['files'].items():
            raw = (folder/name).read_bytes()
            self.assertEqual(len(raw), info['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), info['sha256'])
            if name.endswith('.gz'):
                self.assertEqual(raw[9], 255)
                data = json.loads(gzip.decompress(raw))
                self.assertEqual(data['source_sha256'], source_digests())
        result = json.loads((folder/'validation.json').read_text())
        self.assertEqual(result['source_sha256'], source_digests())
        self.assertTrue(result['passed'])
        self.assertEqual(result['chevalley_coxeter']['jacobi']['checked'], 2511496)
        self.assertTrue(result['chevalley_coxeter']['jacobi']['exhaustive_distinct_triples'])
        jordan = result['jordan_polynomials']
        self.assertEqual(jordan['jacobi']['triples_checked'], 2511496)
        self.assertTrue(jordan['jacobi']['exhaustive'])
        self.assertEqual(jordan['grade_pair_maps'], 7440)
        self.assertEqual(jordan['distinct_nonzero_coefficients'], 50)
        self.assertEqual(jordan['cartans']['normalizer_minors_checked'], 3720)
        self.assertTrue(result['asterion_e8_basis']['chevalley_comparison']['asterion_is_denser'])
        self.assertEqual(result['chart_transport']['intertwining']['basis_pairs_checked'], 30628)

    def test_full_retained_asterion_basis_certificate_replays(self):
        folder = ROOT/'results/asterion'
        record = json.loads(gzip.decompress((folder/'response_basis.json.gz').read_bytes()))
        result = verify_certificate(E8LieAlgebra().bracket, record['certificate'])
        self.assertTrue(result['valid'])
        self.assertEqual(result['bracket_pairs'], 30628)
        self.assertEqual(record['certificate']['determinant'], '-1')
        self.assertTrue(record['certificate']['same_integer_lattice'])
        kernels = json.loads(gzip.decompress((folder/'jordan_kernels.json.gz').read_bytes()))
        self.assertEqual(len(kernels['maps']), 7440)
        columns = json.loads(gzip.decompress((folder/'transport_columns.json.gz').read_bytes()))
        self.assertEqual(len(columns['columns']), 248)

    def test_independent_compound_seed_lattice_counterexample(self):
        raw = (ROOT/'results/asterion/compound_seed_basis.json.gz').read_bytes()
        data = json.loads(gzip.decompress(raw))
        self.assertEqual(data['source_sha256'], source_digests())
        encoded = json.dumps(data['certificate'], sort_keys=True, separators=(',', ':')).encode()
        self.assertEqual(hashlib.sha256(encoded).hexdigest(), data['certificate_sha256'])
        replay = verify_certificate(E8LieAlgebra().bracket, data['certificate'])
        self.assertTrue(replay['valid'])
        self.assertEqual(replay['bracket_pairs'], 30628)
        self.assertEqual(data['certificate']['determinant'], '-5')
        self.assertFalse(data['certificate']['same_integer_lattice'])


if __name__ == '__main__':
    unittest.main()
