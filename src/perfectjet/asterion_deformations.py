"""Exact, bounded Lie-bracket deformation and coordinate-gauge arithmetic.

This module computes the classical adjoint Chevalley--Eilenberg degree-two
problem, not a new classification theorem.  Cochains use the ordered slots
``(i, j, k)`` with ``i < j``: slot ``(i,j,k)`` is the coefficient of ``e_k``
in ``phi(e_i,e_j)``.  The Jacobi convention is
``[[x,y],z] + [[y,z],x] + [[z,x],y]``.

The exact dense linear algebra is deliberately bounded to dimension eight.
``cochain_dimensions`` remains available for larger requests and reports the
allocation that was avoided.  In particular this module never silently forms
the full E8 cochain matrices.
"""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import combinations
from math import comb
from typing import Callable, Mapping

from .exact import nullspace, rref


def cochain_dimensions(dimension: int) -> dict:
    """Report cochain sizes without allocating matrices or Lie brackets."""
    if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1:
        raise ValueError("dimension must be a positive integer")
    n = dimension
    c1, c2, c3 = n*n, n*comb(n, 2), n*comb(n, 3)
    return {"dimension": n, "C1_dimension": c1, "C2_dimension": c2,
            "C3_dimension": c3, "d1_shape": [c2, c1],
            "d2_shape": [c3, c2],
            "dense_matrix_entries": c2*c1 + c3*c2}


class CochainSizeError(ValueError):
    """A bounded request failed before any matrix allocation."""
    def __init__(self, dimension: int, maximum: int):
        self.record = dict(cochain_dimensions(dimension), maximum_dimension=maximum,
                           allocated=False)
        super().__init__(f"deformation dimension {dimension} exceeds bounded maximum "
                         f"{maximum}; inspect .record for avoided matrix sizes")


def _clean(vector: Mapping, n: int) -> dict[int, Q]:
    if not isinstance(vector, Mapping):
        raise ValueError("a sparse vector must map integer indices to coefficients")
    out = {}
    for i, value in vector.items():
        if isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < n:
            raise ValueError("sparse vector index outside the vector space")
        z = Q(value)
        if z:
            out[i] = z
    return out


def _add(target: dict, source: Mapping, scale=1):
    for k, value in source.items():
        z = target.get(k, Q(0)) + scale*value
        if z:
            target[k] = z
        else:
            target.pop(k, None)
    return target


