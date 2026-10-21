"""Exact inverse search for P-521 coordinates under power-of-two field charts.

The search asks whether 2**k * x (mod 2**521-1) is a coordinate assembled
from the specified historical FreeLIP output stream. It never treats a match
as proof that a historical implementation used that chart.
"""
from __future__ import annotations

import argparse
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from research.p521 import freelip_recovery as f
from research.p521.curve import A as CURVE_A, B as CURVE_B, GX, P

PRIORITY_PHASES = (23, 55, 25)


def rotate(value, phase):
    """Canonical multiplication by 2**phase, exactly a 521-bit cyclic rotation."""
    if type(value) is not int or not 0 <= value < P:
        raise ValueError('value must be a canonical P-521 field element')
    if type(phase) is not int:
        raise ValueError('phase must be an integer')
    return value * pow(2, phase % 521, P) % P


def phase_order():
    return list(PRIORITY_PHASES) + [k for k in range(521) if k not in PRIORITY_PHASES]


def exponents(gaps):
    times = [0]
    for gap in gaps:
        if type(gap) is not int or gap not in (1, 2):
            raise ValueError('a source gap must be one or two')
        times.append(times[-1]+gap)
    return times


def quotient_bounds(row):
    lower = ((f.M-1)*sum(min(x, 0) for x in row)+f.M-1)//f.M
    upper = ((f.M-1)*sum(max(x, 0) for x in row))//f.M
    return lower, upper


def relation_excludes(outputs, row):
    """Exact all-state contradiction from a modular relation on emitting states."""
    lower, upper = quotient_bounds(row)
    residue = -sum(q*y for q, y in zip(row, outputs)) % f.B
    first = lower + (residue-lower) % f.B
    return first > upper


def verify_relation(row, gaps):
    return (len(row) == len(gaps)+1 and all(type(q) is int for q in row)
            and any(row) and sum(q*pow(f.A, t, f.M)
                                  for q, t in zip(row, exponents(gaps))) % f.M == 0)


def build_bank(observations=8):
    """Discover short dual rows once per gap pattern, shared by every target."""
    bank = []
    for gaps in product((1, 2), repeat=observations-1):
        powers = [pow(f.A, t, f.M) for t in exponents(gaps)]
        rows = [[f.M]+[0]*(observations-1)]
        for i in range(1, observations):
            row = [0]*observations
            row[0] = -powers[i]
            row[i] = 1
            rows.append(row)
        reduced = f.reduce_basis(rows)
        reduced = sorted(reduced, key=lambda q: sum(map(abs, q)))
        if not all(verify_relation(q, gaps) for q in reduced):
            raise ArithmeticError('discovered dual relation failed its exact check')
        bank.append({'gaps': list(gaps), 'relations': reduced})
    return bank


def _source_states(first_emitting, accepted_index):
    # The old module's backward interface retains both possible pre-call states
    # if the first call may have crossed a rejected state.
    return f._source_initial_states(first_emitting, accepted_index)


def recover_profile(target, count, order, bank):
    traces = f.interior_sequences(target, count, order)
    if not traces:
        return {'status': 'excluded-by-range', 'traces': [], 'candidates': []}
    records, candidates = [], []
    for interior in traces:
        observed = interior['outputs'][:len(bank[0]['gaps'])+1]
        choices, survivors = [], []
        for entry in bank:
            witness = next((i for i, row in enumerate(entry['relations'])
                            if relation_excludes(observed, row)), None)
            if witness is not None:
                choices.append(str(witness))
                continue
            choices.append('s')
            result = f.recover_low_outputs(observed, gaps=entry['gaps'])
            recovered = []
            for state in result['states']:
                if state >= f.M-f.M % f.B:
                    continue
                tail, emitting_tail = f.draw(state, len(observed)-1, rejection=True)
                if [state % f.B]+tail != observed:
                    continue
                source_states = [state]+emitting_tail
                if any(source_states[i+1] != pow(f.A, gap, f.M)*source_states[i] % f.M
                       for i, gap in enumerate(entry['gaps'])):
                    continue
                for initial in _source_states(state, interior['first_output_index']):
                    limbs, _ = f.draw(initial, count, rejection=True)
                    if f.assemble(limbs, order) % P == target:
                        match = {'initial_state': initial, 'limbs': limbs,
                                 'emitting_state': state, 'gaps': entry['gaps']}
                        if match not in candidates:
                            candidates.append(match)
                        recovered.append(initial)
            survivors.append({'gaps': entry['gaps'], 'recovery': result,
                              'full_coordinate_states': sorted(set(recovered))})
        records.append({'interior': interior, 'choices': ''.join(choices), 'survivors': survivors})
    complete = all(s['recovery']['complete'] for r in records for s in r['survivors'])
    return {'status': ('matched' if candidates else 'excluded' if complete else 'unresolved'),
            'traces': records, 'candidates': candidates, 'complete': complete}


