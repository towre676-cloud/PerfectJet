import unittest
from research.p521 import curve


class PublicCurveTests(unittest.TestCase):
    def test_standard_point_and_order(self):
        self.assertTrue(curve.on_curve(curve.G))
        self.assertIsNone(curve.multiply(curve.N))
        self.assertEqual(curve.multiply(curve.N+1), curve.G)

    def test_group_controls(self):
        self.assertEqual(curve.add(curve.multiply(37), curve.multiply(41)), curve.multiply(78))
        self.assertIsNone(curve.add(curve.G, (curve.GX, -curve.GY % curve.P)))
        self.assertFalse(curve.on_curve((curve.GX, (curve.GY+1) % curve.P)))

    def test_field_and_published_seed(self):
        self.assertTrue(curve.lucas_lehmer())
        self.assertTrue(curve.seed_provenance()['matches_standard'])


if __name__ == '__main__':
    unittest.main()
