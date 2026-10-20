"""Exact affine E8 currents and all-degree Jordan-refined state populations.

Finite E8 has no neutral Jordan component. Its affine central generator and
its vertex algebra do: the vacuum has degree zero, and composite neutral
states occur from conformal weight two. These are distinct gradings.

The population identities are classical representation/modular-form facts,
implemented here with exact series arithmetic and finite replay certificates.
In particular, they are not a new sphere-packing density theorem.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import comb, isqrt, pi, sqrt
from typing import Mapping

from .asterion_jordan import Cyclotomic5, GRADES, LABELS, ONE, ZERO, ZETA_POWERS, JordanE8, grade_add
from .asterion_transport import E8ChartTransport

ALL_GRADES = ((0, 0, 0),) + GRADES


def _degree(value):
    if not isinstance(value, int) or value < 0:
        raise ValueError("a nonnegative integer maximum degree is required")
    return value


def _convolution(left, right, maximum):
    return tuple(sum(left[j]*right[n-j] for j in range(n+1))
                 for n in range(maximum+1))


@lru_cache(maxsize=256)
def euler_product_coefficients(exponents, max_degree):
    """Coefficients of product_d product_(n>=1) (1-q**(d*n))**r_d.

    ``exponents`` is a hashable tuple of (positive step, integer exponent).
    Every omitted factor starts above the truncation, so the result is exact.
    """
    maximum = _degree(max_degree)
    exponents = tuple(exponents)
    if any(not isinstance(step, int) or step <= 0 or not isinstance(power, int)
           for step, power in exponents):
        raise ValueError("positive integer steps and integer exponents are required")
    out = [1]+[0]*maximum
    for part in range(1, maximum+1):
        exponent = sum(power for step, power in exponents if part % step == 0)
        if not exponent:
            continue
        before = out[:]
        limit = min(exponent, maximum//part) if exponent > 0 else maximum//part
        for count in range(1, limit+1):
            coefficient = ((-1)**count*comb(exponent, count) if exponent > 0
                           else comb(-exponent+count-1, count))
            for n in range(count*part, maximum+1):
                out[n] += coefficient*before[n-count*part]
    return tuple(out)


def colored_partitions(colors, max_degree):
    if not isinstance(colors, int) or colors < 0:
        raise ValueError("a nonnegative integer number of colors is required")
    return euler_product_coefficients(((1, -colors),), max_degree)


@lru_cache(maxsize=128)
def e4_coefficients(max_degree):
    maximum = _degree(max_degree)
    coefficients = [0]*(maximum+1)
    coefficients[0] = 1
    for divisor in range(1, maximum+1):
        for n in range(divisor, maximum+1, divisor):
            coefficients[n] += 240*divisor**3
    return tuple(coefficients)


@lru_cache(maxsize=64)
def a4_theta_coefficients(max_degree):
    """Enumerate A4={(x0,...,x4) in Z^5:sum x_i=0}, by norm/2.

    Each coordinate is bounded by floor(sqrt(2*N)); dynamic convolution of
    the five labeled coordinates is therefore a complete finite enumeration.
    """
    maximum = _degree(max_degree)
    bound = isqrt(2*maximum)
    states = {(0, 0): 1}
    for used in range(1, 6):
        next_states = {}
        remaining = 5-used
        for (total, norm), count in states.items():
            for coordinate in range(-bound, bound+1):
                new_norm, new_total = norm+coordinate*coordinate, total+coordinate
                if new_norm <= 2*maximum and abs(new_total) <= remaining*bound:
                    key = new_total, new_norm
                    next_states[key] = next_states.get(key, 0)+count
        states = next_states
    return tuple(states.get((0, 2*n), 0) for n in range(maximum+1))


def eta_twining_certificate(max_degree=12):
    """Replay the finite Sturm certificate behind the all-order twine.

    Both forms are holomorphic in M4(Gamma0(5)), with trivial character.
    The index is six, so the weight-four bound is two. Eta exponents (10,-2)
    meet Newman's conditions and have cusp orders 0 and 2. Equality of the
    coefficients through q^2 therefore implies equality to all orders.
    """
    maximum = max(_degree(max_degree), 2)
    theta = a4_theta_coefficients(maximum)
    square = _convolution(theta, theta, maximum)
    eisenstein = e4_coefficients(maximum)
    left = tuple(Fraction(5*square[n]-eisenstein[n], 4) for n in range(maximum+1))
    right = euler_product_coefficients(((1, 10), (5, -2)), maximum)
    return {"passed": left == right,
            "identity": "(5*Theta_A4^2-E4)/4 = eta(tau)^10/eta(5*tau)^2",
            "weight": 4, "level": 5, "character": "trivial",
            "group_index": 6, "sturm_bound": 2,
            "coefficients_through_sturm_bound": [str(value) for value in left[:3]],
            "eta_exponents": {"1": 10, "5": -2},
            "newman_mod24_sums": [0, 48], "cusp_orders": {"infinity": 0, "zero": 2},
            "a4_theta_modularity": {"rank": 4, "gram_determinant": 5,
                                     "level": 5, "character": "Legendre(d/5)"},
            "independent_lattice_coefficients_replayed_through": maximum,
            "all_order_conclusion_uses_modularity_and_sturm_theorem": True,
            "simple_twining": "phi(q)^2/phi(q^5)^2"}


def finite_fourier_projector_certificate():
    """Exact character orthogonality for all 125 differences in F5^3.

    Each entry of F F* depends only on the difference of two grade labels.
    These 125 calculations therefore verify all 15,625 matrix entries.
    """
    for difference in ALL_GRADES:
        multiplicities = [0]*5
        for element in ALL_GRADES:
            exponent = sum(a*b for a, b in zip(difference, element)) % 5
            multiplicities[exponent] += 1
        trace = sum((multiplicities[i]*ZETA_POWERS[i] for i in range(5)), ZERO)
        expected = Cyclotomic5(125 if difference == (0, 0, 0) else 0)
        if trace != expected:
            return {"passed": False, "difference": difference}
    return {"passed": True, "characters": 125, "difference_checks": 125,
            "fourier_gram_matrix_entries_certified": 15625,
            "projector_denominator": 125,
            "identity": "F*conjugate(transpose(F))=125*I",
            "all_order_rank_formulas": ["rank(P_0)=(Z+124*T)/125", "rank(P_a)=(Z-T)/125 for a!=0"]}


class CurrentPopulations:
    """Exact populations for the universal and simple level-one vacuum modules.

    Every nonzero Jordan grade has the same dimension. This equality follows
    from conjugacy of the 124 nonidentity automorphisms, not from an observed
    numerical coincidence or a nonnegativity check.
    """

    def __init__(self, max_degree=12):
        self.max_degree = maximum = _degree(max_degree)
        self.simple = _convolution(e4_coefficients(maximum), colored_partitions(8, maximum), maximum)
        self.universal = colored_partitions(248, maximum)
        self.simple_twine = euler_product_coefficients(((1, 2), (5, -2)), maximum)
        self.universal_twine = euler_product_coefficients(((1, 2), (5, -50)), maximum)
        self.relations = tuple(u-s for u, s in zip(self.universal, self.simple))
        self.relation_twine = tuple(u-s for u, s in zip(self.universal_twine, self.simple_twine))
        self._graded = {}
        for kind in ("simple", "universal", "relations"):
            totals = getattr(self, kind)
            twine = getattr(self, "relation_twine" if kind == "relations" else kind+"_twine")
            neutral, nonzero = [], []
            for total, trace in zip(totals, twine):
                zero_num, nonzero_num = total+124*trace, total-trace
                if zero_num % 125 or nonzero_num % 125:
                    raise ArithmeticError("finite Fourier projection is not integral")
                zero, each = zero_num//125, nonzero_num//125
                if min(zero, each) < 0 or zero+124*each != total:
                    raise ArithmeticError("graded population reconstruction failed")
                neutral.append(zero)
                nonzero.append(each)
            self._graded[kind] = tuple(neutral), tuple(nonzero)

    def graded_dimension(self, degree, grade, kind="simple"):
        if kind not in self._graded:
            raise ValueError("kind must be simple, universal, or relations")
        if not isinstance(degree, int) or not 0 <= degree <= self.max_degree:
            raise ValueError("degree is outside this computed truncation")
        if len(grade) != 3 or any(not isinstance(x, int) for x in grade):
            raise ValueError("a three-component integer grade is required")
        normalized = tuple(x % 5 for x in grade)
        return self._graded[kind][0 if normalized == (0, 0, 0) else 1][degree]

    def distribution(self, degree, kind="simple"):
        return {grade: self.graded_dimension(degree, grade, kind) for grade in ALL_GRADES}

    def rows(self):
        rows = []
        for n in range(self.max_degree+1):
            simple_zero, simple_each = (values[n] for values in self._graded["simple"])
            universal_zero, universal_each = (values[n] for values in self._graded["universal"])
            relation_zero, relation_each = (values[n] for values in self._graded["relations"])
            rows.append({"degree": n, "simple": self.simple[n], "universal": self.universal[n],
                         "relations": self.relations[n],
                         "retention_exact": str(Fraction(self.simple[n], self.universal[n])),
                         "simple_neutral": simple_zero, "simple_each_nonzero": simple_each,
                         "universal_neutral": universal_zero, "universal_each_nonzero": universal_each,
                         "relations_neutral": relation_zero, "relations_each_nonzero": relation_each,
                         "relation_neutral_minus_each_nonzero": self.relation_twine[n],
                         "neutral_retention_exact": (str(Fraction(simple_zero, universal_zero))
                                                       if universal_zero else None),
                         "nonzero_retention_exact": (str(Fraction(simple_each, universal_each))
                                                       if universal_each else None)})
        return rows

    def receipt(self):
        return {"max_degree": self.max_degree, "rows": self.rows(),
                "finite_jordan_neutral_dimension": 0,
                "vertex_vacuum_neutral_dimension": 1,
                "total_character": "E4(q)/phi(q)^8",
                "simple_nonidentity_twine": "phi(q)^2/phi(q^5)^2",
                "universal_nonidentity_twine": "phi(q)^2/phi(q^5)^50",
                "nontrivial_automorphism_eigenmultiplicities": [48, 50, 50, 50, 50],
                "projection": {"neutral": "(Z+124*T)/125", "each_nonzero": "(Z-T)/125"},
                "all_order_refinement_proof":
                    "Elduque order-five conjugacy; index-five A4^2 gluing; finite character orthogonality; Sturm bound two",
                "first_nonuniform_relation_degree": 5,
                "first_nonuniform_relation_neutral_excess": 48,
                "all_order_relation_trace_identity": "phi(q)^2*(phi(q^5)^(-50)-phi(q^5)^(-2))",
                "asymptotic_log_growth": {"simple_sqrt_n_coefficient": "4*pi/sqrt(3)",
                    "universal_sqrt_n_coefficient": "2*pi*sqrt(248/6)",
                    "retention_sqrt_n_coefficient_approx": 2*pi*(sqrt(8/6)-sqrt(248/6)),
                    "sugawara_central_charge": 8,
                    "universal_colored_partition_growth_parameter": 248,
                    "new_geometric_density_claim": False}}


def _put(out, key, value):
    if value:
        result = out.get(key, ZERO)+value
        if result:
            out[key] = result
        else:
            out.pop(key, None)


def _field_rank(vectors):
    """Sparse exact row reduction over Q(zeta_5), including actual pivots."""
    echelon = {}
    for source in vectors:
        row = {key: Cyclotomic5(value) for key, value in source.items() if value}
        while row:
            pivot = min(row)
            coefficient = row[pivot]
            if pivot not in echelon:
                echelon[pivot] = {key: value/coefficient for key, value in row.items()}
                break
            for key, value in echelon[pivot].items():
                _put(row, key, -coefficient*value)
    return len(echelon)


def encode_quadratic_state(state):
    return [{"left": list(left), "right": list(right),
             "coefficient": Cyclotomic5(value).to_json()}
            for (left, right), value in sorted(state.items()) if value]


class AffineE8Currents:
    """Jordan-labeled affine currents with the degree derivation.

    Current keys are ("J", mode, i,p,q,r); the other keys are "K" and "d".
    K is the central identity with prescribed level. Setting level=1 is the
    usual normalized central extension; other levels scale its cocycle.
    """

    def __init__(self, level=1, jordan=None):
        self.level = Fraction(level)
        self.jordan = jordan if jordan is not None else JordanE8()
        self.transport = E8ChartTransport(jordan=self.jordan)
        self._coordinates = {}
        self._metric_cache = {}
        self._opposite_roots = {index: self.transport.chevalley.root_index[tuple(-x for x in root)]
                                for index, root in self.transport.chevalley.index_root.items()}

    @staticmethod
    def _current(label, mode):
        if not isinstance(mode, int):
            raise ValueError("an integer current mode is required")
        label = JordanE8._label(label)
        return ("J", mode, *label)

    def basis_current(self, label, mode=0):
        return {self._current(label, mode): ONE}

    @staticmethod
    def central():
        return {"K": ONE}

    @staticmethod
    def derivation():
        return {"d": ONE}

    def _coordinates_for(self, label):
        if label not in self._coordinates:
            self._coordinates[label] = self.transport.jordan_to_chevalley({label: ONE})
        return self._coordinates[label]

    def metric(self, left, right):
        """Normalized Killing form: (h_i,h_j)=A_ij, (e_alpha,e_-alpha)=1."""
        left, right = JordanE8._label(left), JordanE8._label(right)
        key = tuple(sorted((left, right)))
        if key not in self._metric_cache:
            x, y = self._coordinates_for(left), self._coordinates_for(right)
            value = ZERO
            for i, a in x.items():
                if i < 8:
                    for j, b in y.items():
                        if j < 8 and self.transport.chevalley.cartan_matrix[i][j]:
                            value += a*b*self.transport.chevalley.cartan_matrix[i][j]
                elif self._opposite_roots[i] in y:
                    value += a*y[self._opposite_roots[i]]
            self._metric_cache[key] = value
        return self._metric_cache[key]

    @staticmethod
    def _key(key):
        if key in ("K", "d"):
            return key
        if not isinstance(key, tuple) or len(key) != 6 or key[0] != "J":
            raise ValueError("a current key, K, or d is required")
        return AffineE8Currents._current(key[2:], key[1])

    def bracket(self, left: Mapping, right: Mapping):
        out = {}
        for a, x in left.items():
            a = self._key(a)
            for b, y in right.items():
                b = self._key(b)
                factor = Cyclotomic5(x)*Cyclotomic5(y)
                if a == "K" or b == "K" or a == b == "d":
                    continue
                if a == "d":
                    _put(out, b, factor*b[1])
                elif b == "d":
                    _put(out, a, -factor*a[1])
                else:
                    first, second = a[2:], b[2:]
                    mode = a[1]+b[1]
                    for label, value in self.jordan.basis_bracket(first, second).items():
                        _put(out, self._current(label, mode), factor*value)
                    if mode == 0 and a[1]:
                        _put(out, "K", factor*self.level*a[1]*self.metric(first, second))
        return out

    def jacobi(self, left, middle, right):
        out = {}
        for x, y, z in ((left, middle, right), (middle, right, left), (right, left, middle)):
            for key, value in self.bracket(self.bracket(x, y), z).items():
                _put(out, key, value)
        return out

    def cartan_conformal_states(self):
        """31 Heisenberg conformal states and 30 explicit level-one nulls.

        Keys are unordered pairs of labels, representing J_left[-1]
        J_right[-1]|0>. Each pair lies in one abelian Cartan line, so its
        ordering produces no commutator correction. The states are independent
        in the universal PBW space, and all become the same conformal vector
        in L1(E8), by Cartan conjugacy and the rank-eight lattice construction.
        """
        if self.level != 1:
            raise ValueError("these simple-quotient conformal relations are at level one")
        states = []
        for line in self.jordan.cartan_lines():
            state = {}
            for label in line:
                partners = [(other, self.metric(label, other)) for other in line
                            if self.metric(label, other)]
                if len(partners) != 1:
                    raise ArithmeticError("Cartan Gram matrix must have a unique monomial dual")
                other, pairing = partners[0]
                monomial = tuple(sorted((label, other)))
                _put(state, monomial, ONE/(2*pairing))
            states.append(state)
        relations = []
        for state in states[1:]:
            relation = dict(state)
            for monomial, coefficient in states[0].items():
                _put(relation, monomial, -coefficient)
            relations.append(relation)
        total = {}
        for state in states:
            for monomial, coefficient in state.items():
                _put(total, monomial, coefficient)
        sugawara = {monomial: coefficient/31 for monomial, coefficient in total.items()}
        return {"cartan_states": tuple(states), "null_relations": tuple(relations),
                "sugawara_state": sugawara}

    def cartan_conformal_receipt(self, *, include_coefficients=False):
        data = self.cartan_conformal_states()
        states, relations = data["cartan_states"], data["null_relations"]
        state_rank, relation_rank = _field_rank(states), _field_rank(relations)
        neutral = all(grade_add(left[:3], right[:3]) == (0, 0, 0)
                      for state in (*states, *relations) for left, right in state)
        global_casimir = {}
        for label in LABELS:
            for other in LABELS:
                pairing = self.metric(label, other)
                if pairing:
                    _put(global_casimir, tuple(sorted((label, other))), ONE/(2*pairing))
        mean_identity = global_casimir == {monomial: 31*coefficient
            for monomial, coefficient in data["sugawara_state"].items()}
        commuting = self.jordan.verify_cartans()
        difference_rank = _field_rank([*relations, {
            monomial: sum(state.get(monomial, ZERO) for state in states)-31*states[0].get(monomial, ZERO)
            for monomial in global_casimir}])
        record = {"passed": (len(states) == state_rank == 31
                               and len(relations) == relation_rank == difference_rank == 30
                               and neutral and mean_identity and commuting["passed"]),
                  "cartan_conformal_states": len(states), "universal_state_rank": state_rank,
                  "explicit_quadratic_null_relations": len(relations),
                  "explicit_relation_rank": relation_rank,
                  "all_support_has_neutral_jordan_grade": neutral,
                  "all_within_line_brackets_replayed": commuting["ambient_brackets_checked"],
                  "global_sugawara_average_identity": mean_identity,
                  "sugawara_denominator": 31,
                  "denominator_31_eliminated_modulo_these_relations": difference_rank == relation_rank,
                  "nullity_in_simple_quotient_dependency":
                      "rank-eight lattice Heisenberg conformal vector equals E8 conformal vector; all Cartans are inner conjugate",
                  "neutral_quadratic_nullspace_dimension": 216,
                  "remaining_neutral_quadratic_nullspace_dimension": 216-relation_rank,
                  "exhaustive_nullspace_claim": False}
        if include_coefficients:
            record["cartan_states"] = [encode_quadratic_state(state) for state in states]
            record["null_relations"] = [encode_quadratic_state(state) for state in relations]
            record["sugawara_state"] = encode_quadratic_state(data["sugawara_state"])
        return record

    def verify_metric(self):
        nonzero, counts = 0, {label: 0 for label in LABELS}
        for i, left in enumerate(LABELS):
            for right in LABELS[i:]:
                value = self.metric(left, right)
                if value:
                    if grade_add(left[:3], right[:3]) != (0, 0, 0):
                        return {"passed": False, "failure": "non-opposite grades paired"}
                    nonzero += 1 if left == right else 2
                    counts[left] += 1
                    if left != right:
                        counts[right] += 1
        return {"passed": all(count == 1 for count in counts.values()),
                "basis_pairings_computed": 248*249//2,
                "nonzero_ordered_pairings": nonzero,
                "opposite_grade_blocks": 62,
                "nondegenerate_monomial_pairing": all(count == 1 for count in counts.values()),
                "normalization": "Killing form divided by 60"}

    def verify_metric_invariance(self):
        """All 122,016 potentially nonzero ordered basis invariance triples.

        Other triples vanish by the independently checked grade orthogonality.
        Integer cyclotomic products are precomputed after one common rational
        denominator is cleared, so the replay is exact.
        """
        metric_receipt = self.verify_metric()
        if not metric_receipt["passed"]:
            return {"passed": False, "metric": metric_receipt}
        n = len(LABELS)
        index = {label: i for i, label in enumerate(LABELS)}
        raw_brackets = {(i, j): self.jordan.basis_bracket(LABELS[i], LABELS[j])
                        for i, j in combinations(range(n), 2)}
        raw_metric = {(i, j): self.metric(a, b) for i, a in enumerate(LABELS)
                      for j, b in enumerate(LABELS) if grade_add(a[:3], b[:3]) == (0, 0, 0)}
        values = [value for result in raw_brackets.values() for value in result.values()]
        values += [value for value in raw_metric.values() if value]
        from math import lcm
        denominator = 1
        for value in values:
            for q in value.coefficients:
                denominator = lcm(denominator, q.denominator)
        coefficients, ids = [], {}

        def intern(value):
            if value not in ids:
                ids[value] = len(coefficients)
                coefficients.append(value)
            return ids[value]

        table = [() for _ in range(n*n)]
        for (i, j), result in raw_brackets.items():
            table[n*i+j] = tuple((index[label], intern(tuple(int(q*denominator)
                for q in value.coefficients))) for label, value in result.items())
            table[n*j+i] = tuple((index[label], intern(tuple(-int(q*denominator)
                for q in value.coefficients))) for label, value in result.items())
        gram = {(i, j): intern(tuple(int(q*denominator) for q in value.coefficients))
                for (i, j), value in raw_metric.items() if value}

        def multiply(left, right):
            out = [0]*7
            for i, a in enumerate(left):
                for j, b in enumerate(right):
                    out[i+j] += a*b
            for k in range(6, 3, -1):
                for j in range(4):
                    out[k-4+j] -= out[k]
            return tuple(out[:4])

        products = [[multiply(a, b) for b in coefficients] for a in coefficients]
        checked = 0
        for i, a in enumerate(LABELS):
            for j, b in enumerate(LABELS):
                target = tuple(-x % 5 for x in grade_add(a[:3], b[:3]))
                if target == (0, 0, 0):
                    continue
                for fiber in range(2):
                    k = index[(*target, fiber)]
                    residual = [0]*4
                    for output, coefficient in table[n*i+j]:
                        pairing = gram.get((output, k))
                        if pairing is not None:
                            value = products[coefficient][pairing]
                            for r in range(4):
                                residual[r] += value[r]
                    for output, coefficient in table[n*j+k]:
                        pairing = gram.get((i, output))
                        if pairing is not None:
                            value = products[coefficient][pairing]
                            for r in range(4):
                                residual[r] -= value[r]
                    checked += 1
                    if any(residual):
                        return {"passed": False, "triples_checked": checked,
                                "counterexample": [i, j, k], "integer_residual": residual}
        return {"passed": True, "triples_checked": checked,
                "all_other_triples_zero_by_verified_grade_orthogonality": True,
                "common_coefficient_denominator": denominator,
                "affine_cocycle_jacobi_for_all_integer_modes": True,
                "finite_E8_jacobi_source": "JordanE8; exhaustive finite Jacobi is certified separately"}


def encode_current_vector(vector):
    return [{"key": list(key) if isinstance(key, tuple) else key,
             "coefficient": Cyclotomic5(value).to_json()}
            for key, value in sorted(vector.items(), key=lambda pair: repr(pair[0])) if value]


def currents_receipt(max_degree=12, *, verify_currents=True, include_coefficients=False):
    populations = CurrentPopulations(max_degree)
    identity = eta_twining_certificate(max_degree)
    projectors = finite_fourier_projector_certificate()
    receipt = {"passed": identity["passed"] and projectors["passed"], "populations": populations.receipt(),
               "eta_twining_identity": identity,
               "finite_fourier_projectors": projectors,
               "classical_construction": True, "new_density_theorem_claim": False,
               "sources": ["https://arxiv.org/pdf/0810.2737",
                           "https://arxiv.org/pdf/hep-th/0701244",
                           "https://math.jhu.edu/~savitt/papers/pdfs/newman.pdf",
                           "https://www.lmfdb.org/knowledge/show/cmf.sturm_bound"]}
    if verify_currents:
        currents = AffineE8Currents()
        metric = currents.verify_metric()
        invariance = currents.verify_metric_invariance()
        receipt["metric"] = metric
        receipt["metric_invariance"] = invariance
        conformal = currents.cartan_conformal_receipt(include_coefficients=include_coefficients)
        receipt["cartan_conformal_relations"] = conformal
        receipt["passed"] = receipt["passed"] and metric["passed"] and invariance["passed"] and conformal["passed"]
    return receipt


__all__ = ["AffineE8Currents", "CurrentPopulations", "currents_receipt",
           "eta_twining_certificate", "euler_product_coefficients", "colored_partitions",
           "e4_coefficients", "a4_theta_coefficients", "encode_current_vector", "ALL_GRADES",
           "finite_fourier_projector_certificate", "encode_quadratic_state"]
