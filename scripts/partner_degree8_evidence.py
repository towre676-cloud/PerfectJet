"""Numerical evidence that degree-8 partners occur on bielliptic sextics with AB^2+BC/6-9D/2=0.

For three sparse two-parameter families without an evident symmetry, the exact degree-8 drop
locus (comprehensive rank cells) is zero-dimensional. Its points are located numerically from a
lexicographic Groebner basis. Each sextic is tested for an involution of P^1 permuting its six
roots (all pairings, tolerance 1e-5), and the weight-5 invariant relation is evaluated. A control
runs the same involution test on random integer sextics. Requires numpy (optional extras).
Writes results/partner_degree8_evidence.json.
"""
import itertools, json, random
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
from perfectjet.polynomial import Poly
from perfectjet.parametric import polynomial_matrix, drop_locus, groebner, _lex, dimension
from perfectjet.transvectants import gate_matrix, transvectant

ROOT = Path(__file__).resolve().parents[1]
x, y = Poly.variable(0), Poly.variable(1)
FAMILIES = {"x^6+a x^5y+3x^4y^2+b x^2y^4+2xy^5+y^6": lambda a, b: x**6+Q(a)*x**5*y+3*x**4*y**2+Q(b)*x**2*y**4+2*x*y**5+y**6,
            "x^6+2x^5y+a x^3y^3+b xy^5-y^6": lambda a, b: x**6+2*x**5*y+Q(a)*x**3*y**3+Q(b)*x*y**5-y**6,
            "x^6+a x^4y^2+x^3y^3+b xy^5+2y^6": lambda a, b: x**6+Q(a)*x**4*y**2+x**3*y**3+Q(b)*x*y**5+2*y**6}


def has_involution(roots, tol=1e-5):
    for perm in itertools.permutations(range(6)):
        if perm == tuple(range(6)) or any(perm[perm[i]] != i for i in range(6)):
            continue
        pairs = [(i, perm[i]) for i in range(6) if i < perm[i]]
        if len(pairs) < 2:
            continue
        (i, j), (k, l) = pairs[0], pairs[1]
        a = np.array([[-(roots[i]+roots[j]), -1, roots[i]*roots[j]], [-(roots[k]+roots[l]), -1, roots[k]*roots[l]]])
        p, q, r = np.linalg.svd(a)[2][-1].conj()
        if all(abs((p*roots[u]+q)/(r*roots[u]-p)-roots[perm[u]]) < tol*max(1, abs(roots[u])) for u in range(6)):
            return True
    return False


def numeric_clebsch(c):
    from math import comb

    def d(c, ox, oy):
        for _ in range(ox):
            m = len(c)-1
            c = np.array([c[i]*(m-i) for i in range(m)]) if m > 0 else np.zeros(1)
        for _ in range(oy):
            m = len(c)-1
            c = np.array([c[i+1]*(i+1) for i in range(m)]) if m > 0 else np.zeros(1)
        return c

    def tv(f, g, k):
        return sum((-1)**i*comb(k, i)*np.convolve(d(f, k-i, i), d(g, i, k-i)) for i in range(k+1))
    i = tv(c, c, 4)
    y1 = tv(c, i, 4)
    y3 = tv(i, tv(i, y1, 2), 2)
    return tv(c, c, 6)[0], tv(i, i, 4)[0], tv(i, tv(i, i, 2), 4)[0], tv(y3, y1, 2)[0]


def points(cell):
    g = groebner(cell["equations"], _lex)
    uni = next(p for p in g if all(e[0] == 0 for e in p))
    deg = max(e[1] for e in uni)
    out = []
    for bv in np.roots([float(uni.get((0, k), 0)) for k in range(deg, -1, -1)]):
        rest = min((p for p in g if p is not uni), key=lambda p: max(e[0] for e in p))
        da = max(e[0] for e in rest)
        for av in np.roots([sum(complex(float(v))*bv**e[1] for e, v in rest.items() if e[0] == k) for k in range(da, -1, -1)]):
            if all(abs(sum(complex(float(v))*av**e[0]*bv**e[1] for e, v in p.items())) < 1e-6 for p in g):
                out.append((av, bv))
    return out


def main():
    report = {"families": [], "control": {}}
    for name, fam in FAMILIES.items():
        m = polynomial_matrix(lambda a, b: gate_matrix(fam(a, b), 8, 3)+gate_matrix(fam(a, b), 8, 5), 2, 1)
        res = drop_locus(m, 2, ["a", "b"])
        rows = []
        for cell in res["_cells"]:
            if cell["rank"] >= res["generic_rank"] or dimension(cell["equations"], 2) != 0:
                continue
            for av, bv in points(cell):
                base = [complex(float(fam(0, 0).terms.get((6-i, i), 0))) for i in range(7)]
                da = [float(fam(1, 0).terms.get((6-i, i), 0))-base[i].real for i in range(7)]
                db = [float(fam(0, 1).terms.get((6-i, i), 0))-base[i].real for i in range(7)]
                coeffs = np.array([base[i]+av*da[i]+bv*db[i] for i in range(7)])
                a_, b_, c_, d_ = numeric_clebsch(coeffs)
                rel = abs(a_*b_*b_+b_*c_/6-4.5*d_)/max(abs(a_)**5, 1e-300) if abs(a_) > 1e-9 else None
                rows.append({"a": [av.real, av.imag], "b": [bv.real, bv.imag], "involution": has_involution(np.roots(coeffs)),
                             "R5_relative": rel})
        report["families"].append({"family": name, "points": rows})
    rng = random.Random(3)
    tested = flagged = 0
    for _ in range(200):
        c = [rng.randint(-5, 5) for _ in range(7)]
        if c[0] == 0:
            continue
        tested += 1
        flagged += has_involution(np.roots(c))
    report["control"] = {"random_integer_sextics": tested, "with_involution": flagged}
    allpts = [p for f in report["families"] for p in f["points"]]
    report["summary"] = {"points": len(allpts), "with_involution": sum(p["involution"] for p in allpts),
                         "max_R5_relative": max((p["R5_relative"] or 0) for p in allpts)}
    out = ROOT/"results/partner_degree8_evidence.json"
    out.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report["summary"]), json.dumps(report["control"]))


if __name__ == "__main__":
    main()
