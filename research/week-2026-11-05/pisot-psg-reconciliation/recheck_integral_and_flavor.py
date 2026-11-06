#!/usr/bin/env python3
"""Independent checks for the Pisot/PSG reconciliation.

Quadratures are high-precision numerical checks, not interval certificates.
The accompanying report supplies the analytic integral proof. Polynomial
remainders and Bezout identities below use exact rational arithmetic.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import mpmath as mp
import sympy as sp


def log_cos(x):
    return -mp.log1p(-2 * mp.sin(x / 2) ** 2)


def regularized_integral(alpha):
    """Subtract the lower-end singularity, then use a logarithmic upper tail."""
    delta = mp.mpf(1) / 4
    phase = mp.exp(-mp.j * mp.pi * alpha / 2)

    def residual(x):
        if not x:
            return mp.mpf('0.5') if alpha == 1 else mp.mpf(0)
        deformation = mp.expm1(-alpha * mp.log1p(-mp.j * log_cos(x) / x))
        return mp.re(phase * deformation) / x ** alpha

    lower = mp.quad(residual, [0, delta])
    if alpha != 1:
        lower += mp.cos(mp.pi * alpha / 2) * delta ** (1 - alpha) / (1 - alpha)

    u0 = log_cos(delta)

    def tail(u):
        x = mp.acos(mp.exp(-u))
        jacobian = mp.exp(-u) / mp.sqrt(-mp.expm1(-2 * u))
        return mp.re((u + mp.j * x) ** (-alpha)) * jacobian

    return lower + mp.quad(tail, [u0, mp.mpf(1), 4, 16, mp.inf])


def integral_checks(dps):
    rows = []
    with mp.workdps(dps):
        for raw in ['0.125', '0.25', '0.5', '0.741804515087894688919016', '0.9', '0.99']:
            alpha = mp.mpf(raw)
            value = regularized_integral(alpha)
            expected = mp.pi / (2 * mp.log(2) ** alpha)
            err = abs(value - expected)
            assert err < mp.mpf(10) ** (-(dps // 2))
            rows.append(dict(alpha=raw, integral=mp.nstr(value, 55),
                             closed_form=mp.nstr(expected, 55),
                             absolute_difference=mp.nstr(err, 8)))
        at_one = regularized_integral(mp.mpf(1))
        endpoint_expected = mp.pi / (2 * mp.log(2)) - mp.pi / 2
        assert abs(at_one - endpoint_expected) < mp.mpf(10) ** (-(dps // 2))
        return dict(precision_decimal_digits=dps, status='PASS',
                    evidence='high-precision checks; the proof is analytic',
                    interior=rows,
                    endpoint_alpha_one=dict(integral=mp.nstr(at_one, 55),
                         expected=mp.nstr(endpoint_expected, 55),
                         missing_boundary_mass=mp.nstr(mp.pi / 2, 55),
                         absolute_difference=mp.nstr(abs(at_one-endpoint_expected), 8)))


def exact_flavor_check():
    x = sp.symbols('x')
    P = x**8 - 7*x**6 + 14*x**4 - 8*x**2 + 1
    Q = -1 + 3*x - x**3
    Vprime = P * Q
    h = sp.expand((4-x*x)*sp.diff(Vprime, x) - x*Vprime)
    R = sp.rem(sp.diff(h*h, x), P, domain=sp.QQ)
    expected = 5040-6880*x-31360*x*x+43600*x**3+24160*x**4-30080*x**5-4400*x**6+4800*x**7
    assert sp.expand(R - expected) == 0
    A, B, gcd = sp.gcdex(P, R, x)
    assert gcd == 1 and sp.expand(A*P+B*R) == 1
    return dict(status='PASS', evidence='exact rational polynomial arithmetic',
                P=str(P), Q=str(Q), angular_curvature=str(h), remainder=str(R),
                gcd='1', bezout_P=str(A), bezout_R=str(B),
                conclusion='The declared scalar loop torque is nonzero at every root of P.',
                scope='This is the specified scalar-only counterterm; it is not a no-go theorem for additional fields.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dps', type=int, default=80)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('integral-and-flavor-checks.json'))
    args = parser.parse_args()
    if args.dps < 50:
        parser.error('--dps must be at least 50')
    report = dict(status='PASS', integral=integral_checks(args.dps), flavor=exact_flavor_check())
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
