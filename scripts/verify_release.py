"""Verify a release ZIP, install its wheel in isolation, and exercise its launcher.

Run from outside the extracted tree. Requires pip/setuptools/wheel only to build;
the installed Math Lab has no third-party runtime dependencies.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.request
import venv
import zipfile


def run(*args, cwd, env=None):
    subprocess.run(args, cwd=cwd, env=env, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    archive = args.archive.resolve()
    expected = archive.with_suffix(archive.suffix+'.sha256').read_text().split()[0]
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected, 'ZIP checksum mismatch'
    with tempfile.TemporaryDirectory(prefix='perfectjet-release-') as tmp:
        base = Path(tmp)
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            assert len(names) == len(set(names))
            assert z.testzip() is None
            assert all(n.startswith('PerfectJet/') and '..' not in Path(n).parts and '\\' not in n for n in names)
            manifest = json.loads(z.read('PerfectJet/MANIFEST.json'))
            assert manifest['version'] == '0.17.0'
            assert set(names) == {'PerfectJet/'+e['path'] for e in manifest['files']} | {'PerfectJet/MANIFEST.json'}
            for entry in manifest['files']:
                raw = z.read('PerfectJet/'+entry['path'])
                assert len(raw) == entry['size_bytes']
                assert hashlib.sha256(raw).hexdigest() == entry['sha256'], entry['path']
            z.extractall(base)
        root = base/'PerfectJet'
        assert 'version = "0.17.0"' in (root/'pyproject.toml').read_text()
        assert '__version__ = "0.17.0"' in (root/'src/perfectjet/__init__.py').read_text()
        equations = json.loads((root/'data/equations.json').read_text())['equations']
        original = json.loads((root/'data/equation_id_contract.json').read_text())['sha256_of_canonical_records']
        ids = {e['id'] for e in equations}
        assert len(ids) == len(equations) == 464
        for e in equations:
            if e['id'] in original:
                assert hashlib.sha256(json.dumps(e, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest() == original[e['id']]
        assert set(original) <= ids
        run(sys.executable, 'scripts/check_coverage.py', cwd=root)
        env = os.environ.copy()
        env.pop('PYTHONPATH', None)
        env['BROWSER'] = 'true'  # HTTP is checked below; desktop rendering is separate.
        wheels = base/'wheels'
        run(sys.executable, '-m', 'pip', 'wheel', '--no-deps', '--no-build-isolation', '--wheel-dir', str(wheels), str(root), cwd=base, env=env)
        venv.EnvBuilder(with_pip=True).create(base/'venv')
        python = base/'venv'/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        run(str(python), '-m', 'pip', 'install', '--no-index', '--no-deps', str(next(wheels.glob('*.whl'))), cwd=base, env=env)
        check = '''
import json
from importlib.metadata import version
from perfectjet.mathlab import LABS, catalogue, evaluate
assert version('perfectjet') == '0.17.0'
cat = catalogue()
assert len(cat['equations']) == 464 and len(cat['families']) == 24 and len(LABS) == 25
for lab in LABS:
    result = evaluate(dict(operation='math-lab', lab=lab['id'], params=lab['example']['params']))
    assert result['lab'] == lab['id'] and result['scope'] and result['summary']
    json.dumps(result, allow_nan=False)
print('Installed wheel: all 25 Math Lab tools passed')
'''
        run(str(python), '-c', check, cwd=base, env=env)
        # Invoke the actual supplied source launcher with an isolated interpreter.
        process = subprocess.Popen([str(python), str(root/'run_observatory.py'), '--port', '0'], cwd=base, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            line = process.stdout.readline()
            url = re.search(r'http://127\.0\.0\.1:\d+', line).group()
            with urllib.request.urlopen(url, timeout=30) as response:
                page = response.read().decode()
            assert 'id="mathLabView"' in page and 'id="atlasSearch"' in page
            token = page.split("token='")[1].split("'")[0]
            def query(payload):
                req = urllib.request.Request(url+'/api/evaluate', json.dumps(payload).encode(), {'Content-Type':'application/json', 'X-Observatory-Token':token})
                with urllib.request.urlopen(req, timeout=120) as response:
                    return json.load(response)
            cat = query({'operation':'math-catalog'})
            assert len(cat['labs']) == 25
            for lab in cat['labs']:
                result = query(dict(operation='math-lab', lab=lab['id'], params=lab['example']['params']))
                assert result['lab'] == lab['id'] and result['scope']
            assert 'python run_observatory.py' in (root/'Start_Math_Lab.bat').read_text()
        finally:
            process.terminate()
            process.communicate(timeout=30)
    print(json.dumps(dict(version='0.17.0', sha256=expected, manifest_files=len(manifest['files']), equations=464, families=24, installed_tools=25, launcher_http_tools=25, desktop_rendering='not checked by this script')))


if __name__ == '__main__':
    main()
