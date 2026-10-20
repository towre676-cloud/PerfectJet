"""A source-supported bit obstruction independent of any RNG recurrence."""
from __future__ import annotations
import json
from pathlib import Path

try:
    from research.p521.curve import P, GX, GY
except ModuleNotFoundError:
    from curve import P, GX, GY


def certificate(target, name):
    if type(target) is not int or not 0 <= target < P:
        raise ValueError('Target must be a canonical field element')
    # Seventeen 31-bit unsigned values stored in 32-bit slots have zero bits
    # at positions31,63,...,543, regardless of the order of those slots.
    total_bits, forbidden_bit = 17*32, 31
    maximum_q = ((1 << total_bits)-1-target)//P
    low = target % (1 << forbidden_bit)
    if not (0 <= maximum_q <= low and (target >> forbidden_bit) & 1):
        raise ValueError('This target has no supplied bit obstruction')
    return {'schema': 'perfectjet/p521-word-obstruction/1', 'coordinate': name,
            'target': hex(target), 'word_count': 17, 'slot_bits': 32, 'value_bits': 31,
            'forbidden_bit': forbidden_bit, 'maximum_quotient': maximum_q,
            'low_bits': low, 'target_bit': 1,
            'conclusion': 'No sequence of seventeen unsigned31-bit words in32-bit slots '
                          'can reduce to this coordinate modulo2^521-1, in either word order.'}


def verify_document(document):
    if not isinstance(document, dict) or document.get('schema') != 'perfectjet/p521-word-suite/1':
        raise ValueError('Invalid word obstruction document')
    expected = [certificate(value, name) for name, value in (('Gx', GX), ('Gy', GY))]
    if document.get('certificates') != expected:
        raise ValueError('Word obstruction differs from exact public-coordinate calculation')
    return {'verified': True, 'coordinate_proofs': 2, 'assembly_cases': 4,
            'scope': 'Seventeen31-bit unsigned values in32-bit slots, either word order, '
                     'direct assembly followed by reduction modulo the P-521 prime.'}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    if args.verify:
        print(json.dumps(verify_document(json.loads(args.verify.read_text())), indent=2))
    else:
        result = {'schema': 'perfectjet/p521-word-suite/1',
                  'certificates': [certificate(value, name) for name, value in (('Gx', GX), ('Gy', GY))]}
        verify_document(result)
        content = json.dumps(result, indent=2, sort_keys=True)+'\n'
        if args.output:
            args.output.write_text(content, encoding='utf-8')
        else:
            print(content, end='')
