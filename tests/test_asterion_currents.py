import json
import random
import unittest
from fractions import Fraction
from itertools import product

from perfectjet.asterion_currents import (
    AffineE8Currents, CurrentPopulations, ALL_GRADES, a4_theta_coefficients,
    colored_partitions, currents_receipt, encode_current_vector,
    eta_twining_certificate, finite_fourier_projector_certificate,
    encode_quadratic_state,
)
from perfectjet.asterion_jordan import LABELS, ONE, ZETA, ZERO


class CurrentPopulationTests(unittest.TestCase):
    def test_character_and_universal_pbw_coefficients(self):
        p = CurrentPopulations(12)
        self.assertEqual(p.simple[:8], (1, 248, 4124, 34752, 213126, 1057504, 4530744, 17333248))
        self.assertEqual(p.universal[:5], (1, 248, 31124, 2634752, 169205626))
        self.assertEqual(p.simple[10], 603096260)
        self.assertEqual(p.universal[10], 403262150157786676)
        self.assertEqual(colored_partitions(0, 5), (1, 0, 0, 0, 0, 0))

    def test_a4_lattice_enumeration_against_independent_direct_tuples(self):
        direct = [0]*5
        for vector in product(range(-2, 3), repeat=5):
            norm = sum(x*x for x in vector)
            if sum(vector) == 0 and norm <= 8:
                self.assertEqual(norm % 2, 0)
                direct[norm//2] += 1
        self.assertEqual(tuple(direct), a4_theta_coefficients(4))
        self.assertEqual(tuple(direct), (1, 20, 30, 60, 60))

    def test_eta_identity_has_modularity_and_sturm_certificate(self):
        certificate = eta_twining_certificate(20)
        self.assertTrue(certificate["passed"])
        self.assertEqual(certificate["sturm_bound"], 2)
        self.assertEqual(certificate["coefficients_through_sturm_bound"], ["1", "-10", "35"])
        self.assertEqual(certificate["newman_mod24_sums"], [0, 48])
        self.assertEqual(certificate["cusp_orders"], {"infinity": 0, "zero": 2})

    def test_finite_fourier_projectors_are_exact(self):
        certificate = finite_fourier_projector_certificate()
        self.assertTrue(certificate["passed"])
        self.assertEqual(certificate["fourier_gram_matrix_entries_certified"], 15625)
        self.assertEqual(certificate["projector_denominator"], 125)

    def test_all_125_grade_populations_reconstruct_traces_and_dimensions(self):
        p = CurrentPopulations(20)
        self.assertEqual([p.graded_dimension(n, (0, 0, 0)) for n in range(5)], [1, 0, 32, 280, 1706])
        self.assertEqual([p.graded_dimension(n, (1, 0, 0)) for n in range(5)], [0, 2, 33, 278, 1705])
        for kind in ("simple", "universal", "relations"):
            for n in range(21):
                distribution = p.distribution(n, kind)
                self.assertEqual(len(distribution), 125)
                self.assertEqual(sum(distribution.values()), getattr(p, kind)[n])
                for element in ((1, 0, 0), (2, 3, 4), (0, 0, 1)):
                    trace = sum((dimension*ZETA**(sum(x*y for x, y in zip(grade, element)) % 5)
                                 for grade, dimension in distribution.items()), ZERO)
                    expected = (p.relation_twine if kind == "relations"
                                else getattr(p, kind+"_twine"))[n]
                    self.assertEqual(trace, expected)

    def test_first_nonuniform_relation_layer_is_five(self):
        p = CurrentPopulations(15)
        self.assertEqual(p.relation_twine[:5], (0, 0, 0, 0, 0))
        self.assertEqual(p.relation_twine[5], 48)
        self.assertEqual(p.graded_dimension(2, (0, 0, 0), "relations"), 216)
        self.assertEqual(p.graded_dimension(2, (1, 0, 0), "relations"), 216)
        self.assertEqual(p.graded_dimension(3, (0, 0, 0), "relations"), 20800)
        self.assertEqual(p.graded_dimension(3, (1, 0, 0), "relations"), 20800)
        self.assertEqual(p.graded_dimension(5, (0, 0, 0), "relations")
                         -p.graded_dimension(5, (1, 0, 0), "relations"), 48)

    def test_count_receipt_is_exact_and_keeps_neutral_grades_distinct(self):
        receipt = currents_receipt(6, verify_currents=False)
        self.assertTrue(receipt["passed"])
        populations = receipt["populations"]
        self.assertEqual(populations["finite_jordan_neutral_dimension"], 0)
        self.assertEqual(populations["vertex_vacuum_neutral_dimension"], 1)
        self.assertEqual(populations["asymptotic_log_growth"]["sugawara_central_charge"], 8)
        self.assertFalse(receipt["new_density_theorem_claim"])
        json.dumps(receipt)


class AffineCurrentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.algebra = AffineE8Currents()

    def test_metric_is_nonzero_only_on_opposite_grades_and_nondegenerate(self):
        receipt = self.algebra.verify_metric()
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["nonzero_ordered_pairings"], 248)
        self.assertEqual(receipt["basis_pairings_computed"], 30876)
        self.assertEqual(receipt["opposite_grade_blocks"], 62)

    def test_metric_invariance_exhausts_all_possibly_nonzero_triples(self):
        receipt = self.algebra.verify_metric_invariance()
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["triples_checked"], 122016)
        self.assertTrue(receipt["affine_cocycle_jacobi_for_all_integer_modes"])

    def test_metric_invariance_rejects_a_corrupted_central_pairing(self):
        a = self.algebra
        left = LABELS[0]
        right = next(label for label in LABELS if a.metric(left, label))
        key = tuple(sorted((left, right)))
        original = a._metric_cache[key]
        a._metric_cache[key] = -original
        try:
            # The corrupted form remains nondegenerate and grade orthogonal;
            # actual invariance, rather than that weaker property, must fail.
            self.assertTrue(a.verify_metric()["passed"])
            self.assertFalse(a.verify_metric_invariance()["passed"])
        finally:
            a._metric_cache[key] = original

    def test_zero_modes_reproduce_finite_e8(self):
        a = self.algebra
        for left, right in zip(LABELS[::11], LABELS[3::11]):
            expected = {("J", 0, *label): value
                        for label, value in a.jordan.basis_bracket(left, right).items()}
            self.assertEqual(a.bracket(a.basis_current(left), a.basis_current(right)), expected)

    def test_central_term_and_degree_derivation(self):
        a = self.algebra
        left = LABELS[0]
        right = next(label for label in LABELS if a.metric(left, label))
        x, y = a.basis_current(left, 3), a.basis_current(right, -3)
        self.assertEqual(a.bracket(x, y), {"K": 3*a.metric(left, right)})
        self.assertEqual(a.bracket(y, x), {"K": -3*a.metric(left, right)})
        self.assertEqual(a.bracket(x, a.basis_current(right, -2)), {})
        self.assertEqual(a.bracket(a.derivation(), x), {key: 3*value for key, value in x.items()})
        self.assertEqual(a.bracket(x, a.derivation()), {key: -3*value for key, value in x.items()})
        self.assertEqual(a.bracket(a.central(), x), {})
        self.assertEqual(a.jacobi(a.derivation(), x, y), {})

    def test_mode_jacobi_and_skew_symmetry_on_reproducible_panel(self):
        a = self.algebra
        rng = random.Random(9931)
        for _ in range(250):
            labels = rng.sample(LABELS, 3)
            target = tuple(-(labels[0][i]+labels[1][i]) % 5 for i in range(3))
            if target == (0, 0, 0):
                continue
            labels[2] = (*target, rng.randrange(2))
            modes = [rng.randrange(-3, 4) for _ in range(3)]
            # Force many cocycle-sensitive triples to total mode zero.
            modes[2] = -modes[0]-modes[1]
            x, y, z = [a.basis_current(label, mode) for label, mode in zip(labels, modes)]
            self.assertEqual(a.jacobi(x, y, z), {})
            self.assertEqual(a.bracket(x, y), {key: -value for key, value in a.bracket(y, x).items()})

    def test_current_json_encoding_and_invalid_mode(self):
        a = self.algebra
        encoded = encode_current_vector({("J", -2, *LABELS[0]): ZETA/3, "K": ONE})
        self.assertEqual(len(encoded), 2)
        json.dumps(encoded)
        with self.assertRaises(ValueError):
            a.basis_current(LABELS[0], Fraction(1, 2))

    def test_31_cartan_states_give_30_explicit_independent_neutral_nulls(self):
        a = self.algebra
        data = a.cartan_conformal_states()
        states, relations = data["cartan_states"], data["null_relations"]
        self.assertEqual((len(states), len(relations)), (31, 30))
        self.assertTrue(all(len(state) == 4 for state in states))
        self.assertTrue(all(len(relation) == 8 for relation in relations))
        # Each non-reference state has four monomials belonging to none of
        # the other thirty Cartan states: an independent support certificate.
        supports = [set(state) for state in states]
        self.assertEqual(sum(map(len, supports)), len(set.union(*supports)))
        for state in (*states, *relations):
            for left, right in state:
                self.assertEqual(tuple((x+y) % 5 for x, y in zip(left[:3], right[:3])), (0, 0, 0))
        receipt = a.cartan_conformal_receipt(include_coefficients=True)
        self.assertTrue(receipt["passed"], receipt)
        self.assertEqual(receipt["universal_state_rank"], 31)
        self.assertEqual(receipt["explicit_relation_rank"], 30)
        self.assertEqual(receipt["remaining_neutral_quadratic_nullspace_dimension"], 186)
        self.assertFalse(receipt["exhaustive_nullspace_claim"])
        json.dumps(receipt)

    def test_sugawara_mean_denominator_31_cancels_modulo_named_relations(self):
        a = self.algebra
        data = a.cartan_conformal_states()
        mean = data["sugawara_state"]
        states = data["cartan_states"]
        for monomial, coefficient in mean.items():
            self.assertEqual(31*coefficient, sum((state.get(monomial, ZERO) for state in states), ZERO))
        # Actual modulo-31 VOA reduction is a separate task; this check is in
        # characteristic zero and exhibits representatives without that prime.
        state_denominators = {q.denominator for value in states[0].values() for q in value.coefficients}
        mean_denominators = {q.denominator for value in mean.values() for q in value.coefficients}
        self.assertTrue(all(d % 31 != 0 for d in state_denominators))
        self.assertTrue(any(d % 31 == 0 for d in mean_denominators))
        receipt = a.cartan_conformal_receipt()
        self.assertTrue(receipt["denominator_31_eliminated_modulo_these_relations"])
        json.dumps(encode_quadratic_state(states[0]))
        with self.assertRaises(ValueError):
            AffineE8Currents(level=2).cartan_conformal_states()


if __name__ == "__main__":
    unittest.main()
