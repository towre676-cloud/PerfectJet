"""Independent integer-only verifier for the fixed P-521 LCG research receipt.

No discovery module, lattice solver, or third-party Python package is imported.
The native exhaustive search can be rerun explicitly with --rerun-native.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

M = 1 << 48
A = 0x5DEECE66D
C = 11
FIELD = (1 << 521) - 1
COORDINATES = {
    'Gx': int('c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3d'
              'baa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66', 16),
    'Gy': int('11839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c'
              '97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650', 16),
}
SEED = 'd09e8800291cb85396cc6717393284aaa0da64ba'
TIMESTAMP = 871002724


class ProofError(ValueError):
    pass


def require(value, message):
    if not value:
        raise ProofError(message)


def advance(state):
    return (A*state+C) % M


def top_outputs(state, width, length):
    result = []
    for _ in range(length):
        result.append(state >> (48-width))
        state = advance(state)
    return result


def proof_interval(data, coefficients):
    """Bound an annihilating functional over every compatible state box."""
    require(isinstance(data, bytes) and len(data) == 20, 'need exactly twenty observed bytes')
    require(isinstance(coefficients, list) and len(coefficients) == len(data)
            and all(type(x) is int for x in coefficients), 'invalid integer relation')
    require(sum(q*pow(A, i, M) for i, q in enumerate(coefficients)) % M == 0,
            'relation does not annihilate the recurrence')
    offset, lower, upper = 0, 0, 0
    for byte, q in zip(data, coefficients):
        ends = (q*((byte << 40)-offset), q*(((byte+1) << 40)-1-offset))
        lower += min(ends)
        upper += max(ends)
        offset = advance(offset)
    return lower, upper


def verify_dual(proof, expected_data):
    require(isinstance(proof, dict) and proof.get('schema') == 'perfectjet/lcg-dual-exclusion/1',
            'unsupported dual certificate')
    require(proof.get('observation_hex') == expected_data.hex(), 'wrong public observation')
    lo, hi = proof_interval(expected_data, proof.get('coefficients'))
    require(type(proof.get('interval_lower')) is int and proof['interval_lower'] == lo,
            'incorrect dual lower bound')
    require(type(proof.get('interval_upper')) is int and proof['interval_upper'] == hi,
            'incorrect dual upper bound')
    require(-((-lo)//M) > hi//M, 'dual interval contains a possible lattice multiple')


def native_queries():
    """Rebuild the exact native workload independently of the scanner wrapper."""
    queries = []
    for _, coordinate in COORDINATES.items():
        encoded = coordinate.to_bytes(66, 'big')
        for representation in (encoded, encoded[::-1]):
            text = ''.join(format(byte, '08b') for byte in representation)
            for width, stride in ((31, 31), (32, 32), (31, 32)):
                for start in range(529-4*stride):
                    words = [int(text[start+j*stride:start+(j+1)*stride], 2) for j in range(4)]
                    if width == 31 and stride == 32 and any(word >= 1 << 31 for word in words):
                        continue
                    queries.append((width, words))
    state = advance((TIMESTAMP << 16) | 0x330E)
    controls = [(width, top_outputs(state, width, 6)) for width in (31, 32)]
    payload = ''.join(f'{width} {len(words)} '+ ' '.join(map(str, words))+'\n'
                      for width, words in queries+controls)
    return queries, controls, state, payload


def verify_native_metadata(report, rerun=False):
    queries, controls, state, payload = native_queries()
    require(len(queries) == 3302, 'independent query construction count changed')
    require(report.get('traces') == len(queries), 'wrong native trace count')
    require(report.get('observations_per_trace') == 4, 'wrong native observation count')
    count = sum(1 << (48-width) for width, _ in queries)
    require(count == 327680000 and report.get('states_enumerated') == count,
            'wrong exhaustive first-state count')
    require(report.get('query_sha256') == hashlib.sha256(payload.encode()).hexdigest(),
            'native query digest mismatch')
    require(report.get('matches') == [], 'receipt has native matches')
    rows = report.get('controls')
    require(isinstance(rows, list) and len(rows) == 2, 'missing native controls')
    for row, (width, words) in zip(rows, controls):
        require(row.get('output_bits') == width and row.get('words') == words
                and row.get('expected_state') == state and row.get('states') == [state]
                and row.get('passed') is True, 'native inverse control mismatch')
    if rerun:
        with tempfile.TemporaryDirectory(prefix='p521-independent-lcg-') as tmp:
            binary = Path(tmp)/'scan'
            source = Path(__file__).with_name('lcg_scan.cpp')
            subprocess.run(['c++', '-std=c++17', '-O3', str(source), '-o', str(binary)], check=True)
            output = subprocess.run([str(binary)], input=payload, text=True,
                                    capture_output=True, check=True).stdout.splitlines()
        require(len(output) == len(queries)+2, 'native result count differs')
        require(all(line == '0' for line in output[:-2]), 'native scan found a match')
        require(output[-2:] == [f'1 {state}', f'1 {state}'], 'rerun native controls failed')
    return {'traces': len(queries), 'first_states': count, 'exhaustive_search_rerun': rerun}


def verify_document(document, rerun_native=False):
    require(isinstance(document, dict)
            and document.get('schema') == 'perfectjet/p521-lcg-forensics/1', 'unsupported receipt')
    state = (TIMESTAMP << 16) | 0x330E
    first_state = None
    emitted = []
    for index in range(20*1136):
        state = advance(state)
        if index >= 20*1135:
            if first_state is None:
                first_state = state
            emitted.append(state >> 40)
    require(bytes(emitted).hex() == SEED, 'independent public seed replay failed')
    require(document.get('seed_forward_control') == SEED.upper(), 'seed receipt mismatch')
    expected_windows = {}
    for name, coordinate in COORDINATES.items():
        blob = coordinate.to_bytes(66, 'big')
        for order, representation in (('big', blob), ('reversed', blob[::-1])):
            for offset in range(47):
                expected_windows[name, order, offset] = representation[offset:offset+20]
    top = document.get('top_bytes', {})
    require(top.get('traces') == 188 and top.get('exactly_excluded_traces') == 188,
            'wrong byte trace count')
    seen = set()
    for row in top.get('dual_exclusion_certificates', []):
        key = row.get('coordinate'), row.get('byte_order'), row.get('byte_offset')
        require(key not in seen and key in expected_windows, 'duplicate or unknown byte trace')
        require(type(key[2]) is int, 'invalid byte offset')
        verify_dual(row.get('certificate'), expected_windows[key])
        seen.add(key)
    require(seen == set(expected_windows), 'byte trace certificate coverage incomplete')
    require(top.get('matches') == [], 'byte scan contains a match')
    control = top.get('positive_control', {})
    require(control.get('curve') == 'P-521' and control.get('first_state') == first_state
            and control.get('timestamp') == TIMESTAMP and control.get('candidate') == 1136,
            'byte inverse positive control mismatch')
    require(control.get('recovered_initialization') ==
            {'timestamp': TIMESTAMP, 'distance_before_first_output': 22701},
            'inverse initialization distance mismatch')
    assembly = document.get('byte_assembly', {})
    require(assembly.get('min_raw_bytes') == 65 and assembly.get('max_raw_bytes') == 110,
            'wrong declared assembly byte range')
    require(assembly.get('uncovered') == [{'coordinate': 'Gx', 'raw_bytes': 110},
                                         {'coordinate': 'Gy', 'raw_bytes': 110}],
            'incorrect unresolved assembly boundaries')
    expected_assembly = {(name, size, order) for name in COORDINATES
                         for size in range(65, 110) for order in ('big', 'little')}
    assembly_seen, proofs = set(), 0
    for row in assembly.get('certificates', []):
        name, size = row.get('coordinate'), row.get('raw_bytes')
        require(name in COORDINATES and type(size) is int and 65 <= size <= 109,
                'assembly row lies outside fixed research contract')
        target = COORDINATES[name]
        if row.get('reason') == 'raw_range_below_coordinate':
            require((1 << (8*size))-1 < target, 'invalid direct range exclusion')
            keys = [(name, size, order) for order in ('big', 'little')]
        else:
            require(row.get('schema') == 'perfectjet/p521-byte-assembly-exclusion/1',
                    'wrong assembly certificate schema')
            order, low = row.get('byte_order'), row.get('window_low_bit')
            require(order in ('big', 'little') and type(low) is int and low >= 0 and low % 8 == 0
                    and low+160 <= min(521, 8*size), 'invalid interior byte window')
            qmax = (((1 << (8*size))-1)-target)//FIELD
            require(type(row.get('maximum_quotient')) is int
                    and row['maximum_quotient'] == qmax and qmax >= 0, 'wrong quotient upper bound')
            require(target % (1 << low) >= qmax, 'interior window can change under reduction')
            data = ((target >> low) & ((1 << 160)-1)).to_bytes(20, 'big')
            if order == 'little':
                data = data[::-1]
            verify_dual(row.get('dual_certificate'), data)
            keys = [(name, size, order)]
        require(all(key not in assembly_seen for key in keys), 'duplicate assembly coverage')
        assembly_seen.update(keys)
        proofs += 1
    require(assembly_seen == expected_assembly and proofs == 179,
            'full assembly certificate coverage incomplete')
    native = verify_native_metadata(document.get('top_bits', {}), rerun_native)
    return {'verified': True, 'byte_trace_proofs': len(seen), 'assembly_proof_rows': proofs,
            'assembly_coordinate_order_cases': len(assembly_seen),
            'scope': 'Consecutive POSIX LCG top8 bytes, stated assembly and mod(2^521-1) only.',
            'native': native}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipt', nargs='?', type=Path,
                        default=Path(__file__).with_name('results')/'lcg_forensics.json')
    parser.add_argument('--rerun-native', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = verify_document(json.loads(args.receipt.read_text()), args.rerun_native)
    except (ProofError, KeyError, TypeError, ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f'Certificate rejected: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
