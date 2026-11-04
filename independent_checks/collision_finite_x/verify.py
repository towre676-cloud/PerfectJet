"""Independent finite integer oracles; no production counting oracle is used.

The pre-existing least-prime coefficient implementation, original signed
factor pairs, and a direct divisor loop check the new summatory certificates.
These finite checks supplement the written all-X proof.
"""
from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def main():
    from perfectjet.collision_asymptotic import counting_certificate
    from perfectjet.collision_intervals import Interval, euler_gamma_bounds
    from perfectjet.collision_constant_extraction import extracted_asymptotic_constants
    from perfectjet.collision_intervals import asymptotic_constants
    from perfectjet.collision_zeta_intervals import zeta_two_constants
    from perfectjet.collision_zeta import conductor_two_values

    def valuation_pair_sign(left, right):
        residue, prime = 0, 2
        while prime * prime <= max(left, right):
            a = b = 0
            while left % prime == 0:
                left //= prime
                a += 1
            while right % prime == 0:
                right //= prime
                b += 1
            residue += a * b
            prime += 1
        if left == right and left > 1:
            residue += 1
        return -1 if residue % 2 else 1

    values = conductor_two_values(1_000_000)
    direct_coefficients = 0
    for n in range(1, 129):
        direct = sum(valuation_pair_sign(d, n // d) for d in range(1, n + 1) if n % d == 0)
        if direct != values[n]:
            raise ArithmeticError(f"signed factor-pair coefficient failed: {n}")
        direct_coefficients += 1
    points = sorted(set([1, 2, 3, 4, 16, 100, 1000, 10000, 100000, 1000000] +
                        [1 + (i * 7919) % 100000 for i in range(200)]))
    prefix, total = {}, 0
    wanted = set(points)
    for n, value in enumerate(values):
        total += value
        if n in wanted:
            prefix[n] = total
    # Some certificates are fractional, while their reference count is a
    # cumulative integer sum through floor(X).
    certificate_points = [Fraction(n) for n in points] + [Fraction(3, 2), Fraction(200001, 2)]
    enclosed = 0
    for X in certificate_points:
        count = prefix.get(X.numerator // X.denominator)
        if count is None:
            count = sum(values[:X.numerator // X.denominator + 1])
        row = counting_certificate(X, prime_cutoff=100)
        interval = row["count_enclosure"]
        if not interval["lower"] <= count <= interval["upper"]:
            raise ArithmeticError(f"independent exact count outside enclosure: {X}")
        enclosed += 1
    # An independent integral-test enclosure of the defining series checks
    # the signs and scale of the new Euler--Maclaurin zeta calculations.
    # It does not reuse the production Euler--Maclaurin formulas.
    summation_limit = 1000
    zeta_partial = sum((Fraction(1, n*n) for n in range(1, summation_limit + 1)), Fraction(0))
    log_partial = Interval(0)
    for n in range(1, summation_limit + 1):
        log_partial += Interval(n).log() / (n*n)
    direct_zeta = Interval(zeta_partial + Fraction(1, summation_limit + 1),
                           zeta_partial + Fraction(1, summation_limit))
    upper_log_tail = (Interval(summation_limit).log() + 1) / summation_limit
    lower_log_tail = (Interval(summation_limit + 1).log() + 1) / (summation_limit + 1)
    direct_derivative = Interval(-log_partial.upper - upper_log_tail.upper,
                                 -log_partial.lower - lower_log_tail.lower)
    zeta = zeta_two_constants()
    for independent, production in ((direct_zeta, zeta["zeta2"]),
                                    (direct_derivative, zeta["zeta2_derivative"])):
        if not independent.lower <= production.lower <= production.upper <= independent.upper:
            raise ArithmeticError("new zeta enclosure lies outside the independent defining-series bounds")
    # Direct and extracted expressions are separately certified.  Their
    # intersections must exist at every cutoff checked here.
    extraction_comparisons = 0
    for cutoff in (2, 7, 100, 1000, 10000):
        direct = asymptotic_constants(cutoff)
        extracted = extracted_asymptotic_constants(cutoff)
        for name in ("C", "D", "K"):
            if max(direct[name].lower, extracted[name].lower) > min(direct[name].upper, extracted[name].upper):
                raise ArithmeticError(f"direct/extracted constant intervals disagree: {cutoff}, {name}")
            extraction_comparisons += 1
    # Direct divisor summation supplies a separate finite check of the 6/5
    # hyperbola bound, including rational y on both sides of jumps.
    gamma = euler_gamma_bounds()
    divisor_points = [Fraction(n) for n in range(1, 501)] + [Fraction(2*n+1, 2) for n in range(1, 501)]
    for y in divisor_points:
        integer = y.numerator // y.denominator
        direct = sum(integer // d for d in range(1, integer + 1))
        value = Interval(y)
        difference = direct - (value * value.log() + (2*gamma - 1) * value)
        radius = Fraction(6, 5) * value.pow(Fraction(1, 2)).lower
        if max(abs(difference.lower), abs(difference.upper)) > radius:
            raise ArithmeticError(f"divisor remainder check failed at {y}")
    print(json.dumps({"status": "passed", "signed_coefficients": direct_coefficients,
                      "independently_enclosed_counts": enclosed,
                      "original_coefficient_oracle_through": 1_000_000,
                      "direct_divisor_remainder_checks": len(divisor_points),
                      "independent_defining_series_zeta_checks": 2,
                      "direct_extracted_constant_intersections": extraction_comparisons,
                      "scope": "Finite independent checks; the all-X justification is the written proof."}))


if __name__ == "__main__":
    main()
