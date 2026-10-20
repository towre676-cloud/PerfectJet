import unittest
from copy import deepcopy
from fractions import Fraction as Q

from perfectjet.asterion_monodromy_algebra import KZResidueAlgebra, cyclotomic_form_obstruction


class MonodromyResidueAlgebraTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.algebra = KZResidueAlgebra()

    def test_exact_associative_and_lie_word_certificates(self):
        for kind, centered, dimension, depth in (("associative", False, 25, 5),
                                                ("lie", False, 25, 7),
                                                ("lie", True, 24, 7)):
            certificate = self.algebra.word_certificate(kind, centered=centered)
            self.assertEqual(certificate["dimension"], dimension)
            self.assertEqual(certificate["maximum_word_length"], depth)
            self.assertTrue(self.algebra.replay_word_certificate(certificate)["passed"])
            if centered:
                self.assertTrue(certificate["all_basis_traces_zero"])
            damaged = deepcopy(certificate)
            damaged["basis_matrices"][0][0][0] = "123"
            with self.assertRaises(ArithmeticError):
                self.algebra.replay_word_certificate(damaged)

    def test_exact_spectral_projection_and_all_matrix_units(self):
        record = self.algebra.spectral_matrix_unit_certificate()
        self.assertEqual(record["edge_count"], 10)
        self.assertEqual(record["adjoint_projection_degree"], 10)
        self.assertTrue(record["all_twenty_offdiagonal_units_replayed"])
        self.assertEqual(len(record["all_offdiagonal_matrix_unit_paths"]), 20)
        self.assertEqual(record["trace_A"], "-100")

    def test_selfadjoint_forms_are_distinguished_from_invariant_forms(self):
        record = self.algebra.form_certificate()
        self.assertEqual(record["common_commutant_dimension"], 1)
        self.assertEqual(record["residue_selfadjoint_form_dimension"], 1)
        self.assertTrue(record["residue_selfadjoint_gram_positive_definite"])
        self.assertTrue(record["crossing_is_orthogonal_for_this_gram"])
        self.assertEqual(record["infinitesimally_invariant_bilinear_form_dimension"], 0)
        self.assertEqual(record["centered_infinitesimally_invariant_bilinear_form_dimension"], 0)
        self.assertFalse(record["monodromy_invariant_hermitian_form_computed"])

    def test_rational_spectrum_and_all_similitude_factors(self):
        record = self.algebra.specialization_spectrum(Q(1, 34))
        self.assertEqual(record["spectrum_root_order"], 17)
        self.assertEqual(record["spectrum_exponents"], [4, 2, 11, 0, 1])
        self.assertEqual(record["local_monodromy_order_from_nonresonant_semisimple_form"], 17)
        self.assertEqual(record["determinant_image_exact_order"], 17)
        form = record["bilinear_similitude_obstruction"]
        self.assertEqual(len(form["rank_bounds"]), 17)
        self.assertEqual(form["maximum_rank_over_all_factors"], 3)
        self.assertFalse(form["nondegenerate_projective_bilinear_form_possible"])
        self.assertFalse(record["specialized_full_closure_proved_here"])
        # A familiar selfdual odd spectrum must be accepted: the obstruction
        # routine is not hardcoded to reject every cyclotomic representation.
        other = cyclotomic_form_obstruction(17, (-2, -1, 0, 1, 2))
        self.assertTrue(other["nondegenerate_projective_bilinear_form_possible"])

    def test_resonances_do_not_imply_local_finite_order(self):
        record = self.algebra.specialization_spectrum(Q(1, 32))
        self.assertTrue(record["nonzero_integer_residue_difference_resonances"])
        self.assertIsNone(record["local_monodromy_order_from_nonresonant_semisimple_form"])
        self.assertTrue(record["GL5_closure_excluded_by_finite_determinant"])
        theorem = self.algebra.generic_monodromy_theorem()
        self.assertEqual(theorem["actual_constant_term_Lie_word_rank"], 25)
        self.assertTrue(theorem["rational_parameter_excluded_from_this_argument"])
        self.assertFalse(theorem["analytic_epsilon_numerically_certified"])


if __name__ == "__main__":
    unittest.main()
