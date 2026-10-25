"""Independent verification of the Asterion e = 1 / e = 2 affine
linear stage (asterion_linear_e12.py).

Routes, all independent of the main extraction (which used greedily
selected tuples and an exact matrix inverse):

  A. Outcome check against the stored system
     (asterion_e{e}_system.json), read back from disk:
       - consistent: the stored particular solution and null-space
         basis satisfy / annihilate EVERY stored affine equation,
         exactly over Q;
       - inconsistent: the stored Farkas lambda is dotted against
         the stored rows.
  B. Contraction re-derivation of three full sectors: for each
     sector, every channel component is recomputed as
     f_J = <F, T_J> / <T_J, T_J> under the sl2-invariant pairing
     summed over ALL weight tuples of the sector; the channel Gram
     matrix is checked to be exactly diagonal (Schur orthogonality);
     the recomputed affine forms are compared exactly with the
     stored rows.  Sectors: an old sector (11,13,V_11,V_17), a
     d-trivial sector (1,7,V_7,1), a c-trivial sector
     (1,13,1,V_13).
  C. Global spot check: stored rows reproduce
     F(tuple) = sum_J f_J T_J(tuple) on random (sector, tuple) pairs.
  D. Bookkeeping: no stored sector is a diagonal (quadratic) sector;
     row counts and the diagonal-sector list match the results JSON.

Usage: python3 verify_e12.py --e {1,2} [--repo PATH]
Exit code 0 iff every check passes.
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
from fractions import Fraction as Q
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import asterion_linear_e12 as A  # noqa: E402

ZERO = Q(0)


def dualfac(m, p):
    return Q((-1) ** p, comb(2 * m, p))


def contraction_check(md, cp, stored, sectors_meta, sector):
    a, b, Bc, Bd = sector
    c, d = Bc[0], Bd[0]
    sid_t = next(sid for sid, s in enumerate(sectors_meta)
                 if s["sector"] == [a, b, list(Bc), list(Bd)])
    Js = A.sector_channels(a, b, c, d)
    sector_rows = {}
    for (sid, J, coeffs, const) in stored:
        if sid == sid_t:
            sector_rows[J] = (coeffs, const)
    assert sorted(sector_rows) == Js, (sector, sorted(sector_rows), Js)

    tot_wt = a + b + c + d
    tuples = []
    for i in range(2 * a + 1):
        for j in range(2 * b + 1):
            for k in range(2 * c + 1):
                l = tot_wt - i - j - k
                if 0 <= l <= 2 * d:
                    tuples.append((i, j, k, l))
    print(f"   sector {sector}: {len(tuples)} weight tuples, channels {Js}")

    def chan_val_dual(J, t):
        i, j, k, l = t
        fac = (dualfac(a, i) * dualfac(b, j) * dualfac(c, k) * dualfac(d, l))
        if not fac:
            return ZERO
        return fac * A.chan_val(md, a, b, c, d, J,
                                2 * a - i, 2 * b - j, 2 * c - k, 2 * d - l)

    gram = {J: ZERO for J in Js}
    cross = ZERO
    tdual = {}
    for t in tuples:
        tv = [A.chan_val(md, a, b, c, d, J, *t) for J in Js]
        td = [chan_val_dual(J, t) for J in Js]
        tdual[t] = td
        for x in range(len(Js)):
            if tv[x] and td[x]:
                gram[Js[x]] += tv[x] * td[x]
            for y in range(x + 1, len(Js)):
                if tv[x] and td[y]:
                    cross += tv[x] * td[y]
                if tv[y] and td[x]:
                    cross += tv[y] * td[x]
    print(f"   Gram off-diagonal sum (must be 0): {cross}; "
          f"diagonal all nonzero: {all(gram[J] for J in Js)}")
    ok = (cross == 0) and all(gram[J] for J in Js)

    num = {J: A.AFF_ZERO for J in Js}
    for t in tuples:
        td = tdual[t]
        if not any(td):
            continue
        Jv = cp.jacobi((a, t[0]), (b, t[1]), (Bc, t[2]))
        f_aff = cp.pair_w(Jv, (Bd, t[3]))
        for x, J in enumerate(Js):
            if td[x]:
                num[J] = A.aff_add(num[J], A.aff_scale(f_aff, td[x]))
    for J in Js:
        f_contr = A.aff_scale(num[J], 1 / gram[J])
        coeffs_s, const_s = sector_rows[J]
        match = (f_contr[0] == const_s and f_contr[1] == coeffs_s)
        print(f"   J={J}: contraction const = {f_contr[0]}, "
              f"params = {len(f_contr[1])}; stored const = {const_s}, "
              f"params = {len(coeffs_s)}; match = {match}")
        ok &= match
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e", type=int, required=True, choices=(1, 2))
    ap.add_argument("--repo", type=Path, default=HERE.parents[1] / "PerfectJet")
    args = ap.parse_args()
    e = args.e
    ok = True

    results = json.loads((HERE / f"asterion_e{e}_results.json").read_text())
    res = results["result"]
    sectors_meta = results["system"]["sectors"]
    diag_meta = results["system"]["diagonal_sectors"]

    stored = []
    with open(HERE / f"asterion_e{e}_system.json") as fh:
        for line in fh:
            d = json.loads(line)
            stored.append((d["sector"], d["J"],
                           {int(k): Q(v) for k, v in d["coeffs"].items()},
                           Q(d["const"])))
    print(f"e={e}: loaded {len(stored)} stored affine equations; "
          f"outcome = {res['outcome']}")

    # ---- D. bookkeeping -------------------------------------------------
    print("D. bookkeeping:")
    cp0 = A.Completion(A.Model(args.repo), e)
    bad_stored = 0
    for s in sectors_meta:
        a, b = s["sector"][0], s["sector"][1]
        Bc = tuple(s["sector"][2])
        Bd = tuple(s["sector"][3])
        if A.is_diagonal_sector(cp0, a, b, Bc, Bd):
            bad_stored += 1
    n_diag_ch = sum(len(s["channels_J"]) for s in diag_meta)
    print(f"   stored sectors that are diagonal: {bad_stored} (must be 0); "
          f"diagonal sectors deferred: {len(diag_meta)} with {n_diag_ch} "
          f"channel equations")
    ok &= (bad_stored == 0 and len(diag_meta) == 49 and n_diag_ch == 1205)
    ok &= (len(stored) == results["counts"]["channel_equations_affine"])

    # ---- A. outcome check ----------------------------------------------
    print("A. outcome check against all stored rows:")
    if res["outcome"] == "consistent":
        particular = [Q(x) for x in res["particular"]]
        null_basis = [[Q(x) for x in vec] for vec in res["null_basis"]]
        bad_rows = 0
        for (sid, J, coeffs, const) in stored:
            val = const
            for k, v in coeffs.items():
                if particular[k]:
                    val += v * particular[k]
            if val:
                bad_rows += 1
                continue
            for vec in null_basis:
                s = ZERO
                for k, v in coeffs.items():
                    if vec[k]:
                        s += v * vec[k]
                if s:
                    bad_rows += 1
                    break
        a_ok = (bad_rows == 0
                and len(null_basis) == res["solution_dimension"])
        print(f"   particular + {len(null_basis)} null vectors satisfy all "
              f"{len(stored)} rows: {a_ok} (bad rows: {bad_rows})")
        ok &= a_ok
    else:
        fk = res["farkas"]
        lam = [Q(x) for x in fk["lambda"]]
        frows = fk["rows"]
        support = [(frows[i], lam[i]) for i in range(len(frows)) if lam[i]]
        coeff_sum = {}
        const_sum = ZERO
        for ri, li in support:
            _sid, _J, coeffs, const = stored[ri]
            for k, v in coeffs.items():
                coeff_sum[k] = coeff_sum.get(k, ZERO) + li * v
            const_sum += li * const
        a_ok = (all(not v for v in coeff_sum.values()) and const_sum != 0
                and str(const_sum) == fk["constant_sum"])
        print(f"   Farkas support size {len(support)}; combined coefficients "
              f"all zero: {all(not v for v in coeff_sum.values())}; "
              f"constant sum = {const_sum}; match = {a_ok}")
        ok &= a_ok

    # ---- model -----------------------------------------------------------
    md = A.Model(args.repo)
    cp = A.Completion(md, e)

    # ---- B. contraction checks -------------------------------------------
    print("B. contraction verification of three sectors:")
    for sector in [(11, 13, (11, 0), (17, 0)),
                   (1, 7, (7, 0), (0, 0)),
                   (1, 13, (0, 0), (13, 0))]:
        ok &= contraction_check(md, cp, stored, sectors_meta, sector)

    # ---- C. global spot check ---------------------------------------------
    rows_by_sector = {}
    for (sid, J, coeffs, const) in stored:
        rows_by_sector.setdefault(sid, {})[J] = (coeffs, const)
    rng = random.Random(1234)
    c_ok = True
    tested = 0
    for _ in range(300):
        sid = rng.randrange(len(sectors_meta))
        sa, sb = sectors_meta[sid]["sector"][0], sectors_meta[sid]["sector"][1]
        Bc = tuple(sectors_meta[sid]["sector"][2])
        Bd = tuple(sectors_meta[sid]["sector"][3])
        Js_s = sectors_meta[sid]["channels_J"]
        tw = sa + sb + Bc[0] + Bd[0]
        for _try in range(20):
            i = rng.randrange(2 * sa + 1)
            j = rng.randrange(2 * sb + 1)
            k = rng.randrange(2 * Bc[0] + 1)
            l = tw - i - j - k
            if 0 <= l <= 2 * Bd[0]:
                break
        else:
            continue
        Jv = cp.jacobi((sa, i), (sb, j), (Bc, k))
        f_aff = cp.pair_w(Jv, (Bd, l))
        recon = A.AFF_ZERO
        for J in Js_s:
            coeffs_s, const_s = rows_by_sector[sid][J]
            tv = A.chan_val(md, sa, sb, Bc[0], Bd[0], J, i, j, k, l)
            if tv:
                recon = A.aff_add(recon, A.aff_scale((const_s, coeffs_s), tv))
        tested += 1
        if recon != f_aff:
            c_ok = False
            print(f"   global spot failure: sector "
                  f"{sectors_meta[sid]['sector']} tuple {(i, j, k, l)}")
            break
    print(f"C. global spot check on {tested} random (sector, tuple) pairs: {c_ok}")
    ok &= c_ok

    print("ALL CHECKS PASSED" if ok else "VERIFICATION FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
