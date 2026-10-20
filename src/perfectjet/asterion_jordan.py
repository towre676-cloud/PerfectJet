"""An exact, executable Jordan-graded polynomial presentation of E8.

This is an implementation of an established algebra, not a claim of a new
simple Lie algebra.  The rational ``2A4`` bracket is Proposition 3.1 (equations
7, 8, 10, 14--17) of Cabrera--Draper--Garvin (2025),
https://doi.org/10.1007/s13398-025-01768-3 .  Its refinement uses the clock and
shift operators in Elduque, Theorem 2.1,
https://arxiv.org/abs/0810.2737 .  Every coefficient is in Q[z]/Phi_5(z).

The polynomial labels are nonzero elements of (Z/5)^3, with two vectors at
each label.  Ordinary polynomial multiplication is NOT the Lie bracket.
The nonidentity monomial span is NOT the augmentation ideal.  The routines
below supply the actual bracket and an invertible Fourier coordinate map.
No claim about an integral Chevalley lattice or characteristic five is made.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, product
import json
from math import lcm
from typing import Mapping


@lru_cache(maxsize=65536)
def _multiply_coefficients(a, b):
    """Cache exact products: a compiled grade law repeats few coefficients."""
    if not any(a) or not any(b):
        return (Fraction(0),)*4
    if not any(b[1:]):
        return tuple(c*b[0] for c in a)
    if not any(a[1:]):
        return tuple(c*a[0] for c in b)
    out = [Fraction(0)]*7
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    out[i+j] += x*y
    for k in range(6, 3, -1):
        if out[k]:
            for j in range(4):
                out[k-4+j] -= out[k]
    return tuple(out[:4])


@dataclass(frozen=True, init=False)
class Cyclotomic5:
    """Exact Q(zeta_5), in the power basis 1,z,z^2,z^3."""

    coefficients: tuple[Fraction, Fraction, Fraction, Fraction]

    def __init__(self, value=0):
        if isinstance(value, Cyclotomic5):
            cs = value.coefficients
        elif isinstance(value, (int, Fraction)):
            cs = (Fraction(value), Fraction(0), Fraction(0), Fraction(0))
        elif isinstance(value, (tuple, list)) and len(value) == 4:
            if any(isinstance(c, float) for c in value):
                raise TypeError("floating point cyclotomic coefficients are not accepted")
            cs = tuple(Fraction(c) for c in value)
        else:
            raise TypeError("an exact rational or four rational coefficients are required")
        object.__setattr__(self, "coefficients", cs)

    def __bool__(self):
        return any(self.coefficients)

    def __eq__(self, other):
        try:
            return self.coefficients == Cyclotomic5(other).coefficients
        except (TypeError, ValueError):
            return False

    def __hash__(self):
        # Equal rational values must have the same hash as Fraction/int.
        if not any(self.coefficients[1:]):
            return hash(self.coefficients[0])
        return hash(self.coefficients)

    def __add__(self, other):
        other = Cyclotomic5(other)
        return Cyclotomic5(tuple(a+b for a, b in zip(self.coefficients, other.coefficients)))

    __radd__ = __add__

    def __neg__(self):
        return Cyclotomic5(tuple(-c for c in self.coefficients))

    def __sub__(self, other):
        return self + -Cyclotomic5(other)

    def __rsub__(self, other):
        return Cyclotomic5(other) + -self

    def __mul__(self, other):
        other = Cyclotomic5(other)
        return Cyclotomic5(_multiply_coefficients(self.coefficients, other.coefficients))

    __rmul__ = __mul__

    def __pow__(self, exponent):
        if type(exponent) is not int:
            raise TypeError("integer exponent required")
        if exponent < 0:
            return self.inverse() ** -exponent
        out, base = ONE, self
        while exponent:
            if exponent & 1:
                out = out*base
            base = base*base
            exponent //= 2
        return out

    def inverse(self):
        if not self:
            raise ZeroDivisionError("zero in Q(zeta_5)")
        if not any(self.coefficients[1:]):
            return Cyclotomic5(1/self.coefficients[0])
        columns = [(self*Cyclotomic5(tuple(int(i == j) for i in range(4)))).coefficients
                   for j in range(4)]
        rows = [[columns[j][i] for j in range(4)]+[Fraction(i == 0)] for i in range(4)]
        for j in range(4):
            pivot = next(i for i in range(j, 4) if rows[i][j])
            rows[j], rows[pivot] = rows[pivot], rows[j]
            d = rows[j][j]
            rows[j] = [c/d for c in rows[j]]
            for i in range(4):
                if i != j and rows[i][j]:
                    d = rows[i][j]
                    rows[i] = [x-d*y for x, y in zip(rows[i], rows[j])]
        return Cyclotomic5(tuple(rows[i][4] for i in range(4)))

    def __truediv__(self, other):
        return self * Cyclotomic5(other).inverse()

    def __rtruediv__(self, other):
        return Cyclotomic5(other) * self.inverse()

    def conjugate(self):
        return sum((c*ZETA_POWERS[(-i) % 5] for i, c in enumerate(self.coefficients)), ZERO)

    def to_json(self):
        return [str(c) for c in self.coefficients]

    def __repr__(self):
        return "Cyclotomic5("+repr(tuple(str(c) for c in self.coefficients))+")"


ZERO = Cyclotomic5(0)
ONE = Cyclotomic5(1)
ZETA = Cyclotomic5((0, 1, 0, 0))
ZETA_POWERS = tuple(ZETA**i for i in range(5))
Grade = tuple[int, int, int]
Label = tuple[int, int, int, int]
ZERO_GRADE = (0, 0, 0)
GRADES = tuple(a for a in product(range(5), repeat=3) if a != ZERO_GRADE)
LABELS = tuple((*a, r) for a in GRADES for r in range(2))


def _grade(grade, *, allow_zero=False):
    if (not isinstance(grade, (tuple, list)) or len(grade) != 3
            or any(type(k) is not int for k in grade)):
        raise ValueError("grade must contain three exact integers (booleans excluded)")
    result = tuple(k % 5 for k in grade)
    if result == ZERO_GRADE and not allow_zero:
        raise ValueError("a nonzero grade is required")
    return result


def grade_add(a: Grade, b: Grade) -> Grade:
    return tuple((x+y) % 5 for x, y in zip(a, b))


def same_line(a: Grade, b: Grade) -> bool:
    return any(tuple(k*x % 5 for x in a) == b for k in range(1, 5))


def _sign(indices):
    return -1 if sum(indices[i] > indices[j] for i in range(len(indices))
                     for j in range(i+1, len(indices))) % 2 else 1


def _wedge(a, b):
    if set(a).intersection(b):
        return None
    return tuple(sorted(a+b)), _sign(a+b)


@lru_cache(maxsize=None)
def exterior_star(a, b):
    """Equation (7), on sorted wedge basis tuples; None means zero."""
    if len(a)+len(b) < 5:
        return _wedge(a, b)
    comp = tuple(k for k in range(5) if k not in b)
    if not set(comp).issubset(a):
        return None
    rest = tuple(k for k in a if k not in comp)
    return rest, _sign(b+comp)*_sign(comp+rest)


def _pair(a, b):
    out = exterior_star(a, b)
    return out[1] if out is not None and not out[0] else 0


@lru_cache(maxsize=None)
def _moment(a, b):
    """Trace-dual product M: tr(f M) = (f.a,b), Equation (10)."""
    entries = {}
    for k, col in enumerate(a):
        for row in range(5):
            replaced = a[:k]+(row,)+a[k+1:]
            if len(set(replaced)) < len(a):
                continue
            value = _sign(replaced)*_pair(tuple(sorted(replaced)), b)
            if value:
                entries[col, row] = entries.get((col, row), 0)+value
    trace = sum(entries.get((k, k), 0) for k in range(5))
    for k in range(5):
        entries[k, k] = entries.get((k, k), 0)-Fraction(trace, 5)
    return tuple((r, c, v) for (r, c), v in entries.items() if v)


def _m(copy, row, col):
    return ("m", copy, row, col)


def _w(i, a, b):
    return ("w", i, a, b)


@lru_cache(maxsize=None)
def a4_basis_bracket(a, b):
    """Rational bracket in ambient matrix/wedge coordinates.

    Matrix coordinates have two trace constraints.  Individual diagonal matrix
    units are convenient ambient coordinates, not independent E8 basis vectors.
    """
    if a > b:
        return tuple((k, -v) for k, v in a4_basis_bracket(b, a))
    out = {}

    def add(k, v):
        if v:
            out[k] = out.get(k, 0)+v
            if not out[k]:
                del out[k]

    if a[0] == b[0] == "m":
        _, cp, r, c = a
        _, cq, s, t = b
        if cp == cq:
            if c == s:
                add(_m(cp, r, t), 1)
            if t == r:
                add(_m(cp, s, c), -1)
    elif a[0] == "m" and b[0] == "w":
        _, cp, row, col = a
        _, i, left, right = b
        wedge = (left, right)[cp]
        for k, entry in enumerate(wedge):
            if entry != col:
                continue
            replaced = wedge[:k]+(row,)+wedge[k+1:]
            if len(set(replaced)) != len(replaced):
                continue
            new = tuple(sorted(replaced))
            add(_w(i, new if cp == 0 else left, new if cp == 1 else right), _sign(replaced))
    else:
        _, i, a1, a2 = a
        _, j, b1, b2 = b
        # Lexicographic order orders the integer Z5 grades first, as required
        # by the skew extension of Equation (15).
        if i+j == 5:
            p1, p2 = _pair(a1, b1), _pair(a2, b2)
            for r, c, v in _moment(a1, b1):
                add(_m(0, r, c), -p2*v)
            for r, c, v in _moment(a2, b2):
                add(_m(1, r, c), -p1*v)
        else:
            x, y = exterior_star(a1, b1), exterior_star(a2, b2)
            if x is not None and y is not None:
                add(_w((i+j) % 5, x[0], y[0]), x[1]*y[1])
    return tuple(out.items())


def _put(out, key, value):
    if value:
        out[key] = out.get(key, ZERO)+value
        if not out[key]:
            del out[key]


def a4_bracket(x: Mapping, y: Mapping):
    """Bilinear extension of the actual split E8 2A4 bracket."""
    out = {}
    for a, ca in x.items():
        for b, cb in y.items():
            factor = Cyclotomic5(ca)*Cyclotomic5(cb)
            for k, v in a4_basis_bracket(a, b):
                _put(out, k, factor*v)
    return out


def _shift_wedge(a):
    unsorted = tuple((k+1) % 5 for k in a)
    return tuple(sorted(unsorted)), _sign(unsorted)


def _shift_token(token):
    if token[0] == "m":
        _, cp, r, c = token
        return _m(cp, (r+1) % 5, (c+1) % 5), 1
    _, i, a, b = token
    x, sx = _shift_wedge(a)
    y, sy = _shift_wedge(b)
    return _w(i, x, y), sx*sy


def _orbit(token):
    out, sign = [], 1
    for _ in range(5):
        out.append((token, sign))
        token, step = _shift_token(token)
        sign *= step
    if token != out[0][0] or sign != 1:
        raise ArithmeticError("the signed clock-shift orbit did not close")
    return tuple(out)


class JordanE8:
    """248 polynomial coordinates, their full bracket and Fourier isomorphism.

    A basis label is (i,p,q,r): i,p,q are modulo-five grading coordinates,
    and r is 0 or 1.  The all-zero grade is absent.  ``basis_vector`` returns
    its five-term expansion in the explicit rational 2A4 model.
    """

    dimension = 248
    grades = GRADES
    labels = LABELS
    coefficient_field = "Q(zeta_5), Phi_5=1+z+z^2+z^3+z^4"

    def __init__(self):
        self._seeds = {}
        self._orbits = {}
        for p, q in product(range(5), repeat=2):
            if p == q == 0:
                continue
            for cp, inv_weight in ((0, 1), (1, 3)):
                self._seeds[0, p, q, cp] = _m(cp, p*inv_weight % 5, 0)
        for i in range(1, 5):
            tokens = tuple(_w(i, a, b)
                           for a in combinations(range(5), i)
                           for b in combinations(range(5), (2*i) % 5))
            seen, by_p = set(), {p: [] for p in range(5)}
            for token in tokens:
                if token in seen:
                    continue
                orbit = _orbit(token)
                seen.update(t for t, _ in orbit)
                p = (sum(token[2])+2*sum(token[3])) % 5
                by_p[p].append(token)
            for p in range(5):
                if len(by_p[p]) != 2:
                    raise ArithmeticError("the Jordan component does not have two fibers")
                for r, seed in enumerate(sorted(by_p[p])):
                    for q in range(5):
                        self._seeds[i, p, q, r] = seed
        for seed in set(self._seeds.values()):
            self._orbits[seed] = _orbit(seed)
        self._vectors = {
            label: {t: sign*ZETA_POWERS[(-label[2]*k) % 5]
                    for k, (t, sign) in enumerate(self._orbits[seed])}
            for label, seed in self._seeds.items()}
        self._kernels = {}

    @staticmethod
    def _label(label):
        if (not isinstance(label, (tuple, list)) or len(label) != 4
                or any(type(k) is not int for k in label)):
            raise ValueError("label must be (i,p,q,r), with integer entries")
        out = (label[0] % 5, label[1] % 5, label[2] % 5, label[3])
        if out[:3] == ZERO_GRADE or out[3] not in (0, 1):
            raise ValueError("a nonzero grade and fiber 0 or 1 are required")
        return out

    def basis_vector(self, label):
        return dict(self._vectors[self._label(label)])

    def to_a4(self, coordinates: Mapping):
        out = {}
        for label, coefficient in coordinates.items():
            label = self._label(label)
            for token, c in self._vectors[label].items():
                _put(out, token, Cyclotomic5(coefficient)*c)
        return out

    def from_a4(self, vector: Mapping, *, check=True):
        """Inverse Fourier map; rejects traceful or invalid ambient input."""
        vector = {t: Cyclotomic5(c) for t, c in vector.items() if c}
        valid = {t for v in self._vectors.values() for t in v}
        if any(t not in valid for t in vector):
            raise ValueError("unknown 2A4 ambient coordinate")
        if any(sum((vector.get(_m(cp, k, k), ZERO) for k in range(5)), ZERO)
               for cp in range(2)):
            raise ValueError("the two matrix components must have trace zero")
        out = {}
        for label, seed in self._seeds.items():
            q = label[2]
            c = sum((sign*vector.get(t, ZERO)*ZETA_POWERS[(q*k) % 5]
                     for k, (t, sign) in enumerate(self._orbits[seed])), ZERO)/5
            if c:
                out[label] = c
        if check and self.to_a4(out) != vector:
            raise ArithmeticError("the exact Fourier round trip failed")
        return out

    def automorphism(self, vector: Mapping, which: str):
        """Apply 'grade', 'clock', or 'shift' to an ambient 2A4 vector."""
        if which not in ("grade", "clock", "shift"):
            raise ValueError("which must be grade, clock, or shift")
        out = {}
        for token, c in vector.items():
            target = token
            if which == "shift":
                target, multiplier = _shift_token(token)
            elif which == "grade":
                multiplier = ZETA_POWERS[token[1] if token[0] == "w" else 0]
            elif token[0] == "m":
                multiplier = ZETA_POWERS[((1+token[1])*(token[2]-token[3])) % 5]
            else:
                multiplier = ZETA_POWERS[(sum(token[2])+2*sum(token[3])) % 5]
            _put(out, target, Cyclotomic5(c)*multiplier)
        return out

    def project_grade(self, vector: Mapping, grade: Grade):
        """Exact character projector onto a chosen joint eigenspace.

        This is (1/125) sum_{s in F5^3} zeta^(-grade.s) sigma_s.
        The grade and clock operators are already diagonal in the ambient
        coordinates, so their two character sums reduce to exact filtering;
        only the five-term shift Fourier sum needs to be performed.
        """
        i, p, q = _grade(grade, allow_zero=True)
        # This also verifies the ambient domain and the two trace conditions.
        self.from_a4(vector, check=False)
        filtered = {}
        for token, coefficient in vector.items():
            first = token[1] if token[0] == "w" else 0
            clock = (((1+token[1])*(token[2]-token[3])) % 5 if token[0] == "m"
                     else (sum(token[2])+2*sum(token[3])) % 5)
            if first == i and clock == p:
                _put(filtered, token, Cyclotomic5(coefficient))
        out = {}
        for k in range(5):
            for token, coefficient in filtered.items():
                _put(out, token, coefficient*ZETA_POWERS[(-q*k) % 5]/5)
            filtered = self.automorphism(filtered, "shift")
        return out

    def basis_bracket(self, left, right, *, check=False):
        left, right = self._label(left), self._label(right)
        target = grade_add(left[:3], right[:3])
        if target == ZERO_GRADE or same_line(left[:3], right[:3]):
            if check and a4_bracket(self._vectors[left], self._vectors[right]):
                raise ArithmeticError("a Cartan-line bracket is nonzero")
            return {}
        key = (left[:3], right[:3])
        reverse = key[0] > key[1]
        if reverse:
            key = key[::-1]
            a, b = right, left
        else:
            a, b = left, right
        subkey = (key, a[3], b[3])
        if subkey not in self._kernels:
            raw = a4_bracket(self._vectors[a], self._vectors[b])
            result = {(*target, r): raw.get(self._seeds[(*target, r)], ZERO)
                      for r in range(2)}
            result = {k: v for k, v in result.items() if v}
            # Homogeneity makes the coefficient at each orbit seed a pivot.
            # Optional replay verifies the *entire* ambient bracket, not just
            # those two pivot coordinates.
            if check and self.to_a4(result) != raw:
                raise ArithmeticError("the grade kernel lost an ambient coefficient")
            self._kernels[subkey] = result
        elif check:
            raw = a4_bracket(self._vectors[a], self._vectors[b])
            if self.to_a4(self._kernels[subkey]) != raw:
                raise ArithmeticError("cached grade kernel failed ambient replay")
        return {k: -v if reverse else v for k, v in self._kernels[subkey].items()}

    def bracket(self, left: Mapping, right: Mapping):
        out = {}
        for a, x in left.items():
            for b, y in right.items():
                factor = Cyclotomic5(x)*Cyclotomic5(y)
                for k, value in self.basis_bracket(a, b).items():
                    _put(out, k, factor*value)
        return out

    def grade_kernel(self, a: Grade, b: Grade, *, check=False):
        """2-by-2-by-2 tensor: result[input_left][input_right][output]."""
        a, b = _grade(a), _grade(b)
        target = grade_add(a, b)
        rows = []
        for r in range(2):
            row = []
            for s in range(2):
                result = self.basis_bracket((*a, r), (*b, s), check=check)
                row.append(tuple(result.get((*target, t), ZERO) for t in range(2)))
            rows.append(tuple(row))
        return tuple(rows)

    def all_grade_kernels(self, *, check=False):
        """All 7,440 unordered independent grade-pair product maps."""
        return {(a, b): self.grade_kernel(a, b, check=check)
                for a, b in combinations(GRADES, 2) if not same_line(a, b)}

    def kernel_receipt(self, kernels=None):
        """Canonical checksum and exact coefficient-size census of all maps.

        The checksum serializes sorted (grade,grade) keys, r,s,t tensor order,
        and four rational power-basis coefficients encoded as Fraction strings.
        No floating point approximation enters the checksum or arithmetic data.
        """
        kernels = self.all_grade_kernels() if kernels is None else kernels
        expected = {(a, b) for a, b in combinations(GRADES, 2) if not same_line(a, b)}
        if set(kernels) != expected:
            raise ValueError("the census requires exactly all 7,440 independent grade pairs")
        serial, values = [], []
        for (a, b), tensor in sorted(kernels.items()):
            if (len(tensor) != 2 or any(len(row) != 2 for row in tensor)
                    or any(len(output) != 2 for row in tensor for output in row)):
                raise ValueError("each grade kernel must have tensor shape 2 by 2 by 2")
            encoded = [[[Cyclotomic5(c).to_json() for c in output] for output in row]
                       for row in tensor]
            serial.append([list(a), list(b), encoded])
            values.extend(Cyclotomic5(c) for row in tensor for output in row for c in output if c)
        rationals = [c for value in values for c in value.coefficients]
        digest = sha256(json.dumps(serial, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()
        return {"grade_pair_maps": len(kernels), "basis_brackets_compiled": 4*len(kernels),
                "nonzero_scalar_outputs": len(values), "distinct_nonzero_coefficients": len(set(values)),
                "max_power_basis_denominator": max(c.denominator for c in rationals),
                "power_basis_denominator_lcm": lcm(*{c.denominator for c in rationals}),
                "max_absolute_power_basis_coefficient": str(max(abs(c) for c in rationals)),
                "max_absolute_power_basis_numerator": max(abs(c.numerator) for c in rationals),
                "closed_over_Z_zeta5": all(c.denominator == 1 for c in rationals),
                "cyclotomic_integer_structure_constants": all(c.denominator == 1 for c in rationals),
                "closed_free_Z_zeta5_lattice": all(c.denominator == 1 for c in rationals),
                "same_Chevalley_Z_lattice_claim": False,
                "chevalley_Z_lattice_identified": False,
                "kernel_sha256": digest,
                "checksum_encoding": "sorted grades; r,s,t order; four Fraction strings; compact JSON ASCII"}

    def cartan_lines(self):
        lines, seen = [], set()
        for a in GRADES:
            if a in seen:
                continue
            line = tuple(sorted(tuple(k*x % 5 for x in a) for k in range(1, 5)))
            seen.update(line)
            lines.append(tuple((*g, r) for g in line for r in range(2)))
        return tuple(lines)

    def verify_cartans(self, *, include_witnesses=False):
        """Replay commutativity and certify all 31 self-normalizing Cartans.

        For every outside grade, bracket against the eight line vectors is a
        map from its two-dimensional fiber to distinct outside-grade targets.
        A nonzero 2x2 minor proves this map injective. Hence no vector outside
        the line can normalize it. Abelian and self-normalizing is the Cartan
        criterion; commutativity alone would not suffice. All 3,720 minors are
        exact, and can optionally be returned as replayable witnesses.
        """
        lines = self.cartan_lines()
        checked, witnesses = 0, []
        for line_index, line in enumerate(lines):
            for a, b in combinations(line, 2):
                self.basis_bracket(a, b, check=True)
                checked += 1
            line_grades = {label[:3] for label in line}
            for grade in GRADES:
                if grade in line_grades:
                    continue
                first = None
                witness = None
                for h in line:
                    outputs = [self.basis_bracket(h, (*grade, r)) for r in range(2)]
                    target = grade_add(h[:3], grade)
                    for t in range(2):
                        row = tuple(outputs[r].get((*target, t), ZERO) for r in range(2))
                        if not any(row):
                            continue
                        if first is None:
                            first = (h, t, row)
                        else:
                            determinant = first[2][0]*row[1]-first[2][1]*row[0]
                            if determinant:
                                witness = {"line": line_index, "outside_grade": grade,
                                           "rows": ((first[0], first[1]), (h, t)),
                                           "determinant": determinant.to_json()}
                                break
                    if witness is not None:
                        break
                if witness is None:
                    return {"passed": False, "failed_line": line_index,
                            "outside_grade": grade, "reason": "no full-rank normalizer minor"}
                witnesses.append(witness)
        result = {"passed": len(lines) == 31 and len({a for line in lines for a in line}) == 248,
                  "lines": len(lines), "line_dimension": 8, "ambient_brackets_checked": checked,
                  "normalizer_minors_checked": len(witnesses), "normalizer_dimension_each": 8,
                  "cartan_identification": "abelian and self-normalizing, certified by graded 2x2 minors",
                  "normalizer_minor_sha256": sha256(json.dumps(witnesses, sort_keys=True,
                                                              separators=(",", ":")).encode()).hexdigest()}
        if include_witnesses:
            result["normalizer_minor_witnesses"] = witnesses
        return result

    def jacobi(self, a, b, c):
        out = {}
        for x, y, z in ((a, b, c), (b, c, a), (c, a, b)):
            for k, v in self.basis_bracket(x, y).items():
                for t, w in self.basis_bracket(k, z).items():
                    _put(out, t, v*w)
        return out

    def _verify_jacobi_compiled(self):
        """Exhaustive exact Jacobi, with integer cyclotomic arithmetic.

        A common denominator D clears every structure coefficient. Each
        nested bracket then has common denominator D**2.  Precomputed
        products and eight integer sums (two fibers, four power-basis
        coefficients) therefore test zero exactly, without modular or
        probabilistic fingerprints. Grade homogeneity determines the output
        grade; the two fiber coordinates must still be checked separately.
        """
        from math import lcm

        labels = tuple(self.labels)
        n = len(labels)
        index = {label: i for i, label in enumerate(labels)}
        raw = {}
        denominator = 1
        for i, j in combinations(range(n), 2):
            result = self.basis_bracket(labels[i], labels[j])
            raw[i, j] = result
            for coefficient in result.values():
                for value in coefficient.coefficients:
                    denominator = lcm(denominator, value.denominator)

        coefficients, coefficient_ids = [], {}

        def intern(value):
            if value not in coefficient_ids:
                coefficient_ids[value] = len(coefficients)
                coefficients.append(value)
            return coefficient_ids[value]

        table = [() for _ in range(n*n)]
        for (i, j), result in raw.items():
            table[n*i+j] = tuple(
                (index[k], intern(tuple(int(value*denominator)
                                        for value in coefficient.coefficients)))
                for k, coefficient in result.items())
            table[n*j+i] = tuple(
                (index[k], intern(tuple(-int(value*denominator)
                                        for value in coefficient.coefficients)))
                for k, coefficient in result.items())

        def multiply(left, right):
            out = [0]*7
            for i, x in enumerate(left):
                for j, y in enumerate(right):
                    out[i+j] += x*y
            for k in range(6, 3, -1):
                for j in range(4):
                    out[k-4+j] -= out[k]
            return tuple(out[:4])

        products = [[multiply(left, right) for right in coefficients]
                    for left in coefficients]
        checked = 0
        for i, j, k in combinations(range(n), 3):
            accum = [0]*8
            for x, y, z in ((i, j, k), (j, k, i), (k, i, j)):
                for inner, first in table[n*x+y]:
                    for output, second in table[n*inner+z]:
                        value = products[first][second]
                        offset = 4*labels[output][3]
                        accum[offset] += value[0]
                        accum[offset+1] += value[1]
                        accum[offset+2] += value[2]
                        accum[offset+3] += value[3]
            checked += 1
            if any(accum):
                return {"passed": False, "exhaustive": True,
                        "triples_checked": checked,
                        "counterexample": (labels[i], labels[j], labels[k]),
                        "residual_power_basis_by_fiber": [
                            [str(Fraction(value, denominator**2)) for value in accum[:4]],
                            [str(Fraction(value, denominator**2)) for value in accum[4:]]],
                        "coefficient_field": self.coefficient_field}
        return {"passed": True, "exhaustive": True,
                "triples_checked": checked,
                "coefficient_field": self.coefficient_field,
                "common_coefficient_denominator": denominator,
                "distinct_structure_coefficients": len(coefficients),
                "algorithm": "integer power-basis products modulo Phi_5; common denominator D^2"}

    def verify_jacobi(self, triples=None):
        """Exact Jacobi replay; None exhausts all C(248,3)=2,511,496 triples.

        Equal-label triples vanish by skew symmetry.  A supplied iterable is
        explicitly reported as a finite panel, never an exhaustive proof.
        The exhaustive path compiles exact integer power-basis products.
        """
        if triples is None:
            return self._verify_jacobi_compiled()
        exhaustive = False
        checked = 0
        for a, b, c in triples:
            checked += 1
            residual = self.jacobi(a, b, c)
            if residual:
                return {"passed": False, "exhaustive": exhaustive, "triples_checked": checked,
                        "counterexample": (a, b, c), "residual": residual}
        return {"passed": True, "exhaustive": exhaustive, "triples_checked": checked,
                "coefficient_field": self.coefficient_field}

    def gauge_transform(self, gauges: Mapping):
        """A new presentation under invertible 2x2 maps in each grade."""
        return GaugedJordanE8(self, gauges)


class GaugedJordanE8:
    """Explicit internal-fiber gauge; columns are new vectors in old coordinates."""

    def __init__(self, algebra, gauges):
        self.algebra, self.gauges, self.inverses = algebra, {}, {}
        for grade, matrix in gauges.items():
            grade = _grade(grade)
            if (not isinstance(matrix, (tuple, list)) or len(matrix) != 2
                    or any(not isinstance(r, (tuple, list)) or len(r) != 2 for r in matrix)):
                raise ValueError("nonzero grade and a 2x2 matrix required")
            a, b, c, d = (Cyclotomic5(v) for row in matrix for v in row)
            determinant = a*d-b*c
            if not determinant:
                raise ValueError("fiber gauge must be invertible")
            self.gauges[grade] = ((a, b), (c, d))
            self.inverses[grade] = ((d/determinant, -b/determinant),
                                    (-c/determinant, a/determinant))

    @staticmethod
    def _transform(vector, matrices):
        out = {}
        for label, value in vector.items():
            label = JordanE8._label(label)
            grade, r = tuple(label[:3]), label[3]
            matrix = matrices.get(grade, ((ONE, ZERO), (ZERO, ONE)))
            for s in range(2):
                _put(out, (*grade, s), Cyclotomic5(value)*matrix[s][r])
        return out

    def to_original(self, vector):
        return self._transform(vector, self.gauges)

    def from_original(self, vector):
        return self._transform(vector, self.inverses)

    def bracket(self, left, right):
        return self.from_original(self.algebra.bracket(self.to_original(left), self.to_original(right)))


def naive_permutation_no_go():
    """A concrete witness against untwisted SL3(F5) permutation covariance.

    The determinant-one map swaps e1,e2 and negates e3. Transitivity on ordered
    independent pairs would force one alternating C2xC2->C2 product. Its image
    has dimension <=1, so the derived algebra has dimension <=124, not 248.
    """
    return {"swap_matrix_mod5": ((0, 1, 0), (1, 0, 0), (0, 0, 4)),
            "determinant_mod5": 1, "alternating_fiber_image_dimension_bound": 1,
            "derived_dimension_bound": 124, "e8_dimension": 248,
            "conclusion": "degree permutation alone cannot preserve an E8 Jordan bracket",
            "required_covariance": "T_g(a+b) beta_ab(u,v) = beta_ga,gb(T_g(a)u,T_g(b)v)"}


def naive_permutation_counterexample(algebra=None):
    """An exact numerical failure of the untwisted swap in this actual basis."""
    algebra = algebra or JordanE8()

    def swap(label):
        i, p, q, r = label
        return (p, i, -q % 5, r)

    for a, b in combinations(LABELS, 2):
        if same_line(a[:3], b[:3]):
            continue
        mapped = {swap(k): v for k, v in algebra.basis_bracket(a, b).items()}
        direct = algebra.basis_bracket(swap(a), swap(b))
        if mapped != direct:
            return {"left": a, "right": b, "mapped_left": swap(a), "mapped_right": swap(b),
                    "mapped_original_bracket": [(k, v.to_json()) for k, v in mapped.items()],
                    "bracket_of_mapped_inputs": [(k, v.to_json()) for k, v in direct.items()],
                    "exact_mismatch": True}
    raise ArithmeticError("untwisted swap unexpectedly preserved all brackets")


def construction_receipt(*, all_kernels=False, ambient_replay=False):
    """Reproducible metadata, with computational scope stated explicitly."""
    algebra = JordanE8()
    receipt = {
        "construction": "explicit 2A4 exterior algebra bracket with clock-shift Fourier basis",
        "dimension": 248, "nonzero_grades": 124, "fiber_dimension": 2,
        "coefficient_field": algebra.coefficient_field,
        "split_e8_identification": "Cabrera-Draper-Garvin Proposition 3.1, solution (17)",
        "grading_identification": "Elduque Theorem 2.1",
        "cartans": algebra.verify_cartans(), "no_go": naive_permutation_no_go(),
        "no_go_counterexample": naive_permutation_counterexample(algebra),
        "integral_lattice_claim": False, "new_simple_lie_algebra_claim": False,
        "integral_lattice_claim_scope": "Chevalley Z lattice and rational descent not identified; Z[zeta5] closure censused separately",
    }
    if all_kernels:
        kernels = algebra.all_grade_kernels(check=ambient_replay)
        receipt.update(algebra.kernel_receipt(kernels))
        receipt["all_ambient_coefficients_replayed"] = ambient_replay
    return receipt
