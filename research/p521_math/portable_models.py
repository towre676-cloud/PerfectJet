"""Exact, parameterized FreeLIP provenance models for the P-521 x coordinate.

LLL discovers a finite lattice basis; all exclusions are independently checked
using integer arithmetic. A budget limit is unresolved, never an exclusion.
The historical low-word source models are distinguished from analytic wrappers.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import product
import json
from math import gcd, lcm
from pathlib import Path

from research.p521.freelip_recovery import A, M, P, GX, inverse, reduce_basis

HEADER_URL = "https://raw.githubusercontent.com/oreparaz/crypto-archeology/1de75d5681e620a49f2404c5760075f3e0664413/freelip_1.0/lip.h"
HEADER_SHA256 = "6f71e7255155d2c9ee759cfd8c0de8c075e52fb14efba0ca99d4594370ea910f"
NTL15_URL = "https://web.archive.org/web/19970801214429id_/http://www.cs.wisc.edu/~shoup/ntl/ntl-1.5.tar.Z"
NTL15_SHA256 = "c2d80c5293c824b16f89ac7e5e0aeb29e3996f8560b877c44858f41c43717e1c"
_CACHE = {}


def draw(state, count, width, output_slice="low", rejection=False):
    if not 1 <= width <= 106 or output_slice not in {"low", "high"}:
        raise ValueError("invalid output model")
    if rejection and output_slice != "low":
        raise ValueError("the original rejection sampler emits low words")
    base = 1 << width
    values, states = [], []
    for _ in range(count):
        state = A * state % M
        while rejection and state >= M - M % base:
            state = A * state % M
        values.append(state % base if output_slice == "low" else state >> (107-width))
        states.append(state)
    return values, states


def assemble(values, width, order="msb"):
    if order not in {"msb", "lsb"}:
        raise ValueError("invalid limb order")
    values = list(values)
    if order == "lsb":
        values.reverse()
    raw = 0
    for value in values:
        if not 0 <= value < 1 << width:
            raise ValueError("limb out of range")
        raw = (raw << width) | value
    return raw


def pack(values, width, order="msb", packing="mod-p"):
    raw = assemble(values, width, order)
    if packing in {"randomlen-520", "randomlen-521"}:
        bitlength = int(packing.split("-")[1])
        if order != "lsb" or len(values) != (bitlength+width-1)//width:
            raise ValueError("RandomLen uses low limbs first and exact limb count")
        return (raw & ((1 << (bitlength-1))-1)) | (1 << (bitlength-1))
    if packing == "mod-p":
        return raw % P
    if packing == "low-521":
        return raw & P
    if packing == "high-521":
        return raw >> max(0, width*len(values)-521)
    raise ValueError("invalid packing")


def rejection_gap_proof(width):
    """Positive modular dual witnesses bound every source rejection run."""
    if width <= 52:
        q = [9944586160332543, 21699637613853658]
    elif width == 62:
        q = [6610084184, 40481587063, 44879765762]
    else:
        raise ValueError("no rejection-run certificate for this width")
    r = M % (1 << width)
    result = {"width": width, "numerator": q, "modulus": M,
              "reject_distance_maximum": r,
              "minimum": sum(q), "maximum": r*sum(q),
              "maximum_consecutive_rejections": len(q)-1}
    if not verify_rejection_gap_proof(result):
        raise ArithmeticError("invalid rejection-run certificate")
    return result


def verify_rejection_gap_proof(proof):
    try:
        q, width = proof["numerator"], proof["width"]
        r = M % (1 << width)
        return (proof["modulus"] == M and len(q) >= 2
                and all(type(v) is int and v > 0 for v in q)
                and sum(v*pow(A, i, M) for i, v in enumerate(q)) % M == 0
                and proof["reject_distance_maximum"] == r
                and proof["minimum"] == sum(q)
                and proof["maximum"] == r*sum(q)
                and 0 < sum(q) <= r*sum(q) < M
                and proof["maximum_consecutive_rejections"] == len(q)-1)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def affine_problem(outputs, width, output_slice="low", gaps=None):
    outputs = list(outputs)
    if (len(outputs) < 2 or not 1 <= width <= 106
            or any(type(y) is not int or not 0 <= y < 1 << width for y in outputs)
            or output_slice not in {"low", "high"}):
        raise ValueError("invalid observations")
    gaps = list(gaps) if gaps is not None else [1]*(len(outputs)-1)
    if len(gaps) != len(outputs)-1 or any(type(g) is not int or g < 1 for g in gaps):
        raise ValueError("invalid gaps")
    exponents = [0]
    for gap in gaps:
        exponents.append(exponents[-1]+gap)
    powers = [pow(A, e, M) for e in exponents]
    if output_slice == "low":
        base = 1 << width
        inv_base = pow(base, -1, M)
        shift = [((power*outputs[0]-y)*inv_base) % M for power, y in zip(powers, outputs)]
        upper = [(M-1-y)//base for y in outputs]
    else:
        base = 1 << (107-width)
        shift = [(base*(power*outputs[0]-y)) % M for power, y in zip(powers, outputs)]
        upper = [min(base-1, M-1-base*y) for y in outputs]
    rows = [powers]
    for i in range(1, len(outputs)):
        row = [0]*len(outputs)
        row[i] = M
        rows.append(row)
    return rows, shift, upper


def _dual(outputs, width, output_slice, gaps, column):
    denominator = lcm(*(v.denominator for v in column))
    q = [int(v*denominator) for v in column]
    common = gcd(denominator, *q)
    denominator //= common
    q = [v//common for v in q]
    _, shift, upper = affine_problem(outputs, width, output_slice, gaps)
    low = sum(min(-s*v, (u-s)*v) for v, s, u in zip(q, shift, upper))
    high = sum(max(-s*v, (u-s)*v) for v, s, u in zip(q, shift, upper))
    return {"schema": "perfectjet/portable-dual-exclusion/1", "width": width,
            "output_slice": output_slice, "outputs": list(outputs), "gaps": list(gaps),
            "numerator": q, "denominator": denominator,
            "minimum": low, "maximum": high}


def verify_exclusion(certificate):
    try:
        if certificate["schema"] != "perfectjet/portable-dual-exclusion/1":
            return False
        q, den = certificate["numerator"], certificate["denominator"]
        rows, shift, upper = affine_problem(certificate["outputs"], certificate["width"],
                                            certificate["output_slice"], certificate["gaps"])
        if (type(den) is not int or den <= 0 or len(q) != len(upper)
                or any(type(v) is not int for v in q)
                or any(sum(v*w for v, w in zip(row, q)) % den for row in rows)):
            return False
        low = sum(min(-s*v, (u-s)*v) for v, s, u in zip(q, shift, upper))
        high = sum(max(-s*v, (u-s)*v) for v, s, u in zip(q, shift, upper))
        return (low == certificate["minimum"] and high == certificate["maximum"]
                and -((-low)//den) > high//den)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


def recover_outputs(outputs, width, output_slice="low", gaps=None, budget=100000):
    outputs = list(outputs)
    gaps = list(gaps) if gaps is not None else [1]*(len(outputs)-1)
    rows, shift, upper = affine_problem(outputs, width, output_slice, gaps)
    key = tuple(gaps)
    if key not in _CACHE:
        reduced = reduce_basis(rows)
        _CACHE[key] = reduced, inverse(reduced)
    reduced, inv = _CACHE[key]
    ranges = []
    for j in range(len(outputs)):
        column = [inv[i][j] for i in range(len(outputs))]
        low = sum(min(-s*v, (u-s)*v) for v, s, u in zip(column, shift, upper))
        high = sum(max(-s*v, (u-s)*v) for v, s, u in zip(column, shift, upper))
        lo, hi = -((-low.numerator)//low.denominator), high.numerator//high.denominator
        if lo > hi:
            certificate = _dual(outputs, width, output_slice, gaps, column)
            if not verify_exclusion(certificate):
                raise ArithmeticError("dual verification failed")
            return {"status": "excluded", "complete": True, "states": [], "certificate": certificate}
        ranges.append((lo, hi))
    size = 1
    for lo, hi in ranges:
        size *= hi-lo+1
    if size > budget:
        return {"status": "unresolved", "complete": False, "states": [], "coefficient_box_size": size}
    states = []
    for z in product(*(range(lo, hi+1) for lo, hi in ranges)):
        u = [shift[i]+sum(z[j]*reduced[j][i] for j in range(len(outputs))) for i in range(len(outputs))]
        if not all(0 <= v <= bound for v, bound in zip(u, upper)):
            continue
        xs = ([(1 << width)*v+y for v, y in zip(u, outputs)] if output_slice == "low"
              else [(1 << (107-width))*y+v for v, y in zip(u, outputs)])
        if all(xs[i+1] == pow(A, gaps[i], M)*xs[i] % M for i in range(len(xs)-1)):
            states.append(xs[0])
    return {"status": "recovered" if states else "excluded-by-enumeration", "complete": True,
            "states": states, "coefficient_box_size": size,
            "enumeration": {"basis": reduced, "ranges": ranges}}


def interior_sequences(target, width, count, order="msb", packing="mod-p"):
    """All full observed limbs for a Mersenne reduction or a bit-window wrapper."""
    if not 0 <= target <= P or order not in {"msb", "lsb"} or width*count >= 1042:
        raise ValueError("unsupported coordinate/layout")
    total = width*count
    if packing in {"randomlen-520", "randomlen-521"}:
        bitlength = int(packing.split("-")[1])
        if order != "lsb" or count != (bitlength+width-1)//width:
            raise ValueError("invalid RandomLen layout")
        if target.bit_length() != bitlength:
            return []
        # The last generated word is altered by the forced top bit. Omit that
        # complete word, even when bitlength is a multiple of the word width.
        first, last, prefixes = 0, (bitlength-1)//width-1, {target}
    elif total < 521:
        if target >= 1 << total:
            return []
        first, last, prefixes = 0, count-1, {target}
    elif packing == "mod-p":
        if target == P:
            return []
        h = total-521
        first, last = (h+width-1)//width, min(count-1, 521//width-1)
        offset, high_max = first*width, (1 << h)-1
        prefixes = set()
        for wrap in (0, 1):
            lo, hi = max(0, target+wrap*P-high_max), min(P, target+wrap*P)
            if lo <= hi:
                prefixes.update(range(lo >> offset, (hi >> offset)+1))
    elif packing in {"low-521", "high-521"}:
        offset = max(0, total-521) if packing == "high-521" else 0
        first, last = (offset+width-1)//width, (offset+521)//width-1
        prefixes = {(target << offset) >> (first*width)}
    else:
        raise ValueError("invalid packing")
    result = []
    for prefix in sorted(prefixes):
        values = [(prefix >> (width*(k-first))) % (1 << width) for k in range(first, last+1)]
        start = first
        if order == "msb":
            values.reverse()
            start = count-1-last
        result.append({"outputs": values, "first_output_index": start,
                       "lowest_limb": first, "highest_limb": last})
    return result


def _initial_states(emitting_state, accepted_index, width, rejection):
    inv_a = pow(A, -1, M)
    reject = M-M % (1 << width)
    state = emitting_state
    for _ in range(accepted_index):
        state = inv_a*state % M
        while rejection and state >= reject:
            state = inv_a*state % M
    state = inv_a*state % M
    candidates = [state]
    while rejection and state >= reject:
        state = inv_a*state % M
        candidates.append(state)
    return candidates


def recover_coordinate(target, width, count, order="msb", packing="mod-p",
                       output_slice="low", rejection=False):
    proof = rejection_gap_proof(width) if rejection else None
    gap_max = len(proof["numerator"]) if proof else 1
    records, candidates = [], []
    for interior in interior_sequences(target, width, count, order, packing):
        selected = interior["outputs"][:(4 if width >= 62 else 6)]
        if len(selected) < 2:
            return {"complete": False, "candidates": [], "status": "insufficient full limbs"}
        for gaps in product(range(1, gap_max+1), repeat=len(selected)-1):
            result = recover_outputs(selected, width, output_slice, gaps)
            records.append({"interior": interior, "observations_used": len(selected), "recovery": result})
            for state in result["states"]:
                if rejection and state >= M-M % (1 << width):
                    continue
                tail, _ = draw(state, len(selected)-1, width, output_slice, rejection)
                first = state % (1 << width) if output_slice == "low" else state >> (107-width)
                if [first]+tail != selected:
                    continue
                for initial in _initial_states(state, interior["first_output_index"], width, rejection):
                    values, states = draw(initial, count, width, output_slice, rejection)
                    if pack(values, width, order, packing) == target:
                        candidate = {"initial_state": initial, "limbs": values, "emitting_states": states}
                        if candidate not in candidates:
                            candidates.append(candidate)
    return {"schema": "perfectjet/portable-coordinate-recovery/1", "target": hex(target),
            "width": width, "limb_count": count, "order": order, "packing": packing,
            "output_slice": output_slice, "source_rejection": rejection,
            "complete": all(r["recovery"]["complete"] for r in records),
            "candidates": candidates, "branches": records, "rejection_gap_proof": proof}


def profile_specs():
    specs = []
    # Historical FreeLIP/NTL configurations first. Adjacent counts model small wrapper
    # changes; only ceil(521/NBITS)+1 with msb/mod-p is original zrandomb.
    for width in (30, 50, 62):
        source_count = (521+width-1)//width+1
        for count, order, packing in product(range(source_count-2, source_count+1),
                                               ("msb", "lsb"), ("mod-p", "low-521", "high-521")):
            support = ("source-zrandomb" if count == source_count and order == "msb" and packing == "mod-p"
                       else "wrapper-of-source-low-word-RNG")
            specs.append((width, count, order, packing, "low", True, support))
        for order, packing in product(("msb", "lsb"), ("mod-p", "low-521", "high-521")):
            specs.append((width, source_count, order, packing, "high", False,
                          "analytic-high-word-variant; not-original-zrandom"))
    for width in (31, 32):
        count = (521+width-1)//width+1
        for order, packing in product(("msb", "lsb"), ("mod-p", "low-521", "high-521")):
            support = ("analytic-only; odd-NBITS-rejected-by-header" if width == 31
                       else "custom-even-NBITS-on-64-bit; not-default")
            specs.append((width, count, order, packing, "low", True, support))
    for width, bitlength in product((26, 30, 50, 62), (520, 521)):
        specs.append((width, (bitlength+width-1)//width, "lsb", f"randomlen-{bitlength}",
                      "low", True, "source-NTL1.5-zrandoml-RandomLen" if width != 62
                      else "NTL1.5-zrandoml-wrapper-at-FreeLIP-ALPHA-width62"))
    return specs


def control_specs():
    # Recover known origins, including a seed forcing TWO width62 rejections.
    forced = pow(A, -1, M)*(M-3389828199694795) % M
    specs = []
    for width, output_slice, rejection in ((26, "low", True), (30, "low", True),
                                          (31, "low", True), (32, "low", True),
                                          (50, "low", True), (62, "low", True),
                                          (30, "high", False), (50, "high", False), (62, "high", False)):
        count = (521+width-1)//width+1
        seed = forced if width == 62 and rejection else 871002724
        for order, packing in product(("msb", "lsb"), ("mod-p", "low-521", "high-521")):
            specs.append((seed, width, count, order, packing, output_slice, rejection))
    for width, bitlength in product((26, 30, 50, 62), (520, 521)):
        specs.append((forced if width == 62 else 871002724, width, (bitlength+width-1)//width,
                      "lsb", f"randomlen-{bitlength}", "low", True))
    return specs


def run_suite():
    profiles, controls = [], []
    for width, count, order, packing, output_slice, rejection, support in profile_specs():
        result = recover_coordinate(GX, width, count, order, packing, output_slice, rejection)
        result["historical_support"] = support
        profiles.append(result)
    for seed, width, count, order, packing, output_slice, rejection in control_specs():
        values, _ = draw(seed, count, width, output_slice, rejection)
        target = pack(values, width, order, packing)
        result = recover_coordinate(target, width, count, order, packing, output_slice, rejection)
        candidate = next((c for c in result["candidates"] if c["initial_state"] == seed), None)
        controls.append({"width": width, "output_slice": output_slice, "source_rejection": rejection,
                         "limb_count": count, "order": order, "packing": packing,
                         "initial_state": seed, "target": hex(target), "candidate": candidate,
                         "complete": result["complete"], "recovered": candidate is not None})
        if candidate is None or not result["complete"]:
            raise ArithmeticError(f"positive control failed: {controls[-1]}")
    return {"schema": "perfectjet/portable-model-suite/1", "target": hex(GX),
            "sources": [{"url": HEADER_URL, "sha256": HEADER_SHA256,
                         "lines": {"ALPHA-and-ALPHA50": [533, 577], "default-and-SINGLE_MUL": [589, 595],
                                   "even-positive-less-than-long": [646, 659]}},
                        {"url": NTL15_URL, "sha256": NTL15_SHA256,
                         "supports": "Author-distributed NTL 1.5 captured 1997-08-01; zrandoml lines 4716-4755, ZZ.h RandomLen wrapper; MakeDesc.c 139-146 gives width30 on32-bit and50 on64-bit IEEEdouble53"},
                        {"url": "https://www.shoup.net/papers/factorimpl.pdf", "section": "8.2",
                         "supports": "LIP default radix 2^30 and alternative radix 2^26"}],
            "profiles": profiles, "synthetic_controls": controls,
            "all_controls_pass": all(c["recovered"] and c["complete"] for c in controls),
            "candidate_count": sum(len(p["candidates"]) for p in profiles),
            "all_profiles_complete": all(p["complete"] for p in profiles),
            "scope": "Finite declared FreeLIP multiplier/output/assembly families; no claim about other generators, curve security, or provenance uniqueness."}


def verify_document(document):
    """Verify the entire retained GX exclusion receipt without running LLL.

    Re-derive exact model, interior-prefix and raw-gap coverage; reject omitted,
    duplicate or rebound certificates. Positive controls retain full state replay.
    """
    try:
        if (document["schema"] != "perfectjet/portable-model-suite/1"
                or document["target"] != hex(GX) or document["candidate_count"] != 0
                or document["all_profiles_complete"] is not True
                or document["all_controls_pass"] is not True):
            return False
        profiles = document["profiles"]
        specs = profile_specs()
        if len(profiles) != len(specs):
            return False
        for profile, spec in zip(profiles, specs):
            width, count, order, packing, output_slice, rejection, support = spec
            fields = ("width", "limb_count", "order", "packing", "output_slice", "source_rejection", "historical_support")
            if (tuple(profile[k] for k in fields) != spec or profile["target"] != hex(GX)
                    or profile["schema"] != "perfectjet/portable-coordinate-recovery/1"
                    or profile["complete"] is not True or profile["candidates"] != []):
                return False
            proof = profile["rejection_gap_proof"]
            if rejection:
                if proof != rejection_gap_proof(width) or not verify_rejection_gap_proof(proof):
                    return False
                gap_max = len(proof["numerator"])
            else:
                if proof is not None:
                    return False
                gap_max = 1
            expected = []
            for interior in interior_sequences(GX, width, count, order, packing):
                selected = interior["outputs"][:(4 if width >= 62 else 6)]
                for gaps in product(range(1, gap_max+1), repeat=len(selected)-1):
                    expected.append((interior, selected, gaps))
            if len(profile["branches"]) != len(expected):
                return False
            for branch, (interior, selected, gaps) in zip(profile["branches"], expected):
                recovery = branch["recovery"]
                cert = recovery["certificate"]
                if (branch["interior"] != interior or branch["observations_used"] != len(selected)
                        or recovery["status"] != "excluded" or recovery["complete"] is not True
                        or recovery["states"] != [] or cert["width"] != width
                        or cert["output_slice"] != output_slice or cert["outputs"] != selected
                        or cert["gaps"] != list(gaps) or not verify_exclusion(cert)):
                    return False
        controls = document["synthetic_controls"]
        if len(controls) != len(control_specs()):
            return False
        for control, spec in zip(controls, control_specs()):
            seed, width, count, order, packing, output_slice, rejection = spec
            fields = ("initial_state", "width", "limb_count", "order", "packing", "output_slice", "source_rejection")
            if (tuple(control[k] for k in fields) != spec or control["complete"] is not True
                    or control["recovered"] is not True):
                return False
            values, states = draw(seed, count, width, output_slice, rejection)
            if (control["target"] != hex(pack(values, width, order, packing))
                    or control["candidate"] != {"initial_state": seed, "limbs": values, "emitting_states": states}):
                return False
        return True
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("results")/"portable-models.json")
    parser.add_argument("--verify", type=Path, help="verify a retained receipt offline; no LLL dependency needed")
    args = parser.parse_args()
    if args.verify:
        valid = verify_document(json.loads(args.verify.read_text()))
        print(json.dumps({"valid": valid, "mode": "offline-integer-receipt-verification"}))
        raise SystemExit(0 if valid else 1)
    result = run_suite()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({k: result[k] for k in ("candidate_count", "all_profiles_complete", "all_controls_pass")}))
