"""Outward rational intervals for finite conductor-two counting certificates.

No binary floating point or third-party numerical library enters a bound.
Logarithms use the positive atanh series after binary range reduction;
exponentials use Taylor's series with a geometric bound on its tail.  Every
public arithmetic operation rounds outwards to a dyadic grid.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from math import gcd

from .collision_constants import _cutoff, primes_up_to


MIN_BITS = 32
MAX_BITS = 256
MAX_ARGUMENT_BITS = 16384


def _precision(bits):
    if isinstance(bits, bool) or not isinstance(bits, int) or not MIN_BITS <= bits <= MAX_BITS:
        raise ValueError(f"bits must be an integer in [{MIN_BITS}, {MAX_BITS}]")
    return bits


def _rational(value):
    if isinstance(value, bool) or not isinstance(value, (int, Q)):
        raise ValueError("interval arguments must be integers or Fractions")
    value = Q(value)
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_ARGUMENT_BITS:
        raise ValueError("rational argument exceeds the interval bit budget")
    return value


def _down(value, bits):
    return Q((value.numerator << bits) // value.denominator, 1 << bits)


def _up(value, bits):
    return -_down(-value, bits)


@dataclass(frozen=True, init=False)
class Interval:
    """Closed rational interval, rounded outwards to multiples of ``2**-bits``."""
    lower: Q
    upper: Q
    bits: int

    def __init__(self, lower, upper=None, bits=80):
        bits = _precision(bits)
        lower = _rational(lower)
        upper = lower if upper is None else _rational(upper)
        if lower > upper:
            raise ValueError("interval lower endpoint exceeds upper endpoint")
        object.__setattr__(self, "lower", _down(lower, bits))
        object.__setattr__(self, "upper", _up(upper, bits))
        object.__setattr__(self, "bits", bits)

    def _other(self, value):
        return value if isinstance(value, Interval) else Interval(value, bits=self.bits)

    def __add__(self, value):
        other = self._other(value)
        return Interval(self.lower + other.lower, self.upper + other.upper,
                        bits=min(self.bits, other.bits))

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.upper, -self.lower, bits=self.bits)

    def __sub__(self, value):
        return self + (-self._other(value))

    def __rsub__(self, value):
        return self._other(value) - self

    def __mul__(self, value):
        other = self._other(value)
        values = (self.lower * other.lower, self.lower * other.upper,
                  self.upper * other.lower, self.upper * other.upper)
        return Interval(min(values), max(values), bits=min(self.bits, other.bits))

    __rmul__ = __mul__

    def reciprocal(self):
        if self.lower <= 0 <= self.upper:
            raise ValueError("cannot divide by an interval containing zero")
        return Interval(1 / self.upper, 1 / self.lower, bits=self.bits)

    def __truediv__(self, value):
        return self * self._other(value).reciprocal()

    def __rtruediv__(self, value):
        return self._other(value) / self

    def __pow__(self, exponent):
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            raise ValueError("use .pow(Fraction) for noninteger powers")
        if abs(exponent) > 16384:
            raise ValueError("integer power exceeds interval work budget")
        if exponent < 0:
            return (self ** -exponent).reciprocal()
        if exponent == 0:
            return Interval(1, bits=self.bits)
        endpoint_bits = max(abs(self.lower.numerator).bit_length(), self.lower.denominator.bit_length(),
                            abs(self.upper.numerator).bit_length(), self.upper.denominator.bit_length())
        if endpoint_bits * exponent > MAX_ARGUMENT_BITS:
            raise ValueError("integer power exceeds the rational endpoint bit budget")
        # Endpoint monotonicity gives a tighter enclosure than repeated interval
        # multiplication when a square crosses zero.
        if exponent % 2:
            return Interval(self.lower ** exponent, self.upper ** exponent, bits=self.bits)
        values = (self.lower ** exponent, self.upper ** exponent)
        return Interval(0 if self.lower <= 0 <= self.upper else min(values),
                        max(values), bits=self.bits)

    def log(self):
        return log_bounds(self, bits=self.bits)

    def exp(self):
        return exp_bounds(self, bits=self.bits)

    def pow(self, exponent):
        return power_bounds(self, exponent, bits=self.bits)

    def record(self):
        return {"lower": str(self.lower), "upper": str(self.upper),
                "endpoint_rounding": f"outward to multiples of 2^-{self.bits}"}

    @property
    def midpoint(self):
        return (self.lower + self.upper) / 2

    @property
    def width(self):
        return self.upper - self.lower


def _as_interval(value, bits):
    _precision(bits)
    return Interval(value.lower, value.upper, bits=min(bits, value.bits)) if isinstance(value, Interval) else Interval(value, bits=bits)


@lru_cache(maxsize=8192)
def _log_point(value, bits):
    if value <= 0:
        raise ValueError("logarithm requires a strictly positive argument")
    # Choose k so u=value/2**k lies in [1,2).
    k = value.numerator.bit_length() - value.denominator.bit_length()
    scale = Q(2 ** k) if k >= 0 else Q(1, 2 ** -k)
    u = value / scale
    if u < 1:
        k -= 1
        u *= 2
    elif u >= 2:
        k += 1
        u /= 2
    if u == 1:
        base = Interval(0, bits=bits)
    else:
        base = _atanh_log(u, bits)
    return base + k * _log_two(bits) if k else base


def _atanh_log(u, bits):
    """log(u)=2 sum z**(2j+1)/(2j+1), 0<=z<=1/3."""
    z = (u - 1) / (u + 1)
    z2 = z * z
    term = z
    total = Q(0)
    j = 0
    tolerance = Q(1, 1 << (bits + 8))
    while True:
        total += term / (2 * j + 1)
        term *= z2
        remainder = 2 * term / ((2 * j + 3) * (1 - z2))
        if remainder <= tolerance:
            return Interval(2 * total, 2 * total + remainder, bits=bits)
        j += 1


@lru_cache(maxsize=16)
def _log_two(bits):
    return _atanh_log(Q(2), bits)


def log_bounds(value, bits=80):
    """Enclose log(value), including input uncertainty, by a rational series."""
    value = _as_interval(value, bits)
    if value.lower <= 0:
        raise ValueError("logarithm requires a strictly positive interval")
    lo = _log_point(value.lower, value.bits)
    hi = _log_point(value.upper, value.bits)
    return Interval(lo.lower, hi.upper, bits=value.bits)


def _exp_point(value, bits):
    if abs(value) > 4096:
        raise ValueError("exponential argument exceeds the certified work budget")
    if value < 0:
        return _exp_point(-value, bits).reciprocal()
    if value == 0:
        return Interval(1, bits=bits)
    # 0<t<=1/2.  Subsequent exact squarings propagate the certified enclosure.
    scale = max(0, value.numerator.bit_length() - value.denominator.bit_length() + 2)
    t = value / (1 << scale)
    total = term = Q(1)
    j = 0
    tolerance = Q(1, 1 << (bits + 12 + scale))
    while True:
        j += 1
        term = term * t / j
        total += term
        first = term * t / (j + 1)
        remainder = first / (1 - t / (j + 2))
        if remainder <= tolerance:
            result = Interval(total, total + remainder, bits=bits)
            for _ in range(scale):
                result = result * result
            return result


def exp_bounds(value, bits=80):
    """Enclose exp(value) using Taylor's positive series and its tail bound."""
    value = _as_interval(value, bits)
    lo = _exp_point(value.lower, value.bits)
    hi = _exp_point(value.upper, value.bits)
    return Interval(lo.lower, hi.upper, bits=value.bits)


