"""Append primitive-generator discoveries to the Asterion ledger from the retained receipt.

Idempotent: earlier AST-D049+ rows and ``primitives_update`` entries are
replaced.  The preserved programme hash excludes ``frontier_update``, so the
new gate states are recorded inside that field and every original record and
acceptance criterion remains byte-identical.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = "results/asterion-frontiers/primitives.json"


def main():
    receipt = json.loads((ROOT/RECEIPT).read_text())
    if receipt.get("passed") is not True or receipt.get("exhaustive_requested") is not True:
        raise ValueError("the retained primitive receipt must be an exhaustive passing replay")
    sectors = receipt["sectors"]
    singlet = receipt["length_four_singlet"]
    adjoint = receipt["length_four_3875"]
    path = ROOT/"docs/ASTERION_DISCOVERIES.json"
    ledger = json.loads(path.read_text())
    ledger["discoveries"] = [d for d in ledger["discoveries"] if int(d["id"][5:]) <= 48]
    evidence = lambda *keys: [f"{RECEIPT}#/{k}" for k in keys]+["src/perfectjet/asterion_primitives.py#primitives_receipt", "docs/ASTERION_PRIMITIVES.md"]
    rep = lambda label: sectors[label]["representatives"][0]
    rows = [
        ("Exact lattice null criterion for the level-one E8 vacuum module",
         {"map": "h_i->h_i(-1)|0>, e_alpha->sign(ht alpha)e^alpha",
          "ordered_pairs_checked": receipt["lattice_realization"]["ordered_pairs"],
          "weight_four_lift_image_terms": receipt["weight_four_lift_replay"]["R_Q_lattice_image_terms"],
          "Sym_F_Q_alone_image_terms": receipt["weight_four_lift_replay"]["Sym_F_Q_alone_image_terms"]},
         evidence("lattice_realization", "weight_four_lift_replay"), ["AST-D037"],
         "A finite exact realization check; the Frenkel-Kac identification and Borcherds formula are classical inputs."),
        ("Explicit weight-five 248 and 147250 primitive generators with null lifts",
         {"P_248": receipt["closed_forms"]["identities"]["w5-248"]["formula"],
          "P_248_lift_correction": receipt["closed_forms"]["identities"]["w5-248"]["correction"],
          "P_248_terms": rep("w5-248")["symbol_terms"],
          "P_147250": "2H002-3H011", "P_147250_terms": rep("w5-147250")["symbol_terms"],
          "kernel_multiplicities": {k: sectors[k]["kernel_multiplicity"] for k in ("w5-248", "w5-3875", "w5-147250")},
          "full_weight_space_nonmembership": {k: receipt["full_weight_space_nonmembership"][k]["passed"]
                                              for k in ("w5-248", "w5-147250")}},
         evidence("sectors/w5-248", "sectors/w5-147250", "closed_forms", "full_weight_space_nonmembership"),
         ["AST-D037", "AST-D038"],
         "Finite weight-five certificates; primitive refers to the commutative differential ideal of the arc algebra."),
        ("Explicit forced weight-six V30380 primitive",
         {"P_30380": receipt["closed_forms"]["identities"]["w6-30380"]["formula"],
          "terms": rep("w6-30380")["symbol_terms"], "lift_correction_terms": rep("w6-30380")["correction_terms"],
          "arc_multiplicity": sectors["w6-30380"]["arc_multiplicity"],
          "kernel_multiplicity": sectors["w6-30380"]["kernel_multiplicity"]},
         evidence("sectors/w6-30380", "closed_forms"), ["AST-D048"],
         "A finite weight-six certificate; the contraction-tensor expression is verified exactly against the searched vector."),
        ("The invariant quartic F0 is the contraction of the weight-five 248 primitive",
         {"kappa": singlet["kappa"], "c": singlet["F0_equals_c_Y_modulo_ideal"],
          "T0_ideal_annihilation_evaluations": singlet["T0_ideal_annihilation"]["evaluations"],
          "length_four_3875_values": adjoint["values_on_x_h1_F_Q"],
          "length_four_3875_syzygy_values": adjoint["values_on_x_h0_DF_Q"]},
         evidence("length_four_singlet", "length_four_3875"), ["AST-D047", "AST-D048"],
         "F0 has zero associated-graded image; both length-four summands are products of lower kernel classes."),
        ("Li-bigraded weight-six kernel and minimal differential generators through weight six",
         {"li_bigraded": receipt["li_bigraded_kernel_through_weight_six"],
          "generators": [g for g in receipt["minimal_generators_through_weight_six"] if g["new"]]},
         evidence("li_bigraded_kernel_through_weight_six", "minimal_generators_through_weight_six"),
         ["AST-D048"],
         "Complete through conformal weight six for the commutative differential ideal; no all-weight presentation, finite generation or vertex-Poisson statement."),
    ]
    for n, (title, claim, ev, deps, boundary) in enumerate(rows, 49):
        ledger["discoveries"].append({
            "id": f"AST-D{n:03d}", "title": title, "claim": claim,
            "evidence_status": "computed_certificate", "evidence": ev, "dependencies": deps,
            "source_ids": ["AST-S007"], "claim_boundary": boundary,
            "priority_claim": "No worldwide novelty claim is made."})
    updates = {
        "AST-P018": ("weight6_kernel_li_bigraded_and_minimal_generators_explicit;weight7_classification_target",
                     ["AST-D050", "AST-D051", "AST-D053"],
                     ["Classify the weight-seven length-four Li-degree-three arc character and its kernel.",
                      "Complete the remaining weight-seven length-three sectors (248 and the singlet).",
                      "Seek an all-weight argument before any finite-generation claim."]),
        "AST-P019": ("first_syzygies_through_weight6_recorded;complete_syzygy_module_target",
                     ["AST-D052", "AST-D053"],
                     ["Compute the kernel of g[0]K5+g[1]K4 -> A6 length4 explicitly.",
                      "Extend syzygies to weight seven with normal-form certificates."]),
        "AST-P020": ("weight6_primitive_modules_explicit;Jordan_transport_of_new_vectors_target",
                     ["AST-D050", "AST-D051"],
                     ["Transport P_248, P_147250 and P_30380 into Jordan coordinates if coordinate formulas are claimed."]),
    }
    for row in ledger["programme"]:
        if row["id"] in updates:
            state, ev, criteria = updates[row["id"]]
            row.setdefault("frontier_update", {})["primitives_update"] = {
                "proposed_state": state, "additional_evidence": ev,
                "next_acceptance_criteria": criteria,
                "source": "docs/ASTERION_PRIMITIVES.md"}
    text = json.dumps(ledger, indent=2, ensure_ascii=False)+"\n"
    path.write_text(text, encoding="utf-8")
    (ROOT/"src/perfectjet/resources/asterion_discoveries.json").write_text(text, encoding="utf-8")
    print(json.dumps({"discoveries": len(ledger["discoveries"])}))


if __name__ == "__main__":
    main()
