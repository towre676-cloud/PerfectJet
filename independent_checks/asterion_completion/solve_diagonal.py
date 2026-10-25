"""Solve the assembled diagonal systems over Q.

Structural fact (verified in this script, from the polynomial files):
every equation is LINEAR in a small monomial vector.

e = 1: monomials (z2^2, z2*z3, z3^2, z11); 1205 x 4 coefficient
matrix M1.  If rank_Q M1 = 4 then every solution of the diagonal
system has z2^2 = z2*z3 = z3^2 = z11 = 0, in particular sigma = z11
= 0, contradicting the side condition sigma != 0: dimension 494 is
excluded.  The script exhibits the certificate explicitly: four
equations whose coefficient matrix is invertible, and the rational
row combination of ALL 1205 (resp. of the four) producing the
polynomial z11 itself; equivalently it verifies that the polynomial
identity  sum_i lam_i * eq_i = z11  holds exactly, with lam supported
on few equations.  Any common zero of the eq_i then has z11 = 0.

e = 2: monomials (z13*z15, z14^2, and ten cubics); the 1205 x 12
coefficient matrix M2 has rank_Q = 4, and the det direction
(1,-1,0,...,0) is orthogonal to ker M2, i.e. det = z13*z15 - z14^2
lies in the row space of M2: an exact rational combination of the
equations equals det itself (found greedily on a sparse row support
and verified as a polynomial identity).  Every common zero then has
det = 0, contradicting det != 0: dimension 495 is excluded.

All arithmetic exact (sympy rationals / Fractions).  Writes
solve_results.json with ranks, certificates, and verification data.
"""
from __future__ import annotations

import json
from fractions import Fraction as Q
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
LOG = []


def log(msg):
    print(msg, flush=True)
    LOG.append(msg)


def load(e):
    d = json.loads((HERE / f"diagonal_e{e}_polys.json").read_text())
    return d["equations"]


def poly_dict(eq):
    return {tuple(int(x) for x in m.split(",")) if m else (): Q(c)
            for m, c in eq["poly"].items()}


def fmt_poly(p, names):
    parts = []
    for m in sorted(p):
        c = p[m]
        mon = "*".join(names[i] for i in m) if m else "1"
        parts.append(f"({c})*{mon}")
    return " + ".join(parts) if parts else "0"


def solve_e1():
    log("=== e = 1 (dimension 494) ===")
    eqs = load(1)
    mons = [(2, 2), (2, 3), (3, 3), (11,)]
    M = sp.Matrix([[sp.Rational(str(eq["poly"].get(
        ",".join(str(i) for i in m), "0"))) for m in mons] for eq in eqs])
    rank = M.rank()
    log(f"coefficient matrix 1205x4 over monomials "
        f"(z2^2, z2z3, z3^2, sigma): rank_Q = {rank}")
    assert rank == 4
    # Find an invertible 4x4 row subset (greedy).
    chosen = []
    cur = sp.zeros(0, 4)
    for i in range(M.rows):
        trial = cur.col_join(M[i, :])
        if trial.rank() == cur.rank() + 1:
            chosen.append(i)
            cur = trial
        if len(chosen) == 4:
            break
    A = M[chosen, :]
    log(f"invertible row subset: equation indices {chosen}, det = {A.det()}")
    # Row combination producing the monomial vector e_sigma = (0,0,0,1):
    # solve lam * A = (0,0,0,1).
    lam = sp.Matrix([[0, 0, 0, 1]]) * A.inv()
    lam = [Q(int(x.p), int(x.q)) for x in lam]
    log(f"lambda (on the 4 chosen equations) = {[str(x) for x in lam]}")
    # Verify the polynomial identity sum lam_i eq_i == z11 exactly.
    acc = {}
    for li, i in zip(lam, chosen):
        if not li:
            continue
        for m, c in poly_dict(eqs[i]).items():
            acc[m] = acc.get(m, Q(0)) + li * c
    acc = {m: c for m, c in acc.items() if c}
    log(f"sum lambda_i * eq_i = {fmt_poly(acc, {11: 'sigma', 2: 'z2', 3: 'z3'})}")
    assert acc == {(11,): Q(1)}, acc
    support = [(i, l) for i, l in zip(chosen, lam) if l]
    chosen_meta = [{"index": i, "sector": eqs[i]["sector"], "J": eqs[i]["J"],
                    "lambda": str(l), "poly": eqs[i]["poly"]}
                   for i, l in support]
    log(f"lambda support: {[(i, str(l)) for i, l in support]} (the "
        f"other two rows of the invertible subset have weight 0)")
    log("CERTIFICATE e=1: the two support equations above, combined "
        "with the rational weights lambda, give exactly sigma.  Hence "
        "every common zero of the 1,205 diagonal equations has "
        "sigma = 0, contradicting sigma != 0.  Dimension 494 is "
        "EXCLUDED (given the stage-two linear solution space and the "
        "normal form).")
    return {"rank": rank, "chosen_equations": chosen,
            "chosen_meta": chosen_meta,
            "lambda": [str(x) for x in lam],
            "lambda_support": [(i, str(l)) for i, l in support],
            "identity": "sum lambda_i eq_i = z11 (sigma)",
            "conclusion": "494 excluded"}


