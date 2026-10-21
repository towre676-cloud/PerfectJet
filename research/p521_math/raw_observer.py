"""Sharp raw-state observers and optimal bounded-error recovery for FreeLIP.

The retained certificates are checked with the Python standard library. LLL is
used only by ``build_suite`` to discover an integer basis. This module observes
the current raw state before advancing; it does not model rejected draws.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

M = (1 << 107) - 1
A = pow(3, 121, M)
B = 1 << 26
U = (M-1)//B
HORIZON = 9
RECEIPT = Path(__file__).with_name('results')/'raw-observer.json'
COLLISION_STATES = (122758394145529637777561808240313,
                    50140205173557533948874584981177)


def raw_outputs(state, count):
    """Observe current state, then advance by one raw recurrence step."""
    if type(state) is not int or not 0 <= state < M:
        raise ValueError('State must be a canonical residue modulo M')
    if type(count) is not int or count < 0:
        raise ValueError('Count must be a nonnegative integer')
    answer = []
    for _ in range(count):
        answer.append(state % B)
        state = A*state % M
    return answer


def _inverse_and_determinant(rows):
    """Independent exact Gauss-Jordan arithmetic, with no reduction library."""
    n = len(rows)
    work = [[Fraction(v) for v in row] + [Fraction(i == j) for j in range(n)]
            for i, row in enumerate(rows)]
    determinant = Fraction(1)
    for column in range(n):
        pivot = next((i for i in range(column, n) if work[i][column]), None)
        if pivot is None:
            raise ValueError('Singular certificate basis')
        if pivot != column:
            work[pivot], work[column] = work[column], work[pivot]
            determinant = -determinant
        divisor = work[column][column]
        determinant *= divisor
        work[column] = [v/divisor for v in work[column]]
        for i in range(n):
            if i != column:
                factor = work[i][column]
                work[i] = [v-factor*w for v, w in zip(work[i], work[column])]
    return [row[n:] for row in work], determinant


def _fraction_record(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def _normalized(times):
    return tuple(t-times[0] for t in times)


def required_patterns(horizon=HORIZON):
    """Time translation identifies identical difference-lattice problems."""
    if type(horizon) is not int or not 5 <= horizon <= HORIZON:
        raise ValueError('Supported certified horizons are five through nine')
    return {_normalized(times) for times in combinations(range(horizon), 5)}


@lru_cache(maxsize=256)
def _check_basis(times, rows):
    if len(times) != 5 or times[0] != 0 or tuple(sorted(set(times))) != times:
        raise ValueError('Need five distinct normalized observation times')
    if times[-1] >= HORIZON or any(type(t) is not int for t in times):
        raise ValueError('Observation times exceed the stated horizon')
    if len(rows) != 5 or any(len(row) != 5 for row in rows):
        raise ValueError('Certificate basis must be five by five')
    if any(type(v) is not int for row in rows for v in row):
        raise ValueError('Basis coefficients must be integers')
    powers = [pow(A, t, M) for t in times]
    if any((row[i]-powers[i]*row[0]) % M for row in rows for i in range(5)):
        raise ValueError('Basis row is outside the collision lattice')
    inverse, determinant = _inverse_and_determinant(rows)
    if abs(determinant) != M**4:
        raise ValueError('Basis does not have the complete collision-lattice index')
    bounds = [U*sum(abs(inverse[i][j]) for i in range(5)) for j in range(5)]
    if any(value >= 1 for value in bounds):
        raise ValueError('Difference box is not certified to contain only zero')
    return tuple(tuple(row) for row in inverse), tuple(bounds)


def verify_certificate(certificate):
    if not isinstance(certificate, dict) or certificate.get('schema') != 'perfectjet/raw-observer-basis/1':
        raise ValueError('Unknown observer certificate schema')
    try:
        times = tuple(certificate['times'])
        rows = tuple(tuple(row) for row in certificate['basis'])
        inverse, bounds = _check_basis(times, rows)
    except (KeyError, TypeError) as exc:
        raise ValueError('Malformed observer basis') from exc
    if certificate.get('coefficient_bounds') != [_fraction_record(q) for q in bounds]:
        raise ValueError('Reported coefficient bounds differ from exact arithmetic')
    return {'verified': True, 'times': list(times),
            'maximum_bound': _fraction_record(max(bounds))}


def verify_document(document):
    """Check complete theorem coverage without importing the discovery module."""
    if not isinstance(document, dict) or document.get('schema') != 'perfectjet/raw-observer-suite/1':
        raise ValueError('Unknown raw observer receipt schema')
    if document.get('parameters') != {'modulus': M, 'multiplier': A, 'output_radix': B}:
        raise ValueError('Wrong recurrence or observation map')
    if document.get('horizon') != HORIZON:
        raise ValueError('Wrong theorem horizon')
    certificates = document.get('subset_certificates')
    if not isinstance(certificates, list):
        raise ValueError('Missing certificates')
    expected = required_patterns()
    seen, worst = set(), Fraction(0)
    for certificate in certificates:
        checked = verify_certificate(certificate)
        times = tuple(checked['times'])
        if times in seen or times not in expected:
            raise ValueError('Duplicate or unexpected observation pattern')
        seen.add(times)
        bound = checked['maximum_bound']
        worst = max(worst, Fraction(bound['numerator'], bound['denominator']))
    if seen != expected:
        raise ValueError('Some five-position observation patterns are unproved')
    pair = document.get('sharpness_witness')
    if not isinstance(pair, dict) or pair.get('states') != list(COLLISION_STATES):
        raise ValueError('Missing the declared sharpness witness')
    left, right = [raw_outputs(state, 6) for state in COLLISION_STATES]
    if pair.get('six_outputs') != [left, right] or left[:4] != right[:4] or left[4] == right[4] or left[5] == right[5]:
        raise ValueError('Sharpness pair failed recurrence replay')
    midpoint = left[:]
    midpoint[4] = right[4]
    if pair.get('ambiguous_one_error_word') != midpoint:
        raise ValueError('Incorrect six-symbol ambiguity')
    if not (sum(a != b for a, b in zip(midpoint, left)) == 1
            and sum(a != b for a, b in zip(midpoint, right)) == 1):
        raise ValueError('Received word is not within one error of both states')
    if not M > B**4:
        raise ValueError('Information lower bound does not apply')
    return {'verified': True, 'normalized_subset_certificates': len(seen),
            'five_subsets_of_nine': 126, 'maximum_coefficient_bound': _fraction_record(worst),
            'raw_state_observation_minimum': 5,
            'one_error_minimum': 7, 'two_error_minimum': 9,
            'guarantee': 'For 5<=n<=9, unique correction of t arbitrary output errors and e known erasures whenever n>=5+2*t+e.',
            'scope': 'Current raw emitting state, fixed consecutive recurrence steps and low26 observations; no rejection wrapper, unknown warmup or historic recipe identification.'}


def make_certificate(times):
    """Discover a basis; the independent checker establishes its adequacy."""
    from research.p521.freelip_recovery import reduce_basis
    times = tuple(times)
    rows = [[pow(A, t, M) for t in times]]
    for i in range(1, 5):
        row = [0]*5
        row[i] = M
        rows.append(row)
    basis = reduce_basis(rows)
    _, bounds = _check_basis(times, tuple(tuple(row) for row in basis))
    result = {'schema': 'perfectjet/raw-observer-basis/1', 'times': list(times),
              'basis': basis, 'coefficient_bounds': [_fraction_record(q) for q in bounds]}
    verify_certificate(result)
    return result


def build_suite():
    left, right = [raw_outputs(state, 6) for state in COLLISION_STATES]
    midpoint = left[:]
    midpoint[4] = right[4]
    result = {'schema': 'perfectjet/raw-observer-suite/1',
              'parameters': {'modulus': M, 'multiplier': A, 'output_radix': B},
              'horizon': HORIZON,
              'subset_certificates': [make_certificate(times) for times in sorted(required_patterns())],
              'sharpness_witness': {'states': list(COLLISION_STATES), 'six_outputs': [left, right],
                                    'ambiguous_one_error_word': midpoint},
              'attribution': 'Classical truncated-congruential lattice and coding arguments, specialized and exactly certified here. Worldwide priority unverified.'}
    verify_document(result)
    return result


@lru_cache(maxsize=1)
def _retained_certificates():
    document = json.loads(RECEIPT.read_text(encoding='utf-8'))
    verify_document(document)
    return {tuple(c['times']): c for c in document['subset_certificates']}


def recover_five(times, outputs, certificate=None):
    """Return the state at global time zero, or None for an impossible trace."""
    times, outputs = tuple(times), tuple(outputs)
    if len(times) != 5 or len(outputs) != 5 or tuple(sorted(set(times))) != times:
        raise ValueError('Exactly five sorted distinct positions and outputs required')
    if any(type(t) is not int or t < 0 or t >= HORIZON for t in times):
        raise ValueError('Positions exceed the certified nine-step horizon')
    if any(type(y) is not int or not 0 <= y < B for y in outputs):
        raise ValueError('Each output must be a26-bit unsigned value')
    normalized = _normalized(times)
    certificate = certificate if certificate is not None else _retained_certificates()[normalized]
    verify_certificate(certificate)
    if tuple(certificate['times']) != normalized:
        raise ValueError('Certificate is for different positions')
    rows = tuple(tuple(row) for row in certificate['basis'])
    inverse, _ = _check_basis(normalized, rows)
    powers = [pow(A, t, M) for t in normalized]
    inverse_radix = pow(B, -1, M)
    shifts = [((p*outputs[0]-y)*inverse_radix) % M for p, y in zip(powers, outputs)]
    upper = [(M-1-y)//B for y in outputs]
    coefficients = []
    for j in range(5):
        endpoints = [(-shifts[i]*inverse[i][j], (upper[i]-shifts[i])*inverse[i][j]) for i in range(5)]
        low = sum(min(pair) for pair in endpoints)
        high = sum(max(pair) for pair in endpoints)
        first = -((-low.numerator)//low.denominator)
        last = high.numerator//high.denominator
        if first > last:
            return None
        if first != last:
            raise ArithmeticError('Certified box unexpectedly permits multiple coefficients')
        coefficients.append(first)
    high_parts = [shifts[i]+sum(coefficients[j]*rows[j][i] for j in range(5)) for i in range(5)]
    if not all(0 <= v <= limit for v, limit in zip(high_parts, upper)):
        return None
    emitting = B*high_parts[0]+outputs[0]
    if any((p*emitting % M) % B != y for p, y in zip(powers, outputs)):
        return None
    return emitting*pow(A, -times[0], M) % M


def decode(observations, errors=0):
    """Correct unknown symbol errors and None-marked known erasures exactly.

    This guaranteed decoder requires n>=5+2t+e, with 5<=n<=9. It reports
    impossible received words rather than guessing a state outside the bound.
    """
    observations = list(observations)
    n = len(observations)
    if type(errors) is not int or errors < 0 or not 5 <= n <= HORIZON:
        raise ValueError('Require5..9 observations and a nonnegative error budget')
    if any(y is not None and (type(y) is not int or not 0 <= y < B) for y in observations):
        raise ValueError('Outputs must be26-bit values or None erasures')
    known = [i for i, y in enumerate(observations) if y is not None]
    if len(known) < 5+2*errors:
        raise ValueError('The certified error/erasure bound is not met')
    for times in combinations(known, 5):
        state = recover_five(times, [observations[t] for t in times])
        if state is None:
            continue
        predicted = raw_outputs(state, n)
        bad = [i for i in known if observations[i] != predicted[i]]
        if len(bad) <= errors:
            return {'status': 'recovered', 'state': state, 'corrected_outputs': predicted,
                    'error_positions': bad,
                    'erasure_positions': [i for i, y in enumerate(observations) if y is None]}
    return {'status': 'inconsistent', 'state': None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate', action='store_true', help='Discover all exact observer certificates')
    parser.add_argument('--output', type=Path, default=RECEIPT)
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args(argv)
    if args.generate:
        document = build_suite()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(document, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    else:
        document = json.loads((args.verify or RECEIPT).read_text(encoding='utf-8'))
    print(json.dumps(verify_document(document), indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
