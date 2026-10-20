from fractions import Fraction as Q
import unittest

from perfectjet.asterion_kernel_characters import (
    TRIPLE_NUMERATOR, ambient_length_three_dimension,
    arc_bidegree_dimensions, character_dimension, covariance_rank_certificate,
    diagonal_image_ranks, kernel_characters_receipt, length_three_character,
    length_three_hilbert_coefficient, length_two_character, partitions_123,
    s3_polynomial_multiplicities, weight_five_arc_character,
)


class KernelCharacterTests(unittest.TestCase):
    def test_s3_molien_multiplicities_independent_of_free_module_formula(self):
        for degree in range(31):
            trivial, standard, sign = s3_polynomial_multiplicities(degree)
            self.assertEqual(trivial, partitions_123(degree))
            self.assertEqual(standard, partitions_123(degree-1)+partitions_123(degree-2))
            self.assertEqual(sign, partitions_123(degree-3))
            self.assertEqual(trivial+2*standard+sign, (degree+1)*(degree+2)//2)

    def test_actual_pair_diagonal_covariants_have_all_claimed_ranks(self):
        receipt = covariance_rank_certificate(24)
        self.assertTrue(receipt['passed'])
        self.assertFalse(receipt['finite_panel_is_all_order_proof'])
        for row in receipt['rows']:
            degree = row['jet_degree']
            self.assertEqual(row['ranks'], diagonal_image_ranks(degree))

    def test_cycle_index_ambient_matches_enumerated_jet_partitions(self):
        n = 248
        for degree in range(12):
            total = 0
            for a in range(degree+1):
                for b in range(a,degree+1):
                    c = degree-a-b
                    if c < b:
                        continue
                    if a == c:
                        total += n*(n+1)*(n+2)//6
                    elif a == b or b == c:
                        total += n*n*(n+1)//2
                    else:
                        total += n**3
            self.assertEqual(ambient_length_three_dimension(degree), total)

    def test_all_order_rational_hilbert_coefficients_match_restriction_formula(self):
        expected_prefix = [0,151373,1112621,4585365]
        self.assertEqual([length_three_hilbert_coefficient(d) for d in range(4)], expected_prefix)
        for d in range(40):
            numerator_expansion = sum(z*partitions_123(d-i) for i,z in enumerate(TRIPLE_NUMERATOR))
            self.assertEqual(numerator_expansion,length_three_hilbert_coefficient(d))
            self.assertGreaterEqual(numerator_expansion,0)

    def test_complete_weight_five_character_and_li_bidegrees(self):
        expected = {1:2,248:6,3875:4,27000:1,30380:3,147250:2,779247:1}
        self.assertEqual(weight_five_arc_character(),expected)
        self.assertEqual(character_dimension(expected),1208877)
        self.assertEqual(arc_bidegree_dimensions(5),{0:0,1:0,2:1112621,3:96008,4:248})
        self.assertEqual(length_three_character(1),{248:1,3875:1,147250:1})
        self.assertEqual(length_three_character(2),{248:3,3875:2,30380:1,147250:2,779247:1})

    def test_weight_six_open_piece_is_explicit(self):
        dimensions = arc_bidegree_dimensions(6)
        self.assertIsNone(dimensions[2])
        self.assertEqual(dimensions[3],4585365)
        self.assertEqual(sum(x for x in dimensions.values() if x is not None),4712497)
        self.assertEqual(length_three_character(3),
                         {1:1,248:5,3875:4,27000:1,30380:3,147250:3,779247:2,2450240:1})
        for degree in range(12):
            self.assertEqual(character_dimension(length_three_character(degree)),
                             length_three_hilbert_coefficient(degree))
            self.assertTrue(all(x >= 0 for x in length_three_character(degree).values()))

    def test_two_factor_sectors_remove_one_copy_of_I_at_every_degree(self):
        self.assertEqual(length_two_character(0),{1:1,3875:1})
        self.assertEqual(character_dimension(length_two_character(3)),96008)
        self.assertEqual(character_dimension(length_two_character(4)),126884)

    def test_recomputed_lie_projection_and_acceptance_scope(self):
        receipt = kernel_characters_receipt()
        self.assertTrue(receipt['passed'])
        self.assertEqual(receipt['arc_character_prefix'],[1,248,4124,34752,217001,1208877])
        self.assertEqual(receipt['weight_five_kernel_dimension'],151373)
        self.assertEqual(receipt['weight_five_new_primitive_dimension_lower_bound'],147498)
        self.assertEqual(receipt['weight_six_kernel_dimension_lower_bound'],181753)
        dependency = receipt['polarization_dependency']
        self.assertEqual(dependency['actual_mu_P_I_delta_scalars'],
                         {'248':'54/31','30380':'3/7','779247':'13/7','1763125':'3'})
        self.assertTrue(all(dependency['checks'].values()))
        self.assertFalse(receipt['full_weight_six_arc_dimension_claim'])
        self.assertFalse(receipt['complete_infinite_kernel_claim'])
        self.assertFalse(receipt['first_kernel_differential_generation_claim'])

    def test_invalid_degrees_cannot_be_accepted_as_verified_results(self):
        for bad in (True,-1,Q(1,2),1.0):
            with self.assertRaises(ValueError):
                length_three_hilbert_coefficient(bad)
        with self.assertRaises(ValueError):
            kernel_characters_receipt(max_weight=7)
        with self.assertRaises(TypeError):
            kernel_characters_receipt(exhaustive=1)


if __name__ == '__main__':
    unittest.main()
