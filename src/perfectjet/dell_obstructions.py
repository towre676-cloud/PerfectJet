"""Exact obstruction to particlewise ellipticization of trigonometric RS.

This module retains the standard three-particle Ruijsenaars coordinate
coefficients and replaces every multiplicative momentum y_i by one common
profile f(y_i).  It does not obstruct general double-elliptic systems.
Only fractions and finite polynomial arithmetic enter the certificates.
"""

from collections import defaultdict
from fractions import Fraction
from itertools import product


Q = Fraction
WITNESS_POSITIONS = (Q(1), Q(3), Q(7))
SECOND_WITNESS_POSITIONS = (Q(1), Q(2), Q(5))
# K(T) = sum_j COUPLING_WITNESS[j] T^j, in ascending powers.
COUPLING_WITNESS = (Q(-35, 24), Q(7, 4), Q(0), Q(-13, 36), Q(5, 72))
SECOND_COUPLING_WITNESS = (Q(-35, 8), Q(45, 8), Q(0), Q(-27, 16), Q(7, 16))


def coupling_witness(coupling):
    """Coefficient of the exact diagonal-momentum bracket identity."""
    coupling = Q(coupling)
    return sum(c * coupling**j for j, c in enumerate(COUPLING_WITNESS))


def _coordinate_data(positions, coupling):
    x = tuple(map(Q, positions))
    t = Q(coupling)
    if len(x) != 3 or len(set(x)) != 3 or any(v == 0 for v in x):
        raise ValueError("Three distinct nonzero positions are required")

    def factor(i, j):
        return (t * x[i] - x[j]) / (x[i] - x[j])

    def derivative(i, j, k):
        sign = int(k == i) - int(k == j)
        return sign * (1 - t) * x[i] * x[j] / (x[i] - x[j])**2

    def evaluate(pairs, k=None):
        if k is None:
            result = Q(1)
            for i, j in pairs:
                result *= factor(i, j)
            return result
        result = Q(0)
        for n, (i, j) in enumerate(pairs):
            term = derivative(i, j, k)
            for m, (left, right) in enumerate(pairs):
                if m != n:
                    term *= factor(left, right)
            result += term
        return result

    singletons = [[(i, j) for j in range(3) if j != i] for i in range(3)]
    # b_i is the coefficient of the pair complementary to i.
    complements = [[(j, i) for j in range(3) if j != i] for i in range(3)]
    a = tuple(evaluate(p) for p in singletons)
    b = tuple(evaluate(p) for p in complements)
    da = tuple(tuple(evaluate(p, i) for p in singletons) for i in range(3))
    db = tuple(tuple(evaluate(p, i) for p in complements) for i in range(3))
    return a, b, da, db


def bracket_profile_polynomials(positions=WITNESS_POSITIONS, coupling=2):
    """Return P_i(z), where {H1[f],H2[f]}=sum_i y_i f'(y_i) P_i(f(y)).

    Polynomial keys are triples of nonnegative exponents.  Coefficients
    use {x_i,y_j}=delta_ij x_i y_j, hence the opposite Poisson convention
    negates all three polynomials without changing the obstruction.
    """
    a, b, da, db = _coordinate_data(positions, coupling)
    polynomials = []
    for i in range(3):
        out = defaultdict(Q)
        for j in range(3):
            for k in range(3):
                if k == i:
                    continue
                remaining = next(l for l in range(3) if l != i and l != k)
                power = [0, 0, 0]
                power[j] += 1
                power[remaining] += 1
                out[tuple(power)] += da[i][j] * b[k]
        for k in range(3):
            power = tuple(int(l != k) for l in range(3))
            out[power] -= a[i] * db[i][k]
        polynomials.append({m: c for m, c in out.items() if c})
    return tuple(polynomials)


def profile_bracket(positions, coupling, momenta, profile, logarithmic_derivative):
    """Evaluate the exact bracket for supplied f(y) and y*f'(y)."""
    if len(momenta) != 3:
        raise ValueError("Three momenta are required")
    y = tuple(map(Q, momenta))
    z = tuple(Q(profile(v)) for v in y)
    g = tuple(Q(logarithmic_derivative(v)) for v in y)
    polynomials = bracket_profile_polynomials(positions, coupling)
    return sum(g[i] * sum(c * product_value(z, m) for m, c in p.items())
               for i, p in enumerate(polynomials))


def product_value(values, powers):
    result = Q(1)
    for value, power in zip(values, powers):
        result *= value**power
    return result


