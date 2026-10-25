"""Validation of the assembled diagonal polynomial systems.

For each e in {1, 2}:
  (A) Channel-identity check on the solution space.  For several
      random rational points z (with sigma != 0 resp. det S11 != 0),
      params = sum_i z_i basis_i are fed to stage two's exact numeric
      model (every bracket checked against its defining pairings,
      S_11 inverted exactly).  For sampled weight tuples in ALL 49
      diagonal sectors, the identity

          denom(z) * F_numeric(tuple)
              = sum_J G_J(z) * chan_val(tuple, J)

      must hold exactly, where denom = sigma (e=1) or det S11 (e=2)
      and G_J are the assembled restricted polynomials.  This is the
      defining property of the channel components, checked at tuples
      other than the extraction tuples.
  (B) Parameter-level spot check of stage two's quadratic evidence:
      in sector (7,7,7,7), with all params zero except S_11 = I and
      the single mixed channel recorded in stage two's results, the
      parameter-level assembled polynomials must reproduce the
      recorded numeric F values at p = 0, 1, 2 (sigma = 1 there, so
      the cleared and uncleared values coincide).

Exact rational arithmetic throughout.  Exits nonzero on any failure.
"""
from __future__ import annotations

import importlib.util
import json
import random
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "asm", HERE / "assemble_diagonal.py")
ASM = importlib.util.module_from_spec(spec)
# prevent assemble's __main__ block; module import is safe (guarded).
spec.loader.exec_module(ASM)
S2 = ASM.S2
ZERO = Q(0)


def poly_eval(poly_json, point):
    total = ZERO
    for mstr, cstr in poly_json.items():
        mon = tuple(int(x) for x in mstr.split(",")) if mstr else ()
        v = Q(cstr)
        for i in mon:
            v *= point[i]
        total += v
    return total


def main():
    repo = HERE.parents[1]  # repository root, when run from independent_checks/asterion_completion/
    md = S2.Model(repo)
    rng = random.Random(987654321)
    failures = 0
    for e in (1, 2):
        cp = S2.Completion(md, e)
        res = json.loads((HERE / f"asterion_e{e}_results.json").read_text())
        basis = [[Q(x) for x in vec] for vec in res["result"]["null_basis"]]
        nz = len(basis)
        data = json.loads((HERE / f"diagonal_e{e}_polys.json").read_text())
        datap = json.loads((HERE / f"diagonal_e{e}_params.json").read_text())
        by_sector = {}
        for eq in data["equations"]:
            by_sector.setdefault(tuple(eq["sector"][0:2]) +
                                 (tuple(eq["sector"][2]),
                                  tuple(eq["sector"][3])), []).append(eq)
        # --- (A) solution-space channel identity
        checks_a = 0
        for trial in range(4):
            while True:
                z = [Q(rng.randrange(-4, 5), rng.choice((1, 1, 2)))
                     for _ in range(nz)]
                if e == 1:
                    denom = z[11]
                else:
                    denom = z[13] * z[15] - z[14] * z[14]
                if denom:
                    break
            params = [sum(z[i] * basis[i][k] for i in range(nz))
                      for k in range(cp.n_params)]
            if e == 1:
                assert params[cp.stt_index[(0, 0)]] == denom
            else:
                S = [[params[cp.stt_index[(min(t, u), max(t, u))]]
                      for u in range(2)] for t in range(2)]
                assert S[0][0] * S[1][1] - S[0][1] * S[1][0] == denom
            nm = S2.NumericModel(md, cp, params)
            for (a, b, Bc, Bd), eqs in sorted(by_sector.items()):
                c, d = Bc[0], Bd[0]
                total_wt = a + b + c + d
                tuples = set()
                while len(tuples) < 3:
                    i = rng.randrange(2 * a + 1)
                    j = rng.randrange(2 * b + 1)
                    k = rng.randrange(2 * c + 1)
                    l = total_wt - i - j - k
                    if 0 <= l <= 2 * d:
                        tuples.add((i, j, k, l))
                gz = {eq["J"]: poly_eval(eq["poly"], z) for eq in eqs}
                for (i, j, k, l) in tuples:
                    numeric = nm.F((a, i), (b, j), (Bc, k), (Bd, l),
                                   verify=(checks_a % 25 == 0))
                    recon = ZERO
                    for eq in eqs:
                        tv = S2.chan_val(md, a, b, c, d, eq["J"], i, j, k, l)
                        if tv:
                            recon += gz[eq["J"]] * tv
                    checks_a += 1
                    if denom * numeric != recon:
                        failures += 1
                        print(f"FAIL e={e} sector {(a, b, Bc, Bd)} tuple "
                              f"{(i, j, k, l)}: {denom * numeric} != {recon}")
        print(f"e={e}: (A) channel-identity checks: {checks_a}, "
              f"failures so far: {failures}")
        # --- (B) parameter-level evidence point
        qev = res["quadratic_evidence_diagonal_sector"]
        assert qev["found"], qev
        (ti, tj, tk, tl) = qev["tuple"]
        ch = qev["channel"]
        pidx = cp.channel_index[(ch[0], tuple(ch[1]), tuple(ch[2]))]
        eqs77 = [eq for eq in datap["equations"]
                 if eq["sector"] == [7, 7, [7, 0], [7, 0]]]
        assert eqs77
        for pv, expect in zip((0, 1, 2), qev["F_at_p0_p1_p2"]):
            params = [ZERO] * cp.n_params
            for t in range(e):
                params[cp.stt_index[(t, t)]] = Q(1)
            params[pidx] = Q(pv)
            recon = ZERO
            for eq in eqs77:
                tv = S2.chan_val(md, 7, 7, 7, 7, eq["J"], ti, tj, tk, tl)
                if tv:
                    recon += poly_eval(eq["poly"], params) * tv
            ok = recon == Q(expect)
            print(f"e={e}: (B) p={pv}: assembled {recon}, recorded "
                  f"{expect}, {'OK' if ok else 'FAIL'}")
            if not ok:
                failures += 1
    print(f"TOTAL FAILURES: {failures}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
