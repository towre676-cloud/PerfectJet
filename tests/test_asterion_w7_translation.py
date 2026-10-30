"""Structural sl2 identities underlying survival of translated kernel classes."""
from fractions import Fraction as Q
import unittest
from perfectjet.asterion_primitives import JetAlgebra, _add, decode_polynomial, load_certificates


class TranslationTests(unittest.TestCase):
    def test_mobius_commutator_on_repeated_and_mixed_jets(self):
        for orders in ((0,), (1,), (6,), (0,0), (0,1,3), (0,0,4), (1,1,2)):
            p = {tuple((0, r) for r in sorted(orders)): Q(7,3)}
            lhs = JetAlgebra.mobius_lower(JetAlgebra.derivative(p))
            _add(lhs, JetAlgebra.derivative(JetAlgebra.mobius_lower(p)), -1)
            self.assertEqual(lhs, {m: 2*sum(r+1 for _,r in m)*z for m,z in p.items()})

    def test_differentiated_quadratic_ideal_is_lowering_stable(self):
        # The highest quadratic generator e_theta^2; equivariance covers its module.
        j = JetAlgebra()
        from perfectjet.asterion_primitives import THETA
        u = j.algebra.root_index[THETA]
        original = {((u,0),(u,0)): Q(1)}
        current = original
        for k in range(1,6):
            previous = current
            current = j.derivative(current)
            self.assertEqual(j.mobius_lower(current), {m:k*(k+3)*z for m,z in previous.items()})

    def test_adjoint_double_derivative_is_highest(self):
        j = JetAlgebra()
        source = load_certificates()['sectors']['w5-248']['representatives'][0]
        symbol = j.derivative(j.derivative(decode_polynomial(source['symbol'])))
        self.assertTrue(j.is_highest(symbol))
        self.assertTrue(symbol)
        self.assertTrue(all(len(m)==3 and sum(r+1 for _,r in m)==7 for m in symbol))


if __name__ == '__main__':
    unittest.main()