def _diagonal_polynomial(polynomial):
    result = defaultdict(Q)
    for m, c in polynomial.items():
        result[(m[0], m[1] + m[2])] += c
    return {m: c for m, c in result.items() if c}


def coupling_identity_certificate(positions=WITNESS_POSITIONS,
                                  coefficients=COUPLING_WITNESS):
    """Prove the witness identity for every coupling by degree <=4.

    At fixed positions all a,b and their logarithmic derivatives have
    coupling degree <=2.  Thus all P_i have degree <=4, so checking five
    distinct couplings proves each polynomial identity for every T.
    """
    checks = []
    for coupling in range(5):
        p = bracket_profile_polynomials(positions, coupling)
        k = sum(c * Q(coupling)**j for j, c in enumerate(coefficients))
        p0 = _diagonal_polynomial(p[0])
        p12 = defaultdict(Q)
        ordinary = defaultdict(Q)
        for i, polynomial in enumerate(p):
            for m, c in polynomial.items():
                shifted = tuple(power + int(j == i) for j, power in enumerate(m))
                ordinary[shifted] += c
            if i:
                for m, c in _diagonal_polynomial(polynomial).items():
                    p12[m] += c
        p12 = {m: c for m, c in p12.items() if c}
        expected0 = {m: c for m, c in { (1, 1): -k, (0, 2): k }.items() if c}
        expected12 = {m: c for m, c in { (2, 0): k, (1, 1): -k }.items() if c}
        checks.append({
            "coupling": coupling,
            "witness_coefficient": str(k),
            "P0_diagonal_identity": p0 == expected0,
            "P1_plus_P2_diagonal_identity": p12 == expected12,
            "ordinary_RS_bracket_zero": all(c == 0 for c in ordinary.values()),
        })
    return {
        "maximum_coupling_degree": 4,
        "distinct_exact_evaluations": 5,
        "checks": checks,
        "all_checks_passed": all(all(row[key] for key in (
            "P0_diagonal_identity", "P1_plus_P2_diagonal_identity",
            "ordinary_RS_bracket_zero")) for row in checks),
    }


