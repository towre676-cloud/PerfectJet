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
            release_version = manifest['version']
            assert re.fullmatch(r'\d+\.\d+\.\d+', release_version)
            assert set(names) == {'PerfectJet/'+e['path'] for e in manifest['files']} | {'PerfectJet/MANIFEST.json'}
            for entry in manifest['files']:
                raw = z.read('PerfectJet/'+entry['path'])
                assert len(raw) == entry['size_bytes']
                assert hashlib.sha256(raw).hexdigest() == entry['sha256'], entry['path']
            z.extractall(base)
        root = base/'PerfectJet'
        assert f'version = "{release_version}"' in (root/'pyproject.toml').read_text()
        assert f'__version__ = "{release_version}"' in (root/'src/perfectjet/__init__.py').read_text()
        equations = json.loads((root/'data/equations.json').read_text())['equations']
        original = json.loads((root/'data/equation_id_contract.json').read_text())['sha256_of_canonical_records']
        ids = {e['id'] for e in equations}
        assert len(ids) == len(equations) and len(equations) >= 464
        family_count = len(json.loads((root/'data/equation_power.json').read_text())['families'])
        tool_count = len(list((root/'examples/mathlab').glob('*.json')))
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
import json, sys
from importlib.metadata import version
from perfectjet.mathlab import LABS, catalogue, evaluate
expected_version, expected_equations, expected_families, expected_tools = sys.argv[1:]
assert version('perfectjet') == expected_version
cat = catalogue()
assert len(cat['equations']) == int(expected_equations) and len(cat['families']) == int(expected_families) and len(LABS) == int(expected_tools)
for lab in LABS:
    result = evaluate(dict(operation='math-lab', lab=lab['id'], params=lab['example']['params']))
    assert result['lab'] == lab['id'] and result['scope'] and result['summary']
    json.dumps(result, allow_nan=False)
print(f'Installed wheel: all {len(LABS)} Math Lab tools passed')
'''
        run(str(python), '-c', check, release_version, str(len(equations)), str(family_count), str(tool_count), cwd=base, env=env)
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
            assert len(cat['labs']) == tool_count
            for lab in cat['labs']:
                result = query(dict(operation='math-lab', lab=lab['id'], params=lab['example']['params']))
                assert result['lab'] == lab['id'] and result['scope']
            assert 'python run_observatory.py' in (root/'Start_Math_Lab.bat').read_text()
        finally:
            process.terminate()
            process.communicate(timeout=30)
    print(json.dumps(dict(version=release_version, sha256=expected, manifest_files=len(manifest['files']), equations=len(equations), families=family_count, installed_tools=tool_count, launcher_http_tools=tool_count, desktop_rendering='not checked by this script')))


if __name__ == '__main__':
    main()
