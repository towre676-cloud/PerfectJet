"""Independent exact checks of noncommutative DELL boundary compilation."""
import unittest
from fractions import Fraction as Q

from perfectjet.dell_quantum import QuantumDellBoundary, quantum_boundary_receipt


class QuantumDellBoundaryTests(unittest.TestCase):
    def test_current_shells_and_first_inverse_correction(self):
        a = QuantumDellBoundary(order=1)
        self.assertEqual(a.current(0,0), {a.zero:Q(1)})
        self.assertEqual(len(a.current(0,1)),6)
        self.assertEqual(len(a.current(1,0)),3)
        # Check C_0 H_1=C_1 through first order at every output shift.
        out = dict(a.normalized(1,1))
        for n,c in a.current(0,1).items():
            for m,d in a.normalized(1,0,n).items():
                key = tuple(i+j for i,j in zip(n,m))
                out[key] = out.get(key,0)+c*d
        self.assertEqual({n:c for n,c in out.items() if c},a.current(1,1))

    def test_all_order_two_commutator_coefficients_at_independent_points(self):
        result = quantum_boundary_receipt()
        self.assertTrue(result["passed"])
        for row in result["certificates"]:
            self.assertEqual(row["normalized_commutator_nonzero_coefficients_by_degree"],[0,0,0])
            self.assertGreater(row["numerator_commutator_nonzero_coefficients_by_degree"][1],0)
            self.assertIsNotNone(row["frozen_product_difference_witness"])
            self.assertTrue(row["all_output_shift_coefficients_checked"])
        self.assertFalse(result["all_order_commutativity_proved"])
        self.assertTrue(result["coordinate_elliptic_dependence_checked"])

    def test_coordinate_nome_first_coefficient_against_log_derivative(self):
        a=QuantumDellBoundary(coordinate_order=2)
        shift=(2,-1,0);offset=(1,0,-1)
        series=a.coefficient(shift,offset).coefficients
        point=tuple(x*a.quantum**d for x,d in zip(a.positions,offset))
        correction=Q(0)
        for i in range(3):
            for j in range(i+1,3):
                ratio=point[i]/point[j]
                argument=a.coupling**(shift[i]-shift[j])*ratio
                correction+=ratio+1/ratio-argument-1/argument
        b=QuantumDellBoundary()
        self.assertEqual(series[0],b.coefficient(shift,offset))
        self.assertEqual(series[1],series[0]*correction)
        theta=a.theta(Q(2)).coefficients
        self.assertEqual(theta,(Q(-1),Q(5,2),Q(3,2)))

    def test_genuine_two_nome_order_three_commutator(self):
        a=QuantumDellBoundary(order=3,coordinate_order=2)
        self.assertTrue(all(not values for values in a.commutator().values()))

    def test_four_particle_all_three_hamiltonian_pairs(self):
        a=QuantumDellBoundary((2,5,11,17),3,7,2,1)
        for i in range(1,4):
            for j in range(i+1,4):
                self.assertTrue(all(not values for values in a.commutator(i,j).values()))

    def test_shift_action_is_not_a_scalar_product(self):
        a = QuantumDellBoundary(order=0)
        self.assertNotEqual(a.coefficient((1,0,0),(0,1,0)),
                            a.coefficient((1,0,0),(0,0,0)))
        self.assertNotEqual(a.multiply(1,2),a.multiply(1,2,frozen=True))

    def test_free_coupling_is_translation_invariant(self):
        a = QuantumDellBoundary(coupling=1,order=2)
        self.assertTrue(all(not row for row in a.commutator().values()))
        self.assertEqual(a.multiply(1,2),a.multiply(1,2,frozen=True))

    def test_charge_energy_support_is_exact(self):
        a = QuantumDellBoundary(order=3)
        for (charge,degree),shifts in a.shells.items():
            for n in shifts:
                self.assertEqual(sum(n),charge)
                self.assertEqual(sum(k*(k-1)//2 for k in n),degree)
        for d in range(4):
            self.assertTrue(all(sum(n)==1 for n in a.normalized(1,d)))

    def test_invalid_inputs_and_poles(self):
        for kw in ({"quantum":0},{"coupling":0},{"order":True},{"order":5},
                   {"positions":(2.0,3,5)},{"positions":(0,3,5)},
                   {"coordinate_order":4}):
            with self.assertRaises(ValueError):
                QuantumDellBoundary(**kw)
        a=QuantumDellBoundary(positions=(1,7,11),quantum=7)
        with self.assertRaises(ValueError):
            a.coefficient((1,0,0),(1,0,0))
        with self.assertRaises(ValueError):
            QuantumDellBoundary(positions=(2,5)).receipt()


if __name__ == "__main__":
    unittest.main()
