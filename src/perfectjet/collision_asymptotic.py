"""Certified finite-input conductor-two cumulative counts.

The proof is in docs/COLLISION_FINITE_X.md. No floating-point value enters
the enclosure. The point prediction is the midpoint of a certified interval
for the two-term main term, not an exact count.
"""
from fractions import Fraction
from functools import lru_cache
import re

from .collision_intervals import Interval, asymptotic_constants
from .collision_majorant import majorant_bounds, _sigma


SIGMA_GRID = (Fraction(51, 100), Fraction(21, 40), Fraction(11, 20),
              Fraction(23, 40)) + tuple(Fraction(n, 20) for n in range(12, 19))
MAX_X_BITS = 1024


def _rational(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, str, Fraction)):
        raise ValueError(f"{name} must be an integer, rational string or Fraction")
    if isinstance(value, str) and len(value) > 1024:
        raise ValueError(f"{name} exceeds the input length budget")
    if isinstance(value, str):
        value = value.strip()
        # Fraction accepts scientific notation with an arbitrarily large
        # exponent. Reject it before parsing, so the bit budget is a real
        # preflight bound rather than a check after allocating 10**exponent.
        if re.fullmatch(r"[+-]?(?:[0-9]+(?:/[0-9]+)?|[0-9]*\.[0-9]+)", value) is None:
            raise ValueError(f"{name} must be a bounded integer, fraction or decimal string")
    try:
        value = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"invalid rational {name}") from exc
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > MAX_X_BITS:
        raise ValueError(f"{name} exceeds the {MAX_X_BITS}-bit input budget")
    return value


def _ceil(value):
    return -((-value.numerator) // value.denominator)


@lru_cache(maxsize=24)
def _constants(cutoff, bits):
    return asymptotic_constants(prime_cutoff=cutoff, bits=bits)


@lru_cache(maxsize=128)
def _majorant(sigma, cutoff, bits):
    return majorant_bounds(sigma=sigma, prime_cutoff=cutoff, bits=bits)


def remainder_coefficient(sigma, gamma, bits=80):
    """max(6/5, exp(-1-(1-sigma)*(2*gamma-1))/(1-sigma))."""
    a = 1 - sigma
    c = 2 * gamma - 1
    tail = (-1 - a * c).exp() / a
    return max(Fraction(6, 5), tail.upper)


def counting_certificate(X, sigma="auto", prime_cutoff=1000, bits=80,
                         include_exact=False):
    """Enclose S(X)=sum(n<=X) A(n), for rational X>=1.

    Auto compares a documented finite rational sigma grid using rigorous
    upper bounds. It does not claim a global parameter optimum. Increasing
    prime_cutoff can improve both the constants and the majorant.
    """
    X = _rational(X, "X")
    if X < 1:
        raise ValueError("X must be at least one")
    if not isinstance(include_exact, bool):
        raise ValueError("include_exact must be Boolean")
    # Validate cheap arguments before constructing any prime products.
    if isinstance(bits, bool) or not isinstance(bits, int) or not 32 <= bits <= 256:
        raise ValueError("bits must be an integer in [32,256]")
    if (isinstance(prime_cutoff, bool) or not isinstance(prime_cutoff, int)
            or not 2 <= prime_cutoff <= 10000):
        raise ValueError("prime_cutoff must be an integer in [2,10000]")
    if sigma == "auto":
        sigmas = SIGMA_GRID
    else:
        sigmas = (_sigma(_rational(sigma, "sigma")),)
        if min(2 * sigmas[0] - 1, 1 - sigmas[0]) <= Fraction(1, 1 << bits):
            raise ValueError("sigma is too close to a boundary for the supplied bits")
    if include_exact:
        from .collision_counting import MAX_CONVOLUTION_X
        if X.numerator // X.denominator > MAX_CONVOLUTION_X:
            raise ValueError(f"exact replay exceeds the {MAX_CONVOLUTION_X} input budget")
    constants = _constants(prime_cutoff, bits)
    x = Interval(X, bits=bits)
    log_x = x.log()
    main = constants["C"] * x * log_x + constants["K"] * x
    candidates = []
    for s in sigmas:
        b = _majorant(s, prime_cutoff, bits)
        coefficient = remainder_coefficient(s, constants["gamma"], bits)
        radius = (x.pow(s) * b["upper"] * coefficient).upper
        candidates.append({"sigma": s, "B_upper": b["upper"],
                           "coefficient_upper": coefficient,
                           "remainder_upper": radius,
                           "tail_log_upper": b["tail_log_upper"]})
    best = min(candidates, key=lambda row: row["remainder_upper"])
    radius = best["remainder_upper"]
    raw_lower, raw_upper = main.lower - radius, main.upper + radius
    N = X.numerator // X.denominator
    # 1<=A(n)<=d(n) and sum d(n)<=N H_N<=N(1+log N).
    structural_upper = (Interval(N, bits=bits) *
                        (1 + Interval(N, bits=bits).log())).upper
    lower = max(N, _ceil(raw_lower))
    upper = min(structural_upper.numerator // structural_upper.denominator,
                raw_upper.numerator // raw_upper.denominator)
    record = {
        "schema": "perfectjet/conductor-two-finite-x/1",
        "X": X, "floor_X": N, "sigma": best["sigma"],
        "prime_cutoff": prime_cutoff, "bits": bits,
        "prediction": (main.lower + main.upper) / 2,
        "main_term": main.record(), "remainder_upper": radius,
        "prediction_error_upper": radius + (main.upper - main.lower) / 2,
        "analytic_enclosure": {"lower": raw_lower, "upper": raw_upper},
        "count_enclosure": {"lower": lower, "upper": upper},
        "constants": {name: constants[name].record() for name in ("C", "D", "gamma", "K")},
        "constant_evidence": {
            "partial_C": constants["partial_C"].record(),
            "partial_D": constants["partial_D"].record(),
            "C_tail_loss_upper": constants["C_tail_loss_bound"],
            "D_tail": constants["D_tail_bound"].record(),
            "tail_method": constants["tail_method"],
        },
        "majorant_method": "zeta(2sigma)^2 extraction with a positive residual Euler product and modulo-210 prime tails",
        "parameter_candidates": candidates,
        "parameter_selection": "minimum certified radius on the stated finite sigma grid" if sigma == "auto" else "supplied rational sigma",
        "theorem": "abs(S(X)-C*X*log(X)-K*X) <= B_sigma*X^sigma*max(6/5,exp(-1-(1-sigma)*(2*gamma-1))/(1-sigma))",
        "proof": "docs/COLLISION_FINITE_X.md",
        "arithmetic": "outward-rounded rational intervals with explicit series and Euler-product tails",
        "count_semantics": "positive grouped conductor-two coefficients A(p^e)=1 for even e and e+1 for odd e",
    }
    if include_exact:
        from .collision_counting import exact_count
        exact = exact_count(N)
        if not lower <= exact <= upper:
            raise ArithmeticError("exact replay lies outside certified enclosure")
        record["exact_count"] = exact
        record["observed_error"] = Interval(exact, bits=bits).__sub__(main).record()
        record["exact_count_enclosed"] = True
    return record


def certificate_receipt(*args, **kwargs):
    """JSON-safe form of counting_certificate; all endpoints remain rational."""
    from .collision_research import json_value
    return json_value(counting_certificate(*args, **kwargs))
