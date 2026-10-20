"""Exact principal-sl2 polynomial coordinates and E8 transvectant couplings.

The principal basis and transvectants are classical.  ``Asterion`` names
this implementation and its exact replay, not a newly discovered basis.
All arithmetic is rational and uses only the Python standard library.
"""

from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from math import comb, factorial, gcd, lcm

from .asterion_e8 import E8LieAlgebra


EXPONENTS = (1, 7, 11, 13, 17, 19, 23, 29)
SparseVector = dict[int, Q]


def _clean(vector):
    return {i: Q(x) for i, x in vector.items() if x}


def _scale(vector, scalar):
    return {i: x * scalar for i, x in vector.items() if x * scalar}


def _add_into(target, source, scalar=1):
    for i, value in source.items():
        target[i] = target.get(i, Q(0)) + scalar * value
        if not target[i]:
            del target[i]


def _rref(matrix, ncols=None):
    width = len(matrix[0]) if matrix else (ncols or 0)
    rows = [[Q(x) for x in row] for row in matrix]
    if any(len(row) != width for row in rows):
        raise ValueError("ragged matrix")
    pivots = []
    for col in range(width):
        pivot = next((i for i in range(len(pivots), len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        index = len(pivots)
        rows[index], rows[pivot] = rows[pivot], rows[index]
        divisor = rows[index][col]
        rows[index] = [x / divisor for x in rows[index]]
        for i in range(len(rows)):
            if i != index and rows[i][col]:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[index])]
        pivots.append(col)
        if len(pivots) == len(rows):
            break
    return rows, pivots


def _nullspace(matrix, ncols):
    rows, pivots = _rref(matrix, ncols)
    result = []
    for free in range(ncols):
        if free in pivots:
            continue
        vector = [Q(int(j == free)) for j in range(ncols)]
        for i, pivot in enumerate(pivots):
            vector[pivot] = -rows[i][free]
        result.append(vector)
    return result


def _inverse_and_determinant(matrix):
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("matrix must be square")
    rows = [[Q(x) for x in row] + [Q(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    determinant = Q(1)
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        if pivot is None:
            raise ValueError("singular basis block")
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            determinant = -determinant
        divisor = rows[col][col]
        determinant *= divisor
        rows[col] = [x / divisor for x in rows[col]]
        for i in range(n):
            if i != col and rows[i][col]:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[col])]
    return [row[n:] for row in rows], determinant


def _primitive(vector):
    denominator = lcm(*(x.denominator for x in vector))
    integers = [int(x * denominator) for x in vector]
    divisor = gcd(*integers)
    integers = [x // divisor for x in integers]
    if next(x for x in integers if x) < 0:
        integers = [-x for x in integers]
    return integers


def _falling(n, r):
    if r < 0 or r > n:
        return 0
    return factorial(n) // factorial(n - r)


def _small_prime_factors(number):
    """Exact factorization for the fixed E8 determinants (all primes <=59)."""
    remaining = abs(number)
    factors = []
    for candidate in range(2, 60):
        power = 0
        while remaining % candidate == 0:
            remaining //= candidate
            power += 1
        if power:
            factors.append([candidate, power])
    if remaining != 1:
        raise ArithmeticError("unexpected prime above 59 in fixed principal E8 determinant")
    return factors


@lru_cache(maxsize=None)
def coupling_slots():
    """All 170 allowed channels, including slots whose actual value is zero."""
    return tuple((a, b, c) for k, a in enumerate(EXPONENTS)
                 for b in EXPONENTS[k:] for c in EXPONENTS
                 if abs(a - b) <= c <= a + b)


def monomial_transvectant(a, i, b, j, r):
    """Coefficient of T_r on binomial-normalized binary monomials.

    Inputs are binom(2a,i)x^(2a-i)y^i and binom(2b,j)x^(2b-j)y^j.
    The returned integer multiplies x^(2a+2b-i-j-r)y^(i+j-r).
    This is the unnormalized Cayley transvectant.
    """
    if not (0 <= i <= 2 * a and 0 <= j <= 2 * b and 0 <= r <= min(2 * a, 2 * b)):
        raise ValueError("invalid monomial or transvectant order")
    lo = max(0, r - j, r - (2 * a - i))
    hi = min(r, i, 2 * b - j)
    value = sum((-1) ** k * comb(r, k)
                * _falling(2 * a - i, r - k) * _falling(i, k)
                * _falling(2 * b - j, k) * _falling(j, r - k)
                for k in range(lo, hi + 1))
    return comb(2 * a, i) * comb(2 * b, j) * value


class PrincipalE8Basis:
    """248 exact chain vectors with inverse blocks and all reduced couplings.

    ``vectors[(m,j)]`` is (ad f)^j z_m / j!.  The highest vectors are
    primitive integral, with first nonzero Chevalley coordinate positive.
    ``z_1=e`` fixes the principal normalization.  Polynomial coordinates
    identify these vectors with binom(2m,j)x^(2m-j)y^j.
    """

    def __init__(self, algebra=None):
        self.algebra = algebra or E8LieAlgebra()
        g = self.algebra
        self.e = {}
        for i in range(8):
            _add_into(self.e, g.simple_e(i))
        inverse, _ = _inverse_and_determinant(g.cartan_matrix)
        self.h_coefficients = tuple(2 * sum(row) for row in inverse)
        self.h, self.f = {}, {}
        for i, value in enumerate(self.h_coefficients):
            _add_into(self.h, g.cartan_vector(i), value)
            _add_into(self.f, g.simple_f(i), value)
        if g.bracket(self.e, self.f) != self.h:
            raise ArithmeticError("principal triple normalization failed")
        if g.bracket(self.h, self.e) != _scale(self.e, 2):
            raise ArithmeticError("principal h does not have root height 2")
        self.height_indices = {
            height: tuple(i for i in range(248) if g.height(i) == height)
            for height in range(-29, 30)
        }
        self.highest = {}
        self.vectors = {}
        self.keys = tuple((m, j) for m in EXPONENTS for j in range(2 * m + 1))
        self.basis_labels = self.keys
        self.label_index = {key: i for i, key in enumerate(self.keys)}
        for m in EXPONENTS:
            domain = self.height_indices[m]
            codomain = self.height_indices.get(m + 1, ())
            images = [g.bracket(self.e, {i: Q(1)}) for i in domain]
            matrix = [[image.get(i, Q(0)) for image in images] for i in codomain]
            kernel = _nullspace(matrix, len(domain))
            if len(kernel) != 1:
                raise ArithmeticError(f"highest weight {m} has kernel dimension {len(kernel)}")
            coefficients = _primitive(kernel[0])
            seed = {i: Q(x) for i, x in zip(domain, coefficients) if x}
            if m == 1:
                if seed != self.e:
                    raise ArithmeticError("primitive spin-one seed differs from e")
                seed = self.e.copy()
            self.highest[m] = seed
            current = seed
            for j in range(2 * m + 1):
                self.vectors[m, j] = current
                current = _scale(g.bracket(self.f, current), Q(1, j + 1))
            if current:
                raise ArithmeticError(f"spin {m} chain did not terminate")
        self.block_keys = {}
        self.block_inverses = {}
        self.block_determinants = {}
        for height, indices in self.height_indices.items():
            keys = tuple((m, m - height) for m in EXPONENTS if abs(height) <= m)
            matrix = [[self.vectors[key].get(i, Q(0)) for key in keys] for i in indices]
            inverse, determinant = _inverse_and_determinant(matrix)
            self.block_keys[height] = keys
            self.block_inverses[height] = inverse
            self.block_determinants[height] = determinant
        self._couplings = None

    def to_principal(self, vector):
        """Chevalley sparse coordinates -> principal sparse coordinates."""
        vector = _clean(vector)
        if any(not isinstance(i, int) or not 0 <= i < 248 for i in vector):
            raise ValueError("Chevalley coordinate index outside 0..247")
        answer = {}
        for height in sorted({self.algebra.height(i) for i in vector}):
            values = [vector.get(i, Q(0)) for i in self.height_indices[height]]
            for key, row in zip(self.block_keys[height], self.block_inverses[height]):
                value = sum(x * y for x, y in zip(row, values))
                if value:
                    answer[key] = value
        return answer

    def to_chevalley(self, vector):
        """Principal sparse coordinates -> Chevalley sparse coordinates.

        Either integer positions in ``basis_labels`` or explicit (m,j)
        keys are accepted; the inverse ``from_chevalley`` uses integers.
        """
        answer = {}
        for key, value in vector.items():
            if isinstance(key, int) and 0 <= key < 248:
                key = self.keys[key]
            if key not in self.vectors:
                raise ValueError("unknown principal basis key")
            _add_into(answer, self.vectors[key], Q(value))
        return answer

    def from_chevalley(self, vector):
        """Chevalley sparse coordinates -> integer principal positions."""
        return {self.label_index[key]: value for key, value in self.to_principal(vector).items()}

    def bracket(self, left, right):
        """Bracket in integer-indexed principal coordinates."""
        def labels(vector):
            result = {}
            for index, value in vector.items():
                if not isinstance(index, int) or not 0 <= index < 248:
                    raise ValueError("principal coordinate index outside 0..247")
                if value:
                    result[self.keys[index]] = Q(value)
            return result
        answer = self.polynomial_bracket(labels(left), labels(right))
        return {self.label_index[key]: value for key, value in answer.items()}

    def couplings(self):
        """Compute every allowed exact reduced transvectant coefficient.

        Projection of [z_a,b_(b,r)] onto z_c, for r=a+b-c, is
        kappa_ab^c (2a)_r(2b)_r.  Projection uses the full inverse
        weight block, so contributions from larger spins are retained.
        """
        if self._couplings is None:
            values = {}
            for a, b, c in coupling_slots():
                r = a + b - c
                bracket = self.algebra.bracket(self.highest[a], self.vectors[b, r])
                projected = self.to_principal(bracket).get((c, 0), Q(0))
                values[a, b, c] = projected / (_falling(2 * a, r) * _falling(2 * b, r))
            self._couplings = values
        return self._couplings.copy()

    def polynomial_basis_bracket(self, left, right):
        """Bracket of two basis keys using only the 170 scalar couplings."""
        if left not in self.vectors or right not in self.vectors:
            raise ValueError("unknown principal basis key")
        a, i = left
        b, j = right
        couplings = self.couplings()
        answer = {}
        for c in EXPONENTS:
            if not abs(a - b) <= c <= a + b:
                continue
            r = a + b - c
            output_j = i + j - r
            if not 0 <= output_j <= 2 * c:
                continue
            kappa = couplings[min(a, b), max(a, b), c]
            if not kappa:
                continue
            value = kappa * monomial_transvectant(a, i, b, j, r) / comb(2 * c, output_j)
            if value:
                answer[c, output_j] = value
        return answer

    def polynomial_bracket(self, left, right):
        """Bilinear bracket of arbitrary principal-coordinate vectors."""
        answer = {}
        for a, x in left.items():
            for b, y in right.items():
                _add_into(answer, self.polynomial_basis_bracket(a, b), Q(x) * Q(y))
        return answer

    def verify(self, exhaustive=False):
        """Replay chains, coordinate inverses and direct-vs-polynomial brackets.

        The default checks all 248 chains, all 248 inverse columns, and
        every highest-seed input against every basis vector (1984 pairs).
        Exhaustive mode checks all 30876 unordered pairs including diagonal.
        Antisymmetry and bilinearity then cover every pair of vectors.
        """
        g = self.algebra
        chain_checks = 0
        inverse_checks = 0
        for (m, j), vector in self.vectors.items():
            expected_e = _scale(self.vectors.get((m, j - 1), {}), 2 * m - j + 1)
            expected_f = _scale(self.vectors.get((m, j + 1), {}), j + 1)
            if g.bracket(self.e, vector) != expected_e:
                raise ArithmeticError(f"e chain failure at {(m, j)}")
            if g.bracket(self.f, vector) != expected_f:
                raise ArithmeticError(f"f chain failure at {(m, j)}")
            if g.bracket(self.h, vector) != _scale(vector, 2 * m - 2 * j):
                raise ArithmeticError(f"h chain failure at {(m, j)}")
            chain_checks += 3
            if self.to_principal(vector) != {(m, j): Q(1)}:
                raise ArithmeticError(f"basis inverse failure at {(m, j)}")
            inverse_checks += 1
        if exhaustive:
            pairs = ((a, b) for i, a in enumerate(self.keys) for b in self.keys[i:])
        else:
            pairs = (((m, 0), b) for m in EXPONENTS for b in self.keys)
        bracket_checks = 0
        for a, b in pairs:
            direct = g.bracket(self.vectors[a], self.vectors[b])
            polynomial = self.to_chevalley(self.polynomial_basis_bracket(a, b))
            if direct != polynomial:
                raise ArithmeticError(f"polynomial bracket failure at {(a, b)}")
            bracket_checks += 1
        return {"basis_rank": 248, "chain_relations_checked": chain_checks,
                "inverse_columns_checked": inverse_checks,
                "bracket_pairs_checked": bracket_checks,
                "bracket_replay_exhaustive": bool(exhaustive),
                "all_checks_passed": True}

    def receipt(self, exhaustive=False):
        """JSON-ready complete coefficients, seeds and lattice comparison."""
        verification = self.verify(exhaustive=exhaustive)
        couplings = self.couplings()
        determinants = self.block_determinants
        determinant = Q(1)
        for value in determinants.values():
            determinant *= value
        primitive_index = abs(determinant)
        primitive_scales = {}
        max_denominator = 1
        common_denominator = 1
        for key, vector in self.vectors.items():
            denominator = lcm(*(x.denominator for x in vector.values()))
            integers = [int(x * denominator) for x in vector.values()]
            divisor = gcd(*integers)
            scale = Q(denominator, divisor)
            primitive_scales[key] = scale
            primitive_index *= scale
            max_denominator = max(max_denominator, *(x.denominator for x in vector.values()))
            common_denominator = lcm(common_denominator, denominator)
        if primitive_index.denominator != 1:
            raise ArithmeticError("integer-column lattice index was not integral")
        return {
            "schema": "perfectjet.asterion.principal.v1",
            "status": "exact classical principal basis and computed E8 couplings",
            "arithmetic": "fractions.Fraction; no floating-point arithmetic",
            "exponents": list(EXPONENTS),
            "polynomial_degrees": [2 * m for m in EXPONENTS],
            "chain_dimensions": [2 * m + 1 for m in EXPONENTS],
            "normalization": "b_(m,j)=(ad f)^j z_m/j! <-> binom(2m,j)x^(2m-j)y^j; z_1=e; unnormalized transvectants",
            "principal_h_chevalley_coefficients": [str(x) for x in self.h_coefficients],
            "highest_seeds": [{"exponent": m, "coordinates": [[i, str(x)] for i, x in sorted(seed.items())]}
                              for m, seed in self.highest.items()],
            "allowed_coupling_slots": len(couplings),
            "nonzero_coupling_slots": sum(bool(x) for x in couplings.values()),
            "zero_coupling_slots": sum(not x for x in couplings.values()),
            "couplings": [{"left_exponent": a, "right_exponent": b,
                           "output_exponent": c, "transvectant_order": a + b - c,
                           "coefficient": str(x)} for (a, b, c), x in couplings.items()],
            "height_blocks": [{"height": height, "dimension": len(self.height_indices[height]),
                               "determinant": str(determinants[height])}
                              for height in sorted(determinants)],
            "basis_absolute_determinant": {
                "exact_representation": "abs(product of the 59 height_blocks determinant values)",
                "prime_power_factors": _small_prime_factors(determinant.numerator),
                "numerator_bit_length": abs(determinant.numerator).bit_length(),
                "numerator_unsigned_big_endian_sha256": sha256(
                    abs(determinant.numerator).to_bytes(
                        (abs(determinant.numerator).bit_length() + 7) // 8, "big")).hexdigest(),
                "denominator": str(determinant.denominator),
            },
            "largest_coordinate_denominator": str(max_denominator),
            "common_coordinate_denominator": str(common_denominator),
            "primitive_integer_column_lattice_index": str(primitive_index.numerator),
            "primitive_integer_column_lattice_index_prime_power_factors": _small_prime_factors(primitive_index.numerator),
            "same_chevalley_integer_lattice": primitive_index == 1 and common_denominator == 1,
            "lattice_caution": "Rational divided chains need not be a Z-basis of the Chevalley lattice; integer-column index is computed after primitive column scaling.",
            "verification": verification,
        }


PrincipalE8 = PrincipalE8Basis


def principal_receipt(exhaustive=False):
    """Construct and verify the complete exact principal E8 calculation."""
    return PrincipalE8Basis().receipt(exhaustive=exhaustive)
