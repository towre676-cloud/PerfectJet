"""Independent verification of the Asterion e=0 inconsistency certificate.

The main run (asterion_linear.py) found the affine-linear (g0, g0, W)
Jacobi system for dimension 493 INCONSISTENT.  In fact 434 of the
22688 channel equations are nonzero constants with all 169 parameter
coefficients equal to zero; each one is by itself a Farkas-style
inconsistency certificate.  The headline certificate is row 826:
sector (a, b, c, d) = (7, 7, 7, 7), intermediate spin J = 1,

    f = 1/750140620033193209655193330568396800000000  !=  0,

with stored lambda 750140620033193209655193330568396800000000 giving
constant sum exactly 1.

This script re-verifies the claim through routes independent of the
main extraction (which used greedily selected tuples and a matrix
inverse):

  A. Farkas dot products: the stored lambda is dotted against the
     stored system rows (asterion_linear_system.json).
  B/E. Contraction extraction: for sectors (7,7,7,7) and (7,11,7,11),
     every channel component is recomputed as
     f_J = <F, T_J> / <T_J, T_J>, where <U, V> is the sl2-invariant
     pairing sum_t U(t) V(t*) over ALL weight tuples t of the sector
     (t* = beta-dual tuple).  The Gram matrix of the channel tensors
     is checked to be exactly diagonal (Schur orthogonality), which
     validates the formula; the recomputed affine forms are compared
     exactly against the stored rows of the sector.
  C. Residual identity: on fresh random tuples of sector (7,7,7,7),
     F(tuple) = sum_J f_J T_J(tuple) as affine forms.
  D. Global spot check: for random sectors and random weight tuples
     across the whole system, the stored rows reproduce
     F(tuple) = sum_J f_J T_J(tuple).

Usage: python3 verify_certificate.py [--repo PATH]
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
import asterion_linear as AL  # noqa: E402

ZERO = Q(0)


def dualfac(m, p):
    return Q((-1) ** p, comb(2 * m, p))


def contraction_check(md, cp, stored, sectors_meta, sector, do_residual=False):
    """Full contraction verification of one sector. Returns True/False."""
    a, b, c, d = sector
    sid_t = next(sid for sid, s in enumerate(sectors_meta)
                 if s["sector"] == list(sector))
    Js = AL.sector_channels(a, b, c, d)
    sector_rows = {}
    for (sid, J, coeffs, const) in stored:
        if sid == sid_t:
            sector_rows[J] = (coeffs, const)
    assert sorted(sector_rows) == Js

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
        return fac * AL.chan_val(md, a, b, c, d, J,
                                 2 * a - i, 2 * b - j, 2 * c - k, 2 * d - l)

    gram = {J: ZERO for J in Js}
    cross = ZERO
    tdual = {}
    for t in tuples:
        tv = [AL.chan_val(md, a, b, c, d, J, *t) for J in Js]
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

    num = {J: AL.AFF_ZERO for J in Js}
    for t in tuples:
        td = tdual[t]
        if not any(td):
            continue
        Jv = cp.jacobi((a, t[0]), (b, t[1]), (c, t[2]))
        f_aff = cp.pair_w(Jv, (d, t[3]))
        for x, J in enumerate(Js):
            if td[x]:
                num[J] = AL.aff_add(num[J], AL.aff_scale(f_aff, td[x]))
    for J in Js:
        f_contr = AL.aff_scale(num[J], 1 / gram[J])
        coeffs_s, const_s = sector_rows[J]
        match = (f_contr[0] == const_s and f_contr[1] == coeffs_s)
        print(f"   J={J}: contraction const = {f_contr[0]}, "
              f"params = {len(f_contr[1])}; stored const = {const_s}, "
              f"params = {len(coeffs_s)}; match = {match}")
        ok &= match

    if do_residual:
        rng = random.Random(99)
        fresh = [t for t in tuples if rng.random() < 0.05][:40]
        r_ok = True
        for t in fresh:
            Jv = cp.jacobi((a, t[0]), (b, t[1]), (c, t[2]))
            f_aff = cp.pair_w(Jv, (d, t[3]))
            recon = AL.AFF_ZERO
            for J in Js:
                coeffs_s, const_s = sector_rows[J]
                tv = AL.chan_val(md, a, b, c, d, J, *t)
                if tv:
                    recon = AL.aff_add(recon, AL.aff_scale((const_s, coeffs_s), tv))
            if recon != f_aff:
                r_ok = False
                print(f"   residual failure at tuple {t}")
        print(f"   residual identity on {len(fresh)} fresh tuples: {r_ok}")
        ok &= r_ok
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path,
                    default=HERE.parents[1] / "PerfectJet")
    args = ap.parse_args()
    ok = True

    results = json.loads((HERE / "asterion_linear_results.json").read_text())
    res = results["result"]
    assert res["outcome"] == "inconsistent", res["outcome"]
    fk = res["farkas"]
    lam = [Q(x) for x in fk["lambda"]]
    frows = fk["rows"]
    sectors_meta = results["system"]["sectors"]

    stored = []
    with open(HERE / "asterion_linear_system.json") as fh:
        for line in fh:
            d = json.loads(line)
            stored.append((d["sector"], d["J"],
                           {int(k): Q(v) for k, v in d["coeffs"].items()},
                           Q(d["const"])))
    print(f"loaded {len(stored)} stored equations")

    # ---- A. Farkas dot products ---------------------------------------
    support = [(frows[i], lam[i]) for i in range(len(frows)) if lam[i]]
    print("A. Farkas support (row, lambda):", support)
    coeff_sum = {}
    const_sum = ZERO
    for ri, li in support:
        _sid, _J, coeffs, const = stored[ri]
        for k, v in coeffs.items():
            coeff_sum[k] = coeff_sum.get(k, ZERO) + li * v
        const_sum += li * const
    a_ok = all(not v for v in coeff_sum.values()) and const_sum != 0
    print(f"   combined coefficients all zero: "
          f"{all(not v for v in coeff_sum.values())}; constant sum = {const_sum}")
    ok &= a_ok
    target_row = support[0][0]
    sid_t, J_t, coeffs_t, const_t = stored[target_row]
    print(f"   obstructing row {target_row}: sector "
          f"{sectors_meta[sid_t]['sector']}, J = {J_t}, coeffs = {coeffs_t}, "
          f"const = {const_t}")

    # ---- model ---------------------------------------------------------
    md = AL.Model(args.repo)
    cp = AL.Completion(md)

    # ---- B. contraction, sector (7,7,7,7), with residual check --------
    print("B. contraction verification, sector (7,7,7,7):")
    ok &= contraction_check(md, cp, stored, sectors_meta, (7, 7, 7, 7),
                            do_residual=True)

    # ---- E. contraction, sector (7,11,7,11) ----------------------------
    print("E. contraction verification, sector (7,11,7,11):")
    ok &= contraction_check(md, cp, stored, sectors_meta, (7, 11, 7, 11))

    # ---- D. global spot check ------------------------------------------
    rows_by_sector = {}
    for (sid, J, coeffs, const) in stored:
        rows_by_sector.setdefault(sid, {})[J] = (coeffs, const)
    rng = random.Random(1234)
    d_ok = True
    tested = 0
    for _ in range(300):
        sid = rng.randrange(len(sectors_meta))
        sa, sb, sc, sd = sectors_meta[sid]["sector"]
        Js_s = sectors_meta[sid]["channels_J"]
        tw = sa + sb + sc + sd
        for _try in range(20):
            i = rng.randrange(2 * sa + 1)
            j = rng.randrange(2 * sb + 1)
            k = rng.randrange(2 * sc + 1)
            l = tw - i - j - k
            if 0 <= l <= 2 * sd:
                break
        else:
            continue
        Jv = cp.jacobi((sa, i), (sb, j), (sc, k))
        f_aff = cp.pair_w(Jv, (sd, l))
        recon = AL.AFF_ZERO
        for J in Js_s:
            coeffs_s, const_s = rows_by_sector[sid][J]
            tv = AL.chan_val(md, sa, sb, sc, sd, J, i, j, k, l)
            if tv:
                recon = AL.aff_add(recon, AL.aff_scale((const_s, coeffs_s), tv))
        tested += 1
        if recon != f_aff:
            d_ok = False
            print(f"   global spot failure: sector {(sa, sb, sc, sd)} "
                  f"tuple {(i, j, k, l)}")
            break
    print(f"D. global spot check on {tested} random (sector, tuple) pairs: {d_ok}")
    ok &= d_ok

    print("ALL CHECKS PASSED" if ok else "VERIFICATION FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
