"""Replay the recovered theorem in isolation; never publish or alter the API.

The checkout must contain the byte-identical PR16 import. Outputs are written
to --output; all mathematical regeneration takes place in a temporary copy.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RECOVERY = ROOT / 'research/week-2026-11-05'
PREFIX = 'asterion-complete-weight7/Asterion_Research_Advance/'


def prepare(destination):
    manifest = json.loads((RECOVERY / 'IMPORT_MANIFEST.json').read_text())
    selected = [r for r in manifest['files'] if r['path'].startswith(PREFIX)]
    if not selected:
        raise ValueError('missing recovered E8 source inventory')
    records = json.loads((RECOVERY / 'COMPRESSED_EVIDENCE.json').read_text())
    compressed = {r['path']: r for r in records}
    bindings = {}
    for row in selected:
        relative = Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('unsafe inventory path')
        if row['path'] in compressed:
            item = compressed[row['path']]
            stored = (RECOVERY / item['stored_path']).read_bytes()
            if hashlib.sha256(stored).hexdigest() != item['stored_sha256']:
                raise ValueError('changed compressed input: ' + item['stored_path'])
            raw = gzip.decompress(stored)
            if len(raw) != item['original_size'] or hashlib.sha256(raw).hexdigest() != item['original_sha256']:
                raise ValueError('corrupt restored evidence: ' + row['path'])
        else:
            raw = (RECOVERY / relative).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if len(raw) != row['size'] or digest != row['sha256']:
            raise ValueError('changed imported input: ' + str(relative))
        target = destination / relative.relative_to(PREFIX.rstrip('/'))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        bindings[str(relative)] = digest
    for row in records:
        if not row['path'].startswith(PREFIX):
            continue
        stored = destination / Path(row['stored_path']).relative_to(PREFIX.rstrip('/'))
        raw = gzip.decompress(stored.read_bytes())
        if len(raw) != row['original_size'] or hashlib.sha256(raw).hexdigest() != row['original_sha256']:
            raise ValueError('corrupt restored evidence: ' + row['path'])
        target = destination / Path(row['path']).relative_to(PREFIX.rstrip('/'))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return bindings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check-inputs', action='store_true', help='integrity only; does not verify the theorem')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    summary = {'checkout_commit': commit, 'replay_completed': False,
               'installed_package_verified': False, 'publication_authorized': False}
    with tempfile.TemporaryDirectory(prefix='perfectjet-weight7-') as temporary:
        scratch = Path(temporary)
        summary['input_sha256'] = prepare(scratch)
        if args.check_inputs:
            summary['mode'] = 'input-integrity-only'
            (output / 'audit-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
            return
        summary['mode'] = 'complete-research-replay'
        env = dict(os.environ, PYTHONUTF8='1')
        with (output / 'replay.log').open('w') as log:
            result = subprocess.run([sys.executable, '-u', 'replay.py', '--weight7', '--tests'],
                                    cwd=scratch, env=env, stdout=log, stderr=subprocess.STDOUT)
        summary['exit_code'] = result.returncode
        summary['replay_completed'] = result.returncode == 0
        for path in scratch.glob('*.json'):
            shutil.copy2(path, output / path.name)
        (output / 'audit-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
