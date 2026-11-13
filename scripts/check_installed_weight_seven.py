"""Build and test a wheel in an isolated virtual environment outside the checkout."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv

ROOT = Path(__file__).resolve().parents[1]


def main():
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    with tempfile.TemporaryDirectory(prefix='perfectjet-installed-w7-') as directory:
        scratch = Path(directory)
        source = scratch / 'source'
        shutil.copytree(ROOT / 'src', source / 'src',
                        ignore=shutil.ignore_patterns('__pycache__', '*.egg-info'))
        shutil.copyfile(ROOT / 'pyproject.toml', source / 'pyproject.toml')
        subprocess.run([sys.executable, '-I', '-m', 'pip', 'wheel', '--no-deps',
                        '--no-build-isolation', '--wheel-dir', str(scratch), str(source)], cwd=scratch, env=env, check=True)
        wheel, = scratch.glob('*.whl')
        environment = scratch / 'venv'
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        subprocess.run([str(python), '-I', '-m', 'pip', 'install', '--no-index',
                        '--no-deps', str(wheel)], cwd=scratch, env=env, check=True)
        for module in ('weight_seven', 'complete_weight_seven'):
            subprocess.run([str(python), '-I', '-m', 'perfectjet.' + module],
                           cwd=scratch, env=env, check=True, stdout=subprocess.DEVNULL)
        checks = scratch / 'checks'
        checks.mkdir()
        for name in ('test_weight_seven_integration.py', 'test_complete_weight_seven.py',
                     'test_asterion_lattice_projection4.py'):
            shutil.copyfile(ROOT / 'tests' / name, checks / name)
        subprocess.run([str(python), '-I', '-m', 'unittest', 'discover', '-s', str(checks), '-v'],
                       cwd=scratch, env=env, check=True)


if __name__ == '__main__':
    main()
