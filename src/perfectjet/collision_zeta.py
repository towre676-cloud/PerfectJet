"""Exact collision arithmetic and finite Euler-factor extraction.

All polynomial coefficients are constant first.  Zeta exponents are FORMAL
local identities; a finite extraction retains its residual rational factor.
It never evaluates a naive infinite product of zeta functions.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


def integer(value, name, low=0, high=None):
    if isinstance(value, str) and len(value) <= 1024 and value.isascii() and value.isdigit():
        value = int(value)
    if isinstance(value, bool) or not isinstance(value, int) or value < low or (high is not None and value > high):
        raise ValueError(f"{name} must be an integer in the declared range")
    return value


def _trim(poly):
    out = list(poly)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out)


def _multiply(a, b, degree_budget=20000):
    if len(a) + len(b) - 2 > degree_budget:
        raise ValueError("residual polynomial degree exceeds the work budget")
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    out[i+j] += x*y
    return _trim(out)


def pell_pair(index, modulus=None, max_bits=32768):
    """Return u,v in (1+sqrt(2))**index=u+v*sqrt(2), by binary powering.

    Exact output is preflight bounded using u,v < 2**(2*index+1).
    Modular output supports remote indices without constructing that output.
    """
    n = integer(index, "index")
    bits = integer(max_bits, "max_bits", 16, 1000000)
    if modulus is not None:
        modulus = integer(modulus, "modulus", 2)
        if modulus.bit_length() > bits:
            raise ValueError("modulus exceeds the bit budget")
    elif 2*n+2 > bits:
        raise ValueError("exact Pell output exceeds the conservative bit budget; supply a modulus")
    if n.bit_length() > 4096:
        raise ValueError("index exceeds the powering work budget")
    def product(a, b):
        u, v = a[0]*b[0]+2*a[1]*b[1], a[0]*b[1]+a[1]*b[0]
        return (u % modulus, v % modulus) if modulus else (u, v)
    out, base = (1, 0), (1, 1)
    while n:
        if n & 1:
            out = product(out, base)
        n >>= 1
        if n:
            base = product(base, base)
    return out


def pell_lucas(index, modulus=None, max_bits=32768):
    u, _ = pell_pair(index, modulus, max_bits)
    return (2*u) % modulus if modulus else 2*u


def conductor_two_coefficient(index):
    """Coefficient of x**index in L_2; exact even at a remote index."""
    n = integer(index, "index")
    if n.bit_length() > 4096:
        raise ValueError("index exceeds the input-bit budget")
    return n+1 if n % 2 else 1


def conductor_two_values(limit=1000):
    """Multiplicative A(n), 1<=n<=limit, using a least-prime sieve.

    A(p**k)=1 for even k and k+1 for odd k.  The returned list has
    A(0)=0 as an unused sentinel.  This enumerates n, not divisor pairs.
    """
    limit = integer(limit, "limit", 1, 1000000)
    least = [0] * (limit+1)
    values = [0] * (limit+1)
    exponents = [0] * (limit+1)
    cores = [1] * (limit+1)
    primes = []
    values[1] = 1
    for n in range(2, limit+1):
        if not least[n]:
            least[n] = n
            primes.append(n)
        p = least[n]
        m = n//p
        if m % p == 0:
            exponents[n] = exponents[m]+1
            cores[n] = cores[m]
        else:
            exponents[n] = 1
            cores[n] = m
        values[n] = values[cores[n]] * conductor_two_coefficient(exponents[n])
        for p in primes:
            if p > least[n] or p*n > limit:
                break
            least[p*n] = p
    return values


@dataclass(frozen=True)
class RationalEulerFactor:
    """A bounded exact member of (1+x Z[[x]]) represented by P/Q."""
    numerator: tuple[int, ...]
    denominator: tuple[int, ...] = (1,)

    def __post_init__(self):
        for name in ("numerator", "denominator"):
            raw = getattr(self, name)
            if not isinstance(raw, (tuple, list)) or not raw or len(raw) > 4097:
                raise ValueError("polynomial must have 1..4097 integer coefficients")
            if any(isinstance(x, bool) or not isinstance(x, int) or x.bit_length() > 32768 for x in raw):
                raise ValueError("polynomial coefficients must be bounded integers")
            if raw[0] != 1:
                raise ValueError("each polynomial must have constant coefficient one")
            object.__setattr__(self, name, _trim(raw))

    def coefficients(self, order=24):
        order = integer(order, "order", 0, 512)
        p, q = self.numerator, self.denominator
        growth = max(abs(v).bit_length() for v in q) + len(q).bit_length()+1
        if max(abs(v).bit_length() for v in p)+(order+1)*growth > 262144:
            raise ValueError("formal coefficient growth exceeds the preflight bit budget")
        out = []
        for n in range(order+1):
            out.append((p[n] if n < len(p) else 0)-sum(q[k]*out[n-k] for k in range(1, min(n+1, len(q)))))
        return out

    def logarithmic_coefficients(self, order=24):
        """Return c_n=[x**n] x L'(x)/L(x), with c_0=0."""
        a = self.coefficients(order)
        c = [0] * len(a)
        for n in range(1, len(a)):
            c[n] = n*a[n]-sum(c[k]*a[n-k] for k in range(1, n))
        return c

    def zeta_exponents(self, order=24):
        """Unique integers b_n with L(x)=prod(1-x**n)**(-b_n)."""
        c = self.logarithmic_coefficients(order)
        b = [0] * len(c)
        for n in range(1, len(c)):
            value = c[n]-sum(d*b[d] for d in range(1, n) if n % d == 0)
            b[n], remainder = divmod(value, n)
            if remainder:
                raise ArithmeticError("Euler exponent integrality failed")
        return b

    def evaluate(self, x):
        if not isinstance(x, (int, Fraction)) or isinstance(x, bool):
            raise ValueError("exact rational x required")
        x = Fraction(x)
        def horner(p):
            out = Fraction(0)
            for v in reversed(p):
                out = out*x+v
            return out
        return horner(self.numerator)/horner(self.denominator)

    def extract(self, order=4, degree_budget=20000):
        """Finite exact factorization, retaining R with R=1+O(x**(order+1)).

        L=prod_{n<=order}(1-x**n)**(-b_n) * R.  Multiplication
        is preflight bounded; exponential exponents cannot allocate silently.
        The residual is intentionally not canceled, preserving a replayable
        polynomial identity without a symbolic factorizer dependency.
        """
        order = integer(order, "order", 0, 512)
        degree_budget = integer(degree_budget, "degree_budget", 1, 20000)
        exponents = self.zeta_exponents(order)
        p_degree = len(self.numerator)-1 + sum(n*max(b, 0) for n, b in enumerate(exponents))
        q_degree = len(self.denominator)-1 + sum(n*max(-b, 0) for n, b in enumerate(exponents))
        if max(p_degree, q_degree) > degree_budget:
            raise ValueError("finite extraction exceeds the residual degree budget; request fewer factors")
        p, q = self.numerator, self.denominator
        for n, b in enumerate(exponents[1:], 1):
            factor = (1,)+(0,)*(n-1)+(-1,)
            for _ in range(abs(b)):
                if b > 0:
                    p = _multiply(p, factor, degree_budget)
                else:
                    q = _multiply(q, factor, degree_budget)
        if any((p[k] if k < len(p) else 0) != (q[k] if k < len(q) else 0) for k in range(order+1)):
            raise ArithmeticError("finite extraction residual failed replay")
        # Find the actual first possible residual term; a finite extraction
        # may cancel more than the requested order, or be identically one.
        first = next((k for k in range(max(len(p), len(q))) if (p[k] if k < len(p) else 0) != (q[k] if k < len(q) else 0)), None)
        return {"zeta_exponents": exponents[1:], "residual_numerator": list(p),
                "residual_denominator": list(q), "residual_first_degree": first,
                "absolute_tail_half_plane": None if first is None else f"Re(s) > 1/{first}",
                "identity": "L(x)=product((1-x^n)^(-b_n),n<=order)*R(x)",
                "scope": "Finite local identity. Finitely many small primes may need separate factors; no infinite zeta product is evaluated."}


