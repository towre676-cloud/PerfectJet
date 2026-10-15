"""Evaluate recovered official inputs; publish aggregates, keep predictions private.

Only load a checkpoint freshly created by prepare_official_bridge_data.py and
whose digest matches its preparation receipt. Pickle is not an interchange
format for untrusted downloads.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pickle
from statistics import fmean
import time

from perfectjet.applications.nfl_scouting import bridges, burst_transfer
from perfectjet.applications.nfl_scouting.official import FRONT_DRILLS
from perfectjet.applications.nfl_scouting import official, movement_targets


def aggregate(value):
    """Omit individual predictions, identifiers and influence rankings."""
    if isinstance(value, dict):
        return {k: aggregate(v) for k, v in value.items() if k != 'largest_influences'}
    if isinstance(value, (list, tuple)):
        return [aggregate(v) for v in value]
    return value


def public_receipt(result):
    """Allowlist public metrics rather than guessing where private IDs occur."""
    keys = ('protocol', 'protocol_sha256', 'synthetic', 'status', 'include_ngs',
            'summary', 'movement_vs_direct_baseline_summary',
            'movement_vs_conventional_bridge_summary', 'conventional_bridge_summary',
            'conclusion', 'elapsed_seconds', 'checkpoint_sha256',
            'aggregate_only_public_receipt', 'full_refit_sensitivity')
    output = {key: aggregate(result[key]) for key in keys if key in result}
    if 'full_refit_sensitivity' in result:
        refits = result['full_refit_sensitivity']
        output['full_refit_sensitivity'] = {
            key: aggregate(value) for key, value in refits.items() if key != 'failures'}
        output['full_refit_sensitivity']['failed_draws'] = len(refits.get('failures', []))
        output['full_refit_sensitivity']['failed_draw_indices'] = [
            failure['draw'] for failure in refits.get('failures', [])]
    def fold_receipt(fold):
        metrics = {key: fmean((y-p)**2 for y, p in zip(fold['y'], fold[key]))
                   for key in ('baseline', 'movement', 'conventional_bridge', 'strong_baseline')
                   if key in fold and fold['y']}
        state = fold.get('full_stage_audit', {})
        return {key: fold[key] for key in ('year', 'chosen_penalties', 'inner_scores',
                'strong_baseline_family', 'strong_baseline_selection_scope') if key in fold} | {
                'evaluated_athletes': len(fold['ids']), 'mse_by_predictor': metrics,
                'training_movement_state': {key: state[key] for key in ('nfl_sequences',
                    'state_history_steps', 'state_count', 'state_cv_mse', 'instantaneous_cv_mse',
                    'state_horizon_seconds', 'state_training_maximum_season') if key in state}}
    if 'folds' in result:
        output['folds'] = [fold_receipt(f) for f in result['folds']]
    if 'families' in result:
        output['families'] = {name: {
            **{key: aggregate(family[key]) for key in ('usable_attempts', 'source_players',
                'attempts_by_drill', 'summary') if key in family},
            'folds': [fold_receipt(f) for f in family['folds']]}
            for name, family in result['families'].items()}
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint', required=True, type=Path)
    p.add_argument('--receipt', required=True, type=Path)
    p.add_argument('--private-output', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--kind', choices=('bridge', 'burst'), default='bridge')
    p.add_argument('--without-ngs', action='store_true')
    p.add_argument('--refits', type=int, default=0)
    p.add_argument('--front-drills', action='store_true',
                   help='Declared secondary bridge using all original front drill families')
    args = p.parse_args()
    raw = args.checkpoint.read_bytes()
    receipt = json.loads(args.receipt.read_text())
    digest = hashlib.sha256(raw).hexdigest()
    if digest != receipt['checkpoint_sha256']:
        raise ValueError('Private checkpoint differs from the preparation receipt')
    for module in (official, movement_targets):
        expected = receipt.get('extractor_sha256', {}).get(module.__name__)
        actual = hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
        if expected is None or actual != expected:
            raise ValueError('Extraction code differs from the checkpoint preparation receipt; rebuild it')
    data = pickle.loads(raw)
    started = time.monotonic()
    if args.kind == 'bridge':
        config = bridges.BridgeConfig(source_drills=tuple(FRONT_DRILLS)) if args.front_drills else None
        result = bridges.experiment(data['dataset'], data['movement'], not args.without_ngs, config=config)
        if args.refits:
            result['full_refit_sensitivity'] = bridges.full_refit_sensitivity(
                data['dataset'], data['movement'], args.refits, not args.without_ngs, config=config)
    else:
        result = burst_transfer.experiment(data['dataset'], not args.without_ngs)
        if args.refits:
            result['full_refit_sensitivity'] = burst_transfer.full_refit_sensitivity(
                data['dataset'], args.refits, not args.without_ngs)
    result['elapsed_seconds'] = time.monotonic() - started
    result['checkpoint_sha256'] = digest
    result['aggregate_only_public_receipt'] = True
    args.private_output.parent.mkdir(parents=True, exist_ok=True)
    args.private_output.write_text(json.dumps(result, indent=2) + '\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(public_receipt(result), indent=2) + '\n')
    print(json.dumps({'status': 'complete', 'seconds': result['elapsed_seconds'],
                      'summary': aggregate(result.get('summary', result.get('families')))}), flush=True)


if __name__ == '__main__':
    main()
