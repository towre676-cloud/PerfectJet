"""Exact arithmetic in monogenic rational quotient algebras Q[x]/(f).

The modulus is supplied low coefficient first and must be monic. Elements are
coefficient vectors in the power basis 1,x,...,x^(n-1).  All arithmetic is
fractions.Fraction and dependency-free.
"""
from __future__ import annotations

from fractions import Fraction as Q


def _q(value):
    if isinstance(value, bool) or not isinstance(value, (int, str, Q)):
        raise ValueError("exact integer or rational-string coefficient required")
    try:
        return Q(value)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError("invalid exact rational coefficient") from error


def determinant(matrix):
    rows = [[Q(x) for x in row] for row in matrix]
    n = len(rows)
    if any(len(row) != n for row in rows):
        raise ValueError("square matrix required")
    if not n:
        return Q(1)
    det = Q(1)
    for column in range(n):
        pivot = next((i for i in range(column, n) if rows[i][column]), None)
        if pivot is None:
            return Q(0)
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            det = -det
        value = rows[column][column]
        det *= value
        for i in range(column+1, n):
            if rows[i][column]:
                ratio = rows[i][column] / value
                rows[i] = [x-ratio*y for x, y in zip(rows[i], rows[column])]
    return det


class MonogenicQuotient:
    """Power-basis arithmetic for Q[x]/(f), with f monic."""

    def __init__(self, modulus):
        if not isinstance(modulus, (list, tuple)) or len(modulus) < 2:
            raise ValueError("modulus must contain at least constant and leading terms")
        self.modulus = tuple(_q(c) for c in modulus)
        if self.modulus[-1] != 1:
            raise ValueError("modulus must be monic")
        self.degree = len(self.modulus)-1

    def element(self, coefficients):
        if not isinstance(coefficients, (list, tuple)) or len(coefficients) > self.degree:
            raise ValueError("element needs at most degree-many power-basis coefficients")
        return tuple([_q(c) for c in coefficients] + [Q(0)]*(self.degree-len(coefficients)))

    def basis(self, index):
        if type(index) is not int or not 0 <= index < self.degree:
            raise ValueError("basis index out of range")
        return tuple(Q(i == index) for i in range(self.degree))

    def add(self, a, b):
        a, b = self.element(a), self.element(b)
        return tuple(x+y for x, y in zip(a, b))

    def scale(self, a, scalar):
        a, scalar = self.element(a), _q(scalar)
        return tuple(scalar*x for x in a)

    def multiply(self, a, b):
        a, b = self.element(a), self.element(b)
        n = self.degree
        work = [Q(0)]*(2*n-1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                work[i+j] += x*y
        # x^n = -sum_{i<n} modulus[i] x^i.
        for k in range(2*n-2, n-1, -1):
            coefficient = work[k]
            if not coefficient:
                continue
            for i in range(n):
                work[i+k-n] -= coefficient*self.modulus[i]
            work[k] = Q(0)
        return tuple(work[:n])

    def power(self, a, exponent):
        if type(exponent) is not int or exponent < 0:
            raise ValueError("nonnegative integer exponent required")
        result = self.basis(0)
        base = self.element(a)
        while exponent:
            if exponent & 1:
                result = self.multiply(result, base)
            base = self.multiply(base, base)
            exponent //= 2
        return result

    def multiplication_matrix(self, a):
        a = self.element(a)
        columns = [self.multiply(a, self.basis(j)) for j in range(self.degree)]
        return [[columns[j][i] for j in range(self.degree)] for i in range(self.degree)]

    def trace(self, a):
        matrix = self.multiplication_matrix(a)
        return sum((matrix[i][i] for i in range(self.degree)), Q(0))

    def norm(self, a):
        return determinant(self.multiplication_matrix(a))

    def trace_matrix(self):
        return [[self.trace(self.multiply(self.basis(i), self.basis(j)))
                 for j in range(self.degree)] for i in range(self.degree)]

    def discriminant(self):
        return determinant(self.trace_matrix())

    def record(self, a):
        return [str(x) for x in self.element(a)]

    def receipt(self):
        x = self.basis(1) if self.degree > 1 else self.basis(0)
        return {
            "schema": "perfectjet/monogenic-quotient/1",
            "modulus_low_to_high": [str(x) for x in self.modulus],
            "degree": self.degree,
            "generator": self.record(x),
            "generator_multiplication_matrix": [
                [str(v) for v in row] for row in self.multiplication_matrix(x)],
            "trace_matrix": [[str(v) for v in row] for row in self.trace_matrix()],
            "discriminant": str(self.discriminant()),
            "scope": (
                "Exact arithmetic in the presented rational quotient algebra. "
                "Irreducibility, maximality of the corresponding integral order, "
                "and number-field identifications are separate mathematical obligations."
            ),
        }
