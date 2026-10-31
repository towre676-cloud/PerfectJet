"""Independent exact cumulative conductor-two collision counts.

The sieve changes one prime-power contribution at a time.  The second method
uses the sparse powerful-number support of h in A=d*h, and the exact divisor
hyperbola identity.  Neither method evaluates an asymptotic approximation.
"""
from __future__ import annotations

from array import array
from math import isqrt


MAX_SIEVE_X = 10_000_000
MAX_CONVOLUTION_X = 1_000_000_000_000
MAX_POINTS = 1024


def _integer(value, name, maximum):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum:
        raise ValueError(f"{name} must be an integer from 0 through {maximum}")
    return value


def _primes(limit):
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:min(2, limit + 1)] = b"\x00" * min(2, limit + 1)
    for prime in range(2, isqrt(limit) + 1):
        if sieve[prime]:
            square = prime * prime
            sieve[square::prime] = b"\x00" * ((limit - square) // prime + 1)
    return (n for n in range(2, limit + 1) if sieve[n])


def coefficient_sieve(limit):
    """Return A(0)=0, A(1)=1, ... as compact unsigned integer storage.

    For each prime, successively install the contributions 2,1,4,1,6,1,...
    on multiples of p,p^2,p^3,p^4,... .  Even steps remove the previous odd
    contribution, so each division is exact.  This construction is separate
    from the least-prime recurrence in collision_zeta.conductor_two_values.
    """
    limit = _integer(limit, "limit", MAX_SIEVE_X)
    values = array("I", [1]) * (limit + 1)
    values[0] = 0
    for prime in _primes(limit):
        power, exponent = prime, 1
        while power <= limit:
            if exponent % 2:
                factor = exponent + 1
                for n in range(power, limit + 1, power):
                    values[n] *= factor
            else:
                factor = exponent
                for n in range(power, limit + 1, power):
                    values[n] //= factor
            if power > limit // prime:
                break
            power *= prime
            exponent += 1
    return values


def divisor_summatory(limit):
    """Exact sum_{n<=limit} d(n), using integer arithmetic only."""
    limit = _integer(limit, "limit", MAX_CONVOLUTION_X)
    root = isqrt(limit)
    return 2 * sum(limit // k for k in range(1, root + 1)) - root * root


def powerful_coefficients(limit):
    """Yield each (n,h(n)) with n<=limit and h(n)!=0 exactly once.

    A prime in n must have exponent at least two.  Increasing prime indices
    give unique factorization, with h(p^e)=2*(-1)^(e-1)*(e-1).  Preflight
    limits bound the prime sieve before its allocation.
    """
    limit = _integer(limit, "limit", MAX_CONVOLUTION_X)
    if not limit:
        return
    primes = tuple(_primes(isqrt(limit)))

    def visit(start, number, coefficient):
        yield number, coefficient
        ceiling = limit // number
        for index in range(start, len(primes)):
            prime = primes[index]
            power = prime * prime
            if power > ceiling:
                break
            exponent = 2
            while power <= ceiling:
                local = 2 * (exponent - 1) * (-1 if exponent % 2 == 0 else 1)
                yield from visit(index + 1, number * power, coefficient * local)
                if power > ceiling // prime:
                    break
                power *= prime
                exponent += 1

    yield from visit(0, 1, 1)


def exact_count(X, method="convolution"):
    """Return S(X)=sum_{n<=X} A(n) exactly for bounded nonnegative integer X.

    ``convolution`` has a 10^12 input ceiling; ``sieve`` has a 10^7 ceiling.
    These are execution budgets, not mathematical restrictions on S.
    """
    if method == "sieve":
        return sum(coefficient_sieve(X))
    if method != "convolution":
        raise ValueError("method must be 'convolution' or 'sieve'")
    X = _integer(X, "X", MAX_CONVOLUTION_X)
    return sum(coefficient * divisor_summatory(X // n)
               for n, coefficient in powerful_coefficients(X))


def exact_counts(points, method="sieve"):
    """Return an integer-keyed mapping of inputs to exact cumulative counts.

    Sieve mode shares one coefficient table across all requested points.
    At most 1024 points are accepted, checked before coefficient allocation.
    """
    if not isinstance(points, (list, tuple)) or len(points) > MAX_POINTS:
        raise ValueError(f"points must be a list or tuple of at most {MAX_POINTS} inputs")
    if method not in ("sieve", "convolution"):
        raise ValueError("method must be 'convolution' or 'sieve'")
    maximum = MAX_SIEVE_X if method == "sieve" else MAX_CONVOLUTION_X
    ordered = sorted({_integer(point, "X", maximum) for point in points})
    if not ordered:
        return {}
    if method == "convolution":
        return {point: exact_count(point) for point in ordered}
    values = coefficient_sieve(ordered[-1])
    out, cumulative, start = {}, 0, 1
    for point in ordered:
        for n in range(start, point + 1):
            cumulative += values[n]
        out[point] = cumulative
        start = point + 1
    return out
