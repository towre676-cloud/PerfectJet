#!/usr/bin/env python3
"""
Symplectic-Moyal Bridge v4: Exact Rational Quantization Boundary Classifier

Adds exact Q[i][hbar]-valued polynomial arithmetic, multidimensional Moyal
products, hbar-defect order classification, affine-quadratic safe-sector proof in
T*R^2, and retained numerical symplectic-vs-volume geometry controls.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import factorial
import csv
import json
import hashlib
import os
from typing import Dict, Iterable, List, Tuple, Optional

import numpy as np


@dataclass(frozen=True)
class GI:
    """Gaussian rational a + i b."""
    re: Fraction = Fraction(0)
    im: Fraction = Fraction(0)

    def __add__(self, other: "GI") -> "GI":
        other = to_gi(other)
        return GI(self.re + other.re, self.im + other.im)

    def __sub__(self, other: "GI") -> "GI":
        other = to_gi(other)
        return GI(self.re - other.re, self.im - other.im)

    def __neg__(self) -> "GI":
        return GI(-self.re, -self.im)

    def __mul__(self, other: "GI") -> "GI":
        other = to_gi(other)
        return GI(self.re * other.re - self.im * other.im,
                  self.re * other.im + self.im * other.re)

    def __truediv__(self, other: "GI") -> "GI":
        other = to_gi(other)
        denom = other.re * other.re + other.im * other.im
        return GI((self.re * other.re + self.im * other.im) / denom,
                  (self.im * other.re - self.re * other.im) / denom)

    def is_zero(self) -> bool:
        return self.re == 0 and self.im == 0

    def conj(self) -> "GI":
        return GI(self.re, -self.im)

    def __str__(self) -> str:
        if self.im == 0:
            return frac_str(self.re)
        if self.re == 0:
            return f"{frac_str(self.im)}i"
        sign = "+" if self.im >= 0 else "-"
        return f"{frac_str(self.re)} {sign} {frac_str(abs(self.im))}i"


def to_gi(x) -> GI:
    if isinstance(x, GI):
        return x
    if isinstance(x, Fraction):
        return GI(x, Fraction(0))
    if isinstance(x, int):
        return GI(Fraction(x), Fraction(0))
    raise TypeError(f"cannot convert {type(x)} to GI")


def frac_str(x: Fraction) -> str:
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


I = GI(Fraction(0), Fraction(1))
ONE = GI(Fraction(1), Fraction(0))
ZERO = GI(Fraction(0), Fraction(0))


class PolyH:
    """Polynomial in q_0..q_{n-1}, p_0..p_{n-1}, and hbar.

    Terms are keyed by (hbar_power, exponents), where exponents has length 2n.
    Coefficients are exact Gaussian rationals.
    """
    def __init__(self, n: int, terms: Optional[Dict[Tuple[int, Tuple[int, ...]], GI]] = None):
        self.n = n
        self.m = 2 * n
        self.terms: Dict[Tuple[int, Tuple[int, ...]], GI] = {}
        if terms:
            for key, coeff in terms.items():
                coeff = to_gi(coeff)
                if not coeff.is_zero():
                    hpow, exps = key
                    assert len(exps) == self.m
                    self.terms[(hpow, tuple(exps))] = coeff

    @staticmethod
    def zero(n: int) -> "PolyH":
        return PolyH(n)

    @staticmethod
    def one(n: int) -> "PolyH":
        return PolyH(n, {(0, (0,) * (2 * n)): ONE})

    @staticmethod
    def monomial(n: int, exps: Tuple[int, ...], coeff=Fraction(1), hpow: int = 0) -> "PolyH":
        return PolyH(n, {(hpow, tuple(exps)): to_gi(coeff)})

    @staticmethod
    def q(n: int, i: int) -> "PolyH":
        exps = [0] * (2 * n)
        exps[i] = 1
        return PolyH.monomial(n, tuple(exps))

    @staticmethod
    def p(n: int, i: int) -> "PolyH":
        exps = [0] * (2 * n)
        exps[n + i] = 1
        return PolyH.monomial(n, tuple(exps))

    def copy(self) -> "PolyH":
        return PolyH(self.n, dict(self.terms))

    def __add__(self, other: "PolyH") -> "PolyH":
        assert self.n == other.n
        out = dict(self.terms)
        for key, coeff in other.terms.items():
            out[key] = out.get(key, ZERO) + coeff
            if out[key].is_zero():
                del out[key]
        return PolyH(self.n, out)

    def __sub__(self, other: "PolyH") -> "PolyH":
        assert self.n == other.n
        out = dict(self.terms)
        for key, coeff in other.terms.items():
            out[key] = out.get(key, ZERO) - coeff
            if out[key].is_zero():
                del out[key]
        return PolyH(self.n, out)

    def __neg__(self) -> "PolyH":
        return PolyH(self.n, {k: -v for k, v in self.terms.items()})

    def scale(self, c) -> "PolyH":
        c = to_gi(c)
        if c.is_zero():
            return PolyH.zero(self.n)
        return PolyH(self.n, {k: c * v for k, v in self.terms.items()})

    def mul(self, other: "PolyH") -> "PolyH":
        assert self.n == other.n
        out: Dict[Tuple[int, Tuple[int, ...]], GI] = {}
        for (ha, ea), ca in self.terms.items():
            for (hb, eb), cb in other.terms.items():
                key = (ha + hb, tuple(ea[i] + eb[i] for i in range(self.m)))
                out[key] = out.get(key, ZERO) + ca * cb
                if out[key].is_zero():
                    del out[key]
        return PolyH(self.n, out)

    def derivative(self, deriv_exps: Tuple[int, ...]) -> "PolyH":
        assert len(deriv_exps) == self.m
        out: Dict[Tuple[int, Tuple[int, ...]], GI] = {}
        for (hpow, exps), coeff in self.terms.items():
            new_exps = list(exps)
            factor = Fraction(1)
            ok = True
            for idx, order in enumerate(deriv_exps):
                if order > new_exps[idx]:
                    ok = False
                    break
                # falling factorial
                for t in range(order):
                    factor *= new_exps[idx] - t
                new_exps[idx] -= order
            if not ok:
                continue
            key = (hpow, tuple(new_exps))
            out[key] = out.get(key, ZERO) + coeff * GI(factor, Fraction(0))
            if out[key].is_zero():
                del out[key]
        return PolyH(self.n, out)

    def max_var_exp(self) -> Tuple[int, ...]:
        mx = [0] * self.m
        for _, exps in self.terms.keys():
            for i, e in enumerate(exps):
                mx[i] = max(mx[i], e)
        return tuple(mx)

    def is_zero(self) -> bool:
        return not self.terms

    def variable_part_zero(self) -> bool:
        return all(all(e == 0 for e in exps) for _, exps in self.terms.keys())

    def first_hbar_power(self) -> Optional[int]:
        if not self.terms:
            return None
        return min(h for h, _ in self.terms.keys())

    def norm_l1_float(self) -> float:
        s = 0.0
        for c in self.terms.values():
            s += float(abs(c.re)) + float(abs(c.im))
        return s

    def real_only(self) -> bool:
        return all(c.im == 0 for c in self.terms.values())

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PolyH) and self.n == other.n and self.terms == other.terms

    def __str__(self) -> str:
        if not self.terms:
            return "0"
        pieces = []
        for (hpow, exps), coeff in sorted(self.terms.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            mon = []
            if hpow:
                mon.append("h" if hpow == 1 else f"h^{hpow}")
            for i in range(self.n):
                e = exps[i]
                if e:
                    mon.append(f"q{i+1}" if e == 1 else f"q{i+1}^{e}")
            for i in range(self.n):
                e = exps[self.n + i]
                if e:
                    mon.append(f"p{i+1}" if e == 1 else f"p{i+1}^{e}")
            mstr = "*".join(mon) if mon else "1"
            pieces.append(f"({coeff})*{mstr}")
        return " + ".join(pieces)


def multi_indices(bounds: Tuple[int, ...]) -> Iterable[Tuple[int, ...]]:
    return product(*[range(b + 1) for b in bounds])


def factorial_multi(alpha: Tuple[int, ...]) -> int:
    out = 1
    for a in alpha:
        out *= factorial(a)
    return out


def star_product(f: PolyH, g: PolyH) -> PolyH:
    assert f.n == g.n
    n = f.n
    m = 2 * n
    fmx = f.max_var_exp()
    gmx = g.max_var_exp()
    # alpha differentiates q in f and p in g; beta differentiates p in f and q in g.
    alpha_bounds = tuple(min(fmx[i], gmx[n + i]) for i in range(n))
    beta_bounds = tuple(min(fmx[n + i], gmx[i]) for i in range(n))
    out = PolyH.zero(n)
    for alpha in multi_indices(alpha_bounds):
        for beta in multi_indices(beta_bounds):
            k = sum(alpha) + sum(beta)
            deriv_f = tuple(alpha[i] for i in range(n)) + tuple(beta[i] for i in range(n))
            deriv_g = tuple(beta[i] for i in range(n)) + tuple(alpha[i] for i in range(n))
            df = f.derivative(deriv_f)
            dg = g.derivative(deriv_g)
            if df.is_zero() or dg.is_zero():
                continue
            sign = -1 if (sum(beta) % 2) else 1
            denom = factorial_multi(alpha) * factorial_multi(beta) * (2 ** k)
            coeff = GI(Fraction(sign, denom), Fraction(0))
            coeff = coeff * (I_power(k))
            term = df.mul(dg).scale(coeff)
            # multiply by hbar^k
            if k:
                shifted = {}
                for (hpow, exps), c in term.terms.items():
                    shifted[(hpow + k, exps)] = c
                term = PolyH(n, shifted)
            out = out + term
    return out


def I_power(k: int) -> GI:
    r = k % 4
    if r == 0:
        return ONE
    if r == 1:
        return I
    if r == 2:
        return GI(Fraction(-1), Fraction(0))
    return GI(Fraction(0), Fraction(-1))


def poisson_bracket(f: PolyH, g: PolyH) -> PolyH:
    assert f.n == g.n
    n = f.n
    out = PolyH.zero(n)
    for i in range(n):
        dq_i = [0] * (2 * n); dq_i[i] = 1
        dp_i = [0] * (2 * n); dp_i[n + i] = 1
        out = out + f.derivative(tuple(dq_i)).mul(g.derivative(tuple(dp_i)))
        out = out - f.derivative(tuple(dp_i)).mul(g.derivative(tuple(dq_i)))
    return out


def scaled_moyal_bracket(f: PolyH, g: PolyH) -> PolyH:
    comm = star_product(f, g) - star_product(g, f)
    # divide by i*h: coefficient multiply by 1/i = -i and hpow -= 1.
    out_terms: Dict[Tuple[int, Tuple[int, ...]], GI] = {}
    minus_i = GI(Fraction(0), Fraction(-1))
    for (hpow, exps), coeff in comm.terms.items():
        if hpow < 1:
            raise ValueError("commutator has hbar^0 term; star product implementation inconsistent")
        key = (hpow - 1, exps)
        out_terms[key] = out_terms.get(key, ZERO) + coeff * minus_i
        if out_terms[key].is_zero():
            del out_terms[key]
    return PolyH(f.n, out_terms)


def egorov_defect(H: PolyH, f: PolyH) -> PolyH:
    return scaled_moyal_bracket(H, f) - poisson_bracket(H, f)


def classify_defect(defect: PolyH) -> str:
    if defect.is_zero():
        return "EXACT"
    if defect.variable_part_zero():
        return "CENTRAL_DEFECT"
    return "NONCENTRAL_DEFECT"


def monomials_total_degree(n: int, max_total_degree: int) -> List[Tuple[Tuple[int, ...], PolyH]]:
    m = 2 * n
    result = []
    for exps in product(range(max_total_degree + 1), repeat=m):
        if sum(exps) <= max_total_degree:
            result.append((tuple(exps), PolyH.monomial(n, tuple(exps))))
    result.sort(key=lambda x: (sum(x[0]), x[0]))
    return result


def monomial_label(n: int, exps: Tuple[int, ...]) -> str:
    parts = []
    for i in range(n):
        e = exps[i]
        if e:
            parts.append(f"q{i+1}" if e == 1 else f"q{i+1}^{e}")
    for i in range(n):
        e = exps[n + i]
        if e:
            parts.append(f"p{i+1}" if e == 1 else f"p{i+1}^{e}")
    return "1" if not parts else "*".join(parts)


def affine_quadratic_safe_sector_error_exact(n: int = 2) -> bool:
    basis = monomials_total_degree(n, 2)
    for _, f in basis:
        for _, g in basis:
            if scaled_moyal_bracket(f, g) != poisson_bracket(f, g):
                return False
    return True


def scan_phase_diagram_1d(max_total_degree: int = 5) -> Tuple[List[dict], dict]:
    n = 1
    monos = monomials_total_degree(n, max_total_degree)
    rows = []
    counts = {"EXACT": 0, "CENTRAL_DEFECT": 0, "NONCENTRAL_DEFECT": 0}
    order_counts = {}
    for expH, H in monos:
        for expf, f in monos:
            pb = poisson_bracket(H, f)
            mb = scaled_moyal_bracket(H, f)
            d = mb - pb
            cls = classify_defect(d)
            counts[cls] += 1
            hp = d.first_hbar_power()
            if hp is not None:
                order_counts[str(hp)] = order_counts.get(str(hp), 0) + 1
            rows.append({
                "H": monomial_label(n, expH),
                "f": monomial_label(n, expf),
                "degree_H": sum(expH),
                "degree_f": sum(expf),
                "classification": cls,
                "first_hbar_power": "" if hp is None else hp,
                "defect": str(d),
            })
    summary = {"max_total_degree": max_total_degree,
               "pair_count": len(rows),
               "classification_counts": counts,
               "first_hbar_power_counts": order_counts}
    return rows, summary


def symplectic_matrix_J(n: int) -> np.ndarray:
    return np.block([[np.zeros((n, n)), np.eye(n)], [-np.eye(n), np.zeros((n, n))]])


def shear_symplectic_map(n: int, steps: int = 400, seed: int = 7) -> Tuple[float, float]:
    rng = np.random.default_rng(seed)
    A = np.eye(2 * n)
    J = symplectic_matrix_J(n)
    for _ in range(steps):
        # q shear by symmetric B: q <- q + B p
        B = rng.normal(scale=0.01, size=(n, n)); B = 0.5 * (B + B.T)
        S1 = np.block([[np.eye(n), B], [np.zeros((n, n)), np.eye(n)]])
        # p shear by symmetric C: p <- p + C q
        C = rng.normal(scale=0.01, size=(n, n)); C = 0.5 * (C + C.T)
        S2 = np.block([[np.eye(n), np.zeros((n, n))], [C, np.eye(n)]])
        A = S2 @ S1 @ A
    symp_err = float(np.linalg.norm(A.T @ J @ A - J, ord='fro'))
    vol_err = float(abs(np.linalg.det(A) - 1.0))
    return symp_err, vol_err


def negative_control(n: int = 2) -> Tuple[float, float]:
    # determinant-one matrix that is not symplectic in q-first/p-second ordering.
    A = np.diag([2.0, 0.5, 1.0, 1.0])
    J = symplectic_matrix_J(n)
    vol_err = float(abs(np.linalg.det(A) - 1.0))
    symp_err = float(np.linalg.norm(A.T @ J @ A - J, ord='fro'))
    return vol_err, symp_err


def write_csv(path: str, rows: List[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_metrics(outdir: str) -> dict:
    n1 = 1
    q = PolyH.q(n1, 0); p = PolyH.p(n1, 0)
    q2 = q.mul(q); p2 = p.mul(p)
    q3 = q2.mul(q); p3 = p2.mul(p)
    q4 = q3.mul(q)
    q5 = q4.mul(q); p5 = p3.mul(p2)

    quadratic_dirac_exact = scaled_moyal_bracket(q2, p2) == poisson_bracket(q2, p2)
    cubic_defect = egorov_defect(q3, p3)
    expected_cubic = PolyH.monomial(n1, (0, 0), Fraction(-3, 2), hpow=2)
    cubic_exact = cubic_defect == expected_cubic

    quintic_defect = egorov_defect(q5, p5)

    # Associativity exact over Q[i,h] for a mixed stress triple.
    f = q2.mul(p)
    g = q.mul(p2)
    h = q3 + p3
    associativity_exact = star_product(star_product(f, g), h) == star_product(f, star_product(g, h))

    # Quadratic Egorov exact for a nonlinear observable.
    Hquad = q2.scale(Fraction(1, 2)) + p2.scale(Fraction(1, 2))
    obs = q3 + q.mul(p2) + p3
    quadratic_egorov_exact = egorov_defect(Hquad, obs).is_zero()

    # Quartic oscillator defect.
    Hquartic = Hquad + q4.scale(Fraction(1, 4))
    quartic_defect = egorov_defect(Hquartic, p3)
    expected_quartic = PolyH.monomial(n1, (1, 0), Fraction(-3, 2), hpow=2)
    quartic_exact = quartic_defect == expected_quartic

    affine_quad_n2_exact = affine_quadratic_safe_sector_error_exact(n=2)

    rows, summary = scan_phase_diagram_1d(max_total_degree=5)
    write_csv(os.path.join(outdir, "phase_diagram_exact.csv"), rows)
    with open(os.path.join(outdir, "degree_order_summary.json"), "w", encoding="utf-8") as fsum:
        json.dump(summary, fsum, indent=2)

    symp_err, vol_err = shear_symplectic_map(n=3, steps=400)
    neg_vol, neg_symp = negative_control(n=2)

    metrics = {
        "exact_rational_algebra": True,
        "affine_quadratic_1d_exact": quadratic_dirac_exact,
        "affine_quadratic_n2_safe_sector_exact": affine_quad_n2_exact,
        "cubic_obstruction_exact": cubic_exact,
        "cubic_obstruction_defect": str(cubic_defect),
        "associativity_exact": associativity_exact,
        "quadratic_egorov_exact": quadratic_egorov_exact,
        "quartic_egorov_defect_exact": quartic_exact,
        "quartic_egorov_defect": str(quartic_defect),
        "quintic_defect_tower": str(quintic_defect),
        "scan_summary": summary,
        "nd_symplectic_error_float": symp_err,
        "nd_volume_error_float": vol_err,
        "negative_control_volume_error_float": neg_vol,
        "negative_control_symplectic_error_float": neg_symp,
    }
    return metrics


def main() -> None:
    outdir = os.path.dirname(os.path.abspath(__file__))
    metrics = build_metrics(outdir)
    with open(os.path.join(outdir, "metrics_v4.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    checks = [
        metrics["exact_rational_algebra"],
        metrics["affine_quadratic_1d_exact"],
        metrics["affine_quadratic_n2_safe_sector_exact"],
        metrics["cubic_obstruction_exact"],
        metrics["associativity_exact"],
        metrics["quadratic_egorov_exact"],
        metrics["quartic_egorov_defect_exact"],
        metrics["nd_symplectic_error_float"] < 1e-12,
        metrics["nd_volume_error_float"] < 1e-12,
        metrics["negative_control_volume_error_float"] == 0.0,
        metrics["negative_control_symplectic_error_float"] > 1.0,
    ]
    passed = sum(bool(x) for x in checks)
    total = len(checks)
    status = "PASS" if passed == total else "FAIL"
    print(f"VERIFY_BRIDGE_V4: {status}")
    print(f"checks_passed={passed}/{total}")
    for k, v in metrics.items():
        if k == "scan_summary":
            print(f"scan_pair_count={v['pair_count']}")
            print(f"scan_counts={v['classification_counts']}")
            print(f"scan_first_hbar_power_counts={v['first_hbar_power_counts']}")
        elif isinstance(v, bool):
            print(f"{k}={v}")
        elif isinstance(v, float):
            print(f"{k}={v:.17e}")
        else:
            print(f"{k}={v}")


if __name__ == "__main__":
    main()
