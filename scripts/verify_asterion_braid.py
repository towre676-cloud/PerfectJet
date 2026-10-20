"""Rebuild or independently replay source-bound half-braid certificates."""
import argparse
import hashlib
import json
from pathlib import Path
from perfectjet.kz_half_braid import braid_receipt

ROOT=Path(__file__).resolve().parents[1]
SOURCES=('src/perfectjet/kz_half_braid.py','src/perfectjet/asterion_kz.py',
         'src/perfectjet/asterion_monodromy.py','src/perfectjet/rings.py',
         'src/perfectjet/asterion_e8.py','scripts/verify_asterion_braid.py',
         'docs/ASTERION_HALF_BRAID.md','scripts/build_asterion_braid_catalogue.py',
         'data/asterion_braid_equations.json')

def payloads():
    receipt=braid_receipt(exhaustive=True)
    if not receipt['passed']:
        raise ArithmeticError('half-braid certificate did not pass')
    raw=(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    manifest={'schema':'perfectjet/asterion-half-braid-ledger/1',
        'sources':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
        'certificates':{'certificate.json':{'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}},
        'proved':['linear B3 extension of the declared pure-loop pair',
            'exact cyclotomic braid and central identities','Tuba--Wenzl simple equivalence class',
            'common character twist with trivial center and determinant'],
        'open':['explicit same-chart algebraic conjugator','canonical endpoint associator',
            'kernel of the triangle-group representation','presentation of the countable dense image'],
        'proof_dependency':'classical KZ descent and Tuba--Wenzl classification; no Lean formalization or priority claim'}
    return {'certificate.json':raw,'manifest.json':(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    p.add_argument('--output',type=Path,default=ROOT/'results/asterion-half-braid')
    args=p.parse_args()
    data=payloads()
    if not args.check:
        args.output.mkdir(parents=True,exist_ok=True)
    for name,raw in data.items():
        path=args.output/name
        if args.check:
            if not path.is_file() or path.read_bytes()!=raw:
                raise ValueError('stale or corrupted half-braid certificate: '+str(path))
        else:
            path.write_bytes(raw)
    print(json.dumps({'passed':True,'mode':'check' if args.check else 'write','files':len(data)}))

if __name__=='__main__':
    main()
