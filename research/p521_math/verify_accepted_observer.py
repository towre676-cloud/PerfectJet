"""Independent standard-library audit of the six-accepted-output theorem.

This verifier imports no project module, lattice package, or discovery code.
Its proof inputs are the receipt's integer bases and the public recurrence.
"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse
import json

MODULUS = 2**107-1
MULTIPLIER = pow(3, 121, MODULUS)
RADIX = 2**26
REJECT_SIZE = RADIX-1
ACCEPT_LIMIT = MODULUS-REJECT_SIZE
WEIGHT = 2**55
DIFFERENCE_LIMIT = (MODULUS-1)//RADIX
DEFAULT_RECEIPT = Path(__file__).with_name('results')/'accepted-observer.json'
AMBIGUOUS_STATES = (126295752713511514371453877552714,
                    81692446156502146450273842038346)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _invert(matrix):
    """Fraction elimination checks determinant and returns inverse together."""
    n = len(matrix)
    _require(isinstance(matrix, list) and all(isinstance(row, list) and len(row) == n
                                             for row in matrix), 'Nonsquare basis')
    _require(all(type(v) is int for row in matrix for v in row), 'Noninteger basis')
    work = [[Fraction(v) for v in row]+[Fraction(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    det = Fraction(1)
    for j in range(n):
        pivot = next((i for i in range(j, n) if work[i][j] != 0), None)
        _require(pivot is not None, 'Singular basis')
        if pivot != j:
            work[j], work[pivot] = work[pivot], work[j]
            det *= -1
        divisor = work[j][j]
        det *= divisor
        work[j] = [q/divisor for q in work[j]]
        for i in range(n):
            if i != j:
                multiple = work[i][j]
                work[i] = [q-multiple*r for q, r in zip(work[i], work[j])]
    return [row[n:] for row in work], det


def _positions(gaps):
    _require(len(gaps) == 5 and all(type(g) is int and g in (1, 2) for g in gaps),
             'Invalid six-output gap pattern')
    positions = [0]
    for gap in gaps:
        positions.append(positions[-1]+gap)
    return positions


def _ceil(q):
    return -((-q.numerator)//q.denominator)


def _interval(weights, lower, upper):
    return (sum(min(w*a, w*b) for w, a, b in zip(weights, lower, upper)),
            sum(max(w*a, w*b) for w, a, b in zip(weights, lower, upper)))


def _ranges(inverse, lower, upper):
    result = []
    for column in zip(*inverse):
        low, high = _interval(column, lower, upper)
        result.append([_ceil(low), high.numerator//high.denominator])
    return result


def _accepted_trace(first, count):
    _require(type(first) is int and 0 <= first < ACCEPT_LIMIT, 'Unaccepted first state')
    state, states, outputs, gaps = first, [first], [first % RADIX], []
    for _ in range(count-1):
        state = MULTIPLIER*state % MODULUS
        gap = 1
        while state >= ACCEPT_LIMIT:
            state = MULTIPLIER*state % MODULUS
            gap += 1
            _require(gap <= 2, 'Consecutive rejections contradict checked lemma')
        states.append(state)
        outputs.append(state % RADIX)
        gaps.append(gap)
    return {'states': states, 'outputs': outputs, 'gaps': gaps}


def _same_pattern(record):
    gaps, basis = tuple(record['gaps']), record['basis']
    powers = [pow(MULTIPLIER, t, MODULUS) for t in _positions(gaps)]
    _require(len(basis) == 6, 'Wrong same-pattern dimension')
    inv, det = _invert(basis)
    _require(abs(det) == MODULUS**5, 'Same-pattern lattice has wrong index')
    _require(all((row[i]-powers[i]*row[0]) % MODULUS == 0
                 for row in basis for i in range(6)), 'Wrong same-pattern lattice membership')
    bounds = [DIFFERENCE_LIMIT*sum(abs(q) for q in column) for column in zip(*inv)]
    _require(all(q < 1 for q in bounds), 'Same-pattern difference box not unique')
    _require(record.get('injective') is True and record.get('bounds') == [str(q) for q in bounds],
             'Reported same-pattern bounds do not replay')
    return gaps, max(bounds)


def _cross_problem(left, right):
    le, re = _positions(left), _positions(right)
    _require(2 in left and left != right, 'Cross pair requires an anchored rejection')
    anchor = le[left.index(2)]+1
    alpha = [(-pow(MULTIPLIER, t-anchor, MODULUS)) % MODULUS for t in le]
    beta = [pow(MULTIPLIER, t, MODULUS) for t in re]
    correction = [((a-b*alpha[0])*pow(RADIX, -1, MODULUS)) % MODULUS
                  for a, b in zip(alpha, beta)]
    generators = [[WEIGHT, 0]+correction[1:], [0, 1]+beta[1:]]
    for coordinate in range(2, 7):
        generators.append([MODULUS if i == coordinate else 0 for i in range(7)])
    return (alpha[0], beta, correction, generators,
            [WEIGHT]+[-DIFFERENCE_LIMIT]*6,
            [WEIGHT*REJECT_SIZE]+[DIFFERENCE_LIMIT]*6)


def _cross_pattern(record):
    left, right = tuple(record['left_gaps']), tuple(record['right_gaps'])
    alpha0, beta, correction, generators, lower, upper = _cross_problem(left, right)
    _require(record.get('complete') is True and record.get('collisions') == [],
             'Cross proof claims a collision or incomplete search')
    if record.get('status') == 'excluded':
        cert = record['certificate']
        nums, den = cert['numerator'], cert['denominator']
        _require(type(den) is int and den > 0 and len(nums) == 7
                 and all(type(v) is int for v in nums), 'Malformed dual witness')
        _require(all(sum(a*b for a, b in zip(row, nums)) % den == 0 for row in generators),
                 'Dual witness is not integral on the complete lattice')
        low, high = _interval(nums, lower, upper)
        _require(cert.get('minimum') == low and cert.get('maximum') == high,
                 'Wrong reported dual interval')
        _require(-((-low)//den) > high//den, 'Dual interval contains an integer')
        return (left, right), 0, 0
    _require(record.get('status') == 'enumerated', 'Unproved cross-pattern status')
    basis = record['basis']
    _require(len(basis) == 7, 'Wrong scaled cross-pattern dimension')
    inv, det = _invert(basis)
    _require(abs(det) == WEIGHT*MODULUS**5, 'Scaled lattice has wrong index')
    for row in basis:
        _require(row[0] % WEIGHT == 0, 'Rejection coordinate not divisible by scale')
        u = row[0]//WEIGHT
        _require(all((row[i+1]-beta[i]*row[1]-correction[i]*u) % MODULUS == 0
                     for i in range(1, 6)), 'Wrong scaled lattice membership')
    ranges = _ranges(inv, lower, upper)
    _require(record.get('ranges') == ranges, 'Incorrect enclosing coefficient intervals')
    count = 1
    for lo, hi in ranges:
        count *= max(0, hi-lo+1)
    _require(count <= 1000000 and record.get('box_size') == count,
             'Wrong or excessive coefficient enumeration size')
    in_box = 0
    for coefficients in product(*(range(lo, hi+1) for lo, hi in ranges)):
        vector = [sum(c*row[i] for c, row in zip(coefficients, basis)) for i in range(7)]
        if any(v < lo or v > hi for v, lo, hi in zip(vector, lower, upper)):
            continue
        in_box += 1
        u, z0 = vector[0]//WEIGHT, vector[1]
        state_left = alpha0*u % MODULUS
        state_right = (state_left-RADIX*z0) % MODULUS
        if state_left == state_right or state_left >= ACCEPT_LIMIT or state_right >= ACCEPT_LIMIT:
            continue
        trace_left = _accepted_trace(state_left, 6)
        trace_right = _accepted_trace(state_right, 6)
        if trace_left['gaps'] != list(left) or trace_right['gaps'] != list(right):
            continue
        _require(trace_left['outputs'] != trace_right['outputs'],
                 'Actual distinct accepted states collide in six outputs')
    _require(record.get('box_vectors') == in_box, 'Wrong count of lattice points in box')
    return (left, right), count, in_box


def verify_document(document):
    """Independently establish exact coverage, uniqueness, and five-output failure."""
    _require(isinstance(document, dict) and document.get('schema') == 'perfectjet/accepted-observer/1',
             'Unknown accepted-observer schema')
    _require(document.get('parameters') == {
        'modulus': MODULUS, 'multiplier': MULTIPLIER, 'output_radix': RADIX,
        'accept_below': ACCEPT_LIMIT, 'rejection_scale': WEIGHT}, 'Wrong fixed model')
    _require(document.get('observations') == 6, 'Only the six-output theorem is audited')
    q = [9944586160332543, 21699637613853658]
    low, high = sum(q), REJECT_SIZE*sum(q)
    _require(MODULUS % RADIX == REJECT_SIZE and
             (q[0]+MULTIPLIER*q[1]) % MODULUS == 0 and 0 < low <= high < MODULUS,
             'Independent no-consecutive-rejections proof failed')
    _require(document.get('no_consecutive_rejections') == {
        'numerator': q, 'denominator': MODULUS, 'minimum': low, 'maximum': high},
        'Wrong retained no-consecutive-rejections witness')
    patterns = set(product((1, 2), repeat=5))
    expected_cross = {(left, right) for left in patterns if 2 in left
                      for right in patterns if left != right}
    same_seen, cross_seen = set(), set()
    worst, combinations, vectors = Fraction(0), 0, 0
    for record in document['same_patterns']:
        gaps, bound = _same_pattern(record)
        _require(gaps in patterns and gaps not in same_seen, 'Duplicate or unexpected same pattern')
        same_seen.add(gaps)
        worst = max(worst, bound)
    for record in document['cross_patterns']:
        key, count, in_box = _cross_pattern(record)
        _require(key in expected_cross and key not in cross_seen, 'Duplicate or unexpected cross pair')
        cross_seen.add(key)
        combinations += count
        vectors += in_box
    _require(same_seen == patterns and cross_seen == expected_cross, 'Incomplete pattern coverage')
    traces = [_accepted_trace(state, 6) for state in AMBIGUOUS_STATES]
    _require(traces[0]['outputs'][:5] == traces[1]['outputs'][:5]
             and traces[0]['outputs'][5] != traces[1]['outputs'][5], 'Five-output ambiguity did not replay')
    _require(document.get('sharpness_witness') == {'states': list(AMBIGUOUS_STATES), 'six_traces': traces},
             'Wrong retained sharpness witness')
    predecessor = pow(MULTIPLIER, -1, MODULUS)*(MODULUS-1) % MODULUS
    emission = MULTIPLIER*(MODULUS-1) % MODULUS
    equivalence = {'pre_call_state_a': predecessor, 'pre_call_state_b': MODULUS-1,
                   'same_first_emitting_state': emission,
                   'outputs': _accepted_trace(emission, 8)['outputs'],
                   'reason': 'Both calls first return at the same accepted raw successor.'}
    _require(predecessor < ACCEPT_LIMIT and emission < ACCEPT_LIMIT
             and document.get('initial_call_equivalence') == equivalence,
             'Pre-call equivalence witness did not replay')
    fibres = {'two_preimages': REJECT_SIZE, 'one_preimage': MODULUS-2*REJECT_SIZE}
    _require(document.get('first_call_fibres') == fibres, 'Wrong first-call fibre counts')
    return {'independently_verified': True, 'minimum_accepted_outputs': 6,
            'same_patterns': len(same_seen), 'cross_pattern_pairs': len(cross_seen),
            'coefficient_combinations': combinations, 'in_box_vectors': vectors,
            'maximum_same_pattern_bound': str(worst),
            'initial_state_unique_in_general': False,
            'scope': 'First emitting state under exact source rejection loop.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipt', type=Path, nargs='?', default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    print(json.dumps(verify_document(json.loads(args.receipt.read_text())), indent=2))
