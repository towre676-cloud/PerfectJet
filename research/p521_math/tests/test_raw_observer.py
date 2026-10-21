"""Global-certificate corruption, inverse recovery and error-location tests."""
import copy
from itertools import combinations
import json
from pathlib import Path
import unittest

from research.p521_math import raw_observer as observer


class RawObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(observer.RECEIPT.read_text())

    def test_complete_global_proof(self):
        result = observer.verify_document(self.document)
        self.assertEqual(70, result['normalized_subset_certificates'])
        self.assertEqual(126, result['five_subsets_of_nine'])
        self.assertEqual((5, 7, 9), (result['raw_state_observation_minimum'],
                                     result['one_error_minimum'], result['two_error_minimum']))

    def test_certificate_and_coverage_corruption_rejected(self):
        mutations = []
        changed = copy.deepcopy(self.document)
        changed['subset_certificates'][0]['basis'][0][0] += 1
        mutations.append(changed)
        changed = copy.deepcopy(self.document)
        changed['subset_certificates'][0]['basis'][0] = [2*v for v in changed['subset_certificates'][0]['basis'][0]]
        mutations.append(changed)
        changed = copy.deepcopy(self.document)
        changed['subset_certificates'][0]['coefficient_bounds'][0]['numerator'] += 1
        mutations.append(changed)
        changed = copy.deepcopy(self.document)
        changed['subset_certificates'].pop()
        mutations.append(changed)
        changed = copy.deepcopy(self.document)
        changed['subset_certificates'].append(changed['subset_certificates'][0])
        mutations.append(changed)
        changed = copy.deepcopy(self.document)
        changed['parameters']['multiplier'] += 1
        mutations.append(changed)
        changed = copy.deepcopy(self.document)
        changed['sharpness_witness']['states'][0] += 1
        mutations.append(changed)
        for changed in mutations:
            with self.assertRaises(ValueError):
                observer.verify_document(changed)

    def test_all_five_subsets_and_boundary_states(self):
        for state in (0, observer.M-1, 20000, 123456789123456789123456789):
            outputs = observer.raw_outputs(state, 9)
            for times in combinations(range(9), 5):
                self.assertEqual(state, observer.recover_five(times, [outputs[t] for t in times]))

    def test_any_one_error_in_seven(self):
        for state in (0, observer.M-1, 20000):
            original = observer.raw_outputs(state, 7)
            for index in range(7):
                received = original[:]
                received[index] = (received[index]+12345) % observer.B
                recovered = observer.decode(received, errors=1)
                self.assertEqual(state, recovered['state'])
                self.assertEqual([index], recovered['error_positions'])
                self.assertEqual(original, recovered['corrected_outputs'])

    def test_any_two_error_positions_in_nine(self):
        state = 123456789123456789123456789
        original = observer.raw_outputs(state, 9)
        for left, right in combinations(range(9), 2):
            received = original[:]
            received[left] = (received[left]+1) % observer.B
            received[right] = (received[right]+observer.B//2) % observer.B
            recovered = observer.decode(received, errors=2)
            self.assertEqual(state, recovered['state'])
            self.assertEqual([left, right], recovered['error_positions'])

    def test_any_four_erasures_in_nine(self):
        state = observer.M-1
        original = observer.raw_outputs(state, 9)
        for erased in combinations(range(9), 4):
            received = [None if i in erased else y for i, y in enumerate(original)]
            recovered = observer.decode(received)
            self.assertEqual(state, recovered['state'])
            self.assertEqual(list(erased), recovered['erasure_positions'])

    def test_mixed_errors_and_erasures(self):
        state = 20000
        original = observer.raw_outputs(state, 9)
        for erased in ((0, 1), (0, 8), (3, 4), (7, 8)):
            for bad in set(range(9))-set(erased):
                received = original[:]
                for index in erased:
                    received[index] = None
                received[bad] = (received[bad]+314159) % observer.B
                recovered = observer.decode(received, errors=1)
                self.assertEqual(state, recovered['state'])
                self.assertEqual([bad], recovered['error_positions'])

    def test_sharpness_witness_and_short_window_failures(self):
        left, right = [observer.raw_outputs(state, 8) for state in observer.COLLISION_STATES]
        self.assertEqual(left[:4], right[:4])
        self.assertEqual(2, sum(a != b for a, b in zip(left[:6], right[:6])))
        ambiguous = left[:6]
        ambiguous[4] = right[4]
        self.assertEqual(1, sum(a != b for a, b in zip(left[:6], ambiguous)))
        self.assertEqual(1, sum(a != b for a, b in zip(right[:6], ambiguous)))
        with self.assertRaises(ValueError):
            observer.decode(ambiguous, errors=1)
        self.assertEqual(4, sum(a != b for a, b in zip(left, right)))
        ambiguous = left[:]
        ambiguous[4:6] = right[4:6]
        self.assertEqual(2, sum(a != b for a, b in zip(left, ambiguous)))
        self.assertEqual(2, sum(a != b for a, b in zip(right, ambiguous)))
        with self.assertRaises(ValueError):
            observer.decode(ambiguous, errors=2)

    def test_reject_bad_budget_and_inconsistent_data(self):
        original = observer.raw_outputs(0, 9)
        original[0] = 1
        original[1] = 2
        self.assertEqual('inconsistent', observer.decode(original, errors=1)['status'])
        with self.assertRaises(ValueError):
            observer.decode([0]*8, errors=2)
        with self.assertRaises(ValueError):
            observer.decode([None]*5)
        with self.assertRaises(ValueError):
            observer.recover_five(range(5), [0, 0, 0, 0, observer.B])


if __name__ == '__main__':
    unittest.main()
