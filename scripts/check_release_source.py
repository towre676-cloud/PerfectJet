"""Bind every archived source byte to the selected Git revision.

Generated outer checksums and MANIFEST.json are checked by the builder/verifier;
all manifest members must be tracked and byte-identical to HEAD. No Git metadata
is required to use an extracted distribution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from build_release import ROOT, eligible


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    expected = {p for p in tracked if p and eligible(ROOT / p)}
    with zipfile.ZipFile(args.archive) as archive:
        manifest = json.loads(archive.read('PerfectJet/MANIFEST.json'))
        entries = {entry['path']: entry for entry in manifest['files']}
        assert set(entries) == expected, (set(entries) - expected, expected - set(entries))
        for name, entry in entries.items():
            committed = subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT)
            assert hashlib.sha256(committed).hexdigest() == entry['sha256'], name
            assert archive.read('PerfectJet/' + name) == committed, name
    print(json.dumps({'source_commit': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        'tracked_archive_files': len(entries), 'source_bytes_match': True}))


if __name__ == '__main__':
    main()
