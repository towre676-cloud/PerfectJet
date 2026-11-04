"""Source-bound report of the completed cubic theorem (not a fresh lattice replay).

Available in an installed wheel: python -m perfectjet.weight_seven.
The full independent replay commands are in the research documentation.
"""
import hashlib
from importlib.resources import files
import json

from .asterion import source_digests

RESOURCE = 'asterion_w7_integration.json'


def report():
    resources = files('perfectjet.resources')
    record = json.loads(resources.joinpath(RESOURCE).read_text(encoding='utf-8'))
    if record['source_sha256'] != source_digests():
        raise ValueError('stale weight-seven source binding')
    required = {'asterion_w7_certificates.json', 'asterion_primitive_certificates.json'}
    if set(record['installed_resource_sha256']) != required:
        raise ValueError('incomplete installed certificate bindings')
    for name, expected in record['installed_resource_sha256'].items():
        if hashlib.sha256(resources.joinpath(name).read_bytes()).hexdigest() != expected:
            raise ValueError('stale installed certificate: ' + name)
    expected = {str(d): int(d in (248, 3875, 30380, 147250))
                for d in (1, 248, 3875, 27000, 30380, 147250, 779247, 2450240, 4096000)}
    if record['kernel_multiplicities'] != expected:
        raise ValueError('incomplete or inconsistent cubic sector list')
    if record['new_cubic_primitive_multiplicity'] != 0:
        raise ValueError('inconsistent cubic primitive claim')
    if record['kernel_dimension'] != sum(int(d)*m for d,m in expected.items()):
        raise ValueError('inconsistent cubic dimension')
    return record


if __name__ == '__main__':
    print(json.dumps(report(), indent=2, sort_keys=True))
