"""Exact residue-algebra certificates and carefully scoped monodromy consequences.

The five-channel adjoint E8 residues generate M_5 and gl_5.  This statement
alone does not determine the monodromy at a rational value of hbar.  In
particular, its determinant has finite image at every rational value.  The
formal and small non-root-of-unity parameter arguments are documented in
docs/ASTERION_MONODROMY_ALGEBRA.md; they are proofs, not numerical loop tests.
"""
from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction as Q
from functools import lru_cache
from math import lcm

from .asterion_kz import (CHANNELS, EIGENVALUES, E8KZ, identity, matrix_add,
                          matrix_multiply, matrix_scale)


def _flatten(a):
    return tuple(x for row in a for x in row)


def _matrix(v, n=5):
    return tuple(tuple(v[n*i:n*(i+1)]) for i in range(n))


def _transpose(a):
    return tuple(zip(*a))


def _commutator(a, b):
    return matrix_add(matrix_multiply(a, b), matrix_multiply(b, a), -1)


def _encode(a):
    return [[str(x) for x in row] for row in a]


def _nullspace(rows, n):
    rows = [list(map(Q, row)) for row in rows]
    r, pivots = 0, []
    for col in range(n):
        p = next((i for i in range(r, len(rows)) if rows[i][col]), None)
        if p is None:
            continue
        rows[p], rows[r] = rows[r], rows[p]
        d = rows[r][col]
        rows[r] = [x/d for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][col]:
                d = rows[i][col]
                rows[i] = [x-d*y for x, y in zip(rows[i], rows[r])]
        pivots.append(col)
        r += 1
    out = []
    for col in range(n):
        if col in pivots:
            continue
        v = [Q(0)]*n
        v[col] = Q(1)
        for i, p in enumerate(pivots):
            v[p] = -rows[i][col]
        d = next(x for x in v if x)
        out.append(tuple(x/d for x in v))
    return tuple(out)


def _polynomial_product_linear(coefficients, root):
    out = [Q(0)]*(len(coefficients)+1)
    for i, c in enumerate(coefficients):
        out[i] -= root*c
        out[i+1] += c
    return out


def cyclotomic_form_obstruction(modulus=17, exponents=(4, 2, 11, 0, 1)):
    """Exhaust all possible similitude factors for a cyclotomic spectrum.

    If U^t G U = alpha G and G is nonzero, alpha is the product of two
    eigenvalues, hence a modulus-th root.  In the U-eigenbasis each alpha
    permits just the blocks s+t=a.  The returned rank bound is sharp for
    arbitrary bilinear forms, and therefore also bounds symmetric forms.
    """
    if type(modulus) is not int or modulus < 2:
        raise ValueError("modulus must be an integer at least two")
    if not exponents or any(type(s) is not int for s in exponents):
        raise ValueError("a nonempty integer spectrum is required")
    counts = Counter(s % modulus for s in exponents)
    n = len(exponents)
    records = []
    for a in range(modulus):
        rank = sum(min(m, counts[(a-s) % modulus]) for s, m in counts.items())
        records.append({"similitude_exponent": a,
                        "maximum_bilinear_form_rank": rank,
                        "nondegenerate_possible": rank == n})
    return {"modulus": modulus, "spectrum_exponents": [s % modulus for s in exponents],
            "dimension": n, "all_similitude_factors_exhausted": True,
            "rank_bounds": records,
            "maximum_rank_over_all_factors": max(r["maximum_bilinear_form_rank"] for r in records),
            "nondegenerate_projective_bilinear_form_possible": any(r["nondegenerate_possible"] for r in records)}


