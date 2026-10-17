"""Numerical cross-check of the slice partner loci (degrees 5-7). Requires numpy.

Solves L_N(p,q,r) g = 0 with a normalization on g by Gauss-Newton from random complex
starts on the slice xy(x-y)(x^3+px^2y+qxy^2+ry^3). For degree 6 the normalization uses
only the x^6 and y^6 coefficients, which vanish for f itself, so the trivial partner g=f
is excluded. Solutions are split into squarefree-enough forms (root separation >= 0.05,
away from repeated roots at 0 and 1) and repeated-root forms. Usage:
    python scripts/partner_numeric_search.py DEGREE STARTS [SEED]
"""
import sys
import numpy as np
from perfectjet.parametric import polynomial_matrix
from perfectjet.invariants import slice_form
from perfectjet.incidence import correction_matrix


def main(n, starts, seed=0):
    m = polynomial_matrix(lambda p, q, r: correction_matrix(slice_form(p, q, r), n), 3, 1)
    rows, cols = len(m), n+1
    comp = lambda e: np.array([[float(m[i][j].get(e, 0)) for j in range(cols)] for i in range(rows)], dtype=complex)
    l0, lp, lq, lr = comp((0, 0, 0)), comp((1, 0, 0)), comp((0, 1, 0)), comp((0, 0, 1))
    rng = np.random.default_rng(seed)
    a = np.zeros(cols, dtype=complex)
    if n == 6:
        a[0], a[-1] = rng.normal()+1j*rng.normal(), rng.normal()+1j*rng.normal()
    else:
        a = rng.normal(size=cols)+1j*rng.normal(size=cols)
    found = {"squarefree": 0, "repeated_root": 0}
    pts = []
    for _ in range(starts):
        z = np.concatenate([rng.normal(size=3)*2+2j*rng.normal(size=3), rng.normal(size=cols)+1j*rng.normal(size=cols)])
        z[3:] /= a@z[3:]
        for _ in range(80):
            p, q, r = z[:3]
            lm = l0+p*lp+q*lq+r*lr
            res = np.concatenate([lm@z[3:], [a@z[3:]-1]])
            if np.linalg.norm(res) < 1e-13:
                break
            jac = np.vstack([np.column_stack([lp@z[3:], lq@z[3:], lr@z[3:], lm]), np.concatenate([[0, 0, 0], a])[None, :]])
            z = z+np.linalg.lstsq(jac, -res, rcond=None)[0]
            if np.linalg.norm(z) > 1e8:
                break
        p, q, r = z[:3]
        lm = l0+p*lp+q*lq+r*lr
        if np.linalg.norm(lm@z[3:]) > 1e-11 or np.linalg.norm(z[:3]) > 60:
            continue
        if any(np.linalg.norm(z[:3]-u) < 1e-6 for u in pts):
            continue
        pts.append(z[:3].copy())
        coeffs = np.array([0, 1, p-1, q-p, r-q, -r, 0], dtype=complex)
        rts = np.roots(coeffs[1:6])  # roots other than infinity
        sep = min(abs(x-y) for i, x in enumerate(rts) for y in rts[i+1:])
        degenerate = sep < 0.05 or abs(r) < 0.02 or abs(1+p+q+r) < 0.02
        found["repeated_root" if degenerate else "squarefree"] += 1
    print({"degree": n, "starts": starts, "distinct_solutions": len(pts), **found})


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 0)
