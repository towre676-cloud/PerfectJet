"""Reduced principal E8 tangent rigidity with explicit rational gauge data.

The gauge matrices and equivalent sparse tangent constraints are computed.
One complete proof uses Whitehead and complete reducibility explicitly.
The exhaustive receipt independently compiles literal Jacobi rows giving
ranks155 and162 with matching global gauge bounds, without Whitehead.
The full grid of reduced Jacobi rows is not claimed to be assembled.
"""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import combinations_with_replacement
from math import comb, gcd, lcm

from .asterion_principal import EXPONENTS, PrincipalE8Basis, coupling_slots, monomial_transvectant
from .exact import rank


def _q(value):
    if isinstance(value, (float, bool)):
        raise ValueError("exact rational coefficients required")
    try:
        return Q(value)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        raise ValueError("exact rational coefficients required") from exc


def _add(target, source, scale=1):
    for i, value in source.items():
        target[i] = target.get(i, Q(0)) + scale * value
        if not target[i]:
            del target[i]


def _wire(vector):
    return [[i, str(x)] for i, x in sorted(vector.items())]


def _primitive_integer(vector):
    vector = {i: _q(x) for i, x in vector.items() if x}
    if not vector:
        return {}
    denominator = lcm(*(x.denominator for x in vector.values()))
    integers = {i: int(x * denominator) for i, x in vector.items()}
    divisor = gcd(*(abs(x) for x in integers.values()))
    sign = -1 if integers[min(integers)] < 0 else 1
    return {i: sign * x // divisor for i, x in integers.items()}


class _IntegerRowSpan:
    """Exact fraction-free row elimination with primitive content removal."""
    def __init__(self):
        self.rows, self.pivots = [], []

    def add(self, vector):
        vector = _primitive_integer(vector)
        for pivot, old in zip(self.pivots, self.rows):
            coefficient = vector.get(pivot, 0)
            if coefficient:
                residual = {i: value * old[pivot] for i, value in vector.items()}
                for i, value in old.items():
                    residual[i] = residual.get(i, 0) - coefficient * value
                vector = _primitive_integer(residual)
            if not vector:
                return False
        if not vector:
            return False
        self.pivots.append(min(vector))
        self.rows.append(vector)
        return True


class PrincipalRigidity:
    """Actual diagonal gauges and complete theorem-dependent tangent tests."""
    def __init__(self, principal=None):
        self.principal = principal or PrincipalE8Basis()
        self.couplings = self.principal.couplings()
        self.slots = coupling_slots()
        self.principal_slots = tuple((1, m, m) for m in EXPONENTS)
        self._systems = {}

    def _system(self, fixed=False):
        if type(fixed) is not bool:
            raise ValueError("fixed must be a Boolean")
        if fixed in self._systems:
            return self._systems[fixed]
        slots = tuple(slot for slot in self.slots if not fixed or slot not in self.principal_slots)
        positions = {slot: i for i, slot in enumerate(slots)}
        spins = EXPONENTS[1:] if fixed else EXPONENTS
        matrix = []
        for a, b, c in slots:
            matrix.append(tuple(self.couplings[a, b, c]
                                * (int(a == m) + int(b == m) - int(c == m)) for m in spins))
        pivots = tuple((m, m, 1) for m in EXPONENTS[1:])
        if not fixed:
            pivots = ((1, 1, 1),) + pivots
        pivot_positions = tuple(positions[slot] for slot in pivots)
        recovery = []
        for m in spins:
            if m == 1:
                row = {positions[1, 1, 1]: 1 / self.couplings[1, 1, 1]}
            else:
                row = {positions[m, m, 1]: 1 / (2 * self.couplings[m, m, 1])}
                if not fixed:
                    row[positions[1, 1, 1]] = 1 / (2 * self.couplings[1, 1, 1])
            recovery.append(row)
        constraints = []
        nonpivots = tuple(j for j in range(len(slots)) if j not in pivot_positions)
        for j in nonpivots:
            row = {j: Q(1)}
            for coefficient, inverse_row in zip(matrix[j], recovery):
                _add(row, inverse_row, -coefficient)
            constraints.append(row)
        result = {"slots": slots, "positions": positions, "spins": spins,
                  "matrix": tuple(matrix), "pivot_slots": pivots,
                  "pivot_positions": pivot_positions, "recovery": tuple(recovery),
                  "constraint_rows": tuple(constraints), "nonpivot_positions": nonpivots}
        self._systems[fixed] = result
        return result

    def diagonal_gauge_matrix(self, fixed=False):
        system = self._system(fixed)
        return {"slots": system["slots"], "gauge_spins": system["spins"],
                "matrix": system["matrix"]}

    def infinitesimal_gauge(self, scalars, fixed=False):
        system = self._system(fixed)
        scalars = tuple(map(_q, scalars))
        if len(scalars) != len(system["spins"]):
            raise ValueError("gauge scalar count differs")
        return {slot: value for slot, row in zip(system["slots"], system["matrix"])
                if (value := sum((x * y for x, y in zip(row, scalars)), Q(0)))}

    def finite_diagonal_gauge(self, scalars):
        scalars = tuple(map(_q, scalars))
        if len(scalars) != 8 or not all(scalars):
            raise ValueError("eight nonzero rational diagonal scales required")
        scales = dict(zip(EXPONENTS, scalars))
        return {(a, b, c): value * scales[a] * scales[b] / scales[c]
                for (a, b, c), value in self.couplings.items()}

    def finite_orbit_membership(self, candidate, fixed=False):
        """Exact membership in the diagonal orbit, with its unique scales.

        Self-channel ratios recover every scale globally.  This tests the
        declared orbit; rejection does not classify other Jacobi components.
        """
        if type(fixed) is not bool or not hasattr(candidate, "items"):
            raise ValueError("a coupling mapping and Boolean fixed flag are required")
        values = {slot: Q(0) for slot in self.slots}
        for slot, value in candidate.items():
            slot = tuple(slot)
            if slot not in values:
                raise ValueError("unknown principal coupling slot")
            values[slot] = _q(value)
        scales = {m: values[m, m, m] / self.couplings[m, m, m] for m in EXPONENTS}
        if not all(scales.values()):
            return {"in_declared_gauge_orbit": False, "reason": "a self-channel ratio is zero",
                    "unique_scales": None, "other_jacobi_components_classified": False}
        if fixed and scales[1] != 1:
            return {"in_declared_gauge_orbit": False, "reason": "principal scale must equal one",
                    "unique_scales": [[m, str(scales[m])] for m in EXPONENTS],
                    "other_jacobi_components_classified": False}
        for a, b, c in self.slots:
            expected = self.couplings[a, b, c] * scales[a] * scales[b] / scales[c]
            if values[a, b, c] != expected:
                return {"in_declared_gauge_orbit": False,
                        "unique_scales": [[m, str(scales[m])] for m in EXPONENTS],
                        "failure": {"slot": [a, b, c], "expected": str(expected),
                                    "actual": str(values[a, b, c])},
                        "other_jacobi_components_classified": False}
        return {"in_declared_gauge_orbit": True,
                "unique_scales": [[m, str(scales[m])] for m in EXPONENTS],
                "all_170_coefficients_checked": True,
                "other_jacobi_components_classified": False}

    def tangent_constraints(self, fixed=False):
        """Sparse independent equations equivalent to linearized Jacobi.

        Equivalence uses the explicit Whitehead/SL2 theorem proof.  These
        are not represented as literal rows extracted from a dense Jacobian.
        """
        system = self._system(fixed)
        return {"slots": system["slots"], "rows": system["constraint_rows"],
                "pivot_slots": system["pivot_slots"],
                "nonpivot_positions": system["nonpivot_positions"],
                "identification": "same kernel as reduced Jacobi differential by Whitehead plus exact sl2 invariants"}

    def tangent_membership(self, delta, fixed=False):
        system = self._system(fixed)
        if not hasattr(delta, "items"):
            raise ValueError("coupling perturbation mapping required")
        vector = {}
        for slot, value in delta.items():
            slot = tuple(slot)
            if slot not in self.couplings:
                raise ValueError("unknown principal coupling slot")
            value = _q(value)
            if fixed and slot in self.principal_slots:
                if value:
                    raise ValueError("principal action must remain fixed")
                continue
            if value:
                vector[system["positions"][slot]] = value
        scales = tuple(sum((x * vector.get(j, Q(0)) for j, x in row.items()), Q(0))
                       for row in system["recovery"])
        failure = None
        for index, row in enumerate(system["constraint_rows"]):
            value = sum((x * vector.get(j, Q(0)) for j, x in row.items()), Q(0))
            if value:
                failure = {"constraint_index": index, "functional": _wire(row),
                           "value": str(value),
                           "interpretation": "This functional annihilates every diagonal coboundary. Whitehead plus exact sl2 invariants makes it a witness that the perturbation is not a Jacobi cocycle."}
                break
        return {"is_cocycle_in_declared_theorem_scope": failure is None,
                "gauge_spins": list(system["spins"]),
                "recovered_gauge_scalars": list(map(str, scales)),
                "unique_gauge_when_cocycle": failure is None,
                "first_constraint_witness": failure,
                "dense_jacobi_jacobian_used": False,
                "external_theorem_dependencies": ["Whitehead H2(E8,E8)=0", "complete reducibility of finite-dimensional sl2 modules"]}

    def coupling_bracket(self, couplings, left, right):
        """Evaluate an arbitrary reduced equivariant two-cochain."""
        answer = {}
        for i, x in left.items():
            for j, y in right.items():
                if type(i) is not int or type(j) is not int or not 0 <= i < 248 or not 0 <= j < 248:
                    raise ValueError("principal vector index outside 0..247")
                x, y = _q(x), _q(y)
                a, ia = self.principal.basis_labels[i]
                b, ib = self.principal.basis_labels[j]
                for c in EXPONENTS:
                    if not abs(a - b) <= c <= a + b:
                        continue
                    value = _q(couplings.get((min(a, b), max(a, b), c), 0))
                    if not value:
                        continue
                    r = a + b - c
                    output = ia + ib - r
                    if not 0 <= output <= 2 * c:
                        continue
                    value *= x * y * monomial_transvectant(a, ia, b, ib, r) / comb(2 * c, output)
                    if value:
                        _add(answer, {self.principal.label_index[c, output]: value})
        return answer

    def jacobi_derivative(self, delta, left, middle, right):
        """An actual six-term linearized Jacobi evaluation, not a rank claim."""
        answer = {}
        bracket = self.principal.bracket
        perturb = lambda x, y: self.coupling_bracket(delta, x, y)
        for x, y, z in ((left, middle, right), (middle, right, left), (right, left, middle)):
            _add(answer, perturb(x, bracket(y, z)))
            _add(answer, bracket(x, perturb(y, z)))
        return answer

    def jacobian_rank_certificate(self, *, max_panels=196, progress=None):
        """Actually compile enough reduced Jacobi rows to certify rank 155.

        All intermediate equation channels of every declared panel are
        included, including spins outside the eight retained sectors.  The
        certificate retains independent literal Jacobian rows with source
        panel tags.  It does not assemble every spin quadruple's Jacobian.
        """
        from .asterion_higher import (compile_jacobi_constraints,
                                     evaluate_jacobi_constraints,
                                     linearized_jacobi_rows)
        if type(max_panels) is not int or max_panels < 1:
            raise ValueError("positive panel limit required")
        if progress is not None and not callable(progress):
            raise ValueError("progress must be callable")
        variables = tuple(sorted(slot for slot in self.couplings if slot[0] != 1))
        spins = EXPONENTS[1:]
        relative_gauge = tuple(tuple(int(a == m) + int(b == m) - int(c == m)
                                     for m in spins) for a, b, c in variables)
        if rank(relative_gauge) != 7:
            raise ArithmeticError("relative diagonal gauge rank differs")
        span, selected, panels = _IntegerRowSpan(), [], []
        candidates = ((7, b, c, d) for d in spins
                      for b, c in combinations_with_replacement(spins, 2)
                      if max(0, c - 7 - b) <= d <= 7 + b + c)
        for panel in candidates:
            if len(panels) >= max_panels:
                break
            compiled = compile_jacobi_constraints(*panel)
            if not evaluate_jacobi_constraints(compiled, self.couplings)["passed"]:
                raise ArithmeticError(f"actual E8 couplings failed Jacobi panel {panel}")
            linear = linearized_jacobi_rows(compiled, self.couplings, relative=True)
            if linear["variables"] != variables:
                raise ArithmeticError("Jacobi compiler variable order differs")
            added = 0
            for encoded_row in linear["rows"]:
                row = dict(encoded_row)
                if any(sum(value * relative_gauge[j][m] for j, value in row.items())
                       for m in range(7)):
                    raise ArithmeticError("actual Jacobian row failed the gauge-kernel check")
            for equation_index, encoded_row in enumerate(linear["rows"]):
                row = dict(encoded_row)
                if row and span.add(row):
                    selected.append({"panel": list(panel), "equation_index": equation_index,
                                     "intermediate_spin": str(compiled["equation_intermediates"][equation_index]),
                                     "row": _wire(row)})
                    added += 1
                if len(span.rows) == 155:
                    break
            panels.append({"panel": list(panel), "equation_count": len(linear["rows"]),
                           "outside_sector_equation_count": len(compiled["outside_sector_intermediates"]),
                           "new_independent_rows": added, "cumulative_rank": len(span.rows)})
            if progress:
                progress(panels[-1])
            if len(span.rows) == 155:
                break
        actual_rank = len(span.rows)
        certificate = {"coordinate_system": "relative eta_v: kappa_v(t)=kappa_v*(1+t*eta_v)",
                "variables": [list(slot) for slot in variables],
                "variable_count": len(variables), "selected_rows": selected,
                "actual_selected_jacobian_rank": actual_rank,
                "target_rank": 155, "target_rank_reached": actual_rank == 155,
                "echelon_pivot_columns": list(span.pivots),
                "panels": panels, "panel_limit": max_panels,
                "runtime_budget": {"maximum_declared_panels": max_panels,
                                   "compiled_panels": len(panels),
                                   "maximum_panel_recoupling_multiplicity": 15,
                                   "scope": "Deterministic finite panel budget; no wall-time observation is part of the mathematical certificate."},
                "relative_gauge_rank": 7,
                "all_computed_rows_annihilate_seven_gauges": True,
                "full_jacobian_rank_upper_bound": 155,
                "upper_bound_proof": "The seven independent fixed-action diagonal gauges arise from exact Lie-basis changes, hence d2*d1=0 puts them in the kernel of EVERY reduced Jacobi row, not just the compiled panels. Rank-nullity bounds the full 162-variable Jacobian rank by 155.",
                "full_jacobian_rank_certified": 155 if actual_rank == 155 else None,
                "whitehead_needed_for_this_rank_certificate": False if actual_rank == 155 else True,
                "full_reduced_jacobian_assembled": False,
                "scope": "Literal selected Jacobi rows give a computed lower bound. When rank 155 is reached, the seven exact global gauge directions give the matching upper bound."}
        if actual_rank == 155:
            certificate["full_170_variable_block_augmentation"] = self.full_rank_block_augmentation(certificate)
        return certificate

    def full_rank_block_augmentation(self, fixed_certificate):
        """Seven actual principal-only rows extend the fixed rank155 to162.

        The selected 155 fixed-action rows are partial derivatives of actual
        full Jacobi rows.  Their unrecorded principal columns do not affect
        the block-triangular minor with these seven principal-only rows.
        """
        from .asterion_higher import (compile_jacobi_constraints,
                                     evaluate_jacobi_constraints,
                                     linearized_jacobi_rows)
        if fixed_certificate["actual_selected_jacobian_rank"] != 155:
            raise ValueError("the fixed-action rank155 certificate is required")
        variables = tuple(sorted(self.couplings))
        principal_positions = tuple(i for i, slot in enumerate(variables) if slot[0] == 1)
        position_to_principal = {j: i for i, j in enumerate(principal_positions)}
        selected, span = [], _IntegerRowSpan()
        for m in EXPONENTS[1:]:
            panel = (1, 1, m, m)
            compiled = compile_jacobi_constraints(*panel)
            if not evaluate_jacobi_constraints(compiled, self.couplings)["passed"]:
                raise ArithmeticError("principal-only Jacobi augmentation failed at E8")
            linear = linearized_jacobi_rows(compiled, self.couplings, fixed_principal=False, relative=True)
            if linear["variables"] != variables:
                raise ArithmeticError("full cochain variable order differs")
            for equation_index, encoded in enumerate(linear["rows"]):
                row = dict(encoded)
                if any(j not in position_to_principal for j in row):
                    raise ArithmeticError("augmentation row has a nonprincipal variable")
                projected = {position_to_principal[j]: value for j, value in row.items()}
                if sum(projected.values()):
                    raise ArithmeticError("principal augmentation does not annihilate common scale")
                if projected and span.add(projected):
                    selected.append({"panel": list(panel), "equation_index": equation_index,
                                     "intermediate_spin": str(compiled["equation_intermediates"][equation_index]),
                                     "row": _wire(row), "principal_projection": _wire(projected)})
        if len(span.rows) != 7:
            raise ArithmeticError("principal augmentation rank was not seven")
        return {"full_variable_count": 170, "full_variable_order": [list(slot) for slot in variables],
                "principal_coordinate_positions": list(principal_positions),
                "selected_principal_only_rows": selected, "principal_only_rank": 7,
                "principal_minor_columns_within_eight_actions": list(span.pivots),
                "fixed_nonprincipal_rank": 155,
                "full_jacobian_rank_lower_bound": 162,
                "global_eight_gauges_rank": 8, "full_jacobian_rank_upper_bound": 162,
                "full_jacobian_rank_certified": 162,
                "whitehead_needed": False,
                "block_minor_proof": "Choose the 155 pivot nonprincipal columns in the retained fixed-action submatrix and seven pivot principal columns here. The 162 rows form [[J155,unknown],[0,P7]], after column order. Both diagonal blocks are nonsingular, so the full Jacobi Jacobian has rank at least162 irrespective of the unrecorded block. Eight independent global diagonal gauge directions give rank at most170-8=162.",
                "full_jacobian_assembled": False}

    def replay_jacobian_certificate(self, certificate, *, recompile=True):
        """Recompile retained panels and replay exact rank/gauge witnesses."""
        from .asterion_higher import compile_jacobi_constraints, linearized_jacobi_rows
        variables = tuple(tuple(slot) for slot in certificate["variables"])
        expected = tuple(sorted(slot for slot in self.couplings if slot[0] != 1))
        if variables != expected:
            raise ValueError("Jacobian certificate variable order differs")
        panel_cache, span = {}, _IntegerRowSpan()
        checked = 0
        for item in certificate["selected_rows"]:
            row = {i: _q(value) for i, value in item["row"]}
            if len(row) != len(item["row"]):
                raise ValueError("duplicate Jacobian row coordinate")
            if recompile:
                panel = tuple(item["panel"])
                if panel not in panel_cache:
                    compiled = compile_jacobi_constraints(*panel)
                    panel_cache[panel] = (compiled, linearized_jacobi_rows(compiled, self.couplings, relative=True))
                compiled, linear = panel_cache[panel]
                expected_row = dict(linear["rows"][item["equation_index"]])
                if row != expected_row:
                    raise ArithmeticError("recorded literal Jacobi row does not recompile")
                if item["intermediate_spin"] != str(compiled["equation_intermediates"][item["equation_index"]]):
                    raise ArithmeticError("Jacobian intermediate-channel tag differs")
            for m in EXPONENTS[1:]:
                if sum(value * (int(variables[j][0] == m) + int(variables[j][1] == m)
                                - int(variables[j][2] == m)) for j, value in row.items()):
                    raise ArithmeticError("recorded Jacobian row does not annihilate gauge")
            if not span.add(row):
                raise ArithmeticError("retained Jacobian rows are dependent")
            checked += 1
        if (span.pivots != certificate["echelon_pivot_columns"]
                or checked != certificate["actual_selected_jacobian_rank"]):
            raise ArithmeticError("Jacobian rank replay differs")
        if (certificate["target_rank"] != 155
                or certificate["target_rank_reached"] != (checked == 155)
                or certificate["full_jacobian_rank_certified"] != (155 if checked == 155 else None)
                or certificate["full_jacobian_rank_upper_bound"] != 155):
            raise ArithmeticError("Jacobian rank conclusion differs from the replay")
        full_replay = None
        if "full_170_variable_block_augmentation" in certificate:
            expected_full = self.full_rank_block_augmentation(certificate)
            if expected_full != certificate["full_170_variable_block_augmentation"]:
                raise ArithmeticError("full170 variable Jacobian block augmentation differs")
            full_replay = {"principal_only_rows_recompiled": 7, "rank": 162,
                           "block_triangular_minor_verified": True}
        return {"passed": True, "literal_jacobi_rows_recompiled": checked if recompile else 0,
                "independent_rows_replayed": checked, "distinct_panels_recompiled": len(panel_cache),
                "all_rows_annihilate_global_gauge": True, "full170_rank_replay": full_replay}

    def nongauge_witness(self):
        """A single-channel perturbation with an actual nonzero Jacobi derivative."""
        delta = {(7, 7, 7): Q(1)}
        inputs = [{self.principal.label_index[7, j]: Q(1)} for j in (0, 1, 7)]
        residual = self.jacobi_derivative(delta, *inputs)
        if not residual:
            raise ArithmeticError("declared nongauge Jacobi witness vanished")
        return {"perturbed_slot": [7, 7, 7], "perturbation_value": "1",
                "input_principal_labels": [[7, 0], [7, 1], [7, 7]],
                "actual_linearized_jacobi_residual": _wire(residual),
                "tangent_membership": self.tangent_membership(delta, fixed=True),
                "jacobi_failure_computed_directly": True}

    def verify(self, fixed=False):
        system = self._system(fixed)
        G, H, L = system["matrix"], system["recovery"], system["constraint_rows"]
        gauge_dimension, variables = len(system["spins"]), len(system["slots"])
        inverse_product = [[sum((x * G[j][k] for j, x in row.items()), Q(0))
                            for k in range(gauge_dimension)] for row in H]
        if inverse_product != [[Q(i == j) for j in range(gauge_dimension)] for i in range(gauge_dimension)]:
            raise ArithmeticError("gauge recovery is not a left inverse")
        for row in L:
            if any(sum((value * G[j][k] for j, value in row.items()), Q(0))
                   for k in range(gauge_dimension)):
                raise ArithmeticError("tangent constraint does not annihilate gauge")
        nonpivots = system["nonpivot_positions"]
        if any(row.get(j, 0) != int(i == k) for i, row in enumerate(L) for k, j in enumerate(nonpivots)):
            raise ArithmeticError("independent constraint identity minor failed")
        actual_rank = rank(G)
        if actual_rank != gauge_dimension:
            raise ArithmeticError("diagonal gauge matrix rank differs")
        minor = tuple(G[j] for j in system["pivot_positions"])
        determinant = Q(1)
        for i in range(gauge_dimension):
            determinant *= minor[i][i]
            if any(minor[i][j] for j in range(i + 1, gauge_dimension)):
                raise ArithmeticError("declared triangular gauge minor failed")
        return {"cochain_variables": variables, "gauge_dimension": gauge_dimension,
                "actual_gauge_matrix_rank": actual_rank,
                "gauge_matrix": [[str(x) for x in row] for row in G],
                "slot_order": [list(slot) for slot in system["slots"]],
                "gauge_spin_order": list(system["spins"]),
                "minor_row_slots": [list(slot) for slot in system["pivot_slots"]],
                "minor_matrix": [[str(x) for x in row] for row in minor],
                "minor_determinant": str(determinant),
                "gauge_recovery_rows": [_wire(row) for row in H],
                "equivalent_tangent_constraint_rows": [_wire(row) for row in L],
                "equivalent_tangent_constraint_rank": len(L),
                "constraint_identity_minor_columns": list(nonpivots),
                "left_inverse_verified": True, "constraints_annihilate_gauge": True,
                "constraint_identity_minor_verified": True,
                "jacobi_tangent_kernel_dimension_by_theorem": gauge_dimension,
                "jacobi_differential_rank_by_theorem": variables - gauge_dimension,
                "jacobi_jacobian_assembled": False,
                "rank_status": "Gauge ranks and equivalent constraint ranks computed exactly; Jacobi identification proved using stated external theorems."}

    def theorem_certificate(self):
        return {"base_field": "Q or C; characteristic zero",
                "principal_spins": list(EXPONENTS), "trivial_principal_modules": 0,
                "invariant_endomorphism_dimension": 8,
                "invariant_alternating_two_cochain_dimension": len(self.slots),
                "centralizer_of_principal_sl2_dimension": 0,
                "invariant_derivation_dimension": 0,
                "proof_steps": [
                    "The verified principal decomposition has eight pairwise nonisomorphic irreducibles V_m and no V_0. Schur gives End_sl2(g)=Q^8 and the principal centralizer g^sl2=0.",
                    "Clebsch-Gordan multiplicities are one. For a=b every retained output spin c is odd, so the flip parity (-1)^(2a-c) is minus one; all 170 allowed slots are alternating cochains.",
                    "Whitehead H2(g,g)=0 makes every adjoint two-cocycle a coboundary d1(S). The differential is sl2-equivariant. Complete reducibility supplies exact invariant projections P1,P2 with d1 P1=P2 d1, so an invariant cocycle has an invariant preimage.",
                    "Whitehead H1(g,g)=0 makes every derivation inner. An inner derivation ad(z) commuting with principal sl2 has [s,z]=0 because g has zero center. There is no V_0, so z=0. Consequently d1 is injective on the eight invariant endomorphisms.",
                    "Thus the invariant Jacobi tangent kernel is the eight-dimensional image of the computed gauge matrix, and its differential rank is 170-8=162.",
                    "Every principal-action row (1,m,m) changes by kappa_(1,m,m)*s1=s1/2. Fixing all eight such rows is exactly s1=0 on cocycles. The remaining 162 cochain variables have kernel dimension seven and Jacobi differential rank 162-7=155."
                ],
                "external_theorems": [
                    {"name": "Whitehead first and second lemmas", "statement": "H1(g,M)=H2(g,M)=0 for finite-dimensional semisimple g and finite-dimensional M in characteristic zero", "source": "https://www.math.ubc.ca/~reichst/Lie-Algebra-Cohomology.pdf"},
                    {"name": "Weyl complete reducibility", "statement": "Finite-dimensional sl2 modules are semisimple, so taking invariants is exact", "source": "https://ocw.mit.edu/courses/18-745-lie-groups-and-lie-algebras-i-fall-2020/mit18_745_f20_lec18.pdf"},
                    {"name": "Clebsch-Gordan and Schur", "statement": "Multiplicity-free tensor channels and scalar endomorphisms for each principal irreducible", "source": "https://arxiv.org/html/2309.08213v3"}
                ],
                "scope": "Tangent space at the semisimple E8 point in the fixed principal-sl2-equivariant alternating-cochain space. No classification of singular boundary points, global scheme components, integral forms or quantum deformations follows from this calculation."}

    def local_classification_receipt(self, rank_source="Whitehead plus exact gauge matrices"):
        self_channels = [[m, str(self.couplings[m, m, m])] for m in EXPONENTS]
        if not all(self.couplings[m, m, m] for m in EXPONENTS):
            raise ArithmeticError("self-channel scale recovery is not invertible")
        return {"geometric_base_field": "C; the explicit orbit equations and inverse are defined over Q",
                "full_local_dimension": 8, "fixed_action_local_dimension": 7,
                "full_jacobi_scheme_smooth_at_e8": True,
                "fixed_action_jacobi_scheme_smooth_at_e8": True,
                "diagonal_gauge_stabilizer": "trivial",
                "actual_self_channel_coefficients": self_channels,
                "global_inverse_on_declared_orbit": "lambda_m=kappa_prime_(m,m,m)/kappa_(m,m,m)",
                "orbit_equations_in_full_support_torus": "kappa_prime_(a,b,c)/kappa_(a,b,c)=lambda_a*lambda_b/lambda_c",
                "orbit_open_in_jacobi_scheme": True,
                "orbit_closed_in_full_support_torus": True,
                "e8_full_support_connected_component_is_gauge_orbit": True,
                "formal_deformations_through_e8_locally_gauge": True,
                "rank_source": rank_source,
                "proof_steps": [
                    "A self-channel (m,m,m) transforms by lambda_m. Every such actual coefficient is nonzero. Thus scales are recovered by self-channel ratios and the stabilizer is trivial, including scheme-theoretically.",
                    "The torus orbit has dimension eight (seven with lambda_1=1). It lies in the corresponding Jacobi scheme, giving the same lower bound on local Krull dimension.",
                    "The certified Jacobi tangent dimensions are eight and seven. Local Krull dimension cannot exceed tangent dimension, so equality makes each local ring regular. Finite-type schemes over the characteristic-zero field are smooth at these points.",
                    "The orbit is a smooth locally closed subvariety of full local dimension at a smooth point, hence is open near that point. Torus translation proves openness along the entire orbit. The same proof applies to the fixed-action torus.",
                    "Inside the torus where all170 coefficients are nonzero, the orbit is the closed graph of the displayed Laurent-monomial equations, with inverse given by self-channel ratios. Its open-and-closed, connected image is therefore the full-support connected component containing E8. Other components are not classified.",
                    "The orbit map has an explicit regular inverse. Its completed local map is an isomorphism, so compatible formal deformations specializing to E8 are uniquely diagonal gauge with scales specializing to one."
                ],
                "external_geometry": ["https://stacks.math.columbia.edu/tag/00KU", "https://stacks.math.columbia.edu/tag/00TS"],
                "scope": "The E8 point and its declared diagonal orbit/full-support component only. No classification of zero-channel boundary points or other full-support components, integral structures or quantum brackets is claimed."}


def rigidity_receipt(exhaustive=False):
    """Complete JSON-safe gauge and theorem-dependent tangent certificate."""
    if type(exhaustive) is not bool:
        raise ValueError("exhaustive must be a Boolean")
    rigidity = PrincipalRigidity()
    transport = rigidity.principal.verify(exhaustive=exhaustive)
    full, fixed = rigidity.verify(), rigidity.verify(fixed=True)
    receipt = {"schema": "perfectjet.asterion.rigidity.v1",
            "status": "computed exact gauge matrices with theorem-dependent complete tangent identification",
            "arithmetic": "fractions.Fraction",
            "principal_transport": transport,
            "full_invariant_cochains": full,
            "fixed_principal_action": fixed,
            "theorem_certificate": rigidity.theorem_certificate(),
            "local_classification": rigidity.local_classification_receipt(),
            "all_170_actual_couplings_nonzero": all(rigidity.couplings.values()),
            "nongauge_direction_witness": rigidity.nongauge_witness(),
            "literal_jacobi_rows_computed": False,
            "full_rank_162_and_155_computed": False,
            "dense_jacobi_jacobian_computed": False,
            "new_whitehead_theorem_claim": False}
    if exhaustive:
        actual = rigidity.jacobian_rank_certificate()
        receipt["actual_jacobian_rank_certificate"] = actual
        receipt["actual_jacobian_rank_replay"] = rigidity.replay_jacobian_certificate(actual)
        receipt["literal_jacobi_rows_computed"] = True
        receipt["full_rank_162_and_155_computed"] = actual["target_rank_reached"]
        if actual["target_rank_reached"]:
            receipt["status"] = "computed exact selected Jacobian ranks155 and162 with matching global gauge bounds; independent Whitehead proof"
            receipt["local_classification"] = rigidity.local_classification_receipt(
                "actual selected Jacobi rank155, seven principal-only rows giving rank162, and global gauge upper bounds")
    receipt["passed"] = (transport["all_checks_passed"]
                         and full["actual_gauge_matrix_rank"] == 8
                         and fixed["actual_gauge_matrix_rank"] == 7
                         and (not exhaustive or (
                             receipt["actual_jacobian_rank_certificate"]["target_rank_reached"]
                             and receipt["actual_jacobian_rank_replay"]["passed"])))
    return receipt


__all__ = ["PrincipalRigidity", "rigidity_receipt"]
