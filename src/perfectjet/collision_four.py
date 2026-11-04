"""Exact conductor-four transport to coprime factors and a fourth power.

For each prime independently, 4 divides a*b iff the source exponent pair is
in the domain.  The target is (u,v,w) with u*v=0 and a+b=u+v+4*w.  These are
exponents, not the underlying integers; no factorization is performed here.
"""
from __future__ import annotations

from collections.abc import Sequence


DEFAULT_MAX_PRIMES = 4096


def _natural(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(name + " must be a nonnegative integer")
    return value


def collision_four_forward(a, b):
    """Return target exponents (u,v,w) for one allowed original pair (a,b).

    With both a,b even, remove their minimum into twice w.  Otherwise the
    odd exponent is retained and the other, divisible by four, becomes w.
    """
    a, b = _natural(a, "a"), _natural(b, "b")
    if a % 2 == 0 and b % 2 == 0:
        common = min(a, b)
        return a - common, b - common, common // 2
    if a % 2 and b % 4 == 0:
        return a, 0, b // 4
    if b % 2 and a % 4 == 0:
        return 0, b, a // 4
    raise ValueError("source exponents must satisfy 4 divides a*b")


def collision_four_inverse(u, v, w):
    """Recover (a,b), requiring coprime-factor exponents u*v=0 exactly."""
    u, v, w = (_natural(value, name)
               for value, name in ((u, "u"), (v, "v"), (w, "w")))
    if u and v:
        raise ValueError("target exponents must satisfy u*v=0")
    if (u + v) % 2 == 0:
        return u + 2 * w, v + 2 * w
    return (u, 4 * w) if u else (4 * w, v)


def _vectors(values, names, max_primes):
    max_primes = _natural(max_primes, "max_primes")
    if max_primes < 1:
        raise ValueError("max_primes must be positive")
    for value in values:
        if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
            raise ValueError("exponent vectors must be finite sequences")
    try:
        widths = [len(value) for value in values]
    except OverflowError as exc:
        raise ValueError("exponent-vector length exceeds the supported sequence range") from exc
    if len(set(widths)) > 1:
        raise ValueError("aligned exponent vectors must have equal lengths")
    if widths[0] > max_primes:
        raise ValueError("exponent-vector budget exceeded before transport")
    return tuple(tuple(_natural(value, name) for value in vector)
                 for vector, name in zip(values, names))


def collision_four_forward_vectors(a, b, *, max_primes=DEFAULT_MAX_PRIMES):
    """Transport aligned prime-exponent vectors to immutable (u,v,w) vectors.

    Coordinate i must name the same prime in both inputs.  An empty basis is
    permitted and represents the unit integer.  Prime labels and primality
    are the caller's responsibility; the algebra acts coordinatewise.
    """
    a, b = _vectors((a, b), ("a exponent", "b exponent"), max_primes)
    triples = tuple(collision_four_forward(x, y) for x, y in zip(a, b))
    return tuple(tuple(row[i] for row in triples) for i in range(3))


def collision_four_inverse_vectors(u, v, w, *, max_primes=DEFAULT_MAX_PRIMES):
    """Recover aligned original exponent vectors; require coordinatewise u*v=0."""
    u, v, w = _vectors((u, v, w), ("u exponent", "v exponent", "w exponent"), max_primes)
    pairs = tuple(collision_four_inverse(x, y, z) for x, y, z in zip(u, v, w))
    return tuple(tuple(row[i] for row in pairs) for i in range(2))


def collision_four_size_count(total_exponent):
    """Count admissible source pairs of total exponent e without enumerating e.

    For every c with 0<=4*c<=e, the residual e-4*c has two orientations when
    positive and one when zero.  This works for arbitrarily large integers.
    """
    e = _natural(total_exponent, "total_exponent")
    return 2 * (e // 4) + 1 + int(e % 4 != 0)


def receipt():
    """Small exact replay plus the separately proved all-exponent statement."""
    checked = 0
    for a in range(17):
        for b in range(17):
            if (a * b) % 4:
                continue
            target = collision_four_forward(a, b)
            if collision_four_inverse(*target) != (a, b):
                raise ArithmeticError("conductor-four inverse replay failed")
            if target[0] * target[1] or a + b != target[0] + target[1] + 4 * target[2]:
                raise ArithmeticError("conductor-four size/coprimality replay failed")
            checked += 1
    return {
        "schema": "perfectjet/collision-four-transport/1",
        "arithmetic": "exact nonnegative integer exponents",
        "statement": "prime-local allowed (m,n) biject with gcd(u,v)=1 triples (u,v,w), preserving mn=u*v*w^4",
        "local_domain": "4 divides a*b at each prime separately",
        "coefficient_formula": "A4(N)=sum_{d^4 divides N} 2^omega(N/d^4), omega(1)=0",
        "finite_checks": {"allowed_pairs_in_0_through_16": checked, "roundtrip_and_size": True},
        "proof": "docs/COLLISION_PROJECTION_CLASSIFICATION.md",
        "limits": ["No prime factorization or primality validation is performed.",
                   "Prime-local divisibility differs from divisibility of total collision."],
    }
