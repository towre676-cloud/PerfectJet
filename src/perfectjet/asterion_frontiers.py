"""Next-push exact certificates with separate mathematical closure boundaries."""
from __future__ import annotations


FRONTIER_COMPONENTS = ("kernel-characters", "kernel-tower", "quartic", "elliptic",
                       "monodromy", "monodromy-algebra", "jacobi")


def _options(exhaustive, max_degree):
    if not isinstance(exhaustive, bool):
        raise ValueError("exhaustive must be Boolean")
    if isinstance(max_degree, bool) or not isinstance(max_degree, int) or not 0 <= max_degree <= 8:
        raise ValueError("frontier lattice degree must be an integer in 0..8")


def frontier_component_report(component, *, exhaustive=False, max_degree=4):
    _options(exhaustive,max_degree)
    if component == "kernel-characters":
        from .asterion_kernel_characters import kernel_characters_receipt
        result = kernel_characters_receipt(exhaustive=exhaustive)
    elif component == "kernel-tower":
        from .asterion_kernel_tower import kernel_tower_receipt
        result = kernel_tower_receipt(exhaustive=exhaustive)
    elif component == "elliptic":
        from .asterion_elliptic import elliptic_receipt
        result = elliptic_receipt(exhaustive=exhaustive)
    elif component == "quartic":
        from .asterion_quartic import quartic_receipt
        result = quartic_receipt(exhaustive=exhaustive)
    elif component == "monodromy":
        from .asterion_monodromy import monodromy_receipt
        result = monodromy_receipt(exhaustive=exhaustive)
    elif component == "monodromy-algebra":
        from .asterion_monodromy_algebra import monodromy_algebra_receipt
        result = monodromy_algebra_receipt(exhaustive=exhaustive)
    elif component == "jacobi":
        from .asterion_jacobi import jacobi_receipt
        result = jacobi_receipt(max_degree,exhaustive=exhaustive)
    else:
        raise ValueError("unknown Asterion frontier component")
    if result.get("passed") is not True:
        raise ArithmeticError(f"frontier certificate did not pass: {component}")
    from .asterion import json_ready
    return json_ready(result)


def frontiers_report(*, exhaustive=False, max_degree=4):
    """Replay all seven components with separate declared closure scopes."""
    _options(exhaustive,max_degree)
    from .asterion import source_digests
    reports = {name:frontier_component_report(name,exhaustive=exhaustive,max_degree=max_degree)
               for name in FRONTIER_COMPONENTS}
    from .asterion_kernel_characters import length_three_character, length_two_character
    arc6 = {248:1}
    for character in (length_three_character(3),length_two_character(4),
                       reports["quartic"]["exact_quartic_multiplication_kernel_character"]):
        for dimension,copies in character.items():
            dimension = int(dimension)
            arc6[dimension] = arc6.get(dimension,0)+copies
    simple_record = next(row for row in reports["kernel-tower"]["simple_finite_characters"]
                         if row["conformal_degree"] == 6)
    simple6 = {row["dimension"]:row["multiplicity"] for row in simple_record["irreducibles"]}
    kernel6 = {d:arc6.get(d,0)-simple6.get(d,0) for d in set(arc6)|set(simple6)}
    kernel6 = {d:c for d,c in sorted(kernel6.items()) if c}
    arc_dimension = sum(d*c for d,c in arc6.items())
    kernel_dimension = sum(d*c for d,c in kernel6.items())
    finite6 = {"passed":reports["quartic"]["exact_full_quartic_kernel_claim"]
               and arc_dimension == 4716373 and kernel_dimension == 185629
               and kernel6 == {1:1,248:1,3875:2,30380:1,147250:1},
               "conformal_weight":6,"exact_arc_dimension":arc_dimension,
               "exact_simple_dimension":simple_record["reconstructed_dimension"],
               "exact_kernel_dimension":kernel_dimension,"exact_kernel_character":kernel6,
               "exact_arc_character":dict(sorted(arc6.items())),
               "higher_length_vanishing":"length5 at weight6 has four zero jets; length6 has six. All vanish because every zero-jet cubic vanishes.",
               "proof":"Complete lengths1,2,3 plus the independently classified length4 multiplication kernel; finite E8 character subtraction across the surjective arc map.",
               "full_Li_bigraded_kernel_embedding_computed":False,
               "complete_minimal_differential_generator_list_computed":False,
               "explicit_new_primitive_affine_null_lifts_computed":False}
    if not finite6["passed"]:
        raise ArithmeticError("the combined exact weight-six character closure failed")
    return {"schema":"perfectjet/asterion-frontiers/1","passed":True,
            "exhaustive_requested":exhaustive,"max_degree":max_degree,
            "source_sha256":source_digests(),"components":reports,
            "finite_weight_six_closure":finite6,
            "claim_scope":"Exact receipts and proofs in the accompanying monographs; worldwide priority is unverified.",
            "remaining_programme":[
                "Complete all-weight arc kernel and minimal differential/vertex-Poisson presentation",
                "Explicit primitive relation lifts beyond the certified first weight-four vector",
                "All-order quantum elliptic E8 R-matrix with an implemented quantum dynamical identity",
                "An explicit flat KZB connection and a certified map from the existing KZ local system",
                "Discrete monodromy image presentation, faithfulness and quantitative word approximation",
                "All-shell Ramanujan nonvanishing, equivalently the Lehmer angular-design boundary"],
            "retained_programme":"All 64 earlier research identifiers and their original acceptance criteria are preserved."}
