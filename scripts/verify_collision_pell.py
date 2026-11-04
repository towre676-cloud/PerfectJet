"""Deterministically regenerate the source-bound collision/Pell research record."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def build():
    from perfectjet.collision_research import evaluate, json_value
    from perfectjet.collision_four import receipt as four_receipt
    from perfectjet.collision_norm import collision_norm, norm_classification_theorem
    from perfectjet.collision_projection import projection_classification_theorem, collision_projection
    from perfectjet.collision_zeta import conductor_two_values
    from perfectjet.mathlab import catalogue, evaluate as lab
    values = conductor_two_values(100000)
    requests = [
        {'operation':'report','order':32,'index':str(10**100+1),'limit':10000},
        {'operation':'pell','index':str(10**100+12345),'modulus':1000000007},
        {'operation':'constants','prime_cutoff':10000,'s':2},
        {'operation':'extract','order':6},
        {'operation':'projection','conductor':4,'order':24},
        {'operation':'population','conductor':6,'residue':0,'factorization':[[2,4],[3,3],[5,2]],'rank':7},
        {'operation':'population','conductor':2,'exponent':str(10**100),'residue':0},
    ]
    card = next(row for row in catalogue()['labs'] if row['id']=='collision')
    samples = [card['request_schema']['sample_params']]+card['request_schema']['additional_samples']
    return json_value({
        'schema':'perfectjet/collision-replay/1',
        'norm_theorem':norm_classification_theorem(),
        'prime_local_projection_theorem':projection_classification_theorem(),
        'norm_checkpoints':[collision_norm(n).report() for n in range(1,13)],
        'projection_checkpoints':[collision_projection(n).report() for n in range(1,33)],
        'fourth_power_transport':four_receipt(),
        'queries':[{'request':request,'answer':evaluate(request)} for request in requests],
        'summatory_counts':{str(n):sum(values[:n+1]) for n in (10,100,1000,10000,100000)},
        'lab_samples':[lab({'lab':'collision','params':sample}) for sample in samples],
        'scope':'Exact executable identities plus separately written all-conductor proofs. Classical Estermann input is attributed. No Lean, worldwide-priority, single-complex-phase-product or empirical-performance claim.',
    })


def sources():
    paths = ['src/perfectjet/collision.py','src/perfectjet/rings.py',
             'src/perfectjet/cli.py','src/perfectjet/mathlab.py',
             'docs/chapters/39_collision_pell_and_analytic_boundaries.md',
             'research/collision_pell/README.md','research/collision_pell/explorer.html',
             'scripts/verify_collision_pell.py','scripts/build_collision_catalogue.py',
             'scripts/check_collision_explorer.cjs','data/collision_equations.json']
    paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'src/perfectjet').glob('collision_*.py')]
    paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'tests').glob('test_collision*.py')]
    paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'docs').glob('COLLISION_*.md')]
    return {path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in sorted(set(paths))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    report = build()
    encoded = json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
    manifest = {'schema':'perfectjet/collision-source-manifest/1','source_sha256':sources(),
                'validation_sha256':hashlib.sha256(encoded.encode()).hexdigest()}
    destination = ROOT/'results/collision-pell'
    destination.mkdir(parents=True,exist_ok=True)
    records = {'validation.json':encoded,'manifest.json':json.dumps(manifest,indent=2)+'\n'}
    for name,content in records.items():
        path = destination/name
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != content:
                raise ValueError('stale collision replay: '+name)
        else:
            path.write_text(content,encoding='utf-8')
    print(json.dumps({'status':'passed','mode':'check' if args.check else 'build',
                      'norm_conductors':12,'projection_conductors':32,'public_queries':7,
                      'lab_samples':len(report['lab_samples']),'source_files':len(manifest['source_sha256'])}))


if __name__=='__main__':
    main()
