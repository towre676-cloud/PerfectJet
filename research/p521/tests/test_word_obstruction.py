import copy
import unittest
from research.p521.word_obstruction import certificate, verify_document, GX, GY


class WordObstructionTests(unittest.TestCase):
    def test_public_coordinates(self):
        document = {'schema': 'perfectjet/p521-word-suite/1',
                    'certificates': [certificate(value, name) for name, value in (('Gx', GX), ('Gy', GY))]}
        self.assertTrue(verify_document(document)['verified'])
        changed = copy.deepcopy(document)
        changed['certificates'][0]['maximum_quotient'] += 1
        with self.assertRaises(ValueError):
            verify_document(changed)

    def test_satisfiable_zero_coordinate_has_no_obstruction(self):
        with self.assertRaises(ValueError):
            certificate(0, 'synthetic')


if __name__ == '__main__':
    unittest.main()
