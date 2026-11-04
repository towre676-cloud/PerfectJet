"""An effective square-root/log-squared collision remainder.

The positive residual product G(s)=prod_p(1+4*p**(-3*s)+3*p**(-4*s))
converges at s=1/2.  Factoring |h| through square-supported divisor
coefficients removes the sigma-dependent pole in the earlier majorant.
The complete derivation is in docs/COLLISION_SQRT_REMAINDER.md.
"""
from fractions import Fraction as Q
from functools import lru_cache

from .collision_constants import _cutoff, primes_up_to
from .collision_intervals import Interval, _precision, euler_gamma_bounds, power_bounds
from .collision_majorant import wheel_power_tail


DIVISOR_COEFFICIENT = Q(6, 5)
SMALL_ARGUMENT_KERNEL_BOUND = Q(10)
MAX_X_BITS = 1024


@lru_cache(maxsize=64)
def _g_half_bounds(prime_cutoff, bits):
    effective = max(prime_cutoff, 7)
    partial = Interval(1, bits=bits)
    primes = primes_up_to(effective)
    for p in primes:
        x = power_bounds(p, Q(-1, 2), bits=bits)
        partial *= 1 + 4 * x ** 3 + 3 * x ** 4
    tail = (4 * wheel_power_tail(Q(3, 2), effective, bits)
            + 3 * wheel_power_tail(Q(2), effective, bits))
    upper = (partial * Interval(0, tail, bits=bits).exp()).upper
    return Interval(partial.lower, upper, bits=bits), partial, tail, effective, len(primes)


def g_half_bounds(prime_cutoff=1000, bits=80):
    """Enclose G(1/2), including all primes and an explicit residual tail."""
    prime_cutoff = _cutoff(prime_cutoff)
    bits = _precision(bits)
    value, partial, tail, effective, count = _g_half_bounds(prime_cutoff, bits)
    return {"lower": value.lower, "upper": value.upper,
            "G_half": value.record(), "partial_product": partial.record(),
            "tail_log_upper": tail, "prime_cutoff": prime_cutoff,
            "effective_prime_cutoff": effective, "prime_count": count,
            "tail_method": "positive residual product and reduced-residue modulo-210 integral tails"}


def sqrt_remainder_bound(X, prime_cutoff=1000, bits=80):
    """Return a rigorous bound for |S(X)-C*X*log(X)-K*X|, X>=1.

    X is an exact integer or Fraction, with a 1024-bit input budget. The
    returned endpoint is a Fraction; the other fields record the constant
    and polynomial evidence. No sigma is chosen or implicitly rounded.
    """
    if isinstance(X, bool) or not isinstance(X, (int, Q)):
        raise ValueError("X must be an exact integer or Fraction")
    X = Q(X)
    if X < 1:
        raise ValueError("X must be at least one")
    if max(X.numerator.bit_length(), X.denominator.bit_length()) > MAX_X_BITS:
        raise ValueError(f"X exceeds the {MAX_X_BITS}-bit input budget")
    prime_cutoff = _cutoff(prime_cutoff)
    bits = _precision(bits)
    k = DIVISOR_COEFFICIENT
    c = 2 * euler_gamma_bounds(bits=bits) - 1
    # kappa(c)=c+integral_0^infinity exp(-3v/2)*|2-2c-4v| dv.
    kappa = -Q(4, 9) - c / 3 + Q(32, 9) * (-Q(3, 4) * (1 - c)).exp()
    residual = max(Q(0), (k * (kappa - k)).upper)
    linear = k * (1 + c) + c + 2
    constant = k * (c + 2 * k) + (c + 2) * (c + 1) + c + 4 + residual
    x = Interval(X, bits=bits)
    logarithm = x.log() / 2
    polynomial = Q(1, 2) * k * logarithm ** 2 + linear * logarithm + constant
    kernel_upper = max(SMALL_ARGUMENT_KERNEL_BOUND, polynomial.upper)
    g = g_half_bounds(prime_cutoff=prime_cutoff, bits=bits)
    remainder = (x.pow(Q(1, 2)) * g["upper"] * kernel_upper).upper
    return {
        "X": X, "prime_cutoff": prime_cutoff, "bits": bits,
        "remainder_upper": remainder, "G_half_upper": g["upper"],
        "G_half_evidence": g,
        "polynomial_coefficients": {
            "log_sqrt_squared": Q(1, 2) * k,
            "log_sqrt": linear.record(), "constant": constant.record(),
        },
        "polynomial_upper": polynomial.upper,
        "kernel_upper": kernel_upper,
        "small_argument_kernel_upper": SMALL_ARGUMENT_KERNEL_BOUND,
        "divisor_coefficient": k, "c": c.record(), "kappa": kappa.record(),
        "theorem": "abs(S(X)-M(X)) <= G(1/2)*sqrt(X)*max(10,P(log(X)/2))",
        "proof": "docs/COLLISION_SQRT_REMAINDER.md",
    }
