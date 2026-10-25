"""Asterion AST-P036, stage three: assemble the 1,205 deferred
diagonal-sector (g0,g0,W)-against-W channel equations at e = 1 and
e = 2 as EXACT polynomial equations on the stage-two linear solution
spaces (12 coordinates z at e = 1; 16 at e = 2).

Method.  Stage two (../asterion_linear_e12/asterion_linear_e12.py)
carries brackets as BV objects whose Delta terms are kept symbolic in
S_11^{-1}: a Delta term is (cov, nd) representing the n-supported
vector  sum_{t,u} (S_11^{-1})_{tu} cov_u * nd_t,  where cov_u are
affine forms (the trivial-W covector of an inner bracket) and nd_t is
the n-part of [x, e_t], an affine vector.  Pairing against w' in an
M-block of spin d gives  s_t = sum_i beta(d, i, l) nd_t[(d, i)]
(affine), so the full Jacobi component is

    F = A + sum_{terms} sum_{t,u} (S_11^{-1})_{tu} cov_u s_t,

with A the affine part stage two's pair_w computes from J.vec.
Clearing the denominator:
  e = 1:  G := sigma * F = sigma * A + sum cov_0 s_0
          (quadratic polynomial in the 177 params);
  e = 2:  G := det(S_11) * F = det * A
             + sum adj(S_11)_{tu} cov_u s_t
          (polynomial of degree <= 3 in the 186 params),
where adj is the classical adjugate (entries linear in S_11).
Channel components G_J of G are extracted per diagonal sector by
exactly stage two's evaluation-matrix method (chan_val transvectant
matrix, rational Gaussian elimination), now with polynomial RHS.
Finally the params are restricted to the stage-two solution space
(params = sum_i z_i * basis_i; the particular solution is 0), giving
polynomials in z.  On the open set sigma != 0 (resp. det != 0),
G_J(z) = 0 for all J is equivalent to the diagonal Jacobi system.

Outputs per e, in this script's directory:
  diagonal_e{e}_polys.json      the 1,205 restricted polynomials
                                 (sector, J, monomials in z -> coeff)
  diagonal_e{e}_params.json     the same equations before restriction
                                 (monomials in the full params)
  assemble_e{e}.log             stage log

Usage: python3 assemble_diagonal.py --e {1,2} [--repo PATH]
Default repo: ../../PerfectJet relative to this file (read-only).
Standard library only.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

ZERO = Q(0)
ONE = Q(1)
HERE = Path(__file__).resolve().parent
STAGE2 = HERE / "asterion_linear_e12.py"

spec = importlib.util.spec_from_file_location("stage2", STAGE2)
S2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S2)

LOG_LINES = []


def log(msg):
    print(msg, flush=True)
    LOG_LINES.append(msg)


# ---------------------------------------------------------------------------
# Polynomials in the full parameter set: {monomial: coeff},
# monomial = sorted tuple of param indices (with repetition); () = const.
# ---------------------------------------------------------------------------

def p_add(p, q):
    out = dict(p)
    for m, c in q.items():
        nv = out.get(m, ZERO) + c
        if nv:
            out[m] = nv
        elif m in out:
            del out[m]
    return out


def p_scale(p, s):
    s = Q(s)
    if not s:
        return {}
    if s == 1:
        return dict(p)
    return {m: c * s for m, c in p.items()}


def p_mul(p, q):
    if not p or not q:
        return {}
    out = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = tuple(sorted(m1 + m2))
            nv = out.get(m, ZERO) + c1 * c2
            if nv:
                out[m] = nv
            elif m in out:
                del out[m]
    return out


def p_from_affine(aff):
    const, d = aff
    out = {}
    if const:
        out[()] = const
    for k, v in d.items():
        out[(k,)] = v
    return out


def p_degree(p):
    return max((len(m) for m in p), default=-1)


# ---------------------------------------------------------------------------
# Full pairing: cleared Jacobi component as a polynomial in the params.
# ---------------------------------------------------------------------------

def pair_w_full(cp, J, wp):
    """Return G = sigma*F (e=1) resp. det(S_11)*F (e=2) as a polynomial
    in the params, for wp = (Bd, l) with Bd an M-block.  F is the exact
    Jacobi component B(Jac(x,y,w), w'); stage two's pair_w computes its
    affine part A from J.vec and raises NonAffine on the Delta terms;
    here the Delta terms are paired explicitly and the denominator is
    cleared."""
    md = cp.md
    Bd, l = wp
    m = Bd[0]
    assert m > 1
    # Affine part A (verbatim logic of stage two's pair_w).
    A = S2.AFF_ZERO
    for key, val in J.vec.items():
        if key[0] == 'g' and key[1] == m:
            bv_ = md.beta(m, key[2], l)
            if bv_:
                A = S2.aff_add(A, S2.aff_scale(val, bv_))
        elif key[0] == 'w' and key[1] == Bd:
            if not S2.aff_is_const(val):
                raise ArithmeticError("non-constant J_W in pair_w_full")
            bv_ = md.beta(m, key[2], l)
            if bv_ and val[0]:
                A = S2.aff_add(A, (ZERO, {cp.s_index[m]: val[0] * bv_}))
    # Delta terms: for each, s_t = pairing of nd_t against (Bd, l).
    terms = []
    for cov, nd in J.delta:
        s = {}
        for t in range(cp.e):
            st = S2.AFF_ZERO
            for (mm, ii), aval in nd.get(t, {}).items():
                if mm == m:
                    bv_ = md.beta(m, ii, l)
                    if bv_:
                        st = S2.aff_add(st, S2.aff_scale(aval, bv_))
            s[t] = st
        terms.append((cov, s))
    if cp.e == 1:
        sig = cp.stt_index[(0, 0)]
        assert all(k != sig for k in A[1]), "affine part involves sigma"
        G = p_mul({(sig,): ONE}, p_from_affine(A))
        for cov, s in terms:
            G = p_add(G, p_mul(p_from_affine(cov.get(0, S2.AFF_ZERO)),
                               p_from_affine(s[0])))
        return G
    # e == 2
    i00 = cp.stt_index[(0, 0)]
    i01 = cp.stt_index[(0, 1)]
    i11 = cp.stt_index[(1, 1)]
    assert all(k not in (i00, i01, i11) for k in A[1]), \
        "affine part involves S_11"
    det = {(i00, i11): ONE, (i01, i01): -ONE}
    G = p_mul(det, p_from_affine(A))
    adj = {(0, 0): (ZERO, {i11: ONE}), (1, 1): (ZERO, {i00: ONE}),
           (0, 1): (ZERO, {i01: -ONE}), (1, 0): (ZERO, {i01: -ONE})}
    for cov, s in terms:
        for t in range(2):
            if S2.aff_is_zero(s[t]):
                continue
            ps = p_from_affine(s[t])
            for u in range(2):
                cu = cov.get(u, S2.AFF_ZERO)
                if S2.aff_is_zero(cu):
                    continue
                G = p_add(G, p_mul(p_from_affine(adj[(t, u)]),
                                   p_mul(p_from_affine(cu), ps)))
    return G


# ---------------------------------------------------------------------------
# Sector extraction with polynomial RHS (stage two's evaluation method).
# ---------------------------------------------------------------------------

def solve_square_poly(mat, rhs):
    n = len(mat)
    rows = [list(mat[i]) + [rhs[i]] for i in range(n)]
    for col in range(n):
        piv = next((r for r in range(col, n) if rows[r][col]), None)
        if piv is None:
            raise ArithmeticError("singular evaluation matrix")
        rows[col], rows[piv] = rows[piv], rows[col]
        pv = rows[col][col]
        rows[col] = [x / pv for x in rows[col][:n]] + \
                    [p_scale(rows[col][n], 1 / pv)]
        for r in range(n):
            if r != col and rows[r][col]:
                f = rows[r][col]
                rows[r] = [x - f * y for x, y in zip(rows[r][:n], rows[col][:n])] + \
                          [p_add(rows[r][n], p_scale(rows[col][n], -f))]
    return [rows[i][n] for i in range(n)]


def extract_sector_poly(cp, a, b, Bc, Bd, rng):
    md = cp.md
    c, d = Bc[0], Bd[0]
    Js = S2.sector_channels(a, b, c, d)
    nch = len(Js)
    total_wt = a + b + c + d
    cands = []
    for i in range(2 * a + 1):
        for j in range(2 * b + 1):
            for k in range(2 * c + 1):
                l = total_wt - i - j - k
                if 0 <= l <= 2 * d:
                    cands.append((i, j, k, l))
    rng.shuffle(cands)
    basis = []
    chosen = []
    chosen_vals = []
    for (i, j, k, l) in cands:
        vals = [S2.chan_val(md, a, b, c, d, J, i, j, k, l) for J in Js]
        if not any(vals):
            continue
        red = S2.reduce_vec(vals, basis)
        piv = next((t for t, x in enumerate(red) if x), None)
        if piv is None:
            continue
        inv = red[piv]
        newrow = [x / inv for x in red]
        new_basis = []
        for p, row in basis:
            if row[piv]:
                f = row[piv]
                row = [x - f * y for x, y in zip(row, newrow)]
            new_basis.append((p, row))
        new_basis.append((piv, newrow))
        new_basis.sort(key=lambda t: t[0])
        basis = new_basis
        chosen.append((i, j, k, l))
        chosen_vals.append(vals)
        if len(chosen) == nch:
            break
    if len(chosen) < nch:
        raise ArithmeticError(f"sector {(a, b, Bc, Bd)}: evaluation rank "
                              f"{len(chosen)} < {nch} channels")
    gvals = []
    for (i, j, k, l) in chosen:
        J = cp.jacobi((a, i), (b, j), (Bc, k))
        gvals.append(pair_w_full(cp, J, (Bd, l)))
    return Js, chosen, solve_square_poly(chosen_vals, gvals)


# ---------------------------------------------------------------------------
# Restriction to the solution space: params = sum_i z_i * basis_i.
# ---------------------------------------------------------------------------

def restrict_poly(poly, basis):
    """basis: list of vectors (Fractions) over params.  Returns a
    polynomial in z: {monomial over z indices: coeff}."""
    lin = {}
    for k in range(len(basis[0])):
        d = {i: basis[i][k] for i in range(len(basis)) if basis[i][k]}
        if d:
            lin[k] = {tuple([i]): c for i, c in d.items()}
    out = {}
    for mon, coeff in poly.items():
        acc = {(): ONE}
        for k in mon:
            lf = lin.get(k)
            if lf is None:
                acc = {}
                break
            acc = p_mul(acc, lf)
        if acc:
            out = p_add(out, p_scale(acc, coeff))
    return out


def poly_to_json(p):
    return {",".join(str(i) for i in m): str(c)
            for m, c in sorted(p.items()) if c}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e", type=int, required=True, choices=(1, 2))
    # Default --repo is the repository root, when this script is run
    # from independent_checks/asterion_completion/ inside a checkout.
    ap.add_argument("--repo", type=Path,
                    default=Path(__file__).resolve().parents[2])
    args = ap.parse_args()
    e = args.e
    t0 = time.time()
    log(f"=== assemble diagonal systems, e = {e} (dimension {493 + e}) ===")
    md = S2.Model(args.repo)
    cp = S2.Completion(md, e)
    log(f"params: {cp.n_params} (omega2 {cp.n_omega2}, mixed "
        f"{len(cp.mixed_index)}, S {cp.n_s})")
    res_path = (HERE / f"asterion_e{e}_results.json")
    res = json.loads(res_path.read_text())
    assert res["result"]["outcome"] == "consistent"
    assert all(Q(x) == 0 for x in res["result"]["particular"])
    basis = [[Q(x) for x in vec] for vec in res["result"]["null_basis"]]
    nz = len(basis)
    log(f"solution space: {nz} coordinates (particular = 0)")

    rng = random.Random(20261025 + e)
    equations = []
    equations_params = []
    nsec = 0
    for ai, a in enumerate(cp.E):
        for b in cp.E[ai:]:
            for Bc in cp.WB:
                for Bd in cp.WB:
                    if not S2.is_diagonal_sector(cp, a, b, Bc, Bd):
                        continue
                    Js0 = S2.sector_channels(a, b, Bc[0], Bd[0])
                    if not Js0:
                        continue
                    nsec += 1
                    Js, chosen, g = extract_sector_poly(cp, a, b, Bc, Bd, rng)
                    assert Js == Js0
                    for J, gp in zip(Js, g):
                        gz = restrict_poly(gp, basis)
                        equations.append({
                            "sector": [a, b, list(Bc), list(Bd)],
                            "J": J, "poly": poly_to_json(gz)})
                        equations_params.append({
                            "sector": [a, b, list(Bc), list(Bd)],
                            "J": J, "poly": poly_to_json(gp)})
                    log(f"  sector {(a, b, Bc, Bd)}: {len(Js)} channels "
                        f"({time.time() - t0:.0f}s)")
    log(f"diagonal sectors: {nsec}; equations: {len(equations)}")
    assert nsec == 49 and len(equations) == 1205, (nsec, len(equations))
    nzero = sum(1 for eq in equations if not eq["poly"])
    degs = {}
    for eq in equations:
        dgr = max((len(m.split(",")) if m else 0)
                  for m in eq["poly"]) if eq["poly"] else -1
        degs[dgr] = degs.get(dgr, 0) + 1
    log(f"restricted system: {nzero} identically zero equations; "
        f"degree histogram {degs}")
    nmon = [len(eq["poly"]) for eq in equations]
    log(f"monomial counts: max {max(nmon)}, total {sum(nmon)}")
    out = {
        "schema": "asterion-diagonal-polys/1",
        "e": e, "dimension": 493 + e,
        "variables": [f"z{i}" for i in range(nz)],
        "clearing": ("sigma" if e == 1 else "det(S11)"),
        "side_condition": ("z11 != 0 (sigma)" if e == 1
                           else "z13*z15 - z14^2 != 0 (det S11)"),
        "n_equations": len(equations),
        "n_zero": nzero,
        "degree_histogram": {str(k): v for k, v in sorted(degs.items())},
        "equations": equations,
    }
    (HERE / f"diagonal_e{e}_polys.json").write_text(json.dumps(out, indent=1))
    outp = dict(out)
    outp["equations"] = equations_params
    outp["variables"] = [f"p{i}" for i in range(cp.n_params)]
    (HERE / f"diagonal_e{e}_params.json").write_text(json.dumps(outp, indent=1))
    log(f"wrote diagonal_e{e}_polys.json and diagonal_e{e}_params.json "
        f"in {time.time() - t0:.0f}s")
    (HERE / f"assemble_e{e}.log").write_text("\n".join(LOG_LINES) + "\n")


if __name__ == "__main__":
    main()