def _multiply_polynomials(left, right):
    result = [Q(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i+j] += a*b
    return result


def coupling_boundary_certificate():
    """Exact Bezout identity: the two witnesses vanish together only at T=1."""
    a = tuple(72*c for c in COUPLING_WITNESS)
    b = tuple(16*c for c in SECOND_COUPLING_WITNESS)
    left = (Q(-529875), Q(-72145), Q(142128))
    right = (Q(835114), Q(187859), Q(-101520))
    la = _multiply_polynomials(a, left)
    rb = _multiply_polynomials(b, right)
    actual = [x+y for x, y in zip(la, rb)]
    expected = [Q(-2821105), Q(2821105)] + [Q(0)]*5
    second = coupling_identity_certificate(SECOND_WITNESS_POSITIONS,
                                           SECOND_COUPLING_WITNESS)
    return {
        "second_positions": [str(x) for x in SECOND_WITNESS_POSITIONS],
        "second_coupling_polynomial_ascending": [str(c) for c in SECOND_COUPLING_WITNESS],
        "second_identity": second,
        "integer_polynomial_A": [str(c) for c in a],
        "integer_polynomial_B": [str(c) for c in b],
        "bezout_multiplier_A": [str(c) for c in left],
        "bezout_multiplier_B": [str(c) for c in right],
        "bezout_result_ascending": [str(c) for c in actual],
        "only_common_coupling_zero": "1",
        "bezout_identity_passed": actual == expected,
        "free_coupling_coordinate_derivatives_zero":
            bracket_profile_polynomials(coupling=1) == ({}, {}, {}),
        "passed": actual == expected and second["all_checks_passed"],
    }


def inverse_profile_counterexample():
    """All coefficients for f(y)=y+epsilon/y at y=(2,3,3), T=2."""
    y = (Q(2), Q(3), Q(3))
    f = tuple((v, 1/v) for v in y)
    g = tuple((v, -1/v) for v in y)
    coefficients = [Q(0)] * 4
    for i, polynomial in enumerate(bracket_profile_polynomials()):
        for m, c in polynomial.items():
            factors = [g[i]] + [f[j] for j in range(3) for _ in range(m[j])]
            for choices in product(range(2), repeat=3):
                coefficients[sum(choices)] += c * product_value(
                    [factors[j][choices[j]] for j in range(3)], (1, 1, 1))
    return tuple(coefficients)


def forced_mode_certificate():
    """A mixed first-nome harmonic forced by classical current normalization.

    A_a denotes the sign-stripped current mode, so the actual KS Fourier
    mode is O_a=(-1)^a A_a.  Both Hamiltonian sign conventions are retained.
    This is a support theorem for the specified current, not a new model.
    """
    x = WITNESS_POSITIONS
    t = Q(2)

    def cost(n):
        return sum(v*(v-1)//2 for v in n)

    def coefficient(n):
        result = Q(1)
        for i in range(3):
            for j in range(i+1, 3):
                z = x[i]/x[j]
                result *= (1-t**(n[i]-n[j])*z)/(1-z)
        return result

    numerator_first = sorted(n for n in product(range(-1, 3), repeat=3)
                             if sum(n) == 1 and cost(n) == 1)
    denominator_first = sorted(n for n in product(range(-1, 3), repeat=3)
                               if sum(n) == 0 and cost(n) == 1)
    target = (-1, 2, 0)
    contributions = []
    total = Q(0)
    for n in denominator_first:
        for j in range(3):
            e = tuple(int(i == j) for i in range(3))
            if tuple(n[i]+e[i] for i in range(3)) == target:
                value = -coefficient(n)*coefficient(e)
                total += value
                contributions.append({
                    "denominator_mode": list(n), "leading_numerator_mode": list(e),
                    "denominator_coefficient": str(coefficient(n)),
                    "leading_numerator_coefficient": str(coefficient(e)),
                    "product_with_inverse_sign": str(value),
                })
    return {
        "coordinate_nome": "0",
        "positions": [str(v) for v in x],
        "coupling": str(t),
        "momentum_nome_order": 1,
        "target_momentum_mode": list(target),
        "first_numerator_support": [list(n) for n in numerator_first],
        "first_denominator_support": [list(n) for n in denominator_first],
        "target_absent_from_first_numerator": target not in numerator_first,
        "normalization_contributions": contributions,
        "sign_stripped_H1_coefficient": str(total),
        "KS_O0_inverse_O1_coefficient": str(-total),
        "support_bound": "At nome cost <=1 every n_i lies in {-1,0,1,2}; enumeration is exhaustive.",
        "scope": "Forced mixed Fourier support in the specified normalized current; no claim that this is itself a new interaction or that the current is generally commuting.",
        "passed": target not in numerator_first and len(contributions) == 1
                  and total == Q(-715, 6144),
    }


def obstruction_receipt():
    """JSON-safe finite certificates supporting the analytic no-go proof."""
    coupling = coupling_identity_certificate()
    boundary = coupling_boundary_certificate()
    forced_mode = forced_mode_certificate()
    counterexample = inverse_profile_counterexample()
    controls = []
    for exponent in (-2, -1, 0, 1, 2, 3):
        value = profile_bracket(WITNESS_POSITIONS, 2, (2, 3, 5),
                                lambda y: 3*y**exponent,
                                lambda y: 3*exponent*y**exponent)
        controls.append({"integer_exponent": exponent, "bracket": str(value)})
    return {
        "schema": "perfectjet/dell-particlewise-obstruction/1",
        "scope": "Unchanged standard trigonometric RS coordinate weights and one common scalar momentum profile; this is not a no-go for general DELL systems.",
        "positions": [str(x) for x in WITNESS_POSITIONS],
        "coupling_polynomial_ascending": [str(x) for x in COUPLING_WITNESS],
        "coupling_2_witness": str(coupling_witness(2)),
        "coupling_identity": coupling,
        "classified_coupling_boundary": boundary,
        "forced_current_mode": forced_mode,
        "analytic_elliptic_extension": {
            "hypotheses": "Multiaffine base Hamiltonians commute; coefficients are holomorphic in the coordinate nome near zero and have this RS limit.",
            "conclusion": "For each fixed nonzero T != 1 the same profile no-go holds in some complex neighborhood of coordinate nome zero; outside the discrete zeros of a chosen analytic witness it holds throughout its connected holomorphy domain.",
            "computed_nonzero_radius": None,
            "all_moduli_claim": False,
            "proof": "docs/DELL_OBSTRUCTIONS.md, abstract multiaffine lemma and analytic persistence",
        },
        "inverse_profile_bracket_coefficients": [str(x) for x in counterexample],
        "power_profile_controls": controls,
        "analytic_proof_required": True,
        "worldwide_priority_claim": False,
        "passed": coupling["all_checks_passed"] and boundary["passed"] and forced_mode["passed"]
        and counterexample == (Q(0), Q(-95, 216), Q(95, 1296), Q(0))
        and all(row["bracket"] == "0" for row in controls),
    }
