import unittest
from fractions import Fraction as Q

from perfectjet.asterion_boundary import PrincipalReesFamily, CotangentLieAlgebra, quadratic_completion_bound
from perfectjet.asterion_principal import EXPONENTS


class PrincipalBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.family = PrincipalReesFamily()

    def test_actual_16_leading_channels_and_154_higher_channels(self):
        support = self.family.leading_support()
        self.assertEqual(len(support), 16)
        self.assertEqual(len(self.family.couplings) - len(support), 154)
        for row in support:
            self.assertEqual(row["transvectant_order"], 1)
            self.assertIn(Q(row["coefficient"]), (Q(1, 2), Q(-1, 2)))

    def test_polynomial_bracket_evaluation_and_exact_scaling(self):
        f = self.family
        x = {f.label_index[7, 3]: Q(2, 3), f.label_index[29, 20]: Q(7), 0: Q(-1)}
        y = {f.label_index[11, 18]: Q(-3), f.label_index[19, 13]: Q(9, 2)}
        polynomial = f.polynomial_bracket(x, y)
        self.assertTrue(all(power >= 0 and power % 2 == 0 for p in polynomial.values() for power in p))
        for t in (Q(0), Q(1, 2), Q(2), Q(-1)):
            expected = {i: sum(value * t ** power for power, value in p.items()) for i, p in polynomial.items()}
            expected = {i: value for i, value in expected.items() if value}
            self.assertEqual(f.bracket(x, y, t), expected)
            if t:
                self.assertTrue(f.verify_scaling(x, y, t)["valid"])
                self.assertEqual(f.scale(f.scale(x, t), t, inverse=True), x)
        with self.assertRaises(ValueError):
            f.verify_scaling(x, y, 0)
        with self.assertRaises(ValueError):
            f.scale(x, 0, inverse=True)

    def test_exact_boundary_structure_and_nilpotency_witness(self):
        r = self.family.structure_receipt()
        self.assertEqual([x["dimension"] for x in r["nilradical_lower_central"]], [245, 207, 145, 59, 0])
        self.assertEqual([x["dimension"] for x in r["nilradical_derived"]], [245, 207, 59, 0])
        self.assertEqual(r["nilpotency_class"], 4)
        self.assertEqual(r["nilradical_center_spins"], [29])
        self.assertEqual(r["nilradical_abelianization_dimension"], 38)
        self.assertTrue(r["full_algebra_perfect"])
        self.assertEqual(len(r["module_image_witnesses"]), 8)
        self.assertEqual(len(r["four_factor_witness"]["successive_images"]), 3)

    def test_contraction_cone_and_complete_small_cuts(self):
        f = self.family
        receipt = f.cone_receipt()
        self.assertEqual(receipt["dimension"], 7)
        self.assertTrue(receipt["pointed"])
        self.assertEqual(receipt["binary_admissible_weights"], [[0] * 7, [1] * 7])
        self.assertEqual(receipt["ternary_admissible_count"], 129)
        weights = {m: m - 1 for m in EXPONENTS}
        self.assertTrue(f.valuation_receipt(weights)["admissible"])
        weights[7] = 0
        self.assertFalse(f.valuation_receipt(weights)["admissible"])
        with self.assertRaises(ValueError):
            f.bracket({0: 1}, {1: 1}, weights=weights)

    def test_invariant_form_obstruction(self):
        r = self.family.invariant_form_receipt()
        self.assertFalse(r["nondegenerate_invariant_symmetric_form_exists"])
        self.assertEqual(r["all_invariant_symmetric_forms_dimension"], 1)
        self.assertEqual(r["all_invariant_symmetric_forms_maximum_rank"], 3)
        self.assertEqual(r["limiting_killing_radical_dimension"], 245)
        bounds = quadratic_completion_bound(248, 3)
        self.assertEqual(bounds["unrestricted_quadratic_completion_lower_bound"], 493)
        self.assertEqual(bounds["canonical_cotangent_upper_bound"], 496)
        self.assertEqual(bounds["isotropic_embedding_lower_bound"], 496)
        self.assertFalse(bounds["unrestricted_minimum_attained_known"])


def sl2(left, right):
    table = {(0, 1): {1: Q(2)}, (0, 2): {2: Q(-2)}, (1, 2): {0: Q(1)}}
    out = {}
    for i, x in left.items():
        for j, y in right.items():
            if i == j:
                continue
            sign = 1 if i < j else -1
            for k, z in table[min(i, j), max(i, j)].items():
                out[k] = out.get(k, Q(0)) + sign * x * y * z
                if not out[k]:
                    del out[k]
    return out


class CotangentTests(unittest.TestCase):
    def test_complete_small_quadratic_model(self):
        g = CotangentLieAlgebra(3, sl2)
        units = [{i: Q(1)} for i in range(6)]
        self.assertTrue(g.verify_quadratic()["passed"])
        for i, x in enumerate(units):
            for j, y in enumerate(units):
                self.assertEqual(g.pairing(x, y), int(abs(i - j) == 3))
                for z in units:
                    self.assertEqual(g.pairing(g.bracket(x, y), z), g.pairing(x, g.bracket(y, z)))
                    jacobi = {}
                    for a, b, c in ((x, y, z), (y, z, x), (z, x, y)):
                        for k, v in g.bracket(a, g.bracket(b, c)).items():
                            jacobi[k] = jacobi.get(k, Q(0)) + v
                    self.assertTrue(all(v == 0 for v in jacobi.values()))

    def test_actual_boundary_double_sparse_invariance(self):
        f = PrincipalReesFamily()
        g = CotangentLieAlgebra(248, f.bracket)
        x = g.embed({f.label_index[7, 0]: 1})
        y = g.embed({f.label_index[11, 1]: 1})
        z = g.dual({f.label_index[17, 0]: 1})
        self.assertEqual(g.pairing(g.bracket(x, y), z), g.pairing(x, g.bracket(y, z)))
        self.assertNotEqual(g.pairing(g.bracket(x, y), z), 0)
        self.assertEqual(g.bracket(g.dual({0: 1}), g.dual({13: 1})), {})
        self.assertEqual(g.dimension, 496)


if __name__ == "__main__":
    unittest.main()
