"""Exact exceptional-coupling classification for quadratic DELL normalizers.

This distinguishes a kernel in the 21 coefficient parameters from nonzero
functions represented by that kernel.  Primitive cubic roots produce only
basis dependencies; t=-1 produces an existing-integral normalizer.
"""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import combinations_with_replacement

from . import dell_normalization as dn


class _Eisenstein:
    """Q(zeta), zeta^2+zeta+1=0; rational specializations have b=0."""
    __slots__ = ('a', 'b')

    def __init__(self, a=0, b=0):
        self.a, self.b = Q(a), Q(b)

    def __bool__(self):
        return bool(self.a or self.b)

    def __add__(self, other):
        return _Eisenstein(self.a+other.a, self.b+other.b)

    def __sub__(self, other):
        return _Eisenstein(self.a-other.a, self.b-other.b)

    def __mul__(self, other):
        return _Eisenstein(self.a*other.a-self.b*other.b,
                           self.a*other.b+self.b*other.a-self.b*other.b)

    def __truediv__(self, other):
        norm = other.a**2-other.a*other.b+other.b**2
        return self*_Eisenstein((other.a-other.b)/norm, -other.b/norm)

    def serialize(self):
        return [str(self.a), str(self.b)]


def _specialize(laurent, coupling):
    result = {}
    roots = (_Eisenstein(1), _Eisenstein(0, 1), _Eisenstein(-1, -1))
    for momentum, polynomial in laurent.items():
        for key, value in polynomial.items():
            phase = roots[key[0] % 3] if coupling == 'zeta3' else _Eisenstein(Q(coupling)**key[0])
            monomial = (momentum, key[1:])
            result[monomial] = result.get(monomial, _Eisenstein())+_Eisenstein(value)*phase
    return {key: value for key, value in result.items() if value}


def _combination(columns, relation):
    result = {}
    for col, coefficient in relation.items():
        for key, value in columns[col].items():
            result[key] = result.get(key, _Eisenstein())+coefficient*value
            if not result[key]:
                del result[key]
    return result


def _rank(columns):
    """Sparse exact column elimination retaining both lower and upper witnesses."""
    pivots, relations, pivot_rows, pivot_cols = {}, [], [], []
    determinant = _Eisenstein(1)
    for index, column in enumerate(columns):
        remainder, representation = dict(column), {index: _Eisenstein(1)}
        for pivot, (basis, basis_representation) in pivots.items():
            if pivot not in remainder:
                continue
            coefficient = remainder[pivot]
            for key, value in basis.items():
                remainder[key] = remainder.get(key, _Eisenstein())-coefficient*value
                if not remainder[key]:
                    del remainder[key]
            for key, value in basis_representation.items():
                representation[key] = representation.get(key, _Eisenstein())-coefficient*value
                if not representation[key]:
                    del representation[key]
        if remainder:
            pivot = min(remainder)
            value = remainder[pivot]
            determinant = determinant*value
            pivots[pivot] = ({key: coefficient/value for key, coefficient in remainder.items()},
                             {key: coefficient/value for key, coefficient in representation.items()})
            pivot_rows.append(pivot)
            pivot_cols.append(index)
        else:
            relations.append(representation)
    nulls_verified = all(not _combination(columns, relation) for relation in relations)
    return {'rank': len(pivots), 'relations': relations, 'pivot_rows': pivot_rows,
            'pivot_cols': pivot_cols, 'minor_determinant': determinant,
            'nulls_verified': nulls_verified}


def _quadratic_columns():
    h1, h2, first_zero = dn._shell((1, 0, 0)), dn._shell((1, 1, 0)), dn._shell((-1, 0, 1))
    keys = sorted(first_zero)
    pairs = tuple(combinations_with_replacement(range(6), 2))
    functions, columns = [], []
    for i, j in pairs:
        basis = dn._laurent_multiply({keys[i]: first_zero[keys[i]]},
                                    {keys[j]: first_zero[keys[j]]})
        functions.append(basis)
        columns.append(dn._laurent_add(
            dn._laurent_multiply(h1, dn._bracket_numerator(basis, h2, 2, 1)),
            dn._laurent_multiply(h2, dn._bracket_numerator(h1, basis, 1, 2))))
    return h1, h2, functions, columns, pairs


