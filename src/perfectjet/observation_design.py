"""Exact design of coefficient-observation panels for polynomial response spaces."""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import combinations


def _rational_polynomial(poly):
    if not isinstance(poly, dict):
        raise ValueError("polynomials must be degree->coefficient dictionaries")
    out = {}
    for degree, coefficient in poly.items():
        if type(degree) is not int or degree < 0:
            raise ValueError("polynomial degrees must be nonnegative integers")
        if isinstance(coefficient, bool) or not isinstance(coefficient, (int, str, Q)):
            raise ValueError("coefficients must be exact integers/rationals")
        value = Q(coefficient)
        if value:
            out[degree] = value
    return out


def coefficient_matrix(polynomials, panel):
    polys = [_rational_polynomial(p) for p in polynomials]
    panel = tuple(panel)
    if len(panel) != len(polys) or len(set(panel)) != len(panel):
        raise ValueError("panel must contain one distinct degree per response polynomial")
    if any(type(d) is not int or d < 0 for d in panel):
        raise ValueError("panel degrees must be distinct nonnegative integers")
    return [[p.get(degree, Q(0)) for p in polys] for degree in panel]


def invert_with_determinant(matrix):
    rows = [[Q(x) for x in row] for row in matrix]
    n = len(rows)
    if not n or any(len(row) != n for row in rows):
        raise ValueError("square nonempty matrix required")
    rows = [row + [Q(i == j) for j in range(n)] for i, row in enumerate(rows)]
    det = Q(1)
    for column in range(n):
        pivot = next((i for i in range(column, n) if rows[i][column]), None)
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            det = -det
        value = rows[column][column]
        det *= value
        rows[column] = [x/value for x in rows[column]]
        for i in range(n):
            if i != column and rows[i][column]:
                value = rows[i][column]
                rows[i] = [x-value*y for x, y in zip(rows[i], rows[column])]
    return [row[n:] for row in rows], det


def inverse_infinity_norm(inverse):
    return max(sum(abs(Q(x)) for x in row) for row in inverse)


def optimize_coefficient_panel(polynomials, names=None):
    """Exhaust all distinct coefficient evaluations and minimize ||M^-1||_infinity.

    The optimization domain is exactly the union of degrees appearing in the
    supplied response polynomials, with no row rescaling and equal absolute
    error assigned to every selected coefficient.
    """
    polys = [_rational_polynomial(p) for p in polynomials]
    if not polys:
        raise ValueError("at least one response polynomial is required")
    dimension = len(polys)
    if names is not None and len(names) != dimension:
        raise ValueError("names length differs from response dimension")
    degrees = sorted(set().union(*(p.keys() for p in polys)))
    if len(degrees) < dimension:
        raise ValueError("too few candidate degrees for a square observation panel")

    total = nonsingular = ties = 0
    best = None
    for panel in combinations(degrees, dimension):
        total += 1
        try:
            inverse, det = invert_with_determinant(coefficient_matrix(polys, panel))
        except ValueError:
            continue
        nonsingular += 1
        gain = inverse_infinity_norm(inverse)
        candidate = (gain, panel, det, inverse)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
            ties = 1
        elif gain == best[0]:
            ties += 1

    if best is None:
        raise ValueError("no invertible coefficient panel exists")
    gain, panel, det, inverse = best
    return {
        "schema": "perfectjet/coefficient-panel/1",
        "dimension": dimension,
        "coordinate_names": list(names) if names is not None else None,
        "candidate_degrees": degrees,
        "subsets_checked": total,
        "invertible": nonsingular,
        "optimal_panel": list(panel),
        "optimal_determinant": str(det),
        "inverse_infinity_norm": str(gain),
        "optimal_ties": ties,
        "inverse": [[str(x) for x in row] for row in inverse],
        "objective": "minimize exact ||M^-1||_infinity for equal unscaled coefficient errors",
        "scope": "Global only within distinct single-coefficient observations from the supplied degree support; arbitrary rational linear sensors are a larger design problem.",
    }
