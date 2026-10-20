import importlib.util
import copy
import json
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "lcg_forensics.py"
SPEC = importlib.util.spec_from_file_location("p521_lcg_forensics", MODULE)
lcg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lcg)


class LCGForensicsTests(unittest.TestCase):
    def test_frozen_receipt_coverage_cannot_shrink(self):
        path = MODULE.parent / "results" / "lcg_forensics.json"
        report = json.loads(path.read_text())
        self.assertTrue(lcg.verify_report(report)["verified"])
        for section, field in [("byte_assembly", "certificates"),
                               ("top_bytes", "dual_exclusion_certificates")]:
            corrupted = copy.deepcopy(report)
            corrupted[section][field] = []
            with self.assertRaises(ValueError):
                lcg.verify_report(corrupted)

    def test_published_seed_forward_replay(self):
        self.assertEqual(lcg.candidate_seed(lcg.P521_TIMESTAMP, 1136), lcg.P521_SEED)

    def test_inverse_and_exhaustive_recovery(self):
        first = lcg.step((lcg.P521_TIMESTAMP << 16) | 0x330E)
        self.assertEqual(lcg.previous(first), (lcg.P521_TIMESTAMP << 16) | 0x330E)
        words = lcg.outputs(first, 5, 32)
        self.assertEqual(lcg.recover_top_bits_python(words, 32), [first])
        words[-1] ^= 1
        self.assertEqual(lcg.recover_top_bits_python(words, 32), [])

    def test_native_exhaustive_scan_and_synthetic_controls(self):
        report = lcg.scan_top_bits()
        self.assertGreater(report["traces"], 3000)
        self.assertEqual(report["matches"], [])
        self.assertTrue(all(control["passed"] for control in report["controls"]))

    def test_lattice_inverse_when_installed(self):
        try:
            import fpylll
        except ImportError:
            self.skipTest("optional fpylll not installed")
        states = lcg.recover_top_bytes_lattice(lcg.P521_SEED)
        self.assertEqual(len(states), 1)
        self.assertEqual(bytes(lcg.outputs(states[0], 20, 8)), lcg.P521_SEED)
        self.assertIsNone(lcg.exclusion_certificate(lcg.P521_SEED))
        certificate = lcg.exclusion_certificate(lcg.P521_GX.to_bytes(66, "big")[:20])
        self.assertIsNotNone(certificate)
        self.assertTrue(lcg.verify_exclusion(certificate))
        corrupted = copy.deepcopy(certificate)
        corrupted["coefficients"][0] += 1
        self.assertFalse(lcg.verify_exclusion(corrupted))
        corrupted = copy.deepcopy(certificate)
        corrupted["interval_lower"] += 1
        self.assertFalse(lcg.verify_exclusion(corrupted))
        assembly = lcg.byte_assembly_exclusions(66, 68)
        self.assertEqual(assembly["uncovered"], [])
        self.assertEqual(len(assembly["certificates"]), 12)
        self.assertTrue(all(lcg.verify_byte_assembly_exclusion(c)
                            for c in assembly["certificates"]))
        corrupted = copy.deepcopy(assembly["certificates"][0])
        corrupted["maximum_quotient"] += 1
        self.assertFalse(lcg.verify_byte_assembly_exclusion(corrupted))
        for certificate in assembly["certificates"]:
            if certificate["raw_bytes"] != 66:
                continue
            coordinate = {"Gx": lcg.P521_GX, "Gy": lcg.P521_GY}[certificate["coordinate"]]
            low = certificate["window_low_bit"]
            mask = (1 << 160) - 1
            for quotient in range(certificate["maximum_quotient"] + 1):
                raw = coordinate + quotient * ((1 << 521) - 1)
                self.assertEqual((raw >> low) & mask, (coordinate >> low) & mask)


if __name__ == "__main__":
    unittest.main()
