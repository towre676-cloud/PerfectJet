"""Public frontier dispatch, retained certificates and scope must agree."""
import hashlib
import json
from pathlib import Path
import unittest

from perfectjet.asterion import evaluate, source_digests
from perfectjet.asterion_frontiers import FRONTIER_COMPONENTS

ROOT = Path(__file__).resolve().parents[1]


class FrontierIntegrationTests(unittest.TestCase):
    def test_immutable_592_record_prefix_and_frontier_equations(self):
        source = json.loads((ROOT/"data/equations.json").read_text())["equations"]
        frontier = json.loads((ROOT/"data/asterion_frontier_equations.json").read_text())
        prefix = frontier["preserved_prefix"]
        self.assertEqual(prefix["equation_count"],592)
        raw = json.dumps(source[:592],sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),prefix["sha256_of_canonical_records"])
        self.assertEqual(source[592:],frontier["equations"])
        self.assertEqual([r["id"] for r in source[592:]],[f"PJ-X{i:03d}" for i in range(1,49)])
        self.assertEqual(len(source),640)

    def test_strict_public_parameters(self):
        for request in ({"operation":"frontiers","max_degree":True},
                        {"operation":"frontiers","max_degree":9},
                        {"operation":"elliptic","exhaustive":1},
                        {"operation":"monodromy","level":5},
                        {"operation":"kernel-tower","max_degree":4},
                        {"operation":"jacobi","invented":1}):
            with self.subTest(request=request),self.assertRaises((ValueError,TypeError)):
                evaluate(request)

    def test_callable_jacobi_and_quick_scope(self):
        receipt = evaluate({"operation":"jacobi","max_degree":2})
        self.assertTrue(receipt["passed"])
        json.dumps(receipt,allow_nan=False)
        group = evaluate({"operation":"monodromy"})
        self.assertTrue(group["passed"])
        self.assertFalse(group["group_closure_certified_in_this_run"])

    def test_all_retained_bytes_and_source_bindings(self):
        folder = ROOT/"results/asterion-frontiers"
        manifest = json.loads((folder/"manifest.json").read_text())
        self.assertEqual(manifest["source_sha256"],source_digests())
        for name,metadata in manifest["files"].items():
            raw = (folder/name).read_bytes()
            self.assertEqual(len(raw),metadata["bytes"],name)
            self.assertEqual(hashlib.sha256(raw).hexdigest(),metadata["sha256"],name)
            self.assertEqual(json.loads(raw)["source_sha256"],source_digests(),name)
        report = json.loads((folder/"validation.json").read_text())
        self.assertTrue(report["passed"])
        self.assertTrue(report["exhaustive_requested"])
        self.assertEqual(set(report["components"]),set(FRONTIER_COMPONENTS))
        group = report["components"]["monodromy"]
        self.assertTrue(group["group_closure_certified_in_this_run"])
        self.assertEqual(group["compact_identity_component"],"SU(5)")
        self.assertEqual(group["component_count"],17)
        self.assertEqual(group["specialized_irreducibility"]["edge_count"],20)
        closure = report["finite_weight_six_closure"]
        self.assertTrue(closure["passed"])
        self.assertEqual(closure["exact_arc_dimension"],4716373)
        self.assertEqual(closure["exact_kernel_dimension"],185629)
        self.assertEqual(closure["exact_kernel_character"],
                         {"1":1,"248":1,"3875":2,"30380":1,"147250":1})
        self.assertFalse(closure["complete_minimal_differential_generator_list_computed"])

    def test_all_earlier_research_identifiers_survive(self):
        ledger = evaluate({"operation":"discoveries"})
        ids = {row["id"] for row in ledger["programme"]}
        self.assertTrue({f"AST-P{i:03d}" for i in range(1,65)} <= ids)
        self.assertEqual(len(ledger["discoveries"]),48)
        contract = ledger["preserved_baseline"]
        programme = [{k:v for k,v in row.items() if k != "frontier_update"}
                     for row in ledger["programme"]]
        canonical = lambda value: hashlib.sha256(json.dumps(value,sort_keys=True,
            ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
        self.assertEqual(canonical(programme),contract["canonical_programme_sha256"])
        self.assertEqual(canonical(ledger["discoveries"][:32]),contract["canonical_discovery_prefix_sha256"])


if __name__ == "__main__":
    unittest.main()
