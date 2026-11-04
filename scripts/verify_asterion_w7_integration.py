"""Seal/check the evidence inventory after the documented exact replays.

Hash checks do not replace mathematical replay. The dedicated CI workflow
recomputes all cubic rank evidence before checking this inventory.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from perfectjet.asterion import source_digests

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'results/asterion-primitives'
RESOURCE=ROOT/'src/perfectjet/resources/asterion_w7_integration.json'


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def without_sources(value):
    if isinstance(value,dict):return {k:without_sources(v) for k,v in value.items() if k!='source_sha256'}
    if isinstance(value,list):return [without_sources(v) for v in value]
    return value


def build():
    sources=source_digests()
    prior=read(FOLDER/'w7-prior-sectors-replay.json.gz')
    completed=read(ROOT/'src/perfectjet/resources/asterion_w7_certificates.json')
    for data in (prior,completed):
        if data['source_sha256']!=sources:raise ValueError('stale cubic source binding')
    rows=dict(prior['sectors'],**completed['sectors'])
    expected={str(d):int(d in (248,3875,30380,147250)) for d in (1,248,3875,27000,30380,147250,779247,2450240,4096000)}
    multiplicities={str(v['weyl_dimension']):v['kernel_multiplicity'] for v in rows.values()}
    if multiplicities!=expected:raise ValueError('inconsistent nine-sector theorem')
    paths=[]
    for folder in ('asterion','asterion-extension','asterion-frontiers'):
        manifest=read(ROOT/'results'/folder/'manifest.json')
        for name,metadata in manifest['files'].items():
            path=ROOT/'results'/folder/name
            raw=path.read_bytes()
            if len(raw)!=metadata['bytes'] or hashlib.sha256(raw).hexdigest()!=metadata['sha256']:
                raise ValueError('corrupted receipt: '+str(path))
            if read(path)['source_sha256']!=sources:raise ValueError('stale publication binding: '+str(path))
        paths.extend(p for p in (ROOT/'results'/folder).iterdir() if not p.name.startswith('.'))
    audit=read(FOLDER/'w7-provenance-audit.json')
    for name,expected_hash in audit['mathematical_payload_sha256'].items():
        raw=json.dumps(without_sources(read(ROOT/name)),sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
        if hashlib.sha256(raw).hexdigest()!=expected_hash:raise ValueError('mathematical payload changed: '+name)
    paths.extend(FOLDER/name for name in ('w7-provenance-audit.json','length-three-boundary.json',
        'w7-prior-sectors-replay.json.gz','w7-1-projected-rank.json.gz','w7-248-projected-rank.json.gz',
        'w7-adjoint-ideal.json.gz','w7-schur-reconstruction.json','w7-source-null-replay.json',
        'w7-completion-summary.json','w7-verification.json'))
    paths.extend(ROOT/'scripts'/name for name in ('verify_asterion.py','verify_asterion_extension.py',
        'verify_asterion_frontiers.py','verify_asterion_w7_rank_certificates.py',
        'replay_asterion_w7_prior_sectors.py','verify_asterion_w7_integration.py'))
    paths.extend(ROOT/name for name in ('src/perfectjet/weight_seven.py','docs/ASTERION_WEIGHT_SEVEN_LENGTH_THREE.md',
        'docs/INSTALL.md','tests/test_weight_seven_integration.py','.github/workflows/asterion-w7.yml'))
    installed=('asterion_w7_certificates.json','asterion_primitive_certificates.json')
    return {'schema':'perfectjet/asterion-w7-integration/1','source_sha256':sources,
        'kernel_multiplicities':multiplicities,'kernel_dimension':181753,'new_cubic_primitive_multiplicity':0,
        'verification_mode':'Retained exact replay evidence with current source/resource bindings; this report does not execute a fresh lattice replay.',
        'installed_resource_sha256':{name:hashlib.sha256((ROOT/'src/perfectjet/resources'/name).read_bytes()).hexdigest() for name in installed},
        'evidence_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)},
        'scope':'Complete weight-seven length-three kernel only. Quartic, longer-length and full weight-seven primitive classification remain open.',
        'historical_boundary':'Original boundary retains its historical source binding; the fresh prior-sector replay verifies all seven inherited cubic sectors.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    raw=(json.dumps(build(),indent=2,sort_keys=True)+'\n').encode()
    if args.write:RESOURCE.write_bytes(raw)
    elif RESOURCE.read_bytes()!=raw:raise ValueError('stale integration inventory')
    print(json.dumps({'passed':True,'mode':'write' if args.write else 'check','kernel_dimension':181753}))


if __name__=='__main__':main()
