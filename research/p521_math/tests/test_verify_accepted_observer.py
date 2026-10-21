"""Independent proof replay and rejection of incomplete or corrupted proofs."""
import copy
import json
import unittest

from research.p521_math import verify_accepted_observer as audit


class IndependentAcceptedAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(audit.DEFAULT_RECEIPT.read_text())

    def test_complete_receipt(self):
        checked = audit.verify_document(self.document)
        self.assertTrue(checked['independently_verified'])
        self.assertEqual(6, checked['minimum_accepted_outputs'])
        self.assertEqual(32, checked['same_patterns'])
        self.assertEqual(961, checked['cross_pattern_pairs'])
        self.assertEqual(1556, checked['coefficient_combinations'])
        self.assertEqual(304, checked['in_box_vectors'])
        self.assertFalse(checked['initial_state_unique_in_general'])

    def test_proper_sublattice_is_rejected(self):
        for kind in ('same_patterns', 'cross_patterns'):
            changed = copy.deepcopy(self.document[kind][0])
            changed['basis'][0] = [2*v for v in changed['basis'][0]]
            with self.assertRaisesRegex(ValueError, 'index'):
                (audit._same_pattern if kind == 'same_patterns' else audit._cross_pattern)(changed)

    def test_scaled_membership_is_rejected(self):
        changed = copy.deepcopy(self.document['cross_patterns'][0])
        changed['basis'][0][0] += 1
        with self.assertRaises(ValueError):
            audit._cross_pattern(changed)

    def test_coefficient_truncation_is_rejected(self):
        changed = copy.deepcopy(self.document['cross_patterns'][0])
        changed['ranges'][0][0] += 1
        with self.assertRaisesRegex(ValueError, 'coefficient intervals'):
            audit._cross_pattern(changed)

    def test_omitted_pair_cannot_prove_theorem(self):
        changed = copy.deepcopy(self.document)
        changed['cross_patterns'].pop()
        with self.assertRaisesRegex(ValueError, 'coverage'):
            audit.verify_document(changed)

    def test_duplicate_pattern_is_rejected(self):
        changed = copy.deepcopy(self.document)
        changed['same_patterns'].append(changed['same_patterns'][0])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            audit.verify_document(changed)

    def test_rejection_lemma_and_scope_data_are_replayed(self):
        changed = copy.deepcopy(self.document)
        changed['no_consecutive_rejections']['numerator'][0] += 1
        with self.assertRaisesRegex(ValueError, 'rejections witness'):
            audit.verify_document(changed)
        changed = copy.deepcopy(self.document)
        changed['parameters']['accept_below'] += 1
        with self.assertRaisesRegex(ValueError, 'fixed model'):
            audit.verify_document(changed)


if __name__ == '__main__':
    unittest.main()
