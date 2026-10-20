"""Exact affine straightening, singular vectors and a nonclassical arc relation."""
from fractions import Fraction as Q
import copy
import json
import unittest

from perfectjet.asterion_relations import (
    AffinePBW, OMEGA_3875, _add, arc_nonmembership_certificate,
    highest_weight_dimension, jet_derivative, relations_receipt,
    verify_relation_certificate, weight_four_completeness_receipt,
)


class AffineRelationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = AffinePBW()
        cls.quadratic, cls.jet, cls.candidates = cls.module.weight_four_candidates()
        cls.relation = {}
        for candidate, coefficient in zip(cls.candidates, (1, -8, 24)):
            _add(cls.relation, candidate, coefficient)

    def test_pbw_swap_has_the_exact_negative_current_commutator(self):
        m = self.module
        e = next(iter(m.algebra.simple_e(0)))
        f = next(iter(m.algebra.simple_f(0)))
        left = m.normalize(((1, e), (1, f)))
        _add(left, m.normalize(((1, f), (1, e))), -1)
        self.assertEqual(left, {((2, 0),): Q(1)})
        vacuum = {(): Q(1)}
        self.assertTrue(m.mode_commutator_check(e, 1, f, -1, vacuum))
        self.assertTrue(m.mode_commutator_check(e, 0, f, -1,
                                              {((1, e),): Q(1)}))
        self.assertTrue(m.mode_commutator_check(0, 2, 0, -2, vacuum))

    def test_opposition_is_anti_lie_on_every_simple_generator_and_basis_vector(self):
        m = self.module
        generators = [next(iter(g)) for i in range(8)
                      for g in (m.algebra.simple_e(i), m.algebra.simple_f(i))]
        for a in generators:
            for b in range(248):
                lhs = {m.opposite[c]: z*m.tau_sign[c]
                       for c, z in m.algebra.basis_bracket(a, b).items()}
                rhs = {c: z*m.tau_sign[a]*m.tau_sign[b]
                       for c, z in m.algebra.basis_bracket(m.opposite[b], m.opposite[a]).items()}
                self.assertEqual(lhs, rhs)

    def test_level_one_singular_square_and_level_two_counterexample(self):
        m = self.module
        singular = m.singular_square()
        self.assertTrue(all(m.finite_highest_checks(singular)))
        for mode in (1, 2):
            for index in range(248):
                self.assertEqual(m.act(index, mode, singular), {})
        other = AffinePBW(level=2)
        theta = m.algebra.root_index[m.algebra.roots[-1]]
        self.assertEqual(other.act(other.opposite[theta], 1, singular),
                         {((1, theta),): Q(2)})
        self.assertEqual(other.pairing(singular, singular), 4)

    def test_translation_and_divided_jet_convention_agree(self):
        m = self.module
        s = m.singular_square()
        original = m.leading_li_symbol(s)['polynomial']
        first = m.derivative(s)
        second = m.derivative(first)
        self.assertEqual(m.leading_li_symbol(first)['polynomial'], jet_derivative(original))
        self.assertEqual(m.leading_li_symbol(second)['polynomial'],
                         jet_derivative(jet_derivative(original)))

    def test_nonzero_highest_3875_tensor_and_null_lift(self):
        m = self.module
        self.assertEqual(len(self.quadratic), 7)
        self.assertEqual(len(self.jet), 783)
        self.assertEqual(len(self.relation), 804)
        for candidate in self.candidates:
            self.assertTrue(all(m.finite_highest_checks(candidate)))
        self.assertTrue(all(m.root_weight(word) == OMEGA_3875 for word in self.relation))
        gram = [[m.pairing(a, b) for b in self.candidates] for a in self.candidates]
        self.assertEqual(gram, [[45696, -336, -2016], [-336, 210, 84], [-2016, 84, 112]])
        self.assertFalse(any(m.pairing(a, self.relation) for a in self.candidates))
        self.assertEqual(m.pairing(self.relation, self.relation), 0)
        symbol = m.leading_li_symbol(self.relation)
        self.assertEqual(symbol['differential_degree'], 1)
        self.assertEqual(symbol['polynomial'], self.jet)
        self.assertEqual(highest_weight_dimension((1,0,0,0,0,0,0,0)), 3875)
        self.assertEqual(highest_weight_dimension((0,0,0,0,0,0,2,0)), 27000)

    def test_independent_modular_rank_certificates_exclude_old_sources(self):
        proof = arc_nonmembership_certificate(self.module)
        self.assertTrue(proof['passed'])
        a = proof['symmetric_cubic_source']
        b = proof['quadratic_null_module_tensor_current_source']
        self.assertEqual((a['columns'], a['rows'], a['rank_mod_prime']), (364, 791, 364))
        self.assertEqual((b['columns'], b['rows'], b['rank_mod_prime']), (1092, 3366, 1092))
        self.assertEqual(len(set(a['selected_original_rows'])), 364)
        self.assertEqual(set(b['pivot_columns']), set(range(1092)))
        self.assertTrue(all(z % 1009 for z in a['nonzero_pivot_values']))

    def test_complete_pbw_sector_enumeration_and_bounded_requests(self):
        sector = self.module.weight_four_sector()
        self.assertEqual(len(sector), 14441)
        self.assertEqual(len(set(sector)), 14441)
        self.assertEqual(sum(len(word) == 4 for word in sector), 13328)
        self.assertEqual(sum(len(word) == 3 for word in sector), 1092)
        self.assertEqual(sum(len(word) == 2 for word in sector), 21)
        with self.assertRaises(ValueError):
            self.module.weight_four_sector(limit=100)
        for bad in (((True, 0),), ((0, 0),), ((1, 248),), ((5, 0),)):
            with self.assertRaises(ValueError):
                self.module.normalize(bad)
        with self.assertRaises(ValueError):
            relations_receipt(exhaustive='yes')

    def test_serialized_null_lift_detects_coefficient_corruption(self):
        record = {'relation': [{'word': word, 'coefficient': str(z)}
                               for word, z in sorted(self.relation.items())]}
        self.assertTrue(verify_relation_certificate(record)['passed'])
        corrupt = copy.deepcopy(record)
        corrupt['relation'][0]['coefficient'] = str(Q(corrupt['relation'][0]['coefficient'])+1)
        result = verify_relation_certificate(corrupt)
        self.assertFalse(result['passed'])
        self.assertFalse(result['checks']['prescribed_lift'])
        duplicate = copy.deepcopy(record)
        duplicate['relation'].append(duplicate['relation'][0])
        with self.assertRaises(ValueError):
            verify_relation_certificate(duplicate)

    def test_json_records_remain_exact(self):
        # Full14,441-row replay is an explicit release receipt, rather than a
        # repeated79-second unit-test loop.  This panel checks the published
        # record contract and does not call it a full-sector proof.
        receipt = relations_receipt()
        json.dumps(receipt, allow_nan=False)
        self.assertTrue(receipt['passed'])
        self.assertEqual(receipt['candidate_combination'], [1, -8, 24])
        self.assertFalse(receipt['nonzero_arc_kernel_generator_certified_in_this_run'])
        self.assertFalse(receipt['full_arc_kernel_claim'])

    def test_projected_polarization_closes_the_complete_weight_four_kernel(self):
        proof = weight_four_completeness_receipt(self.module)
        self.assertTrue(proof['passed'])
        self.assertTrue(all(proof['checks'].values()))
        self.assertEqual(proof['arc_character_through_weight4'], [1,248,4124,34752,217001])
        self.assertEqual(proof['simple_character_through_weight4'], [1,248,4124,34752,213126])
        self.assertEqual(proof['weight4_arc_kernel_dimension'], 3875)
        self.assertEqual(proof['mixed_weight4_arc_dimension'], 151373)
        self.assertEqual(proof['Li_degree2_weight4_dimension'], 65380)
        self.assertEqual(proof['graded_kernel_per_sector'], 31)
        self.assertEqual(proof['graded_kernel_sector_count'], 125)
        self.assertEqual(proof['graded_kernel_Li_differential_degree'], 1)
        self.assertFalse(proof['graded_kernel_derivation']['explicit_generator_transported_to_Jordan_coordinates'])
        rows = proof['cubic_highest_modules']
        self.assertEqual([row['dimension'] for row in rows], [248,30380,779247,1763125])
        self.assertEqual([Q(row['mu_P_I_delta_scalar']) for row in rows],
                         [Q(54,31), Q(3,7), Q(13,7), Q(3)])
        self.assertEqual([Q(row['mu_P_W_delta_scalar']) for row in rows],
                         [Q(39,31), Q(18,7), Q(8,7), Q(0)])
        self.assertEqual([row['P_W_delta_is_zero'] for row in rows], [False,False,False,True])
        self.assertFalse(proof['infinite_differential_kernel_claim'])
        with self.assertRaisesRegex(ValueError, 'level-one'):
            weight_four_completeness_receipt(AffinePBW(level=2))


if __name__ == '__main__':
    unittest.main()