def _record(value):
    if isinstance(value, Q):
        return value.numerator if value.denominator == 1 else str(value)
    if isinstance(value, dict):
        return {str(k): _record(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_record(v) for v in value]
    return value


class _Span:
    """Incremental exact row span; used only to select quotient representatives."""
    def __init__(self):
        self.rows = {}

    def insert(self, vector):
        row = {i: Q(z) for i, z in enumerate(vector) if z}
        for pivot in sorted(self.rows):
            if pivot in row:
                _add(row, self.rows[pivot], -row[pivot])
        if not row:
            return False
        pivot = min(row)
        z = row[pivot]
        self.rows[pivot] = {i: value/z for i, value in row.items()}
        return True


class LieDeformationComplex:
    """Compute ``Z2/B2`` and second-order obstructions over the rationals.

    ``basis_bracket(i,j)`` must return a sparse vector and must implement both
    input orders.  Antisymmetry and every basis-triple Jacobi identity are
    checked before the deformation complex is used.  The ambient bound cannot
    exceed eight, even when ``max_dimension`` is supplied by a caller.
    """
    def __init__(self, dimension: int, basis_bracket: Callable,
                 max_dimension: int = 8):
        self.sizes = cochain_dimensions(dimension)
        if (isinstance(max_dimension, bool) or not isinstance(max_dimension, int)
                or not 1 <= max_dimension <= 8):
            raise ValueError("max_dimension must be an integer in 1..8")
        if dimension > max_dimension:
            raise CochainSizeError(dimension, max_dimension)
        self.dimension = n = dimension
        self.pairs = tuple(combinations(range(n), 2))
        self.triples = tuple(combinations(range(n), 3))
        self.slots = tuple((i, j, k) for i, j in self.pairs for k in range(n))
        self.slot_index = {slot: i for i, slot in enumerate(self.slots)}
        self.table = [[_clean(basis_bracket(i, j), n) for j in range(n)]
                      for i in range(n)]
        for i in range(n):
            if self.table[i][i]:
                raise ValueError(f"nonalternating bracket at ({i},{i})")
            for j in range(i+1, n):
                if _add(dict(self.table[i][j]), self.table[j][i]):
                    raise ValueError(f"nonantisymmetric bracket at ({i},{j})")
        self.jacobi_witness = self._jacobi_witness(self.table)
        if self.jacobi_witness is not None:
            raise ValueError(f"input bracket fails Jacobi: {_record(self.jacobi_witness)}")
        self._d1 = self._d2 = self._analysis = None

    def _evaluate(self, table, x, y):
        out = {}
        for i, a in x.items():
            for j, b in y.items():
                _add(out, table[i][j], a*b)
        return out

    def _jacobi_witness(self, table):
        for i, j, k in self.triples:
            out = {}
            for a, b, c in ((i, j, k), (j, k, i), (k, i, j)):
                _add(out, self._evaluate(table, table[a][b], {c: Q(1)}))
            if out:
                return {"triple": [i, j, k], "residual": out}
        return None

    def cochain(self, value) -> list[Q]:
        """Accept flat coordinates or ``{(i,j): {k: coefficient}}``."""
        if isinstance(value, Mapping):
            out = [Q(0)]*len(self.slots)
            for pair, vector in value.items():
                if (not isinstance(pair, tuple) or len(pair) != 2 or
                        any(isinstance(x, bool) or not isinstance(x, int) for x in pair)):
                    raise ValueError("cochain keys must be integer pairs (i,j)")
                i, j = pair
                if not 0 <= i < j < self.dimension:
                    raise ValueError("cochain input pairs must satisfy 0<=i<j<n")
                for k, z in _clean(vector, self.dimension).items():
                    out[self.slot_index[(i, j, k)]] = z
            return out
        if not isinstance(value, (list, tuple)) or len(value) != len(self.slots):
            raise ValueError(f"cochain needs exactly {len(self.slots)} coordinates")
        return [Q(z) for z in value]

    def cochain_table(self, value):
        n = self.dimension
        table = [[{} for _ in range(n)] for _ in range(n)]
        for (i, j, k), z in zip(self.slots, self.cochain(value)):
            if z:
                table[i][j][k] = z
                table[j][i][k] = -z
        return table

    def cochain_record(self, value):
        return [{"inputs": [i, j], "output": k, "coefficient": _record(z)}
                for (i, j, k), z in zip(self.slots, self.cochain(value)) if z]

    def _linearized(self, phi):
        rows = []
        for i, j, k in self.triples:
            out = {}
            for a, b, c in ((i, j, k), (j, k, i), (k, i, j)):
                _add(out, self._evaluate(self.table, phi[a][b], {c: Q(1)}))
                _add(out, self._evaluate(phi, self.table[a][b], {c: Q(1)}))
            rows.extend(out.get(q, Q(0)) for q in range(self.dimension))
        return rows

    def linearized_jacobi(self, value):
        """Return the exact coefficient of t in Jacobi(mu+t*phi)."""
        return self._linearized(self.cochain_table(value))

    def gauge(self, operator):
        """Return ``[Sx,y]+[x,Sy]-S[x,y]`` in flat C2 coordinates.

        Operators are row-major dense matrices: ``S[k][i]`` multiplies e_k
        in ``S(e_i)``.  This convention fixes the sign of the gauge map.
        """
        n = self.dimension
        if (not isinstance(operator, (list, tuple)) or len(operator) != n or
                any(not isinstance(row, (list, tuple)) or len(row) != n
                    for row in operator)):
            raise ValueError("gauge operator must be an n by n matrix")
        operator = [[Q(z) for z in row] for row in operator]
        columns = [{k: operator[k][i] for k in range(n) if operator[k][i]}
                   for i in range(n)]
        out = []
        for i, j in self.pairs:
            row = self._evaluate(self.table, columns[i], {j: Q(1)})
            _add(row, self._evaluate(self.table, {i: Q(1)}, columns[j]))
            for k, z in self.table[i][j].items():
                _add(row, columns[k], -z)
            out.extend(row.get(k, Q(0)) for k in range(n))
        return out

    def matrices(self):
        """Return copies of d1:C1->C2 and d2:C2->C3."""
        n = self.dimension
        if self._d1 is None:
            cols = []
            for k in range(n):
                for i in range(n):
                    operator = [[Q(0)]*n for _ in range(n)]
                    operator[k][i] = Q(1)
                    cols.append(self.gauge(operator))
            self._d1 = [[col[row] for col in cols]
                        for row in range(len(self.slots))]
        if self._d2 is None:
            cols = []
            for column in range(len(self.slots)):
                phi = [Q(0)]*len(self.slots)
                phi[column] = Q(1)
                cols.append(self.linearized_jacobi(phi))
            self._d2 = [[col[row] for col in cols]
                        for row in range(self.sizes['C3_dimension'])]
        return ([row[:] for row in self._d1], [row[:] for row in self._d2])

    def analyze(self):
        """Return exact ranks and actual cocycle representatives modulo gauge."""
        if self._analysis is not None:
            return self._analysis
        d1, d2 = self.matrices()
        gauge_columns = [[d1[i][j] for i in range(len(self.slots))]
                         for j in range(self.sizes['C1_dimension'])]
        span = _Span()
        for column in gauge_columns:
            span.insert(column)
        rank1 = len(span.rows)
        rr, pivots = rref(d2, len(self.slots))
        cocycles = nullspace(d2, len(self.slots))
        quotient = []
        for vector in cocycles:
            if span.insert(vector):
                quotient.append(vector)
        chain_witness = None
        for column, vector in enumerate(gauge_columns):
            image = self.linearized_jacobi(vector)
            if any(image):
                chain_witness = {"gauge_column": column, "residual": image}
                break
        if chain_witness is not None:
            raise ArithmeticError(f"d2*d1 unexpectedly nonzero: {_record(chain_witness)}")
        self._analysis = {"rank_d1": rank1, "rank_d2": len(pivots),
                          "Z2_dimension": len(cocycles),
                          "B2_dimension": rank1,
                          "H2_dimension": len(quotient),
                          "derivations_dimension": self.sizes['C1_dimension']-rank1,
                          "representatives": quotient,
                          "d2_d1_zero": True}
        return self._analysis

    def report(self, include_representatives=True):
        result = self.analyze()
        out = dict(self.sizes,
                   **{k: v for k, v in result.items() if k != 'representatives'},
                   arithmetic="exact rational", basis_jacobi_verified=True,
                   basis_triples_checked=len(self.triples),
                   cohomology="adjoint H2 = Z2/B2",
                   scope="Bounded classical infinitesimal deformation problem; "
                         "not a classification of finite deformations or E8.")
        if include_representatives:
            out['representatives'] = [self.cochain_record(v)
                                      for v in result['representatives']]
        return out

    def jacobi_obstruction(self, value):
        """Return the coefficient of t² in Jacobi(mu+t*phi)."""
        phi = self.cochain_table(value)
        out = []
        for i, j, k in self.triples:
            row = {}
            for a, b, c in ((i, j, k), (j, k, i), (k, i, j)):
                _add(row, self._evaluate(phi, phi[a][b], {c: Q(1)}))
            out.extend(row.get(q, Q(0)) for q in range(self.dimension))
        return out

    def second_order_extension(self, value):
        """Solve d2*psi = -Jacobi(phi), returning a correction or obstruction.

        A failure includes a left-null witness w with ``w*d2=0`` and
        ``w*(-Jacobi(phi)) != 0``.  A success only asserts Jacobi through order
        two; it does not assert a convergent or all-order deformation.
        """
        phi = self.cochain(value)
        first = self.linearized_jacobi(phi)
        if any(first):
            return {"first_order_cocycle": False, "extends_to_order_two": False,
                    "first_order_residual": _record(first),
                    "scope": "First-order Jacobi already fails."}
        obstruction = self.jacobi_obstruction(phi)
        _, d2 = self.matrices()
        rhs = [-z for z in obstruction]
        columns = len(self.slots)
        augmented = [row+[z] for row, z in zip(d2, rhs)]
        reduced, pivots = rref(augmented, columns+1)
        bad = next((row for row in reduced
                    if not any(row[:columns]) and row[columns]), None)
        base = {"first_order_cocycle": True,
                "quadratic_obstruction": _record(obstruction),
                "scope": "Exact Jacobi extension through order two only."}
        if bad is not None:
            # Recover a directly replayable functional on the original rows.
            transposed = [[d2[i][j] for i in range(len(d2))]
                          for j in range(columns)]
            witness = next(w for w in nullspace(transposed, len(rhs))
                           if sum((a*b for a, b in zip(w, rhs)), Q(0)))
            response = sum((a*b for a, b in zip(witness, rhs)), Q(0))
            return dict(base, extends_to_order_two=False,
                        left_null_witness=_record(witness),
                        witness_rhs=_record(response))
        solution = [Q(0)]*columns
        for row, pivot in zip(reduced, pivots):
            if pivot < columns:
                solution[pivot] = row[columns]
        residual = [sum((a*b for a, b in zip(row, solution)), Q(0))-z
                    for row, z in zip(d2, rhs)]
        if any(residual):
            raise ArithmeticError("second-order correction failed exact replay")
        return dict(base, extends_to_order_two=True,
                    correction=self.cochain_record(solution),
                    correction_coordinates=_record(solution),
                    residual_zero=True)


def deformation_receipt():
    """Small, independently replayable rigidity and obstruction examples."""
    sl2 = {(0, 1): {0: -2}, (0, 2): {1: 1}, (1, 2): {2: -2}}

    def bracket(i, j):
        if i < j:
            return sl2.get((i, j), {})
        return {k: -z for k, z in sl2.get((j, i), {}).items()} if i > j else {}

    simple = LieDeformationComplex(3, bracket)
    abelian = LieDeformationComplex(3, lambda i, j: {})
    nonintegrable = {(0, 1): {0: 1}, (1, 2): {1: 1}}
    return {"schema": "perfectjet/asterion-deformations/1",
            "sl2": simple.report(), "abelian3": abelian.report(False),
            "obstructed_abelian_direction": abelian.second_order_extension(nonintegrable),
            "E8_full_complex_not_allocated": cochain_dimensions(248)}
