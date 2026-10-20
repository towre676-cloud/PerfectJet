"""Public extension contracts and retained evidence must agree."""
import gzip
import hashlib
import json
from pathlib import Path
import unittest

from perfectjet.asterion import evaluate, source_digests
from perfectjet.asterion_extension import COMPONENTS
from perfectjet.mathlab import catalogue

ROOT = Path(__file__).resolve().parents[1]


class ExtensionPublicationTests(unittest.TestCase):
    def test_immutable_prefix_and_installed_extension_equations(self):
        extension = json.loads((ROOT / "data/asterion_extension_equations.json").read_text())
        records = json.loads((ROOT / "data/equations.json").read_text())["equations"]
        prefix = extension["preserved_prefix"]
        self.assertEqual(prefix["equation_count"], 504)
        canonical = json.dumps(records[:504], sort_keys=True, ensure_ascii=False,
                               separators=(",", ":")).encode()
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), prefix["sha256_of_canonical_records"])
        self.assertEqual(records[504:592], extension["equations"])
        self.assertEqual([r["id"] for r in records[504:592]], [f"PJ-H{i:03d}" for i in range(1, 89)])
        cat = catalogue()
        self.assertEqual(len(cat["equations"]), len(records))
        for row in cat["equations"][504:592]:
            self.assertIn("asterion-extension", row["callable_labs"])
        for name in ("equations.json", "equation_power.json"):
            self.assertEqual(json.loads((ROOT / "data" / name).read_text()),
                             json.loads((ROOT / "src/perfectjet/resources" / name).read_text()))

    def test_retained_full_mathematical_replay_and_source_binding(self):
        folder = ROOT / "results/asterion-extension"
        manifest = json.loads((folder / "manifest.json").read_text())
        self.assertEqual(manifest["source_sha256"], source_digests())
        for name, metadata in manifest["files"].items():
            raw = (folder / name).read_bytes()
            self.assertEqual(len(raw), metadata["bytes"], name)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), metadata["sha256"], name)
            if name.endswith(".gz"):
                self.assertEqual(raw[9], 255)
                value = json.loads(gzip.decompress(raw))
            else:
                value = json.loads(raw)
            self.assertEqual(value["source_sha256"], source_digests(), name)
        report = json.loads((folder / "validation.json").read_text())
        self.assertTrue(report["passed"])
        self.assertEqual(set(report["components"]), set(COMPONENTS))
        self.assertTrue(report["exhaustive_requested"])
        relation = report["components"]["relations"]
        self.assertTrue(relation["nonzero_arc_kernel_generator_certified_in_this_run"])
        self.assertEqual(relation["complete_sector_pairing"]["rows_checked"], 14441)
        self.assertEqual(relation["generated_kernel_component_weyl_dimension"], 3875)
        self.assertFalse(relation["full_arc_kernel_claim"])
        completeness = relation["weight_four_completeness"]
        self.assertTrue(completeness["passed"])
        self.assertEqual(completeness["arc_character_through_weight4"][-1], 217001)
        self.assertEqual(completeness["weight4_arc_kernel_dimension"], 3875)
        self.assertEqual(completeness["graded_kernel_per_sector"], 31)
        self.assertTrue(report["components"]["rigidity"]["full_rank_162_and_155_computed"])
        self.assertTrue(report["components"]["kz"]["monodromy_generator_certificate"]["nonabelian_image_certified"])

    def test_strict_public_scope_and_bounds(self):
        for request in ({"operation": "extension", "max_degree": True},
                        {"operation": "extension", "max_degree": 81},
                        {"operation": "boundary", "exhaustive": 1},
                        {"operation": "relations", "invented": 1},
                        {"operation": "currents", "exhaustive": True},
                        {"operation": "rigidity", "max_degree": 4}):
            with self.subTest(request=request), self.assertRaises(ValueError):
                evaluate(request)

    def test_discovery_ledger_installed_copy(self):
        data = evaluate({"operation": "discoveries"})
        self.assertEqual(data, json.loads((ROOT / "docs/ASTERION_DISCOVERIES.json").read_text()))
        json.dumps(data, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
