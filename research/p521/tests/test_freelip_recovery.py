"""Meaningful recovery, source-calibration and certificate-corruption tests."""
import copy
import importlib.util
import json
from pathlib import Path
import random
import unittest

SOURCE = Path(__file__).resolve().parents[1]/"freelip_recovery.py"
spec = importlib.util.spec_from_file_location("freelip_recovery", SOURCE)
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


class FreeLIPRecoveryTests(unittest.TestCase):
    def test_published_p192_positive_control(self):
        """Calibrate the exact historical recipe against a known explained Gx."""
        p = (1 << 192)-(1 << 64)-1
        b = 0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1
        expected = 0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012
        _, states = f.draw(20000, 7)
        state = states[-1]
        for _ in range(100):
            limbs, states = f.draw(state, 9)
            state = states[-1]
            x = f.assemble(limbs) % p
            rhs = (x*x*x-3*x+b) % p
            if rhs == 0 or pow(rhs, (p-1)//2, p) == 1:
                self.assertEqual(expected, x)
                break
        else:
            self.fail("source recipe failed to produce a point")

    def test_recover_low_limb_state(self):
        outputs, states = f.draw(123456789123456789123456789, 8)
        result = f.recover_low_outputs(outputs)
        self.assertTrue(result["complete"])
        self.assertEqual([states[0]], result["states"])

    def test_zero_state_not_lost(self):
        self.assertEqual([0], f.recover_low_outputs([0]*8)["states"])

    def test_source_rejection_gap_and_recovery(self):
        # Force the rare rejection rather than relying on a random test to see
        # a probability-2**-81 event.
        emitting = pow(f.A, -1, f.M)*(f.M-1) % f.M
        outputs, states = f.draw(emitting, 7, rejection=True)
        self.assertEqual(f.A*(f.M-1) % f.M, states[0])
        observations = [emitting % f.B]+outputs
        recovered = f.recover_low_outputs(observations, gaps=[2]+[1]*6)
        self.assertEqual([emitting], recovered["states"])
        proof = f.no_consecutive_rejections()
        q = proof["numerator"]
        self.assertEqual(0, (q[0]+f.A*q[1]) % f.M)
        self.assertTrue(0 < proof["minimum"] <= proof["maximum"] < f.M)

    def test_committed_source_loop_certificates(self):
        path = SOURCE.parent/"results"/"freelip-source-recovery.json"
        if not path.exists():
            self.skipTest("source-loop receipt not generated")
        receipt = json.loads(path.read_text())
        total = 0
        for profile in receipt["profiles"]:
            self.assertTrue(profile["source_rejection"])
            self.assertEqual(128, len(profile["branches"]))
            patterns = set()
            for branch in profile["branches"]:
                certificate = branch["recovery"]["certificate"]
                self.assertTrue(f.verify_exclusion(certificate))
                patterns.add(tuple(certificate["gaps"]))
                total += 1
            self.assertEqual(128, len(patterns))
        self.assertEqual(768, total)

    def test_all_declared_layouts_recover_synthetic(self):
        state = 123456789012345678901234567890
        for count in (20, 21, 22):
            for order in ("msb", "lsb"):
                limbs, _ = f.draw(state, count)
                target = f.assemble(limbs, order) % f.P
                result = f.recover_coordinate(target, count, order)
                self.assertTrue(result["complete"])
                self.assertIn(state, [r["initial_state"] for r in result["candidates"]])

    def test_interior_extraction_includes_true_draws(self):
        rng = random.Random(521)
        for count in (20, 21, 22):
            for order in ("msb", "lsb"):
                for _ in range(20):
                    limbs, _ = f.draw(rng.randrange(f.M), count)
                    target = f.assemble(limbs, order) % f.P
                    sequences = f.interior_sequences(target, count, order)
                    self.assertTrue(any(r["outputs"] == limbs[r["first_output_index"]:r["first_output_index"]+len(r["outputs"])] for r in sequences))

    def test_p521_all_state_exclusion_certificates(self):
        for count in (20, 21, 22):
            for order in ("msb", "lsb"):
                result = f.recover_coordinate(count=count, order=order)
                self.assertTrue(result["complete"])
                self.assertEqual([], result["candidates"])
                self.assertGreater(len(result["branches"]), 0)
                for r in result["branches"]:
                    self.assertEqual("excluded", r["recovery"]["status"])
                    self.assertTrue(f.verify_exclusion(r["recovery"]["certificate"]))

    def test_certificate_corruption_rejected(self):
        result = f.recover_coordinate()
        original = result["branches"][0]["recovery"]["certificate"]
        for key in ("minimum", "maximum", "denominator"):
            changed = copy.deepcopy(original)
            changed[key] += 1
            self.assertFalse(f.verify_exclusion(changed), key)
        changed = copy.deepcopy(original)
        changed["numerator"][0] += 1
        self.assertFalse(f.verify_exclusion(changed))

    def test_small_coordinate_branch_boundary(self):
        for target in (0, 1, (1 << 25)-1, (1 << 26)-1, (1 << 51)-1):
            for count in (21, 22):
                records = f.interior_sequences(target, count)
                self.assertGreater(len(records), 0)
                self.assertLessEqual(len(records), 4)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            f.recover_low_outputs([1])
        with self.assertRaises(ValueError):
            f.recover_low_outputs([1, f.B])
        with self.assertRaises(ValueError):
            f.interior_sequences(count=19)
        self.assertFalse(f.verify_exclusion({}))


if __name__ == "__main__":
    unittest.main()
