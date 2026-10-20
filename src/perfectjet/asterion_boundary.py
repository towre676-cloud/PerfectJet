"""Exact principal Rees contractions and their canonical quadratic doubles.

The construction mechanisms are classical.  This module computes their
specific E8 data from the actual 170 rational principal couplings, and records
the algebraic argument proving Jacobi at every parameter, including zero.
No interpolation or sampled Jacobi test is used as that proof.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, product
from math import comb

from .asterion_principal import EXPONENTS, PrincipalE8Basis


def _q(value):
    if isinstance(value, (float, bool)):
        raise ValueError("exact rational coefficients required")
    try:
        return Q(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError("exact rational coefficients required") from exc


def _vector(vector, dimension):
    if not hasattr(vector, "items"):
        raise ValueError("sparse coordinate mapping required")
    result = {}
    for i, value in vector.items():
        if isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < dimension:
            raise ValueError("coordinate index outside the declared dimension")
        value = _q(value)
        if value:
            result[i] = value
    return result


def _add(target, source, scale=1):
    for i, value in source.items():
        target[i] = target.get(i, Q(0)) + scale * value
        if not target[i]:
            del target[i]


def _wire(vector):
    return [[i, str(value)] for i, value in sorted(vector.items())]


def _weights(values):
    if hasattr(values, "items"):
        if set(values) != set(EXPONENTS):
            raise ValueError("weights must specify all eight principal exponents")
        result = {m: values[m] for m in EXPONENTS}
    else:
        values = tuple(values)
        if len(values) != 8:
            raise ValueError("eight diagonal weights required")
        result = dict(zip(EXPONENTS, values))
    if any(isinstance(w, bool) or not isinstance(w, int) for w in result.values()):
        raise ValueError("integer diagonal weights required")
    if result[1] != 0:
        raise ValueError("the principal sl2 block must have weight zero")
    return result


def quadratic_completion_bound(dimension, maximum_restricted_rank):
    """A necessary dimension bound for an embedding into a quadratic algebra.

    ``maximum_restricted_rank`` must be proved for invariant forms on the
    embedded algebra.  This function does not assert that the lower bound
    is attainable or that the cotangent extension is minimal.
    """
    if (isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1
            or isinstance(maximum_restricted_rank, bool)
            or not isinstance(maximum_restricted_rank, int)
            or not 0 <= maximum_restricted_rank <= dimension):
        raise ValueError("positive dimension and a valid invariant-form rank bound required")
    radical_bound = dimension - maximum_restricted_rank
    return {"embedded_dimension": dimension,
            "maximum_restricted_invariant_form_rank": maximum_restricted_rank,
            "minimum_restricted_radical_dimension": radical_bound,
            "unrestricted_quadratic_completion_lower_bound": dimension + radical_bound,
            "canonical_cotangent_upper_bound": 2 * dimension,
            "isotropic_embedding_lower_bound": 2 * dimension,
            "isotropic_minimum_achieved_by_cotangent": True,
            "unrestricted_minimum_attained_known": False,
            "proof": "If R is the radical of the restricted form on g, r maps to (d+g -> B(r,d)) in (D/g)*. This is well-defined because B(r,g)=0 and injective because B is nondegenerate on D. Thus dim(D/g)>=dim R>=dim g-rank(B|g). For an isotropic embedding R=g, giving dim D>=2dim g."}


class PrincipalReesFamily:
    """The exact E8 family on the fixed 248-dimensional principal space.

    Public vectors use integer indices in ``basis_labels``.  ``bracket``
    defaults to the singular t=0 boundary.  For t != 0, ``scale`` is an
    isomorphism to the original principal E8 bracket.
    """
    dimension = 248

    def __init__(self, principal=None):
        self.principal = principal or PrincipalE8Basis()
        self.basis_labels = self.principal.basis_labels
        self.label_index = self.principal.label_index
        self.weights = {m: m - 1 for m in EXPONENTS}
        self.couplings = self.principal.couplings()
        self._classical_cache = {}

    def _index(self, index):
        if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < 248:
            raise ValueError("principal index outside 0..247")
        return index

    def _classical(self, left, right):
        self._index(left)
        self._index(right)
        if left == right:
            return {}
        if left > right:
            return {i: -x for i, x in self._classical(right, left).items()}
        key = (left, right)
        if key not in self._classical_cache:
            image = self.principal.polynomial_basis_bracket(
                self.basis_labels[left], self.basis_labels[right])
            self._classical_cache[key] = {self.label_index[k]: x for k, x in image.items()}
        return self._classical_cache[key]

    def polynomial_basis_bracket(self, left, right, weights=None):
        """Return output-index -> {parameter-power: exact coefficient}."""
        weights = self.weights if weights is None else _weights(weights)
        self._require_admissible(weights)
        a = self.basis_labels[self._index(left)][0]
        b = self.basis_labels[self._index(right)][0]
        return {index: {weights[a] + weights[b] - weights[self.basis_labels[index][0]]: value}
                for index, value in self._classical(left, right).items()}

    def polynomial_bracket(self, left, right, weights=None):
        """The polynomial family bracket of arbitrary exact sparse vectors."""
        left, right = _vector(left, 248), _vector(right, 248)
        weights = self.weights if weights is None else _weights(weights)
        self._require_admissible(weights)
        answer = {}
        for i, x in left.items():
            for j, y in right.items():
                a, b = self.basis_labels[i][0], self.basis_labels[j][0]
                for index, value in self._classical(i, j).items():
                    power = weights[a] + weights[b] - weights[self.basis_labels[index][0]]
                    polynomial = answer.setdefault(index, {})
                    polynomial[power] = polynomial.get(power, Q(0)) + x * y * value
                    if not polynomial[power]:
                        del polynomial[power]
        return {i: polynomial for i, polynomial in answer.items() if polynomial}

    def basis_bracket(self, left, right, t=0, weights=None):
        """Evaluate the polynomial family on two basis vectors."""
        t = _q(t)
        weights = self.weights if weights is None else _weights(weights)
        # All internally selected weights are already admissible.  Public
        # supplied weights are checked before evaluation, even at t != 0.
        if weights is not self.weights:
            self._require_admissible(weights)
        a = self.basis_labels[self._index(left)][0]
        b = self.basis_labels[self._index(right)][0]
        result = {}
        for index, value in self._classical(left, right).items():
            power = weights[a] + weights[b] - weights[self.basis_labels[index][0]]
            coefficient = value * t ** power
            if coefficient:
                result[index] = coefficient
        return result

    def bracket(self, left, right, t=0, weights=None):
        left, right = _vector(left, 248), _vector(right, 248)
        t = _q(t)
        weights = self.weights if weights is None else _weights(weights)
        self._require_admissible(weights)
        answer = {}
        for i, x in left.items():
            for j, y in right.items():
                a, b = self.basis_labels[i][0], self.basis_labels[j][0]
                for index, value in self._classical(i, j).items():
                    power = weights[a] + weights[b] - weights[self.basis_labels[index][0]]
                    coefficient = x * y * value * t ** power
                    if coefficient:
                        _add(answer, {index: coefficient})
        return answer

    def scale(self, vector, t, inverse=False, weights=None):
        """S_t b_(m,j)=t^w_m b_(m,j); inverse requires nonzero t."""
        vector, t = _vector(vector, 248), _q(t)
        weights = self.weights if weights is None else _weights(weights)
        if inverse and not t:
            raise ValueError("singular scaling has no inverse at t=0")
        if not t and any(weights[self.basis_labels[i][0]] < 0 for i in vector):
            raise ValueError("negative scaling power at t=0")
        result = {}
        for i, value in vector.items():
            power = weights[self.basis_labels[i][0]] * (-1 if inverse else 1)
            coefficient = value * t ** power
            if coefficient:
                result[i] = coefficient
        return result

    def verify_scaling(self, left, right, t, weights=None):
        t = _q(t)
        if not t:
            raise ValueError("scaling isomorphism is asserted only for nonzero t")
        lhs = self.scale(self.bracket(left, right, t, weights), t, weights=weights)
        rhs = self.principal.bracket(self.scale(left, t, weights=weights),
                                     self.scale(right, t, weights=weights))
        return {"valid": lhs == rhs, "parameter": str(t),
                "identity": "S_t [x,y]_t = [S_t x,S_t y]_E8"}

    def _require_admissible(self, weights):
        failed = [(a, b, c) for (a, b, c), value in self.couplings.items()
                  if value and weights[a] + weights[b] - weights[c] < 0]
        if failed:
            raise ValueError(f"negative channel valuation at {failed[0]}")

    def leading_support(self, weights=None):
        weights = self.weights if weights is None else _weights(weights)
        self._require_admissible(weights)
        return [{"left": a, "right": b, "output": c,
                 "coefficient": str(value), "transvectant_order": a + b - c}
                for (a, b, c), value in self.couplings.items()
                if value and weights[a] + weights[b] - weights[c] == 0]

    def valuation_receipt(self, weights):
        """Necessary and sufficient diagonal polynomial-extension criterion."""
        weights = _weights(weights)
        channels = [{"left": a, "right": b, "output": c,
                     "valuation": weights[a] + weights[b] - weights[c]}
                    for (a, b, c), value in self.couplings.items() if value]
        bad = [row for row in channels if row["valuation"] < 0]
        return {"weights": [[m, weights[m]] for m in EXPONENTS],
                "admissible": not bad, "constraints_checked": len(channels),
                "failed_channels": bad,
                "leading_channels": sum(row["valuation"] == 0 for row in channels),
                "criterion": "w_a+w_b-w_c >= 0 for every actual nonzero coupling; w_1=0",
                "necessary_and_sufficient": True}

    def _module_images(self, left, right, weights=None):
        left, right = set(left), set(right)
        return {row["output"] for row in self.leading_support(weights)
                if ((row["left"] in left and row["right"] in right)
                    or (row["right"] in left and row["left"] in right))}

    def structure_receipt(self):
        """Exact image-module certificates for the first-order boundary."""
        radical = set(EXPONENTS) - {1}
        lower, current = [], radical
        while current:
            lower.append({"spins": sorted(current), "dimension": sum(2 * m + 1 for m in current)})
            current = self._module_images(radical, current)
        lower.append({"spins": [], "dimension": 0})
        derived, current = [], radical
        while current:
            derived.append({"spins": sorted(current), "dimension": sum(2 * m + 1 for m in current)})
            current = self._module_images(current, current)
        derived.append({"spins": [], "dimension": 0})
        center = {m for m in radical if not self._module_images({m}, radical)}
        # Nonzero equivariant maps onto an irreducible target are surjective.
        # The following actual vectors witness every nonprincipal r=1 map.
        witnesses = []
        for row in self.leading_support():
            a, b, c = row["left"], row["right"], row["output"]
            if a == 1:
                continue
            i, j = self.label_index[a, 0], self.label_index[b, 1]
            image = self.basis_bracket(i, j)
            if set(image) != {self.label_index[c, 0]}:
                raise ArithmeticError("leading-channel highest-vector witness failed")
            witnesses.append({"channel": [a, b, c], "left_basis_index": i,
                              "right_basis_index": j, "image": _wire(image)})
        x = {self.label_index[7, 0]: Q(1)}
        chain = {self.label_index[11, 22]: Q(1)}
        chain_receipt = []
        for _ in range(3):
            chain = self.bracket(x, chain)
            if not chain:
                raise ArithmeticError("four-factor nilpotency witness vanished")
            chain_receipt.append(_wire(chain))
        return {"levi_factor": "sl2", "levi_dimension": 3,
                "nilradical_dimension": 245, "nilradical_lower_central": lower,
                "nilradical_derived": derived, "nilpotency_class": len(lower) - 1,
                "nilradical_center_spins": sorted(center),
                "nilradical_center_dimension": sum(2 * m + 1 for m in center),
                "nilradical_abelianization_spins": [7, 11],
                "nilradical_abelianization_dimension": 38,
                "full_algebra_perfect": self._module_images(set(EXPONENTS), set(EXPONENTS)) == set(EXPONENTS),
                "full_algebra_center_dimension": 0,
                "module_image_witnesses": witnesses,
                "four_factor_witness": {"repeated_input": _wire(x),
                                         "initial_input": [[self.label_index[11, 22], "1"]],
                                         "successive_images": chain_receipt},
                "proof": "Each block is irreducible under the verified principal sl2 action. A witnessed nonzero equivariant channel maps onto its whole target. Therefore module-support iteration computes exact lower-central and derived ideals. The center is an sl2-submodule; no trivial block occurs in the full algebra."}

    def cone_receipt(self):
        """Exact contraction cone plus complete small nonnegative-weight cuts.

        No extremal-ray or global orbit classification is claimed.  The
        ternary box contains only 2187 points, so it is checked completely.
        """
        binary, ternary, step_counts = [], 0, {}
        for entries in product(range(3), repeat=7):
            weights = dict(zip(EXPONENTS, (0,) + entries))
            if any(weights[a] + weights[b] < weights[c]
                   for (a, b, c), value in self.couplings.items() if value):
                continue
            ternary += 1
            if max(entries) <= 1:
                binary.append(list(entries))
            if any(entries):
                radical = set(EXPONENTS) - {1}
                first = self._module_images(radical, radical, weights)
                second = self._module_images(radical, first, weights) if first else set()
                if second:
                    raise ArithmeticError("ternary-cut radical exceeded class two")
                step = 2 if first else 1
                step_counts[step] = step_counts.get(step, 0) + 1
        # Zero in any nonprincipal coordinate forces the following closure.
        closures = []
        for m in EXPONENTS[1:]:
            closed = {1, m}
            while True:
                updated = closed | {c for (a, b, c), value in self.couplings.items()
                                    if value and a in closed and b in closed}
                if updated == closed:
                    break
                closed = updated
            if closed != set(EXPONENTS):
                raise ArithmeticError("zero-coordinate closure did not reach every block")
            closures.append({"starting_zero_spin": m, "forced_zero_spins": sorted(closed)})
        return {"variables": list(EXPONENTS[1:]), "constraint_count_with_multiplicity": 170,
                "dimension": 7, "pointed": True,
                "nonzero_weights_strictly_positive_on_nonprincipal_blocks": True,
                "zero_coordinate_closure_certificates": closures,
                "interior_point": [1] * 7,
                "binary_box_points_checked": 128, "binary_admissible_weights": binary,
                "ternary_box_points_checked": 2187, "ternary_admissible_count": ternary,
                "nonzero_ternary_cut_nilpotency_class_counts": {str(k): v for k, v in sorted(step_counts.items())},
                "proof": "Slots (m,m,1) force w_m>=0. A zero coordinate propagates through nonzero channels to every spin. All weights in {1,2}^7 are admissible because 1+1>=2; only all-zero weights add another ternary point. At the all-one point every nonprincipal inequality is strict, proving full dimension. Binary cuts are therefore exactly zero and all-one.",
                "scope": "Exact cone inequalities and complete binary/ternary boxes; extremal rays and isomorphism classes are not enumerated."}

    def invariant_form_receipt(self):
        return {"pulled_back_killing_block_valuations": [[m, 2 * (m - 1)] for m in EXPONENTS],
                "limiting_killing_rank": 3, "limiting_killing_radical_dimension": 245,
                "all_invariant_symmetric_forms_dimension": 1,
                "all_invariant_symmetric_forms_maximum_rank": 3,
                "nondegenerate_invariant_symmetric_form_exists": False,
                "proof": [
                    "The eight pairwise nonisomorphic irreducible sl2 modules are mutually orthogonal for any invariant symmetric bilinear form (Schur).",
                    "For m>1, the boundary bracket [V_m,V_m] has no V_1 component; hence B([s,x],y)=B(s,[x,y])=0 for all s in sl2 and x,y in V_m.",
                    "Since [sl2,V_m]=V_m, the entire V_m block is in the radical. This holds for every m>1.",
                    "The remaining form on V_1=sl2 is a scalar multiple of its Killing form and extends by zero. Thus the invariant-form space is exactly one-dimensional and every such form has rank zero or three."
                ],
                "monodromy_caution": "The punctured scaling gauge has integral weights, so this family alone supplies no nontrivial monodromy or physical observable."}


class CotangentLieAlgebra:
    """Reusable finite cotangent double g semidirect coadjoint(g*).

    Coordinates 0..n-1 are primal and n..2n-1 are dual.  The base callable
    must be a Lie bracket.  The canonical Jacobi and metric proofs reduce
    to base Jacobi, the transpose definition, and evaluation duality.
    """
    def __init__(self, dimension, bracket):
        if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1:
            raise ValueError("positive base dimension required")
        if not callable(bracket):
            raise ValueError("base bracket must be callable")
        self.base_dimension = dimension
        self.dimension = 2 * dimension
        self.base_bracket = bracket
        self._table = {}
        self._coadjoint_table = None

    def embed(self, vector):
        return _vector(vector, self.base_dimension)

    def dual(self, covector):
        return {i + self.base_dimension: value for i, value in _vector(covector, self.base_dimension).items()}

    def _base(self, left, right):
        key = (left, right)
        if key not in self._table:
            self._table[key] = _vector(self.base_bracket({left: Q(1)}, {right: Q(1)}), self.base_dimension)
        return self._table[key]

    def _ensure_coadjoint(self):
        if self._coadjoint_table is not None:
            return
        n = self.base_dimension
        table = {}
        for i in range(n):
            for j in range(n):
                for k, coefficient in self._base(i, j).items():
                    table.setdefault((i, k), {})[j] = -coefficient
        self._coadjoint_table = table

    def coadjoint(self, vector, covector):
        vector = _vector(vector, self.base_dimension)
        covector = _vector(covector, self.base_dimension)
        self._ensure_coadjoint()
        result = {}
        for i, x in vector.items():
            for k, y in covector.items():
                _add(result, self._coadjoint_table.get((i, k), {}), x * y)
        return result

    def bracket(self, left, right):
        left, right = _vector(left, self.dimension), _vector(right, self.dimension)
        n = self.base_dimension
        x, xi = {}, {}
        y, eta = {}, {}
        for i, value in left.items():
            (x if i < n else xi)[i if i < n else i - n] = value
        for i, value in right.items():
            (y if i < n else eta)[i if i < n else i - n] = value
        primal = _vector(self.base_bracket(x, y), n)
        dual = self.coadjoint(x, eta)
        _add(dual, self.coadjoint(y, xi), -1)
        _add(primal, {n + i: value for i, value in dual.items()})
        return primal

    def pairing(self, left, right):
        left, right = _vector(left, self.dimension), _vector(right, self.dimension)
        n = self.base_dimension
        return sum((value * right.get(i + n if i < n else i - n, Q(0))
                    for i, value in left.items()), Q(0))

    def verify_quadratic(self):
        """Full finite skew/transpose check and an algebraic metric certificate.

        This does not silently certify an arbitrary input bracket's Jacobi.
        Cotangent Jacobi is a theorem conditional on base Jacobi, which the
        E8 boundary receipt certifies independently.
        """
        self._ensure_coadjoint()
        n = self.base_dimension
        nonzero, transpose_checks = 0, 0
        for i in range(n):
            if self._base(i, i):
                raise ArithmeticError("base bracket is not alternating")
            for j in range(n):
                vector = self._base(i, j)
                reverse = self._base(j, i)
                if vector != {k: -value for k, value in reverse.items()}:
                    raise ArithmeticError("base bracket is not skew")
                for k, value in vector.items():
                    if self._coadjoint_table.get((i, k), {}).get(j) != -value:
                        raise ArithmeticError("coadjoint transpose identity failed")
                    transpose_checks += 1
                nonzero += len(vector)
        return {"dimension": 2 * n, "base_dimension": n,
                "gram_matrix": "[[0,I],[I,0]]", "pairing_rank": 2 * n,
                "real_signature": [n, n], "primal_and_dual_isotropic": True,
                "base_ordered_pairs_checked": n * n,
                "coadjoint_nonzero_transpose_entries_checked": transpose_checks,
                "base_ordered_structure_terms": nonzero,
                "dual_ideal_abelian": True,
                "jacobi_scope": "Cotangent Jacobi follows from separately verified base Jacobi; arbitrary base Jacobi is not asserted here.",
                "invariance_proof": "<[(x,xi),(y,eta)],(z,zeta)>=zeta([x,y])-eta([x,z])+xi([y,z]), which equals <(x,xi),[(y,eta),(z,zeta)]> by base skew symmetry.",
                "jacobi_proof": "The dual part of Jacobi is the representation identity [ad_x^*,ad_y^*]=ad_[x,y]^*, the transpose of base Jacobi; primal Jacobi is base Jacobi.",
                "passed": True}


def boundary_receipt(exhaustive=False):
    """JSON-safe complete boundary, cone, and 496-dimensional double receipt."""
    family = PrincipalReesFamily()
    transport = family.principal.verify(exhaustive=exhaustive)
    base_jacobi = family.principal.algebra.verify_jacobi("full" if exhaustive else "generators")
    valuations = family.valuation_receipt(family.weights)
    if not valuations["admissible"] or not base_jacobi["passed"]:
        raise ArithmeticError("Rees-family prerequisites failed")
    support = family.leading_support()
    quadratic = CotangentLieAlgebra(248, family.bracket).verify_quadratic()
    return {"schema": "perfectjet.asterion.boundary.v1",
            "passed": (transport["all_checks_passed"] and base_jacobi["passed"]
                       and valuations["admissible"] and quadratic["passed"]),
            "status": "exact computed E8 principal Rees boundary; classical construction mechanisms",
            "arithmetic": "fractions.Fraction; no floating point",
            "dimension": 248, "parameter": "t",
            "weights": [[m, m - 1] for m in EXPONENTS],
            "leading_channel_count": len(support),
            "higher_channel_count": len(family.couplings) - len(support),
            "leading_support": support,
            "valuation_certificate": valuations,
            "principal_transport": transport,
            "source_e8_jacobi": base_jacobi,
            "all_parameter_jacobi_proof": {
                "identity": "[x_a,y_b]_t=S_t^-1[S_t x_a,S_t y_b]_E8 for t!=0; all channel exponents are nonnegative integers",
                "nested_bracket_exponent": "w_a+w_b+w_c-w_d, independent of intermediate spin",
                "argument": "Each fixed input/output Jacobi coefficient is a polynomial in t and vanishes for every nonzero rational t by the exact gauge identity and E8 Jacobi. It is therefore the zero polynomial and also vanishes at t=0.",
                "all_parameter_jacobi_established": True,
                "computational_scope": "Full source-triple and basis-pair replay when exhaustive=true; otherwise source Jacobi is generator-panel replay plus the classical lattice-cocycle E8 construction, with that scope stated explicitly.",
            },
            "boundary_structure": family.structure_receipt(),
            "invariant_forms": family.invariant_form_receipt(),
            "quadratic_completion_bounds": quadratic_completion_bound(248, 3),
            "diagonal_contraction_cone": family.cone_receipt(),
            "cotangent_double": quadratic,
            "limitations": [
                "For nonzero t the family is isomorphic to E8; no new simple Lie algebra or punctured-family monodromy is claimed.",
                "The first-order limit uses projected, channel-weighted transvectants; its eight degrees are not an unrestricted ordinary Poisson subalgebra.",
                "Cone inequalities are exact; global extremal-ray, contraction-isomorphism, cohomology, and compatible connection classifications remain open tasks.",
                "The cotangent construction and contraction mechanism are classical; no literature priority claim is made for the E8-specific computed presentation."
            ]}


__all__ = ["PrincipalReesFamily", "CotangentLieAlgebra", "quadratic_completion_bound", "boundary_receipt"]
