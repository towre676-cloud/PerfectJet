"""Independent small matrix checks for Asterion basis certificates."""
import copy
from fractions import Fraction as Q
from itertools import combinations
import random
import unittest

from perfectjet.asterion_basis import (
    AsterionBasis, BasisCompilationError, basis_receipt, compile_basis,
    e8_response_basis, e8_response_receipt, optimize_basis, primitive, sparse, tensor_cost, verify_certificate,
    verify_jacobi,
)


def matrix_bracket(left, right):
    """Compute the sl2 bracket directly as 2x2 matrix multiplication.

    Ambient vectors are h,e,f coordinates, independently of the module's
    hand-written demonstration structure constants.
    """
    def matrix(v):
        h, e, f = (Q(v.get(i, 0)) for i in range(3))
        return [[h, e], [f, -h]]
    a, b = matrix(left), matrix(right)
    c = [[sum(a[i][k] * b[k][j] - b[i][k] * a[k][j] for k in range(2))
          for j in range(2)] for i in range(2)]
    return {i: x for i, x in enumerate((c[0][0], c[0][1], c[1][0])) if x}


class AsterionBasisTests(unittest.TestCase):
    def canonical(self):
        return AsterionBasis(3, matrix_bracket, [{i: 1} for i in range(3)])

    def compiled(self):
        return compile_basis(3, matrix_bracket, [{1: 1, 2: 1}],
                             [{1: 1}, {2: 1}], seed_labels=['e+f'], probe_labels=['e', 'f'])

    def test_compiles_actual_mixed_vectors_and_bidirectional_coordinates(self):
        b = self.compiled()
        self.assertEqual(b.columns, ({1: Q(1), 2: Q(1)}, {0: Q(1)}, {1: Q(1)}))
        self.assertEqual(b.labels, ('A(e+f;)', 'A(e+f;e)', 'A(e+f;e,e)'))
        self.assertEqual(b.determinant, 1)
        self.assertTrue(b.unimodular)
        self.assertTrue(b.verify_inverse()['valid'])
        rng = random.Random(104)
        for _ in range(30):
            vector = {i: Q(rng.randrange(-10, 11), rng.randrange(1, 8)) for i in range(3)}
            vector = sparse(vector, 3)
            self.assertEqual(b.ambient(b.coordinates(vector)), vector)
            self.assertEqual(b.coordinates(b.ambient(vector)), vector)

    def test_replays_all_brackets_against_independent_matrix_multiplication(self):
        b = self.compiled()
        for i in range(3):
            for j in range(3):
                expected = matrix_bracket(b.columns[i], b.columns[j])
                self.assertEqual(b.ambient(b.basis_bracket(i, j)), expected)
        record = b.record(pairs=list(combinations(range(3), 2)))
        self.assertTrue(verify_certificate(matrix_bracket, record)['valid'])
        self.assertEqual(verify_certificate(matrix_bracket, record)['bracket_pairs'], 3)
        restored = AsterionBasis.from_record(matrix_bracket, record)
        self.assertEqual(restored.columns, b.columns)

    def test_tampering_inverse_determinant_word_elimination_or_bracket_is_rejected(self):
        record = self.compiled().record(pairs=list(combinations(range(3), 2)))
        mutants = []
        wrong = copy.deepcopy(record)
        wrong['inverse_rows'][0][0][1] = '9'
        mutants.append(wrong)
        wrong = copy.deepcopy(record)
        wrong['determinant'] = '-1'
        mutants.append(wrong)
        wrong = copy.deepcopy(record)
        wrong['provenance']['basis_words'][1]['word'] = [1]
        mutants.append(wrong)
        wrong = copy.deepcopy(record)
        wrong['provenance']['elimination_history'][1]['pivot'] = 2
        mutants.append(wrong)
        wrong = copy.deepcopy(record)
        wrong['bracket_images'][0]['coordinates'] = []
        mutants.append(wrong)
        wrong = copy.deepcopy(record)
        wrong['bracket_coverage']['pairs'] = 999
        mutants.append(wrong)
        for wrong in mutants:
            self.assertFalse(verify_certificate(matrix_bracket, wrong)['valid'])
        for wrong in (None, [], 3, 'not a certificate'):
            self.assertFalse(verify_certificate(matrix_bracket, wrong)['valid'])

    def test_singular_basis_and_floating_coefficients_rejected(self):
        with self.assertRaisesRegex(ValueError, 'singular'):
            AsterionBasis(3, matrix_bracket, [{0: 1}, {1: 1}, {1: 2}])
        for bad in ({0: 0.5}, {True: 1}, {3: 1}, [1, 2]):
            with self.assertRaises(ValueError):
                sparse(bad, 3)
        with self.assertRaises(ValueError):
            self.canonical().shear(0, 1, Q(1, 2))

    def test_primitive_line_is_not_a_lattice_index_claim(self):
        vector, factor = primitive({0: Q(-2, 3), 1: Q(4, 9)})
        self.assertEqual(vector, {0: Q(3), 1: Q(-2)})
        self.assertEqual(factor, Q(-9, 2))
        b = AsterionBasis(3, matrix_bracket, [{0: 2}, {1: 1}, {2: 1}])
        self.assertTrue(b.integral)
        self.assertFalse(b.unimodular)
        self.assertEqual(b.determinant, 2)
        record = b.record()
        record['same_integer_lattice'] = True
        self.assertFalse(verify_certificate(matrix_bracket, record)['valid'])

    def test_failed_compilation_distinguishes_closed_obstruction_from_depth_limit(self):
        with self.assertRaises(BasisCompilationError) as caught:
            compile_basis(3, matrix_bracket, [{1: 1}], [{0: 1}])
        failure = caught.exception.record
        self.assertEqual(failure['rank'], 1)
        self.assertTrue(failure['probe_invariant_span'])
        self.assertTrue(failure['all_future_obstruction'])
        witness = {i: Q(x) for i, x in failure['annihilator']}
        self.assertEqual(sum(witness.get(i, 0) * x for i, x in {1: 1}.items()), 0)
        self.assertTrue(witness)
        with self.assertRaises(BasisCompilationError) as caught:
            compile_basis(3, matrix_bracket, [{1: 1, 2: 1}], [{1: 1}], max_depth=0)
        self.assertFalse(caught.exception.record['all_future_obstruction'])
        # An invariant accepted span does not contain a seed that the resource
        # limit prevented us from examining.  It cannot certify all futures.
        with self.assertRaises(BasisCompilationError) as caught:
            compile_basis(2, lambda a, b: {}, [{0: 1}, {1: 1}], [], max_candidates=1)
        failure = caught.exception.record
        self.assertTrue(failure['probe_invariant_span'])
        self.assertFalse(failure['all_seeds_in_span'])
        self.assertEqual(failure['seed_indices_outside_span'], [1])
        self.assertFalse(failure['all_future_obstruction'])

    def test_integer_shear_and_reverse_preserve_lattice_and_bracket(self):
        b = self.compiled()
        for i, j in ((0, 1), (2, 0), (1, 2)):
            moved = b.shear(i, j, -3)
            self.assertEqual(moved.determinant, b.determinant)
            self.assertTrue(moved.unimodular)
            self.assertEqual(moved.shear(i, j, 3).columns, b.columns)
            self.assertTrue(verify_jacobi(3, moved.bracket)['valid'])
            record = moved.record(pairs=list(combinations(range(3), 2)))
            self.assertTrue(verify_certificate(matrix_bracket, record)['valid'])

    def test_search_measures_a_real_support_improvement_without_claiming_global_optimality(self):
        canonical = self.canonical()
        sheared = canonical.shear(1, 0, 1)
        self.assertEqual(tensor_cost(canonical)['output_terms'], 3)
        self.assertEqual(tensor_cost(sheared)['output_terms'], 6)
        optimized = optimize_basis(sheared, rounds=2, max_trials=48)
        self.assertLess(optimized.optimization['final']['objective'], optimized.optimization['initial']['objective'])
        self.assertEqual(optimized.optimization['final']['output_terms'], 3)
        self.assertFalse(optimized.optimization['global_optimality_claimed'])
        self.assertTrue(optimized.optimization['integer_lattice_preserved_relative_to_input'])
        self.assertIsNone(sheared.optimization)
        self.assertTrue(verify_jacobi(3, optimized.bracket)['valid'])
        record = optimized.record(pairs=list(combinations(range(3), 2)))
        self.assertTrue(verify_certificate(matrix_bracket, record)['optimization_replayed'])
        for key in ('initial', 'final'):
            wrong = copy.deepcopy(record)
            wrong['optimization'][key]['output_terms'] += 1
            self.assertFalse(verify_certificate(matrix_bracket, wrong)['valid'])
        wrong = copy.deepcopy(record)
        wrong['optimization']['accepted_moves'][0]['after'][0] -= 1
        self.assertFalse(verify_certificate(matrix_bracket, wrong)['valid'])
        wrong = copy.deepcopy(record)
        wrong['optimization']['workload_pairs'] = [[0, 1]]
        self.assertFalse(verify_certificate(matrix_bracket, wrong)['valid'])

    def test_workload_scope_and_resource_limits_are_explicit(self):
        b = self.canonical()
        self.assertFalse(tensor_cost(b, pairs=[(0, 1)])['full_unordered_tensor'])
        with self.assertRaises(ValueError):
            tensor_cost(b, max_pairs=2)
        with self.assertRaises(ValueError):
            optimize_basis(b, pairs=[(0, 1), (0, 1)])
        r = optimize_basis(b, rounds=1, max_trials=1, pairs=[(0, 1)])
        self.assertEqual(r.optimization['trials'], 1)
        self.assertTrue(r.optimization['trial_limit_reached'])
        self.assertFalse(r.optimization['final']['full_unordered_tensor'])

    def test_jacobi_checker_accepts_transport_and_rejects_an_antisymmetric_nonlie_bracket(self):
        self.assertTrue(verify_jacobi(3, self.compiled().bracket)['full_basis_jacobi'])
        def faulty(left, right):
            table = {(0, 1): {0: 1}, (1, 2): {1: 1}, (0, 2): {}}
            out = {}
            for i, a in left.items():
                for j, b in right.items():
                    if i == j:
                        continue
                    for k, c in table[min(i, j), max(i, j)].items():
                        out[k] = out.get(k, 0) + a * b * c * (1 if i < j else -1)
            return {i: v for i, v in out.items() if v}
        failure = verify_jacobi(3, faulty)
        self.assertFalse(failure['valid'])
        self.assertEqual(failure['failure'], 'jacobi')
        self.assertEqual(failure['indices'], [0, 1, 2])

    def test_receipt_is_full_scope_for_its_declared_small_algebra(self):
        r = basis_receipt()
        self.assertTrue(r['certificate_replay']['valid'])
        self.assertTrue(r['jacobi']['full_basis_jacobi'])
        self.assertTrue(r['optimized_inverse']['valid'])
        self.assertEqual(r['optimization']['final']['output_terms'], 3)

    def test_prescribed_e8_basis_is_integral_unimodular_and_replays_its_mixed_words(self):
        from perfectjet.asterion_e8 import E8LieAlgebra
        algebra = E8LieAlgebra()
        basis = e8_response_basis(algebra)
        self.assertEqual(len(basis.columns), 248)
        self.assertEqual(basis.determinant, -1)
        self.assertTrue(basis.unimodular)
        self.assertEqual(sum(map(len, basis.columns)), 256)
        self.assertEqual(sum(map(len, basis.inverse_rows)), 256)
        self.assertEqual(len(basis.provenance['elimination_history']), 3943)
        self.assertEqual(max(len(w['word']) for w in basis.provenance['basis_words']), 28)
        for i in range(8):
            expected = dict(algebra.simple_e(i))
            expected.update(algebra.simple_f(i))
            self.assertEqual(basis.columns[i], expected)
        receipt = e8_response_receipt(algebra=algebra)
        self.assertTrue(receipt['passed'])
        self.assertEqual(receipt['certificate_replay']['word_columns'], 248)
        self.assertEqual(receipt['certificate_replay']['bracket_pairs'], 92)
        self.assertFalse(receipt['tensor_cost']['full_unordered_tensor'])

    def test_full_e8_receipt_preserves_the_negative_sparsity_comparison(self):
        receipt = e8_response_receipt(exhaustive=True)
        self.assertTrue(receipt['passed'])
        self.assertEqual(receipt['certificate_replay']['bracket_pairs'], 30628)
        self.assertEqual(receipt['tensor_cost']['output_terms'], 9062)
        self.assertEqual(receipt['tensor_cost']['nonzero_input_pairs'], 8200)
        comparison = receipt['chevalley_comparison']
        self.assertEqual(comparison['baseline_tensor_cost']['output_terms'], 8347)
        self.assertEqual(comparison['baseline_tensor_cost']['nonzero_input_pairs'], 7752)
        self.assertEqual(comparison['output_term_ratio'], '9062/8347')
        self.assertTrue(comparison['asterion_is_denser'])
        self.assertFalse(comparison['sparsity_advantage_established'])


if __name__ == '__main__':
    unittest.main()
