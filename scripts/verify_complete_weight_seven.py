"""Regenerate the complete weight-seven theorem using the maintained runtime."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from scripts.audit_complete_weight7 import prepare, ROOT
from perfectjet.complete_weight_seven import (
    INSTALLED_RESOURCES, RESOURCE, complete_source_digests, report,
)

PACKAGE = ROOT / 'src/perfectjet'
OUTPUTS = (
    'COMPLETE_WEIGHT7_THEOREM.json', 'VOA_weight7_character.json', 'arc_length3_replay.json',
    'quartic_schur_receipt.json', 'quartic_casimir_cutoff_receipt.json',
    'quartic_independent_rank_verification.json', 'quartic_frontier_verification.json',
    'quartic_30380_VOA_receipt.json', 'quartic_30380_ideal_receipt.json',
    'quartic_30380_partial_products.json', 'weight7_short_and_long_receipt.json',
    *(f'quartic_{sector}_{kind}_receipt.json'
      for sector in ('adjoint', '3875') for kind in ('ideal', 'products')),
    'quartic_singlet_ideal_receipt.json',
    *(f'weight{source}_source_replay.json'
      for source in ('4_3875', '5_adjoint', '5_147250', '6_quartic', '6_30380')),
    *(f'quartic_span_certificate_{dimension}.json'
      for dimension in (27000, 147250, 779247, 1763125, 2450240, 4096000, 6696000)),
    *(f'quartic_full_{dimension}.json'
      for dimension in (27000, 1763125, 2450240, 4096000, 6696000)),
    *(f'quartic_{kind}_{dimension}.json'
      for dimension in (147250, 779247) for kind in ('ideal_only', 'old_products')),
)


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def make_record(scratch, imported):
    summary_files = (
        'COMPLETE_WEIGHT7_THEOREM.json', 'quartic_schur_receipt.json',
        'quartic_30380_VOA_receipt.json', 'quartic_adjoint_products_receipt.json',
        'quartic_3875_products_receipt.json', 'quartic_30380_partial_products.json',
        'quartic_old_products_147250.json', 'quartic_old_products_779247.json',
    )
    evidence = {name: json.loads((scratch / name).read_bytes()) for name in summary_files}
    theorem = dict(evidence['COMPLETE_WEIGHT7_THEOREM.json'])
    source = evidence['quartic_schur_receipt.json']['weight7_length4_ambient']['irreducibles']
    theorem['quartic_source_character'] = {str(row['dimension']): row['multiplicity'] for row in source}
    theorem['quartic_source_dimension'] = sum(row['dimension'] * row['multiplicity'] for row in source)
    voa = evidence['quartic_30380_VOA_receipt.json']
    counts = {row['length']: row['highest_count'] for row in voa['lower_highest_counts']}
    if (counts != {1: 0, 2: 3, 3: 10}
            or len(voa['lower_highest_columns']) != 13
            or len(voa['projected_image_columns']) != 14
            or (voa['lower_projected_rank_Q'], voa['with_quartic_projected_rank_Q']) != (7, 8)):
        raise ValueError('incomplete 30380 lower-length image comparison')
    return {
        'schema': 'perfectjet/asterion-complete-weight7/1',
        'scope': 'Level-one E8 arc-to-Li kernel over characteristic zero at conformal weight seven.',
        'conformal_weight': 7,
        'kernel_li_degrees_by_current_length': {'3': 4, '4': 3},
        'quartic_old_product_null_dependencies': {
            '1': ['weight5_adjoint_source_replay.json', 'weight6_quartic_source_replay.json'],
            '248': evidence['quartic_adjoint_products_receipt.json']['null_lift_dependencies'],
            '3875': [evidence['quartic_3875_products_receipt.json']['null_lift_dependency']],
            '30380': evidence['quartic_30380_partial_products.json']['null_lift_dependencies'],
            **{str(d): evidence[f'quartic_old_products_{d}.json']['null_dependencies']
               for d in (147250, 779247)},
        },
        'quartic_30380_image_check': {
            'lower_highest_counts': counts,
            'lower_projected_rank': 7,
            'with_quartic_projected_rank': 8,
        },
        'verification_mode': 'Retained exact mathematical replay evidence from the maintained runtime. Reading this report checks installed bindings and character arithmetic.',
        'verification_status': {
            'complete_mathematical_replay_passed': True,
            'focused_replay_tests_passed': True,
            'runs_lattice_replay_on_report_read': False,
        },
        'research_import_commit': '3000885b26f8b679c266013761168894d4711465',
        'source_sha256': complete_source_digests(),
        'installed_resource_sha256': {
            name: sha((PACKAGE / 'resources' / name).read_bytes()) for name in INSTALLED_RESOURCES
        },
        'imported_input_sha256': imported,
        'replay_evidence_encoding': 'UTF-8 JSON, sorted keys, two-space indentation and a final LF',
        'replay_evidence_sha256': {name: sha(encoded(json.loads((scratch / name).read_bytes()))) for name in OUTPUTS},
        'theorem': theorem,
    }


def check_record(retained, replayed):
    for name, digest in replayed['replay_evidence_sha256'].items():
        if retained['replay_evidence_sha256'].get(name) != digest:
            raise ValueError('complete weight-seven replay differs: ' + name)
    if retained != replayed:
        raise ValueError('complete weight-seven report differs from regenerated evidence')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--write', action='store_true', help='refresh the report after successful replay')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='perfectjet-complete-w7-') as temporary:
        scratch = Path(temporary)
        imported = prepare(scratch)
        shutil.rmtree(scratch / 'src')
        shutil.copytree(ROOT / 'src', scratch / 'src', ignore=shutil.ignore_patterns('__pycache__'))
        # The pinned research scripts import the evaluator by its historical name.
        package = scratch / 'src/perfectjet'
        (package / 'asterion_lattice_projection4.py').write_text(
            'from .complete_weight_seven_projection import ProjectedLatticeE8VOA4\n',
            encoding='utf-8',
        )
        for name in OUTPUTS:
            (scratch / name).unlink(missing_ok=True)
        with (args.output / 'replay.log').open('w', encoding='utf-8') as log:
            env = dict(os.environ, PYTHONUTF8='1')
            env.pop('PYTHONOPTIMIZE', None)
            subprocess.run([sys.executable, '-u', 'replay.py', '--weight7', '--tests'],
                           cwd=scratch, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        record = make_record(scratch, imported)
        replayed_sources = complete_source_digests(scratch / 'src/perfectjet')
        replayed_sources.pop('asterion_lattice_projection4.py')
        if record['source_sha256'] != replayed_sources:
            raise ValueError('maintained Asterion sources changed during replay')
        primitive = INSTALLED_RESOURCES[0]
        if record['installed_resource_sha256'][primitive] != sha(
                (scratch / 'src/perfectjet/resources' / primitive).read_bytes()):
            raise ValueError('primitive certificate resource changed during replay')
        for name in OUTPUTS:
            shutil.copyfile(scratch / name, args.output / name)
    path = PACKAGE / 'resources' / RESOURCE
    if args.write:
        path.write_bytes(encoded(record))
    else:
        check_record(json.loads(path.read_bytes()), json.loads(encoded(record)))
    print(json.dumps({'schema': report()['schema'], 'complete_replay_passed': True}))


if __name__ == '__main__':
    main()
