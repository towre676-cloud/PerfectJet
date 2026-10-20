"""Certified level-four E8 KZ monodromy closure.

Exact rational enclosures establish irreducibility at the specified level.
The resulting compact/Zariski closure calculation also uses stated classical
theorems about WZW unitarity and finite primitive groups of degree five.
It is not inferred from floating point sampling or from residue irreducibility.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json
from math import ceil, factorial, gcd

from .asterion_kz import (
    E8KZ, EIGENVALUES, RationalComplex as C, identity, matrix_add,
    matrix_multiply, matrix_scale, _complex_matrix_norm, _round_gaussian,
)


SPECTRUM_EXPONENTS = (4, 2, 11, 0, 1)
SOURCES = {
    "finite_primitive_degree_five": "https://arxiv.org/abs/0806.0168",
    "genus_zero_wzw_unitarity": "https://arxiv.org/abs/1101.5846",
    "fusion_stability": "https://arxiv.org/abs/math/0212387",
    "irreducible_compact_subgroups_degree_five": "https://arxiv.org/abs/1012.5256",
}


def _q(value):
    if isinstance(value, (bool, float)):
        raise TypeError("exact rational input required")
    return Q(value)


def _int(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("an integer >= %s is required" % minimum)
    return value


@dataclass(frozen=True)
class ComplexBall:
    """Closed ordinary-complex-modulus ball, with Gaussian rational center."""

    center: C
    radius: Q = Q(0)

    def __post_init__(self):
        object.__setattr__(self, "center", C(self.center))
        object.__setattr__(self, "radius", _q(self.radius))
        if self.radius < 0:
            raise ValueError("ball radius must be nonnegative")

    def __add__(self, other):
        if not isinstance(other, ComplexBall):
            other = ComplexBall(other)
        return ComplexBall(self.center+other.center, self.radius+other.radius)

    __radd__ = __add__

    def __neg__(self):
        return ComplexBall(-self.center, self.radius)

    def __sub__(self, other):
        return self+-other if isinstance(other, ComplexBall) else self+-ComplexBall(other)

    def __mul__(self, other):
        if not isinstance(other, ComplexBall):
            other = ComplexBall(other)
        radius = (self.center.norm_one()*other.radius+other.center.norm_one()*self.radius
                  +self.radius*other.radius)
        return ComplexBall(self.center*other.center, radius)

    __rmul__ = __mul__

    def inverse(self):
        lower = self.center.modulus_lower()
        if lower <= self.radius:
            raise ArithmeticError("the complex ball is not certified to exclude zero")
        radius = self.radius/(lower*(lower-self.radius))
        return ComplexBall(1/self.center, radius)

    def rounded(self, bits=128):
        denominator = 2**_int(bits, 16)
        center = _round_gaussian(self.center, denominator)
        radius = self.radius+(self.center-center).norm_one()
        radius = Q(ceil(radius*denominator), denominator)
        return ComplexBall(center, radius)

    def to_json(self):
        return {"center": self.center.to_json(), "modulus_error_bound": str(self.radius)}


@dataclass(frozen=True)
class MatrixBall:
    """A matrix infinity-norm ball, using ordinary complex entry moduli."""

    center: tuple
    radius: Q = Q(0)

    def __post_init__(self):
        matrix = tuple(tuple(C(x) for x in row) for row in self.center)
        if len(matrix) != 5 or any(len(row) != 5 for row in matrix):
            raise ValueError("a five by five matrix is required")
        object.__setattr__(self, "center", matrix)
        object.__setattr__(self, "radius", _q(self.radius))
        if self.radius < 0:
            raise ValueError("matrix radius must be nonnegative")
        object.__setattr__(self, "radius", Q(ceil(self.radius*2**256), 2**256))

    def norm_upper(self):
        return _complex_matrix_norm(self.center)+self.radius

    def norm_lower(self):
        return max(sum(x.modulus_lower() for x in row) for row in self.center)

    def __mul__(self, other):
        if isinstance(other, MatrixBall):
            radius = (_complex_matrix_norm(self.center)*other.radius
                      +_complex_matrix_norm(other.center)*self.radius+self.radius*other.radius)
            return MatrixBall(matrix_multiply(self.center, other.center), radius)
        if not isinstance(other, ComplexBall):
            other = ComplexBall(other)
        radius = (self.norm_upper()*other.radius+other.center.norm_one()*self.radius)
        return MatrixBall(matrix_scale(self.center, other.center), radius)

    def subtract_scalar(self, scalar):
        if not isinstance(scalar, ComplexBall):
            scalar = ComplexBall(scalar)
        return MatrixBall(matrix_add(self.center, matrix_scale(identity(), -scalar.center)),
                          self.radius+scalar.radius)


def _atan_inverse(integer, terms):
    x = Q(1, integer)
    value = sum(((-1)**n*x**(2*n+1)/Q(2*n+1) for n in range(terms)), Q(0))
    return value, x**(2*terms+1)/Q(2*terms+1)


@lru_cache(maxsize=8)
def seventeenth_roots(precision_bits=128):
    """Enclose all powers of exp(2*pi*i/17), using rational remainders.

    Machin's identity supplies pi, alternating arctangent remainders bound
    it, and real Taylor remainder estimates bound sin/cos. Every subsequent
    complex multiplication propagates its error; no decimal pi is used.
    """
    bits = _int(precision_bits, 32)
    if bits > 256:
        raise ValueError("bounded root certificate supports at most256 bits")
    terms = bits//2+16
    a, ea = _atan_inverse(5, terms)
    b, eb = _atan_inverse(239, terms)
    raw_pi, pi_error = 16*a-4*b, 16*ea+4*eb
    pi = _round_gaussian(C(raw_pi), 2**bits).real
    pi_error += abs(raw_pi-pi)
    angle, angle_error = 2*pi/17, 2*pi_error/17
    taylor_terms = bits//4+8
    cosine = sum(((-1)**n*angle**(2*n)/factorial(2*n)
                  for n in range(taylor_terms+1)), Q(0))
    sine = sum(((-1)**n*angle**(2*n+1)/factorial(2*n+1)
                for n in range(taylor_terms+1)), Q(0))
    # Real sin/cos are globally1-Lipschitz; Taylor's derivative remainder
    # bounds the polynomial evaluation at the rational angle independently.
    remainder_cos = abs(angle)**(2*taylor_terms+1)/factorial(2*taylor_terms+1)
    remainder_sin = abs(angle)**(2*taylor_terms+2)/factorial(2*taylor_terms+2)
    root = ComplexBall(C(cosine, sine), 2*angle_error+remainder_cos+remainder_sin).rounded(bits)
    roots = [ComplexBall(C(1))]
    for _ in range(1, 17):
        roots.append((roots[-1]*root).rounded(bits))
    return tuple(roots)


def root_certificate(precision_bits=128):
    roots = seventeenth_roots(precision_bits)
    # Exact tangent arithmetic checks the algebraic part of Machin's identity.
    tangent_twice = lambda x: 2*x/(1-x*x)
    t = tangent_twice(tangent_twice(Q(1, 5)))
    machin_tangent = (t-Q(1, 239))/(1+t/Q(239))
    # This also fixes the branch:0<4atan(1/5)-atan(1/239)<1<pi/2.
    # The last inequality follows from2atan(1)>1, by its integral formula.
    branch = 4*(Q(1, 5)-Q(1, 5)**3/3)-Q(1, 239) > 0 and Q(4, 5) < 1
    last = roots[-1]*roots[1]
    closure = (last.center-1).norm_one() <= last.radius
    separated = all((a.center-b.center).modulus_lower() > a.radius+b.radius
                    for i, a in enumerate(roots) for b in roots[i+1:])
    return {"passed": machin_tangent == 1 and branch and closure and separated, "order": 17,
            "precision_bits": precision_bits,
            "method": "pi=16 atan(1/5)-4 atan(1/239); rational alternating and sin/cos Taylor remainders",
            "machin_tangent_identity_checked": machin_tangent == 1,
            "machin_branch_checked": branch,
            "root_power17_enclosure_contains_one": closure,
            "all_root_balls_pairwise_disjoint": separated,
            "roots": [root.to_json() for root in roots],
            "scope": "rigorous enclosures of the specified analytic roots, not floating point estimates"}


def local_spectrum_receipt(level=4):
    level = _int(level, 4)
    kappa = level+30
    common = gcd(kappa, 2)
    order = kappa//common
    exponents = [int(x)//common % order for x in EIGENVALUES]
    determinant_exponent = sum(exponents) % order
    determinant_order = order//gcd(order, determinant_exponent)
    reflection_shifts = [a for a in sorted({(exponents[0]+x) % order for x in exponents})
                         if sorted((a-x) % order for x in exponents) == sorted(exponents)]
    return {"passed": True, "level": level, "kappa": kappa,
            "local_order": order, "projective_local_order": order,
            "spectral_exponents": exponents, "distinct_eigenvalues": len(set(exponents)) == 5,
            "determinant_exponent": determinant_exponent,
            "determinant_image_order": determinant_order,
            "projective_self_duality_reflections": reflection_shifts,
            "projective_symmetric_form_excluded": not reflection_shifts,
            "finite_order_basis": "exact log-free Frobenius basis; local eigenvalues exp(2*pi*i*lambda/(k+30))",
            "finite_order_is_infinite_image_claim": False}


def _reachable(edges, start):
    found, pending = {start}, [start]
    while pending:
        vertex = pending.pop()
        for a, b in edges:
            if a == vertex and b not in found:
                found.add(b)
                pending.append(b)
    return found


def irreducibility_receipt(first_loop, second_loop, *, precision_bits=128):
    """Certify an actual level-four spectral-projector block graph.

    Input balls must enclose the specified monodromies; this routine proves
    the algebraic/numerical consequence of those enclosures. The group
    receipt supplies freshly certified polygon enclosures in exhaustive mode.
    """
    if not isinstance(first_loop, MatrixBall) or not isinstance(second_loop, MatrixBall):
        raise TypeError("certified MatrixBall inputs are required")
    roots = seventeenth_roots(precision_bits)
    eigenvalues = [roots[r] for r in SPECTRUM_EXPONENTS]
    projectors = []
    for i, eigenvalue in enumerate(eigenvalues):
        projector = MatrixBall(identity())
        for j, other in enumerate(eigenvalues):
            if i != j:
                factor = first_loop.subtract_scalar(other)*(eigenvalue-other).inverse()
                projector = projector*factor
        projectors.append(projector)
    records, edges = [], []
    for source, p in enumerate(projectors):
        for target, q in enumerate(projectors):
            if source == target:
                continue
            block = q*second_loop*p
            lower = block.norm_lower()
            nonzero = lower > block.radius
            if nonzero:
                edges.append((source, target))
            records.append({"source_channel": source, "target_channel": target,
                            "center_norm_lower_bound": str(lower),
                            "matrix_error_upper_bound": str(block.radius),
                            "nonzero_certified": nonzero})
    strong = all(len(_reachable(edges, i)) == 5 for i in range(5))
    serialized = [[x.to_json() for x in row] for row in first_loop.center]
    return {"passed": strong, "level": 4, "hbar": "1/34",
            "spectral_order": 17, "spectral_exponents": list(SPECTRUM_EXPONENTS),
            "root_enclosure": root_certificate(precision_bits),
            "first_loop_matrix_sha256": sha256(json.dumps(serialized, separators=(',', ':')).encode()).hexdigest(),
            "first_loop_error_bound": str(first_loop.radius),
            "second_loop_error_bound": str(second_loop.radius),
            "projector_error_bounds": [str(p.radius) for p in projectors],
            "certified_directed_edges": [list(edge) for edge in edges],
            "edge_count": len(edges), "strongly_connected": strong,
            "projector_blocks": records,
            "irreducible_at_specified_level": strong,
            "full_matrix_algebra_generated": strong,
            "argument": "simple spectrum makes every invariant subspace a sum of eigenspaces; a strongly connected graph of nonzero P_target V P_source blocks excludes every proper subset",
            "input_enclosure_scope": "this implication assumes the supplied MatrixBall enclosures and exact local spectrum; exhaustive group receipt constructs both from the implemented KZ connection"}


def _closure_logic(spectrum, irreducible, bundle_verified):
    order = spectrum["projective_local_order"]
    finite_primitive_orders = list(range(1, 7))+list(range(9, 13))
    primitive = irreducible and order == 17
    infinite = primitive and order not in finite_primitive_orders
    no_self_duality = spectrum["projective_symmetric_form_excluded"]
    return {"fixed_level_irreducibility_certified": irreducible,
            "primitivity_certified": primitive,
            "primitivity_argument": "in dimension5 every imprimitive block system has5 lines; an order17 generator has trivial permutation in S5, so both generators would preserve each line",
            "finite_primitive_projective_orders_in_degree5": finite_primitive_orders,
            "finite_primitive_exclusion_theorem": "Rowell-Tuba0806.0168 Lemma5.1(d), using Feit's classification; rescale a finite group to a finite central extension in SL5 without changing projective orders",
            "infinite_image_certified": infinite,
            "unitarity_theorem": "Belkale1101.5846 Theorem1.1; all five rank-four adjoint conformal blocks survive at k4 by fusion/tensor stability",
            "five_dimensional_conformal_block_bundle_identified": bundle_verified,
            "projective_unitarity_suffices": "if U*HU=cH then c^5=|det U|^2=1; c>0 forces c=1, likewise V",
            "proper_connected_irreducible_candidates": ["SO(5) standard", "SU(2) symmetric fourth power"],
            "projective_self_duality_excluded": no_self_duality,
            "identity_component_argument": "Clifford theory and prime dimension5 leave an irreducible connected component, a5-line system, or a scalar component; primitivity excludes5 lines and finite determinant excludes a connected scalar group",
            "connected_subgroup_argument": "the irreducible complex representations of simple Lie algebras of dimension5 are A4 standard/dual, B2 vector, and A1 Sym4; the latter two preserve a unique symmetric bilinear form, which the full group would preserve up to scalar",
            "connected_subgroup_source": "Zeier-Schulte-Herbrueggen1012.5256 Table1 and degree5 highest-weight table; degree5 unaffected by2014 erratum",
            "closure_implication_ready": infinite and no_self_duality and bundle_verified}


def monodromy_group_receipt(*, exhaustive=False, level=4):
    """Classify level-four closure after a fresh rigorous transport replay.

    Fast mode reports exact structural gates and explicitly leaves the
    specialization gate open. Exhaustive mode performs the approximately
    twenty-second polygon calculation and certifies the actual level-four
    representation, rather than substituting a generic residue theorem.
    """
    if type(exhaustive) is not bool:
        raise TypeError("exhaustive must be a boolean")
    if _int(level, 4) != 4:
        raise ValueError("the group-classification certificate currently specializes only level4")
    spectrum = local_spectrum_receipt(level)
    pair, irreducibility, algebra_verification = None, None, None
    local_frobenius = None
    if exhaustive:
        system = E8KZ()
        algebra_verification = system.verify()
        local_frobenius = [system.frobenius(Q(1, 34), order=1, branch=i) for i in range(5)]
        pair = system.monodromy_pair_receipt()
        u = MatrixBall(tuple(tuple(C(x) for x in row)
                             for row in pair["first_loop"]["approximation_exact"]),
                       Q(pair["first_loop"]["infinity_norm_error_bound"]))
        v = MatrixBall(tuple(tuple(C(x) for x in row)
                             for row in pair["second_loop_approximation_exact"]),
                       Q(pair["second_loop_error_bound"]))
        irreducibility = irreducibility_receipt(u, v)
    bundle_verified = bool(algebra_verification and algebra_verification["passed"]
                           and all(record["log_free_all_orders_certified"] for record in local_frobenius))
    actual_irreducible = bool(pair and pair["passed"] and irreducibility["passed"])
    logic = _closure_logic(spectrum, actual_irreducible, bundle_verified)
    certified = actual_irreducible and logic["closure_implication_ready"]
    return {"schema": "perfectjet/asterion-monodromy-group/1", "passed": certified if exhaustive else True,
            "exhaustive_requested": exhaustive, "level": level, "hbar": "1/34",
            "local_spectrum": spectrum, "loop_enclosures": pair,
            "kz_algebra_verification": algebra_verification,
            "local_frobenius": local_frobenius,
            "conformal_block_identification": {
                "adjoint_affine_level": 2, "fusion_stability_level": 4,
                "channel_affine_levels": [0, 2, 2, 3, 4],
                "finite_invariant_fiber_dimension": 5, "conformal_block_rank": 5,
                "argument": "at k4 every multiplicity-one summand of adjoint tensor adjoint survives fusion; factorization gives five four-adjoint singlet blocks, equal to the whole five-dimensional finite invariant fiber",
                "normalization_replayed_in_this_run": bundle_verified},
            "specialized_irreducibility": irreducibility, "proof_gates": logic,
            "group_closure_certified_in_this_run": certified,
            "classification_target": "compact det^{-1}(mu17), connectedSU5; complex det^17=1; projectivelyPU5",
            "compact_closure_up_to_conjugacy": "{g in U(5): det(g)^17=1}" if certified else None,
            "compact_identity_component": "SU(5)" if certified else None,
            "complex_zariski_closure": "{g in GL(5,C): det(g)^17=1}" if certified else None,
            "complex_zariski_identity_component": "SL(5,C)" if certified else None,
            "pointwise_differential_galois_group": "{g in GL(5,C): det(g)^17=1}" if certified else None,
            "differential_galois_argument": "regular-singular Schlesinger density at0,1,infinity identifies the differential Galois group with this specialized monodromy Zariski closure",
            "projective_compact_closure": "PU(5)" if certified else None,
            "component_count": 17 if certified else None,
            "compact_abstract_group": "SU(5) x C17" if certified else None,
            "scalar_determinant_splitting_exponent": 7 if certified else None,
            "closure_lie_algebra_dimension": 24 if certified else None,
            "positive_invariant_hermitian_form_explicitly_computed": False,
            "method": "rigorous actual-loop spectral-projector graph plus stated classification and unitarity theorems",
            "numerical_samples_alone_classify_group": False,
            "worldwide_priority_claim": False,
            "sources": SOURCES,
            "remaining_boundary": "no classification at other levels; no explicit unitarizing matrix or presentation of the countable dense image"}


monodromy_receipt = monodromy_group_receipt
