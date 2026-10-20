"""Build and inspect a deterministic, standalone research source archive."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[1]
PREFIX = 'PerfectJet-P521-Provenance/'
NAME = 'PerfectJet-P521-Provenance-v0.1.0.zip'


def source_files():
    files = [p for p in DIRECTORY.rglob('*') if p.is_file()
             and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo')
             and p.name != 'lcg_scan']
    for name in ('LICENSE',):
        if (ROOT/name).is_file():
            files.append(ROOT/name)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def build(destination):
    files = source_files()
    entries = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    manifest = {'schema': 'perfectjet/p521-source-manifest/1', 'research_version': '0.1.0',
                'files': entries}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        payloads = [(e['path'], (ROOT/e['path']).read_bytes()) for e in entries]
        payloads.append(('MANIFEST.json', (json.dumps(manifest, indent=2, sort_keys=True)+'\n').encode()))
        payloads.append(('README.md', (DIRECTORY/'README.md').read_bytes()))
        for path, data in sorted(payloads):
            info = zipfile.ZipInfo(PREFIX+path, (2026, 10, 20, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive CRC check failed')
        for e in entries:
            if hashlib.sha256(archive.read(PREFIX+e['path'])).hexdigest() != e['sha256']:
                raise ValueError('Archive file hash differs: '+e['path'])
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_name(destination.name+'.sha256').write_text(digest+'  '+destination.name+'\n')
    return {'archive': str(destination), 'sha256': digest, 'files': len(entries),
            'bytes': destination.stat().st_size}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'dist'/NAME)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))
