"""Exact algebraic relations, source conventions and bounded analytic replay."""
from fractions import Fraction as Q
import json
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch
from perfectjet.kz_half_braid import (algebraic_model, analytic_replay,
    braid_receipt, descent_certificate, HALF_PHASES, power)
from perfectjet.asterion_kz import identity, matrix_multiply as mm, matrix_scale
from perfectjet.rings import QuotientRing, cyclotomic

class HalfBraidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=algebraic_model()

    def test_exact_descent_hypotheses_and_tensor_parity(self):
        r=descent_certificate()
        self.assertTrue(r['passed'])
        self.assertEqual(len(r['checks']),16)
        with patch('perfectjet.kz_half_braid.PARITIES',(1,1,1,1,1)):
            self.assertFalse(descent_certificate()['passed'])

    def test_exact_tw_model_relations_and_simplicity(self):
        r=self.model
        self.assertTrue(r['passed'])
        self.assertTrue(all(r['checks'].values()))
        self.assertEqual(len(r['simplicity_polynomials']),20)
        self.assertTrue(all(v['nonzero'] and any(Q(c) for c in v['coefficients'])
                            for v in r['simplicity_polynomials']))
        self.assertEqual((r['gamma_exponent'],r['central_exponent'],r['determinant_exponent']),(12,4,9))
        json.dumps(r,allow_nan=False)

    def test_independent_decode_and_corruption_rejection(self):
        ring=QuotientRing(cyclotomic(17))
        def decode(m):
            return tuple(tuple(ring.element(c) for c in row) for row in m)
        a=decode(self.model['matrices']['sigma1'])
        b=decode(self.model['matrices']['sigma2'])
        self.assertEqual(mm(mm(a,b),a),mm(mm(b,a),b))
        self.assertEqual(power(mm(a,b),3),matrix_scale(identity(),ring.generator**4))
        rows=[list(r) for r in a]; rows[0][1]+=1
        bad=tuple(tuple(r) for r in rows)
        self.assertNotEqual(mm(mm(bad,b),bad),mm(mm(b,bad),b))

    def test_half_spectrum_has_actual_and_projective_order34(self):
        # Signed phases are represented by exponents modulo34 for eta=e^(pi*i/17).
        exponents=[(2*e+(17 if sign<0 else 0))%34 for sign,e in HALF_PHASES]
        self.assertEqual(exponents,[4,2,28,17,1])
        for n in range(1,34):
            self.assertFalse(all(n*(e-exponents[0])%34==0 for e in exponents))
        self.assertEqual(sum(exponents)%34,18)

    def test_fast_receipt_preserves_proof_boundaries(self):
        r=braid_receipt()
        self.assertTrue(r['passed'])
        self.assertTrue(r['linear_B3_representation'])
        self.assertFalse(r['analytic_loop_replayed_in_this_run'])
        self.assertFalse(r['full_discrete_image_presentation'])
        self.assertFalse(r['canonical_endpoint_associator_computed'])
        with self.assertRaises(TypeError):
            braid_receipt(exhaustive=1)

    def test_equation_catalogue_preserves_all698_preceding_records(self):
        root=Path(__file__).resolve().parents[1]
        source=json.loads((root/'data/equations.json').read_text())['equations']
        extension=json.loads((root/'data/asterion_braid_equations.json').read_text())
        prefix=extension['preserved_prefix']
        self.assertGreaterEqual(len(source),710)
        self.assertEqual(source[698:710],extension['equations'])
        raw=json.dumps(source[:698],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),prefix['sha256_of_canonical_records'])
        self.assertEqual(len({r['id'] for r in source}),len(source))
        self.assertEqual([r['id'] for r in source[698:710]],[f'PJ-HB{i:03d}' for i in range(1,13)])

    def test_fresh_rigorous_analytic_replay_and_negative_control(self):
        r=analytic_replay()
        self.assertTrue(r['passed'])
        self.assertTrue(r['specialized_irreducibility']['passed'])
        self.assertTrue(r['omitted_parity_negative_control']['nonzero_certified'])
        for v in r['consistency_enclosures'].values():
            self.assertLess(Q(v['norm_upper_bound']),Q(1,1000))
            self.assertFalse(v['nonzero_certified'])
        for v in r['same_chart_half_braids'].values():
            self.assertGreater(Q(v['infinity_norm_error_bound']),0)

if __name__=='__main__':
    unittest.main()
