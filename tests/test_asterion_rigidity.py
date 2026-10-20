import unittest
from copy import deepcopy
from fractions import Fraction as Q

from perfectjet.asterion_rigidity import PrincipalRigidity


class PrincipalRigidityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rigidity = PrincipalRigidity()

    def test_actual_gauge_ranks_and_independent_tangent_constraints(self):
        for fixed, variables, gauges, constraints in ((False, 170, 8, 162), (True, 162, 7, 155)):
            record = self.rigidity.verify(fixed=fixed)
            self.assertEqual(record["cochain_variables"], variables)
            self.assertEqual(record["actual_gauge_matrix_rank"], gauges)
            self.assertEqual(record["equivalent_tangent_constraint_rank"], constraints)
            self.assertNotEqual(Q(record["minor_determinant"]), 0)
            self.assertFalse(record["jacobi_jacobian_assembled"])

    def test_unique_gauge_recovery_and_a_failing_functional(self):
        for fixed, scalars in ((False, (Q(1, 3), -2, 3, 0, Q(2, 5), -7, 11, 13)),
                               (True, (-2, 3, 0, Q(2, 5), -7, 11, 13))):
            delta = self.rigidity.infinitesimal_gauge(scalars, fixed=fixed)
            record = self.rigidity.tangent_membership(delta, fixed=fixed)
            self.assertTrue(record["is_cocycle_in_declared_theorem_scope"])
            self.assertEqual(tuple(map(Q, record["recovered_gauge_scalars"])), tuple(map(Q, scalars)))
            delta[7, 7, 7] = delta.get((7, 7, 7), 0) + 1
            failure = self.rigidity.tangent_membership(delta, fixed=fixed)
            self.assertFalse(failure["is_cocycle_in_declared_theorem_scope"])
            self.assertNotEqual(Q(failure["first_constraint_witness"]["value"]), 0)

    def test_finite_diagonal_transport_and_actual_coboundary(self):
        r = self.rigidity
        scales = (Q(2), Q(3), Q(5), Q(7), Q(11), Q(13), Q(17), Q(19))
        changed = r.finite_diagonal_gauge(scales)
        self.assertTrue(r.finite_orbit_membership(changed)["in_declared_gauge_orbit"])
        self.assertFalse(r.finite_orbit_membership(changed, fixed=True)["in_declared_gauge_orbit"])
        spin_scales = dict(zip(r.principal.algebra.exponents, scales))
        scale = lambda vector: {i: x * spin_scales[r.principal.basis_labels[i][0]] for i, x in vector.items()}
        x = {r.principal.label_index[7, 4]: Q(2), r.principal.label_index[19, 21]: Q(-1)}
        y = {r.principal.label_index[11, 15]: Q(3), r.principal.label_index[29, 13]: Q(1, 2)}
        lhs = scale(r.coupling_bracket(changed, x, y))
        rhs = r.principal.bracket(scale(x), scale(y))
        self.assertEqual(lhs, rhs)
        delta = r.infinitesimal_gauge(scales)
        direct = r.principal.bracket(scale(x), y)
        for i, value in r.principal.bracket(x, scale(y)).items():
            direct[i] = direct.get(i, 0) + value
        for i, value in scale(r.principal.bracket(x, y)).items():
            direct[i] = direct.get(i, 0) - value
        direct = {i: value for i, value in direct.items() if value}
        self.assertEqual(r.coupling_bracket(delta, x, y), direct)

    def test_actual_linearized_jacobi_vanishes_for_gauge(self):
        r = self.rigidity
        delta = r.infinitesimal_gauge((1, 2, 3, 4, 5, 6, 7, 8))
        vectors = [{r.principal.label_index[7, 3]: Q(2), r.principal.label_index[17, 7]: Q(-1)},
                   {r.principal.label_index[11, 12]: Q(3)},
                   {r.principal.label_index[29, 31]: Q(1, 5)}]
        self.assertEqual(r.jacobi_derivative(delta, *vectors), {})
        witness = r.nongauge_witness()
        self.assertTrue(witness["actual_linearized_jacobi_residual"])
        self.assertFalse(witness["tangent_membership"]["is_cocycle_in_declared_theorem_scope"])

    def test_actual_jacobian_panel_and_strict_rank_replay(self):
        certificate = self.rigidity.jacobian_rank_certificate(max_panels=1)
        self.assertEqual(certificate["actual_selected_jacobian_rank"], 2)
        self.assertFalse(certificate["target_rank_reached"])
        self.assertIsNone(certificate["full_jacobian_rank_certified"])
        self.assertTrue(self.rigidity.replay_jacobian_certificate(certificate)["passed"])
        altered = deepcopy(certificate)
        altered["selected_rows"][0]["intermediate_spin"] = "999"
        with self.assertRaises(ArithmeticError):
            self.rigidity.replay_jacobian_certificate(altered)

    def test_hypotheses_and_proof_scope_are_explicit(self):
        theorem = self.rigidity.theorem_certificate()
        self.assertEqual(theorem["centralizer_of_principal_sl2_dimension"], 0)
        self.assertEqual(theorem["invariant_derivation_dimension"], 0)
        self.assertEqual(len(theorem["external_theorems"]), 3)
        local = self.rigidity.local_classification_receipt()
        self.assertTrue(local["full_jacobi_scheme_smooth_at_e8"])
        self.assertEqual(local["diagonal_gauge_stabilizer"], "trivial")
        with self.assertRaises(ValueError):
            self.rigidity.tangent_membership({(1, 7, 7): 1}, fixed=True)
        with self.assertRaises(ValueError):
            self.rigidity.finite_diagonal_gauge((1,) * 7 + (0,))


if __name__ == "__main__":
    unittest.main()
