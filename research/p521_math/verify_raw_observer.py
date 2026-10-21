"""Independent, standard-library audit of the raw-observer JSON receipt.

This module deliberately imports neither the discovery/recovery module nor its
LLL implementation.  It uses integer Bareiss determinants and an adjugate,
rather than the discovery module's rational Gauss-Jordan elimination.

Observations are x_i mod B BEFORE advancing x_(i+1) = A*x_i mod M.  The
rejection-sampling wrapper and historical seed initialization are outside this
certificate's scope.
"""
from argparse import ArgumentParser
from fractions import Fraction
from itertools import combinations
import json
from math import gcd
from pathlib import Path


M = 162259276829213363391578010288127
A = 56455876562739436995171414077326
B = 67108864
HORIZON = 9
U = (M - 1) // B
DEFAULT_RECEIPT = Path(__file__).with_name('results') / 'raw-observer.json'


class CertificateError(ValueError):
    """The supplied document does not establish the claimed theorem."""


def _require(condition, message):
    if not condition:
        raise CertificateError(message)


def _integer(value):
    return type(value) is int


def determinant(matrix):
    """Integer determinant by fraction-free elimination, including row pivots."""
    n = len(matrix)
    if n == 0:
        return 1
    _require(all(len(row) == n for row in matrix), 'Non-square matrix')
    work = [list(row) for row in matrix]
    sign, divisor = 1, 1
    for k in range(n - 1):
        if work[k][k] == 0:
            pivot = next((i for i in range(k + 1, n) if work[i][k]), None)
            if pivot is None:
                return 0
            work[k], work[pivot] = work[pivot], work[k]
            sign = -sign
        pivot_value = work[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = work[i][j] * pivot_value - work[i][k] * work[k][j]
                quotient, remainder = divmod(numerator, divisor)
                _require(remainder == 0, 'Non-exact Bareiss division')
                work[i][j] = quotient
            work[i][k] = 0
        divisor = pivot_value
    return sign * work[-1][-1]


def adjugate(matrix):
    """Transpose of the cofactor matrix, computed using integer minors."""
    n = len(matrix)
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            minor = [[matrix[r][c] for c in range(n) if c != j]
                     for r in range(n) if r != i]
            result[j][i] = (-1 if (i + j) % 2 else 1) * determinant(minor)
    return result


def _canonical_fraction(value, expected):
    return (isinstance(value, dict) and set(value) == {'numerator', 'denominator'}
            and _integer(value['numerator']) and _integer(value['denominator'])
            and value == fraction_record(expected))


def fraction_record(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def raw_word(state, count):
    _require(_integer(state) and 0 <= state < M, 'Invalid raw state')
    _require(_integer(count) and count >= 0, 'Invalid output count')
    word = []
    for _ in range(count):
        word.append(state % B)
        state = A * state % M
    return word


def _normalize(times):
    return tuple(t - times[0] for t in times)


def _all_patterns():
    coverage = {}
    for times in combinations(range(HORIZON), 5):
        coverage.setdefault(_normalize(times), []).append(times)
    return coverage


def verify_basis(certificate):
    """Check lattice equality and the strict collision bound independently."""
    _require(isinstance(certificate, dict), 'Invalid basis certificate')
    _require(certificate.get('schema') == 'perfectjet/raw-observer-basis/1',
             'Unsupported basis schema')
    times = certificate.get('times')
    _require(isinstance(times, list) and len(times) == 5
             and all(_integer(t) for t in times), 'Invalid basis positions')
    times = tuple(times)
    _require(times[0] == 0 and times[-1] < HORIZON
             and tuple(sorted(set(times))) == times, 'Invalid normalized positions')
    rows = certificate.get('basis')
    _require(isinstance(rows, list) and len(rows) == 5
             and all(isinstance(row, list) and len(row) == 5
                     and all(_integer(v) for v in row) for row in rows),
             'Basis must be a 5 by 5 integer matrix')
    powers = [pow(A, t, M) for t in times]
    for row in rows:
        _require(all((row[j] - powers[j] * row[0]) % M == 0 for j in range(5)),
                 'Basis row is outside the collision lattice')
    det = determinant(rows)
    _require(abs(det) == M ** 4, 'Basis is singular or has the wrong lattice index')
    adj = adjugate(rows)
    for i in range(5):
        for j in range(5):
            _require(sum(rows[i][k] * adj[k][j] for k in range(5))
                     == (det if i == j else 0), 'Adjugate identity failed')
    inverse = tuple(tuple(Fraction(v, det) for v in row) for row in adj)
    bounds = tuple(Fraction(U * sum(abs(adj[i][j]) for i in range(5)), abs(det))
                   for j in range(5))
    _require(all(bound < 1 for bound in bounds), 'Collision coefficient bound is not strict')
    recorded = certificate.get('coefficient_bounds')
    _require(isinstance(recorded, list) and len(recorded) == 5
             and all(_canonical_fraction(given, bound)
                     for given, bound in zip(recorded, bounds)),
             'Recorded coefficient bounds differ from exact recomputation')
    return {'times': times, 'basis': tuple(map(tuple, rows)), 'inverse': inverse,
            'bounds': bounds, 'determinant': det}


def _distance(left, right):
    _require(len(left) == len(right), 'Unequal word lengths')
    return sum(a != b for a, b in zip(left, right))


def verify_sharpness(witness):
    _require(isinstance(witness, dict), 'Missing sharpness witness')
    states = witness.get('states')
    _require(isinstance(states, list) and len(states) == 2
             and all(_integer(x) and 0 <= x < M for x in states)
             and states[0] != states[1], 'Witness must have two distinct states')
    left, right = (raw_word(state, 8) for state in states)
    recorded_words = witness.get('six_outputs')
    _require(isinstance(recorded_words, list) and len(recorded_words) == 2
             and all(isinstance(word, list) and len(word) == 6
                     and all(_integer(y) and 0 <= y < B for y in word)
                     for word in recorded_words)
             and recorded_words == [left[:6], right[:6]],
             'Recorded sharpness trajectories do not replay')
    _require(left[:4] == right[:4] and _distance(left[:6], right[:6]) == 2,
             'Witness does not establish four-symbol / six-symbol ambiguity')
    midpoint = witness.get('ambiguous_one_error_word')
    _require(isinstance(midpoint, list) and len(midpoint) == 6
             and all(_integer(y) and 0 <= y < B for y in midpoint)
             and _distance(left[:6], midpoint) == _distance(right[:6], midpoint) == 1,
             'Recorded midpoint is not within one symbol error of both states')
    # Extend the SAME retained states, so eight-symbol/two-error sharpness is
    # constructive as well as a consequence of the information bound.
    differing = [i for i in range(8) if left[i] != right[i]]
    _require(len(differing) == 4, 'Eight-symbol witness must have distance four')
    midpoint_two = left[:]
    for i in differing[:2]:
        midpoint_two[i] = right[i]
    _require(_distance(left, midpoint_two) == _distance(right, midpoint_two) == 2,
             'Derived two-error midpoint failed')
    return {'states': states, 'eight_outputs': [left, right],
            'ambiguous_two_error_word': midpoint_two}


def verify_document(document):
    _require(isinstance(document, dict), 'Document must be an object')
    _require(document.get('schema') == 'perfectjet/raw-observer-suite/1',
             'Unsupported suite schema')
    parameters = document.get('parameters')
    expected = {'modulus': M, 'multiplier': A, 'output_radix': B}
    _require(isinstance(parameters, dict) and parameters == expected
             and all(_integer(v) for v in parameters.values()), 'Wrong recurrence parameters')
    _require(_integer(document.get('horizon')) and document['horizon'] == HORIZON,
             'Wrong horizon')
    _require(M == 2 ** 107 - 1 and A == pow(3, 121, M) and B == 2 ** 26,
             'Embedded recurrence constants are inconsistent')
    _require(gcd(A, M) == gcd(B, M) == 1, 'Time shift or output radix is not invertible')
    _require(B ** 4 < M <= B ** 5, 'Five-symbol information bound failed')
    coverage = _all_patterns()
    _require(len(coverage) == 70 and sum(map(len, coverage.values())) == 126,
             'Independent position-pattern enumeration failed')
    certificates = document.get('subset_certificates')
    _require(isinstance(certificates, list), 'Missing subset certificates')
    checked = {}
    for certificate in certificates:
        result = verify_basis(certificate)
        times = result['times']
        _require(times in coverage, 'Unexpected position pattern')
        _require(times not in checked, 'Duplicate position pattern')
        checked[times] = result
    _require(set(checked) == set(coverage), 'Incomplete five-subset coverage')
    maximum = max(bound for result in checked.values() for bound in result['bounds'])
    _require(maximum < Fraction(369, 1000), 'Published 0.369 bound failed')
    sharpness = verify_sharpness(document.get('sharpness_witness'))
    return {'verified': True, 'normalized_patterns': len(checked),
            'covered_five_subsets': sum(map(len, coverage.values())),
            'maximum_coefficient_bound': fraction_record(maximum),
            'raw_state_observation_minimum': 5,
            'one_error_observation_minimum': 7, 'two_error_observation_minimum': 9,
            'time_shift_is_bijective': True,
            'state_convention': 'state at global raw time zero, observed before advance',
            'sharpness': sharpness}


def recover_from_basis(certificate, times, outputs):
    """Independent inverse for testing the emitting-state/time-zero alignment.

    The caller supplies one validated five-position pattern and five symbols.
    This function derives the affine equations afresh from x_i=y_i+B*h_i.
    It does not call the discovery implementation, even for constants.
    """
    checked = verify_basis(certificate)
    times, outputs = tuple(times), tuple(outputs)
    _require(len(times) == len(outputs) == 5
             and all(_integer(t) and 0 <= t < HORIZON for t in times)
             and tuple(sorted(set(times))) == times, 'Invalid observation positions')
    _require(_normalize(times) == checked['times'], 'Basis does not match observation positions')
    _require(all(_integer(y) and 0 <= y < B for y in outputs), 'Invalid output symbols')
    powers = [pow(A, t - times[0], M) for t in times]
    radix_inverse = pow(B, -1, M)
    shifts = [((p * outputs[0] - y) * radix_inverse) % M
              for p, y in zip(powers, outputs)]
    caps = [(M - 1 - y) // B for y in outputs]
    inverse = checked['inverse']
    coefficients = []
    for j in range(5):
        lower = upper = Fraction(0)
        for i in range(5):
            endpoints = (-shifts[i] * inverse[i][j],
                         (caps[i] - shifts[i]) * inverse[i][j])
            lower += min(endpoints)
            upper += max(endpoints)
        first = -((-lower.numerator) // lower.denominator)
        last = upper.numerator // upper.denominator
        if first > last:
            return None
        _require(first == last, 'Certified affine box has multiple coefficient candidates')
        coefficients.append(first)
    high = [shifts[i] + sum(coefficients[j] * checked['basis'][j][i] for j in range(5))
            for i in range(5)]
    if any(not 0 <= value <= cap for value, cap in zip(high, caps)):
        return None
    emitting_state = outputs[0] + B * high[0]
    if any((p * emitting_state % M) % B != y for p, y in zip(powers, outputs)):
        return None
    return emitting_state * pow(A, -times[0], M) % M


def main(argv=None):
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('receipt', nargs='?', type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args(argv)
    result = verify_document(json.loads(args.receipt.read_text(encoding='utf-8')))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
