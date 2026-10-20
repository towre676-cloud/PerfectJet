"""Exact cochain, gauge and obstruction replay, independent of E8 machinery."""
from fractions import Fraction as Q
import unittest

from perfectjet.asterion_deformations import (
    CochainSizeError, LieDeformationComplex, cochain_dimensions,
    deformation_receipt,
)


def from_pairs(pairs):
    def bracket(i, j):
        if i < j:
            return pairs.get((i, j), {})
        return {k: -z for k, z in pairs.get((j, i), {}).items()} if i > j else {}
    return bracket


class DeformationTests(unittest.TestCase):
    def test_sl2_exact_rigidity_and_gauge_chain_identity(self):
        model = LieDeformationComplex(3, from_pairs({
            (0, 1): {0: -2}, (0, 2): {1: 1}, (1, 2): {2: -2}}))
        receipt = model.report()
        self.assertEqual((receipt['rank_d1'], receipt['rank_d2'],
                          receipt['H2_dimension']), (6, 3, 0))
        self.assertEqual(receipt['derivations_dimension'], 3)
        self.assertTrue(receipt['d2_d1_zero'])
        operator = [[1, Q(2, 3), -2], [0, 3, 1], [4, -1, 2]]
        tangent = model.gauge(operator)
        self.assertFalse(any(model.linearized_jacobi(tangent)))
        second = model.second_order_extension(tangent)
        self.assertTrue(second['extends_to_order_two'])
        self.assertTrue(second['residual_zero'])

    def test_abelian_h2_and_an_actual_nonintegrable_direction(self):
        model = LieDeformationComplex(3, lambda i, j: {})
        self.assertEqual(model.report()['H2_dimension'], 9)
        self.assertEqual(len(model.report()['representatives']), 9)
        phi = {(0, 1): {0: 1}, (1, 2): {1: 1}}
        self.assertEqual(model.jacobi_obstruction(phi), [Q(-1), Q(0), Q(0)])
        result = model.second_order_extension(phi)
        self.assertTrue(result['first_order_cocycle'])
        self.assertFalse(result['extends_to_order_two'])
        _, d2 = model.matrices()
        witness = [Q(z) for z in result['left_null_witness']]
        rhs = [-z for z in model.jacobi_obstruction(phi)]
        self.assertNotEqual(sum(a*b for a, b in zip(witness, rhs)), 0)
        for column in zip(*d2):
            self.assertEqual(sum(a*b for a, b in zip(witness, column)), 0)

    def test_abelian_direction_that_is_a_lie_bracket_extends(self):
        model = LieDeformationComplex(3, lambda i, j: {})
        heisenberg = {(0, 1): {2: 1}}
        self.assertFalse(any(model.jacobi_obstruction(heisenberg)))
        self.assertTrue(model.second_order_extension(heisenberg)['extends_to_order_two'])
        h3 = LieDeformationComplex(3, from_pairs(heisenberg))
        self.assertEqual(h3.report()['H2_dimension'], 5)

    def test_second_order_failure_can_start_at_first_order(self):
        model = LieDeformationComplex(3, from_pairs({
            (0, 1): {0: -2}, (0, 2): {1: 1}, (1, 2): {2: -2}}))
        bad = {(0, 1): {0: 1}}
        self.assertTrue(any(model.linearized_jacobi(bad)))
        result = model.second_order_extension(bad)
        self.assertFalse(result['first_order_cocycle'])

    def test_small_dimensions_have_correct_empty_cochain_shapes(self):
        one = LieDeformationComplex(1, lambda i, j: {})
        self.assertEqual(one.report()['H2_dimension'], 0)
        two = LieDeformationComplex(2, lambda i, j: {})
        self.assertEqual(two.report()['H2_dimension'], 2)
        self.assertTrue(two.second_order_extension({(0, 1): {0: 1}})['extends_to_order_two'])

    def test_invalid_input_brackets_and_cochains_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'nonalternating'):
            LieDeformationComplex(2, lambda i, j: {0: 1})
        with self.assertRaisesRegex(ValueError, 'nonantisymmetric'):
            LieDeformationComplex(2, lambda i, j: {0: 1} if i != j else {})
        with self.assertRaisesRegex(ValueError, 'Jacobi'):
            LieDeformationComplex(3, from_pairs({(0, 1): {0: 1}, (1, 2): {1: 1}}))
        model = LieDeformationComplex(3, lambda i, j: {})
        for bad in ([0], {(1, 0): {0: 1}}, {(0, 3): {0: 1}}, {(0, 1): {3: 1}}):
            with self.assertRaises(ValueError):
                model.cochain(bad)

    def test_linear_and_quadratic_terms_match_direct_finite_differences(self):
        # This calculates Jacobi directly in perturbed dense multiplication
        # tables, independently of the module's linearization implementation.
        from itertools import combinations
        n = 4
        model = LieDeformationComplex(n, from_pairs({
            (0, 1): {2: 1}, (0, 2): {3: 1}}))
        phi = [Q((3*i+1) % 7-3, (i % 3)+1)
               for i in range(len(model.slots))]
        perturbation = model.cochain_table(phi)

        def direct_jacobi(t):
            table = [[[model.table[i][j].get(k, 0)
                       + t*perturbation[i][j].get(k, 0)
                       for k in range(n)] for j in range(n)] for i in range(n)]
            out = []
            for i, j, k in combinations(range(n), 3):
                for q in range(n):
                    out.append(sum(table[a][b][p]*table[p][c][q]
                                   for a, b, c in ((i, j, k), (j, k, i), (k, i, j))
                                   for p in range(n)))
            return out

        plus, minus = direct_jacobi(1), direct_jacobi(-1)
        self.assertEqual([(a-b)/2 for a, b in zip(plus, minus)],
                         model.linearized_jacobi(phi))
        self.assertEqual([(a+b)/2 for a, b in zip(plus, minus)],
                         model.jacobi_obstruction(phi))

    def test_semisimple_direct_sum_and_corrupted_cross_bracket(self):
        pairs = {}
        for offset in (0, 3):
            for (i, j), vector in {
                (0, 1): {0: -2}, (0, 2): {1: 1}, (1, 2): {2: -2}
            }.items():
                pairs[i+offset, j+offset] = {k+offset: z for k, z in vector.items()}
        model = LieDeformationComplex(6, from_pairs(pairs))
        result = model.report(False)
        self.assertEqual((result['rank_d1'], result['rank_d2'],
                          result['H2_dimension'], result['derivations_dimension']),
                         (30, 60, 0, 6))
        self.assertEqual(result['basis_triples_checked'], 20)
        pairs[0, 3] = {4: 1}
        with self.assertRaisesRegex(ValueError, 'Jacobi'):
            LieDeformationComplex(6, from_pairs(pairs))

    def test_dimension_bound_fires_before_calling_the_bracket(self):
        calls = []
        with self.assertRaises(CochainSizeError) as caught:
            LieDeformationComplex(248, lambda i, j: calls.append((i, j)))
        self.assertEqual(calls, [])
        self.assertFalse(caught.exception.record['allocated'])
        self.assertEqual(caught.exception.record['C2_dimension'], 7595744)
        self.assertEqual(cochain_dimensions(248)['d2_shape'], [622851008, 7595744])
        with self.assertRaises(ValueError):
            LieDeformationComplex(2, lambda i, j: {}, max_dimension=248)
        with self.assertRaises(ValueError):
            cochain_dimensions(True)

    def test_receipt_is_json_safe(self):
        import json
        result = deformation_receipt()
        json.dumps(result, allow_nan=False)
        self.assertEqual(result['sl2']['H2_dimension'], 0)
        self.assertFalse(result['obstructed_abelian_direction']['extends_to_order_two'])


if __name__ == '__main__':
    unittest.main()
