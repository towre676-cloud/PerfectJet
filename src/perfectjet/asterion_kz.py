"""Exact five-channel adjoint E8 KZ and classical Racah calculations.

The KZ connection and adjoint Racah calculus are classical.  This module
derives an arithmetic presentation from the actual E8 structure constants,
using five invariant four-tensors and sparse Casimir contractions; it never
allocates an array of size 248**4.  References and normalization are in
docs/ASTERION_KZ.md.  All algebraic certificates use Fraction arithmetic.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, product
import json
from math import ceil, lcm
import random

from .asterion_e8 import E8LieAlgebra


EIGENVALUES = (Q(-60), Q(-30), Q(-12), Q(0), Q(2))
CHANNELS = (1, 248, 3875, 30380, 27000)
TENSOR_NAMES = ("B(a,b)B(c,d)", "B(a,c)B(b,d)", "B(a,d)B(b,c)",
                "B([a,b],[c,d])", "B([a,c],[b,d])")


def _q(value):
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("exact rational input required; floats and booleans excluded")
    return Q(value)


def _integer(value, *, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("an integer >= %s is required" % minimum)
    return value


@dataclass(frozen=True, init=False)
class RationalComplex:
    """A Gaussian rational; float and bool inputs are intentionally rejected."""

    real: Q
    imag: Q

    def __init__(self, value=0, imag=None):
        if imag is not None:
            real, imag = _q(value), _q(imag)
        elif isinstance(value, RationalComplex):
            real, imag = value.real, value.imag
        elif isinstance(value, (tuple, list)):
            if len(value) != 2:
                raise ValueError("complex coordinates require exactly two rationals")
            real, imag = map(_q, value)
        else:
            real, imag = _q(value), Q(0)
        object.__setattr__(self, "real", real)
        object.__setattr__(self, "imag", imag)

    def __add__(self, other):
        other = RationalComplex(other)
        return RationalComplex(self.real+other.real, self.imag+other.imag)

    __radd__ = __add__

    def __neg__(self):
        return RationalComplex(-self.real, -self.imag)

    def __sub__(self, other):
        return self+-RationalComplex(other)

    def __rsub__(self, other):
        return RationalComplex(other)+-self

    def __mul__(self, other):
        other = RationalComplex(other)
        return RationalComplex(self.real*other.real-self.imag*other.imag,
                               self.real*other.imag+self.imag*other.real)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = RationalComplex(other)
        denominator = other.real**2+other.imag**2
        if not denominator:
            raise ZeroDivisionError("Gaussian rational division by zero")
        return RationalComplex((self.real*other.real+self.imag*other.imag)/denominator,
                               (self.imag*other.real-self.real*other.imag)/denominator)

    def __rtruediv__(self, other):
        return RationalComplex(other)/self

    def __bool__(self):
        return bool(self.real or self.imag)

    def norm_one(self):
        """A rational upper bound for the ordinary complex modulus."""
        return abs(self.real)+abs(self.imag)

    def modulus_lower(self):
        """A rational lower bound for the ordinary complex modulus."""
        return max(abs(self.real), abs(self.imag))

    def to_json(self):
        return [str(self.real), str(self.imag)]


def _complex_matrix_norm(matrix):
    return max(sum(RationalComplex(x).norm_one() for x in row) for row in matrix)


def _round_gaussian(value, denominator):
    value = RationalComplex(value)
    def rounded(x):
        scaled = x*denominator+Q(1, 2)
        return Q(scaled.numerator//scaled.denominator, denominator)
    return RationalComplex(rounded(value.real), rounded(value.imag))


def identity(n=5):
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def matrix_multiply(a, b):
    return tuple(tuple(sum((x*y for x, y in zip(row, col)), Q(0))
                       for col in zip(*b)) for row in a)


def matrix_add(a, b, scale=1):
    return tuple(tuple(x+scale*y for x, y in zip(ar, br)) for ar, br in zip(a, b))


def matrix_scale(a, scale):
    return tuple(tuple(scale*x for x in row) for row in a)


def matrix_vector(a, vector):
    return tuple(sum((x*y for x, y in zip(row, vector)), Q(0)) for row in a)


def inverse(a):
    n = len(a)
    rows = [[_q(c) for c in row]+list(identity(n)[i]) for i, row in enumerate(a)]
    if any(len(row) != 2*n for row in rows):
        raise ValueError("a square matrix is required")
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot is None:
            raise ValueError("singular matrix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        d = rows[j][j]
        rows[j] = [x/d for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                d = rows[i][j]
                rows[i] = [x-d*y for x, y in zip(rows[i], rows[j])]
    return tuple(tuple(row[n:]) for row in rows)


def _kernel_vector(a):
    rows = [list(map(Q, row)) for row in a]
    pivots, r = [], 0
    for c in range(len(rows[0])):
        pivot = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        d = rows[r][c]
        rows[r] = [v/d for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                d = rows[i][c]
                rows[i] = [v-d*w for v, w in zip(rows[i], rows[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(len(rows[0])) if c not in pivots]
    if len(free) != 1:
        raise ArithmeticError("expected a one-dimensional Casimir channel")
    out = [Q(0)]*len(rows[0])
    out[free[0]] = Q(1)
    for i, c in enumerate(pivots):
        out[c] = -rows[i][free[0]]
    # Deterministic rational normalization: first nonzero coordinate is one.
    d = next(v for v in out if v)
    return tuple(v/d for v in out)


def _encoded(matrix):
    return [[str(x) for x in row] for row in matrix]


def _prime_factors(n):
    out, p = [], 2
    while p*p <= n:
        if n % p == 0:
            out.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        out.append(n)
    return out


def _exp_upper(x):
    """A rational upper bound for exp(x), x>=0, using a geometric tail."""
    if x < 0:
        raise ValueError("nonnegative exponent required")
    terms = max(8, ceil(2*x)+2)
    term, total = Q(1), Q(1)
    for k in range(1, terms+1):
        term = term*x/k
        total += term
    next_term = term*x/(terms+1)
    return total+next_term/(1-x/(terms+2))


def _matrix_norm(a):
    return max(sum(abs(x) for x in row) for row in a)


class E8KZ:
    """Five invariant adjoint four-tensors, Casimir residues and crossing.

    ``A`` and ``B`` use the channel basis, ordered by CHANNELS, and satisfy
    dF/dz = hbar*(A/z+B/(z-1))*F. The normalized invariant form gives long
    roots squared length two, so C_ad=60 and hbar=1/(k+30) at WZW level k.
    ``crossing`` is rational and involutive; it is not claimed to be the
    orthonormal convention for a published quantum Racah matrix.
    """

    def __init__(self, algebra=None):
        self.algebra = algebra or E8LieAlgebra()
        self.metric_inverse = inverse(self.algebra.cartan_matrix)
        dual = [(i, j, self.metric_inverse[i][j])
                for i in range(8) for j in range(8) if self.metric_inverse[i][j]]
        dual.extend((i, self.algebra.root_index[tuple(-c for c in root)], Q(1))
                    for i, root in self.algebra.index_root.items())
        self.dual_metric_terms = tuple(dual)
        e = next(iter(self.algebra.simple_e(0)))
        f = next(iter(self.algebra.simple_f(0)))
        self.samples = ((0, 0, 1, 1), (0, 1, 0, 1), (0, 1, 1, 0),
                        (e, 0, f, 0), (e, f, 0, 0))
        evaluation = tuple(self.tensor_values(*sample) for sample in self.samples)
        self.evaluation_matrix = evaluation
        self.evaluation_inverse = inverse(evaluation)
        self.A_tensor = self._residue((0, 1))
        self.B_tensor = self._residue((1, 2))
        self.C_tensor = self._residue((0, 2))
        crossing_evaluations = tuple(self.tensor_values(c, b, a, d)
                                     for a, b, c, d in self.samples)
        self.crossing_tensor = matrix_multiply(self.evaluation_inverse, crossing_evaluations)
        columns = [_kernel_vector(matrix_add(self.A_tensor, identity(), -value))
                   for value in EIGENVALUES]
        self.channel_transform = tuple(zip(*columns))
        self.channel_inverse = inverse(self.channel_transform)
        transform = lambda a: matrix_multiply(self.channel_inverse,
                                             matrix_multiply(a, self.channel_transform))
        self.A = transform(self.A_tensor)
        self.B = transform(self.B_tensor)
        self.C = transform(self.C_tensor)
        self.crossing = transform(self.crossing_tensor)

    @lru_cache(maxsize=None)
    def form(self, i, j):
        if i < 8 and j < 8:
            return Q(self.algebra.cartan_matrix[i][j])
        if i >= 8 and j >= 8:
            return Q(all(x+y == 0 for x, y in zip(self.algebra.index_root[i],
                                                self.algebra.index_root[j])))
        return Q(0)

    def _bracket(self, i, j):
        return self.algebra._basis_bracket(i, j)

    @lru_cache(maxsize=131072)
    def bracket_pairing(self, a, b, c, d):
        return sum((x*y*self.form(i, j) for i, x in self._bracket(a, b)
                    for j, y in self._bracket(c, d)), Q(0))

    def tensor_values(self, a, b, c, d):
        return (self.form(a, b)*self.form(c, d), self.form(a, c)*self.form(b, d),
                self.form(a, d)*self.form(b, c), self.bracket_pairing(a, b, c, d),
                self.bracket_pairing(a, c, b, d))

    def contracted_values(self, sample, pair):
        """Evaluate all five Casimir-contracted tensors at one quadruple."""
        p, q = pair
        out = [Q(0)]*5
        for x, y, coefficient in self.dual_metric_terms:
            for i, ci in self._bracket(x, sample[p]):
                for j, cj in self._bracket(y, sample[q]):
                    args = list(sample)
                    args[p], args[q] = i, j
                    factor = coefficient*ci*cj
                    for r, value in enumerate(self.tensor_values(*args)):
                        out[r] += factor*value
        return tuple(out)

    def _residue(self, pair):
        values = tuple(self.contracted_values(sample, pair) for sample in self.samples)
        return matrix_multiply(self.evaluation_inverse, values)

    def projector(self, eigenvalue):
        eigenvalue = _q(eigenvalue)
        if eigenvalue not in EIGENVALUES:
            raise ValueError("one of the five known Casimir eigenvalues is required")
        out = identity()
        for other in EIGENVALUES:
            if other != eigenvalue:
                out = matrix_scale(matrix_multiply(out, matrix_add(self.A_tensor, identity(), -other)),
                                   1/(eigenvalue-other))
        return out

    def verify(self, *, samples=96, seed=1729, verify_form=True):
        """Exact identities plus independently chosen tensor evaluations.

        Five-tensor spanning follows from the established multiplicity-free
        adjoint tensor square; independence is certified by the displayed
        invertible evaluation matrix. Therefore Casimir invariance and these
        evaluations determine the whole invariant operators, not a fit to an
        unverified arbitrary 248^4 array.
        """
        _integer(samples)
        zero = tuple((Q(0),)*5 for _ in range(5))
        I = identity()
        checks = {
            "evaluation_inverse": matrix_multiply(self.evaluation_inverse, self.evaluation_matrix) == I,
            "diagonal_channel_spectrum": self.A == tuple(tuple(v if i == j else Q(0)
                                                               for j in range(5))
                                                         for i, v in enumerate(EIGENVALUES)),
            "crossing_involution": matrix_multiply(self.crossing, self.crossing) == I,
            "crossing_transports_residue": matrix_multiply(self.crossing, matrix_multiply(self.A, self.crossing)) == self.B,
            "three_residue_sum": matrix_add(matrix_add(self.A, self.B), self.C) == matrix_scale(I, -60),
        }
        commutator = lambda a, b: matrix_add(matrix_multiply(a, b), matrix_multiply(b, a), -1)
        checks["infinitesimal_braid"] = all(commutator(a, matrix_add(b, c)) == zero
                                          for a, b, c in ((self.A, self.B, self.C),
                                                          (self.B, self.A, self.C),
                                                          (self.C, self.A, self.B)))
        projectors = [self.projector(v) for v in EIGENVALUES]
        total = zero
        for p in projectors:
            total = matrix_add(total, p)
        checks["projector_resolution"] = total == I and all(
            matrix_multiply(p, q) == (p if i == j else zero)
            for i, p in enumerate(projectors) for j, q in enumerate(projectors))
        checks["projector_rank_one_on_invariants"] = all(sum(p[i][i] for i in range(5)) == 1 for p in projectors)
        checks["casimir_annihilating_polynomial"] = matrix_multiply(
            self.A_tensor, self._polynomial_nonzero_factors()) == zero
        form_terms = 0
        if verify_form:
            lowered = {}
            # Check the complete lowered structure tensor is alternating.
            for a in range(248):
                for b in range(a+1, 248):
                    for k, value in self._bracket(a, b):
                        if k < 8:
                            targets = ((c, self.form(k, c)) for c in range(8))
                        else:
                            root = self.algebra.index_root[k]
                            targets = ((self.algebra.root_index[tuple(-x for x in root)], Q(1)),)
                        for c, scalar in targets:
                            if scalar:
                                lowered[a, b, c] = lowered.get((a, b, c), Q(0))+value*scalar
            lowered = {k: v for k, v in lowered.items() if v}
            def low(a, b, c):
                return lowered.get((a, b, c), Q(0)) if a < b else -lowered.get((b, a, c), Q(0))
            checks["complete_metric_invariance"] = all(low(a, b, c) == -low(a, c, b)
                                                       for (a, b, c) in lowered)
            form_terms = len(lowered)
            casimir_ok = True
            for z in range(248):
                image = {}
                for x, y, coefficient in self.dual_metric_terms:
                    for inner, first in self._bracket(y, z):
                        for output, second in self._bracket(x, inner):
                            image[output] = image.get(output, Q(0))+coefficient*first*second
                casimir_ok &= {i: v for i, v in image.items() if v} == {z: Q(60)}
            checks["complete_adjoint_quadratic_casimir_60"] = casimir_ok
        rng = random.Random(seed)
        panel = list(self.samples)
        # Opposite root pairs ensure this is not a vacuous zero-weight panel.
        roots = tuple(self.algebra.index_root)
        for _ in range(samples):
            a, c = rng.choice(roots), rng.choice(roots)
            b = self.algebra.root_index[tuple(-x for x in self.algebra.index_root[a])]
            d = self.algebra.root_index[tuple(-x for x in self.algebra.index_root[c])]
            args = [a, b, c, d]
            rng.shuffle(args)
            panel.append(tuple(args))
        # Also include genuine four-root circuits, not just two opposite pairs.
        circuits, attempts = 0, 0
        while circuits < samples//2 and attempts < max(100, 100*samples):
            attempts += 1
            a, b, c = (rng.choice(roots) for _ in range(3))
            alpha, beta, gamma = (self.algebra.index_root[i] for i in (a, b, c))
            delta = tuple(-x-y-z for x, y, z in zip(alpha, beta, gamma))
            d = self.algebra.root_index.get(delta)
            if d is not None and all(not all(x+y == 0 for x, y in zip(u, v))
                                     for u, v in ((alpha, beta), (alpha, gamma), (beta, gamma))):
                panel.append((a, b, c, d))
                circuits += 1
        replay = True
        for sample in panel:
            values = self.tensor_values(*sample)
            for pair, residue in (((0, 1), self.A_tensor), ((1, 2), self.B_tensor), ((0, 2), self.C_tensor)):
                predicted = tuple(sum(values[i]*residue[i][j] for i in range(5)) for j in range(5))
                replay &= predicted == self.contracted_values(sample, pair)
        checks["independent_tensor_evaluations"] = replay
        return {"passed": all(checks.values()), "checks": checks,
                "independent_evaluation_quadruples": len(panel),
                "four_root_circuit_evaluations": circuits,
                "complete_lowered_structure_entries_checked": form_terms,
                "tensor_spanning_dependency": "known E8 adjoint tensor square is multiplicity-free with five summands",
                "arithmetic": "exact rational; normalized invariant form has C_ad=60"}

    def _polynomial_nonzero_factors(self):
        out = identity()
        for value in EIGENVALUES:
            if value:
                out = matrix_multiply(out, matrix_add(self.A_tensor, identity(), -value))
        return out

    def arithmetic_receipt(self):
        matrices = {"A_tensor": self.A_tensor, "B_tensor": self.B_tensor,
                    "C_tensor": self.C_tensor, "crossing_tensor": self.crossing_tensor,
                    "channel_transform": self.channel_transform, "A": self.A,
                    "B": self.B, "crossing": self.crossing}
        denominators = {x.denominator for matrix in matrices.values() for row in matrix for x in row}
        D = lcm(*denominators)
        serial = {name: _encoded(matrix) for name, matrix in matrices.items()}
        return {"matrix_sha256": sha256(json.dumps(serial, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                "matrix_denominator_lcm": D, "denominator_primes": _prime_factors(D),
                "max_absolute_numerator": max(abs(x.numerator) for matrix in matrices.values() for row in matrix for x in row),
                "minimal_localization_proved": False, "matrices": serial}

    @staticmethod
    def level_parameter(level):
        level = _integer(level, minimum=1)
        if level < 4:
            raise ValueError("all five integrable adjoint fusion channels require level >= 4")
        return Q(1, level+30)

    def frobenius(self, hbar, *, order=8, branch=0, logarithms=True):
        """Certified Frobenius coefficients, polynomial in formal log(z).

        At each resonance the canonical integration constant is zero.  A
        nonzero resonance source is integrated to an explicit log term, rather
        than divided by zero or silently discarded. With logarithms=False,
        the first incompatible canonical recurrence is returned as diagnostic.
        """
        hbar, order, branch = _q(hbar), _integer(order), _integer(branch)
        if order > 256:
            raise ValueError("bounded exact Frobenius order must be <=256")
        if type(logarithms) is not bool:
            raise TypeError("logarithms must be a boolean")
        if branch >= 5:
            raise ValueError("branch must lie in 0..4")
        rho = hbar*EIGENVALUES[branch]
        # series[n][p][i] is the coefficient of z^(rho+n) log(z)^p.
        series = [((tuple(Q(i == branch) for i in range(5))),)]
        resonances, obstructions = [], []
        for n in range(1, order+1):
            degree = max(len(polynomial) for polynomial in series)-1
            rhs = [[Q(0)]*5 for _ in range(degree+1)]
            for old in series:
                for p, vector in enumerate(old):
                    contribution = matrix_vector(self.B, vector)
                    for i in range(5):
                        rhs[p][i] -= hbar*contribution[i]
            new = [[Q(0)]*5 for _ in range(degree+2)]
            for i, eigenvalue in enumerate(EIGENVALUES):
                denominator = n+rho-hbar*eigenvalue
                if denominator:
                    for p in range(degree, -1, -1):
                        new[p][i] = (rhs[p][i]-(p+1)*new[p+1][i])/denominator
                else:
                    source = tuple(rhs[p][i] for p in range(degree+1))
                    resonances.append({"order": n, "target_channel": CHANNELS[i],
                                       "source_log_coefficients": [str(v) for v in source],
                                       "zero_source": not any(source)})
                    if any(source) and not logarithms:
                        obstructions.append({"order": n, "target_channel": CHANNELS[i],
                                             "source": [str(v) for v in source]})
                        return self._frobenius_record(series, rho, hbar, branch, order,
                                                       resonances, obstructions, complete=False)
                    for p in range(degree+1):
                        new[p+1][i] = source[p]/(p+1)
            while len(new) > 1 and not any(new[-1]):
                new.pop()
            series.append(tuple(tuple(vector) for vector in new))
        return self._frobenius_record(series, rho, hbar, branch, order,
                                       resonances, obstructions, complete=True)

    def _frobenius_record(self, series, rho, hbar, branch, requested_order,
                          resonances, obstructions, *, complete):
        last_resonance = max((int(hbar*(value-EIGENVALUES[branch])) for value in EIGENVALUES
                              if hbar*(value-EIGENVALUES[branch]) > 0
                              and (hbar*(value-EIGENVALUES[branch])).denominator == 1), default=0)
        residuals = []
        for n in range(1, len(series)):
            degree = max(len(polynomial) for polynomial in series[:n+1])
            residual = [[Q(0)]*5 for _ in range(degree)]
            for p in range(degree):
                current = series[n][p] if p < len(series[n]) else (Q(0),)*5
                derivative = series[n][p+1] if p+1 < len(series[n]) else (Q(0),)*5
                for i in range(5):
                    residual[p][i] = (n+rho-hbar*EIGENVALUES[i])*current[i]+(p+1)*derivative[i]
                for old in series[:n]:
                    if p < len(old):
                        for i, value in enumerate(matrix_vector(self.B, old[p])):
                            residual[p][i] += hbar*value
            residuals.extend(x for row in residual for x in row)
        has_logs = any(any(any(vector) for vector in polynomial[1:]) for polynomial in series)
        resonance_complete = len(series)-1 >= last_resonance
        return {"passed": not any(residuals) and complete, "branch": branch,
                "channel": CHANNELS[branch], "hbar": str(hbar), "rho": str(rho),
                "requested_order": requested_order, "computed_order": len(series)-1,
                "coefficients": [[list(map(str, vector)) for vector in polynomial] for polynomial in series],
                "has_logarithms": has_logs, "resonances": resonances,
                "obstructions": obstructions, "recurrence_residual_zero": not any(residuals),
                "all_positive_integer_resonances_passed": resonance_complete,
                "log_free_all_orders_certified": complete and resonance_complete and not has_logs,
                "normalization": "channel-leading vector; all resonance integration constants zero",
                "scope": "formal local solution; no global analytic-continuation claim"}

    def wzw_resonance_certificate(self):
        """Finite exact certificate of log-free local solutions for every k>=4.

        For k+30>=34 the largest eigenvalue gap is62, so positive integral
        resonances can occur only at n=1. The only such levels are18,30,32;
        their three source coefficients vanish exactly. Once the last
        resonance is passed, the recurrence has unique log-free continuation.
        This is an explicit arithmetic check of classical KZ data, not a
        claimed new general theorem about unitary conformal field theory.
        """
        candidates = sorted({int(b-a)-30 for a, b in combinations(EIGENVALUES, 2)
                             if b-a >= 34})
        checks = {str(k): [self.frobenius(self.level_parameter(k), order=1, branch=i)
                           for i in range(5)] for k in candidates}
        passed = all(r["passed"] and r["log_free_all_orders_certified"]
                     for panel in checks.values() for r in panel)
        return {"passed": passed, "scope": "all integer WZW levels k>=4; all five invariant channels",
                "max_eigenvalue_gap": 62, "min_k_plus_h_dual": 34,
                "possible_resonant_orders": [1], "exceptional_levels": candidates,
                "log_free_at_every_integer_level_ge4": passed,
                "level_one_adjoint_primary_claim": False, "exceptional_level_checks": checks}

    def continue_polygon(self, path, *, hbar, order=40, precision_bits=128,
                         step_ratio=Q(1, 16), tolerance=Q(1, 10**8),
                         max_steps=512, chart="tensor"):
        """A rigorous Gaussian-rational enclosure of polygon transport.

        The returned matrix transports a fundamental matrix initially equal
        to the identity.  Error is in the usual complex-modulus matrix
        infinity norm.  A closed polygon therefore gives one certified loop
        holonomy, with a stated error gate; it does not determine the full
        monodromy group.  Pole-crossing segments are rejected exactly.
        """
        vertices = tuple(RationalComplex(v) for v in path)
        if len(vertices) < 2:
            raise ValueError("a polygon needs at least two vertices")
        hbar, tolerance, step_ratio = _q(hbar), _q(tolerance), _q(step_ratio)
        order = _integer(order, minimum=1)
        precision_bits = _integer(precision_bits, minimum=16)
        max_steps = _integer(max_steps, minimum=1)
        if order > 64 or precision_bits > 512 or max_steps > 4096:
            raise ValueError("bounded polygon continuation requires order<=64, bits<=512, steps<=4096")
        if not 0 < step_ratio <= Q(1, 4) or tolerance <= 0:
            raise ValueError("0<step_ratio<=1/4 and positive tolerance required")
        if chart not in ("tensor", "channel"):
            raise ValueError("chart must be tensor or channel")
        for start, target in zip(vertices, vertices[1:]):
            direction = target-start
            for pole in (RationalComplex(0), RationalComplex(1)):
                offset = pole-start
                cross = direction.real*offset.imag-direction.imag*offset.real
                dot = direction.real*offset.real+direction.imag*offset.imag
                length_squared = direction.real**2+direction.imag**2
                if start == pole or target == pole or (direction and not cross and 0 <= dot <= length_squared):
                    raise ValueError("polygon segment intersects a KZ singularity")
        a, b = (self.A_tensor, self.B_tensor) if chart == "tensor" else (self.A, self.B)
        norm_a, norm_b = _matrix_norm(a), _matrix_norm(b)
        unit = identity()
        value = tuple(tuple(RationalComplex(x) for x in row) for row in unit)
        denominator, error, steps = 2**precision_bits, Q(0), []

        def multiply(left, right):
            # Sparse constant residues avoid unnecessary Gaussian products.
            rows = []
            for row in left:
                nonzero = tuple((i, x) for i, x in enumerate(row) if x)
                rows.append(tuple(sum((x*right[i][j] for i, x in nonzero), RationalComplex())
                                  for j in range(5)))
            return tuple(rows)

        for start, target in zip(vertices, vertices[1:]):
            center = start
            while center != target:
                if len(steps) >= max_steps:
                    raise ValueError("continuation exceeded max_steps before reaching target")
                r0, r1 = center.modulus_lower(), (center-1).modulus_lower()
                distance = min(r0, r1)
                radius = distance/2
                direction = target-center
                fraction = min(Q(1), step_ratio*distance/direction.norm_one())
                step = direction*fraction
                ratio = step.norm_one()/radius
                operator_bound = abs(hbar)*(norm_a/(r0-radius)+norm_b/(r1-radius))
                if operator_bound*radius > 256:
                    raise ValueError("Cauchy majorant exceeds the bounded calculation limit")
                growth_disk = _exp_upper(operator_bound*radius)
                growth_step = _exp_upper(operator_bound*step.norm_one())
                # z(z-1)Y'=hbar*(A(z-1)+Bz)Y gives this O(order)
                # three-term Taylor recurrence, with exact Gaussian rationals.
                q0, q1 = center*(center-1), 2*center-1
                m0 = matrix_scale(matrix_add(matrix_scale(a, center-1), matrix_scale(b, center)), hbar)
                m1 = matrix_scale(matrix_add(a, b), hbar)
                series = [value]
                for n in range(order):
                    left = matrix_add(m0, unit, scale=-n*q1)
                    coefficient = multiply(left, series[n])
                    if n:
                        right = matrix_add(m1, unit, scale=-(n-1))
                        coefficient = matrix_add(coefficient, multiply(right, series[n-1]))
                    series.append(matrix_scale(coefficient, 1/(q0*(n+1))))
                approximation, power = value, RationalComplex(1)
                for n in range(1, order+1):
                    power *= step
                    approximation = matrix_add(approximation, matrix_scale(series[n], power))
                tail = (_complex_matrix_norm(value)*growth_disk*ratio**(order+1)/(1-ratio)
                        if hbar else Q(0))
                rounded = tuple(tuple(_round_gaussian(x, denominator) for x in row)
                                for row in approximation)
                # Each rounded complex entry has modulus error <=1/D;
                # hence a 5x5 row sum has rounding error <=5/D.
                rounding = Q(5, denominator) if rounded != approximation else Q(0)
                bound = growth_step*error+tail+rounding
                error = Q(ceil(bound*denominator), denominator)
                center += step
                value = rounded
                steps.append({"endpoint": center.to_json(), "step": step.to_json(),
                              "cauchy_radius": str(radius), "tail_bound": str(tail),
                              "rounding_bound": str(rounding), "propagated_error_bound": str(error)})
        passed, closed = error <= tolerance, vertices[0] == vertices[-1]
        return {"passed": passed, "completed": True, "chart": chart, "hbar": str(hbar),
                "path": [v.to_json() for v in vertices], "closed_path": closed,
                "approximation_exact": [[x.to_json() for x in row] for row in value],
                "infinity_norm_error_bound": str(error), "requested_tolerance": str(tolerance),
                "tolerance_met": passed, "precision_bits": precision_bits, "taylor_order": order,
                "step_count": len(steps), "steps": steps,
                "single_loop_holonomy_certified": closed and passed,
                "global_monodromy_certified": False,
                "error_bound_method": "Banach-valued Cauchy coefficient estimate; rational exponential majorant; exact Gaussian Taylor recurrence; outward error rounding",
                "scope": "one prescribed polygon transport; a closed path certifies one loop holonomy, not the monodromy group"}

    def continue_real(self, initial, *, start, target, hbar, order=20, max_steps=128):
        """Controlled analytic continuation along a real interval in (0,1).

        Taylor coefficients, endpoint approximation and infinity-norm error
        bound are rational. Cauchy's estimate on a disk of half the distance
        to {0,1}, plus a rational exponential majorant, bounds every omitted
        Taylor tail and propagated input error. No error is inferred by merely
        comparing two numerical resolutions. This does not compute a loop or
        certify a global monodromy matrix.
        """
        c, target, hbar = _q(start), _q(target), _q(hbar)
        order, max_steps = _integer(order, minimum=1), _integer(max_steps, minimum=1)
        if order > 64 or max_steps > 256:
            raise ValueError("bounded exact continuation requires order<=64 and max_steps<=256")
        if not (0 < c < 1 and 0 < target < 1):
            raise ValueError("start and target must be strictly between 0 and1")
        if len(initial) != 5:
            raise ValueError("five channel coordinates required")
        vector = tuple(_q(x) for x in initial)
        error, steps, original_start = Q(0), [], c
        norm_a, norm_b = _matrix_norm(self.A), _matrix_norm(self.B)
        while c != target:
            if len(steps) >= max_steps:
                raise ValueError("continuation exceeded max_steps before reaching target")
            distance = min(c, 1-c)
            radius = distance/2
            magnitude = min(abs(target-c), distance/4)
            step = magnitude if target > c else -magnitude
            operator_bound = abs(hbar)*(norm_a/(c-radius)+norm_b/(1-c-radius))
            if operator_bound*radius > 256:
                raise ValueError("Cauchy majorant exceeds the bounded calculation limit")
            bound_disk = _exp_upper(operator_bound*radius)
            bound_step = _exp_upper(operator_bound*abs(step))
            series = [vector]
            matrices = [matrix_scale(matrix_add(matrix_scale(self.A, 1/c**(j+1)),
                                                matrix_scale(self.B, 1/(c-1)**(j+1))),
                                      hbar*(-1)**j) for j in range(order)]
            for n in range(order):
                value = [Q(0)]*5
                for j in range(n+1):
                    for i, x in enumerate(matrix_vector(matrices[j], series[n-j])):
                        value[i] += x/(n+1)
                series.append(tuple(value))
            approximation = tuple(sum(series[n][i]*step**n for n in range(order+1))
                                  for i in range(5))
            ratio = abs(step)/radius
            tail = (max(abs(x) for x in vector)*bound_disk*ratio**(order+1)/(1-ratio)
                    if hbar else Q(0))
            error = bound_step*error+tail
            steps.append({"start": str(c), "step": str(step), "cauchy_radius": str(radius),
                          "taylor_order": order, "tail_bound": str(tail),
                          "propagated_error_bound": str(error)})
            c += step
            vector = approximation
        return {"passed": True, "start": str(original_start), "target": str(target),
                "hbar": str(hbar), "approximation_exact": list(map(str, vector)),
                "approximation_decimal": [float(x) for x in vector],
                "infinity_norm_error_bound": str(error), "steps": steps,
                "error_bound_method": "Cauchy coefficient bound, rational exp majorant, propagated linear ODE stability",
                "global_monodromy_certified": False}

    def monodromy_pair_receipt(self, *, hbar=Q(1, 34), order=40,
                              precision_bits=128, tolerance=Q(1, 10**8)):
        """Enclose two generators and test their noncommutativity rigorously.

        The first path is a counterclockwise rectangle about zero, based at
        1/2.  The second is its image under z -> 1-z, about one. The checked
        crossing symmetry gives V=XUX exactly, so only one numerical path
        integration is needed. No density or monodromy-group identification
        is inferred from a successful noncommutativity certificate.
        """
        half = Q(1, 2)
        path = [(half, 0), (half, half), (-half, half), (-half, -half),
                (half, -half), (half, 0)]
        transport = self.continue_polygon(path, hbar=hbar, order=order,
                                          precision_bits=precision_bits,
                                          tolerance=tolerance, chart="tensor")
        crossing = self.crossing_tensor
        symmetry = (matrix_multiply(crossing, crossing) == identity()
                    and matrix_multiply(matrix_multiply(crossing, self.A_tensor), crossing) == self.B_tensor)
        u = tuple(tuple(RationalComplex(x) for x in row) for row in transport["approximation_exact"])
        v = matrix_multiply(matrix_multiply(crossing, u), crossing)
        difference = matrix_add(matrix_multiply(u, v), matrix_multiply(v, u), scale=-1)
        error_u = Q(transport["infinity_norm_error_bound"])
        error_v = _matrix_norm(crossing)**2*error_u
        error_difference = 2*(_complex_matrix_norm(u)*error_v
                              +_complex_matrix_norm(v)*error_u+error_u*error_v)
        lower = max(sum(RationalComplex(x).modulus_lower() for x in row) for row in difference)
        certified = transport["single_loop_holonomy_certified"] and symmetry
        return {"passed": certified, "hbar": str(_q(hbar)), "base_point": "1/2",
                "chart": "tensor", "first_loop": transport,
                "second_loop_path": [(1-RationalComplex(x)).to_json() for x in path],
                "second_loop_approximation_exact": [[x.to_json() for x in row] for row in v],
                "second_loop_error_bound": str(error_v),
                "crossing_symmetry_verified": symmetry,
                "commutator_difference_norm_lower_bound": str(lower),
                "commutator_difference_error_upper_bound": str(error_difference),
                "nonabelian_image_certified": certified and lower > error_difference,
                "two_generator_approximations_certified": certified,
                "monodromy_density_claim": False, "global_monodromy_certified": False,
                "scope": "two based generator holonomies with rational enclosures; no identification or density theorem for their generated group"}


FiveChannelKZ = E8KZ


def kz_receipt(*, level=4, order=8, samples=96, include_matrices=True, exhaustive=False):
    if type(exhaustive) is not bool:
        raise TypeError("exhaustive must be a boolean")
    if type(include_matrices) is not bool:
        raise TypeError("include_matrices must be a boolean")
    system = E8KZ()
    _integer(samples)
    hbar = system.level_parameter(level)
    verification = system.verify(samples=max(samples, 384) if exhaustive else samples)
    arithmetic = system.arithmetic_receipt()
    if not include_matrices:
        arithmetic.pop("matrices")
    local = [system.frobenius(hbar, order=order, branch=i) for i in range(5)]
    resonance = system.wzw_resonance_certificate()
    positive_formal_levels = sorted({int(gap/n)-30
                                    for a, b in combinations(EIGENVALUES, 2)
                                    for gap in (b-a,) for n in (1, 2)
                                    if (gap/n).denominator == 1 and gap/n >= 31})
    low_level = {str(k): [system.frobenius(Q(1, k+30), order=2, branch=i)
                          for i in range(5)] for k in (1, 2)}
    monodromy = system.monodromy_pair_receipt(hbar=hbar) if exhaustive else None
    return {"schema": "perfectjet/asterion-kz/1", "passed": verification["passed"] and all(r["passed"] for r in local) and resonance["passed"] and (monodromy is None or monodromy["passed"]),
            "construction": "five invariant four-tensors; exact sparse Casimir contractions",
            "new_racah_matrix_claim": False, "dimension": 5, "channels": list(CHANNELS),
            "split_casimir_eigenvalues": list(map(str, EIGENVALUES)),
            "normalization": "long roots squared length 2; C_ad=60; h_dual=30",
            "finite_lie_dimension": 248, "dense_248_power4_array_used": False,
            "verification": verification, "arithmetic": arithmetic,
            "wzw_level": level, "all_five_integrable_channels": level >= 4,
            "local_solutions": local, "candidate_resonant_wzw_levels_ge4": resonance["exceptional_levels"],
            "all_integer_level_resonance_certificate": resonance,
            "low_level_formal_system_diagnostics": low_level,
            "all_positive_integer_formal_resonant_levels": positive_formal_levels,
            "low_level_five_channel_integrable_claim": False,
            "exhaustive_requested": exhaustive,
            "monodromy_generator_certificate": monodromy,
            "controlled_complex_transport_available": True,
            "global_monodromy_certified": False,
            "global_monodromy_scope": "this component encloses two based generator holonomies and certifies noncommutativity; the independent asterion_monodromy exhaustive certificate proves the level-four compact and Zariski group closures",
            "sources": ["https://arxiv.org/abs/2106.04470", "https://arxiv.org/abs/1511.09077",
                        "https://arxiv.org/abs/math/0212387"]}
