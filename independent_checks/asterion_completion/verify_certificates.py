"""Independent verification of the stage-three exclusion certificates.

Does NOT reuse the symbolic Delta machinery of assemble_diagonal.py.
For each e in {1, 2} it:
  1. loads the two certificate equations (sector (7,7,7,7), J = 1 and
     J = 3) from diagonal_e{e}_polys.json and the weights lambda from
     solve_results.json, and checks, with plain Fraction arithmetic,
     the polynomial identities
        e=1:  lam0 * G_{J=1} + lam1 * G_{J=3}  ==  z11        (sigma)
        e=2:  lam0 * G_{J=1} + lam1 * G_{J=3}  ==  z13*z15 - z14^2
              (det S_11);
  2. re-derives the VALUES G_{J=1}(z), G_{J=3}(z) at several random
     rational points z of the stage-two solution space from stage
     two's exact NUMERIC model alone: at each z it evaluates the
     cleared Jacobi component  denom * F_numeric  at enough random
     weight tuples of sector (7,7,7,7) to invert the channel
     (transvectant) matrix, solves for the channel vector over Q,
     and compares its J=1 and J=3 entries against the stored
     polynomials.  (The numeric model's brackets are verified against
     their defining pairings B([x,w], z) = omega(x,w,z) at every z.)
Any common zero of the 1,205 diagonal equations is a zero of these
two, hence has sigma = 0 (e=1) resp. det S_11 = 0 (e=2): dimensions
494 and 495 admit no completion in the PR #7 normal form.

Exits nonzero on any failure.
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
    "s2mod", HERE / "asterion_linear_e12.py")
S2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S2)
ZERO = Q(0)
ONE = Q(1)


def poly_eval(poly_json, point):
    total = ZERO
    for mstr, cstr in poly_json.items():
        v = Q(cstr)
        if mstr:
            for x in mstr.split(","):
                v *= point[int(x)]
        total += v
    return total


def solve_square(mat, rhs):
    n = len(mat)
    rows = [list(mat[i]) + [rhs[i]] for i in range(n)]
    for col in range(n):
        piv = next((r for r in range(col, n) if rows[r][col]), None)
        if piv is None:
            raise ArithmeticError("singular")
        rows[col], rows[piv] = rows[piv], rows[col]
        pv = rows[col][col]
        rows[col] = [x / pv for x in rows[col]]
        for r in range(n):
            if r != col and rows[r][col]:
                f = rows[r][col]
                rows[r] = [x - f * y for x, y in zip(rows[r], rows[col])]
    return [rows[i][n] for i in range(n)]


def main():
    repo = HERE.parents[1]  # repository root, when run from independent_checks/asterion_completion/
    md = S2.Model(repo)
    sr = json.loads((HERE / "solve_results.json").read_text())
    rng = random.Random(20261026)
    failures = 0
    for e in (1, 2):
        cp = S2.Completion(md, e)
        res = json.loads((HERE / f"asterion_e{e}_results.json").read_text())
        basis = [[Q(x) for x in vec] for vec in res["result"]["null_basis"]]
        nz = len(basis)
        data = json.loads((HERE / f"diagonal_e{e}_polys.json").read_text())
        sector_eqs = [eq for eq in data["equations"]
                      if eq["sector"] == [7, 7, [7, 0], [7, 0]]]
        Js = [eq["J"] for eq in sector_eqs]
        by_J = {eq["J"]: eq["poly"] for eq in sector_eqs}
        if e == 1:
            lam = [Q(x) for x in sr["e1"]["lambda"][:2]]
            target = {(11,): ONE}
        else:
            lam = [Q(x[1]) for x in
                   sorted(sr["e2"]["lambda_support"], key=lambda t: t[0])]
            target = {(13, 15): ONE, (14, 14): -ONE}
        # --- 1. polynomial identity from the files
        acc = {}
        for li, J in zip(lam, (1, 3)):
            if not li:
                continue
            for mstr, cstr in by_J[J].items():
                m = tuple(int(x) for x in mstr.split(",")) if mstr else ()
                acc[m] = acc.get(m, ZERO) + li * Q(cstr)
        acc = {m: c for m, c in acc.items() if c}
        ok = acc == target
        print(f"e={e}: identity lam0*G_1 + lam1*G_3 == "
              f"{'sigma' if e == 1 else 'det'}: {'OK' if ok else 'FAIL ' + str(acc)}")
        if not ok:
            failures += 1
        # --- 2. numeric re-derivation of G_1(z), G_3(z)
        nch = len(Js)
        for trial in range(3):
            while True:
                z = [Q(rng.randrange(-4, 5), rng.choice((1, 1, 2)))
                     for _ in range(nz)]
                denom = z[11] if e == 1 else z[13] * z[15] - z[14] ** 2
                if denom:
                    break
            params = [sum(z[i] * basis[i][k] for i in range(nz))
                      for k in range(cp.n_params)]
            nm = S2.NumericModel(md, cp, params)
            tuples = set()
            while len(tuples) < 400:
                i = rng.randrange(15)
                j = rng.randrange(15)
                k = rng.randrange(15)
                l = 28 - i - j - k
                if 0 <= l <= 14:
                    tuples.add((i, j, k, l))
            # Rank-greedy tuple selection (as in the extraction):
            # accept a tuple only if its chan_val row increases the
            # rank of the accepted set.
            rref_basis = []
            mat = []
            rhs = []
            for (i, j, k, l) in sorted(tuples):
                row = [S2.chan_val(md, 7, 7, 7, 7, J, i, j, k, l)
                       for J in Js]
                if not any(row):
                    continue
                red = S2.reduce_vec(row, rref_basis)
                piv = next((t for t, x in enumerate(red) if x), None)
                if piv is None:
                    continue
                inv = red[piv]
                newrow = [x / inv for x in red]
                new_basis = []
                for p, brow in rref_basis:
                    if brow[piv]:
                        f = brow[piv]
                        brow = [x - f * y for x, y in zip(brow, newrow)]
                    new_basis.append((p, brow))
                new_basis.append((piv, newrow))
                new_basis.sort(key=lambda t: t[0])
                rref_basis = new_basis
                mat.append(row)
                rhs.append(denom * nm.F((7, i), (7, j), ((7, 0), k),
                                        ((7, 0), l), verify=True))
                if len(mat) == nch:
                    break
            assert len(mat) == nch
            sol = solve_square(mat, rhs)
            got = {J: sol[t] for t, J in enumerate(Js)}
            for J in (1, 3):
                expect = poly_eval(by_J[J], z)
                ok = got[J] == expect
                print(f"e={e} trial {trial}: numeric G_{J}(z) = {got[J]}, "
                      f"polynomial = {expect}: {'OK' if ok else 'FAIL'}")
                if not ok:
                    failures += 1
            combo = lam[0] * got[1] + lam[1] * got[3]
            ok = combo == denom
            print(f"e={e} trial {trial}: lam0*G_1 + lam1*G_3 at z = "
                  f"{combo}, denom(z) = {denom}: {'OK' if ok else 'FAIL'}")
            if not ok:
                failures += 1
    print(f"TOTAL FAILURES: {failures}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
