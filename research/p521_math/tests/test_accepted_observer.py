"""Source-faithful sharp observer, guarded decoder, and certificate regressions."""
import copy
import json
import random
import unittest
from unittest.mock import patch

from research.p521_math import accepted_observer as a
from research.p521.freelip_recovery import draw


class AcceptedObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(a.RECEIPT.read_text(encoding='utf-8'))

    def test_complete_sharp_theorem_without_discovery(self):
        with patch.object(a, 'reduce_basis', side_effect=AssertionError('LLL used by verifier')):
            checked = a.verify_document(self.document)
        self.assertEqual(checked['accepted_state_observation_minimum'], 6)
        self.assertEqual(checked['same_patterns'], 32)
        self.assertEqual(checked['cross_pattern_pairs'], 961)
        self.assertEqual(checked['coefficient_combinations'], 1556)
        self.assertEqual(checked['guarded_lattice_vectors'], 304)

    def test_five_accepted_outputs_really_collide(self):
        left, right = [a.accepted_trace(s, 6) for s in a.COLLISION_STATES]
        self.assertEqual(left['outputs'][:5], [53806666, 63148225, 39235656,
                                              43695102, 27978396])
        self.assertEqual(left['outputs'][:5], right['outputs'][:5])
        self.assertEqual(left['gaps'][:4], [1, 1, 1, 2])
        self.assertEqual(right['gaps'][:4], [1, 1, 1, 1])
        self.assertEqual(a.A*left['states'][3] % a.M, a.M-32041695)
        self.assertEqual(left['outputs'][5], 37823841)
        self.assertEqual(right['outputs'][5], 63084375)
        # Compare with the pre-existing advance-before-emission source model.
        for state, trace in zip(a.COLLISION_STATES, (left, right)):
            predecessor = pow(a.A, -1, a.M)*state % a.M
            self.assertEqual(draw(predecessor, 6, rejection=True),
                             (trace['outputs'], trace['states']))

    def test_constructive_decoder_and_actual_forced_rejections(self):
        # Force a rejection at each of the five raw transition positions.
        forced = [pow(a.A, -j, a.M)*(a.M-1) % a.M for j in range(1, 6)]
        states = [0, 1, 42, a.THRESHOLD-1, *a.COLLISION_STATES, *forced]
        rng = random.Random(734)
        states.extend(rng.randrange(a.THRESHOLD) for _ in range(12))
        for state in states:
            with self.subTest(state=state):
                trace = a.accepted_trace(state, 8)
                self.assertEqual(a.recover_accepted(trace['outputs']), state)
                self.assertEqual(a.recover_accepted(trace['outputs'][:6]), state)
        for state in forced:
            self.assertIn(2, a.accepted_trace(state, 6)['gaps'])
        self.assertIsNone(a.recover_accepted([0, 0, 0, 0, 0, 1]))

    def test_initial_call_has_unavoidable_double_fibres(self):
        q = a.no_consecutive_rejections()
        self.assertEqual((q['numerator'][0]+a.A*q['numerator'][1]) % a.M, 0)
        self.assertLess(q['maximum'], a.M)
        for distance in (1, 2, 32041695, a.B-1):
            rejected = a.M-distance
            emitting = a.A*rejected % a.M
            preimages = a.first_call_preimages(emitting)
            self.assertEqual(len(preimages), 2)
            self.assertIn(rejected, preimages)
            self.assertEqual([draw(s, 9, rejection=True)[0] for s in preimages],
                             [a.accepted_trace(emitting, 9)['outputs']]*2)
        self.assertEqual(a.first_call_preimages(0), [0])

    def test_missing_pattern_and_wrong_guards_rejected(self):
        damaged = copy.deepcopy(self.document)
        damaged['cross_patterns'].pop()
        with self.assertRaisesRegex(ValueError, 'unproved'):
            a.verify_document(damaged)
        damaged = copy.deepcopy(self.document)
        damaged['parameters']['accept_below'] += 1
        with self.assertRaisesRegex(ValueError, 'threshold'):
            a.verify_document(damaged)

    def test_basis_membership_index_and_enumeration_tampering_rejected(self):
        certificate = self.document['cross_patterns'][0]
        left, right = certificate['left_gaps'], certificate['right_gaps']
        basis = copy.deepcopy(certificate['basis'])
        basis[0][-1] += 1
        with self.assertRaisesRegex(ValueError, 'outside'):
            a.check_cross_basis(left, right, basis)
        basis = copy.deepcopy(certificate['basis'])
        basis[0] = [2*v for v in basis[0]]
        with self.assertRaisesRegex(ValueError, 'complete'):
            a.check_cross_basis(left, right, basis)
        damaged = copy.deepcopy(self.document)
        damaged['cross_patterns'][0]['ranges'][0][0] += 1
        with self.assertRaisesRegex(ValueError, 'intervals'):
            a.verify_document(damaged)
        damaged = copy.deepcopy(self.document)
        damaged['cross_patterns'][0]['box_vectors'] += 1
        with self.assertRaisesRegex(ValueError, 'replay'):
            a.verify_document(damaged)

    def test_invalid_inputs_and_impossible_suffix(self):
        for state in (-1, a.THRESHOLD, a.M, True):
            with self.assertRaises(ValueError):
                a.accepted_trace(state, 6)
        for outputs in ([1]*5, [a.B]*6, [True]*6):
            with self.assertRaises(ValueError):
                a.recover_accepted(outputs)
        outputs = a.accepted_trace(a.COLLISION_STATES[0], 8)['outputs']
        outputs[-1] ^= 1
        self.assertIsNone(a.recover_accepted(outputs))


if __name__ == '__main__':
    unittest.main()
