"""Length-three arc-kernel sectors at weights seven and eight, by highest weight.

Each sector is the exact computation of ``length_three_sector``: highest
columns of lengths three, two and one, their Frenkel-Kac lattice images, the
exact null space and its classes modulo the differential ideal.  A computed
kernel class is compared with the derivative of the stored lower-weight
representative.  Results are written incrementally, one sector at a time.
Only the listed highest weights are covered; this is not a weight-seven or
weight-eight classification.
"""
import argparse
import json
from pathlib import Path

from perfectjet.asterion import json_ready, source_digests
from perfectjet.asterion_primitives import (
    ZERO, THETA, LAMBDA_3875, OMEGA_147250, OMEGA_30380, OMEGA_779247, JetAlgebra, LatticeE8VOA,
    _in_span, decode_polynomial, g_tensor_i_highest, ideal_highest_images, length_three_sector,
    load_certificates,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/"results/asterion-primitives/length-three-boundary.json"
TARGETS = {
    1: ZERO, 248: THETA,
    4096000: (6, 12, 18, 15, 12, 9, 5, 9), 2450240: (6, 12, 18, 15, 12, 8, 4, 9),
    779247: OMEGA_779247, 27000: (4, 8, 12, 10, 8, 6, 4, 6), 147250: OMEGA_147250,
    30380: OMEGA_30380, 3875: LAMBDA_3875,
}
PLAN = [(7, d) for d in (4096000, 2450240, 779247, 27000, 147250, 30380, 3875, 248, 1)]
PLAN += [(8, d) for d in (4096000, 2450240, 779247, 27000, 147250)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", default=None, help="labels such as w7-3875")
    args = parser.parse_args()
    existing = json.loads(OUTPUT.read_text()) if OUTPUT.is_file() else {"sectors": {}}
    stored = load_certificates()["sectors"]
    jets = JetAlgebra()
    lattice = LatticeE8VOA(jets)
    previous = {}
    for weight, dimension in PLAN:
        label = f"w{weight}-{dimension}"
        if args.only and label not in args.only:
            continue
        target = TARGETS[dimension]
        result = length_three_sector(jets, lattice, target, weight)
        lattice.clear_cache()
        row = {"label": label, "conformal_weight": weight, "li_degree": weight-3,
               "weyl_dimension": dimension, "highest_weight_root_coordinates": list(target),
               "top_monomial_columns": result["top_monomial_columns"],
               "arc_multiplicity": result["arc_multiplicity"],
               "ideal_highest_rank": result["ideal_highest_rank"],
               "lattice_image_dimension": result["lattice_image_dimension"],
               "lattice_null_dimension": result["null_dimension"],
               "kernel_multiplicity": result["kernel_multiplicity"],
               "representative_terms": [len(r["symbol"]) for r in result["representatives"]],
               "correction_terms": [len(r["correction"]) for r in result["representatives"]]}
        source = stored.get(f"w{weight-1}-{dimension}")
        lower = previous.get((weight-1, dimension))
        if lower is None and source and source["representatives"]:
            lower = decode_polynomial(source["representatives"][0]["symbol"])
        if lower is not None and result["representatives"]:
            derived = jets.derivative(lower)
            ideal = ideal_highest_images(jets, g_tensor_i_highest(jets, target), weight)
            symbols = [r["symbol"] for r in result["representatives"]]
            row["equals_derivative_of_lower_class"] = (
                len(symbols) == 1 and _in_span(derived, ideal+symbols) and _in_span(symbols[0], ideal+[derived]))
        if result["representatives"]:
            previous[weight, dimension] = result["representatives"][0]["symbol"]
        row["new_primitive"] = row["kernel_multiplicity"] > (1 if row.get("equals_derivative_of_lower_class", False) else 0)
        existing["sectors"][label] = json_ready(row)
        existing.update({"schema": "perfectjet/asterion-length-three-boundary/1",
                         "source_sha256": source_digests(),
                         "scope": "Weight-seven length three is complete when all nine sectors are present. Weight-eight listed sectors only; length four and longer and all-weight statements remain open."})
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(existing, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        print(json.dumps({k: row[k] for k in ("label", "arc_multiplicity", "kernel_multiplicity", "new_primitive")}), flush=True)


if __name__ == "__main__":
    main()
