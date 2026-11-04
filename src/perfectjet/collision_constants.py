"""Certified rational enclosures for the conductor-two collision Euler product.

The intervals use finite prime products and elementary integer-series tail
bounds.  They require no floating-point arithmetic or analytic continuation.
See docs/COLLISION_ASYMPTOTICS.md for the derivation and the summatory theorem.
"""
from fractions import Fraction
from math import isqrt


MAX_PRIME_CUTOFF = 10_000
MAX_INTEGER_S = 32
MAX_S_TIMES_CUTOFF = 32_000
RECEIPT_BITS = 128


def _integer(value, name, minimum):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer at least {minimum}")
    return value


def _cutoff(value):
    value = _integer(value, "prime_cutoff", 2)
    if value > MAX_PRIME_CUTOFF:
        raise ValueError(f"prime_cutoff exceeds the exact-product budget {MAX_PRIME_CUTOFF}")
    return value


def primes_up_to(prime_cutoff):
    """Return every prime at most the inclusive integer cutoff."""
    prime_cutoff = _cutoff(prime_cutoff)
    sieve = bytearray(b"\x01") * (prime_cutoff + 1)
    sieve[:2] = b"\x00\x00"
    for p in range(2, isqrt(prime_cutoff) + 1):
        if sieve[p]:
            start = p * p
            sieve[start::p] = b"\x00" * ((prime_cutoff - start) // p + 1)
    return tuple(p for p in range(2, prime_cutoff + 1) if sieve[p])


def constant_bounds(prime_cutoff=100):
    """Enclose C=prod_p (1-2/(p+1)^2), using exact Fractions.

    For integer P>=2, the omitted product lies between 1-2/(P+1)
    and one.  The lower endpoint is positive at every allowed cutoff.
    """
    prime_cutoff = _cutoff(prime_cutoff)
    primes = primes_up_to(prime_cutoff)
    partial = Fraction(1)
    for p in primes:
        partial *= 1 - Fraction(2, (p + 1) ** 2)
    loss = Fraction(2, prime_cutoff + 1)
    return {"prime_cutoff": prime_cutoff, "prime_count": len(primes),
            "lower": partial * (1 - loss), "upper": partial,
            "partial_product": partial, "tail_loss_bound": loss}


def _zeta_arguments(s, prime_cutoff):
    s = _integer(s, "s", 2)
    prime_cutoff = _cutoff(prime_cutoff)
    if s > MAX_INTEGER_S or s * prime_cutoff > MAX_S_TIMES_CUTOFF:
        raise ValueError("s or s*prime_cutoff exceeds the exact-power budget "
                         f"(s<={MAX_INTEGER_S}, product<={MAX_S_TIMES_CUTOFF})")
    return s, prime_cutoff


def conductor_two_zeta_bounds(s=2, prime_cutoff=100):
    """Enclose sum A(n)/n^s for integer s>=2 and integer cutoff P>=2.

    A(p^e)=1 for even e and e+1 for odd e.  Finite products are
    lower bounds because every local factor exceeds one.  For the upper
    bound, L_2(x)<=(1-x)^(-2), and the omitted sum of p^(-s) is
    at most T=1/((s-1)*P^(s-1))<1.  The omitted product is at most
    (1-T)^(-2).
    """
    s, prime_cutoff = _zeta_arguments(s, prime_cutoff)
    primes = primes_up_to(prime_cutoff)
    partial = Fraction(1)
    for p in primes:
        x = Fraction(1, p ** s)
        partial *= (1 + 2 * x - x * x) / (1 - x * x) ** 2
    tail_sum = Fraction(1, (s - 1) * prime_cutoff ** (s - 1))
    return {"s": s, "prime_cutoff": prime_cutoff, "prime_count": len(primes),
            "lower": partial, "upper": partial / (1 - tail_sum) ** 2,
            "partial_product": partial, "tail_sum_bound": tail_sum}


def _dyadic(value, upper=False):
    denominator = 1 << RECEIPT_BITS
    numerator, remainder = divmod(value.numerator * denominator, value.denominator)
    if upper and remainder:
        numerator += 1
    return Fraction(numerator, denominator)


def _record(interval):
    # Bound the JSON representation independently of Python integer-string limits.
    result = {key: str(value) if isinstance(value, Fraction) else value
              for key, value in interval.items()
              if key not in ("lower", "upper", "partial_product")}
    result["lower"] = str(_dyadic(interval["lower"]))
    result["upper"] = str(_dyadic(interval["upper"], upper=True))
    result["partial_product_enclosure"] = {
        "lower": str(_dyadic(interval["partial_product"])),
        "upper": str(_dyadic(interval["partial_product"], upper=True)),
    }
    result["endpoint_rounding"] = f"outward to multiples of 2^-{RECEIPT_BITS}"
    return result


def constants_receipt(prime_cutoff=100, s=2):
    """Return a JSON-safe certificate with outward-rounded rational endpoints."""
    s, prime_cutoff = _zeta_arguments(s, prime_cutoff)
    return {"schema": "conductor-two-collision-constants-v1",
            "arithmetic": "exact rational products and tails; outward-rounded dyadic receipt endpoints",
            "leading_summatory_constant": _record(constant_bounds(prime_cutoff)),
            "dirichlet_value": _record(conductor_two_zeta_bounds(s, prime_cutoff)),
            "limits": ("Dirichlet intervals apply to the conductor-two product at integer s>=2. "
                       "This constants receipt is not a finite-X error certificate; "
                       "use collision-research approximate for certified cumulative counts. "
                       "No claim of literature priority or physical predictive performance.")}
