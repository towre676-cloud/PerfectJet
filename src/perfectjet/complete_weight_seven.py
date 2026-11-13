"""Retained exact evidence for the level-one E8 arc-to-Li map at weight seven.

Run with python -m perfectjet.complete_weight_seven from an installed wheel.
"""
from collections import Counter
import hashlib
from importlib.resources import files
import json

from .weight_seven import report as cubic_report

RESOURCE = 'asterion_complete_weight7.json'
INSTALLED_RESOURCES = (
    'asterion_primitive_certificates.json',
    'asterion_w7_certificates.json',
    'asterion_w7_integration.json',
)
PRIMITIVE_SECTORS = frozenset({
    'w5-147250', 'w5-248', 'w5-3875', 'w6-147250', 'w6-248', 'w6-30380', 'w6-3875',
})


def complete_source_digests(package=None):
    if package is None:
        package = files('perfectjet')
    paths = sorted(
        (path for path in package.iterdir()
         if path.name.startswith('asterion') and path.name.endswith('.py')),
        key=lambda path: path.name,
    )
    paths.append(package.joinpath('complete_weight_seven_projection.py'))
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def report():
    resources = files('perfectjet.resources')
    record = json.loads(resources.joinpath(RESOURCE).read_bytes())
    if (record['schema'] != 'perfectjet/asterion-complete-weight7/1'
            or record['conformal_weight'] != 7
            or record['kernel_li_degrees_by_current_length'] != {'3': 4, '4': 3}):
        raise ValueError('invalid complete weight-seven grading or schema')
    if record['source_sha256'] != complete_source_digests():
        raise ValueError('stale complete weight-seven source binding')
    bindings = record['installed_resource_sha256']
    if set(bindings) != set(INSTALLED_RESOURCES):
        raise ValueError('incomplete complete weight-seven resource bindings')
    for name, expected in bindings.items():
        if hashlib.sha256(resources.joinpath(name).read_bytes()).hexdigest() != expected:
            raise ValueError('stale complete weight-seven resource: ' + name)
    primitives = json.loads(resources.joinpath(INSTALLED_RESOURCES[0]).read_bytes())
    if set(primitives['sectors']) != PRIMITIVE_SECTORS:
        raise ValueError('incomplete primitive certificate sectors')

    status = record['verification_status']
    if (status['complete_mathematical_replay_passed'] is not True
            or status['focused_replay_tests_passed'] is not True
            or status['runs_lattice_replay_on_report_read'] is not False):
        raise ValueError('invalid complete weight-seven verification status')
    theorem = record['theorem']
    rows = theorem['quartic_sector_table']
    source = theorem['quartic_source_character']
    if len(rows) != 19 or {str(row['dimension']): row['source'] for row in rows} != source:
        raise ValueError('incomplete quartic source sectors')
    for row in rows:
        if (any(type(row[key]) is not int or row[key] < 0
                for key in ('source', 'ideal', 'arc', 'image', 'kernel'))
                or row['source'] != row['ideal'] + row['arc']
                or row['arc'] != row['image'] + row['kernel']
                or row['new_primitives'] != 0):
            raise ValueError('inconsistent quartic sector ranks')
    for column, field in (('arc', 'quartic_arc'), ('image', 'quartic_VOA_image'),
                          ('kernel', 'quartic_kernel')):
        character = {str(row['dimension']): row[column] for row in rows if row[column]}
        if theorem[field + '_character'] != character:
            raise ValueError('inconsistent quartic character: ' + field)

    cubic = {d: m for d, m in cubic_report()['kernel_multiplicities'].items() if m}
    total = Counter(cubic) + Counter(theorem['quartic_kernel_character'])
    if (theorem['cubic_kernel_character'] != cubic
            or theorem['total_weight7_kernel_character'] != total
            or Counter(theorem['simple_VOA_character']) + total != theorem['total_arc_character']):
        raise ValueError('inconsistent complete weight-seven character')
    for field in ('quartic_source', 'quartic_arc', 'quartic_VOA_image', 'quartic_kernel',
                  'cubic_kernel', 'total_weight7_kernel', 'total_arc', 'simple_VOA'):
        if theorem[field + '_dimension'] != sum(
                int(d) * m for d, m in theorem[field + '_character'].items()):
            raise ValueError('inconsistent weight-seven dimension: ' + field)
    if (theorem['new_weight7_primitive_character'] or theorem['new_weight7_primitive_dimension'] != 0
            or not theorem['short_kernel_zero'] or not theorem['lengths5_through7_arc_zero']
            or theorem['all_weight_finite_generation_proved']):
        raise ValueError('inconsistent complete weight-seven scope')
    return record


if __name__ == '__main__':
    print(json.dumps(report(), indent=2, sort_keys=True))
