"""The exact invariant quartic arc class and its scoped kernel consequence."""
from fractions import Fraction as Q
import json
import unittest

from perfectjet.asterion_e8 import E8LieAlgebra
from perfectjet.asterion_quartic import (
    invariant_pairing, pair_slot_certificate, quartic_operator,
    quartic_receipt, quartic_value,
)
from perfectjet.asterion_relations import AffinePBW, _casimir_quadratic


class QuarticBoundaryTests(unittest.TestCase):
    def test_actual_three_operator_eigenvectors_and_nonzero_norm(self):
        module = AffinePBW()
        c = _casimir_quadratic(module)
        q = module.highest_quadratic_3875()
        theta = module.algebra.root_index[module.algebra.roots[-1]]
        for polynomial, eigenvalue in ((c, -434), (q, 14), ({(theta, theta): Q(1)}, 0)):
            self.assertEqual(quartic_operator(polynomial, module),
                             {key: z*eigenvalue for key, z in polynomial.items() if z*eigenvalue})
        self.assertEqual(434**2+3875*14**2, 947856)

    def test_intrinsic_formula_diagonal_symmetry_and_an_actual_nonzero_value(self):
        g = E8LieAlgebra()
        x, y = {0: Q(1)}, {2: Q(1)}
        self.assertEqual(quartic_value(x, y, g), -8)
        self.assertEqual(invariant_pairing(x, y, g), 0)
        root = g.simple_roots[0]
        positive = g.root_index[root]
        negative = g.root_index[tuple(-z for z in root)]
        x = {0: Q(2, 3), positive: Q(1), negative: Q(3)}
        y = {2: Q(5), positive: Q(-2), negative: Q(1, 7)}
        self.assertEqual(quartic_value(x, x, g), 0)
        self.assertEqual(quartic_value(x, y, g), quartic_value(y, x, g))
        self.assertEqual(quartic_value({i: 3*z for i,z in x.items()}, y, g),
                         9*quartic_value(x, y, g))

    def test_pair_slot_duality_and_scoped_json_receipt(self):
        self.assertTrue(pair_slot_certificate()['passed'])
        r = quartic_receipt(exhaustive=True)
        self.assertTrue(r['passed'])
        self.assertTrue(all(r['checks'].values()))
        self.assertEqual(r['tensor_norm_squared'], 947856)
        self.assertEqual(r['exact_quartic_arc_invariant_dimension'], 1)
        self.assertEqual(r['arc_dimension_lower_bound_increment'], 1)
        self.assertEqual(r['quartic_arc_dimension_lower_bound'], 3876)
        self.assertTrue(r['explicit_invariant_already_included_in_character_bound'])
        self.assertTrue(r['quartic_characters']['passed'])
        self.assertEqual(r['multiplication_27000_certificate']['nonzero_polarization_coefficient'], '8/49')
        self.assertTrue(r['Casimir_cutoff_certificate']['passed'])
        self.assertEqual(r['Casimir_kernel_upper_bound'], 168)
        self.assertEqual(r['remaining_unresolved_extra_kernel_modules'], [])
        self.assertTrue(r['multiplication_147250_certificate']['passed'])
        self.assertEqual(r['multiplication_147250_certificate']['primitive_term_counts'][0],49)
        self.assertEqual(r['multiplication_147250_certificate']['primitive_term_counts'][-1],1421)
        self.assertTrue(all(r['multiplication_147250_certificate']['all_eight_raising_checks']))
        self.assertTrue(r['exact_full_quartic_kernel_claim'])
        self.assertEqual(r['exact_quartic_arc_dimension'],3876)
        self.assertFalse(r['complete_weight6_arc_kernel_claim'])
        self.assertEqual(r['whole_weight6_invariant_counts'],
                         {'short_at_most_two_currents':3, 'three_current_arc_Cartan_3_form':1,
                          'quartic_arc_invariant':1, 'simple_VOA':4, 'kernel_lower_bound':1})
        self.assertFalse(r['voa_image_of_explicit_quartic_class_computed'])
        self.assertFalse(r['affine_null_lift_of_F0_computed'])
        json.dumps(r, allow_nan=False)

    def test_exact_input_boundaries(self):
        for bad in ({True:1}, {248:1}, {0:0.5}, {0:True}, []):
            with self.assertRaises(ValueError):
                quartic_value(bad, {0:1})
        for bad in ({(0,):1}, {(0,248):1}, {(0,1):0.5}, []):
            with self.assertRaises(ValueError):
                quartic_operator(bad)
        with self.assertRaises(ValueError):
            quartic_receipt(exhaustive='yes')


if __name__ == '__main__':
    unittest.main()
