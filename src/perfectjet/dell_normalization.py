"""Exact first-shell normalization rigidity for the classical three-body KS current.

The coordinate nome is zero.  The momentum nome is retained through first
order.  The proof uses global rational-function identities, represented as
sparse Laurent polynomials over Z; it does not infer identities from sample
points.  No claim about full DELL integrability or worldwide priority follows.

The current convention is that C_a is the coefficient of (-z)^a, so the
source's coefficient of z^a is (-1)^a C_a.  This harmless channel sign does
not change the normalization classification.
"""
from __future__ import annotations

from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations_with_replacement, permutations, product
import json
from math import comb


_ONE = {(0, 0, 0, 0): 1}
_ZERO_JET = (0, 0, 0)


def _add(left, right, scale=1):
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, 0) + scale*value
        if not result[key]:
            del result[key]
    return result


def _multiply(left, right):
    result = {}
    for key, value in left.items():
        for other, coefficient in right.items():
            monomial = tuple(a+b for a, b in zip(key, other))
            result[monomial] = result.get(monomial, 0) + value*coefficient
    return {key: value for key, value in result.items() if value}


def _scale(polynomial, scalar):
    return {key: value*scalar for key, value in polynomial.items() if value*scalar}


def _euler(polynomial, variable):
    """x_variable times its derivative; key order is t,x1,x2,x3."""
    return {key: value*key[variable+1] for key, value in polynomial.items()
            if key[variable+1]}


def _evaluate(polynomial, coupling, positions):
    values = (Q(coupling), *map(Q, positions))
    result = Q(0)
    for key, coefficient in polynomial.items():
        term = Q(coefficient)
        for value, exponent in zip(values, key):
            term *= value**exponent
        result += term
    return result


def _coefficient_numerator(momentum):
    """P_n=product_(i<j)(t^(n_i-n_j)*x_i-x_j)."""
    result = _ONE
    for i in range(3):
        for j in range(i+1, 3):
            left = [0]*4
            left[0] = momentum[i]-momentum[j]
            left[i+1] = 1
            right = [0]*4
            right[j+1] = 1
            result = _multiply(result, {tuple(left): 1, tuple(right): -1})
    return result


_DELTA = _coefficient_numerator(_ZERO_JET)


def _shell(pattern):
    return {momentum: _coefficient_numerator(momentum)
            for momentum in sorted(set(permutations(pattern)))}


def _laurent_add(left, right, scale=1):
    result = dict(left)
    for momentum, polynomial in right.items():
        value = _add(result.get(momentum, {}), polynomial, scale)
        if value:
            result[momentum] = value
        elif momentum in result:
            del result[momentum]
    return result


def _laurent_multiply(left, right):
    result = {}
    for momentum, polynomial in left.items():
        for other, coefficient in right.items():
            key = tuple(a+b for a, b in zip(momentum, other))
            value = _add(result.get(key, {}), _multiply(polynomial, coefficient))
            if value:
                result[key] = value
            elif key in result:
                del result[key]
    return result


def _multiply_coefficients(laurent, polynomial):
    return {momentum: _multiply(coefficient, polynomial)
            for momentum, coefficient in laurent.items()}


def _bracket_numerator(left, right, left_power=1, right_power=1):
    """Numerator over Delta^(r+s+1) of brackets of P/Delta^r,Q/Delta^s.

    {x_i,y_j}=delta_ij*x_i*y_j.  On y^n P/Delta and y^m Q/Delta,
    the i-th numerator is
    Delta*(m_i*(x_i d_i P)*Q-n_i*P*(x_i d_i Q))
    +(n_i*s-m_i*r)*P*Q*(x_i d_i Delta).
    """
    result = {}
    for momentum, polynomial in left.items():
        for other, coefficient in right.items():
            numerator = {}
            for i in range(3):
                first = _scale(_multiply(_euler(polynomial, i), coefficient), other[i])
                second = _scale(_multiply(polynomial, _euler(coefficient, i)), -momentum[i])
                numerator = _add(numerator, _multiply(_add(first, second), _DELTA))
                correction = _multiply(_multiply(polynomial, coefficient), _euler(_DELTA, i))
                numerator = _add(numerator, _scale(correction,
                                                   momentum[i]*right_power-other[i]*left_power))
            key = tuple(a+b for a, b in zip(momentum, other))
            value = _add(result.get(key, {}), numerator)
            if value:
                result[key] = value
            elif key in result:
                del result[key]
    return result


