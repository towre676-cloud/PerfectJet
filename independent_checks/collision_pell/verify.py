#!/usr/bin/env python3
"""Independent standard-library replay of the collision/Pell extension.

The oracles below do not import the package's arithmetic helpers.  Package
imports appear only in run(), where their public answers are compared with
direct divisor enumeration, formal logarithms, and field determinants.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from math import comb, gcd, isqrt, prod
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def factor(n):
    answer, d = [], 2
    while d * d <= n:
        e = 0
        while n % d == 0:
            n //= d
            e += 1
        if e:
            answer.append((d, e))
        d += 1
    if n > 1:
        answer.append((n, 1))
    return answer


def collision(a, b):
    left, right = dict(factor(a)), dict(factor(b))
    return sum(v * right.get(p, 0) for p, v in left.items())


def mobius(n):
    f = factor(n)
    return 0 if any(e > 1 for _, e in f) else (-1) ** len(f)


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def trim(p):
    p = list(p)
    while len(p) > 1 and not p[-1]:
        p.pop()
    return p


def multiply(a, b, cutoff=None):
    n = len(a) + len(b) - 1
    if cutoff is not None:
        n = min(n, cutoff + 1)
    c = [0] * n
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if i + j < n:
                c[i + j] += x * y
    return trim(c)


def divide(a, b):
    a, b = trim(a), trim(b)
    q = [Q(0)] * max(1, len(a) - len(b) + 1)
    while len(a) >= len(b) and any(a):
        shift, c = len(a) - len(b), Q(a[-1], b[-1])
        q[shift] += c
        for i, x in enumerate(b):
            a[i + shift] -= c * x
        a = trim(a)
    return trim(q), a


def evaluate(p, x):
    answer = Q(0)
    for c in reversed(p):
        answer = answer * x + c
    return answer


def phi_polynomial(n):
    # Mobius product, rather than the package's recursive cyclotomic division.
    numerator, denominator = [1], [1]
    for d in divisors(n):
        sign = mobius(n // d)
        p = [-1] + [0] * (d - 1) + [1]
        if sign == 1:
            numerator = multiply(numerator, p)
        elif sign == -1:
            denominator = multiply(denominator, p)
    result, remainder = divide(numerator, denominator)
    assert not any(remainder)
    assert all(x.denominator == 1 for x in result)
    return [int(x) for x in result]


def determinant(a):
    a = [list(map(Q, row)) for row in a]
    answer = Q(1)
    for j in range(len(a)):
        i = next((i for i in range(j, len(a)) if a[i][j]), None)
        if i is None:
            return Q(0)
        if i != j:
            a[i], a[j] = a[j], a[i]
            answer = -answer
        pivot = a[j][j]
        answer *= pivot
        for i in range(j + 1, len(a)):
            c = a[i][j] / pivot
            for k in range(j + 1, len(a)):
                a[i][k] -= c * a[j][k]
    return answer


def independent_norm_value(conductor, x):
    modulus = phi_polynomial(conductor)
    degree = len(modulus) - 1
    raw = [Q(0)] * ((conductor - 1) ** 2 + 1)
    for r in range(conductor):
        for s in range(conductor):
            raw[r * s] += x ** (r + s)
    columns = []
    for j in range(degree):
        _, remainder = divide([0] * j + raw, modulus)
        columns.append(remainder + [0] * (degree - len(remainder)))
    return determinant([[columns[j][i] for j in range(degree)] for i in range(degree)])


def interpolate_integers(values):
    # Newton forward differences: f(x)=sum Delta^k f(0) binom(x,k).
    answer, basis, row = [Q(0)], [Q(1)], list(map(Q, values))
    for k in range(len(values)):
        if len(answer) < len(basis):
            answer += [Q(0)] * (len(basis) - len(answer))
        for j, c in enumerate(basis):
            answer[j] += row[0] * c
        row = [b - a for a, b in zip(row, row[1:])]
        basis = [c / (k + 1) for c in multiply(basis, [-k, 1])]
    return trim(answer)


def formal_log(a, order):
    # Literal formal log(1+v), independent of logarithmic derivative recursion.
    v = [0] + list(a[1:order + 1])
    result, power = [Q(0)] * (order + 1), [1]
    for k in range(1, order + 1):
        power = multiply(power, v, order)
        for j, c in enumerate(power):
            result[j] += Q((-1) ** (k + 1), k) * c
    return result


def binomial_euler_rebuild(exponents, order):
    answer = [1]
    for d, b in enumerate(exponents[1:], 1):
        local = [0] * (order + 1)
        local[0] = 1
        for j in range(1, order // d + 1):
            if b > 0:
                local[j * d] = comb(b + j - 1, j)
            elif j <= -b:
                local[j * d] = (-1) ** j * comb(-b, j)
        answer = multiply(answer, local, order)
    return answer + [0] * (order + 1 - len(answer))


def direct_primes(limit):
    return tuple(n for n in range(2, limit + 1)
                 if all(n % d for d in range(2, isqrt(n) + 1)))


def run():
    from perfectjet.collision_zeta import (
        CONDUCTOR_TWO, RationalEulerFactor, conductor_two_coefficient,
        conductor_two_values, pell_pair, pell_lucas,
    )
    from perfectjet.collision_norm import collision_norm
    from perfectjet.collision_population import ExponentSplitPopulation, FactorPairResiduePopulation
    from perfectjet.collision_constants import constant_bounds, conductor_two_zeta_bounds, primes_up_to, constants_receipt
    from perfectjet.collision_projection import PrimeLocalCollisionProjection
    from perfectjet.collision_four import (
        collision_four_forward, collision_four_inverse, collision_four_forward_vectors,
        collision_four_inverse_vectors, collision_four_size_count,
    )

    counts = Counter()
    def check(condition, name):
        if not condition:
            raise AssertionError(name)
        counts[name.split(":")[0]] += 1

    def rejects(thunk, name):
        try:
            thunk()
        except (ValueError, TypeError, IndexError):
            counts["invalid_inputs"] += 1
        else:
            raise AssertionError("unexpected acceptance: " + name)

    # Entire Dirichlet coefficient, counted from actual ordered divisor pairs.
    values = conductor_two_values(720)
    for n in range(1, 721):
        original = [(d, n // d) for d in divisors(n)]
        signed = sum((-1) ** collision(a, b) for a, b in original)
        check(values[n] == signed, "divisor_coefficients")
        if n <= 180:
            for L in (1, 2, 3, 4, 6, 7):
                histogram = tuple(sum(collision(a, b) % L == r for a, b in original) for r in range(L))
                for residue in range(L):
                    pop = FactorPairResiduePopulation(factor(n), L, residue)
                    check(pop.histogram() == histogram, "factor_pair_histograms")
                    accepted = []
                    for a, b in original:
                        if collision(a, b) % L == residue:
                            accepted.append((tuple(dict(factor(a)).get(p, 0) for p, _ in factor(n)), (a, b)))
                    for rank, (exponents, pair) in enumerate(sorted(accepted)):
                        check(pop.unrank(rank) == exponents and pop.rank(exponents) == rank and pop.pair(rank) == pair,
                              "factor_pair_rank")

    # Unsplit local pairs are distinct from signed phase sums.
    for L in range(1, 13):
        projection = PrimeLocalCollisionProjection(L)
        for exponent in range(31):
            for residue in range(L):
                raw = [(a, exponent - a) for a in range(exponent + 1)
                       if a * (exponent - a) % L == residue]
                pop = ExponentSplitPopulation(L, exponent, residue)
                check(pop.count() == len(raw), "local_populations")
                for rank, pair in enumerate(raw):
                    check(pop.unrank(rank) == pair and pop.rank(pair) == rank, "local_rank")
            check(projection.coefficient(exponent) == sum(a * (exponent - a) % L == 0 for a in range(exponent + 1)),
                  "prime_local_projection")
        check((projection.numerator == projection.numerator[::-1]) == (L in (1, 4)), "projection_obstruction")
    global_pop = FactorPairResiduePopulation({2: 2, 3: 2}, 2, 0)
    check(global_pop.contains((1, 1)) and not PrimeLocalCollisionProjection(2).local_exponent_allowed(1, 1),
          "global_vs_prime_local")

    # Exercise the size-preserving fourth-power maps on original integers.
    for N in range(1, 501):
        basis = factor(N)
        targets = set()
        allowed_count = 0
        for m in divisors(N):
            n = N // m
            a = tuple(dict(factor(m)).get(p, 0) for p, _ in basis)
            b = tuple(dict(factor(n)).get(p, 0) for p, _ in basis)
            if any(x * y % 4 for x, y in zip(a, b)):
                continue
            allowed_count += 1
            u, v, w = collision_four_forward_vectors(a, b)
            U, V, W = (prod(p ** e for (p, _), e in zip(basis, vector)) for vector in (u, v, w))
            check(gcd(U, V) == 1 and U * V * W ** 4 == N, "fourth_power_integer_size")
            check(collision_four_inverse_vectors(u, v, w) == (a, b), "fourth_power_integer_roundtrip")
            targets.add((U, V, W))
        formula = sum(2 ** len(factor(N // d ** 4)) for d in range(1, isqrt(isqrt(N)) + 1) if N % (d ** 4) == 0)
        check(allowed_count == len(targets) == formula, "fourth_power_coefficient_formula")
    for a in range(41):
        for b in range(41):
            if a * b % 4 == 0:
                u, v, w = collision_four_forward(a, b)
                check(collision_four_inverse(u, v, w) == (a, b) and a + b == u + v + 4 * w and u * v == 0,
                      "fourth_power_local_map")
    for e in range(201):
        check(collision_four_size_count(e) == sum(a * (e - a) % 4 == 0 for a in range(e + 1)),
              "fourth_power_total_count")

    # Pell powers by linear integer iteration, then independent modular cycles.
    u, v = 1, 0
    lucas = []
    for n in range(201):
        check(pell_pair(n) == (u, v) and pell_lucas(n) == 2 * u, "pell_integer_recurrence")
        check(u * u - 2 * v * v == (-1) ** n, "pell_norm")
        lucas.append(2 * u)
        u, v = u + 2 * v, u + v
    remote = 10 ** 100 + 347
    for modulus in (2, 3, 5, 7, 12, 35, 97, 101):
        cycle, state = [], (1, 0)
        while not cycle or state != (1, 0):
            cycle.append(state)
            state = ((state[0] + 2 * state[1]) % modulus, (state[0] + state[1]) % modulus)
            assert len(cycle) <= modulus * modulus
        check(pell_pair(remote, modulus) == cycle[remote % len(cycle)], "pell_modular_remote")
    order = 80
    logarithmic = [0] + [(-1) ** (n + 1) * lucas[n] + 4 * (n % 2 == 0) for n in range(1, order + 1)]
    exponents = [0]
    for n in range(1, order + 1):
        numerator = sum(mobius(n // d) * logarithmic[d] for d in divisors(n))
        check(numerator % n == 0, "mobius_integrality")
        exponents.append(numerator // n)
    check(CONDUCTOR_TWO.logarithmic_coefficients(order) == logarithmic, "pell_logarithms")
    check(CONDUCTOR_TWO.zeta_exponents(order) == exponents, "pell_euler_exponents")
    check(binomial_euler_rebuild(exponents, order) == [1 if n % 2 == 0 else n + 1 for n in range(order + 1)],
          "binomial_reconstruction")

    rng = random.Random(20261028)
    for _ in range(30):
        p = (1,) + tuple(rng.randrange(-2, 3) for _ in range(rng.randrange(1, 5)))
        q = (1,) + tuple(rng.randrange(-2, 3) for _ in range(rng.randrange(1, 5)))
        obj = RationalEulerFactor(p, q)
        a = [Q(0)] * 13
        for n in range(13):
            a[n] = (p[n] if n < len(p) else 0) - sum(q[j] * a[n - j] for j in range(1, min(n + 1, len(q))))
        log = formal_log(a, 12)
        c = [n * x for n, x in enumerate(log)]
        b = [0] + [sum(mobius(n // d) * c[d] for d in divisors(n)) / n for n in range(1, 13)]
        check(obj.coefficients(12) == a, "random_rational_series")
        check(obj.logarithmic_coefficients(12) == c and obj.zeta_exponents(12) == b, "literal_formal_logarithm")
    for order in range(7):
        extracted = CONDUCTOR_TWO.extract(order)
        for x in (Q(1, 101), Q(-1, 31), Q(2, 17)):
            residual = evaluate(extracted["residual_numerator"], x) / evaluate(extracted["residual_denominator"], x)
            rebuilt = residual * prod((1 - x ** n) ** (-b) for n, b in enumerate(extracted["zeta_exponents"], 1))
            check(rebuilt == (1 + 2 * x - x * x) / (1 - x * x) ** 2, "finite_extraction_evaluation")

    # Recover EVERY norm coefficient from field determinants at distinct x.
    # Production instead multiplies conjugate polynomials in its quotient ring.
    norm_rows = []
    for L in range(1, 7):
        phi = len(phi_polynomial(L)) - 1
        degree = (2 * L - 2) * phi
        samples = [independent_norm_value(L, Q(x)) for x in range(degree + 1)]
        reconstructed = interpolate_integers(samples)
        actual = collision_norm(L).numerator
        check(reconstructed == list(actual), "norm_complete_interpolation")
        check(evaluate(reconstructed, Q(2, 7)) == independent_norm_value(L, Q(2, 7)), "norm_extra_rational_point")
        if L > 1:
            check(actual[-2] != actual[-1] * actual[1], "norm_reciprocity_obstruction")
        norm_rows.append({"conductor": L, "field_degree": phi, "norm_degree": degree,
                          "integer_determinant_samples": degree + 1})

    for cutoff in (2, 3, 7, 19, 37, 100):
        primes = direct_primes(cutoff)
        check(primes_up_to(cutoff) == primes, "independent_prime_list")
        partial = prod((1 - Q(2, (p + 1) ** 2) for p in primes), start=Q(1))
        interval = constant_bounds(cutoff)
        check(interval["upper"] == partial and interval["lower"] == partial * (1 - Q(2, cutoff + 1)), "constant_interval_formula")
        extended = prod((1 - Q(2, (p + 1) ** 2) for p in direct_primes(cutoff + 100)), start=Q(1))
        check(interval["lower"] < extended <= interval["upper"], "constant_extended_product_containment")
        for s in (2, 3, 5):
            interval = conductor_two_zeta_bounds(s, cutoff)
            finite = prod(((1 + 2 * Q(1, p ** s) - Q(1, p ** (2 * s))) / (1 - Q(1, p ** (2 * s))) ** 2 for p in primes), start=Q(1))
            t = Q(1, (s - 1) * cutoff ** (s - 1))
            check(interval["lower"] == finite and interval["upper"] == finite / (1 - t) ** 2, "zeta_interval_formula")
            receipt = constants_receipt(cutoff, s)
            compact = receipt["dirichlet_value"]
            check(Q(compact["lower"]) <= interval["lower"] <= interval["upper"] <= Q(compact["upper"]),
                  "outward_receipt_endpoints")

    for bad in (True, False, -1, 1.5, None, [], {}, "abc", "-1"):
        rejects(lambda bad=bad: conductor_two_coefficient(bad), "coefficient")
        rejects(lambda bad=bad: pell_pair(bad), "Pell index")
        rejects(lambda bad=bad: collision_norm(bad), "norm conductor")
    for _ in range(40):
        bad_order = rng.choice((-rng.randrange(1, 100), rng.randrange(513, 10000), True, 2.5))
        rejects(lambda bad_order=bad_order: CONDUCTOR_TWO.coefficients(bad_order), "series order")
    for kwargs in ({"max_conductor": 1}, {"max_degree": 1}, {"max_work": 1}):
        rejects(lambda kwargs=kwargs: collision_norm(6, **kwargs), "norm allocation budget")
    rejects(lambda: CONDUCTOR_TWO.extract(80, degree_budget=20), "exponential extraction preflight")
    rejects(lambda: pell_pair(10 ** 100), "unmodulated output budget")
    rejects(lambda: pell_pair(1, modulus=2 ** 100, max_bits=16), "modular output budget")
    rejects(lambda: conductor_two_values(1000001), "sieve budget")
    rejects(lambda: FactorPairResiduePopulation({2: 5, 3: 7}, 9, max_work=1), "convolution budget")
    rejects(lambda: FactorPairResiduePopulation({101: 1}, max_trial_divisions=1), "prime proof budget")
    rejects(lambda: FactorPairResiduePopulation({4: 1}), "composite factor")
    rejects(lambda: FactorPairResiduePopulation({2: 10 ** 100}).pair(0), "original output guard")
    rejects(lambda: PrimeLocalCollisionProjection(12, max_terms=10), "projection setup guard")
    rejects(lambda: primes_up_to(10 ** 100), "prime allocation guard")
    rejects(lambda: constant_bounds(10001), "constant product guard")
    rejects(lambda: conductor_two_zeta_bounds(10 ** 100, 2), "exact power guard")
    rejects(lambda: conductor_two_zeta_bounds(32, 10000), "combined power-product guard")
    rejects(lambda: RationalEulerFactor((1,), (1, -(1 << 32767))).coefficients(512),
            "combined coefficient-growth guard")

    # Cross-component public entry points are exercised after arithmetic oracles.
    from perfectjet.collision_research import evaluate as research_evaluate
    integration_requests = [
        {"operation": "report", "order": 8, "index": str(remote), "limit": 180},
        {"operation": "pell", "index": str(remote), "modulus": 97},
        {"operation": "extract", "order": 4},
        {"operation": "norm", "conductor": 3, "order": 8},
        {"operation": "projection", "conductor": 4, "order": 8},
        {"operation": "population", "conductor": 3, "exponent": "100000000000000000007", "residue": 0},
        {"operation": "population", "conductor": 2, "factorization": [[2, 2], [3, 2]], "rank": 0},
        {"operation": "constants", "prime_cutoff": 19, "s": 2},
        {"operation": "classify", "max_conductor": 6},
    ]
    for request in integration_requests:
        answer = research_evaluate(request)
        check(isinstance(json.loads(json.dumps(answer, allow_nan=False)), dict), "public_json_operations")
    from perfectjet.collision_research import json_value
    string_limit = sys.get_int_max_str_digits() if hasattr(sys, "get_int_max_str_digits") else None
    large = research_evaluate({"operation": "pell", "index": 12000})
    state = (1, 0)
    for _ in range(12000):
        state = ((state[0] + 2 * state[1]) % 97, (state[0] + state[1]) % 97)
    for name, expected in zip(("rational", "sqrt_two"), state):
        digits = large["unit_power"][name]
        check(isinstance(digits, str) and len(digits) > 4300 and digits.isascii() and digits.isdigit(),
              "large_pell_json_digits")
        residue = 0
        for digit in digits:
            residue = (10 * residue + ord(digit) - ord("0")) % 97
        check(residue == expected, "large_pell_decimal_residue")
    check(string_limit == (sys.get_int_max_str_digits() if hasattr(sys, "get_int_max_str_digits") else None),
          "python_string_limit_unchanged")
    rejects(lambda: json_value(1 << 262144), "single JSON integer budget")
    rejects(lambda: json_value([1 << 200000] * 4), "combined JSON integer budget")

    return {
        "status": "passed", "comparison_counts": dict(sorted(counts.items())),
        "total_comparisons": sum(counts.values()), "complete_norm_interpolations": norm_rows,
        "analytic_peer_review": {
            "individual_phase_obstruction": "c0=1,c1=2,cD=zeta,c(D-1)=2*zeta^2 contradicts self-inversiveness for every L>1; equal endpoint moduli force roots on both sides",
            "norm_boundary": "The integer Galois norm has constant one and an off-unit root. Estermann applies; a globally meromorphic cyclotomic denominator cannot remove the boundary.",
            "projection_exception": "For nonsquares the leading coefficient is two. For L=k^2 reciprocity forces the gcd-sum S_L=k^3, whose prime-power factors permit only k=1,2.",
            "scope": "Written mathematical peer review; numerical checks do not prove universal or analytic continuation claims. No individual complex-phase Euler-product classification is inferred.",
        },
        "independence": [
            "Original divisor pairs and separate trial-division valuations, not package residue convolution.",
            "Linear Pell iteration and finite modular cycles, not package binary unit powering.",
            "Literal formal logarithms and direct Mobius inversion, not package logarithmic-derivative/divisor recursion.",
            "Complete norm polynomial interpolation from rational field multiplication determinants, with independent Mobius cyclotomic construction.",
            "Trial-division prime oracle, exact product endpoints and longer-product containment.",
        ],
        "limitations": "Finite tests use bounded conductors and samples. They verify implementation and hypotheses; the all-conductor classification is a separate proof and Estermann is an external classical theorem.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional JSON replay report")
    args = parser.parse_args()
    started = time.monotonic()
    report = run()
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    sources = ["src/perfectjet/collision.py", "src/perfectjet/collision_zeta.py",
               "src/perfectjet/collision_population.py", "src/perfectjet/collision_norm.py",
               "src/perfectjet/collision_projection.py", "src/perfectjet/collision_constants.py",
               "src/perfectjet/collision_four.py",
               "docs/COLLISION_NORM_CLASSIFICATION.md", "docs/COLLISION_PROJECTION_CLASSIFICATION.md",
               "docs/COLLISION_ASYMPTOTICS.md", "src/perfectjet/collision_research.py",
               "independent_checks/collision_pell/verify.py"]
    report["source_sha256"] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources}
    report["schema"] = "perfectjet/independent-collision-pell-replay/1"
    data = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
    print(data, end="")


if __name__ == "__main__":
    main()
