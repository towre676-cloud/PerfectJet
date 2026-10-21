"""Exact rotation coverage, corrupted receipts and hidden-parameter controls."""
import copy
import json
from pathlib import Path
import unittest

from research.p521_math import rotations as r


RECEIPT = Path(__file__).resolve().parents[1]/'results'/'rotations.json'


class RotationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(RECEIPT.read_text())
        cls.bank = cls.document['dual_bank']

    def test_complete_public_target_receipt(self):
        verified = r.verify_document(self.document)
        self.assertTrue(verified['full_rotation_orbit'])
        self.assertTrue(verified['six_layouts'])
        self.assertEqual(r.GX, int(self.document['public_x'], 16))
        self.assertTrue(self.document['complete'])
        self.assertEqual((3126, 521, 0),
                         (verified['profiles'], verified['phases'], verified['matches']))
        profiles = self.document['profiles']
        self.assertEqual(534, sum(p['status'] == 'excluded-by-range' for p in profiles))
        self.assertEqual(3608, sum(len(p['traces']) for p in profiles))
        self.assertEqual(461824, sum(len(t['choices']) for p in profiles for t in p['traces']))

    def test_rotation_is_full_cyclic_field_chart(self):
        mask = (1 << 521)-1
        for value in (0, 1, 2, r.GX, r.P-1):
            for phase in range(521):
                cyclic = ((value << phase) | (value >> (521-phase))) & mask
                self.assertEqual(cyclic, r.rotate(value, phase))
                self.assertEqual(value, r.rotate(r.rotate(value, phase), -phase))
        self.assertEqual([23, 55, 25], r.phase_order()[:3])
        self.assertEqual(set(range(521)), set(r.phase_order()))

    def test_relations_never_exclude_satisfiable_state_traces(self):
        for state in (0, 1, r.f.M-1, 123456789123456789123456789):
            for entry in self.bank:
                outputs = [state*pow(r.f.A, t, r.f.M) % r.f.M % r.f.B
                           for t in r.exponents(entry['gaps'])]
                for row in entry['relations']:
                    self.assertTrue(r.verify_relation(row, entry['gaps']))
                    self.assertFalse(r.relation_excludes(outputs, row))

    def test_every_real_raw_coordinate_has_a_retained_prefix_branch(self):
        for initial in (0, r.f.M-1, 20000, 123456789123456789123456789):
            for count in (20, 21, 22):
                limbs, _ = r.f.draw(initial, count, rejection=True)
                for order in ('msb', 'lsb'):
                    target = r.f.assemble(limbs, order) % r.P
                    branches = r.f.interior_sequences(target, count, order)
                    self.assertTrue(any(limbs[b['first_output_index']:
                                              b['first_output_index']+len(b['outputs'])] == b['outputs']
                                        for b in branches))

    def test_corrupted_relation_coverage_and_summaries_rejected(self):
        # A complete single-profile document is enough to test every receipt
        # boundary; the first test separately verifies all 521 phases.
        base = copy.deepcopy(self.document)
        base['phases'] = [23]
        base['layouts'] = [[22, 'msb']]
        base['profiles'] = base['profiles'][:1]
        self.assertTrue(r.verify_document(base)['verified'])
        mutations = []
        changed = copy.deepcopy(base)
        changed['dual_bank'][0]['relations'][0][0] += 1
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed['dual_bank'].pop()
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed['profiles'][0]['traces'].pop()
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed['profiles'][0]['traces'][0]['choices'] = 'x'*128
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed['profiles'][0]['traces'][0]['interior']['outputs'][0] ^= 1
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed['profiles'][0]['raw_target'] = '0x1'
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed['phases'] = [24]
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed['complete'] = False
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed['matches'] = [{'phase': 23}]
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed['source_rejection'] = False
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed['rejection_gap_proof']['numerator'][0] += 1
        mutations.append(changed)
        for number, changed in enumerate(mutations):
            with self.subTest(mutation=number), self.assertRaises(ValueError):
                r.verify_document(changed)

    def test_blinded_valid_point_recovery_and_finite_selection(self):
        regular = 0x123456789abcdef123456789abc
        forced_rejection = (r.f.M-1)*pow(r.f.A, -4, r.f.M) % r.f.M
        for initial, phase, sign, expected_candidate in (
                (regular, 173, 1, 1),
                (forced_rejection, 91, -1, 1),
                (regular, 4, 1, 4)):
            control = r.make_point_control(initial, phase, root_sign=sign)
            self.assertEqual(expected_candidate, control['candidate_index'])
            self.assertTrue(r.replay_point_control(control))
            x, y = control['public_x'], control['public_y']
            self.assertEqual((x*x*x+r.CURVE_A*x+r.CURVE_B) % r.P, y*y % r.P)
            # Only x is given to the solver. Neither the phase nor either
            # state nor the point-selection index is passed as a hint.
            result = r.search(x, layouts=[(22, 'msb')], bank=self.bank)
            self.assertTrue(result['complete'])
            self.assertTrue(r.verify_document(result)['full_rotation_orbit'])
            self.assertEqual([(phase, control['coordinate_initial_state'])],
                             [(m['phase'], m['initial_state']) for m in result['matches']])
            if initial == forced_rejection:
                self.assertIn(2, result['matches'][0]['gaps'])
            changed = control.copy()
            changed['public_y'] ^= 1
            with self.assertRaises(ValueError):
                r.replay_point_control(changed)
        other_root = r.make_point_control(regular, 173, root_sign=-1)
        original = r.make_point_control(regular, 173)
        self.assertEqual(original['public_x'], other_root['public_x'])
        self.assertEqual(0, (original['public_y']+other_root['public_y']) % r.P)


if __name__ == '__main__':
    unittest.main()
