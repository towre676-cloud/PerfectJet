import unittest
from research.p521.known_controls import run_controls


class HistoricalControls(unittest.TestCase):
    def test_all_six_previously_explained_points(self):
        result = run_controls()
        self.assertEqual(len(result['controls']), 6)
        self.assertTrue(result['all_pass'])


if __name__ == '__main__':
    unittest.main()
