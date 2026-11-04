"""Check the completed sectors and the exact closed form of their sole class."""
import json
from importlib.resources import files
import unittest
import perfectjet.asterion_primitives as p


class CompletedSectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record=json.loads(files('perfectjet.resources').joinpath('asterion_w7_certificates.json').read_text())

    def test_exact_sector_dimensions_and_scope(self):
        rows=self.record['sectors']
        self.assertEqual((rows['w7-1']['arc_multiplicity'],rows['w7-1']['kernel_multiplicity']),(1,0))
        self.assertEqual((rows['w7-248']['arc_multiplicity'],rows['w7-248']['kernel_multiplicity']),(9,1))
        self.assertEqual(self.record['kernel_dimension'],181753)
        self.assertIn('remain open',self.record['scope'])
        for row in rows.values():
            self.assertEqual(row['polynomial_highest_vectors']+row['lower_length_highest_vectors']-
                             row['projected_lattice_rank_Q'],row['lattice_null_dimension'])
            self.assertEqual(row['lattice_null_dimension']-row['ideal_highest_rank'],row['kernel_multiplicity'])

    def test_closed_form_symbol_and_correction_equal_double_derivative(self):
        j=p.JetAlgebra();u=j.algebra.root_index[p.THETA]
        source=p.load_certificates()['sectors']['w5-248']['representatives'][0]
        symbol={}
        for c,a,r,s in [(240,0,0,4),(-132,0,1,3),(-128,0,2,2),(48,1,0,3),
                        (-200,1,1,2),(-56,2,0,2),(-90,2,1,1),(-72,3,0,1)]:
            p._add(symbol,j.multiply({((u,a),):1},p._contraction(j,None,r,s)),c)
        correction={((u,6),):18420}
        for c,r,s in [(-80,0,5),(-1076,1,4),(-530,2,3)]:
            p._add(correction,p._contraction(j,u,r,s),c)
        rep=self.record['sectors']['w7-248']['representatives'][0]
        self.assertEqual(symbol,p.decode_polynomial(rep['symbol']))
        self.assertEqual(correction,p.decode_polynomial(rep['correction']))
        self.assertEqual(symbol,j.derivative(j.derivative(p.decode_polynomial(source['symbol']))))
        self.assertEqual(correction,j.derivative(j.derivative(p.decode_polynomial(source['correction']))))
        self.assertEqual(rep['sha256'],p.digest([rep['symbol'],rep['correction']]))
        self.assertTrue(p.verify_primitive_certificate(self.record['sectors']['w7-248'],j,lattice_replay=False)['passed'])


if __name__=='__main__':
    unittest.main()
