"""Source gating, API consumption, boundary and retained-observation checks."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from research.p521_math import ntl15_replay as replay
from research.p521_math import portable_models as pm


class NTL15ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((Path(replay.__file__).with_name("results")/
                                  "ntl15-source-replay.json").read_text())

    def test_offline_record_consistency_requires_no_compiler_or_archive(self):
        with patch.object(replay.subprocess, "run", side_effect=AssertionError("external process")):
            self.assertTrue(replay.verify_document(self.receipt))

    def test_wrong_source_rejected_before_decompression(self):
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder)/"pretend.tar.Z"
            archive.write_bytes(b"untrusted archive")
            with patch.object(replay.subprocess, "run", side_effect=AssertionError("decompressed")):
                with self.assertRaisesRegex(ValueError, "authenticated compressed bytes"):
                    replay.authenticate_archive(archive)

    def test_source_driver_configuration_and_coverage_tampering(self):
        mutations = (
            lambda d: d["source_members_sha256"].update({"lip.c": "0"*64}),
            lambda d: d.update(driver_sha256="0"*64),
            lambda d: d["compiler_flags"].remove("-fwrapv"),
            lambda d: d["builds"].pop(),
            lambda d: d["builds"][0]["observations"].pop(),
            lambda d: d["original_machine_descriptors"].update(ZZ_BITS_PER_LONG=32),
            lambda d: d["builds"][0].update(configuration="native-generated"),
        )
        for mutation in mutations:
            document = copy.deepcopy(self.receipt)
            mutation(document)
            self.assertFalse(replay.verify_document(document))

    def test_observation_and_post_call_state_tampering(self):
        for field in ("value", "state", "model_raw_transitions"):
            document = copy.deepcopy(self.receipt)
            row = next(r for r in document["builds"][0]["observations"]
                       if r["state"] is not None)
            row[field] += 1
            self.assertFalse(replay.verify_document(document))

    def test_rehashed_machine_configuration_cannot_be_rebound(self):
        document = copy.deepcopy(self.receipt)
        for build in document["builds"]:
            config = build["mach_desc"].replace("ZZ_ARITH_RIGHT_SHIFT (1)",
                                                "ZZ_ARITH_RIGHT_SHIFT (0)")
            build["mach_desc"] = config
            build["mach_desc_sha256"] = replay.sha256(config.encode())
        self.assertFalse(replay.verify_document(document))

    def test_scalar_and_big_integer_one_have_different_consumption(self):
        for width in replay.WIDTHS:
            scalar = replay.model(None, "draw", 1, width)
            big = replay.model(None, "bnd", 1, width)
            self.assertEqual(scalar, {"value": 0, "state": replay.A*7157891 % replay.M,
                                      "raw_transitions": 1})
            self.assertEqual(big, {"value": 0, "state": None, "raw_transitions": 0})
            for seed in (None, 7):
                for argument in (-1, 0):
                    self.assertEqual(replay.model(seed, "draw", argument, width)["raw_transitions"], 0)
                for length in (-1, 0, 1):
                    self.assertEqual(replay.model(seed, "len", length, width)["raw_transitions"], 0)

    def test_full_signed_seed_normalization_and_default(self):
        for width in replay.WIDTHS:
            for seed in (0, replay.M, -replay.M, replay.M+1, -replay.M-1,
                         (1 << 200)+12345, -((1 << 200)+12345)):
                normalized = seed % replay.M or 1
                self.assertEqual(replay.model(seed, "len", 521, width),
                                 replay.model(normalized, "len", 521, width))
            self.assertEqual(replay.model(None, "len", 521, width),
                             replay.model(7157891, "len", 521, width))

    def test_exact_acceptance_threshold_is_rejected(self):
        for width in replay.WIDTHS:
            threshold = replay.M-replay.M % (1 << width)
            below = pow(replay.A, -1, replay.M)*(threshold-1) % replay.M
            equal = pow(replay.A, -1, replay.M)*threshold % replay.M
            self.assertEqual(replay.model(below, "draw", 1 << width, width)["raw_transitions"], 1)
            self.assertEqual(replay.model(equal, "draw", 1 << width, width)["raw_transitions"], 2)

    def test_independent_model_agrees_with_certified_packing_family(self):
        for width in replay.WIDTHS:
            for seed in (1, 871002724, (1 << 106)+1234):
                for length in (width-1, width, width+1, 2*width, 520, 521):
                    count = (length+width-1)//width
                    words, states = pm.draw(seed, count, width, rejection=True)
                    raw = sum(v << (i*width) for i, v in enumerate(words))
                    expected = (raw & ((1 << (length-1))-1)) | (1 << (length-1))
                    actual = replay.model(seed, "len", length, width)
                    self.assertEqual((actual["value"], actual["state"]), (expected, states[-1]))
                count = (521+width-1)//width+1
                words, states = pm.draw(seed, count, width, rejection=True)
                actual = replay.model(seed, "bnd", pm.P, width)
                self.assertEqual((actual["value"], actual["state"]),
                                 (pm.pack(words, width, "msb", "mod-p"), states[-1]))

    @unittest.skipUnless(os.environ.get("PERFECTJET_NTL15_ARCHIVE"),
                         "set PERFECTJET_NTL15_ARCHIVE to reexecute authentic historical C")
    def test_authentic_archive_executes_all_controls(self):
        document = replay.replay_archive(os.environ["PERFECTJET_NTL15_ARCHIVE"])
        self.assertTrue(replay.verify_document(document))
        self.assertEqual(document["case_count"], self.receipt["case_count"])


if __name__ == "__main__":
    unittest.main()
