"""Exact low-limb FreeLIP reconstruction and dual-lattice exclusions.

The historical generator is public: state <- 3**121 * state mod (2**107-1)
and each draw exposes its low 26 bits.  A successful dual certificate excludes
*every* generator state for one declared limb sequence, with integer arithmetic.
LLL is only a certificate discovery procedure; verification does not trust it.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
import hashlib
import json

M = (1 << 107) - 1
A = pow(3, 121, M)
BITS = 26
B = 1 << BITS
P = (1 << 521) - 1
GX = int("00c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66", 16)


def draw(state: int, count: int, rejection=False):
    """Return low limbs and the states that emitted them."""
    limbs, states = [], []
    for _ in range(count):
        state = A * state % M
        while rejection and state >= M-(M % B):
            state = A * state % M
        limbs.append(state % B)
        states.append(state)
    return limbs, states


def assemble(limbs, order="msb"):
    if order not in {"msb", "lsb"}:
        raise ValueError("order must be msb or lsb")
    limbs = list(limbs)
    if order == "lsb":
        limbs.reverse()
    raw = 0
    for value in limbs:
        if not 0 <= value < B:
            raise ValueError("limb outside 26-bit range")
        raw = (raw << BITS) | value
    return raw


def _gs(rows):
    n = len(rows)
    star, mu, norms = [], [[Fraction(0) for _ in rows] for _ in rows], []
    for i in range(n):
        v = list(map(Fraction, rows[i]))
        for j in range(i):
            mu[i][j] = sum(Fraction(rows[i][k]) * star[j][k] for k in range(n)) / norms[j]
            for k in range(n):
                v[k] -= mu[i][j] * star[j][k]
        star.append(v)
        norms.append(sum(x*x for x in v))
    return mu, norms


def _nearest(x):
    return (2*x.numerator+x.denominator) // (2*x.denominator)


def reduce_basis(rows):
    """Use fpylll if available, otherwise a small exact rational LLL."""
    try:
        from fpylll import IntegerMatrix, LLL
        matrix = IntegerMatrix.from_matrix(rows)
        LLL.reduction(matrix)
        return [[int(matrix[i, j]) for j in range(len(rows))] for i in range(len(rows))]
    except ImportError:
        pass
    rows = [r[:] for r in rows]
    k = 1
    mu, norms = _gs(rows)
    while k < len(rows):
        for j in range(k-1, -1, -1):
            q = _nearest(mu[k][j])
            if q:
                rows[k] = [x-q*y for x, y in zip(rows[k], rows[j])]
                mu, norms = _gs(rows)
        if norms[k] >= (Fraction(3, 4)-mu[k][k-1]**2)*norms[k-1]:
            k += 1
        else:
            rows[k], rows[k-1] = rows[k-1], rows[k]
            mu, norms = _gs(rows)
            k = max(1, k-1)
    return rows


def inverse(rows):
    n = len(rows)
    t = [[Fraction(x) for x in rows[i]] + [Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if t[i][j])
        t[j], t[pivot] = t[pivot], t[j]
        divisor = t[j][j]
        t[j] = [v/divisor for v in t[j]]
        for i in range(n):
            if i != j:
                q = t[i][j]
                t[i] = [v-q*w for v, w in zip(t[i], t[j])]
    return [r[n:] for r in t]


def _ceil(x):
    return -((-x.numerator)//x.denominator)


def affine_problem(outputs, gaps=None):
    """States B*u_i+y_i give u=d+L, inside an explicit integer box."""
    outputs = list(outputs)
    if len(outputs) < 2 or any(type(y) is not int or not 0 <= y < B for y in outputs):
        raise ValueError("need at least two 26-bit outputs")
    n = len(outputs)
    if gaps is None:
        gaps = [1]*(n-1)
    if len(gaps) != n-1 or any(type(g) is not int or g not in (1, 2) for g in gaps):
        raise ValueError("gaps must contain one or two raw steps")
    exponents = [0]
    for gap in gaps:
        exponents.append(exponents[-1]+gap)
    powers = [pow(A, i, M) for i in exponents]
    inv_b = pow(B, -1, M)
    shift = [((powers[i]*outputs[0]-outputs[i])*inv_b) % M for i in range(n)]
    upper = [(M-1-y)//B for y in outputs]
    rows = [powers]
    for i in range(1, n):
        r = [0]*n
        r[i] = M
        rows.append(r)
    return rows, shift, upper


def _dual_certificate(outputs, column, gaps):
    from math import lcm, gcd
    denominator = lcm(*(v.denominator for v in column))
    numerator = [int(v*denominator) for v in column]
    common = gcd(denominator, *numerator)
    denominator //= common
    numerator = [v//common for v in numerator]
    rows, shift, upper = affine_problem(outputs, gaps)
    low = sum(min(-s*q, (u-s)*q) for q, s, u in zip(numerator, shift, upper))
    high = sum(max(-s*q, (u-s)*q) for q, s, u in zip(numerator, shift, upper))
    return {"schema": "perfectjet/freelip-dual-exclusion/1", "outputs": list(outputs), "gaps": list(gaps),
            "numerator": numerator, "denominator": denominator,
            "minimum": low, "maximum": high}


def verify_exclusion(certificate):
    """Check divisibility on lattice generators and absence of a box multiple."""
    if certificate.get("schema") != "perfectjet/freelip-dual-exclusion/1":
        return False
    try:
        outputs = certificate["outputs"]
        q, den = certificate["numerator"], certificate["denominator"]
        if (type(den) is not int or den <= 0 or len(q) != len(outputs)
                or any(type(v) is not int for v in q)
                or type(certificate["minimum"]) is not int
                or type(certificate["maximum"]) is not int):
            return False
        rows, shift, upper = affine_problem(outputs, certificate.get("gaps"))
        if any(sum(v*w for v, w in zip(row, q)) % den for row in rows):
            return False
        low = sum(min(-s*v, (u-s)*v) for v, s, u in zip(q, shift, upper))
        high = sum(max(-s*v, (u-s)*v) for v, s, u in zip(q, shift, upper))
        if low != certificate["minimum"] or high != certificate["maximum"]:
            return False
        return -((-low)//den) > high//den
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


_BASIS_CACHE = {}


def recover_low_outputs(outputs, max_candidates=100000, gaps=None):
    """Return emitting states or a self-contained all-state exclusion proof.

    Completeness holds only when coefficient-box enumeration finishes.  A work
    budget is always reported as unresolved, never as an empty feasible set.
    """
    outputs = list(outputs)
    gaps = list(gaps) if gaps is not None else [1]*(len(outputs)-1)
    rows, shift, upper = affine_problem(outputs, gaps)
    key = tuple(gaps)
    if key not in _BASIS_CACHE:
        reduced = reduce_basis(rows)
        _BASIS_CACHE[key] = reduced, inverse(reduced)
    reduced, inv = _BASIS_CACHE[key]
    ranges = []
    for j in range(len(outputs)):
        col = [inv[i][j] for i in range(len(outputs))]
        low = sum(min(-s*q, (u-s)*q) for q, s, u in zip(col, shift, upper))
        high = sum(max(-s*q, (u-s)*q) for q, s, u in zip(col, shift, upper))
        lo, hi = _ceil(low), high.numerator//high.denominator
        if lo > hi:
            cert = _dual_certificate(outputs, col, gaps)
            if not verify_exclusion(cert):
                raise ArithmeticError("internal dual certificate failed")
            return {"status": "excluded", "complete": True, "states": [], "certificate": cert}
        ranges.append((lo, hi))
    count = 1
    for lo, hi in ranges:
        count *= hi-lo+1
    if count > max_candidates:
        return {"status": "unresolved", "complete": False, "coefficient_box_size": count, "states": []}
    states = []
    for z in product(*(range(lo, hi+1) for lo, hi in ranges)):
        u = [shift[i]+sum(z[j]*reduced[j][i] for j in range(len(outputs))) for i in range(len(outputs))]
        if not all(0 <= v <= bound for v, bound in zip(u, upper)):
            continue
        xs = [B*v+y for v, y in zip(u, outputs)]
        if all(xs[i+1] == pow(A, gaps[i], M)*xs[i] % M for i in range(len(xs)-1)):
            states.append(xs[0])
    # This branch is an exact finite enumeration.  For exclusion with no simple
    # dual slab, preserve the reduced basis and the full finite coefficient box.
    return {"status": "recovered" if states else "excluded-by-enumeration", "complete": True,
            "states": states, "coefficient_box_size": count,
            "enumeration": {"basis": reduced, "ranges": ranges}}


def interior_sequences(target=GX, count=22, order="msb"):
    """Enumerate every possible consecutive full-limb observation block.

    For a raw 26*count bit value W and p=2**521-1, reduction folds its high
    h=max(0,26*count-521) bits into the bottom.  Above ceil(h/26) limbs only a
    single subtraction carry can change the prefix.  The interval computation
    handles also zero and other unusually small synthetic target values.
    """
    if not 0 <= target < P or count not in {20, 21, 22} or order not in {"msb", "lsb"}:
        raise ValueError("unsupported target/layout")
    total_bits = BITS*count
    if total_bits < 521:
        if target >= 1 << total_bits:
            return []
        indexes = list(range(count))
        values = [(target >> (BITS*k)) % B for k in indexes]
        if order == "msb":
            values.reverse()
        return [{"outputs": values, "first_output_index": 0, "prefix": target,
                 "lowest_limb": 0, "highest_limb": count-1}]
    h = max(0, total_bits-521)
    first = (h+BITS-1)//BITS
    last = min(count-1, 521//BITS-1)
    offset = first*BITS
    high_max = (1 << h)-1
    prefixes = set()
    for wrap in (0, 1):
        low = max(0, target+wrap*P-high_max)
        high = min(P, target+wrap*P)
        if low <= high:
            prefixes.update(range(low >> offset, (high >> offset)+1))
    records = []
    for prefix in sorted(prefixes):
        values = [(prefix >> (BITS*(k-first))) % B for k in range(first, last+1)]
        start = first
        if order == "msb":
            values.reverse()
            start = count-1-last
        records.append({"outputs": values, "first_output_index": start,
                        "prefix": prefix, "lowest_limb": first, "highest_limb": last})
    return records


def no_consecutive_rejections():
    """Integer dual witness that the source rejection loop never skips twice."""
    q = [9944586160332543, 21699637613853658]
    r = M % B
    low, high = sum(q), r*sum(q)
    if (q[0]+A*q[1]) % M or not 0 < low <= high < M:
        raise ArithmeticError("no-consecutive-rejections witness failed")
    return {"schema": "perfectjet/freelip-rejection-gap/1", "numerator": q,
            "denominator": M, "reject_distance_minimum": 1,
            "reject_distance_maximum": r, "minimum": low, "maximum": high,
            "conclusion": "Accepted low26 draws have raw recurrence gaps one or two."}


def _source_initial_states(emitting_state, accepted_index):
    inv_a = pow(A, -1, M)
    reject_minimum = M-(M % B)
    state = emitting_state
    for _ in range(accepted_index):
        state = inv_a*state % M
        if state >= reject_minimum:
            state = inv_a*state % M
    predecessor = inv_a*state % M
    states = [predecessor]
    if predecessor >= reject_minimum:
        states.append(inv_a*predecessor % M)
    return states


def recover_coordinate(target=GX, count=22, order="msb", observation_count=8, rejection=False):
    """Recover or exactly exclude all initial states for a coordinate layout."""
    records = []
    candidates = []
    for interior in interior_sequences(target, count, order):
        selected = interior["outputs"][:observation_count]
        patterns = product((1, 2), repeat=len(selected)-1) if rejection else [[1]*(len(selected)-1)]
        for gaps in patterns:
            recovered = recover_low_outputs(selected, gaps=gaps)
            record = {"interior": interior, "observations_used": len(selected), "recovery": recovered}
            for state in recovered["states"]:
                if rejection:
                    if state >= M-(M % B):
                        continue
                    # The integer relaxation did not impose rejection of skipped
                    # states. Replaying the actual source loop filters it exactly.
                    output_tail, _ = draw(state, len(selected)-1, rejection=True)
                    if [state % B]+output_tail != selected:
                        continue
                    initial_states = _source_initial_states(state, interior["first_output_index"])
                else:
                    initial_states = [state * pow(A, -(interior["first_output_index"]+1), M) % M]
                for initial in initial_states:
                    limbs, _ = draw(initial, count, rejection=rejection)
                    if assemble(limbs, order) % P == target:
                        candidate = {"initial_state": initial, "limbs": limbs}
                        if candidate not in candidates:
                            candidates.append(candidate)
            records.append(record)
    return {"schema": "perfectjet/freelip-coordinate-recovery/1", "target": hex(target),
            "limb_count": count, "order": order, "source_rejection": rejection,
            "complete": all(r["recovery"]["complete"] for r in records),
            "candidates": candidates, "branches": records,
            "scope": "All 107-bit states of the specified multiplier, low26 output and limb assembly only.",
            "rejection_gap_proof": no_consecutive_rejections() if rejection else None}


def run_suite(rejection=False):
    profiles = [recover_coordinate(count=count, order=order, rejection=rejection) for count in (20, 21, 22) for order in ("msb", "lsb")]
    controls = []
    for state in (20000, 871002724, 123456789012345678901234567890):
        for count in (20, 21, 22):
            for order in ("msb", "lsb"):
                limbs, _ = draw(state, count, rejection=rejection)
                target = assemble(limbs, order) % P
                result = recover_coordinate(target, count, order, rejection=rejection)
                ok = any(c["initial_state"] == state for c in result["candidates"])
                controls.append({"initial_state": state, "limb_count": count, "order": order,
                                 "complete": result["complete"], "recovered": ok,
                                 "candidate_count": len(result["candidates"])})
                if not ok:
                    raise ArithmeticError("synthetic recovery control failed")
    return {"schema": "perfectjet/freelip-recovery-suite/1", "source_rejection": rejection,
            "profiles": profiles, "synthetic_controls": controls,
            "all_controls_pass": all(c["recovered"] for c in controls)}


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("results")/"freelip-recovery.json")
    parser.add_argument("--source-rejection", action="store_true", help="model the historical low26 rejection loop exactly")
    args = parser.parse_args()
    result = run_suite(rejection=args.source_rejection)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(result, indent=2, sort_keys=True)+"\n"
    args.output.write_text(encoded)
    print(json.dumps({"profiles": len(result["profiles"]), "all_controls_pass": result["all_controls_pass"],
                      "coordinate_candidates": sum(len(p["candidates"]) for p in result["profiles"]),
                      "sha256": hashlib.sha256(encoded.encode()).hexdigest()}))
