#!/usr/bin/env python3
"""Reproduce and certify the scalar quotient-kernel flip.

Requires python-flint==0.9.0 and mpmath==1.3.0.
The Arb section is an interval certificate; mpmath cycles are cross-checks.
No claim of transcendence, global trapping, or a physical model is made.
"""
import json
from pathlib import Path
import flint
from flint import arb, ctx
import mpmath as mp


X_LO = "0.942857679982338439673381626573607196371104292313667636616937664278159148381"
X_HI = "0.942857679982338439673381626573607196371104292313667636616937664278159148383"


def interval_certificate():
    ctx.prec = 384

    def data(x):
        ell = -x.cos().log()
        tangent = x.tan()
        u = x*x + ell*ell
        h = x + ell*tangent
        e = (1+ell)*(1+tangent*tangent)
        return ell, tangent, u, h, e

    def g(x):
        ell, tangent, u, h, e = data(x)
        return u*u.log() + 2*x*h*x.log()

    def gp(x):
        ell, tangent, u, h, e = data(x)
        return 2*h*(u.log()+2) + 2*(h+x*e)*x.log()

    low, high = arb(X_LO), arb(X_HI)
    assert g(low) < 0
    assert g(high) > 0
    assert data(arb("0.887"))[2] < 1
    assert g(arb(1)) > 0

    # Exactly 1130 rational cells cover [887/1000, 1]. Arb's
    # outward-rounded radii enclose each cell, including its endpoints.
    for i in range(1130):
        x_cell = arb(17741+2*i)/20000 + arb(0, arb(1)/20000)
        assert gp(x_cell) > arb("4.66"), (i, x_cell, gp(x_cell))

    x = (low+high)/2 + arb(0, (high-low)/2)
    ell, tangent, u, h, e = data(x)
    alpha = -2*x.log()/u.log()
    p = alpha/2
    k = (-p*u.log()).exp()
    u1, u2 = 2*h, 2*e
    u3 = 2*tangent*(1+tangent*tangent)*(3+2*ell)
    g1 = -p*u1/u
    g2 = -p*(u2/u-(u1/u)**2)
    g3 = -p*(u3/u-3*u1*u2/u**2+2*(u1/u)**3)
    kxx = k*(g1*g1+g2)
    kxxx = k*(g1**3+3*g1*g2+g3)
    # At the exact flip, x_alpha = -x*log(U)/4 and K_x=-1.
    c1 = 1/alpha-u.log()/2+kxx*x*u.log()/4
    sigma2 = -kxxx/3-kxx*kxx/2
    kappa = (2*c1/sigma2).sqrt()
    assert alpha > 0 and alpha < 1
    assert c1 > 0 and sigma2 > 0
    fields = dict(alpha_star=alpha, x_star=x, c1=c1, sigma2=sigma2,
                  kappa_raw_x=kappa, kxx=kxx, kxxx=kxxx,
                  normalized_reserve_slope=c1*alpha,
                  G_left=g(low), G_right=g(high))
    return {
        "status": "PASS",
        "arithmetic": "Arb real-ball interval arithmetic",
        "python_flint_version": flint.__version__,
        "precision_bits": ctx.prec,
        "root_bracket_exact_decimal": [X_LO, X_HI],
        "global_monotonicity_cells": 1130,
        "covered_interval_exact": ["887/1000", "1"],
        "certified_lower_bound_Gprime": "4.66",
        "bounds": {key: value.str(85) for key, value in fields.items()},
        "conclusion": "One positive-parameter flip; subcritical real two-cycle below threshold.",
    }


def floating_crosscheck(dps):
    mp.mp.dps = dps
    ell = lambda x: -mp.log(mp.cos(x))
    u = lambda x: x*x+ell(x)**2
    h = lambda x: x+ell(x)*mp.tan(x)
    g = lambda x: u(x)*mp.log(u(x))+2*x*h(x)*mp.log(x)
    k = lambda x, a: u(x)**(-a/2)
    x = mp.findroot(g, (mp.mpf("0.94"), mp.mpf("0.95")))
    a = -2*mp.log(x)/mp.log(u(x))
    fixed = lambda b: mp.findroot(lambda z: k(z, b)-z, x)
    mu = lambda b: mp.diff(lambda z: k(z, b), fixed(b))
    c1 = -mp.diff(mu, a)
    kxx = mp.diff(lambda z: k(z, a), x, 2)
    kxxx = mp.diff(lambda z: k(z, a), x, 3)
    sigma2 = -kxxx/3-kxx*kxx/2
    kappa = mp.sqrt(2*c1/sigma2)
    delta = mp.mpf("1e-8")
    a_cycle = a-delta
    x_fixed = fixed(a_cycle)
    cycle_lo, cycle_hi = mp.findroot(
        lambda r, s: (k(r, a_cycle)-s, k(s, a_cycle)-r),
        (x_fixed-kappa*mp.sqrt(delta), x_fixed+kappa*mp.sqrt(delta)))
    multiplier = (mp.diff(lambda z: k(z, a_cycle), cycle_lo)
                  *mp.diff(lambda z: k(z, a_cycle), cycle_hi))
    assert multiplier > 1 and cycle_lo < x_fixed < cycle_hi
    fields = dict(alpha_star=a, x_star=x, c1=c1, sigma2=sigma2,
                  kappa_raw_x=kappa, cycle_alpha=a_cycle,
                  cycle_lo=cycle_lo, cycle_hi=cycle_hi,
                  cycle_multiplier=multiplier,
                  cycle_residual=max(abs(k(cycle_lo, a_cycle)-cycle_hi),
                                     abs(k(cycle_hi, a_cycle)-cycle_lo)))
    return {"status": "PASS", "precision_decimal_digits": dps,
            "classification": "High-precision floating-point cross-check, not interval cycle enclosure",
            "values": {key: mp.nstr(value, 65) for key, value in fields.items()}}


def main():
    certificate = interval_certificate()
    crosschecks = [floating_crosscheck(80), floating_crosscheck(120)]
    for key in ("alpha_star", "x_star", "c1", "sigma2", "kappa_raw_x"):
        assert crosschecks[0]["values"][key] == crosschecks[1]["values"][key]
    result = {"status": "PASS", "interval_certificate": certificate,
              "floating_crosschecks": crosschecks,
              "assumptions": [
                  "K_alpha(x)=(x^2+(-log(cos x))^2)^(-alpha/2)",
                  "0<x<pi/2, alpha>0, real branches",
                  "The full open interval is not invariant under K_alpha",
                  "Amplitude coefficient is stated in the declared raw x coordinate"
              ]}
    path = Path(__file__).with_name("pisot-scalar-certificate.json")
    path.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "certificate": str(path),
                      "cells": certificate["global_monotonicity_cells"],
                      "alpha_star": crosschecks[0]["values"]["alpha_star"],
                      "sigma2": crosschecks[0]["values"]["sigma2"],
                      "classification": "subcritical"}, indent=2))


if __name__ == "__main__":
    main()
