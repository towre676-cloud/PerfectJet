import unittest
from dataclasses import replace
import numpy as np
from perfectjet.applications.nfl_scouting import repeat_decisions as D

class RepeatDecisionIntegrationTests(unittest.TestCase):
    def records(self):
        rng = np.random.default_rng(112)
        rows = []
        for year in (2023,2024,2025):
            for i in range(12):
                s = rng.normal(size=3); a = s+rng.normal(0,.4,3); b = s+rng.normal(0,.4,3)
                aid = f'{year}:{i}'
                rows.append(D.Pair(aid,aid,year,tuple(a),tuple(b)))
        return rows

    def test_model_shapes_and_board_abstention(self):
        report,private = D.evaluate(self.records())
        self.assertEqual(report['ridge_fits'],16)
        self.assertEqual(report['evaluation_players'],12)
        for v in report['results'].values():
            self.assertFalse(v['board_calibration']['finite'])
            self.assertEqual(v['whole_board']['settled_pairs'],0)
        self.assertFalse(report['nfl_scouting_advantage_established'])
        self.assertEqual(np.asarray(private['ridge_joint']['truth']).shape,(12,3))

    def test_evaluation_labels_never_change_model_or_calibration(self):
        rows = self.records(); a,pa = D.evaluate(rows)
        changed = [replace(r,second=tuple(np.asarray(r.second)+50)) if r.year==2025 else r for r in rows]
        b,pb = D.evaluate(changed)
        for name in D.PROTOCOL['methods']:
            self.assertEqual(a['results'][name]['calibration'],b['results'][name]['calibration'])
            np.testing.assert_array_equal(pa[name]['predictions'],pb[name]['predictions'])
            self.assertGreater(b['results'][name]['mse'],a['results'][name]['mse'])

    def test_calibration_labels_change_radius_not_model(self):
        rows = self.records(); a,pa = D.evaluate(rows)
        changed = [replace(r,second=tuple(np.asarray(r.second)+50)) if r.year==2024 else r for r in rows]
        b,pb = D.evaluate(changed)
        for name in D.PROTOCOL['methods']:
            np.testing.assert_array_equal(pa[name]['predictions'],pb[name]['predictions'])
            self.assertGreater(b['results'][name]['calibration']['radius'],a['results'][name]['calibration']['radius'])

    def test_cross_partition_original_leakage_rejected(self):
        rows = self.records(); rows[-1] = replace(rows[-1],original=rows[0].original)
        with self.assertRaises(ValueError):D.evaluate(rows)

    def test_duplicate_fit_keys_rejected(self):
        rows = [r for r in self.records() if r.year==2023]
        with self.assertRaises(ValueError):D.fit_models(rows+[rows[0]])

    def test_original_bootstrap_groups_preserved(self):
        r = D.refit_sensitivity(self.records(),draws=4)
        self.assertEqual(r['successful_draws'],4)
        self.assertTrue(all(x['calibration_originals']<=12 for x in r['draws']))
        self.assertNotIn('confidence',r['scope'].split('no')[0])

if __name__ == '__main__':unittest.main()
