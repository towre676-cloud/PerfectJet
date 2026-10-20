"""One-command, dependency-free verification of the public P-521 study."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.p521.curve import arithmetic_checks
from research.p521.known_controls import run_controls
from research.p521.verify_certificate import verify_document as verify_freelip
from research.p521.word_obstruction import verify_document as verify_words


def verify():
    from research.p521.verify_lcg_certificate import verify_document as verify_lcg
    directory = Path(__file__).resolve().parent
    arithmetic = arithmetic_checks()
    if not all(arithmetic[k] for k in ('field_modulus_is_prime_lucas_lehmer',
               'base_point_on_curve', 'standard_order_annihilates_base_point', 'base_point_nonzero')):
        raise ArithmeticError('Public curve arithmetic failed')
    if not arithmetic['seed_provenance']['matches_standard']:
        raise ArithmeticError('Previously published seed recipe failed')
    historical = run_controls()
    if not historical['all_pass']:
        raise ArithmeticError('Previously explained base-point controls failed')
    inputs = {}
    proofs = {}
    for name, checker in (('freelip-recovery.json', verify_freelip),
                          ('freelip-source-recovery.json', verify_freelip),
                          ('lcg_forensics.json', verify_lcg),
                          ('word-obstructions.json', verify_words)):
        path = directory/'results'/name
        encoded = path.read_bytes()
        inputs[name] = hashlib.sha256(encoded).hexdigest()
        proofs[name] = checker(json.loads(encoded))
    return {'schema': 'perfectjet/p521-research-verification/1',
            'research_version': '0.1.0', 'verified': True,
            'target': 'Public P-521 base-point provenance',
            'public_arithmetic': arithmetic,
            'previously_explained_base_points': historical,
            'proofs': proofs, 'receipt_sha256': inputs,
            'conclusion': 'Declared FreeLIP and lrand48 generator/assembly families are excluded.',
            'open': 'The historical P-521 base-point generation recipe remains unknown.',
            'security_claim': 'No private-key recovery, ECDLP algorithm or security break established.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify all retained certificates (the default)')
    parser.add_argument('--output', type=Path, help='Save the exact verification summary')
    args = parser.parse_args(argv)
    result = verify()
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding='utf-8')
    else:
        print(encoded, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
