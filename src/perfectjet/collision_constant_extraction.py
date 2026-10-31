"""Sharper conductor-two constants by one finite zeta-factor extraction.

H(s)=zeta(2s)**-2 * product_p R(p**-s), where
R(x)=(1+2x-x*x)/((1-x)**2*(1+x)**4).
The residual starts at degree three. All finite factors and prime tails are
evaluated rigorously; this is not an infinite formal zeta factorization.
See docs/COLLISION_CONSTANT_EXTRACTION.md for the full derivation.
"""
from fractions import Fraction as Q
from functools import lru_cache
from math import gcd

from .collision_constants import _cutoff, primes_up_to
from .collision_intervals import Interval, _precision, euler_gamma_bounds, log_bounds
from .collision_zeta_intervals import zeta_two_constants


WHEEL = 210
RESIDUES = tuple(r for r in range(1, WHEEL) if gcd(r, WHEEL) == 1)


def residual_factor(prime):
    """Exact R(1/p) for an integer p>=2; primality is not required here."""
    if isinstance(prime, bool) or not isinstance(prime, int) or prime < 2:
        raise ValueError("prime argument must be an integer at least two")
    if prime.bit_length() > 64:
        raise ValueError("residual argument exceeds the integer bit budget")
    return Q(prime**4 * (prime*prime + 2*prime - 1),
             (prime - 1)**2 * (prime + 1)**4)


def residual_derivative_weight(prime):
    """Exact positive g(1/p), g(x)=x R'(x)/R(x)."""
    if isinstance(prime, bool) or not isinstance(prime, int) or prime < 2:
        raise ValueError("prime argument must be an integer at least two")
    if prime.bit_length() > 64:
        raise ValueError("residual argument exceeds the integer bit budget")
    return Q(4 * (3*prime - 1),
             (prime*prime - 1) * (prime*prime + 2*prime - 1))


def residual_tail_bounds(prime_cutoff=1000, bits=80):
    """Bound sum log R(1/p) and sum log(p)*g(1/p) over omitted primes.

    The valid all-integer bounds are 4/(2P^2) and
    12*(2log(P)+1)/(4P^2). Reduced residue progressions modulo 210 give
    independent stronger bounds. Every omitted prime belongs to one of
    those progressions for P>=7. Tiny requested cutoffs use effective P=7.
    """
    requested = _cutoff(prime_cutoff)
    bits = _precision(bits)
    cutoff = max(7, requested)
    integer_power = Q(1, 2 * cutoff * cutoff)
    integer_log = (2 * log_bounds(cutoff, bits=bits) + 1) / (4 * cutoff * cutoff)
    wheel_power = Q(0)
    wheel_log = Interval(0, bits=bits)
    for residue in RESIDUES:
        first = residue + WHEEL * ((cutoff - residue) // WHEEL + 1)
        wheel_power += Q(1, first**3) + Q(1, 2 * WHEEL * first**2)
        logarithm = log_bounds(first, bits=bits)
        wheel_log += (logarithm / first**3 +
                      (2 * logarithm + 1) / (4 * WHEEL * first**2))
    log_upper = 4 * min(integer_power, wheel_power)
    derivative_upper = 12 * min(integer_log.upper, wheel_log.upper)
    return {"prime_cutoff": requested, "effective_prime_cutoff": cutoff,
            "log_tail": Interval(0, log_upper, bits=bits),
            "derivative_magnitude_tail": Interval(0, derivative_upper, bits=bits),
            "power_prime_tail_upper": min(integer_power, wheel_power),
            "log_power_prime_tail_upper": min(integer_log.upper, wheel_log.upper),
            "method": "minimum of integer and reduced-residue modulo-210 integral tails"}


@lru_cache(maxsize=32)
def _extracted_values(prime_cutoff, bits):
    tails = residual_tail_bounds(prime_cutoff, bits)
    effective = tails["effective_prime_cutoff"]
    primes = primes_up_to(effective)
    residual = Interval(1, bits=bits)
    derivative_magnitude = Interval(0, bits=bits)
    for prime in primes:
        residual *= residual_factor(prime)
        derivative_magnitude += residual_derivative_weight(prime) * log_bounds(prime, bits=bits)
    zeta = zeta_two_constants(bits=bits)
    zeta2, zeta_prime = zeta["zeta2"], zeta["zeta2_derivative"]
    c_base = residual / zeta2**2
    c = c_base * tails["log_tail"].exp()
    d_base = -4 * zeta_prime / zeta2 - derivative_magnitude
    magnitude = tails["derivative_magnitude_tail"]
    d = d_base - magnitude
    gamma = euler_gamma_bounds(bits=bits)
    secondary = c * (2 * gamma - 1 + d)
    return {"C": c, "D": d, "gamma": gamma, "K": secondary,
            "partial_C": c_base, "partial_D": d_base,
            "prime_cutoff": prime_cutoff, "effective_prime_cutoff": effective,
            "prime_count": len(primes), "bits": bits,
            "method": "finite zeta(2s)^-2 extraction with cubic residual prime tails",
            "tail_method": tails["method"],
            "evidence": {
                "identity": "H(s)=zeta(2s)^(-2)*prod_p R(p^(-s)); R(x)=(1+2x-x^2)/((1-x)^2*(1+x)^4)",
                "prime_cutoff": prime_cutoff, "effective_prime_cutoff": effective,
                "zeta2": zeta2.record(), "zeta2_derivative": zeta_prime.record(),
                "zeta_evaluation": zeta.get("evidence", {}),
                "residual_partial_product": residual.record(),
                "residual_derivative_magnitude_partial_sum": derivative_magnitude.record(),
                "residual_log_tail": tails["log_tail"].record(),
                "residual_derivative_tail": (-magnitude).record(),
                "tail_method": tails["method"],
            }}


def extracted_asymptotic_constants(prime_cutoff=1000, bits=80):
    """Certified C,D,gamma,K with prime tails of order P^-2 and log(P)P^-2.

    ``partial_C`` and ``partial_D`` are finite extracted expressions, rather
    than the direct finite product and derivative sum. Their omitted tails
    respectively increase C and decrease D. The evidence records those signs.
    Return a fresh dictionary so callers cannot modify the cached values.
    """
    prime_cutoff = _cutoff(prime_cutoff)
    bits = _precision(bits)
    from copy import deepcopy
    return deepcopy(_extracted_values(prime_cutoff, bits))