def power_bounds(value, exponent, bits=80):
    """Enclose a positive rational/interval raised to a rational exponent."""
    exponent = _rational(exponent)
    if abs(exponent) > 16384:
        raise ValueError("rational power exceeds the interval work budget")
    value = _as_interval(value, bits)
    if value.lower <= 0:
        raise ValueError("rational power requires a strictly positive interval")
    if exponent.denominator == 1:
        return value ** exponent.numerator
    return (value.log() * exponent).exp()


# B_(2k), k=1,...,10.  For positive n the Euler--Maclaurin expansion
# gamma=H_n-log(n)-1/(2n)+sum B_(2k)/(2k*n**(2k)) has a remainder
# with the sign of the first omitted term and magnitude below that term.
# Explicit justification: the Binet/Euler--Maclaurin remainder identity is
# gamma = H_n-log(n)-1/(2n)
#       + 2*integral_0^infinity t/((n*n+t*t)*(exp(2*pi*t)-1)) dt.
# Insert the FINITE geometric identity for 1/(n*n+t*t).  Its first m
# integrated terms equal the Bernoulli terms below.  The remaining integrand
# has sign (-1)^m, and replacing n*n/(n*n+t*t) by 1 bounds its absolute
# integral by the next Bernoulli term.  This proves signed truncation bounds;
# it does not treat the Bernoulli asymptotic expansion as a convergent series.
_BERNOULLI_EVEN = (Q(1, 6), Q(-1, 30), Q(1, 42), Q(-1, 30), Q(5, 66),
                   Q(-691, 2730), Q(7, 6), Q(-3617, 510), Q(43867, 798),
                   Q(-174611, 330))


