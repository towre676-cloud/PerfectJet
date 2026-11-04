"""Recover byte-identical receipts from an immutable, independently replayed run.

The source run completed all mathematical replays and all 936 tests; its
subsequent wheel-install check failed because pip inherited PYTHONPATH.
No expected certificate hash is changed by this recovery. Each reconstructed
receipt must match the exact SHA256 recorded by that completed replay.
Only the integration inventory's workflow-file hash changes for the pip fix.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from perfectjet.asterion import source_digests

ROOT=Path(__file__).resolve().parents[1]
SOURCE_RUN=41857689251
SOURCE_HEAD='142b93688e553aaf08c3cc785e2ededa1168e226'
REPO='towre676-cloud/PerfectJet'
WORKFLOW='.github/workflows/asterion-w7.yml'
RESOURCE='src/perfectjet/resources/asterion_w7_integration.json'
AUDIT='results/asterion-primitives/w7-provenance-audit.json'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def rebind(value,sources):
    if isinstance(value,dict):return {k:(sources if k=='source_sha256' else rebind(v,sources)) for k,v in value.items()}
    if isinstance(value,list):return [rebind(v,sources) for v in value]
    return value


def encoded(value,folder,compressed=False):
    raw=(json.dumps(value,indent=2,sort_keys=True,allow_nan=False,ensure_ascii=folder=='asterion')+'\n').encode()
    if compressed:
        raw=gzip.compress(raw,mtime=0)
        raw=raw[:9]+b'\xff'+raw[10:]
    return raw


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifact',type=Path)
    args=parser.parse_args()
    run=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/actions/runs/{SOURCE_RUN}']))
    if run['head_sha']!=SOURCE_HEAD:raise ValueError('wrong replay source commit')
    jobs=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/actions/runs/{SOURCE_RUN}/jobs']))['jobs']
    steps={s['name']:s['conclusion'] for j in jobs for s in j['steps']}
    for name in ('Rebuild all publication certificates mathematically before rebinding',
                 'Independently replay exact cubic evidence and source null lift',
                 'Complete regression suite with strict provenance tests unchanged'):
        if steps.get(name)!='success':raise ValueError('source replay did not pass: '+name)
    if steps.get('Verify installed theorem outside the checkout')!='failure':
        raise ValueError('unexpected source installation-check result')
    log=(args.artifact/'verification/full-regression.log').read_text()
    if 'Ran 936 tests' not in log or not log.rstrip().endswith('OK'):
        raise ValueError('missing successful full regression evidence')
    permitted={WORKFLOW,'scripts/recover_asterion_w7_verified_receipts.py'}
    changed=set(subprocess.check_output(['git','diff','--name-only',SOURCE_HEAD,'HEAD'],cwd=ROOT).decode().splitlines())
    if changed-permitted:raise ValueError('other code changed since the replay: '+repr(changed-permitted))
    original=read(args.artifact/RESOURCE)
    sources=source_digests()
    if original['source_sha256']!=sources:raise ValueError('mathematical source hashes changed')
    evidence=original['evidence_sha256']
    for folder in ('asterion','asterion-extension','asterion-frontiers'):
        base=ROOT/'results'/folder
        manifest=read(base/'manifest.json')
        for name in manifest['files']:
            path=base/name;relative=path.relative_to(ROOT).as_posix()
            if sha(path.read_bytes())!=evidence[relative]:
                raw=encoded(rebind(read(path),sources),folder,path.suffix=='.gz')
                if sha(raw)!=evidence[relative]:raise ValueError('recovered bytes differ from verified replay: '+relative)
                path.write_bytes(raw)
        manifest=rebind(manifest,sources)
        for name in manifest['files']:
            raw=(base/name).read_bytes()
            manifest['files'][name]={'bytes':len(raw),'sha256':sha(raw)}
        raw=encoded(manifest,folder)
        relative=(base/'manifest.json').relative_to(ROOT).as_posix()
        if sha(raw)!=evidence[relative]:raise ValueError('manifest differs from verified replay: '+relative)
        (base/'manifest.json').write_bytes(raw)
    shutil.copyfile(args.artifact/AUDIT,ROOT/AUDIT)
    shutil.copyfile(args.artifact/RESOURCE,ROOT/RESOURCE)
    for name,expected in evidence.items():
        if name==WORKFLOW:continue
        if sha((ROOT/name).read_bytes())!=expected:raise ValueError('verified evidence changed: '+name)
    subprocess.run(['python','scripts/verify_asterion_w7_integration.py','--write'],cwd=ROOT,check=True)
    current=read(ROOT/RESOURCE)
    normalized=copy.deepcopy(current)
    normalized['evidence_sha256'][WORKFLOW]=original['evidence_sha256'][WORKFLOW]
    if normalized!=original:raise ValueError('integration inventory changed beyond the workflow repair')
    subprocess.run(['python','scripts/verify_asterion_w7_integration.py'],cwd=ROOT,check=True)
    print(json.dumps({'passed':True,'source_run':SOURCE_RUN,'source_head':SOURCE_HEAD,
        'recovered_receipts_match_verified_sha256':True,'mathematical_sources_unchanged':True,
        'prior_full_regression_tests':936,'inventory_change':'workflow-file hash only'}))


if __name__=='__main__':main()
