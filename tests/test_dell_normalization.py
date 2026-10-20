"""Global polynomial proofs plus independent exact scalar-gradient replay."""
from fractions import Fraction as Q
from itertools import permutations
import json
import unittest

from perfectjet import dell_normalization as dn
from perfectjet import dell_normalization_boundary as boundary


def direct_shell(pattern, t, x, y):
    """Values and log-gradients, independently differentiating each ratio."""
    value, dx, dy = Q(0), [Q(0)]*3, [Q(0)]*3
    for n in sorted(set(permutations(pattern))):
        factors, gradients = [], []
        for i in range(3):
            for j in range(i+1, 3):
                u = t**(n[i]-n[j])
                factors.append((u*x[i]-x[j])/(x[i]-x[j]))
                derivative = x[i]*x[j]*(1-u)/(x[i]-x[j])**2
                gradient = [Q(0)]*3
                gradient[i], gradient[j] = derivative, -derivative
                gradients.append(gradient)
        momentum = Q(1)
        for yi, ni in zip(y, n):
            momentum *= yi**ni
        coefficient = factors[0]*factors[1]*factors[2]
        value += momentum*coefficient
        for i in range(3):
            dx[i] += momentum*sum(gradients[j][i]*factors[(j+1)%3]*factors[(j+2)%3]
                                  for j in range(3))
            dy[i] += n[i]*momentum*coefficient
    return value, dx, dy


def direct_bracket(left, right):
    return sum(a*b-c*d for a, b, c, d in zip(left[1], right[2], left[2], right[1]))


class DellNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = dn.normalization_receipt()

    def test_global_polynomial_identities_and_shell_exhaustion(self):
        self.assertTrue(self.receipt['passed'])
        self.assertTrue(all(self.receipt['checks'].values()))
        self.assertEqual(self.receipt['global_identity']['zero_numerator_terms'], 0)
        self.assertEqual(self.receipt['global_identity']['first_order_difference_terms'], 0)
        self.assertEqual([len(self.receipt['first_shell'][str(i)]) for i in range(3)], [6, 3, 3])
        self.assertGreater(self.receipt['global_identity']['raw_bracket_numerator_terms'], 0)

    def test_independent_scalar_gradients_replay_normalization_identity(self):
        for t, x, y in ((2, (1, 3, 7), (2, 5, 11)),
                        (-2, (1, 4, 9), (3, 7, 13)),
                        (Q(3, 5), (2, 7, 17), (Q(1, 2), 3, 19))):
            t, x, y = Q(t), tuple(map(Q, x)), tuple(map(Q, y))
            h1, h2, a, b, c = [direct_shell(pattern, t, x, y) for pattern in
                               ((1, 0, 0), (1, 1, 0), (-1, 0, 1), (-1, 1, 1), (2, 0, 0))]
            raw = direct_bracket(b, h2)+direct_bracket(h1, c)
            correction = h1[0]*direct_bracket(a, h2)+h2[0]*direct_bracket(h1, a)
            self.assertEqual(direct_bracket(h1, h2), 0)
            self.assertEqual(raw, correction)
            if t == 2:
                self.assertEqual(raw, Q(8356261, 901120))

    def test_exact_minor_classifies_every_nonzero_coupling_except_one(self):
        h1, h2, a = dn._shell((1, 0, 0)), dn._shell((1, 1, 0)), dn._shell((-1, 0, 1))
        matrix = dn._minor_matrix(dn._normalizer_columns(h1, h2, a))
        determinant = dn._polynomial_determinant(matrix)
        for t in (Q(2), Q(-2), Q(3, 7), Q(1)):
            self.assertEqual(dn._evaluate(determinant, t, (1, 1, 1)), -(t-1)**14/t**8)
        self.assertEqual(self.receipt['normalizer_classification']['minor_determinant'], '-(t-1)^14/t^8')

    def test_missing_or_misweighted_first_shell_term_is_detected(self):
        h1, h2, a = dn._shell((1, 0, 0)), dn._shell((1, 1, 0)), dn._shell((-1, 0, 1))
        columns = dn._normalizer_columns(h1, h2, a)
        for column in columns:
            self.assertTrue(any(column.values()))
            self.assertTrue(any(dn._specialize_coupling(column, -2).values()))
            self.assertFalse(any(dn._specialize_coupling(column, 1).values()))

    def test_homogeneous_normalizer_freedom_exists_outside_six_term_ansatz(self):
        h1, h2 = dn._shell((1, 0, 0)), dn._shell((1, 1, 0))
        constant = {(0, 0, 0): dn._DELTA}
        column = dn._laurent_add(
            dn._laurent_multiply(h1, dn._bracket_numerator(constant, h2)),
            dn._laurent_multiply(h2, dn._bracket_numerator(h1, constant)))
        self.assertFalse(column)

    def test_receipt_serialization_scope_and_optional_global_evidence(self):
        json.dumps(self.receipt)
        scope = self.receipt['scope']
        self.assertEqual(scope['coordinate_nome'], 0)
        self.assertEqual(scope['momentum_nome_order'], 1)
        self.assertFalse(scope['all_order_integrability_claim'])
        self.assertFalse(scope['full_coordinate_ellipticity_claim'])
        self.assertFalse(scope['global_normalization_uniqueness_claim'])
        self.assertFalse(scope['world_first_priority_claim'])
        full = dn.normalization_receipt(include_numerators=True)
        self.assertEqual(sum(len(row[1]) for row in full['raw_bracket_numerator']),
                         full['global_identity']['raw_bracket_numerator_terms'])
        self.assertEqual(full['global_identity'], self.receipt['global_identity'])


class DellHigherNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.second = dn.second_order_normalization_receipt()
        cls.mixed = dn.mixed_nome_normalization_receipt()

    def test_second_order_global_polynomial_identity(self):
        receipt = self.second
        self.assertTrue(receipt['passed'])
        self.assertTrue(all(receipt['checks'].values()))
        self.assertEqual(receipt['bracket_certificate']['summand_term_counts'], [19902, 13548, 19902])
        self.assertEqual(receipt['bracket_certificate']['difference_terms'], 0)
        self.assertFalse(receipt['second_shell']['C0'])

    def test_quadratic_normalizer_has_complete_generic_rank_certificate(self):
        proof = self.second['homogeneous_normalizer']
        self.assertEqual(proof['dimension'], 21)
        self.assertEqual(proof['generic_rank'], 21)
        self.assertEqual(len(proof['minor_matrix']), 21)
        self.assertEqual(Q(proof['minor_value_at_t_two']), Q(-77175, 16384))
        self.assertFalse(self.second['scope']['all_coupling_rank_classification_claim'])
        json.dumps(self.second)

    def test_mixed_nome_coefficients_are_globally_zero(self):
        receipt = self.mixed
        self.assertTrue(receipt['passed'])
        self.assertEqual(receipt['proof']['zeroth_momentum_zero_terms_by_coordinate_order'], [0, 0])
        self.assertEqual(receipt['proof']['first_momentum_zero_terms_by_coordinate_order'], [0, 0])
        self.assertGreater(receipt['proof']['raw_numerator_terms_by_coordinate_order'][1], 0)
        self.assertFalse(receipt['scope']['all_order_integrability_claim'])
        self.assertFalse(receipt['scope']['full_coordinate_ellipticity_claim'])

    def test_coordinate_correction_matches_independent_theta_ratio_expansion(self):
        t, x = Q(2), (Q(1), Q(3), Q(7))
        for n in ((-1, 0, 1), (2, 0, 0), (1, 1, 1)):
            expected = Q(0)
            for i in range(3):
                for j in range(i+1, 3):
                    z, u = x[i]/x[j], t**(n[i]-n[j])*x[i]/x[j]
                    # theta_p(u)/theta_p(z), factoring out (1-u)/(1-z).
                    # Its first coefficient is the numerator correction
                    # -(u+1/u) minus the denominator correction -(z+1/z).
                    expected += z+1/z-u-1/u
            self.assertEqual(dn._evaluate(dn._coordinate_first_correction(n), t, x), expected)


class DellQuadraticBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = boundary.quadratic_boundary_receipt()
        cls.symbolic_columns = boundary._quadratic_columns()[3]

    def test_complete_coupling_boundary_distinguishes_parameter_and_function_kernels(self):
        self.assertTrue(self.receipt['passed'])
        self.assertTrue(all(self.receipt['checks'].values()))
        for key, expected in {'-1': (20, 21, 1), '-2': (21, 21, 0), '-3': (21, 21, 0),
                              'zeta3': (19, 19, 0), '1': (0, 19, 19)}.items():
            case = self.receipt['cases'][key]
            self.assertEqual((case['operator']['rank'], case['function_space']['rank'],
                              case['nonzero_functional_freedom_dimension']), expected)
        self.assertEqual(self.receipt['cases']['zeta3']['operator_null_function_image_term_counts'], [0, 0])
        self.assertGreater(self.receipt['cases']['-1']['operator_null_function_image_term_counts'][0], 0)
        json.dumps(self.receipt)

    def test_lower_rank_witness_minor_replays_by_independent_dense_row_elimination(self):
        field = boundary._Eisenstein
        for coupling in (-1, 'zeta3'):
            proof = self.receipt['cases'][str(coupling)]['operator']
            columns = [boundary._specialize(column, coupling) for column in self.symbolic_columns]
            rows = [(tuple(n), tuple(k)) for n, k in proof['pivot_rows']]
            matrix = [[columns[col].get(row, field()) for col in proof['pivot_columns']] for row in rows]
            determinant = field(1)
            for index in range(len(matrix)):
                pivot = next(row for row in range(index, len(matrix)) if matrix[row][index])
                if pivot != index:
                    matrix[pivot], matrix[index] = matrix[index], matrix[pivot]
                    determinant = determinant*field(-1)
                value = matrix[index][index]
                determinant = determinant*value
                for row in range(index+1, len(matrix)):
                    if not matrix[row][index]:
                        continue
                    coefficient = matrix[row][index]/value
                    for col in range(index, len(matrix)):
                        matrix[row][col] = matrix[row][col]-coefficient*matrix[index][col]
            self.assertTrue(determinant)
            self.assertEqual(determinant.serialize(), proof['minor_determinant_in_Q_zeta'])

    def test_cubic_field_relation_and_inverse_are_exact(self):
        one, zeta = boundary._Eisenstein(1), boundary._Eisenstein(0, 1)
        self.assertFalse(zeta*zeta+zeta+one)
        for a, b in ((2, 3), (-1, 4), (Q(1, 7), Q(-5, 3))):
            element = boundary._Eisenstein(a, b)
            self.assertEqual((element*(one/element)).serialize(), ['1', '0'])


if __name__ == '__main__':
    unittest.main()