def _evaluate_laurent(polynomial, coupling, positions, momenta, denominator_power):
    denominator = _evaluate(_DELTA, coupling, positions)**denominator_power
    result = Q(0)
    for momentum, coefficient in polynomial.items():
        term = _evaluate(coefficient, coupling, positions)
        for value, exponent in zip(momenta, momentum):
            term *= Q(value)**exponent
        result += term
    return result/denominator


def _canonical(laurent):
    return [[list(momentum), [[list(key), value] for key, value in sorted(coefficient.items())]]
            for momentum, coefficient in sorted(laurent.items())]


def _digest(laurent):
    data = json.dumps(_canonical(laurent), separators=(',', ':'), sort_keys=True).encode()
    return sha256(data).hexdigest()


def _normalizer_columns(h1, h2, first_zero_mode):
    result = []
    for momentum, coefficient in sorted(first_zero_mode.items()):
        basis = {momentum: coefficient}
        result.append(_laurent_add(
            _laurent_multiply(h1, _bracket_numerator(basis, h2)),
            _laurent_multiply(h2, _bracket_numerator(h1, basis))))
    return result


# Rows select a y monomial followed by an x monomial, leaving Laurent t entries.
_MINOR_ROWS = (
    ((-1, 2, 2), (0, 5, 7)),
    ((-1, 2, 2), (1, 3, 8)),
    ((0, 0, 3), (0, 5, 7)),
    ((0, 2, 1), (0, 6, 6)),
    ((1, 0, 2), (2, 2, 8)),
    ((1, 1, 1), (0, 5, 7)),
)


def _minor_matrix(columns, rows=_MINOR_ROWS):
    return [[{(key[0], 0, 0, 0): value
              for key, value in column.get(momentum, {}).items() if key[1:] == positions}
             for column in columns] for momentum, positions in rows]


def _polynomial_determinant(matrix):
    """Exact sparse cofactor expansion, with a sparse row chosen at each step."""
    def solve(rows, columns):
        if not rows:
            return _ONE
        row = min(rows, key=lambda i: sum(bool(matrix[i][j]) for j in columns))
        row_index = rows.index(row)
        next_rows = tuple(i for i in rows if i != row)
        result = {}
        for column_index, col in enumerate(columns):
            if matrix[row][col]:
                minor = solve(next_rows, tuple(j for j in columns if j != col))
                result = _add(result, _multiply(matrix[row][col], minor),
                              -1 if (row_index+column_index) % 2 else 1)
        return result
    indices = tuple(range(len(matrix)))
    return solve(indices, indices)


def _specialize_coupling(laurent, coupling):
    result = {}
    for momentum, polynomial in laurent.items():
        coefficient = {}
        for key, value in polynomial.items():
            monomial = (0, *key[1:])
            coefficient[monomial] = coefficient.get(monomial, Q(0)) + value*Q(coupling)**key[0]
        result[momentum] = {key: value for key, value in coefficient.items() if value}
    return result