def search(public_x=GX, phases=None, layouts=None, bank=None, progress=False):
    if bank is None:
        bank = build_bank()
    phases = list(phase_order() if phases is None else phases)
    layouts = list(((22, 'msb'), (20, 'msb'), (21, 'msb'),
                    (20, 'lsb'), (21, 'lsb'), (22, 'lsb')) if layouts is None else layouts)
    records, matches = [], []
    for k in phases:
        raw = rotate(public_x, k)
        for count, order in layouts:
            result = recover_profile(raw, count, order, bank)
            record = {'phase': k, 'limbs': count, 'order': order,
                      'raw_target': hex(raw), **result}
            records.append(record)
            for candidate in result['candidates']:
                decoded = rotate(f.assemble(candidate['limbs'], order) % P, -k)
                if decoded != public_x:
                    raise ArithmeticError('inverse chart replay failed')
                matches.append({'phase': k, 'limb_count': count, 'order': order,
                                'decoded_x': hex(decoded), **candidate})
        if progress and (k in PRIORITY_PHASES or k % 50 == 0):
            print(json.dumps({'phase': k, 'matches': len(matches)}), file=sys.stderr)
    return {'schema': 'perfectjet/p521-rotation-search/1', 'public_x': hex(public_x),
            'phases': phases, 'layouts': [list(p) for p in layouts],
            'source_rejection': True, 'rejection_gap_proof': f.no_consecutive_rejections(),
            'dual_bank': bank, 'profiles': records, 'matches': matches,
            'complete': all(r.get('complete', True) for r in records),
            'historical_status': 'Chart hypotheses only. A match requires independent historical support.',
            'scope': 'All FreeLIP internal states for the declared low26 source sampler, '
                     'limb assemblies, power-of-two chart conversions, and field reduction.'}


def _verify_profile(public_x, record, bank):
    k, count, order = record['phase'], record['limbs'], record['order']
    target = rotate(public_x, k)
    if record['raw_target'] != hex(target):
        raise ValueError('wrong rotated target')
    necessary = f.interior_sequences(target, count, order)
    if not necessary:
        if record['status'] != 'excluded-by-range' or record['traces'] or record['candidates']:
            raise ValueError('invalid raw-range exclusion')
        return
    if len(record['traces']) != len(necessary):
        raise ValueError('missing carry-prefix branch')
    for actual, expected in zip(record['traces'], necessary):
        if actual['interior'] != expected:
            raise ValueError('incorrect forced prefix')
        choices = actual['choices']
        if len(choices) != len(bank):
            raise ValueError('incomplete rejection-gap coverage')
        observed = expected['outputs'][:len(bank[0]['gaps'])+1]
        if actual['survivors']:
            # Such cases are replayed by the exact recovery algorithm. Most
            # public-target rows have short contradictions and no survivors.
            replay = recover_profile(target, count, order, bank)
            if replay != {key: record[key] for key in replay}:
                raise ValueError('survivor enumeration/replay differs')
            return
        for char, entry in zip(choices, bank):
            if char not in '01234567' or int(char) >= len(entry['relations']):
                raise ValueError('invalid or missing dual witness')
            if not relation_excludes(observed, entry['relations'][int(char)]):
                raise ValueError('dual row does not exclude observation box')
    if record['status'] != 'excluded' or record['candidates']:
        raise ValueError('unsupported exclusion summary')