def _serialize_rank(proof):
    return {'rank': proof['rank'], 'pivot_columns': proof['pivot_cols'],
            'pivot_rows': [[list(n), list(k)] for n, k in proof['pivot_rows']],
            'minor_determinant_in_Q_zeta': proof['minor_determinant'].serialize(),
            'null_relations': [[[index, coefficient.serialize()] for index, coefficient in sorted(relation.items())]
                               for relation in proof['relations']],
            'all_null_relations_replayed': proof['nulls_verified']}


def quadratic_boundary_receipt():
    """Classify the 21-product normalizer ansatz at every nonzero coupling.

    The global 21-minor in second_order_normalization_receipt can vanish
    only at 1,-1,-2,-3 and primitive cubic roots.  Exact full coefficient
    rank at these points completes the classification; -2,-3 are removed
    by nonzero alternate minors.  Cubic roots are evaluated in Q(zeta),
    never with floating point complex numbers.
    """
    h1, h2, functions, columns, pairs = _quadratic_columns()
    cases, checks = {}, {}
    global_minor = dn._polynomial_determinant(dn._minor_matrix(columns, dn._SECOND_MINOR_ROWS))
    checks['global_minor_factorization_replayed'] = global_minor == dn._second_minor_factor()
    for coupling in (-1, -2, -3, 'zeta3', 1):
        specialized = [_specialize(column, coupling) for column in columns]
        function_columns = [_specialize(function, coupling) for function in functions]
        operator_proof, function_proof = _rank(specialized), _rank(function_columns)
        images = [_combination(function_columns, relation) for relation in operator_proof['relations']]
        image_proof = _rank(images)
        key = str(coupling)
        cases[key] = {'operator': _serialize_rank(operator_proof),
                      'function_space': _serialize_rank(function_proof),
                      'nonzero_functional_freedom_dimension': image_proof['rank'],
                      'operator_null_function_image_term_counts': [len(image) for image in images]}
        checks[key+'_exact_rank_witnesses'] = (operator_proof['nulls_verified']
                                               and function_proof['nulls_verified']
                                               and bool(operator_proof['minor_determinant'])
                                               and bool(function_proof['minor_determinant']))
        if coupling == -1:
            # The unique nonzero functional freedom is an old commuting integral.
            target = {tuple(exponent-1 for exponent in n): polynomial
                      for n, polynomial in dn._laurent_multiply(h1, h2).items()}
            target = _specialize(target, -1)
            difference = dict(images[0])
            for monomial, value in target.items():
                difference[monomial] = difference.get(monomial, _Eisenstein())-value
                if not difference[monomial]:
                    del difference[monomial]
            checks['t_minus_one_freedom_is_existing_integral'] = not difference
            cases[key]['functional_generator'] = 'h1*h2/(y1*y2*y3)'
    expected = {'-1': (20, 21, 1), '-2': (21, 21, 0), '-3': (21, 21, 0),
                'zeta3': (19, 19, 0), '1': (0, 19, 19)}
    checks['complete_expected_rank_table'] = all(
        (cases[key]['operator']['rank'], cases[key]['function_space']['rank'],
         cases[key]['nonzero_functional_freedom_dimension']) == values
        for key, values in expected.items())
    return {'schema': 'perfectjet/dell-quadratic-boundary/1',
            'passed': all(checks.values()), 'checks': checks,
            'scope': {'particles': 3, 'coordinate_nome': 0, 'momentum_nome_order': 2,
                      'all_nonzero_couplings_classified_with_global_minor': True,
                      'all_order_integrability_claim': False,
                      'global_normalizer_uniqueness_claim': False},
            'basis_pairs': [list(pair) for pair in pairs],
            'global_minor_reference': 'dell_normalization.second_order_normalization_receipt',
            'cases': cases,
            'complete_classification':
                'For t!=0,1,-1, rho2=0 as a function; primitive cubic roots have only '
                'parameter redundancies. For t=-1, rho2=c*h1*h2/(y1*y2*y3). '
                'For t=1, the represented function space has dimension19 and every element is allowed.',
            'priority': 'new to the project; worldwide novelty not established'}
