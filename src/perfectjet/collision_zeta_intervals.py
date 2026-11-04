"""Certified zeta(2) and zeta'(2) for extracted collision constants.

Euler--Maclaurin is applied separately to t**-2 and log(t)*t**-2.
In particular, no derivative of an interval or of an unsigned remainder
bound is taken.  All sums, coefficients and remainder bounds are rational
interval calculations; no third-party special function enters a bound.

For q=2m, the periodic Bernoulli polynomial has supremum at most |B_q|:
its absolutely convergent cosine series is bounded term by term by its
value at zero.  Thus the Euler--Maclaurin remainder for a function f is
at most |B_q|/q! * integral_N^infinity |f**(q)(t)| dt.  The identities

  (t**-2)**(q) = (q+1)! * t**(-q-2),
  (log(t)*t**-2)**(q)
      = (q+1)! * t**(-q-2) * (log(t)-(H_(q+1)-1))

give the explicit absolute bounds

  E = |B_q| * N**(-q-1),
  E_prime = E * (log(N) + H_(q+1)-1 + 1/(q+1)).

The latter uses |log(t)-h| <= log(t)+h for t>=N>=1, then integrates
each nonnegative term exactly.  It remains valid without assuming the
sign of the logarithmic remainder or convergence of a Bernoulli series.
"""
from fractions import Fraction as Q
from functools import lru_cache
from math import comb

from .collision_intervals import Interval, _precision, log_bounds


MAX_SUMMATION_CUTOFF = 4096
MAX_ORDER = 32


def _positive_integer(value, name, maximum):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [1,{maximum}]")
    return value


@lru_cache(maxsize=MAX_ORDER)
def _bernoulli_even(order):
    """B_2 through B_(2*order), from the exact defining recurrence."""
    numbers = [Q(1)]
    for n in range(1, 2 * order + 1):
        numbers.append(-sum((comb(n + 1, k) * numbers[k] for k in range(n)), Q(0)) / (n + 1))
    return tuple(numbers[2::2])


@lru_cache(maxsize=64)
def _values(bits, cutoff, order):
    work_bits = min(256, bits + 16)
    partial = Interval(0, bits=work_bits)
    partial_prime = Interval(0, bits=work_bits)
    for n in range(1, cutoff):
        partial += Q(1, n * n)
        partial_prime -= log_bounds(n, bits=work_bits) / (n * n)
    logarithm = log_bounds(cutoff, bits=work_bits)
    zeta = partial + Q(1, cutoff) + Q(1, 2 * cutoff * cutoff)
    derivative = partial_prime - (logarithm + 1) / cutoff - logarithm / (2 * cutoff * cutoff)
    bernoulli = _bernoulli_even(order)
    harmonic = Q(1)
    harmonic_values = {1: harmonic}
    for n in range(2, 2 * order + 2):
        harmonic += Q(1, n)
        harmonic_values[n] = harmonic
    for k, number in enumerate(bernoulli, 1):
        coefficient = number / cutoff ** (2 * k + 1)
        zeta += coefficient
        derivative += coefficient * (harmonic_values[2 * k] - 1 - logarithm)
    remainder = abs(bernoulli[-1]) / cutoff ** (2 * order + 1)
    # Keep the tiny prefactor exact. Converting it to a fixed-grid interval
    # first would enlarge a sub-grid remainder to one full grid unit.
    derivative_remainder = remainder * (logarithm.upper + harmonic_values[2 * order + 1]
                                        - 1 + Q(1, 2 * order + 1))
    return (Interval(zeta.lower - remainder, zeta.upper + remainder, bits=bits),
            Interval(derivative.lower - derivative_remainder,
                     derivative.upper + derivative_remainder, bits=bits),
            remainder, derivative_remainder, work_bits)


def zeta_two_constants(bits=80, summation_cutoff=None, order=None):
    """Enclose zeta(2) and its derivative by explicit Euler--Maclaurin bounds.

    The default uses 64 summation terms / order 12 through 128-bit output,
    and cutoff 128 / order 24 for higher precision.  Custom budgets remain
    rigorous even when a low cutoff or order makes their intervals wide.
    """
    bits = _precision(bits)
    cutoff = 64 if bits <= 128 else 128
    truncation = 12 if bits <= 128 else 24
    if summation_cutoff is not None:
        cutoff = _positive_integer(summation_cutoff, "summation_cutoff", MAX_SUMMATION_CUTOFF)
    if order is not None:
        truncation = _positive_integer(order, "order", MAX_ORDER)
    zeta, derivative, remainder, derivative_remainder, work_bits = _values(bits, cutoff, truncation)
    return {
        "zeta2": zeta, "zeta2_derivative": derivative,
        "evidence": {
            "summation_cutoff": cutoff, "included_finite_indices": [1, cutoff - 1],
            "order": truncation, "bits": bits, "work_bits": work_bits,
            "zeta_remainder_upper": remainder,
            "derivative_remainder_upper": derivative_remainder,
            "method": "separate Euler-Maclaurin formulas with absolute periodic-Bernoulli integral remainders",
            "derivative_rule": "B_(2k)*N^(-2k-1)*(H_(2k)-1-log(N))",
        },
    }
