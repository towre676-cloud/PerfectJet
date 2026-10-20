"""Exact low-factor arc characters for the level-one E8 C2 algebra.

The ordinary algebra is R=Sym(g)/(V(2 theta))=1+g+(1+3875).
This module computes the entire factor-length-three arc Hilbert series by
polarizing the pair relation and restricting S3 covariants to a diagonal.
It also closes the arc character through conformal weight five.  The full
infinite arc kernel, and the factor-length-four contribution at weight six,
are deliberately not inferred from these calculations.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from math import comb


ADJOINT = 248
NULL_PAIR = 27000
TRIPLE_NUMERATOR = (0, 151373, 961248, 3321371, 4932875, 4123000, 1763125)
SOURCES = (
    "https://arxiv.org/abs/2606.14407",  # Section6.2: the tensor branchings.
    "https://link.springer.com/article/10.1007/s00220-025-05256-y",  # D.6.
)

# Irrep dimensions are unambiguous for these small representations of E8.
SYM3 = {248: 1, 30380: 1, 779247: 1, 1763125: 1}
SCHUR21 = {248: 2, 3875: 1, 27000: 1, 30380: 1,
           147250: 1, 779247: 1, 4096000: 1}
EXTERIOR3 = {1: 1, 3875: 1, 27000: 1, 30380: 1, 2450240: 1}
MIXED_PAIR_TYPES = {248: 1, 30380: 1, 779247: 1}
PURE_TRIVIAL_PAIR_TYPES = {1763125: 1}
PURE_STANDARD_PAIR_TYPES = {27000: 1, 4096000: 1}
PAIR_BRANCH_LABELS = {
    248: (0, 0, 0, 0, 0, 0, 1, 0),
    27000: (0, 0, 0, 0, 0, 0, 2, 0),
    30380: (0, 0, 0, 0, 0, 1, 0, 0),
    779247: (1, 0, 0, 0, 0, 0, 1, 0),
    1763125: (0, 0, 0, 0, 0, 0, 3, 0),
    4096000: (0, 0, 0, 0, 0, 1, 1, 0),
}


def _degree(value):
    if type(value) is not int or value < 0:
        raise ValueError("a nonnegative integer degree is required")
    return value


def character_dimension(character):
    return sum(dimension*multiplicity for dimension, multiplicity in character.items())


def _character_sum(*terms):
    result = {}
    for scalar, character in terms:
        for dimension, multiplicity in character.items():
            result[dimension] = result.get(dimension, 0)+scalar*multiplicity
    return {key: value for key, value in sorted(result.items()) if value}


def partitions_123(degree):
    """Coefficient of 1/((1-t)(1-t²)(1-t³))."""
    if degree < 0:
        return 0
    return sum((degree-3*c)//2+1 for c in range(degree//3+1))


def s3_polynomial_multiplicities(degree):
    """Trivial, standard and sign multiplicities in Sym^degree(Q^3).

    This uses the exact three conjugacy-class traces, independently of the
    free-covariant-module formulas used by the rank proof.
    """
    degree = _degree(degree)
    identity_trace = comb(degree+2, 2)
    transposition_trace = degree//2+1
    cycle_trace = int(degree % 3 == 0)
    numerators = (identity_trace+3*transposition_trace+2*cycle_trace,
                  2*identity_trace-2*cycle_trace,
                  identity_trace-3*transposition_trace+2*cycle_trace)
    if any(x % 6 for x in numerators):
        raise ArithmeticError("S3 multiplicity was not integral")
    return tuple(x//6 for x in numerators)


def ambient_length_three_dimension(jet_degree):
    """Unconstrained Sym³(g tensor Q[t]) of the specified jet degree."""
    a, b, c = s3_polynomial_multiplicities(jet_degree)
    symmetric_cube = comb(ADJOINT+2, 3)
    exterior_cube = comb(ADJOINT, 3)
    schur21 = ADJOINT*(ADJOINT**2-1)//3
    return a*symmetric_cube+b*schur21+c*exterior_cube


def diagonal_image_ranks(jet_degree):
    """Ranks of invariant, standard and mixed pair-diagonal restrictions."""
    d = _degree(jet_degree)
    return {"invariant": max(1, d), "standard": d, "mixed": d+1}


def length_three_hilbert_coefficient(jet_degree):
    """Exact dimension of the factor-length-three, jet-degree-d arc piece."""
    d = _degree(jet_degree)
    ranks = diagonal_image_ranks(d)
    removed = (character_dimension(MIXED_PAIR_TYPES)*ranks["mixed"]
               +character_dimension(PURE_TRIVIAL_PAIR_TYPES)*ranks["invariant"]
               +character_dimension(PURE_STANDARD_PAIR_TYPES)*ranks["standard"])
    return ambient_length_three_dimension(d)-removed


def length_three_character(jet_degree):
    """Exact irreducible E8 character at every nonnegative jet degree.

    All three Schur inputs and the pair-null tensor branching are separately
    reconstructed from adjoint weights by the receipt's Freudenthal replay.
    """
    d = _degree(jet_degree)
    a, b, c = s3_polynomial_multiplicities(d)
    ranks = diagonal_image_ranks(d)
    return _character_sum((a, SYM3), (b, SCHUR21), (c, EXTERIOR3),
                          (-ranks["mixed"], MIXED_PAIR_TYPES),
                          (-ranks["invariant"], PURE_TRIVIAL_PAIR_TYPES),
                          (-ranks["standard"], PURE_STANDARD_PAIR_TYPES))


length_three_arc_character = length_three_character


def length_two_character(jet_degree):
    """Exact pair-jet character: one copy of I is removed at every degree."""
    d = _degree(jet_degree)
    tensor_square = {1: 1, 248: 1, 3875: 1, 27000: 1, 30380: 1}
    symmetric_square = {1: 1, 3875: 1, 27000: 1}
    # Distinct jet labels occur in floor((d+1)/2) unordered pairs.
    return _character_sum(((d+1)//2, tensor_square),
                          (int(d % 2 == 0), symmetric_square),
                          (-1, {27000: 1}))


def weight_five_arc_character():
    """Complete arc character at conformal weight5, as dimension->multiplicity."""
    return _character_sum((1, length_three_character(2)),
                          (1, length_two_character(3)), (1, {248: 1}))


def arc_bidegree_dimensions(weight):
    """Known dimensions indexed by Li degree; None denotes an open piece.

    The complete answer is returned through weight5.  At weight6 only the
    length-four/Li-degree2 component remains open.  For larger weights this
    routine makes no completeness claim.
    """
    n = _degree(weight)
    if n > 6:
        raise ValueError("complete bidegree bookkeeping is provided through weight6")
    if n == 0:
        return {0: 1}
    result = {d: 0 for d in range(n)}
    result[n-1] = ADJOINT
    if n >= 2:
        result[n-2] = character_dimension(length_two_character(n-2))
    if n >= 3:
        result[n-3] = length_three_hilbert_coefficient(n-3)
    if n == 6:
        result[2] = None
    return result


def _rank(columns, dimension):
    pivots = {}
    for column in columns:
        row = {i: Q(x) for i, x in enumerate(column) if x}
        while row:
            index = min(row)
            if index not in pivots:
                scale = row[index]
                pivots[index] = {i: x/scale for i, x in row.items()}
                break
            scale = row[index]
            for i, x in pivots[index].items():
                row[i] = row.get(i, Q(0))-scale*x
                if not row[i]:
                    del row[i]
        if any(i >= dimension for i in row):
            raise ValueError("column exceeds ambient dimension")
    return len(pivots)


def _restriction_columns(degree, kind):
    """Exact columns in basis s^(d-k)v^k, using actual nonzero scales.

    On (t1,t2,t3)=(t,t,u), s=2t+u and v=t-u, the centered invariants
    sum(y_i²),sum(y_i³) restrict to2v²/3,-2v³/9.  The two standard
    covariants restrict along (1,1,-2) with scales v/3,-v²/9.
    """
    columns = []
    shifts = ((0, Q(1)),) if kind == "invariant" else ((1, Q(1,3)), (2, Q(-1,9)))
    for shift, scale in shifts:
        for c in range(max(0, degree-shift)//3+1):
            for b in range(max(0, degree-shift-3*c)//2+1):
                a = degree-shift-3*c-2*b
                if a < 0:
                    continue
                vector = [Q(0)]*(degree+1)
                vector[shift+2*b+3*c] = scale*Q(2,3)**b*Q(-2,9)**c
                columns.append(tuple(vector))
    return columns


def covariance_rank_certificate(max_jet_degree=12):
    """Replay diagonal-image ranks by exact rational elimination.

    The all-order proof is the semigroup identity <2,3>={0,2,3,...};
    this finite panel separately checks its polynomial implementation and
    Molien multiplicities.  All-order validity does not follow from testing
    a finite number of coefficients.
    """
    maximum = _degree(max_jet_degree)
    rows = []
    for d in range(maximum+1):
        invariant = _restriction_columns(d, "invariant")
        standard = _restriction_columns(d, "standard")
        ranks = {"invariant": _rank(invariant, d+1),
                 "standard": _rank(standard, d+1),
                 "mixed": _rank(invariant+standard, d+1)}
        a, b, c = s3_polynomial_multiplicities(d)
        free_formulas = (partitions_123(d),
                         partitions_123(d-1)+partitions_123(d-2),
                         partitions_123(d-3))
        hs_coefficient = sum(coefficient*partitions_123(d-i)
                             for i, coefficient in enumerate(TRIPLE_NUMERATOR))
        expected = diagonal_image_ranks(d)
        checks = (ranks == expected, (a,b,c) == free_formulas,
                  hs_coefficient == length_three_hilbert_coefficient(d))
        rows.append({"jet_degree": d, "ranks": ranks,
                     "s3_multiplicities": [a,b,c],
                     "arc_dimension": hs_coefficient, "passed": all(checks)})
    return {"passed": all(row["passed"] for row in rows), "rows": rows,
            "invariant_image": "Q[s,v²,v³]",
            "standard_image": "v Q[s,v]",
            "mixed_image": "Q[s,v]",
            "all_order_proof": "<2,3>={0,2,3,...}; vQ[s,v²,v³]+v²Q[s,v²,v³]=vQ[s,v]; adjoining invariant image gives Q[s,v]",
            "finite_panel_is_all_order_proof": False}


@lru_cache(maxsize=2)
def _polarization_dependency(exhaustive):
    # This recomputes actual E8 highest vectors and Casimir projections; no
    # acceptance decision is based on a stored list of expected scalars.
    from .asterion_relations import weight_four_completeness_receipt, highest_weight_dimension
    from .asterion_e8 import E8LieAlgebra
    from .asterion_kernel_tower import tensor_cube_character_receipt
    receipt = weight_four_completeness_receipt()
    algebra = E8LieAlgebra()
    rows = receipt["cubic_highest_modules"]
    scalars = {row["dimension"]: Q(row["mu_P_I_delta_scalar"]) for row in rows}
    mixing = {dimension: 0 < scalars[dimension]/3 < 1
              for dimension in MIXED_PAIR_TYPES}
    dimensions = {dimension: highest_weight_dimension(labels, algebra)
                  for dimension, labels in PAIR_BRANCH_LABELS.items()}
    tensors = tensor_cube_character_receipt()
    def finite_character(rows):
        return {row['dimension']: row['multiplicity'] for row in rows}
    schur_tables = tensors['Schur_components']
    reconstructed_schur = {
        'symmetric_cube': finite_character(schur_tables['symmetric_cube']['irreducibles']),
        'mixed_S21': finite_character(schur_tables['mixed_S21']['irreducibles']),
        'exterior_cube': finite_character(schur_tables['exterior_cube']['irreducibles'])}
    reconstructed_pair = finite_character(tensors['g_tensor_I27000']['irreducibles'])
    checks = {"actual_projected_polarization_passed": receipt["passed"],
              "all_three_mixed_projections_nonzero_on_both_parts": all(mixing.values()),
              "cartan_cube_projection_pure_trivial": scalars[1763125] == 3,
              "pair_branch_dimensions_replayed": all(a == b for a,b in dimensions.items()),
              "pair_branch_dimensions_sum_to_domain": sum(dimensions.values()) == ADJOINT*NULL_PAIR,
              "independent_tensor_Freudenthal_replay": tensors['passed'],
              "pair_branching_reconstructed_from_adjoint_weights": reconstructed_pair == {d:1 for d in PAIR_BRANCH_LABELS},
              "all_Schur_characters_reconstructed_from_adjoint_weights":
                  reconstructed_schur == {'symmetric_cube':SYM3,'mixed_S21':SCHUR21,'exterior_cube':EXTERIOR3},
              "schur21_dimensions_exhaust": character_dimension(SCHUR21) == ADJOINT*(ADJOINT**2-1)//3,
              "symmetric_cube_dimensions_exhaust": character_dimension(SYM3) == comb(ADJOINT+2,3)}
    return {"passed": all(checks.values()), "checks": checks,
            "actual_mu_P_I_delta_scalars": {str(d): str(x) for d,x in scalars.items()},
            "pair_branching_dimensions": dimensions,
            "pair_branching_source": SOURCES[0]+"; Eq6.2.3",
            "pair_branching_status": "independently reconstructed from adjoint weights, Newton identities, lattice degree2 and exact Freudenthal recursion; published branching is a cross-check",
            "tensor_character_certificate": tensors,
            "highest_vector_projection_status": "recomputed using exact sparse E8 brackets",
            "scope": "g tensor I is multiplicity free; its pair-fixed vector is mixed trivial/standard for248,30380,779247, pure trivial for1763125, pure standard for27000,4096000"}


def kernel_characters_receipt(exhaustive=False, max_weight=6):
    """Certified arc Hilbert/character results with explicit open boundaries."""
    if type(exhaustive) is not bool:
        raise TypeError("exhaustive must be boolean")
    maximum = _degree(max_weight)
    if maximum > 6:
        raise ValueError("bidegree receipt is bounded at weight6")
    dependency = _polarization_dependency(exhaustive)
    covariance = covariance_rank_certificate(24 if exhaustive else 8)
    bidegrees = {str(n): arc_bidegree_dimensions(n) for n in range(maximum+1)}
    exact_prefix = [sum(arc_bidegree_dimensions(n).values()) for n in range(min(maximum,5)+1)]
    from .asterion_currents import CurrentPopulations
    actual = CurrentPopulations(max(6,maximum)).simple
    weight5 = weight_five_arc_character()
    weight5_dimension = character_dimension(weight5)
    known6 = sum(value for value in arc_bidegree_dimensions(6).values() if value is not None)
    checks = {"polarization_dependency": dependency["passed"],
              "covariance_rank_replay": covariance["passed"],
              "weight_five_irrep_multiplicities_nonnegative": all(x >= 0 for x in weight5.values()),
              "weight_five_character_dimension": weight5_dimension == sum(arc_bidegree_dimensions(5).values()),
              "weight_four_prefix_recovered": sum(arc_bidegree_dimensions(4).values())-actual[4] == 3875,
              "weight_five_kernel_exceeds_first_derivative": weight5_dimension-actual[5] > 3875}
    return {"schema": "perfectjet/asterion-kernel-characters/1", "passed": all(checks.values()),
            "checks": checks, "polarization_dependency": dependency,
            "covariance_certificate": covariance,
            "factor_length_three_hilbert_series": {
                "numerator_coefficients": list(TRIPLE_NUMERATOR),
                "denominator_degrees": [1,2,3], "all_jet_degrees_certified": True,
                "proof": "S3 covariants and exact pair-diagonal restriction ranks"},
            "factor_length_three_character_coefficients": {
                str(d):length_three_character(d) for d in range(7)},
            "bidegree_dimensions": bidegrees,
            "arc_character_prefix_exact_through_weight": min(maximum,5),
            "arc_character_prefix": exact_prefix,
            "simple_character_prefix": actual[:len(exact_prefix)],
            "weight_five_arc_character": weight5,
            "weight_five_arc_dimension": weight5_dimension,
            "weight_five_simple_dimension": actual[5],
            "weight_five_kernel_dimension": weight5_dimension-actual[5],
            "weight_five_old_differential_generator_dimension_upper_bound": 3875,
            "weight_five_new_primitive_dimension_lower_bound": weight5_dimension-actual[5]-3875,
            "weight_six_known_arc_dimension_lower_bound": known6,
            "weight_six_kernel_dimension_lower_bound": known6-actual[6],
            "weight_six_open_piece": "factor length4, Li differential degree2",
            "full_weight_six_arc_dimension_claim": False,
            "complete_infinite_kernel_claim": False,
            "first_kernel_differential_generation_claim": False,
            "proof_dependencies": ["R=1+g+(1+3875), with all ordinary cubics zero",
                "pair-null module I=27000; all tensor branchings reconstructed from actual adjoint weights and exact Freudenthal recursion",
                "exact sparse projected-polarization certificate recomputed above",
                "symmetric-polynomial and S3 covariant decomposition"],
            "sources": list(SOURCES)}