CONDUCTOR_TWO = RationalEulerFactor((1, 2, -1), (1, 0, -2, 0, 1))


def conductor_two_report(order=24, index=10**100, summatory_limit=1000):
    order = integer(order, "order", 1, 128)
    n = integer(index, "index")
    values = conductor_two_values(summatory_limit)
    c = CONDUCTOR_TWO.logarithmic_coefficients(order)
    pell_check = all(c[k] == (-1)**(k+1)*pell_lucas(k)+4*(k % 2 == 0) for k in range(1, order+1))
    return {"schema": "perfectjet/collision-pell/1", "conductor": 2,
            "local_numerator": list(CONDUCTOR_TWO.numerator),
            "local_denominator": list(CONDUCTOR_TWO.denominator),
            "local_coefficients": CONDUCTOR_TWO.coefficients(order),
            "pell_lucas": [pell_lucas(k) for k in range(order+1)],
            "logarithmic_derivative_coefficients": c,
            "pell_identity_verified": pell_check,
            "formal_zeta_exponents": CONDUCTOR_TWO.zeta_exponents(order)[1:],
            "remote_index": str(n), "remote_coefficient": str(conductor_two_coefficient(n)),
            "summatory_limit": len(values)-1, "summatory_count": sum(values),
            "arithmetic_values": values[1:min(len(values), 65)],
            "analytic_status": {"continuation": "meromorphic for Re(s)>0", "natural_boundary": "Re(s)=0",
                                "theorem": "Estermann applied to 1+2x-x^2; cyclotomic denominator does not change the boundary"},
            "scope": "Exact arithmetic and classical theorem application; numerical finite checks are not a proof of a natural boundary. Historical priority unassessed."}