_SECOND_MINOR_ROWS = (
    ((-2, 2, 3), (0, 6, 9)), ((-2, 2, 3), (1, 4, 10)),
    ((-1, 0, 4), (0, 6, 9)), ((-1, 2, 2), (0, 6, 9)),
    ((0, 0, 3), (1, 4, 10)), ((0, 1, 2), (0, 6, 9)),
    ((-2, 3, 2), (0, 6, 9)), ((-1, 1, 3), (0, 6, 9)),
    ((-1, 3, 1), (0, 6, 9)), ((0, 1, 2), (1, 4, 10)),
    ((0, 2, 1), (0, 6, 9)), ((0, -1, 4), (0, 6, 9)),
    ((0, 1, 2), (1, 6, 8)), ((1, -1, 3), (0, 6, 9)),
    ((1, 0, 2), (0, 6, 9)), ((0, 3, 0), (0, 6, 9)),
    ((1, 1, 1), (0, 6, 9)), ((1, 2, 0), (0, 6, 9)),
    ((2, -1, 2), (1, 4, 10)), ((2, 0, 1), (0, 6, 9)),
    ((2, 1, 0), (0, 6, 9)),
)


def _second_minor_factor():
    result = {(-31, 0, 0, 0): -128}
    for factor, exponent in (({(1, 0, 0, 0): 1, (0, 0, 0, 0): -1}, 44),
                             ({(1, 0, 0, 0): 1, (0, 0, 0, 0): 1}, 2),
                             ({(1, 0, 0, 0): 1, (0, 0, 0, 0): 2}, 5),
                             ({(1, 0, 0, 0): 1, (0, 0, 0, 0): 3}, 2),
                             ({(2, 0, 0, 0): 1, (1, 0, 0, 0): 1, (0, 0, 0, 0): 1}, 3)):
        for _ in range(exponent):
            result = _multiply(result, factor)
    return result


