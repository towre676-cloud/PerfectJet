"""Exact independent checks for recoupling and the higher-program boundaries."""
import copy
from fractions import Fraction as Q
import json
from math import comb
import unittest

from perfectjet.asterion_higher import (
    CurrentFormDGLA, admissible, compile_jacobi_constraints, dynamical_r_boundary,
    e8_symmetric_square_obstruction, evaluate_jacobi_constraints, higher_receipt,
    jacobi_constraint_receipt, linearized_jacobi_rows, moyal_closure_obstruction,
    pentagon_receipt, principal_dj_cobracket_obstruction, recoupling_matrix,
    terminating_4f3, transvectant_coefficient, verify_symmetric_square_certificate,
    wigner_6j, wigner_6j_squared,
)


class ExactRacahTests(unittest.TestCase):
    def test_known_integer_and_half_integer_symbols_without_floating_roots(self):
        integer = wigner_6j(1, 1, 1, 1, 1, 1)
        self.assertEqual(integer['square'], Q(1, 36))
        self.assertEqual(integer['sign'], 1)
        self.assertEqual(integer['racah_sum'], 96)
        self.assertTrue(integer['hypergeometric_replay'])
        half = wigner_6j(Q(1, 2), Q(1, 2), 0, Q(1, 2), Q(1, 2), 0)
        self.assertEqual(half['square'], Q(1, 4))
        self.assertEqual(half['sign'], -1)
        self.assertEqual(wigner_6j_squared(1, 1, 3, 1, 1, 1), 0)
        self.assertFalse(admissible(Q(1, 2), Q(1, 2), Q(1, 2)))

    def test_balanced_terminating_series_and_poles_are_exact(self):
        result = terminating_4f3([5, -1, -1, -1], [1, 1, 1])
        self.assertEqual(result['terms'], (1, -5))
        self.assertEqual(result['value'], -4)
        self.assertTrue(result['balanced'])
        self.assertEqual(terminating_4f3([-2, 1, 1, 1], [1, 1, 1])['value'], 0)
        with self.assertRaises(ValueError):
            terminating_4f3([1, 1, 1, 1], [2, 2, 2])
        with self.assertRaises(ValueError):
            terminating_4f3([-2, 1, 1, 1], [0, 1, 1])
        with self.assertRaises(ValueError):
            wigner_6j(.5, 1, 1, 1, 1, 1)

    def test_tetrahedral_symmetry_and_public_cache_copies(self):
        a = wigner_6j(1, 2, 2, 2, 1, 1)
        b = wigner_6j(2, 1, 2, 1, 2, 1)
        self.assertEqual((a['sign'], a['square']), (b['sign'], b['square']))
        a['square'] = 100
        self.assertNotEqual(wigner_6j(1, 2, 2, 2, 1, 1)['square'], 100)
        result = recoupling_matrix(1, 1, 1, 1)
        result['coefficients'] = ()
        self.assertEqual(len(recoupling_matrix(1, 1, 1, 1)['coefficients']), 3)

    def test_rational_recoupling_matches_independent_polynomial_differentiation(self):
        from perfectjet.polynomial import Poly
        from perfectjet.transvectants import transvectant
        a, b, c, d = 1, 2, 1, 2
        result = recoupling_matrix(a, b, c, d)
        def form(spin, offset):
            return Poly({(2 * spin - i, i): Q((i + offset) * (-1) ** i) * comb(2 * spin, i)
                         for i in range(2 * spin + 1)})
        p, q, r = form(a, 1), form(b, 2), form(c, 3)
        for index, e in enumerate(result['left_intermediates']):
            e = int(e)
            left = transvectant(transvectant(p, q, a + b - e), r, e + c - d)
            right = Poly()
            for f, coefficient in zip(result['right_intermediates'], result['coefficients'][index]):
                f = int(f)
                right += coefficient * transvectant(p, transvectant(q, r, b + c - f), a + f - d)
            self.assertEqual(left, right)
        self.assertEqual(result['weighted_orthogonality_checks'], 9)
        self.assertEqual(result['six_j_square_checks'], 9)
        self.assertTrue(result['passed'])

    def test_pentagon_has_nontrivial_associators_and_equal_paths(self):
        result = pentagon_receipt()
        self.assertTrue(result['passed'])
        self.assertEqual(result['multiplicity'], 3)
        self.assertEqual(result['long_path_matrix'], result['short_path_matrix'])
        self.assertNotEqual(result['direct_matrix'], [[Q(i == j) for j in range(3)] for i in range(3)])
        self.assertEqual(len(result['edge_matrices']), 6)


class JacobiCompilerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from perfectjet.asterion_principal import PrincipalE8
        cls.couplings = PrincipalE8().couplings()

    def test_keeps_outside_intermediate_equations_and_detects_lost_constraints(self):
        receipt = jacobi_constraint_receipt(couplings=self.couplings)
        self.assertEqual(len(receipt['equation_intermediates']), 15)
        self.assertEqual(receipt['quadratic_monomial_count'], 14)
        self.assertEqual(receipt['full_polynomial_equation_rank'], 13)
        self.assertEqual(receipt['retained_sector_equation_rank'], 4)
        self.assertEqual(receipt['independent_constraints_lost_by_truncation'], 9)
        self.assertTrue(receipt['actual_coupling_products_match_one_dimensional_kernel'])
        self.assertTrue(receipt['evaluation']['passed'])
        self.assertIsNotNone(receipt['omitted_constraint_witness'])

    def test_bad_reduced_coupling_is_detected(self):
        compiled = compile_jacobi_constraints(7, 11, 13, 17)
        first = tuple(compiled['equations'][0][0][0][0])
        changed = dict(self.couplings)
        changed[first] *= 2
        self.assertFalse(evaluate_jacobi_constraints(compiled, changed)['passed'])

    def test_actual_jacobian_matches_exact_quadratic_finite_difference(self):
        compiled = compile_jacobi_constraints(7, 11, 13, 17)
        jacobian = linearized_jacobi_rows(compiled, self.couplings)
        self.assertEqual(len(jacobian['variables']), 162)
        eta = {variable: Q((i % 5) - 2) for i, variable in enumerate(jacobian['variables'])}
        plus = {v: x * (1 + eta.get(v, 0)) for v, x in self.couplings.items()}
        minus = {v: x * (1 - eta.get(v, 0)) for v, x in self.couplings.items()}
        fp = evaluate_jacobi_constraints(compiled, plus)['residuals']
        fm = evaluate_jacobi_constraints(compiled, minus)['residuals']
        for row, scale, x, y in zip(jacobian['rows'], jacobian['row_scales'], fp, fm):
            actual = sum(coefficient * eta[jacobian['variables'][i]] for i, coefficient in row)
            self.assertEqual(actual, scale * (x - y) / 2)
        # Exact diagonal changes of module scales are tangent gauge directions.
        for row in jacobian['rows']:
            value = sum(coefficient * (a + b - c - 1)
                        for i, coefficient in row for a, b, c in [jacobian['variables'][i]])
            self.assertEqual(value, 0)


class HigherBoundaryTests(unittest.TestCase):
    def test_current_form_dgla_and_actual_contraction_transfer(self):
        dg = CurrentFormDGLA(2)
        self.assertEqual(dg.differential({(0, 2, 0): 1}), {(0, 1, 1): 2})
        self.assertEqual(dg.homotopy({(1, 1, 1): 1}), {(1, 2, 0): Q(1, 2)})
        self.assertEqual(dg.transfer_binary({0: 1}, {1: 1}), {1: 2})
        result = dg.verify()
        self.assertTrue(result['passed'])
        self.assertEqual(result['dimension'], 15)
        self.assertEqual(result['differential_rank'], 6)
        self.assertEqual(result['cohomology_dimension'], 3)
        self.assertEqual(result['graded_jacobi_triples'], 3375)
        self.assertTrue(result['all_transferred_brackets_arity_at_least_three_vanish'])
        with self.assertRaises(ValueError):
            dg.bracket({(0, 2, 1): 1}, {})
        with self.assertRaises(ValueError):
            dg.differential({(0, 1, 0): .5})

    def test_symmetric_square_has_no_adjoint_and_rank_certificate_rejects_tampering(self):
        result = e8_symmetric_square_obstruction()
        self.assertEqual(result['symmetric_square_dimension'], 30876)
        self.assertEqual(result['raising_matrix_shape'], [50, 36])
        self.assertEqual(result['raising_matrix_rank'], 36)
        self.assertEqual(result['highest_vector_kernel_dimension'], 0)
        self.assertTrue(verify_symmetric_square_certificate(result)['valid'])
        wrong = copy.deepcopy(result)
        wrong['raising_matrix'][0][0] += 1
        self.assertFalse(verify_symmetric_square_certificate(wrong)['valid'])
        wrong = copy.deepcopy(result)
        wrong['raising_matrix_rank'] = 35
        self.assertFalse(verify_symmetric_square_certificate(wrong)['valid'])

    def test_moyal_degree_escape_is_an_actual_nonzero_coefficient(self):
        result = moyal_closure_obstruction()
        self.assertEqual(len(result['commutator_terms']), 29)
        self.assertEqual(result['escaped_term_count'], 21)
        self.assertEqual(result['leading_term'], {'hbar_power': 1, 'x_power': 57,
                                                'y_power': 57, 'coefficient': 3364})
        self.assertFalse(result['closed_in_eight_blocks'])

    def test_principal_dj_inclusion_obstruction_is_preserved(self):
        result = principal_dj_cobracket_obstruction()
        self.assertTrue(result['passed'])
        self.assertFalse(result['principal_inclusion_is_lie_bialgebra_map'])
        self.assertEqual(result['witness_on_principal_e_wedge_h'], 0)
        self.assertEqual(result['witness_on_delta_principal_e'], 182)

    def test_dynamical_derivative_is_necessary_and_elliptic_status_is_honest(self):
        for parameter in (1, Q(2), Q(-3, 2)):
            result = dynamical_r_boundary(parameter)
            self.assertTrue(result['passed'])
            self.assertFalse(result['ordinary_cybe_holds'])
            self.assertTrue(result['classical_dynamical_ybe_holds'])
            self.assertEqual(len(result['ordinary_cybe_tensor']), 6)
            self.assertIn('Not implemented', result['elliptic_extension_status'])
        with self.assertRaises(ValueError):
            dynamical_r_boundary(0)

    def test_full_declared_receipt_is_json_safe_and_scope_is_explicit(self):
        result = higher_receipt(exhaustive=True)
        self.assertTrue(result['passed'])
        self.assertEqual(result['current_form_dgla']['dimension'], 21)
        self.assertEqual(len(result['jacobi_constraints']), 5)
        self.assertIn('does not mean all E8 spin quadruples', result['scope'])
        json.dumps(result)


if __name__ == '__main__':
    unittest.main()
