"""Computable absolute-coefficient norms for conductor-two certificates.

The exact local extraction

    (1 + 2*x**2/(1-x)**2) * (1-x**2)**2 = 1 + 4*x**3 + 3*x**4

isolates zeta(2*sigma)**2.  Its residual product has a much faster prime
tail, even when sigma is close to one half.  Neither prime-density estimates
nor numerical special-function evaluations enter the calculation.
"""
from fractions import Fraction as Q
from functools import lru_cache
from math import gcd

from .collision_constants import _cutoff, _integer, primes_up_to
from .collision_intervals import Interval, _precision, power_bounds


WHEEL = 210
RESIDUES = tuple(r for r in range(1, WHEEL) if gcd(r, WHEEL) == 1)
MAX_SIGMA_BITS = 128
MAX_ZETA_CUTOFF = 4096


def _sigma(value):
    if isinstance(value, bool) or not isinstance(value, (int, Q)):
        raise ValueError("sigma must be an exact Fraction strictly between 1/2 and 1")
    value = Q(value)
    if not Q(1, 2) < value < 1:
        raise ValueError("sigma must be strictly between 1/2 and 1")
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_SIGMA_BITS:
        raise ValueError("sigma exceeds the rational-input bit budget")
    return value


def wheel_power_tail(exponent, prime_cutoff, bits=80):
    """Upper bound for ``sum(p**-exponent, prime p>prime_cutoff)``.

    For P>=7 every omitted prime is in a reduced residue class modulo 210.
    If n_r is the first integer above P in that class, monotonicity gives

      sum(k>=0) (n_r+210*k)**-a
        <= n_r**-a + n_r**(1-a)/(210*(a-1)).

    For smaller P the missing wheel primes are added individually.  This
    bound is elementary and valid at composite and prime cutoffs alike.
    """
    prime_cutoff = _cutoff(prime_cutoff)
    bits = _precision(bits)
    if isinstance(exponent, bool) or not isinstance(exponent, (int, Q)):
        raise ValueError("tail exponent must be an exact rational greater than one")
    exponent = Q(exponent)
    if exponent <= 1 or exponent > 16:
        raise ValueError("tail exponent must lie in (1,16]")
    effective = max(prime_cutoff, 7)
    total = Interval(0, bits=bits)
    for p in (2, 3, 5, 7):
        if prime_cutoff < p:
            total += power_bounds(p, -exponent, bits)
    for residue in RESIDUES:
        first = residue + WHEEL * ((effective - residue) // WHEEL + 1)
        term = power_bounds(first, -exponent, bits)
        # first**(1-a) = first * first**(-a), with the same input enclosure.
        total += term * (1 + Q(first, WHEEL) / (exponent - 1))
    return total.upper


def zeta_real_bounds(exponent, summation_cutoff=64, bits=80):
    """Enclose zeta(a), 1<a<2, without a special-function dependency.

    With f(t)=t**-a, convexity bounds its tail by

      integral_N^infinity f - f(N)/2
        <= sum(n>N) f(n) <= integral_(N+1/2)^infinity f.

    The lower bound is the trapezoid inequality, and the upper bound is
    the midpoint inequality on consecutive unit intervals.  Their gap is
    O(N**(-a-1)); there is no unquantified remainder.
    """
    bits = _precision(bits)
    if isinstance(exponent, bool) or not isinstance(exponent, (int, Q)):
        raise ValueError("zeta exponent must be an exact rational in (1,2)")
    exponent = Q(exponent)
    if not 1 < exponent < 2:
        raise ValueError("zeta exponent must lie in (1,2)")
    if exponent - 1 <= Q(1, 1 << bits):
        raise ValueError("zeta exponent is too close to one for the requested bits")
    cutoff = _integer(summation_cutoff, "summation_cutoff", 1)
    if cutoff > MAX_ZETA_CUTOFF:
        raise ValueError(f"summation_cutoff exceeds {MAX_ZETA_CUTOFF}")
    partial = Interval(0, bits=bits)
    for n in range(1, cutoff + 1):
        partial += power_bounds(n, -exponent, bits)
    endpoint = power_bounds(cutoff, -exponent, bits)
    lower_tail = endpoint * (Q(cutoff) / (exponent - 1) - Q(1, 2))
    upper_tail = power_bounds(Q(2 * cutoff + 1, 2), 1 - exponent, bits) / (exponent - 1)
    return Interval((partial + lower_tail).lower, (partial + upper_tail).upper, bits=bits)


@lru_cache(maxsize=128)
def _majorant_values(sigma, prime_cutoff, bits, zeta_cutoff):
    # Including all four wheel primes keeps the tail formula simple at tiny
    # requested cutoffs.  Report the effective cutoff explicitly.
    effective = max(prime_cutoff, 7)
    residual = Interval(1, bits=bits)
    direct = Interval(1, bits=bits)
    primes = primes_up_to(effective)
    for p in primes:
        x = power_bounds(p, -sigma, bits)
        residual *= 1 + 4 * x ** 3 + 3 * x ** 4
        direct *= 1 + 2 * x ** 2 / (1 - x) ** 2
    zeta = zeta_real_bounds(2 * sigma, zeta_cutoff, bits)
    tail_log_upper = (4 * wheel_power_tail(3 * sigma, effective, bits)
                      + 3 * wheel_power_tail(4 * sigma, effective, bits))
    extracted = zeta ** 2 * residual
    upper = (extracted * Interval(0, tail_log_upper, bits=bits).exp()).upper
    b = Interval(max(direct.lower, extracted.lower), upper, bits=bits)
    return b, direct, residual, zeta, tail_log_upper, effective, len(primes)


def majorant_bounds(sigma=Q(3, 4), prime_cutoff=1000, bits=80, zeta_cutoff=64):
    """Return a certified enclosure of B_sigma=sum |h(n)|/n**sigma.

    ``sigma`` is an exact Fraction, so binary float input is rejected.
    The default 64-term convexity enclosure of zeta is already substantially
    narrower than ordinary unextracted prime-tail estimates.  Increase
    ``zeta_cutoff`` when a narrower absolute-coefficient norm is needed.
    All public endpoints and error bounds are Fractions; Interval-valued
    fields preserve the interval arithmetic evidence for callers.
    """
    sigma = _sigma(sigma)
    prime_cutoff = _cutoff(prime_cutoff)
    bits = _precision(bits)
    if 2 * sigma - 1 <= Q(1, 1 << bits):
        raise ValueError("sigma is too close to 1/2 for the requested bits")
    zeta_cutoff = _integer(zeta_cutoff, "zeta_cutoff", 1)
    if zeta_cutoff > MAX_ZETA_CUTOFF:
        raise ValueError(f"zeta_cutoff exceeds {MAX_ZETA_CUTOFF}")
    b, direct, residual, zeta, tail, effective, count = _majorant_values(
        sigma, prime_cutoff, bits, zeta_cutoff)
    return {"sigma": sigma, "prime_cutoff": prime_cutoff,
            "effective_prime_cutoff": effective, "prime_count": count,
            "bits": bits, "zeta_cutoff": zeta_cutoff,
            "lower": b.lower, "upper": b.upper, "B": b,
            "partial_product": direct, "residual_partial_product": residual,
            "zeta_2sigma": zeta, "tail_log_upper": tail,
            "tail_method": "zeta(2sigma)^2 extraction; reduced residue classes modulo 210",
            "identity": "B_sigma=zeta(2sigma)^2*prod_p(1+4*p^(-3sigma)+3*p^(-4sigma))"}
