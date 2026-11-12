"""Scout reusable exact certificate patterns in monogenic cubic fields.

The principal pattern is deliberately narrow and proof-carrying:

* f is a monic irreducible cubic in Z[x];
* some integral translate f(x+s) is Eisenstein at a prime p;
* after removing the p-power from |disc(f)|, the remaining integer is squarefree.

Eisenstein local maximality excludes p from the index [O_K:Z[alpha]].  For any
other prime ell, ell dividing the index would force ell^2 to divide the power
basis discriminant.  Squarefreeness of the residual discriminant excludes this.
Hence the power order is maximal.

The module also searches for small prime norms N(alpha-k)=-f(k), which are
useful principal-prime witnesses in later class-group or descent arguments.
"""
from __future__ import annotations

from math import comb, isqrt

from .quotient_algebra import MonogenicQuotient


def _ints(coefficients):
    if (not isinstance(coefficients, (list, tuple)) or len(coefficients) != 4
            or any(type(x) is not int for x in coefficients)):
        raise ValueError("monic cubic coefficients must be four exact integers, low-to-high")
    if coefficients[-1] != 1:
        raise ValueError("cubic must be monic")
    return tuple(coefficients)


def is_prime(n):
    return type(n) is int and n >= 2 and all(n % d for d in range(2, isqrt(n)+1))


def divisors(n):
    n = abs(n)
    if n == 0:
        return (0,)
    out = set()
    for d in range(1, isqrt(n)+1):
        if n % d == 0:
            out.update((d, -d, n//d, -(n//d)))
    return tuple(sorted(out))


def evaluate(coefficients, x):
    coefficients = _ints(coefficients)
    value = 0
    for c in reversed(coefficients):
        value = value*x + c
    return value


def irreducible_cubic(coefficients):
    """For a monic cubic over Z, absence of an integer root is irreducibility over Q."""
    coefficients = _ints(coefficients)
    return not any(evaluate(coefficients, r) == 0 for r in divisors(coefficients[0]))


def translate(coefficients, shift):
    coefficients = _ints(coefficients)
    if type(shift) is not int:
        raise ValueError("shift must be an integer")
    out = [0]*4
    for i, c in enumerate(coefficients):
        for j in range(i+1):
            out[j] += c*comb(i, j)*shift**(i-j)
    return tuple(out)


def eisenstein(coefficients, prime):
    coefficients = _ints(coefficients)
    if not is_prime(prime):
        raise ValueError("prime must be prime")
    return (all(c % prime == 0 for c in coefficients[:-1])
            and coefficients[0] % (prime*prime) != 0)


def valuation(n, prime):
    if not is_prime(prime):
        raise ValueError("prime must be prime")
    n = abs(n)
    count = 0
    while n and n % prime == 0:
        n //= prime
        count += 1
    return count


def squarefree(n):
    n = abs(n)
    if n == 0:
        return False
    p = 2
    while p*p <= n:
        if n % (p*p) == 0:
            return False
        p += 1
    return True


def small_prime_norm_witnesses(coefficients, search_radius=8, limit=8):
    coefficients = _ints(coefficients)
    if type(search_radius) is not int or search_radius < 0:
        raise ValueError("search_radius must be a nonnegative integer")
    rows = []
    K = MonogenicQuotient(coefficients)
    for k in range(-search_radius, search_radius+1):
        # For a cubic, N(alpha-k) = -f(k).
        expected = -evaluate(coefficients, k)
        actual = K.norm([-k, 1])
        if actual != expected:
            raise ArithmeticError("quotient norm disagrees with polynomial evaluation")
        if abs(expected) > 1 and is_prime(abs(expected)):
            rows.append({"k": k, "element": [str(-k), "1", "0"],
                         "norm": str(expected), "prime_norm": abs(expected)})
    rows.sort(key=lambda row: (row["prime_norm"], abs(row["k"]), row["k"]))
    return rows[:limit]


def maximal_power_order_pattern(coefficients, prime=2, shift_radius=4):
    coefficients = _ints(coefficients)
    if not irreducible_cubic(coefficients):
        return {"status": "rejected", "reason": "reducible cubic"}
    K = MonogenicQuotient(coefficients)
    disc = K.discriminant()
    if disc.denominator != 1:
        raise ArithmeticError("integral monic cubic produced nonintegral discriminant")
    disc = int(disc)
    shifts = [s for s in range(-shift_radius, shift_radius+1)
              if eisenstein(translate(coefficients, s), prime)]
    if not shifts:
        return {"status": "rejected", "reason": "no Eisenstein translate in search radius",
                "discriminant": disc}
    vp = valuation(disc, prime)
    residual = abs(disc) // (prime**vp)
    if not squarefree(residual):
        return {"status": "rejected", "reason": "residual discriminant is not squarefree",
                "discriminant": disc, "eisenstein_shifts": shifts,
                "residual_discriminant": residual}
    return {
        "schema": "perfectjet/cubic-maximal-power-order-pattern/1",
        "status": "certified_pattern",
        "coefficients_low_to_high": list(coefficients),
        "discriminant": disc,
        "prime": prime,
        "discriminant_valuation_at_prime": vp,
        "residual_discriminant": residual,
        "residual_squarefree": True,
        "eisenstein_shifts": shifts,
        "sample_shifted_polynomial": list(translate(coefficients, shifts[0])),
        "irreducible": True,
        "maximal_power_order": True,
        "small_prime_norm_witnesses": small_prime_norm_witnesses(coefficients),
        "proof": (
            "The translate generates the same order and is Eisenstein at the "
            "declared prime, excluding that prime from the order index. Any other "
            "prime dividing the index would have its square divide the power-basis "
            "discriminant; the residual discriminant is squarefree."
        ),
        "scope": (
            "A certificate for maximality of the monogenic power order, conditional "
            "only on the standard discriminant-index relation and Eisenstein local "
            "maximality. It is not a class-number, unit-group or Selmer certificate."
        ),
    }


def scout_cubics(a_bound=6, b_bound=12, c_bound=6, prime=2,
                 positive_discriminant=True, max_results=20):
    """Search small monic cubics and keep one low-height representative per discriminant."""
    for value, name in ((a_bound, "a_bound"), (b_bound, "b_bound"), (c_bound, "c_bound"),
                        (max_results, "max_results")):
        if type(value) is not int or value < 1:
            raise ValueError(name+" must be a positive integer")
    best = {}
    for a in range(-a_bound, a_bound+1):
        for b in range(-b_bound, b_bound+1):
            for c in range(-c_bound, c_bound+1):
                coefficients = (c, b, a, 1)
                report = maximal_power_order_pattern(coefficients, prime=prime)
                if report.get("status") != "certified_pattern":
                    continue
                disc = report["discriminant"]
                if positive_discriminant and disc <= 0:
                    continue
                score = (abs(a)+abs(b)+abs(c), abs(a), abs(b), abs(c), a, b, c)
                if disc not in best or score < best[disc][0]:
                    best[disc] = (score, report)
    rows = [best[d][1] for d in sorted(best)]
    return {
        "schema": "perfectjet/cubic-certificate-scout/1",
        "bounds": {"a": a_bound, "b": b_bound, "c": c_bound},
        "prime": prime,
        "positive_discriminant_only": positive_discriminant,
        "distinct_discriminants_found": len(rows),
        "results": rows[:max_results],
        "scope": "Deterministic bounded coefficient search; not a census of cubic fields up to isomorphism.",
    }
