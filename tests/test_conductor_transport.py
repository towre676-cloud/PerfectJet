import json
import unittest

from perfectjet.conductor_transport import (
    FiniteFourier, ConductorTransport, crt_permutation, crt_factorization,
    FiniteLatticeTheta, type_a_cartan, TorusSkein, half_lift_parity, receipt,
)


class FourierTransportTests(unittest.TestCase):
    def test_fourier_squared_is_reflection(self):
        for n in range(1,8):
            space=FiniteFourier(n)
            vector=[j+1 for j in range(n)]
            twice=space.fourier(space.fourier(vector))
            self.assertEqual(twice,[n*space.ring.element([vector[-j % n]]) for j in range(n)])

    def test_transport_identities_on_all_basis_vectors(self):
        for l,m in ((1,3),(2,4),(2,6),(3,6),(3,9),(4,8)):
            row=ConductorTransport(l,m).replay()
            self.assertTrue(row['fourier_support_to_pullback'])
            self.assertTrue(row['fourier_pullback_to_support'])
            self.assertTrue(row['chirp_transport'])

    def test_maps_support_actual_cyclotomic_inputs(self):
        transport=ConductorTransport(3,6)
        z=transport.lower.zeta
        self.assertEqual(transport.lift(z),transport.upper.zeta**2)
        vector=[1,z,z*z]
        lhs=transport.upper.fourier(transport.embed_support(vector))
        self.assertEqual(lhs,transport.pullback(transport.lower.fourier(vector)))

    def test_crt_needs_twists_and_coprime_factors(self):
        row=crt_factorization(3,4)
        self.assertTrue(row['fourier_factorization'])
        self.assertTrue(row['chirp_factorization'])
        self.assertEqual(len(set(crt_permutation(3,4))),12)
        # Dropping the twists fails already on one (a,b)=(0,1) diagonal entry.
        space=FiniteFourier(12)
        self.assertNotEqual(space.zeta**9,space.zeta**3)
        for factors in ((2,4),(3,6)):
            with self.assertRaises(ValueError):
                crt_factorization(*factors)

    def test_bad_dimensions_and_resource_limits(self):
        with self.assertRaises(ValueError):
            ConductorTransport(4,6)
        with self.assertRaises(ValueError):
            FiniteFourier(3).fourier([1,2])
        with self.assertRaises(ValueError):
            ConductorTransport(3,6).replay(max_entries=1)


class ThetaTests(unittest.TestCase):
    def test_numerator_formula_against_weak_composition_sum(self):
        for rank in (1,2,3):
            for conductor in (2,3,4):
                theta=FiniteLatticeTheta(type_a_cartan(rank),conductor)
                self.assertTrue(theta.reciprocity())
                for n in range(18):
                    self.assertEqual(theta.coefficient(n),theta.direct_coefficient(n))

    def test_boundary_twist_cannot_be_omitted(self):
        theta=FiniteLatticeTheta(type_a_cartan(2),3)
        phase=theta.space.zeta**theta.quadratic([2,2])
        self.assertTrue(any(theta.numerator[theta.degree-k]!=phase*theta.numerator[k]
                            for k in range(theta.degree+1)))
        self.assertTrue(theta.reciprocity())

    def test_remote_index_and_degenerate_even_lattice(self):
        # Zero form in rank two counts every weak composition: coefficient n+1.
        theta=FiniteLatticeTheta([[0,0],[0,0]],3)
        self.assertEqual(theta.coefficient(10**100),10**100+1)
        self.assertEqual(theta.coefficient(-1),0)
        self.assertTrue(theta.reciprocity())

    def test_invalid_quadratic_lattices_and_budgets(self):
        for matrix in ([[1]],[[2,1],[0,2]],[[2,0,1],[0,2,0]]):
            with self.assertRaises(ValueError):
                FiniteLatticeTheta(matrix,3)
        with self.assertRaises(ValueError):
            FiniteLatticeTheta(type_a_cartan(4),5,max_terms=10)
        with self.assertRaises(ValueError):
            FiniteLatticeTheta(type_a_cartan(3),2).direct_coefficient(100,max_terms=10)


class SkeinParityTests(unittest.TestCase):
    def test_skein_associativity_and_curve_sign(self):
        skein=TorusSkein(5)
        a,b,c={(2,-1):1},{(1,1):1},{(0,2):1}
        self.assertEqual(skein.multiply(skein.multiply(a,b),c),
                         skein.multiply(a,skein.multiply(b,c)))
        self.assertEqual(skein.basis_product((2,-1),(1,1)),
                         skein.basis_product((-2,1),(1,1)))

    def test_conductor_centrality_and_noncentral_negative_case(self):
        for conductor in (2,3,5):
            skein=TorusSkein(conductor)
            self.assertFalse(skein.commutator((conductor,0),(0,1)))
            self.assertTrue(skein.central_basis_curve((conductor,2*conductor)))
            self.assertTrue(skein.commutator((1,0),(0,1)))
            self.assertFalse(skein.central_basis_curve((1,0)))
            # A central multiple remains a different basis element from e_(0,0).
            self.assertNotEqual(skein.basis_product((conductor,0),(0,0)),
                                skein.basis_product((0,0),(0,0)))

    def test_half_lift_sign_proxy_is_strictly_scoped(self):
        self.assertTrue(half_lift_parity([2,2],6)['half_lift_blind'])
        self.assertFalse(half_lift_parity([3,4,3],6)['half_lift_blind'])
        with self.assertRaises(ValueError):
            half_lift_parity([2,2],5)

    def test_receipt_json_shape(self):
        self.assertTrue(json.loads(json.dumps(receipt()))['theta']['reciprocity'])


if __name__=='__main__':
    unittest.main()