@lru_cache(maxsize=16)
def euler_gamma_bounds(bits=80):
    """Euler's constant from adjacent Euler--Maclaurin truncations.

    Ten Bernoulli terms suffice even at 256 bits by choosing n=2**ceil(bits/18).
    The first nine and ten truncations bracket gamma (upper, lower).
    """
    bits = _precision(bits)
    n = 1 << max(5, (bits + 17) // 18)
    # Sum each reciprocal on a finer dyadic grid.  This avoids the lcm(1,...,n)
    # denominator without using any floating point or losing tail information.
    scale = 1 << (bits + 16)
    harmonic_lo = Q(sum(scale // k for k in range(1, n + 1)), scale)
    harmonic_hi = Q(sum((scale + k - 1) // k for k in range(1, n + 1)), scale)
    harmonic = Interval(harmonic_lo, harmonic_hi, bits=bits)
    base = harmonic - Q(1, 2 * n) - log_bounds(n, bits=bits)
    correction = Q(0)
    for k, bernoulli in enumerate(_BERNOULLI_EVEN[:9], 1):
        correction += bernoulli / (2 * k * n ** (2 * k))
    upper = base + correction
    lower = upper + _BERNOULLI_EVEN[9] / (20 * n ** 20)
    return Interval(lower.lower, upper.upper, bits=bits)


def asymptotic_constants(prime_cutoff=1000, bits=80):
    """Certified C, D=H'(1)/H(1), gamma, K=C*(2*gamma-1+D).

    The omitted prime losses obey sum 2/(p+1)^2 <=2/(P+1).
    The derivative tail is bounded by 4*(log(P)+1)/P.  When P>=7, reduced
    residue classes modulo 210 improve both tails.  Neither bound uses an
    unproved prime-density estimate.
    """
    prime_cutoff = _cutoff(prime_cutoff)
    bits = _precision(bits)
    primes = primes_up_to(prime_cutoff)
    partial_c = Interval(1, bits=bits)
    partial_d = Interval(0, bits=bits)
    for p in primes:
        partial_c *= Q(p * p + 2 * p - 1, (p + 1) ** 2)
        weight = Q(4 * p, (p + 1) * (p * p + 2 * p - 1))
        partial_d += weight * log_bounds(p, bits=bits)
    integer_loss = Q(2, prime_cutoff + 1)
    integer_d_tail = 4 * (log_bounds(prime_cutoff, bits=bits) + 1) / prime_cutoff
    loss = integer_loss
    derivative_tail = Interval(0, integer_d_tail.upper, bits=bits)
    tail_method = "all-integer integral"
    if prime_cutoff >= 7:
        # Every omitted prime lies in a reduced residue class modulo 210.
        # For decreasing f, sum_(j>=0)f(a+210j) <= f(a)+integral_a^infty f/210.
        wheel_loss = Q(0)
        wheel_d_tail = Interval(0, bits=bits)
        for residue in range(1, 210):
            if gcd(residue, 210) != 1:
                continue
            first = prime_cutoff + 1 + (residue - prime_cutoff - 1) % 210
            wheel_loss += 2 * (Q(1, (first + 1) ** 2) + Q(1, 210 * (first + 1)))
            logarithm = log_bounds(first, bits=bits)
            wheel_d_tail += 4 * (logarithm / (first * first) + (logarithm + 1) / (210 * first))
        loss = min(integer_loss, wheel_loss)
        derivative_tail = Interval(0, min(integer_d_tail.upper, wheel_d_tail.upper), bits=bits)
        tail_method = "minimum of all-integer and reduced-residue modulo-210 integral tails"
    c = Interval((partial_c * (1 - loss)).lower, partial_c.upper, bits=bits)
    d = Interval(partial_d.lower, (partial_d + derivative_tail).upper, bits=bits)
    gamma = euler_gamma_bounds(bits)
    secondary = c * (2 * gamma - 1 + d)
    return {"C": c, "D": d, "gamma": gamma, "K": secondary,
            "partial_C": partial_c, "partial_D": partial_d,
            "C_tail_loss_bound": loss, "D_tail_bound": derivative_tail,
            "prime_cutoff": prime_cutoff, "prime_count": len(primes), "bits": bits,
            "tail_method": tail_method,
            "method": "rational atanh/Taylor intervals; Euler-Maclaurin gamma; integer prime tails"}
