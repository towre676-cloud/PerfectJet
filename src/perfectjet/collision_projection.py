"""Exact prime-local collision projections and their all-conductor classification.

The local character average imposes L | a*b at each prime separately.  It is
not a global character average imposing L | sum_p a_p*b_p.  Coefficients are
ordinary Python integers; all finite calculations below are exact.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import gcd, isqrt


DEFAULT_MAX_CONDUCTOR = 256
DEFAULT_MAX_TERMS = 1_000_000


def _integer(value, name, minimum):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        adjective = "positive" if minimum else "nonnegative"
        raise ValueError(f"{name} must be a {adjective} integer")
    return value


def classification_theorem():
    """A written all-L proof, separate from any finite constructor replay."""
    return {
        "status": "derived_written_proof_not_formalized",
        "domain": "every positive integer conductor L",
        "local_numerator": "C_L(x)=sum_{0<=r,s<L; L|r*s} x^(r+s)",
        "unit_root_numerator_iff": "L is 1 or 4",
        "finite_zeta_product_iff": "L is 1 or 4",
        "finite_zeta_exceptions": {
            "1": "zeta(s)^2",
            "4": "zeta(s)^2*zeta(4*s)/zeta(2*s)",
        },
        "other_conductors": "meromorphic on Re(s)>0; Re(s)=0 is a natural boundary",
        "analytic_input": "classical Estermann theorem for integer polynomials with constant term 1",
        "proof": "docs/COLLISION_PROJECTION_CLASSIFICATION.md",
        "scope": "prime-local condition L|v_p(m)*v_p(n) for every prime p",
        "excluded_inference": "not the global condition L|kappa(m,n)",
        "finite_sampling_is_not_the_proof": True,
    }


def projection_classification_theorem():
    """Named public entry point for the prime-local projection theorem."""
    return classification_theorem()


@dataclass(frozen=True, init=False)
class PrimeLocalCollisionProjection:
    """Immutable integer numerator for the prime-local divisibility condition.

    Work L^2 and the conductor bound are checked before allocating the residue
    census.  Increasing a budget changes supported computation, not the theorem.
    """

    conductor: int
    numerator: tuple[int, ...]

    def __init__(self, conductor, *, max_conductor=DEFAULT_MAX_CONDUCTOR,
                 max_terms=DEFAULT_MAX_TERMS):
        conductor = _integer(conductor, "conductor", 1)
        max_conductor = _integer(max_conductor, "max_conductor", 1)
        max_terms = _integer(max_terms, "max_terms", 1)
        if conductor > max_conductor:
            raise ValueError("conductor exceeds max_conductor")
        if conductor * conductor > max_terms:
            raise ValueError("residue census exceeds max_terms before allocation")
        coefficients = [0] * (2 * conductor - 1)
        for r in range(conductor):
            for s in range(conductor):
                if (r * s) % conductor == 0:
                    coefficients[r + s] += 1
        while len(coefficients) > 1 and coefficients[-1] == 0:
            coefficients.pop()
        object.__setattr__(self, "conductor", conductor)
        object.__setattr__(self, "numerator", tuple(coefficients))

    @property
    def denominator(self):
        """Coefficients of the unreduced denominator (1-x^L)^2."""
        coefficients = [0] * (2 * self.conductor + 1)
        coefficients[0] = coefficients[-1] = 1
        coefficients[self.conductor] = -2
        return tuple(coefficients)

    @property
    def finite_zeta_exponents(self):
        """Pairs (argument multiplier, exponent), or None outside the exceptions."""
        if self.conductor == 1:
            return ((1, 2),)
        if self.conductor == 4:
            return ((1, 2), (2, -1), (4, 1))
        return None

    def local_exponent_allowed(self, a, b):
        a = _integer(a, "first exponent", 0)
        b = _integer(b, "second exponent", 0)
        return (a * b) % self.conductor == 0

    def coefficient(self, index):
        """Count exponent pairs of a given total, including arbitrarily large indices."""
        index = _integer(index, "index", 0)
        total = 0
        for degree, coefficient in enumerate(self.numerator):
            if degree <= index and (index - degree) % self.conductor == 0:
                total += coefficient * ((index - degree) // self.conductor + 1)
        return total

    def direct_coefficient(self, index, *, max_terms=DEFAULT_MAX_TERMS):
        """Independent unsplit exponent-pair census with a preflight work budget."""
        index = _integer(index, "index", 0)
        max_terms = _integer(max_terms, "max_terms", 1)
        if index + 1 > max_terms:
            raise ValueError("direct exponent-pair census exceeds max_terms")
        return sum(1 for a in range(index + 1)
                   if (a * (index - a)) % self.conductor == 0)

    def report(self):
        """JSON-compatible exact checks and the separately proved classification."""
        conductor = self.conductor
        degree = len(self.numerator) - 1
        mass = sum(self.numerator)
        derivative = sum(i * c for i, c in enumerate(self.numerator))
        closest_sum = min(d + conductor // d for d in range(1, conductor + 1)
                          if conductor % d == 0)
        square = isqrt(conductor) ** 2 == conductor
        finite = self.finite_zeta_exponents
        return {
            "schema": "perfectjet/prime-local-collision-projection/1",
            "arithmetic": "exact integers",
            "conductor": conductor,
            "numerator": list(self.numerator),
            "denominator": list(self.denominator),
            "denominator_expression": f"(1-x^{conductor})^2",
            "degree": degree,
            "leading_coefficient": self.numerator[-1],
            "numerator_at_one": mass,
            "numerator_derivative_at_one": derivative,
            "reciprocal": self.numerator == self.numerator[::-1],
            "checks": {
                "constant_term_one": self.numerator[0] == 1,
                "degree_from_closest_divisors": degree == 2 * conductor - closest_sum,
                "leading_from_square_status": self.numerator[-1] == (1 if square else 2),
                "mass_is_gcd_sum": mass == sum(gcd(r, conductor) for r in range(conductor)),
                "derivative_identity": derivative == conductor * (mass - conductor),
                "reciprocity_classification": (self.numerator == self.numerator[::-1]) == (conductor in (1, 4)),
            },
            "classification": "finite_zeta_product" if finite is not None else "natural_boundary",
            "finite_zeta_exponents": [list(pair) for pair in finite] if finite is not None else None,
            "meromorphic_domain": "C" if finite is not None else "Re(s)>0",
            "natural_boundary": None if finite is not None else "Re(s)=0",
            "theorem": classification_theorem(),
            "global_semantics": "L divides v_p(m)*v_p(n) separately for every prime p",
            "not_global_total_collision": "L|sum_p v_p(m)*v_p(n) alone is insufficient",
        }


def collision_projection(conductor, *, max_conductor=DEFAULT_MAX_CONDUCTOR,
                         max_terms=DEFAULT_MAX_TERMS):
    """Construct the immutable prime-local projection for one supported conductor."""
    return PrimeLocalCollisionProjection(
        conductor, max_conductor=max_conductor, max_terms=max_terms)