def second_order_normalization_receipt():
    """Global omega^2 commutativity and a 21-column homogeneous obstruction.

    Here the extra denominator term rho2 is restricted to products of two
    first-shell basis functions.  The symbolic minor proves generic full
    rank, with explicitly listed exclusions where this particular minor
    vanishes.  No rank classification is made at those excluded couplings.
    """
    h1, h2 = _shell((1, 0, 0)), _shell((1, 1, 0))
    a, b, c = _shell((-1, 0, 1)), _shell((-1, 1, 1)), _shell((2, 0, 0))
    e, f = _shell((-1, 0, 2)), _shell((-1, 1, 2))
    first_h1 = _laurent_add(_multiply_coefficients(b, _DELTA), _laurent_multiply(a, h1), -1)
    first_h2 = _laurent_add(_multiply_coefficients(c, _DELTA), _laurent_multiply(a, h2), -1)
    a_squared, delta_squared = _laurent_multiply(a, a), _multiply(_DELTA, _DELTA)
    second_h1 = _laurent_add(_laurent_add(
        _multiply_coefficients(e, delta_squared),
        _multiply_coefficients(_laurent_multiply(a, b), _DELTA), -1),
        _laurent_multiply(a_squared, h1))
    second_h2 = _laurent_add(_laurent_add(
        _multiply_coefficients(f, delta_squared),
        _multiply_coefficients(_laurent_multiply(a, c), _DELTA), -1),
        _laurent_multiply(a_squared, h2))
    bracket_terms = (_bracket_numerator(h1, second_h2, 1, 3),
                     _bracket_numerator(first_h1, first_h2, 2, 2),
                     _bracket_numerator(second_h1, h2, 3, 1))
    difference = {}
    for term in bracket_terms:
        difference = _laurent_add(difference, term)
    pairs = tuple(combinations_with_replacement(range(6), 2))
    basis_keys = sorted(a)
    columns = []
    for i, j in pairs:
        basis = _laurent_multiply({basis_keys[i]: a[basis_keys[i]]},
                                 {basis_keys[j]: a[basis_keys[j]]})
        columns.append(_laurent_add(
            _laurent_multiply(h1, _bracket_numerator(basis, h2, 2, 1)),
            _laurent_multiply(h2, _bracket_numerator(h1, basis, 1, 2))))
    matrix = _minor_matrix(columns, _SECOND_MINOR_ROWS)
    determinant = _polynomial_determinant(matrix)
    expected = _second_minor_factor()
    zero_mode_shell_two = [n for n in product(range(-1, 3), repeat=3)
                          if sum(n) == 0 and sum(k*(k-1)//2 for k in n) == 2]
    checks = {'omega_squared_global_poisson_identity': not difference,
              'zero_mode_has_no_omega_squared_shell': not zero_mode_shell_two,
              'symbolic_21_by_21_minor_factorization': determinant == expected,
              'minor_nonzero_at_t_two': _evaluate(determinant, 2, (1, 1, 1)) != 0}
    return {
        'schema': 'perfectjet/dell-second-normalization/1',
        'passed': all(checks.values()), 'checks': checks,
        'scope': {'particles': 3, 'coordinate_nome': 0, 'momentum_nome_order': 2,
                  'global_identity': True, 'all_order_integrability_claim': False,
                  'all_coupling_rank_classification_claim': False},
        'second_shell': {'C0': [], 'C1': [list(n) for n in sorted(e)],
                         'C2': [list(n) for n in sorted(f)]},
        'bracket_certificate': {'denominator': 'Delta^5',
                                'summand_term_counts': [sum(map(len, term.values())) for term in bracket_terms],
                                'summand_sha256': [_digest(term) for term in bracket_terms],
                                'difference_terms': sum(map(len, difference.values()))},
        'homogeneous_normalizer': {
            'ansatz': 'rho2=sum_(i<=j) mu_ij f_i f_j, f_i indexed by perm(-1,0,1)',
            'dimension': 21, 'generic_rank': 21, 'unique_correction': 'rho2=0',
            'column_pairs': [list(pair) for pair in pairs],
            'minor_rows': [[list(n), list(k)] for n, k in _SECOND_MINOR_ROWS],
            'minor_matrix': [[[[key[0], value] for key, value in sorted(entry.items())]
                              for entry in row] for row in matrix],
            'minor_determinant': '-128*(t-1)^44*(t+1)^2*(t+2)^5*(t+3)^2*(t^2+t+1)^3/t^31',
            'minor_determinant_laurent_coefficients': [[key[0], value] for key, value in sorted(determinant.items())],
            'minor_value_at_t_two': str(_evaluate(determinant, 2, (1, 1, 1))),
            'unclassified_special_couplings': ['-1', '-2', '-3', 'exp(2*pi*i/3)', 'exp(-2*pi*i/3)'],
            'free_coupling': 't=1', 'undefined_coupling': 't=0',
        },
    }


def _coordinate_first_correction(momentum):
    """S_n in theta_p(t^d z)/theta_p(z)=F_n(0)*(1+p*S_n+O(p^2))."""
    result = {}
    for i in range(3):
        for j in range(i+1, 3):
            difference = momentum[i]-momentum[j]
            for left, right, exponent in ((i, j, difference), (j, i, -difference)):
                base = [0]*4
                base[left+1], base[right+1] = 1, -1
                shifted = list(base)
                shifted[0] = exponent
                result = _add(result, {tuple(base): 1})
                result = _add(result, {tuple(shifted): -1})
    return result


def _coordinate_shell_series(pattern):
    base = _shell(pattern)
    return (base, {momentum: _multiply(coefficient, _coordinate_first_correction(momentum))
                   for momentum, coefficient in base.items()})


def _series_add(left, right, scale=1):
    return tuple(_laurent_add(a, b, scale) for a, b in zip(left, right))


def _series_product(left, right):
    return (_laurent_multiply(left[0], right[0]),
            _laurent_add(_laurent_multiply(left[0], right[1]),
                         _laurent_multiply(left[1], right[0])))


def _series_bracket(left, right):
    return (_bracket_numerator(left[0], right[0]),
            _laurent_add(_bracket_numerator(left[0], right[1]),
                         _bracket_numerator(left[1], right[0])))


def mixed_nome_normalization_receipt():
    """Global first-coordinate-nome, first-momentum-nome compatibility.

    This computes actual rational coefficient identities, not evaluation
    samples.  Combining the p=0 six-column minor with these identities also
    forces lambda_n(p)=1 mod p^2 for every fixed t!=0,1 in the six-function
    first-shell ansatz.  No all-order extension is asserted.
    """
    h1, h2, a, b, c = [_coordinate_shell_series(pattern) for pattern in
                       ((1, 0, 0), (1, 1, 0), (-1, 0, 1), (-1, 1, 1), (2, 0, 0))]
    base = _series_bracket(h1, h2)
    raw = _series_add(_series_bracket(b, h2), _series_bracket(h1, c))
    normalizer = _series_add(_series_product(h1, _series_bracket(a, h2)),
                             _series_product(h2, _series_bracket(h1, a)))
    difference = tuple(_laurent_add(_multiply_coefficients(r, _DELTA), n, -1)
                       for r, n in zip(raw, normalizer))
    checks = {'zeroth_momentum_order_coordinate_coefficients_zero': all(not x for x in base),
              'first_momentum_order_coordinate_coefficients_zero': all(not x for x in difference)}
    return {
        'schema': 'perfectjet/dell-mixed-normalization/1',
        'passed': all(checks.values()), 'checks': checks,
        'scope': {'particles': 3, 'coordinate_nome_order': 1, 'momentum_nome_order': 1,
                  'global_rational_coefficient_identities': True,
                  'all_order_integrability_claim': False,
                  'full_coordinate_ellipticity_claim': False},
        'theta_ratio_correction':
            'S_n=sum_(i<j)[(1-t^(n_i-n_j))*x_i/x_j+(1-t^(n_j-n_i))*x_j/x_i]',
        'proof': {'zeroth_momentum_denominator': 'Delta^3',
                  'first_momentum_denominator': 'Delta^4',
                  'zeroth_momentum_zero_terms_by_coordinate_order': [sum(map(len, x.values())) for x in base],
                  'first_momentum_zero_terms_by_coordinate_order': [sum(map(len, x.values())) for x in difference],
                  'raw_numerator_terms_by_coordinate_order': [sum(map(len, x.values())) for x in raw],
                  'normalizer_numerator_terms_by_coordinate_order': [sum(map(len, x.values())) for x in normalizer],
                  'raw_sha256_by_coordinate_order': [_digest(x) for x in raw],
                  'normalizer_sha256_by_coordinate_order': [_digest(x) for x in normalizer]},
        'conditional_on_first_shell_minor':
            'The independently certified M0 determinant -(t-1)^14/t^8 implies '
            'lambda_n(p)=1 modulo p^2 for all six n and every fixed t!=0,1.',
    }


def normalization_receipt(include_numerators=False):
    """Replay two global identities and the classified first-shell normalizer.

    A complete symbolic coefficient minor is -(t-1)^14/t^8.  Thus rank is
    six at every nonzero t except t=1, where all six columns vanish.  The
    claim concerns the six fixed first-shell functions, with coefficients
    scalar in positions and momenta; it is not uniqueness among all functions.
    """
    h1, h2 = _shell((1, 0, 0)), _shell((1, 1, 0))
    zero, one, two = _shell((-1, 0, 1)), _shell((-1, 1, 1)), _shell((2, 0, 0))
    base = _bracket_numerator(h1, h2)
    raw = _laurent_add(_bracket_numerator(one, h2), _bracket_numerator(h1, two))
    columns = _normalizer_columns(h1, h2, zero)
    normalizer = {}
    for column in columns:
        normalizer = _laurent_add(normalizer, column)
    difference = _laurent_add(_multiply_coefficients(raw, _DELTA), normalizer, -1)
    matrix = _minor_matrix(columns)
    determinant = _polynomial_determinant(matrix)
    expected_determinant = {(power-8, 0, 0, 0): -comb(14, power)*(-1)**(14-power)
                            for power in range(15)}
    at_free_coupling = [_specialize_coupling(column, 1) for column in columns]
    free_columns_zero = all(not coefficient for column in at_free_coupling
                            for coefficient in column.values())
    first_shell_vectors = {
        total: sorted(n for n in product(range(-1, 3), repeat=3)
                      if sum(n) == total and sum(k*(k-1)//2 for k in n) == 1)
        for total in (0, 1, 2)}
    shell_complete = (first_shell_vectors[0] == sorted(zero)
                      and first_shell_vectors[1] == sorted(one)
                      and first_shell_vectors[2] == sorted(two))
    witness = _evaluate_laurent(raw, 2, (1, 3, 7), (2, 5, 11), 3)
    checks = {
        'zeroth_order_global_poisson_identity': not base,
        'first_order_global_normalized_poisson_identity': not difference,
        'first_shell_exhaustive': shell_complete,
        'normalizer_minor_symbolic_factorization': determinant == expected_determinant,
        'normalizer_rank_zero_at_t_one': free_columns_zero,
        'unnormalized_modes_fail': witness != 0,
    }
    receipt = {
        'schema': 'perfectjet/dell-normalization/1',
        'passed': all(checks.values()),
        'checks': checks,
        'source': {'url': 'https://arxiv.org/abs/2010.08077', 'equation': '(1.1)',
                   'channel_convention': 'C_a is the coefficient of (-z)^a; source O_a=(-1)^a C_a'},
        'scope': {'particles': 3, 'coordinate_nome': 0, 'momentum_nome_order': 1,
                  'proof_domain': 'Q(t,x1,x2,x3)[y1^+/-1,y2^+/-1,y3^+/-1]',
                  'poisson': '{x_i,y_j}=delta_ij*x_i*y_j',
                  'first_order_identity_is_global': True,
                  'full_coordinate_ellipticity_claim': False,
                  'all_order_integrability_claim': False,
                  'global_normalization_uniqueness_claim': False,
                  'world_first_priority_claim': False},
        'first_shell': {str(total): [list(n) for n in first_shell_vectors[total]]
                        for total in (0, 1, 2)},
        'global_identity': {'denominator': 'Delta^4, Delta=prod_(i<j)(x_i-x_j)',
                            'zero_numerator_terms': sum(map(len, base.values())),
                            'first_order_difference_terms': sum(map(len, difference.values())),
                            'raw_bracket_numerator_terms': sum(map(len, raw.values())),
                            'normalizer_numerator_terms': sum(map(len, normalizer.values())),
                            'raw_bracket_numerator_sha256': _digest(raw),
                            'normalizer_numerator_sha256': _digest(normalizer)},
        'unnormalized_counterexample': {'t': '2', 'x': ['1', '3', '7'], 'y': ['2', '5', '11'],
                                        'R': str(witness),
                                        'source_signed_bracket': str(-witness),
                                        'power_s_bracket_coefficient': '(1-s)*R'},
        'normalizer_classification': {
            'ansatz': 'rho=sum_(n in perm(-1,0,1)) lambda_n P_n*y^n/Delta',
            'generic_solution': 'lambda_n=1 for all six n',
            'unique_for_all_couplings': 't in C except 0 and 1',
            'exceptional_coupling': 't=1: all six lambda_n arbitrary',
            'excluded_coupling': 't=0: current Laurent coefficients are undefined',
            'column_momenta': [list(n) for n in sorted(zero)],
            'minor_rows': [[list(momentum), list(positions)] for momentum, positions in _MINOR_ROWS],
            'minor_matrix': [[[[key[0], value] for key, value in sorted(entry.items())]
                              for entry in row] for row in matrix],
            'minor_determinant': '-(t-1)^14/t^8',
            'minor_determinant_laurent_coefficients': [[key[0], value]
                                                       for key, value in sorted(determinant.items())],
        },
        'analytic_homogeneous_freedom':
            'For arbitrary rho, first-order commutativity holds iff {rho-A,h1/h2}=0 on h2!=0; '
            'this allows extra normalizers outside the six-function ansatz.',
    }
    if include_numerators:
        receipt['raw_bracket_numerator'] = _canonical(raw)
        receipt['normalizer_numerator'] = _canonical(normalizer)
    return receipt
