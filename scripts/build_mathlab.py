"""Generate the installed equation atlas and reusable computed lab requests."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(check=False):
    equations = json.loads((ROOT/'data/equations.json').read_text())
    power = json.loads((ROOT/'data/equation_power.json').read_text())
    ids = [e['id'] for e in equations['equations']]
    if len(ids) != len(set(ids)) or set(ids) != set(power['assignments']):
        raise ValueError('every stable equation ID needs exactly one family assignment')
    resources = ROOT/'src/perfectjet/resources'
    resources.mkdir(exist_ok=True)
    expected = {'equations.json': equations, 'equation_power.json': power}
    discoveries = ROOT/'docs/ASTERION_DISCOVERIES.json'
    if discoveries.is_file():
        expected['asterion_discoveries.json'] = json.loads(discoveries.read_text())
    for name, content in expected.items():
        path = resources/name
        encoded = json.dumps(content, indent=2, ensure_ascii=False)+'\n'
        if check:
            if not path.is_file() or path.read_text() != encoded:
                raise ValueError(f'stale installed resource {name}; run scripts/build_mathlab.py')
        else:
            path.write_text(encoded, encoding='utf-8')
    from perfectjet.mathlab import LABS
    examples = ROOT/'examples/mathlab'
    examples.mkdir(parents=True, exist_ok=True)
    for lab in LABS:
        request = {'operation': 'math-lab', 'lab': lab['id'], 'params': lab['example']['params']}
        path = examples/(lab['id']+'.json')
        encoded = json.dumps(request, indent=2)+'\n'
        if check:
            if not path.is_file() or path.read_text() != encoded:
                raise ValueError(f'stale example {lab["id"]}')
        else:
            path.write_text(encoded)
    print(json.dumps({'equations': len(ids), 'families': len(power['families']), 'callable_tools': len(LABS), 'mode': 'check' if check else 'build'}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
