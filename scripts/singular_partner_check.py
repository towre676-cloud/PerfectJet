"""Rational (characteristic 0) checks of partner loci on the dense slice with Singular.

For degree N, random integer projections det(R_k L_N(p,q,r)) vanish wherever ker L_N != 0, so their
common zero set contains the partner locus. Singular computes, over Q:
  - emptiness away from repeated roots at 0 and 1:  1 in <dets> + <1 - z h>,  h = r(1+p+q+r);
  - for each named invariant relation J: whether J vanishes there:  1 in <dets> + <1 - z h J>.
A True answer for emptiness or for a relation is a statement about the true locus, because the
projected set contains it. Requires the Singular executable. Usage:
    python scripts/singular_partner_check.py N [relation names...]
Relations: R5, C6 (C^2-6B^3), S12 (A^2-25B/96), ORB10 (B-6A^2, C+36A^3, D), A (control).
"""
import json
import random
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as Q
from perfectjet.parametric import polynomial_matrix, fmt, sub, scale, mul, add
from perfectjet.invariants import slice_form
from perfectjet.incidence import correction_matrix, slice_invariants

NAMES = ["p", "q", "r"]


def poly_str(p):
    return fmt(p, NAMES) if p else "0"


def relations():
    a, b, c, d = slice_invariants()
    return {"R5": [add(add(mul(a, mul(b, b)), scale(mul(b, c), Q(1, 6))), scale(d, Q(-9, 2)))],
            "C6": [sub(mul(c, c), scale(mul(b, mul(b, b)), 6))],
            "S12": [sub(mul(a, a), scale(b, Q(25, 96)))],
            "ORB10": [sub(b, scale(mul(a, a), 6)), add(c, scale(mul(a, mul(a, a)), 36)), d],
            "A": [a],
            "OCTA": [b, c, d],
            "D10": [sub(mul(c, c), scale(mul(b, mul(b, b)), 6)), d]}


def script(n, names, projections=6, seed=1, check_empty=True, char=0, kernel=1):
    rng = random.Random(seed)
    m = polynomial_matrix(lambda p, q, r: correction_matrix(slice_form(p, q, r), n), 3, 1)
    rows, cols = len(m), n+1
    size = cols-kernel+1
    lines = [f"ring R={char},(p,q,r,z),dp;", f"matrix M[{rows}][{cols}];"]
    for i in range(rows):
        for j in range(cols):
            if m[i][j]:
                lines.append(f"M[{i+1},{j+1}]={poly_str(m[i][j])};")
    lines.append("ideal J;")
    for k in range(projections):
        lines.append(f"matrix P{k}[{size}][{rows}];")
        for i in range(size):
            for j in range(rows):
                lines.append(f"P{k}[{i+1},{j+1}]={rng.randint(-3, 3)};")
        lines.append(f"matrix S{k}[{cols}][{size}];")
        for i in range(cols):
            for j in range(size):
                lines.append(f"S{k}[{i+1},{j+1}]={rng.randint(-3, 3) if size < cols else int(i == j)};")
        lines.append(f"J[{k+1}]=det(P{k}*M*S{k});")
    lines.append("poly h=r*(1+p+q+r);")
    if check_empty:
        lines.append('ideal E=std(J+ideal(1-z*h)); print("empty:"+string(dim(E)==-1));')
    rels = relations()
    for name in names:
        for idx, poly in enumerate(rels[name]):
            lines.append(f"poly J{name}{idx}={poly_str(poly)};")
            lines.append(f'ideal T{name}{idx}=std(J+ideal(1-z*h*J{name}{idx})); '
                         f'print("{name}{idx}:"+string(dim(T{name}{idx})==-1));')
    lines.append("quit;")
    return "\n".join(lines)


def run(n, names, projections=6, seed=1, check_empty=True, char=0, kernel=1):
    t = time.time()
    with tempfile.NamedTemporaryFile("w", suffix=".sing", delete=False) as fh:
        fh.write(script(n, names, projections, seed, check_empty, char, kernel))
        path = fh.name
    proc = subprocess.run(["Singular", "-q", path], capture_output=True, text=True)
    res = {"degree": n, "kernel_at_least": kernel, "field": "Q" if char == 0 else f"GF({char})", "projections": projections, "seconds": round(time.time()-t, 1)}
    for line in proc.stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            res[k.strip()] = v.strip() == "1"
    if proc.returncode or not any(k not in ("degree", "kernel_at_least", "field", "projections", "seconds") for k in res):
        res["error"] = (proc.stderr or proc.stdout)[-500:]
    return res


if __name__ == "__main__":
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    char = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--char=")), 0)
    kernel = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--kernel=")), 1)
    print(json.dumps(run(int(sys.argv[1]), args, check_empty="--no-empty" not in sys.argv, char=char, kernel=kernel)), flush=True)
