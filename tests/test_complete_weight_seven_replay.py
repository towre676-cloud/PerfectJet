"""The retained evidence comparison rejects changes to mathematical witnesses."""
import copy
import unittest

from scripts.verify_complete_weight_seven import check_record


class CompleteWeightSevenReplayTests(unittest.TestCase):
    def test_evidence_comparison_rejects_changed_witnesses(self):
        names = (
            'quartic_span_certificate_147250.json',
            'quartic_old_products_779247.json',
            'quartic_30380_VOA_receipt.json',
            'quartic_casimir_cutoff_receipt.json',
        )
        replayed = {'replay_evidence_sha256': dict.fromkeys(names, 'regenerated')}
        check_record(copy.deepcopy(replayed), replayed)
        for name in names:
            retained = copy.deepcopy(replayed)
            retained['replay_evidence_sha256'][name] = 'altered'
            with self.subTest(evidence=name):
                with self.assertRaisesRegex(ValueError, name.replace('.', r'\.')):
                    check_record(retained, replayed)
