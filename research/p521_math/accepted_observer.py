"""Exact state collisions for the source-faithful FreeLIP accepted interface.

The target is the first emitting (accepted) state.  The state before the first
call has unavoidable observational equivalences caused by the rejection loop.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import gcd, lcm
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

M = (1 << 107)-1
A = pow(3, 121, M)
B = 1 << 26

THRESHOLD = M-(M % B)
U = (M-1)//B
SCALE = 1 << 55
RECEIPT = Path(__file__).with_name('results')/'accepted-observer.json'
COLLISION_STATES = (126295752713511514371453877552714,
                    81692446156502146450273842038346)


def inverse(rows):
    """Exact rational inversion; the receipt verifier never calls LLL."""
    n = len(rows)
    work = [[Fraction(v) for v in row]+[Fraction(i == j) for j in range(n)]
            for i, row in enumerate(rows)]
    for column in range(n):
        pivot = next((i for i in range(column, n) if work[i][column]), None)
        if pivot is None:
            raise ValueError('Singular certificate basis')
        work[pivot], work[column] = work[column], work[pivot]
        divisor = work[column][column]
        work[column] = [v/divisor for v in work[column]]
        for i in range(n):
            if i != column:
                multiplier = work[i][column]
                work[i] = [v-multiplier*w for v, w in zip(work[i], work[column])]
    return [row[n:] for row in work]


def reduce_basis(rows):
    from research.p521.freelip_recovery import reduce_basis as discover
    return discover(rows)


def accepted_trace(first_state, count):
    """Observe the supplied accepted state itself, then accepted successors."""
    if (type(first_state) is not int or not 0 <= first_state < THRESHOLD
            or type(count) is not int or count < 1):
        raise ValueError('Need an accepted first state and positive count')
    states, outputs, gaps = [first_state], [first_state % B], []
    state = first_state
    for _ in range(count-1):
        state = A*state % M
        gap = 1
        while state >= THRESHOLD:
            state = A*state % M
            gap += 1
        if gap > 2:
            raise ArithmeticError('Source rejection gap theorem failed')
        states.append(state)
        outputs.append(state % B)
        gaps.append(gap)
    return {'states': states, 'outputs': outputs, 'gaps': gaps}


def exponents(gaps):
    out = [0]
    for gap in gaps:
        if type(gap) is not int or gap not in (1, 2):
            raise ValueError('Raw recurrence gaps must be one or two')
        out.append(out[-1]+gap)
    return out


def determinant(rows):
    """Exact Bareiss determinant for the independent basis-index check."""
    rows = [r[:] for r in rows]
    n, sign, previous = len(rows), 1, 1
    for k in range(n-1):
        pivot = next((i for i in range(k, n) if rows[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            rows[pivot], rows[k] = rows[k], rows[pivot]
            sign = -sign
        current = rows[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                numerator = rows[i][j]*current-rows[i][k]*rows[k][j]
                if numerator % previous:
                    raise ArithmeticError('Nonintegral Bareiss update')
                rows[i][j] = numerator//previous
            rows[i][k] = 0
        previous = current
    return sign*rows[-1][-1]


def collision_problem(left_gaps, right_gaps):
    """Necessary lattice for a collision, anchored at the first left rejection.

    If the rejected state is M-u, u is in[1,B-1].  At left observation i,
    s_i = a_i*u mod M.  Let t_i = b_i*t_0 mod M and s_i-t_i=B*z_i.
    Eliminating t_0 gives z_i=b_i*z_0+c_i*u mod M.  Scaling u balances
    its 26-bit box with the 81-bit difference-coordinate boxes.
    """
    if len(left_gaps) != len(right_gaps) or 2 not in left_gaps:
        raise ValueError('Need equally long patterns with a left rejection')
    left_e, right_e = exponents(left_gaps), exponents(right_gaps)
    anchor = left_e[list(left_gaps).index(2)]+1
    alphas = [-pow(A, e-anchor, M) % M for e in left_e]
    betas = [pow(A, e, M) for e in right_e]
    inv_b = pow(B, -1, M)
    cs = [((a-b*alphas[0])*inv_b) % M for a, b in zip(alphas, betas)]
    n = len(alphas)
    rows = [[SCALE, 0]+cs[1:], [0, 1]+betas[1:]]
    for i in range(2, n+1):
        row = [0]*(n+1)
        row[i] = M
        rows.append(row)
    lower = [SCALE]+[-U]*n
    upper = [SCALE*(B-1)]+[U]*n
    return rows, lower, upper, alphas[0], cs, betas


def _ceil(value):
    return -((-value.numerator)//value.denominator)


def _bounds(column, lower, upper):
    return (sum(min(q*a, q*b) for q, a, b in zip(column, lower, upper)),
            sum(max(q*a, q*b) for q, a, b in zip(column, lower, upper)))


def dual_certificate(column, lower, upper):
    denominator = lcm(*(q.denominator for q in column))
    numerator = [int(q*denominator) for q in column]
    common = gcd(denominator, *numerator)
    denominator //= common
    numerator = [q//common for q in numerator]
    low, high = _bounds(numerator, lower, upper)
    return {'numerator': numerator, 'denominator': denominator,
            'minimum': low, 'maximum': high}


def verify_dual(certificate, rows, lower, upper):
    try:
        qs, den = certificate['numerator'], certificate['denominator']
        if type(den) is not int or den <= 0 or len(qs) != len(rows):
            return False
        if any(type(q) is not int for q in qs):
            return False
        if any(sum(a*b for a, b in zip(row, qs)) % den for row in rows):
            return False
        low, high = _bounds(qs, lower, upper)
        return (low == certificate['minimum'] and high == certificate['maximum']
                and -((-low)//den) > high//den)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def _integer_basis(rows, dimension):
    if (not isinstance(rows, list) or len(rows) != dimension
            or any(not isinstance(row, list) or len(row) != dimension for row in rows)
            or any(type(v) is not int for row in rows for v in row)):
        raise ValueError('Need a square integer certificate basis')


def check_cross_basis(left_gaps, right_gaps, basis):
    rows, lower, upper, alpha0, cs, betas = collision_problem(left_gaps, right_gaps)
    _integer_basis(basis, len(rows))
    for row in basis:
        if row[0] % SCALE:
            raise ValueError('Scaled rejection coordinate is not integral')
        u = row[0]//SCALE
        if any((row[i+1]-betas[i]*row[1]-cs[i]*u) % M
               for i in range(1, len(cs))):
            raise ValueError('Basis row is outside the anchored collision lattice')
    if abs(determinant(basis)) != SCALE*M**len(left_gaps):
        raise ValueError('Basis does not span the complete anchored lattice')
    return rows, lower, upper, alpha0, inverse(basis)


def coefficient_ranges(inv, lower, upper):
    ranges = []
    for j in range(len(inv)):
        col = [inv[i][j] for i in range(len(inv))]
        low, high = _bounds(col, lower, upper)
        lo, hi = _ceil(low), high.numerator//high.denominator
        ranges.append([lo, hi])
    return ranges


def enumerate_box(left_gaps, right_gaps, basis, ranges, lower, upper, alpha0):
    """Enumerate all lattice vectors in the enclosing coefficient box."""
    collisions, box_vectors, pairs = [], 0, set()
    n = len(left_gaps)+1
    for coeff in product(*(range(lo, hi+1) for lo, hi in ranges)):
        v = [sum(c*row[i] for c, row in zip(coeff, basis)) for i in range(n+1)]
        if not all(a <= x <= b for x, a, b in zip(v, lower, upper)):
            continue
        box_vectors += 1
        if v[0] % SCALE:
            raise ArithmeticError('Nonintegral scaled rejection distance')
        u, z0 = v[0]//SCALE, v[1]
        left = alpha0*u % M
        right = (left-B*z0) % M
        if left == right or left >= THRESHOLD or right >= THRESHOLD:
            continue
        tl, tr = accepted_trace(left, n), accepted_trace(right, n)
        # All emitting-state guards and all actual forced rejection guards
        # are checked here.  An arbitrary missing raw draw is not permitted.
        if tl['gaps'] != list(left_gaps) or tr['gaps'] != list(right_gaps):
            continue
        if tl['outputs'] != tr['outputs']:
            continue
        if (left, right) in pairs:
            continue
        pairs.add((left, right))
        collisions.append({'left_state': left, 'right_state': right,
                           'outputs': tl['outputs'], 'left_states': tl['states'],
                           'right_states': tr['states'], 'reject_distance': u})
    return box_vectors, collisions


def solve_pattern_pair(left_gaps, right_gaps, max_vectors=1000000):
    rows, lower, upper, _, _, _ = collision_problem(left_gaps, right_gaps)
    reduced = reduce_basis(rows)
    _, _, _, alpha0, inv = check_cross_basis(left_gaps, right_gaps, reduced)
    ranges = coefficient_ranges(inv, lower, upper)
    for j, (lo, hi) in enumerate(ranges):
        if lo > hi:
            col = [inv[i][j] for i in range(len(rows))]
            cert = dual_certificate(col, lower, upper)
            assert verify_dual(cert, rows, lower, upper)
            return {'left_gaps': list(left_gaps), 'right_gaps': list(right_gaps),
                    'status': 'excluded', 'complete': True, 'certificate': cert,
                    'collisions': []}
    count = 1
    for lo, hi in ranges:
        count *= hi-lo+1
    if count > max_vectors:
        return {'left_gaps': list(left_gaps), 'right_gaps': list(right_gaps),
                'status': 'unresolved', 'complete': False, 'box_size': count,
                'collisions': []}
    box_vectors, collisions = enumerate_box(left_gaps, right_gaps, reduced,
                                            ranges, lower, upper, alpha0)
    return {'left_gaps': list(left_gaps), 'right_gaps': list(right_gaps),
            'status': 'enumerated', 'complete': True, 'box_size': count,
            'box_vectors': box_vectors, 'basis': reduced, 'ranges': ranges,
            'collisions': collisions}


def same_pattern_injective(gaps):
    times = exponents(gaps)
    n = len(times)
    rows = [[pow(A, e, M) for e in times]]
    for i in range(1, n):
        row = [0]*n
        row[i] = M
        rows.append(row)
    reduced = reduce_basis(rows)
    _, bounds = check_same_basis(gaps, reduced)
    return {'gaps': list(gaps), 'injective': all(b < 1 for b in bounds),
            'basis': reduced, 'bounds': [str(b) for b in bounds]}


def check_same_basis(gaps, basis):
    powers = [pow(A, e, M) for e in exponents(gaps)]
    n = len(powers)
    _integer_basis(basis, n)
    if any((row[i]-powers[i]*row[0]) % M for row in basis for i in range(n)):
        raise ValueError('Basis row is outside the same-pattern collision lattice')
    if abs(determinant(basis)) != M**(n-1):
        raise ValueError('Basis does not span the complete same-pattern lattice')
    inv = inverse(basis)
    bounds = [U*sum(abs(inv[i][j]) for i in range(n)) for j in range(n)]
    return inv, bounds


def initial_call_equivalence(rejected_state=M-1, count=8):
    if not THRESHOLD <= rejected_state < M:
        raise ValueError('Need a rejected raw state')
    predecessor = pow(A, -1, M)*rejected_state % M
    first_emission = A*rejected_state % M
    if predecessor >= THRESHOLD or first_emission >= THRESHOLD:
        raise ArithmeticError('No-adjacent-rejections theorem failed')
    trace = accepted_trace(first_emission, count)
    return {'pre_call_state_a': predecessor, 'pre_call_state_b': rejected_state,
            'same_first_emitting_state': first_emission, 'outputs': trace['outputs'],
            'reason': 'Both calls first return at the same accepted raw successor.'}


def no_consecutive_rejections():
    """Check a fixed integer dual witness, independently of lattice discovery."""
    q = [9944586160332543, 21699637613853658]
    low, high = sum(q), (B-1)*sum(q)
    if (q[0]+A*q[1]) % M or not 0 < low <= high < M:
        raise ArithmeticError('No-consecutive-rejections dual witness failed')
    return {'numerator': q, 'denominator': M, 'minimum': low, 'maximum': high}


def first_call_preimages(emitting_state):
    """Exactly the raw states that produce this accepted state on next call."""
    if type(emitting_state) is not int or not 0 <= emitting_state < THRESHOLD:
        raise ValueError('Need an accepted emitting state')
    predecessor = pow(A, -1, M)*emitting_state % M
    answer = [predecessor]
    if predecessor >= THRESHOLD:
        answer.append(pow(A, -1, M)*predecessor % M)
    return answer


def build_suite(observations=6, max_vectors=1000000, first_collision=False):
    if type(observations) is not int or observations < 2:
        raise ValueError('At least two observations required')
    patterns = list(product((1, 2), repeat=observations-1))
    result = {'schema': 'perfectjet/accepted-observer/1',
              'parameters': {'modulus': M, 'multiplier': A, 'output_radix': B,
                             'accept_below': THRESHOLD, 'rejection_scale': SCALE},
              'observations': observations,
              'same_patterns': [], 'cross_patterns': [],
              'no_consecutive_rejections': no_consecutive_rejections(),
              'initial_call_equivalence': initial_call_equivalence(),
              'first_call_fibres': {'two_preimages': B-1,
                                    'one_preimage': M-2*(B-1)},
              'sharpness_witness': {'states': list(COLLISION_STATES),
                                    'six_traces': [accepted_trace(s, 6)
                                                   for s in COLLISION_STATES]},
              'attribution': 'Classical truncated-congruential lattice methods, specialized to the exact rejection return map. Worldwide priority unverified.'}
    for gaps in patterns:
        result['same_patterns'].append(same_pattern_injective(gaps))
    for left in patterns:
        if 2 not in left:
            continue
        for right in patterns:
            if left == right:
                continue
            pair = solve_pattern_pair(left, right, max_vectors)
            result['cross_patterns'].append(pair)
            if first_collision and pair['collisions']:
                return result
    return result


def verify_document(document):
    """Replay the complete sharp six-output proof using standard-library integers.

    Membership plus determinant checks establish that each retained basis spans
    exactly its stated lattice. Exact inverse bounds then cover every possible
    coefficient vector; full source guards eliminate the relaxed candidates.
    """
    if not isinstance(document, dict) or document.get('schema') != 'perfectjet/accepted-observer/1':
        raise ValueError('Unknown accepted-observer receipt schema')
    if document.get('parameters') != {'modulus': M, 'multiplier': A, 'output_radix': B,
                                      'accept_below': THRESHOLD, 'rejection_scale': SCALE}:
        raise ValueError('Wrong recurrence, observation map or rejection threshold')
    if document.get('observations') != 6:
        raise ValueError('This theorem requires exactly six accepted observations')
    if document.get('no_consecutive_rejections') != no_consecutive_rejections():
        raise ValueError('Wrong rejection-gap proof')
    if document.get('initial_call_equivalence') != initial_call_equivalence():
        raise ValueError('Wrong pre-call state equivalence witness')
    if document.get('first_call_fibres') != {'two_preimages': B-1, 'one_preimage': M-2*(B-1)}:
        raise ValueError('Wrong first-call fibre counts')
    witness = document.get('sharpness_witness', {})
    traces = [accepted_trace(s, 6) for s in COLLISION_STATES]
    if (witness.get('states') != list(COLLISION_STATES)
            or witness.get('six_traces') != traces
            or traces[0]['outputs'][:5] != traces[1]['outputs'][:5]
            or traces[0]['outputs'][5] == traces[1]['outputs'][5]):
        raise ValueError('Five-output ambiguity witness failed exact source replay')
    patterns = set(product((1, 2), repeat=5))
    same_seen, cross_seen = set(), set()
    worst_bound, coefficient_combinations, lattice_vectors = Fraction(0), 0, 0
    same = document.get('same_patterns')
    cross = document.get('cross_patterns')
    if not isinstance(same, list) or not isinstance(cross, list):
        raise ValueError('Missing pattern certificates')
    for certificate in same:
        gaps = tuple(certificate['gaps'])
        if gaps not in patterns or gaps in same_seen:
            raise ValueError('Unexpected or duplicate same-gap pattern')
        same_seen.add(gaps)
        _, bounds = check_same_basis(gaps, certificate['basis'])
        if (certificate.get('injective') is not True or any(b >= 1 for b in bounds)
                or certificate.get('bounds') != [str(b) for b in bounds]):
            raise ValueError('Same-pattern difference box is not certified unique')
        worst_bound = max(worst_bound, *bounds)
    required = {(left, right) for left in patterns if 2 in left
                for right in patterns if left != right}
    for certificate in cross:
        left, right = tuple(certificate['left_gaps']), tuple(certificate['right_gaps'])
        key = (left, right)
        if key not in required or key in cross_seen:
            raise ValueError('Unexpected or duplicate cross-gap pattern pair')
        cross_seen.add(key)
        if certificate.get('complete') is not True or certificate.get('collisions') != []:
            raise ValueError('Incomplete or colliding cross-pattern certificate')
        rows, lower, upper, alpha0, _, _ = collision_problem(left, right)
        if certificate.get('status') == 'excluded':
            if not verify_dual(certificate['certificate'], rows, lower, upper):
                raise ValueError('Invalid cross-pattern dual exclusion')
            continue
        if certificate.get('status') != 'enumerated':
            raise ValueError('Cross-pattern certificate lacks a complete proof')
        basis = certificate['basis']
        _, _, _, alpha0, inv = check_cross_basis(left, right, basis)
        ranges = coefficient_ranges(inv, lower, upper)
        if certificate.get('ranges') != ranges:
            raise ValueError('Reported coefficient intervals differ from exact bounds')
        count = 1
        for lo, hi in ranges:
            count *= max(0, hi-lo+1)
        if count > 1000000 or certificate.get('box_size') != count:
            raise ValueError('Wrong or excessive enumeration size')
        vectors, collisions = enumerate_box(left, right, basis, ranges, lower, upper, alpha0)
        if collisions or certificate.get('box_vectors') != vectors:
            raise ValueError('Guarded lattice replay disagrees with the claimed exclusion')
        coefficient_combinations += count
        lattice_vectors += vectors
    if same_seen != patterns or cross_seen != required:
        raise ValueError('Some source gap patterns or cross-pattern pairs are unproved')
    return {'verified': True, 'accepted_state_observation_minimum': 6,
            'same_patterns': len(same_seen), 'cross_pattern_pairs': len(cross_seen),
            'coefficient_combinations': coefficient_combinations,
            'guarded_lattice_vectors': lattice_vectors,
            'maximum_same_pattern_coefficient_bound': str(worst_bound),
            'pre_call_singleton_fibres': M-2*(B-1), 'pre_call_double_fibres': B-1,
            'scope': 'First accepted emitting state, consecutive accepted low26 outputs, exact forced rejection loop. No historical-recipe identification.'}


@lru_cache(maxsize=1)
def retained_same_patterns():
    document = json.loads(RECEIPT.read_text(encoding='utf-8'))
    verify_document(document)
    return {tuple(c['gaps']): c['basis'] for c in document['same_patterns']}


def recover_accepted(outputs):
    """Recover the first emitting state from at least six accepted outputs.

    Return None for an impossible sequence. Unknown skipped raw draws are
    handled only when they are forced by the actual rejection predicate.
    """
    outputs = list(outputs)
    if len(outputs) < 6 or any(type(y) is not int or not 0 <= y < B for y in outputs):
        raise ValueError('Need at least six unsigned 26-bit accepted outputs')
    selected = outputs[:6]
    for gaps, basis in retained_same_patterns().items():
        powers = [pow(A, e, M) for e in exponents(gaps)]
        shifts = [((p*selected[0]-y)*pow(B, -1, M)) % M
                  for p, y in zip(powers, selected)]
        upper = [(THRESHOLD-1-y)//B for y in selected]
        inv, _ = check_same_basis(gaps, basis)
        ranges = coefficient_ranges(inv, [-s for s in shifts],
                                     [u-s for u, s in zip(upper, shifts)])
        if any(lo > hi for lo, hi in ranges):
            continue
        if any(lo != hi for lo, hi in ranges):
            raise ArithmeticError('Certified same-pattern affine box is not unique')
        coefficients = [lo for lo, hi in ranges]
        highs = [shift+sum(c*row[i] for c, row in zip(coefficients, basis))
                 for i, shift in enumerate(shifts)]
        if not all(0 <= h <= u for h, u in zip(highs, upper)):
            continue
        state = selected[0]+B*highs[0]
        trace = accepted_trace(state, len(outputs))
        if trace['gaps'][:5] == list(gaps) and trace['outputs'] == outputs:
            return state
    return None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observations', type=int, default=6)
    parser.add_argument('--output', type=Path, default=RECEIPT)
    parser.add_argument('--max-vectors', type=int, default=1000000)
    parser.add_argument('--first-collision', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        result = json.loads(args.output.read_text(encoding='utf-8'))
    else:
        result = build_suite(args.observations, args.max_vectors, args.first_collision)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    if args.observations == 6 and not args.first_collision:
        print(json.dumps(verify_document(result), indent=2))
    else:
        collisions = [dict(p, collisions=p['collisions']) for p in result['cross_patterns']
                      if p['collisions']]
        print(json.dumps({'partial_or_non_six_scan': True, 'colliding_pairs': collisions}, indent=2))
