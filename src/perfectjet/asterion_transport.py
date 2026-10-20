"""An explicit rational isomorphism between the two executable E8 models.

The 2A4 ambient model has 240 one-dimensional nonzero root spaces and an
eight-dimensional diagonal Cartan space. Its roots are recovered as weights
of the two sl5 diagonal Cartans. A positive system and simple roots are
computed, their graph is identified with the Chevalley model's E8 diagram,
and root images are propagated by the actual brackets. No dense 248 by 248
inversion is needed: root columns are monomial and the only inverse is 8 by
8. All construction coefficients are rational. Coordinate conversion also
works over Q(zeta_5), allowing the Jordan Fourier chart to be transported.

The Cartan coordinate lattice uses the first four diagonal entries in each
trace-zero sl5 block. Integer coordinates are precisely the standard A4+A4
Cartan lattice: E_ii-E_(i+1)(i+1) is a unimodular basis of those coordinates.
The computed E8 Cartan column matrix B has determinant 1/5 and integral
inverse. Thus Z^8 is contained in B Z^8 at index five. This is a statement
about the transported Chevalley Cartan lattice, not integrality of the
Jordan Fourier basis over Z.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from typing import Mapping

from .asterion_e8 import E8LieAlgebra
from .asterion_jordan import Cyclotomic5, JordanE8, ZERO, a4_basis_bracket


def _add(out, key, value):
    if value:
        result = out.get(key, 0) + value
        if result:
            out[key] = result
        else:
            out.pop(key, None)


def _rational_bracket(left: Mapping, right: Mapping) -> dict:
    out = {}
    for a, x in left.items():
        for b, y in right.items():
            for token, coefficient in a4_basis_bracket(a, b):
                _add(out, token, x*y*coefficient)
    return {token: Fraction(value) for token, value in out.items()}


def _inverse(matrix):
    n = len(matrix)
    rows = [[Fraction(value) for value in row] +
            [Fraction(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot is None:
            raise ArithmeticError("the Cartan coordinate matrix is singular")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [value/divisor for value in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                scale = rows[i][j]
                rows[i] = [x-scale*y for x, y in zip(rows[i], rows[j])]
    return tuple(tuple(row[n:]) for row in rows)


def _determinant(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    n, determinant = len(rows), Fraction(1)
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != j:
            rows[j], rows[pivot] = rows[pivot], rows[j]
            determinant = -determinant
        divisor = rows[j][j]
        determinant *= divisor
        for i in range(j+1, n):
            scale = rows[i][j]/divisor
            for k in range(j+1, n):
                rows[i][k] -= scale*rows[j][k]
            rows[i][j] = Fraction(0)
    return determinant


def _matrix_token(copy, row, col):
    return ("m", copy, row, col)


def _weight(token):
    """Weights evaluated on E_ii-E_(i+1)(i+1), i=0..3, in each sl5."""
    if token[0] == "m":
        _, copy, row, col = token
        entries = [0]*8
        for i in range(4):
            entries[4*copy+i] = (int(row == i)-int(row == i+1)
                                 -int(col == i)+int(col == i+1))
        return tuple(entries)
    _, _, left, right = token
    return tuple(int(i in wedge)-int(i+1 in wedge)
                 for wedge in (left, right) for i in range(4))


def _weight_inner(alpha, beta):
    # Inverse A4 Cartan matrix: min(i,j)*(5-max(i,j))/5, one-based.
    return sum(Fraction(min(i+1, j+1)*(5-max(i+1, j+1)), 5)
               * alpha[4*copy+i] * beta[4*copy+j]
               for copy in range(2) for i in range(4) for j in range(4))


class E8ChartTransport:
    """Exact Chevalley <-> rational 2A4 <-> Jordan coordinates.

    ``images`` stores the 248 rational ambient columns of the isomorphism.
    Public conversion methods return exact Cyclotomic5 coefficients, so they
    also accept vectors over the Jordan coefficient field Q(zeta_5).
    """

    dimension = 248

    def __init__(self, chevalley=None, jordan=None):
        self.chevalley = chevalley if chevalley is not None else E8LieAlgebra()
        self.jordan = jordan if jordan is not None else JordanE8()
        tokens = [_matrix_token(copy, row, col)
                  for copy in range(2) for row in range(5) for col in range(5)
                  if row != col]
        tokens += [("w", degree, left, right)
                   for degree in range(1, 5)
                   for left in combinations(range(5), degree)
                   for right in combinations(range(5), (2*degree) % 5)]
        self.weight_token = {_weight(token): token for token in tokens}
        if len(tokens) != 240 or len(self.weight_token) != 240:
            raise ArithmeticError("expected 240 distinct one-dimensional root spaces")
        if any(_weight_inner(alpha, alpha) != 2 for alpha in self.weight_token):
            raise ArithmeticError("the 2A4 weight metric must give root norm two")
        zero = (0,)*8
        positives = {alpha for alpha in self.weight_token if alpha > zero}
        if len(positives) != 120:
            raise ArithmeticError("the lexicographic positive system has wrong size")
        simples = tuple(sorted(alpha for alpha in positives
                               if not any(tuple(a-b for a, b in zip(alpha, beta)) in positives
                                          for beta in positives)))
        if len(simples) != 8:
            raise ArithmeticError("the recovered E8 positive system must have eight simple roots")
        self.recovered_simple_weights = simples
        recovered_cartan = tuple(tuple(_weight_inner(alpha, beta) for beta in simples)
                                 for alpha in simples)
        assignment = self._identify_diagram(recovered_cartan)
        self.diagram_assignment = assignment
        self.simple_ambient_weights = tuple(simples[assignment[i]] for i in range(8))
        self.simple_ambient_tokens = tuple(self.weight_token[alpha]
                                          for alpha in self.simple_ambient_weights)
        images = [None]*248
        self.simple_normalizations = []
        for i, (weight, token) in enumerate(zip(self.simple_ambient_weights,
                                               self.simple_ambient_tokens)):
            opposite = self.weight_token[tuple(-x for x in weight)]
            e, f0 = {token: Fraction(1)}, {opposite: Fraction(1)}
            h0 = _rational_bracket(e, f0)
            acted = _rational_bracket(h0, e)
            if set(acted) != {token} or not acted[token]:
                raise ArithmeticError("opposite root spaces do not give an sl2 pair")
            scale = Fraction(2)/acted[token]
            f = {opposite: scale}
            h = {t: scale*c for t, c in h0.items()}
            images[i] = h
            images[next(iter(self.chevalley.simple_e(i)))] = e
            images[next(iter(self.chevalley.simple_f(i)))] = f
            self.simple_normalizations.append(scale)
        # All other root images are determined by Chevalley brackets, including
        # their cocycle-dependent signs. A norm-two positive root that is not
        # simple has a simple root that can be subtracted.
        for root in sorted(self.chevalley.roots, key=lambda alpha: (abs(sum(alpha)), alpha)):
            index = self.chevalley.root_index[root]
            if images[index] is not None:
                continue
            sign = 1 if sum(root) > 0 else -1
            for i, simple in enumerate(self.chevalley.simple_roots):
                smaller = tuple(a-sign*b for a, b in zip(root, simple))
                smaller_index = self.chevalley.root_index.get(smaller)
                if smaller_index is None or images[smaller_index] is None:
                    continue
                generator = self.chevalley.simple_e(i) if sign == 1 else self.chevalley.simple_f(i)
                generator_index = next(iter(generator))
                coefficient = self.chevalley.basis_bracket(generator_index, smaller_index)
                if set(coefficient) != {index}:
                    continue
                image = _rational_bracket(images[generator_index], images[smaller_index])
                image = {t: c/coefficient[index] for t, c in image.items()}
                if len(image) != 1:
                    raise ArithmeticError("a propagated root image is not one-dimensional")
                images[index] = image
                break
            if images[index] is None:
                raise ArithmeticError("root propagation failed")
        self.images = tuple(dict(image) for image in images)
        self._root_inverse = {}
        for index in range(8, 248):
            token, coefficient = next(iter(self.images[index].items()))
            if token in self._root_inverse or not coefficient:
                raise ArithmeticError("the root map is not invertible")
            expected_weight = tuple(sum(self.chevalley.index_root[index][j]
                                        * self.simple_ambient_weights[j][k]
                                        for j in range(8)) for k in range(8))
            if _weight(token) != expected_weight:
                raise ArithmeticError("propagated root image has the wrong weight")
            self._root_inverse[token] = (index, coefficient)
        self._diagonal_slots = tuple(_matrix_token(copy, i, i)
                                     for copy in range(2) for i in range(4))
        matrix = [[self.images[j].get(token, Fraction(0)) for j in range(8)]
                  for token in self._diagonal_slots]
        self.cartan_coordinate_matrix = tuple(tuple(row) for row in matrix)
        self._cartan_inverse = _inverse(matrix)
        self.cartan_transport_determinant = _determinant(matrix)
        self.cartan_inverse_integral = all(value.denominator == 1
                                          for row in self._cartan_inverse for value in row)
        # Standard A4 simple coroots H_i=E_ii-E_(i+1)(i+1), in the same
        # first-four-diagonal coordinates. Each 4x4 block has determinant 1.
        standard = [[Fraction(int(row == col)-int(row == col+1))
                     if copy == other else Fraction(0)
                     for other in range(2) for col in range(4)]
                    for copy in range(2) for row in range(4)]
        self.standard_a4_cartan_in_chevalley = tuple(
            tuple(sum(self._cartan_inverse[i][k]*standard[k][j] for k in range(8))
                  for j in range(8)) for i in range(8))
        self.standard_a4_embedding_determinant = _determinant(self.standard_a4_cartan_in_chevalley)
        self.standard_a4_embedding_integral = all(value.denominator == 1
            for row in self.standard_a4_cartan_in_chevalley for value in row)
        if (self.cartan_transport_determinant != Fraction(1, 5)
                or not self.cartan_inverse_integral
                or abs(self.standard_a4_embedding_determinant) != 5
                or not self.standard_a4_embedding_integral):
            raise ArithmeticError("the A4+A4 Cartan lattice inclusion must have index five")
        self._valid_tokens = set(tokens) | {_matrix_token(copy, i, i)
                                           for copy in range(2) for i in range(5)}
        # Check the entire recovered simple-root Cartan matrix, not just norms.
        self.simple_cartan_verified = all(
            _rational_bracket(self.images[i], self.images[next(iter(self.chevalley.simple_e(j)))])
            == {t: self.chevalley.cartan_matrix[i][j]*c
                for t, c in self.images[next(iter(self.chevalley.simple_e(j)))].items()
                if self.chevalley.cartan_matrix[i][j]}
            for i in range(8) for j in range(8))
        if not self.simple_cartan_verified:
            raise ArithmeticError("the transported simple-root Cartan matrix disagrees")

    def _identify_diagram(self, recovered):
        target = self.chevalley.cartan_matrix
        target_degrees = [sum(value == -1 for value in row) for row in target]
        recovered_degrees = [sum(value == -1 for value in row) for row in recovered]
        order = sorted(range(8), key=lambda i: (-target_degrees[i], i))
        assignment, used = {}, set()

        def visit(position):
            if position == 8:
                return True
            i = order[position]
            for j in range(8):
                if j in used or target_degrees[i] != recovered_degrees[j]:
                    continue
                if any(target[i][k] != recovered[j][value] for k, value in assignment.items()):
                    continue
                assignment[i] = j
                used.add(j)
                if visit(position+1):
                    return True
                used.remove(j)
                del assignment[i]
            return False

        if not visit(0):
            raise ArithmeticError("the recovered root graph is not E8")
        return tuple(assignment[i] for i in range(8))

    def basis_image(self, index):
        if not 0 <= index < 248:
            raise IndexError(index)
        return dict(self.images[index])

    def chevalley_to_a4(self, vector: Mapping):
        out = {}
        for index, coefficient in vector.items():
            if not 0 <= index < 248:
                raise IndexError(index)
            coefficient = Cyclotomic5(coefficient)
            for token, value in self.images[index].items():
                _add(out, token, coefficient*value)
        return out

    to_a4 = chevalley_to_a4

    def a4_to_chevalley(self, vector: Mapping):
        vector = {token: Cyclotomic5(value) for token, value in vector.items() if value}
        if any(token not in self._valid_tokens for token in vector):
            raise ValueError("unknown 2A4 ambient coordinate")
        if any(sum((vector.get(_matrix_token(copy, i, i), ZERO) for i in range(5)), ZERO)
               for copy in range(2)):
            raise ValueError("the two matrix components must have trace zero")
        out = {}
        for token, coefficient in vector.items():
            if token in self._root_inverse:
                index, scale = self._root_inverse[token]
                _add(out, index, coefficient/scale)
        diagonal = [vector.get(token, ZERO) for token in self._diagonal_slots]
        for i, row in enumerate(self._cartan_inverse):
            coefficient = sum((value*entry for value, entry in zip(row, diagonal)), ZERO)
            _add(out, i, coefficient)
        return out

    from_a4 = a4_to_chevalley

    def chevalley_to_jordan(self, vector: Mapping):
        return self.jordan.from_a4(self.chevalley_to_a4(vector))

    def jordan_to_chevalley(self, vector: Mapping):
        return self.a4_to_chevalley(self.jordan.to_a4(vector))

    def chevalley_bracket(self, left: Mapping, right: Mapping):
        """The same Chevalley bracket extended exactly to Q(zeta_5)."""
        out = {}
        for i, x in left.items():
            for j, y in right.items():
                factor = Cyclotomic5(x)*Cyclotomic5(y)
                for index, coefficient in self.chevalley.basis_bracket(i, j).items():
                    _add(out, index, factor*coefficient)
        return out

    def verify_intertwining(self, exhaustive=True):
        if exhaustive:
            pairs = combinations(range(248), 2)
        else:
            generators = {next(iter(self.chevalley.simple_e(i))) for i in range(8)}
            generators |= {next(iter(self.chevalley.simple_f(i))) for i in range(8)}
            pairs = sorted({tuple(sorted((i, j))) for i in generators for j in range(248) if i != j})
        checked = 0
        for i, j in pairs:
            expected = {}
            for index, value in self.chevalley.basis_bracket(i, j).items():
                for token, coefficient in self.images[index].items():
                    _add(expected, token, value*coefficient)
            actual = _rational_bracket(self.images[i], self.images[j])
            checked += 1
            if actual != expected:
                return {"passed": False, "exhaustive": exhaustive,
                        "basis_pairs_checked": checked, "counterexample": [i, j]}
        return {"passed": True, "exhaustive": exhaustive,
                "basis_pairs_checked": checked}

    def verify_roundtrips(self):
        for index in range(248):
            vector = {index: Cyclotomic5(1)}
            if self.a4_to_chevalley(self.chevalley_to_a4(vector)) != vector:
                return {"passed": False, "chart": "Chevalley-2A4", "index": index}
            if self.jordan_to_chevalley(self.chevalley_to_jordan(vector)) != vector:
                return {"passed": False, "chart": "Chevalley-Jordan", "index": index}
        for label in self.jordan.labels:
            vector = {label: Cyclotomic5(1)}
            if self.chevalley_to_jordan(self.jordan_to_chevalley(vector)) != vector:
                return {"passed": False, "chart": "Jordan-Chevalley", "label": label}
        return {"passed": True, "chevalley_a4_basis_roundtrips": 248,
                "chevalley_jordan_basis_roundtrips": 248,
                "jordan_chevalley_basis_roundtrips": 248}

    def receipt(self, exhaustive=True, *, include_columns=False):
        intertwining = self.verify_intertwining(exhaustive=exhaustive)
        roundtrips = self.verify_roundtrips()
        record = {"passed": intertwining["passed"] and roundtrips["passed"],
                "dimension": 248, "construction_field": "Q",
                "conversion_field": "Q(zeta_5)",
                "ambient_coordinates": 250, "trace_constraints": 2,
                "one_dimensional_root_columns": len(self._root_inverse),
                "cartan_inverse_size": [8, 8],
                "cartan_transport_determinant": str(self.cartan_transport_determinant),
                "cartan_inverse_integral": self.cartan_inverse_integral,
                "root_columns_have_unit_coefficients": all(abs(value) == 1
                    for image in self.images[8:] for value in image.values()),
                "cartan_lattice": {
                    "ambient_coordinates": "first four diagonal entries in each trace-zero sl5 block",
                    "standard_basis": "E_ii-E_(i+1)(i+1), i=0,1,2,3, in each of two sl5 copies",
                    "standard_a4_basis_in_chevalley_is_integral": self.standard_a4_embedding_integral,
                    "standard_a4_basis_embedding_determinant": str(self.standard_a4_embedding_determinant),
                    "standard_a4_cartan_lattice_index_in_chevalley_cartan": 5,
                    "jordan_fourier_basis_unimodular_over_Z_claim": False},
                "simple_cartan_verified": self.simple_cartan_verified,
                "root_column_denominators": sorted({value.denominator
                    for image in self.images[8:] for value in image.values()}),
                "cartan_column_denominators": sorted({value.denominator
                    for image in self.images[:8] for value in image.values()}),
                "simple_f_normalizations": [str(value) for value in self.simple_normalizations],
                "simple_ambient_weights": [list(weight) for weight in self.simple_ambient_weights],
                "intertwining": intertwining, "roundtrips": roundtrips,
                "new_simple_lie_algebra_claim": False}
        if include_columns:
            record["rational_ambient_columns"] = [
                {"chevalley_index": index,
                 "terms": [{"token": token, "coefficient": str(value)}
                           for token, value in sorted(image.items())]}
                for index, image in enumerate(self.images)]
            record["standard_a4_cartan_basis_in_chevalley"] = [
                [str(value) for value in row] for row in self.standard_a4_cartan_in_chevalley]
        return record

    record = receipt


def transport_receipt(exhaustive=True, *, include_columns=False):
    return E8ChartTransport().receipt(exhaustive=exhaustive, include_columns=include_columns)


__all__ = ["E8ChartTransport", "transport_receipt"]
