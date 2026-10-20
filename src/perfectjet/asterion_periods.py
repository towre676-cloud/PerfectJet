"""Exact bounded theta/lambda/2F1 certificates for the level-one E8 character.

The formal variable is Q=exp(pi*i*tau), and the character variable is q=Q^2.
The identities are classical (NIST DLMF 19.5, 20.9 and 23.15); this module
implements their coefficient replay and period cancellation, not a new
modular identity or an identification with the program's KZ local system.
"""
from __future__ import annotations

from fractions import Fraction as Q
from math import comb, isqrt


SOURCES = ('https://dlmf.nist.gov/19.5', 'https://dlmf.nist.gov/20.9',
           'https://dlmf.nist.gov/23.15')


def _order(value, maximum=42):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum:
        raise ValueError(f'order must be an integer in 0..{maximum}')
    return value


def _rational(value):
    if isinstance(value, (bool, float)):
        raise ValueError('exact rational coefficients required')
    try:
        return Q(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError('exact rational coefficients required') from exc


def _series(values, order):
    values = list(values)
    return tuple(_rational(values[i]) if i < len(values) else Q(0) for i in range(order + 1))


def multiply(left, right, order):
    """Truncated exact multiplication through the stated Q degree."""
    order = _order(order)
    left, right = _series(left, order), _series(right, order)
    result = [Q(0)] * (order + 1)
    for i, x in enumerate(left):
        if x:
            for j, y in enumerate(right[:order + 1 - i]):
                if y:
                    result[i + j] += x * y
    return tuple(result)


def power(series, exponent, order):
    order = _order(order)
    if isinstance(exponent, bool) or not isinstance(exponent, int) or exponent < 0:
        raise ValueError('nonnegative integer exponent required')
    result = (Q(1),) + (Q(0),) * order
    base = _series(series, order)
    while exponent:
        if exponent & 1:
            result = multiply(result, base, order)
        exponent //= 2
        if exponent:
            base = multiply(base, base, order)
    return result


def reciprocal(series, order):
    """Invert a unit formal series; a vanishing constant is rejected."""
    order = _order(order)
    series = _series(series, order)
    if not series[0]:
        raise ValueError('only a unit series with nonzero constant can be inverted')
    out = [1 / series[0]]
    for n in range(1, order + 1):
        out.append(-sum((series[k] * out[n - k] for k in range(1, n + 1)), Q(0)) / series[0])
    return tuple(out)


def compose(outer, inner, order):
    """Compose at a zero-constant formal series, retaining exact coefficients."""
    order = _order(order)
    outer, inner = _series(outer, order), _series(inner, order)
    if inner[0]:
        raise ValueError('formal composition requires a zero-constant inner series')
    result = [Q(0)] * (order + 1)
    term = (Q(1),) + (Q(0),) * order
    for coefficient in outer:
        if coefficient:
            for n, value in enumerate(term):
                result[n] += coefficient * value
        term = multiply(term, inner, order)
    return tuple(result)


def embed_q_series(coefficients, order, *, q_power=2):
    """Embed a q-series as q=Q^q_power; q_power=2 is the period convention."""
    order = _order(order)
    if isinstance(q_power, bool) or not isinstance(q_power, int) or q_power < 1:
        raise ValueError('positive integer q_power required')
    out = [Q(0)] * (order + 1)
    for n, value in enumerate(coefficients):
        if q_power * n > order:
            break
        out[q_power * n] = _rational(value)
    return tuple(out)


def theta_lambda_series(order=16):
    """Return theta_3(Q), A(Q), and lambda(Q)=16*Q*A(Q)^4/theta_3(Q)^4."""
    order = _order(order)
    theta = [Q(0)] * (order + 1)
    theta[0] = 1
    for n in range(1, isqrt(order) + 1):
        theta[n * n] += 2
    triangular = [Q(0)] * (order + 1)
    for n in range(isqrt(order) + 1):
        if n * (n + 1) <= order:
            triangular[n * (n + 1)] += 1
    numerator = power(triangular, 4, order)
    shifted = (Q(0),) + tuple(16 * value for value in numerator[:order])
    lam = multiply(shifted, reciprocal(power(theta, 4, order), order), order)
    return {'theta3': tuple(map(Q, theta)), 'A': tuple(triangular), 'lambda': lam}


def hypergeometric_period_coefficients(order=16):
    """Coefficients of 2F1(1/2,1/2;1;lambda)."""
    order = _order(order)
    return tuple(Q(comb(2 * n, n) ** 2, 16 ** n) for n in range(order + 1))


def _subtract(left, right):
    return tuple(x - y for x, y in zip(left, right))


def _json(value):
    if isinstance(value, Q):
        return value.numerator if value.denominator == 1 else str(value)
    if isinstance(value, dict):
        return {str(k): _json(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json(v) for v in value]
    return value


def periods_receipt(order=16):
    """Replay the classical periods and normalized E8-character cube exactly.

    Two extra internal orders are retained before cancelling the Q^2 factor
    of lambda^2.  Public orders are bounded by 40.  Every residual coefficient
    through the reported precision is returned, including the guard orders.
    """
    order = _order(order, 40)
    internal = order + 2
    from .asterion_currents import CurrentPopulations, e4_coefficients, euler_product_coefficients
    series = theta_lambda_series(internal)
    theta, lam = series['theta3'], series['lambda']
    period = compose(hypergeometric_period_coefficients(internal), lam, internal)
    theta_square = power(theta, 2, internal)
    lam_square = power(lam, 2, internal)
    one_minus = tuple(Q(n == 0) - lam[n] for n in range(internal + 1))
    modular_polynomial = tuple(one_minus[n] + lam_square[n] for n in range(internal + 1))
    period_e4 = multiply(modular_polynomial, power(period, 4, internal), internal)
    reference_e4 = embed_q_series(e4_coefficients(internal // 2), internal)
    # Delta=Q^2*phi(Q^2)^24 has a double zero at the Q-cusp.
    delta_unit = embed_q_series(euler_product_coefficients(((1, 24),), internal // 2), internal)
    reference_delta = (Q(0), Q(0)) + delta_unit[:internal - 1]
    lambda_denominator = multiply(lam_square, power(one_minus, 2, internal), internal)
    period_delta = tuple(x / 256 for x in multiply(lambda_denominator, power(period, 12, internal), internal))
    if lambda_denominator[:2] != (0, 0) or lambda_denominator[2] != 256:
        raise ArithmeticError('lambda denominator has the wrong cusp valuation or nome convention')
    # Cancel Q^2 only after computing through order+2.  The remaining
    # denominator is a unit, so ordinary exact series inversion is valid.
    denominator_unit = lambda_denominator[2:order + 3]
    numerator = tuple(256 * x for x in power(modular_polynomial, 3, order))
    character_from_lambda = multiply(numerator, reciprocal(denominator_unit, order), order)
    populations = CurrentPopulations(order // 2)
    normalized_character = embed_q_series(populations.simple, order)
    character_cube = power(normalized_character, 3, order)
    residuals = {
        'hypergeometric_period_minus_theta3_squared': _subtract(period, theta_square),
        'period_e4_minus_divisor_sum_e4': _subtract(period_e4, reference_e4),
        'period_delta_minus_euler_product_delta': _subtract(period_delta, reference_delta),
        'character_cube_minus_period_cancelled_j': _subtract(character_cube, character_from_lambda),
    }
    passed = all(not any(values) for values in residuals.values())
    return _json({'schema': 'perfectjet/asterion-periods/1',
        'order': order, 'internal_order': internal, 'guard_orders_for_cusp_cancellation': 2,
        'arithmetic': 'fractions.Fraction; exact formal-series composition and unit inversion',
        'nome_convention': {'theta_variable': 'Q=exp(pi*i*tau)',
                            'character_variable': 'q=exp(2*pi*i*tau)=Q^2'},
        'identities': {
            'lambda': 'lambda=16*Q*A^4/theta3^4, A=sum_(n>=0)Q^(n(n+1))',
            'period': 'F=2F1(1/2,1/2;1;lambda)=theta3(Q)^2',
            'e4': 'E4(Q^2)=(1-lambda+lambda^2)*F^4',
            'delta': 'Delta(Q^2)=lambda^2*(1-lambda)^2*F^12/256',
            'normalized_character_cube': 'H(Q^2)^3=256*Q^2*(1-lambda+lambda^2)^3/(lambda^2*(1-lambda)^2)',
            'full_character_cube': 'chi(q)=q^(-1/3)*H(q), chi(q)^3=j(tau)',
        },
        'theta3_coefficients': theta[:order + 1], 'lambda_coefficients': lam[:order + 1],
        'hypergeometric_lambda_coefficients': hypergeometric_period_coefficients(order),
        'composed_period_coefficients': period[:order + 1],
        'e4_Q_coefficients': reference_e4[:order + 1],
        'normalized_character_Q_coefficients': normalized_character,
        'normalized_character_cube_Q_coefficients': character_cube,
        'period_cancelled_character_cube_Q_coefficients': character_from_lambda,
        'residuals': residuals,
        'checks': {'period_coefficients': internal + 1, 'e4_coefficients': internal + 1,
                   'delta_coefficients': internal + 1, 'character_cube_coefficients': order + 1},
        'passed': passed, 'sources': SOURCES,
        'scope': 'Classical identities with exact coefficient replay at the stated finite order. No novelty, global analytic-continuation proof, KZ-period comparison, or arithmetic31 identification is claimed.'})
