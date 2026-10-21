"""Corruption and alignment tests for the independent raw-state audit."""
import copy
from fractions import Fraction
from itertools import combinations
import json
import unittest

from research.p521_math import verify_raw_observer as audit


class IndependentRawAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(audit.DEFAULT_RECEIPT.read_text(encoding='utf-8'))
        cls.certificates = {tuple(c['times']): c
                            for c in cls.document['subset_certificates']}

    def test_entire_receipt_and_constructive_sharpness(self):
        result = audit.verify_document(self.document)
        self.assertTrue(result['verified'])
        self.assertEqual(70, result['normalized_patterns'])
        self.assertEqual(126, result['covered_five_subsets'])
        bound = result['maximum_coefficient_bound']
        self.assertEqual(Fraction(59762387137465627635627395045544, audit.M),
                         Fraction(bound['numerator'], bound['denominator']))
        self.assertLess(Fraction(bound['numerator'], bound['denominator']), Fraction(369, 1000))
        self.assertEqual((5, 7, 9), (result['raw_state_observation_minimum'],
                                    result['one_error_observation_minimum'],
                                    result['two_error_observation_minimum']))
        sharpness = result['sharpness']
        left, right = sharpness['eight_outputs']
        midpoint = sharpness['ambiguous_two_error_word']
        self.assertEqual(left[:4], right[:4])
        self.assertEqual(4, sum(a != b for a, b in zip(left, right)))
        self.assertEqual(2, sum(a != b for a, b in zip(left, midpoint)))
        self.assertEqual(2, sum(a != b for a, b in zip(right, midpoint)))

    def test_fraction_free_determinant_and_adjugate(self):
        # Exercise a pivot swap, a negative determinant, and a singular matrix.
        for matrix, expected in (([[0, 2], [3, 4]], -6),
                                 ([[2, 1, 3], [4, 2, 6], [7, 8, 9]], 0),
                                 ([[1, 2, 3], [0, 4, 5], [1, 0, 6]], 22)):
            self.assertEqual(expected, audit.determinant(matrix))
        self.assertEqual([[4, -2], [-3, 0]], audit.adjugate([[0, 2], [3, 4]]))

    def test_membership_index_and_strict_bound_are_distinct_checks(self):
        changed = copy.deepcopy(self.document['subset_certificates'][0])
        changed['basis'][0][0] += 1
        with self.assertRaisesRegex(audit.CertificateError, 'outside'):
            audit.verify_basis(changed)
        changed = copy.deepcopy(self.document['subset_certificates'][0])
        changed['basis'][0] = [2 * x for x in changed['basis'][0]]
        with self.assertRaisesRegex(audit.CertificateError, 'index'):
            audit.verify_basis(changed)
        changed = copy.deepcopy(self.document['subset_certificates'][0])
        changed['basis'][0] = [x + 100 * y for x, y in
                               zip(changed['basis'][0], changed['basis'][1])]
        # A unimodular row operation preserves BOTH membership and determinant,
        # but makes the chosen basis too poor to prove the required small box.
        with self.assertRaisesRegex(audit.CertificateError, 'not strict'):
            audit.verify_basis(changed)

    def test_receipt_corruptions_rejected(self):
        changes = []
        changed = copy.deepcopy(self.document)
        changed['subset_certificates'].pop()
        changes.append(changed)
        changed = copy.deepcopy(self.document)
        changed['subset_certificates'].append(changed['subset_certificates'][0])
        changes.append(changed)
        changed = copy.deepcopy(self.document)
        changed['subset_certificates'][0]['coefficient_bounds'][0]['numerator'] += 1
        changes.append(changed)
        changed = copy.deepcopy(self.document)
        changed['parameters']['multiplier'] += 1
        changes.append(changed)
        changed = copy.deepcopy(self.document)
        changed['parameters']['output_radix'] = float(audit.B)
        changes.append(changed)
        changed = copy.deepcopy(self.document)
        changed['horizon'] = 9.0
        changes.append(changed)
        changed = copy.deepcopy(self.document)
        changed['sharpness_witness']['states'][0] += 1
        changes.append(changed)
        changed = copy.deepcopy(self.document)
        changed['sharpness_witness']['six_outputs'][0][0] += 1
        changes.append(changed)
        changed = copy.deepcopy(self.document)
        changed['sharpness_witness']['ambiguous_one_error_word'][0] += 1
        changes.append(changed)
        for index, changed in enumerate(changes):
            with self.subTest(mutation=index), self.assertRaises(audit.CertificateError):
                audit.verify_document(changed)

    def test_own_inverse_all_subsets_including_shifted_first_position(self):
        for state in (0, 1, audit.M - 1, 20000, 123456789123456789123456789):
            word = audit.raw_word(state, 9)
            for times in combinations(range(9), 5):
                normalized = tuple(t - times[0] for t in times)
                self.assertEqual(state, audit.recover_from_basis(
                    self.certificates[normalized], times, [word[t] for t in times]),
                    (state, times))

    def test_discovery_decoder_agrees_with_independent_state_convention(self):
        # The independent checker above never imports this module.  This test
        # intentionally compares the public implementation against our own
        # recurrence and inversion, especially when position zero is erased.
        from research.p521_math import raw_observer as implementation
        state = 123456789123456789123456789
        word = audit.raw_word(state, 9)
        self.assertEqual(word, implementation.raw_outputs(state, 9))
        times = (4, 5, 6, 7, 8)
        symbols = word[4:]
        independently_recovered = audit.recover_from_basis(
            self.certificates[(0, 1, 2, 3, 4)], times, symbols)
        self.assertEqual(state, independently_recovered)
        self.assertNotEqual(state, state * pow(audit.A, 4, audit.M) % audit.M)
        self.assertEqual(independently_recovered, implementation.recover_five(times, symbols))
        erased = [None] * 4 + symbols
        self.assertEqual(state, implementation.decode(erased)['state'])
        # Cover each allowed mixed budget with the earliest observations erased.
        for n in range(5, 10):
            for errors in range(3):
                for erasures in range(n + 1):
                    if n < 5 + 2 * errors + erasures:
                        continue
                    received = word[:n]
                    for i in range(erasures):
                        received[i] = None
                    for i in range(erasures, erasures + errors):
                        received[i] = (received[i] + 1) % audit.B
                    with self.subTest(n=n, errors=errors, erasures=erasures):
                        result = implementation.decode(received, errors=errors)
                        self.assertEqual(state, result['state'])
                        self.assertEqual(list(range(erasures, erasures + errors)),
                                         result['error_positions'])
                        self.assertEqual(list(range(erasures)), result['erasure_positions'])

    def test_information_bound_for_every_relevant_budget(self):
        self.assertGreater(audit.M, audit.B ** 4)
        for n in range(1, 10):
            for errors in range(3):
                for erasures in range(n + 1):
                    remaining = n - erasures - 2 * errors
                    if 0 <= remaining <= 4:
                        self.assertLess(audit.B ** remaining, audit.M)


if __name__ == '__main__':
    unittest.main()
