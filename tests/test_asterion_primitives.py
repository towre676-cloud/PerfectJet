"""Explicit weight-five/six E8 arc-kernel generators and their certificates."""
from fractions import Fraction as Q
import copy
import unittest

from perfectjet.asterion_primitives import (
    derived_sector_record, closed_form_certificate, length_four_3875_decision, LAMBDA_3875, OMEGA_147250, PRIME, THETA, JetAlgebra, LatticeE8VOA,
    QuarticFunctional, _rational, _sector_record, _weight_four_replay, decode_polynomial,
    digest, encode_polynomial, full_weight_nonmembership, jet_shapes, length_three_sector,
    load_certificates, modular_kernel, quartic_singlet_decision, rational_kernel,
    verify_primitive_certificate,
)
from perfectjet.asterion_kernel_characters import length_three_character


class SharedAlgebra:
    jets = None
    lattice = None

    @classmethod
    def get(cls):
        if cls.jets is None:
            cls.jets = JetAlgebra()
            cls.lattice = LatticeE8VOA(cls.jets)
        return cls.jets, cls.lattice


class ExactLinearAlgebraTests(unittest.TestCase):
    def test_rational_reconstruction_and_verified_kernel(self):
        for value in (Q(3, 7), Q(-22, 5), Q(0), Q(91, 1)):
            residue = value.numerator*pow(value.denominator, -1, PRIME) % PRIME
            self.assertEqual(_rational(residue), value)
        rows = [{0: 1, 1: 2, 2: 3}, {0: 2, 1: 4, 2: 7}]
        rank, basis = modular_kernel(rows, 3)
        self.assertEqual(rank, 2)
        kernel = rational_kernel(rows, 3)
        self.assertEqual(kernel, [{0: Q(-2), 1: Q(1)}])

    def test_shapes_and_polynomial_codec(self):
        self.assertEqual(jet_shapes(3, 2), [(0, 0, 2), (0, 1, 1)])
        self.assertEqual(jet_shapes(3, 3), [(0, 0, 3), (0, 1, 2), (1, 1, 1)])
        polynomial = {((5, 0), (7, 2)): Q(-3, 2), ((1, 1), (1, 1)): Q(4)}
        self.assertEqual(decode_polynomial(encode_polynomial(polynomial)), polynomial)


class LatticeRealizationTests(unittest.TestCase):
    def test_every_bracket_and_form_through_vertex_operators(self):
        _, lattice = SharedAlgebra.get()
        certificate = lattice.bracket_certificate()
        self.assertTrue(certificate["passed"])
        self.assertEqual(certificate["ordered_pairs"], 61504)

    def test_retained_weight_four_lift_is_null_in_the_lattice(self):
        _, lattice = SharedAlgebra.get()
        replay = _weight_four_replay(lattice)
        self.assertTrue(replay["passed"])
        self.assertEqual(replay["R_Q_lattice_image_terms"], 0)
        self.assertEqual(replay["Sym_F_Q_alone_image_terms"], 44)


