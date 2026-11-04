"""Galois norms of cyclotomic collision factors, with scoped classification.

The norm is taken at each prime before multiplying Euler factors.  This is
different from a trace/average, and from an individual complex phase product.
All returned polynomial coefficients are exact integers in ascending order.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import gcd

from .rings import QuotientRing, cyclotomic


def _positive_integer(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(name + " must be a positive integer")
    return value


def _mobius(n):
    sign, prime = 1, 2
    while prime * prime <= n:
        if n % prime == 0:
            n //= prime
            sign = -sign
            if n % prime == 0:
                return 0
            while n % prime == 0:
                n //= prime
        prime += 1
    return -sign if n > 1 else sign


def _multiply(left, right, ring):
    result = [ring.zero] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        if a == 0:
            continue
        for j, b in enumerate(right):
            if b != 0:
                result[i + j] += a * b
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def _integers(coefficients):
    result = []
    for value in coefficients:
        if any(value.coefficients[1:]):
            raise ArithmeticError("Galois invariant coefficient was not rational")
        rational = value.coefficients[0]
        if rational.denominator != 1:
            raise ArithmeticError("Galois norm/trace coefficient was not integral")
        result.append(int(rational))
    return tuple(result)


@dataclass(frozen=True)
class CollisionNorm:
    """Uncancelled rational factor P_L(x)/(1-x^L)^(2 phi(L)).

    Keeping the denominator unaltered preserves the exact norm convention.
    Cyclotomic numerator factors may cancel it; that does not change the
    natural-boundary classification of the remaining noncyclotomic factor.
    """
    conductor: int
    field_degree: int
    numerator: tuple[int, ...]
    trace_numerator: tuple[int, ...]
    estimated_work: int

    @property
    def denominator_period(self):
        return self.conductor

    @property
    def denominator_power(self):
        return 2 * self.field_degree

    def report(self):
        l, phi = self.conductor, self.field_degree
        expected_leading = -1 if l == 2 else 1
        finite = {
            "constant_is_one": self.numerator[0] == 1,
            "degree": len(self.numerator) - 1,
            "expected_degree": (2 * l - 2) * phi,
            "leading_coefficient": self.numerator[-1],
            "expected_leading_coefficient": expected_leading,
            "numerator_at_one": sum(self.numerator),
            "expected_numerator_at_one": l ** phi,
            "all_coefficients_integral": True,
        }
        if l > 1:
            finite.update(
                first_coefficient=self.numerator[1],
                expected_first_coefficient=2 * phi,
                penultimate_coefficient=self.numerator[-2],
                expected_penultimate_coefficient=2 * _mobius(l) * expected_leading,
                reciprocal_necessity_fails=(
                    self.numerator[-2] != self.numerator[-1] * self.numerator[1]
                ),
            )
        return {
            "schema": "perfectjet/collision-norm/1",
            "conductor": l,
            "cyclotomic_field_degree": phi,
            "numerator": list(self.numerator),
            "coefficient_order": "ascending",
            "denominator": {"form": "(1-x^L)^power", "L": l, "power": 2 * phi},
            "primitive_galois_trace_numerator": list(self.trace_numerator),
            "trace_note": "Trace is a sum, not an Euler factor normalized to constant one.",
            "finite_checks": finite,
            "classification": {
                "finite_zeta_product": l == 1,
                "natural_boundary_re_s_zero": l > 1,
                "scope": "prime-local full Galois norm Euler product",
                "basis": "symbolic all-conductor proof plus classical Estermann theorem",
            },
            "estimated_scalar_work": self.estimated_work,
            "limits": [
                "No classification of a single complex-phase Euler product is inferred.",
                "No Lean kernel formalization or historical priority claim.",
                "Finite coefficient checks accompany, rather than prove, the all-conductor theorem.",
            ],
        }


def collision_norm(conductor, *, max_conductor=32, max_degree=1024,
                   max_work=5_000_000):
    """Multiply all primitive Galois conjugates in the exact cyclotomic ring.

    Preflight bounds cover conductor, output degree, and a conservative count
    of field scalar products plus factor construction.  They are work bounds,
    not elapsed-time promises.  A caller may explicitly raise them.
    """
    l = _positive_integer(conductor, "conductor")
    for name, value in (("max_conductor", max_conductor), ("max_degree", max_degree),
                        ("max_work", max_work)):
        _positive_integer(value, name)
    if l > max_conductor:
        raise ValueError("conductor budget exceeded before field construction")
    units = tuple(a for a in range(1, l + 1) if gcd(a, l) == 1)
    phi = len(units)
    factor_degree = 2 * l - 2
    norm_degree = factor_degree * phi
    if norm_degree > max_degree:
        raise ValueError("norm degree budget exceeded before field construction")
    products = sum((k * factor_degree + 1) * (factor_degree + 1)
                   for k in range(phi))
    work = products * phi * phi + phi * l * l * phi
    if work > max_work:
        raise ValueError("norm scalar-work budget exceeded before field construction")

    ring = QuotientRing(cyclotomic(l))
    powers = [ring.one]
    for _ in range(1, l):
        powers.append(powers[-1] * ring.generator)
    result = [ring.one]
    trace = [ring.zero] * (factor_degree + 1)
    for a in units:
        factor = [ring.zero] * (factor_degree + 1)
        for r in range(l):
            for s in range(l):
                factor[r + s] += powers[(a * r * s) % l]
        trace = [x + y for x, y in zip(trace, factor)]
        result = _multiply(result, factor, ring)
    numerator, traced = _integers(result), _integers(trace)
    if len(numerator) - 1 != norm_degree:
        raise ArithmeticError("norm lost its predicted nonzero leading coefficient")
    return CollisionNorm(l, phi, numerator, traced, work)


def norm_classification_theorem():
    """Symbolic statement; it does not enumerate an unbounded set of conductors."""
    return {
        "status": "derived mathematical theorem; not Lean formalized",
        "domain": "every integer conductor L>=1",
        "local_factor": "Norm_Q(zeta_L)/Q(N_L(x))/(1-x^L)^(2*phi(L))",
        "L_equals_1": "zeta(s)^2; finite zeta product",
        "L_greater_than_1": "meromorphic on Re(s)>0; every point Re(s)=0 is a natural boundary",
        "scope": "prime-local full Galois norm Euler product",
        "proof": [
            "For each primitive zeta, N has c0=1,c1=2,cD=zeta,c(D-1)=2*zeta^2, D=2L-2.",
            "If all roots were unit-modulus, self-inversiveness would require c(D-1)=cD*conjugate(c1)=2*zeta, impossible when L>1.",
            "Constant and leading coefficients have equal modulus, so each N has roots inside and outside the unit circle.",
            "The product over all Galois conjugates is an integer polynomial with constant one and a non-unit-modulus root.",
            "Estermann applies to its prime Euler product; multiplying by zeta(L*s)^(2*phi(L)) cannot remove its natural boundary.",
        ],
        "single_complex_phase_product": "not classified by this theorem",
        "source": "docs/COLLISION_NORM_CLASSIFICATION.md",
    }
