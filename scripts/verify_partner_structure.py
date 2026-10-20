#!/usr/bin/env python3
"""Recompute the all-degree sextic polynomial certificates with source hashes."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from perfectjet.partner_structure import receipt


def build():
    result = receipt()
    files = ['src/perfectjet/partner_structure.py', 'tests/test_partner_structure.py',
             'scripts/verify_partner_structure.py', 'docs/PARTNER_STRUCTURE.md',
             'src/perfectjet/polynomial.py', 'src/perfectjet/transvectants.py']
    result['source_sha256'] = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}
    target = ROOT/'results/partner_structure.json'
    target.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    return result


if __name__ == '__main__':
    result = build()
    print(json.dumps({'schema': result['schema'], 'symbolic_resultants': len(result['rows']),
                      'status': 'all exact identities passed', 'receipt': 'results/partner_structure.json'}))
