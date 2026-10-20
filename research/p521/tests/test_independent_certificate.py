"""Corruption and satisfiable-control checks for the independent verifier."""
import copy
import json
from pathlib import Path
import unittest

from research.p521 import verify_certificate as verifier


class IndependentCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((Path(__file__).parents[1]/'results'/'freelip-recovery.json').read_text())
        cls.source_document = json.loads((Path(__file__).parents[1]/'results'/'freelip-source-recovery.json').read_text())

    def test_all_six_layouts_verified_without_discovery_import(self):
        result = verifier.verify_document(self.document)
        self.assertTrue(result['verified'])
        self.assertEqual(len(result['profiles']), 6)

    def test_receipt_corruption_is_rejected(self):
        changes = [
            lambda d: d['profiles'].pop(),
            lambda d: d['profiles'].append(copy.deepcopy(d['profiles'][0])),
            lambda d: d['profiles'][0].update(target='0x0'),
            lambda d: d['profiles'][0].update(complete=False),
            lambda d: d['profiles'][0]['branches'][0]['interior']['outputs'].__setitem__(0, 0),
            lambda d: d['profiles'][0]['branches'][0].update(observations_used=1),
            lambda d: d['profiles'][0]['branches'][0]['recovery']['certificate'].update(denominator=1),
            lambda d: d['profiles'][0]['branches'][0]['recovery']['certificate']['numerator'].__setitem__(0, 0),
            lambda d: d['profiles'][0]['branches'][0]['recovery']['certificate'].update(minimum=0),
            lambda d: d['profiles'][0]['branches'][0]['recovery']['certificate'].update(maximum=0),
            lambda d: d['profiles'][0]['branches'][0]['recovery']['certificate']['outputs'].__setitem__(0, 0),
        ]
        for change in changes:
            with self.subTest(change=change):
                document = copy.deepcopy(self.document)
                change(document)
                with self.assertRaises(verifier.CertificateError):
                    verifier.verify_document(document)

    def test_known_satisfiable_states_cannot_be_excluded(self):
        certificate = self.document['profiles'][0]['branches'][0]['recovery']['certificate']
        for initial in (0, 1, 20000, 871002724, 123456789012345678901234567890,
                        verifier.MODULUS-1):
            state, outputs = initial, []
            for _ in range(8):
                state = verifier.MULTIPLIER*state % verifier.MODULUS
                outputs.append(state % verifier.RADIX)
            result = verifier.dual_bounds(outputs, certificate['numerator'], certificate['denominator'])
            self.assertFalse(result['excludes_every_state'])

    def test_source_faithful_all_768_certificates(self):
        result = verifier.verify_document(self.source_document)
        self.assertTrue(result['source_rejection'])
        self.assertEqual(sum(p['gap_patterns_verified'] for p in result['profiles']), 768)

    def test_source_gap_coverage_and_power_corruption(self):
        def delete_pattern(d):
            d['profiles'][0]['branches'].pop()

        def duplicate_pattern(d):
            d['profiles'][0]['branches'][-1] = copy.deepcopy(d['profiles'][0]['branches'][0])

        def change_power_gap(d):
            d['profiles'][0]['branches'][0]['recovery']['certificate']['gaps'][0] = 2

        def corrupt_rejection_relation(d):
            d['profiles'][0]['rejection_gap_proof']['numerator'][0] += 1

        for change in (delete_pattern, duplicate_pattern, change_power_gap, corrupt_rejection_relation):
            with self.subTest(change=change):
                document = copy.deepcopy(self.source_document)
                change(document)
                with self.assertRaises(verifier.CertificateError):
                    verifier.verify_document(document)

    def test_deliberate_rare_rejection_is_satisfiable(self):
        threshold = verifier.MODULUS-(verifier.RADIX-1)
        state = pow(verifier.MULTIPLIER, -1, verifier.MODULUS)*(verifier.MODULUS-1) % verifier.MODULUS
        self.assertLess(state, threshold)
        outputs, gaps = [state % verifier.RADIX], []
        for _ in range(7):
            gap = 0
            while True:
                state = verifier.MULTIPLIER*state % verifier.MODULUS
                gap += 1
                if state < threshold:
                    break
            gaps.append(gap)
            outputs.append(state % verifier.RADIX)
        self.assertEqual(gaps[0], 2)
        self.assertTrue(all(g in (1, 2) for g in gaps))
        profile = self.source_document['profiles'][0]
        certificate = next(branch['recovery']['certificate'] for branch in profile['branches']
                           if branch['recovery']['certificate']['gaps'] == gaps)
        result = verifier.dual_bounds(outputs, certificate['numerator'], certificate['denominator'], gaps)
        self.assertFalse(result['excludes_every_state'])
        with self.assertRaises(verifier.CertificateError):
            verifier.dual_bounds(outputs, certificate['numerator'], certificate['denominator'], [1]*7)


if __name__ == '__main__':
    unittest.main()