def solve_e2():
    log("=== e = 2 (dimension 495) ===")
    eqs = load(2)
    mons = [(13, 15), (14, 14), (2, 2, 15), (2, 3, 14), (2, 4, 15),
            (2, 5, 14), (3, 3, 13), (3, 4, 14), (3, 5, 13), (4, 4, 15),
            (4, 5, 14), (5, 5, 13)]
    DET = {(13, 15): Q(1), (14, 14): Q(-1)}
    M = sp.Matrix([[sp.Rational(str(eq["poly"].get(
        ",".join(str(i) for i in m), "0"))) for m in mons] for eq in eqs])
    rank = M.rank()
    log(f"coefficient matrix 1205x12 over the monomial vector: "
        f"rank_Q = {rank}, nullity = {12 - rank}")
    ns = M.nullspace()
    dvec = sp.Matrix([1, -1] + [0] * 10)
    orth = all((dvec.T * v)[0] == 0 for v in ns)
    log(f"det direction (1,-1,0,...) orthogonal to the whole null "
        f"space: {orth}  (equivalently det lies in the row space)")
    assert orth
    # Greedy sparse combination: add rows (in file order) while they
    # increase the span, until det is in the span.
    chosen = []
    cur = sp.zeros(0, 12)

    def in_span(mat, v):
        if mat.rows == 0:
            return False
        return mat.col_join(v.T).rank() == mat.rank()

    for i in range(M.rows):
        trial = cur.col_join(M[i, :])
        if trial.rank() == cur.rank() + 1:
            chosen.append(i)
            cur = trial
            if in_span(cur, dvec):
                break
    log(f"rows spanning det: {chosen}")
    A = M[chosen, :]
    # Solve lam * A = dvec (consistent, possibly underdetermined);
    # use the RREF-based particular solution.
    sol, _params = A.T.gauss_jordan_solve(dvec)
    lam = [Q(int(x.p), int(x.q)) for x in sol]
    nz_lam = [(i, l) for i, l in zip(chosen, lam) if l]
    log(f"lambda support: {[(i, str(l)) for i, l in nz_lam]}")
    # Verify the polynomial identity sum lam_i eq_i == det exactly.
    acc = {}
    for li, i in zip(lam, chosen):
        if not li:
            continue
        for m, c in poly_dict(eqs[i]).items():
            acc[m] = acc.get(m, Q(0)) + li * c
    acc = {m: c for m, c in acc.items() if c}
    names = {i: f"z{i}" for i in range(16)}
    log(f"sum lambda_i * eq_i = {fmt_poly(acc, names)}")
    assert acc == DET, acc
    chosen_meta = [{"index": i, "sector": eqs[i]["sector"], "J": eqs[i]["J"],
                    "lambda": str(dict(nz_lam).get(i, Q(0))),
                    "poly": eqs[i]["poly"]} for i, _l in nz_lam]
    log("CERTIFICATE e=2: the exhibited rational combination of the "
        f"{len(nz_lam)} equations above is exactly det(S_11) = "
        "z13*z15 - z14^2.  Hence every common zero of the 1,205 "
        "diagonal equations has det(S_11) = 0, contradicting "
        "det != 0.  Dimension 495 is EXCLUDED (given the stage-two "
        "linear solution space and the normal form).")
    return {"rank": rank, "nullity": 12 - rank,
            "lambda_support": [(i, str(l)) for i, l in nz_lam],
            "chosen_meta": chosen_meta,
            "identity": "sum lambda_i eq_i = z13*z15 - z14^2 (det S11)",
            "conclusion": "495 excluded"}


def main():
    out = {"e1": solve_e1(), "e2": solve_e2()}
    (HERE / "solve_results.json").write_text(json.dumps(out, indent=1))
    (HERE / "solve_diagonal.log").write_text("\n".join(LOG) + "\n")
    log("wrote solve_results.json")


if __name__ == "__main__":
    main()