def verify_document(document):
    if document.get('schema') != 'perfectjet/p521-rotation-search/1':
        raise ValueError('unsupported rotation receipt')
    public_x = int(document['public_x'], 16)
    if not 0 <= public_x < P:
        raise ValueError('noncanonical public coordinate')
    if document.get('source_rejection') is not True:
        raise ValueError('receipt must include the original source rejection loop')
    bank = document['dual_bank']
    patterns = list(product((1, 2), repeat=7))
    if len(bank) != 128 or [b['gaps'] for b in bank] != [list(p) for p in patterns]:
        raise ValueError('dual bank must cover every eight-observation source gap pattern')
    for entry in bank:
        if len(entry['relations']) != 8 or not all(verify_relation(q, entry['gaps']) for q in entry['relations']):
            raise ValueError('invalid dual relation bank')
    if document['rejection_gap_proof'] != f.no_consecutive_rejections():
        raise ValueError('wrong rejection-run proof')
    phases = document['phases']
    layouts = document['layouts']
    if len(set(phases)) != len(phases) or any(type(k) is not int or not 0 <= k < 521 for k in phases):
        raise ValueError('invalid rotation coverage')
    if len({tuple(p) for p in layouts}) != len(layouts):
        raise ValueError('duplicate layout')
    expected = [(k, n, order) for k in phases for n, order in layouts]
    if [(r['phase'], r['limbs'], r['order']) for r in document['profiles']] != expected:
        raise ValueError('profile coverage differs from declared search')
    for record in document['profiles']:
        _verify_profile(public_x, record, bank)
    expected_matches = []
    for record in document['profiles']:
        for candidate in record['candidates']:
            expected_matches.append({'phase': record['phase'], 'limb_count': record['limbs'],
                                     'order': record['order'], 'decoded_x': hex(public_x), **candidate})
    if document['matches'] != expected_matches:
        raise ValueError('positive-match summary differs from recovered profiles')
    if document['complete'] != all(r.get('complete', True) for r in document['profiles']):
        raise ValueError('completeness summary differs from profiles')
    if document['matches']:
        # Explicitly recheck all full-coordinate matches; historical provenance
        # is a separate conclusion and never follows from this status.
        for candidate in document['matches']:
            limbs, _ = f.draw(candidate['initial_state'], candidate['limb_count'], rejection=True)
            if limbs != candidate['limbs'] or rotate(f.assemble(limbs, candidate['order']) % P, -candidate['phase']) != public_x:
                raise ValueError('positive candidate failed full-coordinate replay')
    return {'verified': True, 'profiles': len(expected), 'phases': len(phases),
            'matches': len(document['matches']),
            'full_rotation_orbit': set(phases) == set(range(521)),
            'six_layouts': {tuple(p) for p in layouts} == {(n, o) for n in (20, 21, 22) for o in ('msb', 'lsb')},
            'scope': document['scope']}


def make_point_control(initial, phase, max_candidates=100, root_sign=1):
    """Select the first finite point from consecutive complete raw candidates.

    ``root_sign`` explicitly chooses one of the two square roots. The inverse
    search receives only the resulting public x-coordinate, never the state,
    chart phase, candidate number, or square-root selector.
    """
    if type(initial) is not int or not 0 <= initial < f.M or root_sign not in (-1, 1):
        raise ValueError('invalid synthetic point-control state/root selector')
    current = initial
    for candidate in range(1, max_candidates+1):
        limbs, states = f.draw(current, 22, rejection=True)
        raw = f.assemble(limbs) % P
        x = rotate(raw, -phase)
        rhs = (pow(x, 3, P)+CURVE_A*x+CURVE_B) % P
        if rhs == 0 or pow(rhs, (P-1)//2, P) == 1:
            y = root_sign*pow(rhs, (P+1)//4, P) % P
            return {'public_x': x, 'public_y': y, 'phase': phase,
                    'coordinate_initial_state': current,
                    'original_initial_state': initial, 'candidate_index': candidate,
                    'root_sign': root_sign}
        current = states[-1]
    raise RuntimeError('synthetic point-control candidate budget exhausted')


def replay_point_control(control):
    """Check the whole finite-point selection recipe and its signed root."""
    replay = make_point_control(control['original_initial_state'], control['phase'],
                                max_candidates=control['candidate_index'],
                                root_sign=control['root_sign'])
    if replay != control:
        raise ValueError('synthetic finite-point selection replay differs')
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--priority-only', action='store_true')
    args = parser.parse_args(argv)
    if args.verify:
        print(json.dumps(verify_document(json.loads(args.verify.read_text())), indent=2))
        return
    phases = list(PRIORITY_PHASES) if args.priority_only else None
    result = search(phases=phases, progress=True)
    verify_document(result)
    content = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content)
    else:
        print(content, end='')


if __name__ == '__main__':
    main()
