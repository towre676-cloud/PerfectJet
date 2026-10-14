"""Execute the deliberately artificial stacked bridge and exact plan receipt.

Run with PYTHONPATH=src. The test fixture is synthetic and declares all noise,
cost and covariance assumptions; it is never substituted for official inputs.
"""
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import runpy

from perfectjet.applications.nfl_scouting.bridges import fit_split
from perfectjet.applications.nfl_scouting.bridge_allocation import plan_from_bridge_fit
from perfectjet.applications.nfl_scouting.allocation import MeasurementCandidate

ROOT = Path(__file__).resolve().parents[1]


def encode(value):
    if isinstance(value, Fraction):
        return str(value)
    raise TypeError(type(value).__name__)


def build():
    fixture = runpy.run_path(str(ROOT/'tests/test_nfl_bridges.py'))['fixture']
    ds, records, tr, te, config = fixture()
    assert ds.synthetic
    fit = fit_split(ds, records, tr, te, 2024, 100, seed=71, config=config)
    names = fit['frozen_jacobian']['source_features']
    width = len(names)
    prior = [[int(i == j) for j in range(width)] for i in range(width)]
    candidates = [MeasurementCandidate(f'synthetic-measure-{j}',
                  tuple(int(i == j) for i in range(width)), 1, 1,
                  attempt_ids=(f'new-independent-attempt-{j}',)) for j in range(width)]
    plan = plan_from_bridge_fit(fit, prior, candidates, budget=2)
    sources = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted((ROOT/'src/perfectjet/applications/nfl_scouting').glob('*.py'))}
    out = {'evidence_scope': 'Explicitly artificial cross-domain fixture; no NFL evidence or empirical noise/cost estimates',
           'fixture_seed': 991, 'split_seed': 71, 'config': asdict(config),
           'source_sha256': sources, 'fit': fit, 'allocation': plan,
           'declared_synthetic_measurement_model': {
               'prior': 'Identity in fixture source-feature units',
               'independent_noise_variance': 1, 'unit_candidate_cost': 1, 'budget': 2}}
    dest = ROOT/'results/nfl-math-bridges/stacked_fixture.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, default=encode, allow_nan=False)+'\n')
    print(json.dumps({'synthetic_players': len(ds.athletes), 'source_features': width,
                      'fitted_jacobian_passed': plan['jacobian_composition_audit']['passed'],
                      'selected_synthetic_package': plan['allocation']['candidate_ids'],
                      'maximum_error_identity_discrepancy': max(d['identity_error'] for d in fit['error_decomposition']),
                      'NFL_evidence': False}))


if __name__ == '__main__':
    build()
