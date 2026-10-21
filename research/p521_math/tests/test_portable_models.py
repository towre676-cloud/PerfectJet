"""Positive recovery, exact coverage and tamper tests for portable models."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from research.p521_math import portable_models as pm


class PortableModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(pm.__file__).with_name("results")/"portable-models.json"
        cls.receipt = json.loads(path.read_text())

    def test_retained_receipt_verifies_without_lll(self):
        with patch.object(pm, "reduce_basis", side_effect=AssertionError("LLL called")):
            self.assertTrue(pm.verify_document(self.receipt))

    def test_omitted_model_or_branch_is_rejected(self):
        for mutation in (lambda d: d["profiles"].pop(),
                         lambda d: next(p for p in d["profiles"] if p["branches"])["branches"].pop()):
            document = copy.deepcopy(self.receipt)
            mutation(document)
            self.assertFalse(pm.verify_document(document))

    def test_target_and_rebound_proof_are_rejected(self):
        document = copy.deepcopy(self.receipt)
        document["target"] = hex(pm.GX+1)
        self.assertFalse(pm.verify_document(document))
        document = copy.deepcopy(self.receipt)
        branch = next(p for p in document["profiles"] if p["branches"])["branches"][0]
        branch["recovery"]["certificate"]["outputs"][0] ^= 1
        self.assertFalse(pm.verify_document(document))

    def test_dual_and_positive_replay_tampering_is_rejected(self):
        document = copy.deepcopy(self.receipt)
        branch = next(p for p in document["profiles"] if p["branches"])["branches"][0]
        branch["recovery"]["certificate"]["maximum"] += 1
        self.assertFalse(pm.verify_document(document))
        document = copy.deepcopy(self.receipt)
        document["synthetic_controls"][0]["candidate"]["emitting_states"][0] ^= 1
        self.assertFalse(pm.verify_document(document))

    def test_rejection_bounds_and_tight_width62_example(self):
        for width in (26, 30, 31, 32, 50, 62):
            self.assertTrue(pm.verify_rejection_gap_proof(pm.rejection_gap_proof(width)))
        # t0 and t1=A*t0 mod M are both below 2^62; M-t0 and M-t1
        # are therefore rejected in succession. The next state must pass.
        t0, t1 = 3389828199694795, 5924008525679449
        self.assertEqual(pm.A*t0 % pm.M, t1)
        seed = pow(pm.A, -1, pm.M)*(pm.M-t0) % pm.M
        x0, x1 = pm.M-t0, pm.M-t1
        self.assertEqual(pm.A*seed % pm.M, x0)
        self.assertEqual(pm.A*x0 % pm.M, x1)
        values, states = pm.draw(seed, 1, 62, rejection=True)
        self.assertEqual(states, [pm.A*x1 % pm.M])
        self.assertEqual(values, [states[0] % (1 << 62)])

    def test_interiors_cover_true_full_words_at_boundary_targets(self):
        # Test every packing rule against actual words, including all-zero and
        # all-one words, where modular carry/wrap prefixes are easy to miss.
        for width in (26, 30, 31, 32, 50, 62):
            count = (521+width-1)//width+1
            for words in ([0]*count, [(1 << width)-1]*count,
                          [(123456789123456789*(i+1)) % (1 << width) for i in range(count)]):
                for order in ("msb", "lsb"):
                    for packing in ("mod-p", "low-521", "high-521"):
                        target = pm.pack(words, width, order, packing)
                        interiors = pm.interior_sequences(target, width, count, order, packing)
                        self.assertTrue(any(words[r["first_output_index"]:r["first_output_index"]+len(r["outputs"])]
                                            == r["outputs"] for r in interiors), (width, order, packing, target))

    def test_exact_randomlen_masks_top_bit_and_preserves_lower_words(self):
        for width in (26, 30, 50, 62):
            for bits in (520, 521):
                count = (bits+width-1)//width
                words, _ = pm.draw(871002724, count, width, rejection=True)
                packing = f"randomlen-{bits}"
                target = pm.pack(words, width, "lsb", packing)
                self.assertEqual(target.bit_length(), bits)
                records = pm.interior_sequences(target, width, count, "lsb", packing)
                self.assertTrue(any(words[:len(r["outputs"])] == r["outputs"] for r in records))

    def test_high_word_recovery_and_budget_is_not_exclusion(self):
        values, states = pm.draw(123456789012345678901234567890, 6, 30, "high")
        result = pm.recover_outputs(values, 30, "high")
        self.assertTrue(result["complete"])
        self.assertIn(states[0], result["states"])
        result = pm.recover_outputs(values[:2], 30, "high", budget=0)
        self.assertFalse(result["complete"])
        self.assertEqual(result["status"], "unresolved")


if __name__ == "__main__":
    unittest.main()
