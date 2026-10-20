"""Exact recoupling and higher-structure boundaries for Asterion calculus.

The numerical engines use rational arithmetic, including half-integral spins.
Normalized Wigner symbols are represented by their sign and rational square;
the actual change of polynomial coupling coordinates is a rational matrix.
No floating square root is substituted for exact angular-momentum arithmetic.

Sources: NIST DLMF 34.4 (Racah sum and 4F3), 34.5 (orthogonality);
the current-form DGLA is the standard tensor construction g tensor A for a
commutative differential graded algebra A.  The E8 symmetric-square boundary
is checked by a highest-weight raising-map certificate, not a dimension guess.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, product
from math import comb, factorial, gcd, lcm


def _q(value):
    if isinstance(value, (float, bool)):
        raise ValueError('exact rational input required')
    try:
        return Q(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError('exact rational input required') from exc


def _spin(value):
    value = _q(value)
    if value < 0 or value.denominator not in (1, 2):
        raise ValueError('nonnegative integer or half-integer spin required')
    if value > 100:
        raise ValueError('spin exceeds the exact engine bound of 100')
    return value


def _integer(value):
    value = Q(value)
    if value.denominator != 1:
        raise ValueError('an integral factorial or transvection order was required')
    return value.numerator


def _sign(integer):
    return -1 if _integer(integer) % 2 else 1


def _json(value):
    if isinstance(value, Q):
        return value.numerator if value.denominator == 1 else str(value)
    if isinstance(value, dict):
        return {str(k): _json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json(v) for v in value]
    return value


def admissible(a, b, c):
    a, b, c = map(_spin, (a, b, c))
    return abs(a - b) <= c <= a + b and (a + b + c).denominator == 1


@lru_cache(maxsize=None)
def allowed_spins(a, b):
    a, b = map(_spin, (a, b))
    start = abs(a - b)
    return tuple(start + i for i in range(_integer(a + b - start) + 1))


def terminating_4f3(upper, lower, *, argument=1, max_terms=10000):
    """Evaluate an exact finite 4F3, stopping at its first upper termination.

    A denominator pole before the last retained term is rejected.  A pole
    occurring only after termination is never evaluated.  ``balanced`` means
    sum(lower)-sum(upper)=1; the engine also evaluates unbalanced finite sums.
    """
    if len(upper) != 4 or len(lower) != 3:
        raise ValueError('4 upper and 3 lower parameters required')
    upper, lower = tuple(map(_q, upper)), tuple(map(_q, lower))
    argument = _q(argument)
    stops = [-x.numerator for x in upper if x.denominator == 1 and x <= 0]
    if not stops:
        raise ValueError('at least one nonpositive integral upper parameter must terminate the sum')
    last = min(stops)
    if isinstance(max_terms, bool) or not isinstance(max_terms, int) or last + 1 > max_terms:
        raise ValueError('terminating series exceeds max_terms')
    term = total = Q(1)
    terms = [term]
    for k in range(last):
        numerator = argument
        denominator = Q(k + 1)
        for parameter in upper:
            numerator *= parameter + k
        for parameter in lower:
            denominator *= parameter + k
        if not denominator:
            raise ValueError('denominator pole before termination')
        term *= numerator / denominator
        total += term
        terms.append(term)
    return {'value': total, 'terms': tuple(terms), 'term_count': last + 1,
            'balanced': sum(lower, Q(0)) - sum(upper, Q(0)) == 1,
            'upper': upper, 'lower': lower, 'argument': argument}


@lru_cache(maxsize=None)
def triangle_square(a, b, c):
    """The rational square of the usual triangle coefficient Delta(a,b,c)."""
    a, b, c = map(_spin, (a, b, c))
    if not admissible(a, b, c):
        return Q(0)
    return Q(factorial(_integer(a + b - c)) * factorial(_integer(a - b + c))
             * factorial(_integer(-a + b + c)), factorial(_integer(a + b + c + 1)))


@lru_cache(maxsize=None)
def _wigner_6j_cached(a, b, e, c, d, f):
    """Return exact sign and rational square of {a b e; c d f}.

    The factorial Racah sum is independently evaluated as a terminating
    balanced 4F3 at one.  The representation ``sign*sqrt(square)`` retains
    irrational symbols without introducing approximate radicals.
    """
    a, b, e, c, d, f = map(_spin, (a, b, e, c, d, f))
    triangles = ((a, b, e), (a, d, f), (c, b, f), (c, d, e))
    if not all(admissible(*t) for t in triangles):
        return {'sign': 0, 'square': Q(0), 'admissible': False,
                'racah_sum': Q(0), 'hypergeometric_replay': True}
    prefactor = Q(1)
    for triangle in triangles:
        prefactor *= triangle_square(*triangle)
    lower_bounds = tuple(_integer(x) for x in (a + b + e, a + d + f, c + b + f, c + d + e))
    upper_bounds = tuple(_integer(x) for x in (a + b + c + d, a + c + e + f, b + d + e + f))
    lo, hi = max(lower_bounds), min(upper_bounds)
    values = []
    for z in range(lo, hi + 1):
        denominator = 1
        for t in lower_bounds:
            denominator *= factorial(z - t)
        for u in upper_bounds:
            denominator *= factorial(u - z)
        values.append(Q(_sign(z) * factorial(z + 1), denominator))
    racah = sum(values, Q(0))
    lower = [Q(lo - t + 1) for t in lower_bounds]
    lower.remove(Q(1))  # this factor is the k! in the hypergeometric series
    upper = [Q(lo + 2)] + [Q(lo - u) for u in upper_bounds]
    hyper = terminating_4f3(upper, lower)
    if not hyper['balanced'] or values[0] * hyper['value'] != racah:
        raise ArithmeticError('Racah/terminating-balanced-4F3 disagreement')
    square = prefactor * racah * racah
    return {'sign': (1 if racah > 0 else -1 if racah < 0 else 0),
            'square': square, 'admissible': True, 'triangle_product_square': prefactor,
            'racah_sum': racah, 'racah_range': (lo, hi),
            'hypergeometric_upper': tuple(upper), 'hypergeometric_lower': tuple(lower),
            'hypergeometric_value': hyper['value'], 'hypergeometric_term_count': hyper['term_count'],
            'hypergeometric_balanced': True, 'hypergeometric_replay': True}


def wigner_6j(a, b, e, c, d, f):
    """Public copy of the exact cached sign/square/Racah record."""
    return dict(_wigner_6j_cached(a, b, e, c, d, f))


def wigner_6j_squared(*spins):
    return wigner_6j(*spins)['square']


def _falling(n, k):
    return factorial(n) // factorial(n - k) if 0 <= k <= n else 0


@lru_cache(maxsize=None)
def transvectant_coefficient(a, i, b, j, c):
    """Coefficient in binomial monomials for H_2a tensor H_2b -> H_2c."""
    a, b, c = map(_spin, (a, b, c))
    if not admissible(a, b, c):
        return Q(0)
    na, nb, nc = map(_integer, (2 * a, 2 * b, 2 * c))
    if not 0 <= i <= na or not 0 <= j <= nb:
        return Q(0)
    r = _integer(a + b - c)
    output = i + j - r
    if not 0 <= output <= nc:
        return Q(0)
    value = sum(_sign(k) * comb(r, k) * _falling(na - i, r - k)
                * _falling(i, k) * _falling(nb - j, k) * _falling(j, r - k)
                for k in range(max(0, r - j, r - (na - i)), min(r, i, nb - j) + 1))
    return Q(comb(na, i) * comb(nb, j) * value, comb(nc, output))


@lru_cache(maxsize=None)
def transvectant_norm(a, b, c):
    """Squared adjoint norm on a highest vector with binomial norm binom(n,i)."""
    a, b, c = map(_spin, (a, b, c))
    if not admissible(a, b, c):
        return Q(0)
    r = _integer(a + b - c)
    na, nb = _integer(2 * a), _integer(2 * b)
    return sum((transvectant_coefficient(a, i, b, r - i, c) ** 2
                / (comb(na, i) * comb(nb, r - i))
                for i in range(max(0, r - nb), min(na, r) + 1)), Q(0))


def _inverse(matrix):
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError('square matrix required')
    rows = [[Q(x) for x in row] + [Q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for c in range(n):
        pivot = next((r for r in range(c, n) if rows[r][c]), None)
        if pivot is None:
            raise ValueError('singular interpolation matrix')
        rows[c], rows[pivot] = rows[pivot], rows[c]
        divisor = rows[c][c]
        rows[c] = [x / divisor for x in rows[c]]
        for r in range(n):
            if r != c and rows[r][c]:
                z = rows[r][c]
                rows[r] = [x - z * y for x, y in zip(rows[r], rows[c])]
    return [row[n:] for row in rows]


def _multiply(a, b):
    return [[sum((x * y for x, y in zip(row, column)), Q(0)) for column in zip(*b)] for row in a]


def _independent_insert(rows, vector):
    vector = list(map(Q, vector))
    for pivot, row in rows:
        if vector[pivot]:
            z = vector[pivot]
            vector = [x - z * y for x, y in zip(vector, row)]
    pivot = next((i for i, x in enumerate(vector) if x), None)
    if pivot is None:
        return False
    divisor = vector[pivot]
    rows.append((pivot, [x / divisor for x in vector]))
    return True


def _highest_inputs(spins, total):
    degrees = [_integer(2 * _spin(s)) for s in spins]
    weight = _integer(sum(map(_spin, spins), Q(0)) - _spin(total))
    if weight < 0:
        return
    def generate(prefix, remaining):
        position = len(prefix)
        if position == len(degrees) - 1:
            if 0 <= remaining <= degrees[position]:
                yield tuple(prefix + [remaining])
            return
        for i in range(max(0, remaining - sum(degrees[position + 1:])), min(degrees[position], remaining) + 1):
            yield from generate(prefix + [i], remaining - i)
    yield from generate([], weight)


@lru_cache(maxsize=256)
def _recoupling_cached(a, b, c, d):
    """Exact rational L_e=sum_f C[e,f]R_f between two transvectant trees.

    L_e=T(T(P_a,Q_b),R_c), R_f=T(P_a,T(Q_b,R_c)).  Interpolation uses the
    highest-output functional; equivariance makes it determine the entire
    intertwiner.  All its input coefficients are independently replayed.
    """
    a, b, c, d = map(_spin, (a, b, c, d))
    left = tuple(e for e in allowed_spins(a, b) if admissible(e, c, d))
    right = tuple(f for f in allowed_spins(b, c) if admissible(a, f, d))
    if len(left) != len(right) or not left:
        raise ValueError('no nonzero triple tensor coupling to the requested output spin')
    if len(left) > 64:
        raise ValueError('recoupling multiplicity exceeds the exact interpolation bound of 64')
    samples = []
    independent = []
    left_rows, right_rows = [], []
    all_rows = []
    for i, j, k in _highest_inputs((a, b, c), d):
        lv = [transvectant_coefficient(a, i, b, j, e)
              * transvectant_coefficient(e, i + j - _integer(a + b - e), c, k, d) for e in left]
        rv = [transvectant_coefficient(b, j, c, k, f)
              * transvectant_coefficient(a, i, f, j + k - _integer(b + c - f), d) for f in right]
        all_rows.append((lv, rv))
        if len(samples) < len(left) and _independent_insert(independent, rv):
            samples.append((i, j, k))
            left_rows.append(lv)
            right_rows.append(rv)
    if len(samples) != len(left):
        raise ArithmeticError('right coupling maps did not span their stated multiplicity')
    # At selected inputs, L=R*C^T.
    transpose = _multiply(_inverse(right_rows), left_rows)
    coefficients = tuple(tuple(row) for row in zip(*transpose))
    inverse = tuple(tuple(row) for row in _inverse(coefficients))
    for lv, rv in all_rows:
        if list(lv) != [sum((x * y for x, y in zip(row, rv)), Q(0)) for row in coefficients]:
            raise ArithmeticError('recoupling interpolation failed an unused highest-weight input')
    left_norms = tuple(transvectant_norm(a, b, e) * transvectant_norm(e, c, d) for e in left)
    right_norms = tuple(transvectant_norm(b, c, f) * transvectant_norm(a, f, d) for f in right)
    for i in range(len(left)):
        for j in range(len(left)):
            inner = sum((coefficients[i][f] * coefficients[j][f] * right_norms[f]
                         for f in range(len(right))), Q(0))
            if inner != (left_norms[i] if i == j else 0):
                raise ArithmeticError('rational weighted recoupling orthogonality failed')
    checks = 0
    for i, e in enumerate(left):
        for j, f in enumerate(right):
            normalized_square = coefficients[i][j] ** 2 * right_norms[j] / left_norms[i]
            if normalized_square != (2 * e + 1) * (2 * f + 1) * wigner_6j_squared(a, b, e, c, d, f):
                raise ArithmeticError('polynomial recoupling and independent Racah 6j square disagree')
            checks += 1
    return {'spins': (a, b, c, d), 'left_intermediates': left, 'right_intermediates': right,
            'coefficients': coefficients, 'inverse': inverse,
            'left_norms': left_norms, 'right_norms': right_norms,
            'interpolation_samples': tuple(samples), 'highest_input_checks': len(all_rows),
            'weighted_orthogonality_checks': len(left) ** 2, 'six_j_square_checks': checks,
            'passed': True}


def recoupling_matrix(a, b, c, d):
    """Public copy of the exact cached rational recoupling certificate."""
    return dict(_recoupling_cached(a, b, c, d))


def compile_jacobi_constraints(a, b, c, d, *, sectors=None):
    """Sparse quadratic Jacobi equations in principal transvectant couplings.

    Every admissible (a,b) intermediate is retained as an equation coordinate,
    even when that spin is absent from ``sectors``.  Only actual bracket
    channels have unknown coefficients.  Missing equation coordinates are
    precisely the unjustified truncation this compiler prevents.
    """
    if sectors is None:
        from .asterion_principal import EXPONENTS
        sectors = EXPONENTS
    sectors = tuple(sorted(set(map(_spin, sectors))))
    a, b, c, d = map(_spin, (a, b, c, d))
    if any(spin not in sectors for spin in (a, b, c, d)):
        raise ValueError('external Jacobi spins must be retained sectors')
    normal = recoupling_matrix(a, b, c, d)
    rotated = recoupling_matrix(c, a, b, d)
    left, right = normal['left_intermediates'], normal['right_intermediates']
    rows = [dict() for _ in left]
    def variable(x, y, z):
        sign = 1
        if x == y and _sign(x + y - z) == 1:
            # A symmetric transvectant cannot define an ordinary Lie bracket
            # on two inputs from the same multiplicity-one module.
            return (x, y, z), 0
        if x > y:
            sign = _sign(x + y - z + 1)
            x, y = y, x
        return (x, y, z), sign
    def add(row_index, coefficient, first, second):
        first, s1 = variable(*first)
        second, s2 = variable(*second)
        monomial = tuple(sorted((first, second)))
        value = rows[row_index].get(monomial, Q(0)) + coefficient * s1 * s2
        if value:
            rows[row_index][monomial] = value
        else:
            rows[row_index].pop(monomial, None)
    for i, e in enumerate(left):
        if e in sectors:
            add(i, Q(1), (a, b, e), (e, c, d))
    for j, f in enumerate(right):
        if f in sectors:
            phase = _sign(f + a - d)
            for i in range(len(left)):
                add(i, phase * normal['inverse'][j][i], (b, c, f), (f, a, d))
    rotated_right = {spin: i for i, spin in enumerate(rotated['right_intermediates'])}
    for j, g in enumerate(rotated['left_intermediates']):
        if g in sectors:
            for i, e in enumerate(left):
                coefficient = rotated['coefficients'][j][rotated_right[e]] * _sign(c + e - d)
                add(i, coefficient, (c, a, g), (g, b, d))
    return {'external_spins': (a, b, c, d), 'sectors': sectors,
            'equation_intermediates': left,
            'outside_sector_intermediates': tuple(e for e in left if e not in sectors),
            'equations': tuple(tuple(sorted(row.items())) for row in rows),
            'nonzero_equations': sum(bool(row) for row in rows),
            'quadratic_terms': sum(map(len, rows)),
            'scope': 'All admissible intermediate equation coordinates; absent bracket sectors are zero, not discarded equations.'}


def evaluate_jacobi_constraints(compiled, couplings):
    values = []
    for row in compiled['equations']:
        values.append(sum((coefficient * Q(couplings.get(tuple(monomial[0]), 0))
                           * Q(couplings.get(tuple(monomial[1]), 0))
                           for monomial, coefficient in row), Q(0)))
    return {'passed': not any(values), 'residuals': tuple(values),
            'equations_checked': len(values), 'outside_sector_equations': len(compiled['outside_sector_intermediates'])}


def linearized_jacobi_rows(compiled, couplings, *, fixed_principal=True, relative=True):
    """Sparse exact Jacobian rows of the compiled quadratic equations.

    Relative coordinates mean kappa_v(t)=kappa_v*(1+t*eta_v).  They are
    invertible tangent coordinates when all selected couplings are nonzero.
    Each row is scaled to primitive integers, preserving its rational span.
    """
    variables = tuple(sorted(v for v in couplings if not fixed_principal or v[0] != 1))
    positions = {tuple(v): i for i, v in enumerate(variables)}
    if relative and any(not couplings[v] for v in variables):
        raise ValueError('relative tangent coordinates require nonzero selected couplings')
    rows, row_scales = [], []
    for equation in compiled['equations']:
        row = {}
        for (a, b), coefficient in equation:
            for variable, other in ((a, b), (b, a)):
                variable, other = tuple(variable), tuple(other)
                if variable in positions:
                    value = coefficient * Q(couplings.get(other, 0))
                    if relative:
                        value *= Q(couplings[variable])
                    index = positions[variable]
                    row[index] = row.get(index, Q(0)) + value
                    if not row[index]:
                        del row[index]
        if row:
            denominator = lcm(*(x.denominator for x in row.values()))
            common = gcd(*(abs(int(x * denominator)) for x in row.values()))
            scale = Q(denominator, common)
            if row[min(row)] < 0:
                scale = -scale
            row = {i: value * scale for i, value in row.items()}
        else:
            scale = Q(1)
        rows.append(tuple(sorted(row.items())))
        row_scales.append(scale)
    return {'variables': variables, 'rows': tuple(rows),
            'row_scales': tuple(row_scales),
            'fixed_principal': fixed_principal, 'relative_tangent_coordinates': relative,
            'normalization': 'primitive integer rows; nonzero first coordinate positive',
            'scope': 'Actually computed exact Jacobian rows for the supplied recoupling problem.'}


def jacobi_constraint_receipt(spins=(7, 11, 13, 17), *, couplings=None, include_equations=False):
    """Exact polynomial-equation rank, including the loss from naive truncation."""
    from .exact import rank, nullspace
    if couplings is None:
        from .asterion_principal import PrincipalE8
        couplings = PrincipalE8().couplings()
    compiled = compile_jacobi_constraints(*spins)
    monomials = tuple(sorted({m for row in compiled['equations'] for m, _ in row}))
    rows = [dict(row) for row in compiled['equations']]
    matrix = [[row.get(m, Q(0)) for m in monomials] for row in rows]
    inside = [row for e, row in zip(compiled['equation_intermediates'], matrix)
              if e in compiled['sectors']]
    full_rank = rank(matrix, len(monomials))
    retained_rank = rank(inside, len(monomials))
    lost_witness = next((v for v in nullspace(inside, len(monomials))
        if any(sum((x * y for x, y in zip(row, v)), Q(0)) for row in matrix)), None)
    products = [Q(couplings.get(tuple(m[0]), 0)) * Q(couplings.get(tuple(m[1]), 0)) for m in monomials]
    kernel = nullspace(matrix, len(monomials))
    one_dimensional_match = None
    if len(kernel) == 1:
        index = next(i for i, x in enumerate(kernel[0]) if x)
        scale = products[index] / kernel[0][index]
        one_dimensional_match = products == [scale * x for x in kernel[0]]
    result = {'external_spins': tuple(map(Q, spins)),
        'equation_intermediates': compiled['equation_intermediates'],
        'outside_sector_intermediates': compiled['outside_sector_intermediates'],
        'quadratic_monomials': monomials, 'quadratic_monomial_count': len(monomials),
        'full_polynomial_equation_rank': full_rank,
        'retained_sector_equation_rank': retained_rank,
        'independent_constraints_lost_by_truncation': full_rank - retained_rank,
        'monomial_coordinate_kernel_dimension': len(monomials) - full_rank,
        'actual_coupling_products_match_one_dimensional_kernel': one_dimensional_match,
        'omitted_constraint_witness': lost_witness,
        'evaluation': evaluate_jacobi_constraints(compiled, couplings),
        'scope': 'Rank of exact quadratic polynomial equations in distinct coupling monomials; not a classification of all nonlinear coupling solutions.'}
    if include_equations:
        result['compiled_equations'] = compiled
    return result


def _decorated_trees(shape, spins):
    if isinstance(shape, int):
        return [(shape, _spin(spins[shape]))]
    left, right = shape
    out = []
    for ltree, a in _decorated_trees(left, spins):
        for rtree, b in _decorated_trees(right, spins):
            for c in allowed_spins(a, b):
                out.append(((ltree, rtree, c), c))
    return out


def _tree_value(tree, spins, indices):
    if isinstance(tree, int):
        return Q(1), _spin(spins[tree]), indices[tree]
    left, right, c = tree
    x, a, i = _tree_value(left, spins, indices)
    y, b, j = _tree_value(right, spins, indices)
    return x * y * transvectant_coefficient(a, i, b, j, c), c, i + j - _integer(a + b - c)


def _tree_change(left_trees, right_trees, spins, total):
    independent, left_rows, right_rows, all_rows = [], [], [], []
    n = len(left_trees)
    for indices in _highest_inputs(spins, total):
        left = [_tree_value(tree, spins, indices)[0] for tree in left_trees]
        right = [_tree_value(tree, spins, indices)[0] for tree in right_trees]
        all_rows.append((left, right))
        if len(left_rows) < n and _independent_insert(independent, right):
            left_rows.append(left)
            right_rows.append(right)
    if len(left_rows) != n:
        raise ArithmeticError('decorated tree maps failed to span')
    matrix = [list(row) for row in zip(*_multiply(_inverse(right_rows), left_rows))]
    for left, right in all_rows:
        if left != [sum((x * y for x, y in zip(row, right)), Q(0)) for row in matrix]:
            raise ArithmeticError('tree associator failed an unused input coefficient')
    return matrix, len(all_rows)


def pentagon_receipt(spins=(Q(1, 2),) * 4, total=1):
    """Check both associator paths through all five four-input binary trees."""
    spins = tuple(map(_spin, spins))
    total = _spin(total)
    if len(spins) != 4 or any(s > 3 for s in spins):
        raise ValueError('four spins at most 3 required for bounded pentagon replay')
    shapes = ((((0, 1), 2), 3), ((0, (1, 2)), 3),
              (0, ((1, 2), 3)), (0, (1, (2, 3))), ((0, 1), (2, 3)))
    trees = [tuple(tree for tree, s in _decorated_trees(shape, spins) if s == total) for shape in shapes]
    n = len(trees[0])
    if not n or any(len(t) != n for t in trees) or n > 64:
        raise ValueError('unsupported or absent pentagon multiplicity')
    edges = {}
    checks = 0
    for a, b in ((0, 1), (1, 2), (2, 3), (0, 4), (4, 3), (0, 3)):
        edges[a, b], count = _tree_change(trees[a], trees[b], spins, total)
        checks += count
    long_path = _multiply(_multiply(edges[0, 1], edges[1, 2]), edges[2, 3])
    short_path = _multiply(edges[0, 4], edges[4, 3])
    passed = long_path == short_path == edges[0, 3]
    return {'input_spins': spins, 'output_spin': total, 'multiplicity': n,
            'binary_parenthesizations': 5, 'intertwiner_input_checks': checks,
            'edge_matrices': [{'from': a, 'to': b, 'matrix': matrix} for (a, b), matrix in edges.items()],
            'long_path_matrix': long_path, 'short_path_matrix': short_path,
            'direct_matrix': edges[0, 3], 'passed': passed,
            'scope': 'Exact rational polynomial intertwiners; ordinary representation associativity, not a new quantum associator.'}


def _add(target, source, scale=1):
    for key, value in source.items():
        target[key] = target.get(key, Q(0)) + scale * value
        if not target[key]:
            target.pop(key, None)
    return target


def _sl2(left, right):
    table = {(0, 1): {1: Q(2)}, (0, 2): {2: Q(-2)}, (1, 2): {0: Q(1)}}
    out = {}
    for i, x in left.items():
        for j, y in right.items():
            if i < j:
                _add(out, table[i, j], x * y)
            elif i > j:
                _add(out, table[j, i], -x * y)
    return out


class CurrentFormDGLA:
    """g tensor Q[t,dt]/(t^(N+1),t^N dt), with d(t^k)=k*t^(k-1)dt.

    The differential ideal is explicit: differentiating t^(N+1) gives the
    killed relation (N+1)t^Ndt.  Merely discarding high polynomial degrees
    without this second relation would fail to define this DGA.
    """
    def __init__(self, order=2, *, lie_dimension=3, lie_bracket=None):
        if isinstance(order, bool) or not isinstance(order, int) or not 1 <= order <= 8:
            raise ValueError('current-form order must be an integer in 1..8')
        if isinstance(lie_dimension, bool) or not isinstance(lie_dimension, int) or lie_dimension < 1:
            raise ValueError('positive Lie dimension required')
        self.order = order
        self.lie_dimension = lie_dimension
        self.lie_bracket = lie_bracket or _sl2
        if lie_bracket is None and lie_dimension != 3:
            raise ValueError('supply the bracket for a Lie algebra other than sl2')
        self.labels = tuple((i, power, degree) for degree in (0, 1)
            for power in range(order + 1 - degree) for i in range(lie_dimension))
        self.dimension = len(self.labels)

    def _vector(self, vector):
        if not hasattr(vector, 'items'):
            raise ValueError('sparse current-form vector required')
        out = {}
        for label, value in vector.items():
            if (not isinstance(label, tuple) or len(label) != 3
                    or any(isinstance(x, bool) or not isinstance(x, int) for x in label)):
                raise ValueError('current-form label must be (Lie index, power, form degree)')
            i, power, degree = label
            if not 0 <= i < self.lie_dimension or degree not in (0, 1) or not 0 <= power <= self.order - degree:
                raise ValueError('current-form label outside the finite quotient')
            value = _q(value)
            if value:
                out[label] = value
        return out

    def degree(self, label):
        return label[2]

    def differential(self, vector):
        return {(i, power - 1, 1): Q(value) * power for (i, power, degree), value in self._vector(vector).items()
                if degree == 0 and power and value}

    def homotopy(self, vector):
        return {(i, power + 1, 0): Q(value, power + 1) for (i, power, degree), value in self._vector(vector).items()
                if degree == 1 and value}

    def project(self, vector):
        return {i: Q(value) for (i, power, degree), value in self._vector(vector).items() if not power and not degree and value}

    def include(self, vector):
        out = {}
        for i, value in vector.items():
            if isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < self.lie_dimension:
                raise ValueError('Lie coordinate outside the current algebra')
            value = _q(value)
            if value:
                out[i, 0, 0] = value
        return out

    def bracket(self, left, right):
        out = {}
        left, right = self._vector(left), self._vector(right)
        for (i, p, degree), x in left.items():
            for (j, q, other_degree), y in right.items():
                r = degree + other_degree
                if r > 1 or p + q > self.order - r:
                    continue
                for k, z in self.lie_bracket({i: Q(1)}, {j: Q(1)}).items():
                    key = (k, p + q, r)
                    out[key] = out.get(key, Q(0)) + Q(x) * Q(y) * z
                    if not out[key]:
                        del out[key]
        return out

    def transfer_binary(self, left, right):
        return self.project(self.bracket(self.include(left), self.include(right)))

    def verify(self, *, max_triples=100000):
        if self.dimension ** 3 > max_triples:
            raise ValueError('full graded Jacobi replay exceeds max_triples')
        units = [{label: Q(1)} for label in self.labels]
        for label, vector in zip(self.labels, units):
            if self.differential(self.differential(vector)):
                raise ArithmeticError('d squared is nonzero')
            lhs = self.differential(self.homotopy(vector))
            _add(lhs, self.homotopy(self.differential(vector)))
            rhs = _add(dict(vector), self.include(self.project(vector)), -1)
            if lhs != rhs:
                raise ArithmeticError('dh+hd=id-ip contraction failed')
            if (self.homotopy(self.homotopy(vector)) or self.project(self.homotopy(vector))
                    or self.project(self.differential(vector))):
                raise ArithmeticError('contraction side conditions failed')
        for a, x in zip(self.labels, units):
            for b, y in zip(self.labels, units):
                lhs = self.bracket(x, y)
                _add(lhs, self.bracket(y, x), _sign(a[2] * b[2]))
                if lhs:
                    raise ArithmeticError('graded skew symmetry failed')
                lhs = self.differential(self.bracket(x, y))
                rhs = self.bracket(self.differential(x), y)
                _add(rhs, self.bracket(x, self.differential(y)), _sign(a[2]))
                if lhs != rhs:
                    raise ArithmeticError('differential graded Leibniz rule failed')
                for c, z in zip(self.labels, units):
                    result = {}
                    for first, second, third, p, q in ((x, y, z, a[2], c[2]),
                            (y, z, x, b[2], a[2]), (z, x, y, c[2], b[2])):
                        _add(result, self.bracket(first, self.bracket(second, third)), _sign(p * q))
                    if result:
                        raise ArithmeticError('graded Jacobi failed')
        higher_vanishes = all(not self.homotopy(self.bracket(self.include({i: 1}), self.include({j: 1})))
            for i in range(self.lie_dimension) for j in range(self.lie_dimension))
        return {'passed': True, 'dimension': self.dimension, 'degree_zero_dimension': self.lie_dimension * (self.order + 1),
            'degree_one_dimension': self.lie_dimension * self.order,
            'differential_rank': self.lie_dimension * self.order,
            'cohomology_dimension': self.lie_dimension,
            'd_squared_and_contraction_columns': self.dimension,
            'contraction_side_conditions': 'h^2=0, p*h=0, h*i=0, p*i=id, d*i=0, p*d=0',
            'graded_skew_and_leibniz_pairs': self.dimension ** 2,
            'graded_jacobi_triples': self.dimension ** 3,
            'all_transferred_brackets_arity_at_least_three_vanish': higher_vanishes,
            'all_order_reason': 'Every rooted transfer tree has a lowest binary vertex followed by h; h of a constant current bracket is zero.',
            'scope': 'A genuine finite current-form DGLA and contraction. This formal example has strict transferred Lie structure; it does not exhibit a nonzero higher bracket.'}


def e8_symmetric_square_obstruction(algebra=None):
    """Certify Hom_E8(Sym^2(E8),E8)=0 by a highest-weight raising matrix."""
    from .asterion_e8 import E8LieAlgebra
    from .exact import rank, nullspace
    g = algebra or E8LieAlgebra()
    zero = (0,) * 8
    weights = [zero] * 8 + list(g.roots)
    theta = max(g.roots, key=lambda root: sum(root))
    columns = [(i, j) for i in range(248) for j in range(i, 248)
               if tuple(x + y for x, y in zip(weights[i], weights[j])) == theta]
    images = []
    row_keys = set()
    for i, j in columns:
        out = {}
        for simple in range(8):
            for k, value in g.bracket(g.simple_e(simple), {i: Q(1)}).items():
                key = (simple, min(k, j), max(k, j))
                out[key] = out.get(key, Q(0)) + value
            for k, value in g.bracket(g.simple_e(simple), {j: Q(1)}).items():
                key = (simple, min(i, k), max(i, k))
                out[key] = out.get(key, Q(0)) + value
        out = {key: value for key, value in out.items() if value}
        row_keys.update(out)
        images.append(out)
    row_keys = sorted(row_keys)
    matrix = [[column.get(row, Q(0)) for column in images] for row in row_keys]
    matrix_rank = rank(matrix, len(columns))
    kernel = nullspace(matrix, len(columns))
    return {'symmetric_square_dimension': comb(249, 2),
        'adjoint_highest_weight': theta, 'adjoint_highest_weight_space_dimension': len(columns),
        'raising_matrix_shape': [len(row_keys), len(columns)],
        'raising_matrix_rank': matrix_rank, 'highest_vector_kernel_dimension': len(kernel),
        'no_adjoint_summand': not kernel, 'passed': not kernel,
        'columns': columns, 'rows': row_keys, 'raising_matrix': matrix,
        'scope': 'Complete reducibility in characteristic zero identifies adjoint multiplicity with this highest-vector kernel; no copy of the adjoint occurs in Sym^2(E8).'}


def verify_symmetric_square_certificate(record, algebra=None):
    """Rebuild the actual highest-weight map and reject altered rank evidence."""
    if not isinstance(record, dict):
        return {'valid': False, 'reason': 'certificate must be a mapping'}
    expected = e8_symmetric_square_obstruction(algebra)
    try:
        matrix = [[_q(x) for x in row] for row in record['raising_matrix']]
        if matrix != expected['raising_matrix']:
            return {'valid': False, 'reason': 'raising matrix differs from the E8 symmetric-square action'}
        for key in ('symmetric_square_dimension', 'adjoint_highest_weight',
                'adjoint_highest_weight_space_dimension', 'raising_matrix_shape', 'raising_matrix_rank',
                'highest_vector_kernel_dimension', 'no_adjoint_summand', 'columns', 'rows'):
            if _json(record[key]) != _json(expected[key]):
                return {'valid': False, 'reason': f'certificate field differs: {key}'}
    except (KeyError, ValueError, TypeError) as exc:
        return {'valid': False, 'reason': str(exc)}
    return {'valid': True, 'matrix_entries_rebuilt': len(matrix) * len(matrix[0]),
            'rank': expected['raising_matrix_rank'], 'highest_vector_kernel_dimension': 0}


def moyal_closure_obstruction(degree=58):
    """Exact ordinary Moyal commutator of x^degree and y^degree."""
    if isinstance(degree, bool) or not isinstance(degree, int) or not 1 <= degree <= 100:
        raise ValueError('degree must be an integer in 1..100')
    from .asterion_principal import EXPONENTS
    retained = tuple(2 * m for m in EXPONENTS)
    terms = [{'hbar_power': r, 'x_power': degree - r, 'y_power': degree - r,
              'coefficient': Q(2 * _falling(degree, r) ** 2, 2 ** r * factorial(r))}
             for r in range(1, degree + 1, 2)]
    escaped = [term for term in terms if term['x_power'] + term['y_power'] not in retained]
    return {'convention': 'star=m compose exp((hbar/2)*(d_x tensor d_y-d_y tensor d_x))',
            'input_degrees': [degree, degree], 'retained_polynomial_degrees': retained,
            'commutator_terms': terms, 'escaped_term_count': len(escaped),
            'leading_term': terms[0], 'closed_in_eight_blocks': not escaped,
            'scope': 'Ordinary canonical Moyal multiplication on binary polynomials. Weighted E8 transvectant couplings define a different bracket; no quantization of E8 is claimed.'}


def principal_dj_cobracket_obstruction(algebra=None):
    """A concrete witness that the principal sl2 inclusion is not a DJ subbialgebra.

    Convention: delta(e_i)=e_i wedge h_i, up to a common nonzero scale.
    The positive-simple-root/Cartan coefficient matrix of delta(sum e_i) is
    I_8, whereas that of e wedge h is the rank-one outer product 1*h^T.
    The other two principal wedge generators have different root weights.
    """
    from .asterion_e8 import E8LieAlgebra
    g = algebra or E8LieAlgebra()
    inverse = _inverse(g.cartan_matrix)
    h = tuple(2 * sum(row, Q(0)) for row in inverse)
    if not h[1]:
        raise ArithmeticError('chosen principal h coordinate vanished')
    value = h[1]
    killed_value = h[1] * h[0] - h[0] * h[1]
    return {'normalization': 'delta(e_i)=e_i wedge h_i; common nonzero rescaling does not change the obstruction',
        'principal_h_coefficients': h, 'delta_e_simple_cartan_matrix_rank': 8,
        'principal_e_wedge_h_matrix_rank': 1,
        'witness_terms': [{'coordinate': 'e_1 wedge h_1', 'coefficient': h[1]},
                          {'coordinate': 'e_1 wedge h_2', 'coefficient': -h[0]}],
        'witness_on_principal_e_wedge_h': killed_value,
        'witness_on_delta_principal_e': value,
        'principal_inclusion_is_lie_bialgebra_map': False,
        'passed': killed_value == 0 and value != 0,
        'scope': 'Obstruction for the standard Drinfeld-Jimbo cobracket and this principal inclusion; it does not exclude other Lie bialgebra structures or quantizations.'}


def _cybe(r):
    out = {}
    for (a, b), x in r.items():
        for (c, d), y in r.items():
            for k, z in _sl2({a: 1}, {c: 1}).items():
                _add(out, {(k, b, d): z}, x * y)
            for k, z in _sl2({b: 1}, {c: 1}).items():
                _add(out, {(a, k, d): z}, x * y)
            for k, z in _sl2({b: 1}, {d: 1}).items():
                _add(out, {(a, c, k): z}, x * y)
    return out


def dynamical_r_boundary(parameter=2):
    """Exact sl2 rational CDYBE example: r(lambda)=e wedge f/lambda.

    CYB(r) is nonzero, but Alt(H tensor dr/dlambda)+CYB(r)=0.  This isolates
    the derivative term that an elliptic dynamical proposal must retain. It
    does not construct an elliptic r-matrix or a quantum R-matrix.
    """
    parameter = _q(parameter)
    if not parameter:
        raise ValueError('the dynamical r-matrix has a pole at zero')
    r = {(1, 2): 1 / parameter, (2, 1): -1 / parameter}
    dr = {(1, 2): -1 / parameter ** 2, (2, 1): 1 / parameter ** 2}
    derivative = {}
    for (a, b), value in dr.items():
        _add(derivative, {(0, a, b): value, (a, 0, b): -value, (a, b, 0): value})
    ordinary = _cybe(r)
    residual = _add(dict(ordinary), derivative)
    return {'parameter': parameter, 'r_tensor': r, 'ordinary_cybe_tensor': ordinary,
        'alternated_derivative_tensor': derivative, 'dynamical_residual': residual,
        'ordinary_cybe_holds': not ordinary, 'classical_dynamical_ybe_holds': not residual,
        'passed': bool(ordinary) and not residual,
        'elliptic_extension_status': 'Not implemented: elliptic/spectral kernels, poles, dynamical derivatives and quantum consistency require separate certificates.',
        'scope': 'A proved rational dynamical boundary; no elliptic quantization is asserted.'}


def higher_receipt(*, exhaustive=False, include_tables=False):
    """JSON-safe exact replay of explicitly enumerated higher-program panels."""
    from .asterion_principal import PrincipalE8
    principal = PrincipalE8()
    couplings = principal.couplings()
    panels = [(1, 7, 7, 1), (7, 7, 7, 7), (7, 11, 13, 17)]
    if exhaustive:
        panels += [(11, 13, 17, 19), (7, 11, 19, 23)]
    constraints = [jacobi_constraint_receipt(panel, couplings=couplings,
        include_equations=include_tables) for panel in panels]
    recouplings = []
    for panel in panels:
        result = recoupling_matrix(*panel)
        recouplings.append(result if include_tables else {key: value for key, value in result.items()
            if key not in ('coefficients', 'inverse', 'left_norms', 'right_norms', 'interpolation_samples')})
    dg = CurrentFormDGLA(3 if exhaustive else 2).verify()
    symmetric = e8_symmetric_square_obstruction(principal.algebra)
    if not include_tables:
        symmetric = {key: value for key, value in symmetric.items() if key not in ('columns', 'rows', 'raising_matrix')}
    pentagon = pentagon_receipt()
    dj = principal_dj_cobracket_obstruction(principal.algebra)
    dynamic = dynamical_r_boundary()
    moyal = moyal_closure_obstruction()
    passed = (all(q['evaluation']['passed'] for q in constraints)
        and all(r['passed'] for r in recouplings) and dg['passed'] and symmetric['passed']
        and pentagon['passed'] and dj['passed'] and dynamic['passed'] and not moyal['closed_in_eight_blocks'])
    return _json({'schema': 'perfectjet/asterion-higher/1', 'arithmetic': 'exact rational; Wigner symbols retain sign and rational square',
        'recoupling_panels': recouplings, 'jacobi_constraints': constraints,
        'pentagon': pentagon, 'current_form_dgla': dg,
        'symmetric_square_boundary': symmetric, 'moyal_boundary': moyal,
        'principal_dj_boundary': dj, 'dynamical_boundary': dynamic,
        'passed': passed,
        'scope': 'Every coefficient in each listed recoupling panel is checked. Exhaustive enlarges these stated panels and the finite DGLA; it does not mean all E8 spin quadruples or a full elliptic quantum theory.'})