class KZResidueAlgebra:
    """Arithmetic certificates sourced from the actual E8KZ matrices."""

    def __init__(self, kz=None):
        self.kz = kz or E8KZ()
        self.A, self.B = self.kz.A, self.kz.B
        self.n = len(self.A)
        if self.n != 5 or self.A != tuple(tuple(v if i == j else Q(0)
                for j in range(5)) for i, v in enumerate(EIGENVALUES)):
            raise ValueError("the five-channel E8 residue convention is required")

    @lru_cache(maxsize=None)
    def _word_data(self, kind, centered):
        if kind not in ("associative", "lie"):
            raise ValueError("kind must be associative or lie")
        if centered and kind != "lie":
            raise ValueError("centering is only used for the Lie algebra certificate")
        generators = tuple(matrix_add(a, identity(), 20) if centered else a
                           for a in (self.A, self.B))
        pivots, matrices, words, codes, depths, factors = {}, [], [], [], [], []
        queue = deque()

        def add(matrix, word, code, depth):
            row = list(_flatten(matrix))
            for p, basis in sorted(pivots.items()):
                d = row[p]
                if d:
                    row = [x-d*y for x, y in zip(row, basis)]
            p = next((i for i, x in enumerate(row) if x), None)
            if p is None:
                return
            d = row[p]
            pivots[p] = tuple(x/d for x in row)
            index = len(matrices)
            matrices.append(matrix)
            words.append(word)
            codes.append(code)
            depths.append(depth)
            factors.append(d)
            queue.append(index)

        if kind == "associative":
            add(identity(), "I", ("identity",), 0)
        for i, matrix in enumerate(generators):
            add(matrix, "AB"[i], ("generator", i), 1)
        while queue:
            parent = queue.popleft()
            for i, generator in enumerate(generators):
                if kind == "associative":
                    matrix = matrix_multiply(matrices[parent], generator)
                    word = words[parent]+"AB"[i]
                else:
                    matrix = _commutator(generator, matrices[parent])
                    word = "["+"AB"[i]+","+words[parent]+"]"
                add(matrix, word, ("step", i, parent), depths[parent]+1)
        # Closure under the two generators proves the accepted space is the
        # generated algebra.  Exhausting the queue is part of the certificate.
        return {"kind": kind, "centered": centered, "dimension": len(matrices),
                "ambient_dimension": 25 if not centered else 24,
                "words": words, "word_codes": [list(c) for c in codes],
                "maximum_word_length": max(depths), "pivot_columns": list(pivots),
                "pivot_values": [str(x) for x in factors],
                "basis_matrices": [_encode(a) for a in matrices],
                "generator_closure_exhausted": True,
                "rank_lower_bound": len(matrices),
                "rank_upper_bound": 24 if centered else 25,
                "all_basis_traces_zero": all(sum(a[i][i] for i in range(5)) == 0
                                             for a in matrices)}

    def word_certificate(self, kind="associative", *, centered=False):
        # Return an independent JSON-compatible object, not the cached mutable one.
        import copy
        return copy.deepcopy(self._word_data(kind, centered))

    def replay_word_certificate(self, certificate):
        # Bypass the construction cache: this is an independent fresh exact
        # matrix/word/rank computation, including all rejected closure words.
        expected = type(self)._word_data.__wrapped__(
            self, certificate.get("kind"), certificate.get("centered"))
        if certificate != expected:
            raise ArithmeticError("word/rank certificate does not replay from the E8 residues")
        return {"passed": True, "dimension": expected["dimension"],
                "words_recomputed": len(expected["words"]),
                "generator_closure_exhausted": True}

    def spectral_matrix_unit_certificate(self):
        """Construct edge matrix units by exact polynomials in ad_A."""
        zero = matrix_scale(identity(), 0)
        edges = [(i, j) for i in range(5) for j in range(5)
                 if i != j and self.B[i][j]]
        differences = [EIGENVALUES[i]-EIGENVALUES[j] for i, j in edges]
        if len(set(differences)) != len(edges):
            raise ArithmeticError("edge adjoint eigenvalues must be distinct")
        nodes = [Q(0)]+sorted(differences)
        powers = [self.B]
        for _ in range(len(nodes)-1):
            powers.append(_commutator(self.A, powers[-1]))
        records, units = [], {}
        for (i, j), d in zip(edges, differences):
            coefficients, denominator = [Q(1)], Q(1)
            for other in nodes:
                if other != d:
                    coefficients = _polynomial_product_linear(coefficients, other)
                    denominator *= d-other
            coefficients = [c/denominator for c in coefficients]
            value = zero
            for c, power in zip(coefficients, powers):
                value = matrix_add(value, power, c)
            unit = tuple(tuple(Q(r == i and s == j) for s in range(5)) for r in range(5))
            if value != matrix_scale(unit, self.B[i][j]):
                raise ArithmeticError("Lagrange adjoint projection did not isolate a matrix unit")
            units[i, j] = unit
            records.append({"row": i, "column": j, "adjoint_eigenvalue": str(d),
                            "entry": str(self.B[i][j]),
                            "lagrange_coefficients_ascending": [str(c) for c in coefficients],
                            "matrix_unit_replayed": True})
        paths = []
        for start in range(5):
            queue = deque([(start,)])
            visited = {start}
            while queue:
                path = queue.popleft()
                end = path[-1]
                if end != start:
                    value = units[path[0], path[1]]
                    for r, s in zip(path[1:-1], path[2:]):
                        value = _commutator(value, units[r, s])
                    expected = tuple(tuple(Q(i == start and j == end)
                                           for j in range(5)) for i in range(5))
                    if value != expected:
                        raise ArithmeticError("path commutator failed")
                    paths.append(list(path))
                for i, j in edges:
                    if i == end and j not in visited:
                        visited.add(j)
                        queue.append(path+(j,))
            if len(visited) != 5:
                raise ArithmeticError("the directed edge graph is not connected")
        return {"simple_residue_spectrum": [str(v) for v in EIGENVALUES],
                "edge_count": len(edges), "adjoint_projection_degree": len(nodes)-1,
                "adjoint_eigenvalues_on_B_support": [str(v) for v in nodes],
                "edge_projections": records, "all_offdiagonal_matrix_unit_paths": paths,
                "all_twenty_offdiagonal_units_replayed": len(paths) == 20,
                "four_diagonal_differences_from_commutators": True,
                "trace_A": str(sum(self.A[i][i] for i in range(5))),
                "conclusion": "Lie(A,B)=gl(5); Lie(A+20I,B+20I)=sl(5)"}

    def _linear_matrix_space(self, mode, centered=False):
        equations = []
        generators = tuple(matrix_add(a, identity(), 20) if centered else a
                           for a in (self.A, self.B))
        for x in generators:
            columns = []
            for p in range(25):
                e = _matrix(tuple(Q(i == p) for i in range(25)))
                if mode == "commutant":
                    value = _commutator(x, e)
                elif mode == "selfadjoint":
                    value = matrix_add(matrix_multiply(_transpose(x), e),
                                       matrix_multiply(e, x), -1)
                elif mode == "invariant":
                    value = matrix_add(matrix_multiply(_transpose(x), e),
                                       matrix_multiply(e, x))
                else:
                    raise ValueError("unknown linear matrix space")
                columns.append(_flatten(value))
            equations.extend(zip(*columns))
        return tuple(_matrix(v) for v in _nullspace(equations, 25))

    def form_certificate(self):
        commutant = self._linear_matrix_space("commutant")
        selfadjoint = self._linear_matrix_space("selfadjoint")
        invariant = self._linear_matrix_space("invariant")
        centered = self._linear_matrix_space("invariant", centered=True)
        if len(selfadjoint) != 1:
            raise ArithmeticError("expected a unique residue selfadjoint form")
        gram = selfadjoint[0]
        positive = all(gram[i][i] > 0 for i in range(5)) and all(
            not gram[i][j] for i in range(5) for j in range(5) if i != j)
        p = self.kz.crossing
        return {"common_commutant_dimension": len(commutant),
                "commutant_basis": [_encode(a) for a in commutant],
                "residue_selfadjoint_form_dimension": len(selfadjoint),
                "residue_selfadjoint_gram": _encode(gram),
                "residue_selfadjoint_gram_positive_definite": positive,
                "crossing_is_orthogonal_for_this_gram": matrix_multiply(
                    _transpose(p), matrix_multiply(gram, p)) == gram,
                "infinitesimally_invariant_bilinear_form_dimension": len(invariant),
                "centered_infinitesimally_invariant_bilinear_form_dimension": len(centered),
                "monodromy_invariant_hermitian_form_computed": False,
                "distinction": "X^t G=GX is selfadjointness; X^t G+GX=0 is infinitesimal invariance"}

    def specialization_spectrum(self, hbar=Q(1, 34)):
        if isinstance(hbar, (bool, float)):
            raise TypeError("an exact rational hbar is required")
        hbar = Q(hbar)
        phases = tuple((hbar*v) % 1 for v in EIGENVALUES)
        order = lcm(*(v.denominator for v in phases))
        exponents = tuple(int(v*order) for v in phases)
        resonances = [(i, j, str(hbar*(a-b)))
                      for i, a in enumerate(EIGENVALUES)
                      for j, b in enumerate(EIGENVALUES)
                      if i != j and hbar*(a-b) and (hbar*(a-b)).denominator == 1]
        determinant_phase = (hbar*sum(EIGENVALUES)) % 1
        return {"hbar": str(hbar), "spectrum_root_order": order,
                "spectrum_exponents": list(exponents),
                "local_eigenvalues_pairwise_distinct": len(set(phases)) == 5,
                "nonzero_integer_residue_difference_resonances": [list(r) for r in resonances],
                "local_monodromy_order_from_nonresonant_semisimple_form": order if not resonances else None,
                "determinant_phase_mod_one": str(determinant_phase),
                "determinant_image_exact_order": determinant_phase.denominator,
                "connected_monodromy_closure_contained_in_SL5": True,
                "GL5_closure_excluded_by_finite_determinant": True,
                "bilinear_similitude_obstruction": cyclotomic_form_obstruction(order, exponents)
                    if order >= 2 else None,
                "irreducibility_of_specialized_monodromy_proved_here": False,
                "specialized_full_closure_proved_here": False}

    def generic_monodromy_theorem(self):
        full = self.word_certificate("lie")
        if full["dimension"] != 25:
            raise ArithmeticError("the generic theorem requires actual residue Lie rank 25")
        return {"formal_monodromy_zariski_closure": "GL(5) over the algebraic closure of C((hbar))",
                "formal_parameter_is_constant_for_z_derivation": True,
                "actual_constant_term_Lie_word_rank": full["dimension"],
                "analytic_statement": "There exists epsilon>0 such that 0<|hbar|<epsilon and exp(4*pi*i*hbar) of infinite order imply monodromy closure GL(5,C).",
                "analytic_epsilon_numerically_certified": False,
                "pointwise_differential_galois_consequence": "GL(5,C) for the same small infinite-order specializations, by regular-singular Schlesinger density",
                "proof_steps": [
                    "Local nonresonant Frobenius bases and their connection matrix Phi(hbar) are analytic near0, with Phi(0)=I.",
                    "Common conjugation gives local generators exp(2*pi*i*hbar*A) and Phi(hbar)^(-1) exp(2*pi*i*hbar*B) Phi(hbar).",
                    "An infinite-order exp(4*pi*i*hbar) makes each local cyclic closure its integer-weight one-dimensional torus; its Lie algebra contains A or Phi^(-1)B Phi.",
                    "The recorded25 Lie words evaluated on A and Phi^(-1)B Phi have nonzero determinant at hbar0; their determinant is a formal unit and remains nonzero on some analytic neighborhood.",
                    "The group Lie algebra is gl5, so its Zariski closure equals the connected25-dimensional group GL5."],
                "rational_parameter_excluded_from_this_argument": True,
                "claim_of_Zariski_open_set_of_complex_parameter_values": False,
                "parameterized_Kolchin_group_computed": False,
                "generic_group_over_C_hbar_z_claimed": False,
                "external_density_source": "https://arxiv.org/html/1106.2664v2#S1"}

    def receipt(self, *, exhaustive=False):
        words = {"associative": self.word_certificate(),
                 "lie": self.word_certificate("lie"),
                 "centered_lie": self.word_certificate("lie", centered=True)}
        if exhaustive:
            replay = {name: self.replay_word_certificate(c) for name, c in words.items()}
        else:
            replay = None
        return {"passed": all(c["dimension"] == c["rank_upper_bound"] for c in words.values()),
                "source": "actual exact E8KZ residues on five invariant adjoint four-tensors",
                "channels": list(CHANNELS), "word_algebra_certificates": words,
                "spectral_matrix_unit_certificate": self.spectral_matrix_unit_certificate(),
                "linear_form_certificate": self.form_certificate(),
                "generic_monodromy_theorem": self.generic_monodromy_theorem(),
                "level4_local_spectrum_and_obstructions": self.specialization_spectrum(),
                "strict_word_certificate_replay": replay,
                "level4_full_group_claimed_from_residue_generation": False}


def monodromy_algebra_receipt(*, exhaustive=False):
    return KZResidueAlgebra().receipt(exhaustive=exhaustive)
