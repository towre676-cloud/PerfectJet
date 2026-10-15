"""Replay source-only uncertainty study from an owner-trusted private checkpoint."""
import argparse
import datetime
import hashlib
import importlib.metadata
import platform
import gzip
import json
import pickle
import time
from pathlib import Path
from perfectjet import replication_geometry
from perfectjet.applications.nfl_scouting import repeat_decisions as D, official, movement_targets


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('checkpoint', 'preparation', 'out', 'private'):
        parser.add_argument('--'+name, required=True, type=Path)
    parser.add_argument('--refits', type=int, default=128)
    args = parser.parse_args(); root = Path(__file__).resolve().parents[1]
    if args.private.resolve().is_relative_to(root):
        raise ValueError('private output must be outside public repository')
    if args.refits < 0:
        raise ValueError('refits cannot be negative')
    preparation = json.loads(args.preparation.read_text()); raw = args.checkpoint.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != preparation['checkpoint_sha256']:
        raise ValueError('checkpoint does not match owner preparation')
    for module in (official, movement_targets):
        if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != preparation['extractor_sha256'][module.__name__]:
            raise ValueError('checkpoint extractor source changed')
    # A digest is provenance, not a security sandbox for arbitrary pickle files.
    # Load only the explicitly recovered, owner-trusted checkpoint.
    started = time.monotonic()
    receipt = {'schema': 'perfectjet/repeat-decision-execution/1',
               'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'checkpoint_sha256': digest,
               'environment': {'python': platform.python_version(), **{n: importlib.metadata.version(n) for n in ('numpy','scipy','scikit-learn','pandas')}},
               'source_sha256': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted((root/'src').rglob('*.py')) + [Path(__file__).resolve(),root/'pyproject.toml']}}
    write(args.out/'protocol.json', D.PROTOCOL); write(args.out/'execution-start.json', receipt)
    dataset = pickle.loads(raw)['dataset']; records, coverage = D.source_pairs(dataset)
    write(args.out/'source-coverage.json', coverage); write(args.out/'nominal-audit.json', D.nominal_audit(dataset))
    result, individual = D.evaluate(records); write(args.out/'study.json', result)
    write(args.private/'repeat-decision-individuals.json', individual)
    if args.refits:
        refits = D.refit_sensitivity(records, draws=args.refits); write(args.out/'refits.json', refits)
        receipt['successful_refits'] = refits['successful_draws']; receipt['requested_refits'] = args.refits
    receipt['elapsed_seconds'] = time.monotonic()-started
    receipt['completed_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    write(args.out/'execution.json', receipt)
    names = ['protocol', 'execution-start', 'source-coverage', 'nominal-audit', 'study', 'execution']
    if args.refits:
        names.append('refits')
    public = {n: json.loads((args.out/(n+'.json')).read_text()) for n in names}
    (args.out/'run.json.gz').write_bytes(gzip.compress(json.dumps(public, sort_keys=True, allow_nan=False).encode(), mtime=0))
    print(json.dumps({'fit': result['fit_players'], 'calibration': result['calibration_players'],
        'evaluation': result['evaluation_players'], 'methods': {k: {'mse': v['mse'], 'coverage': v['joint_calibrated_coverage'],
        'volume': v['ellipsoid_volume']} for k, v in result['results'].items()}, 'elapsed_seconds':receipt['elapsed_seconds']}, indent=2))

if __name__ == '__main__':
    main()
