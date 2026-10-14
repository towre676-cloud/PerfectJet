"""Public recovered-data receipts must contain metrics and omit individual data."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('recovered_runner',
    Path(__file__).resolve().parents[1] / 'scripts/run_recovered_official.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class PublicReceiptTests(unittest.TestCase):
    def test_public_whitelist_removes_individual_and_training_records(self):
        private = {'summary': {'gain': .1, 'calibration_mean_error': {'baseline': .2, 'movement': .3},
                              'largest_influences': [{'athlete': 'private-player'}]},
                   'folds': [{'year': 2025, 'ids': ['private-player'], 'y': [2.0],
                              'source_coverage': {'private-player': {}},
                              'full_stage_audit': {'training_ids': ['private-trainer']}}],
                   'sources': {'players': ['private-player']}}
        result = runner.public_receipt(private)
        self.assertNotIn('private-player', str(result))
        self.assertNotIn('private-trainer', str(result))
        self.assertEqual(result['summary']['calibration_mean_error'], {'baseline': .2, 'movement': .3})
        self.assertEqual(result['folds'][0]['evaluated_athletes'], 1)
        self.assertEqual(result['folds'][0]['mse_by_predictor'], {})
        self.assertIn('largest_influences', private['summary'])

    def test_failed_refit_details_remain_private(self):
        result = runner.public_receipt({'full_refit_sensitivity': {
            'requested_draws': 2, 'successful_draws': 1, 'gains': [.01],
            'failures': [{'draw': 0, 'reason': 'unsupported private-player'}]}})
        self.assertNotIn('private-player', str(result))
        self.assertEqual(result['full_refit_sensitivity']['failed_draw_indices'], [0])

    def test_burst_families_retain_coverage_without_posteriors(self):
        value = {'families': {'primary': {'usable_attempts': 0, 'source_players': 0,
            'summary': {'gain': 0, 'decisions': [{'hits': {'baseline': 2, 'movement': 2}}]},
            'folds': [{'year': 2025, 'ids': ['private-player'], 'y': [0], 'posteriors': [{'mean': 99}]}]}}}
        result = runner.public_receipt(value)['families']['primary']
        self.assertEqual(result['usable_attempts'], 0)
        self.assertEqual(result['summary']['decisions'][0]['hits']['movement'], 2)
        self.assertNotIn('posteriors', str(result))


if __name__ == '__main__':
    unittest.main()
