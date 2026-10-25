"""Stable research equations must reach the source and installed equation tables."""
import hashlib
import json
from pathlib import Path
import unittest

from perfectjet.mathlab import LABS, catalogue

ROOT = Path(__file__).resolve().parents[1]


class ResearchFrontierCatalogueTests(unittest.TestCase):
    def test_all_675_preceding_records_and_new_ids_are_preserved(self):
        extension = json.loads((ROOT/'data/research_frontier_equations.json').read_text())
        current = json.loads((ROOT/'data/equations.json').read_text())['equations']
        prefix = extension['preserved_prefix']
        self.assertEqual(prefix['equation_count'], 675)
        canonical = json.dumps(current[:675], sort_keys=True, ensure_ascii=False,
                               separators=(',', ':')).encode()
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), prefix['sha256_of_canonical_records'])
        self.assertEqual(current[675:698], extension['equations'])
        self.assertEqual([r['id'] for r in extension['equations']],
                         [f'PJ-E{i}' for i in range(465, 488)])
        self.assertEqual(len(current[:698]), 698)
        self.assertEqual(len({r['id'] for r in current[:698]}), 698)

    def test_all_new_equations_are_searchable_without_inventing_tools(self):
        canonical = json.loads((ROOT/'data/equations.json').read_text())
        self.assertEqual(json.loads((ROOT/'src/perfectjet/resources/equations.json').read_text()), canonical)
        power = json.loads((ROOT/'data/equation_power.json').read_text())
        self.assertEqual(json.loads((ROOT/'src/perfectjet/resources/equation_power.json').read_text()), power)
        cat = catalogue()
        indexed = {r['id']: r for r in cat['equations']}
        self.assertEqual(len(LABS), 29)
        self.assertEqual(len(cat['families']), 27)
        # Research-frontier and half-braid records; the later PJ-P block is callable from the Asterion labs.
        for row in canonical['equations'][675:710]:
            self.assertEqual(indexed[row['id']]['equation'], row['equation'])
            self.assertIn(row['id'], power['assignments'])
            self.assertEqual(indexed[row['id']]['callable_labs'], [])

    def test_new_proofs_and_prior_research_chapters_reach_master(self):
        master = (ROOT/'docs/MONOGRAPH.md').read_text()
        atlas = (ROOT/'docs/EQUATION_ATLAS.md').read_text()
        for path in (ROOT/'docs/chapters').glob('*.md'):
            self.assertIn(path.read_text(), master, path.name)
        self.assertTrue((ROOT/'docs/PARTNER_STRUCTURE.md').is_file())
        for row in json.loads((ROOT/'data/research_frontier_equations.json').read_text())['equations']:
            self.assertIn(row['id'], atlas)
            self.assertIn(row['id'], master)
            self.assertEqual(row['status'], 'derived')
            self.assertIn('docs/chapters/33_exact_research_frontiers.md', row['source'])
            self.assertTrue(row['assumptions'])

    def test_new_scope_keeps_unbounded_squarefree_classification_open(self):
        chapter = (ROOT/'docs/chapters/33_exact_research_frontiers.md').read_text()
        self.assertIn('do not claim a global squarefree classification', chapter)
        self.assertIn('No worldwide priority, new Lean theorem', chapter)
        self.assertIn('dimension-eight integer representations is not established', chapter)
        self.assertIn('no conductor bound', chapter.lower())


if __name__ == '__main__':
    unittest.main()