class WeightFivePrimitiveTests(unittest.TestCase):
    def test_147250_primitive_search_lift_and_nonmembership(self):
        jets, lattice = SharedAlgebra.get()
        result = length_three_sector(jets, lattice, OMEGA_147250, 5)
        self.assertEqual(result["arc_multiplicity"], 2)
        self.assertEqual(result["kernel_multiplicity"], 1)
        self.assertEqual(result["g_tensor_I_highest"], 0)
        representative = result["representatives"][0]
        self.assertEqual(representative["column_coordinates"], [2, -3])
        self.assertEqual(len(representative["symbol"]), 112)
        self.assertEqual(representative["correction"], {})
        self.assertEqual(lattice.symmetric_lift(representative["symbol"]), {})
        record = _sector_record(result, "w5-147250", 147250)
        replay = verify_primitive_certificate(record, jets, lattice)
        self.assertTrue(replay["passed"])
        independent = full_weight_nonmembership(
            jets, OMEGA_147250, 5, representative["symbol"], length_three_character(2))
        self.assertTrue(independent["passed"])
        self.assertEqual(independent["ideal_rank_mod_p"], 159)

    def test_stored_248_certificate_and_tamper_detection(self):
        jets, lattice = SharedAlgebra.get()
        record = load_certificates()["sectors"]["w5-248"]
        self.assertEqual(record["kernel_multiplicity"], 1)
        self.assertEqual(record["arc_multiplicity"], 3)
        self.assertEqual(tuple(record["highest_weight_root_coordinates"]), THETA)
        replay = verify_primitive_certificate(record, jets, lattice, lattice_replay=False)
        self.assertTrue(replay["passed"])
        forged = copy.deepcopy(record)
        rep = forged["representatives"][0]
        rep["symbol"][0][1] = str(Q(rep["symbol"][0][1])+1)
        rep["sha256"] = digest([rep["symbol"], rep["correction"]])
        self.assertFalse(verify_primitive_certificate(forged, jets, lattice, lattice_replay=False)["passed"])
        stale = copy.deepcopy(record)
        stale["representatives"][0]["correction"] = []
        self.assertFalse(verify_primitive_certificate(stale, jets, lattice, lattice_replay=False)["passed"])

    def test_stored_3875_class_is_the_translated_weight_four_generator(self):
        record = load_certificates()["sectors"]["w5-3875"]
        self.assertEqual(tuple(record["highest_weight_root_coordinates"]), LAMBDA_3875)
        self.assertEqual(record["kernel_multiplicity"], 1)


class WeightSixTests(unittest.TestCase):
    def test_stored_weight_six_multiplicities(self):
        sectors = load_certificates()["sectors"]
        self.assertEqual(sectors["w6-30380"]["kernel_multiplicity"], 1)
        self.assertEqual(sectors["w6-30380"]["arc_multiplicity"], 3)
        self.assertEqual(sectors["w6-147250"]["kernel_multiplicity"], 1)
        self.assertEqual(sectors["w6-3875"]["kernel_multiplicity"], 1)

    def test_quartic_functional_and_F0_decision(self):
        jets, _ = SharedAlgebra.get()
        functional = QuarticFunctional(jets)
        self.assertEqual(functional.value(0, 0, 2, 2), -8)
        p248 = decode_polynomial(load_certificates()["sectors"]["w5-248"]["representatives"][0]["symbol"])
        decision = quartic_singlet_decision(jets, p248)
        self.assertTrue(decision["passed"])
        self.assertNotEqual(decision["kappa"], 0)
        self.assertEqual(decision["T0_norm_trace_identity"], 947856)
        self.assertEqual(decision["kappa"], 6510)
        self.assertEqual(decision["F0_equals_c_Y_modulo_ideal"], Q(91, 155))


    def test_weight_six_248_record_is_the_derivative_lift(self):
        sectors = load_certificates()["sectors"]
        rebuilt = derived_sector_record("w6-248", sectors["w5-248"], 5)
        self.assertEqual(rebuilt["representatives"][0]["sha256"],
                         sectors["w6-248"]["representatives"][0]["sha256"])
        jets, lattice = SharedAlgebra.get()
        replay = verify_primitive_certificate(sectors["w6-248"], jets, lattice, lattice_replay=False)
        self.assertTrue(replay["passed"])

    def test_closed_forms_of_the_new_generators(self):
        jets, _ = SharedAlgebra.get()
        certificate = closed_form_certificate(jets, load_certificates()["sectors"])
        self.assertTrue(certificate["passed"])
        self.assertEqual(certificate["identities"]["w6-30380"]["correction_terms"], 0)

    def test_length_four_3875_is_a_product(self):
        jets, _ = SharedAlgebra.get()
        decision = length_four_3875_decision(jets)
        self.assertTrue(decision["passed"])
        self.assertEqual(decision["dual_dimension"], 1)
        self.assertEqual(decision["values_on_x_h1_F_Q"], [63, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(decision["values_on_x_h0_DF_Q"], [-63, 0, 0, 0, 0, 0, 0, 0])


if __name__ == "__main__":
    unittest.main()
