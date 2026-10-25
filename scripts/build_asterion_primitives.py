"""Search every weight-five/six kernel sector and store its exact representatives.

The stored file is a convenience for fast replays: ``primitives_receipt``
re-verifies each stored representative (raising operators, ideal
nonmembership and, in exhaustive mode, the lattice null lift) and, in
exhaustive mode, repeats the search and compares SHA256 digests.
"""
import argparse
import json
from pathlib import Path

from perfectjet.asterion import json_ready
from perfectjet.asterion_primitives import (
    DERIVED_SECTORS, SECTORS, CERTIFICATE_RESOURCE, JetAlgebra, LatticeE8VOA, _sector_record,
    derived_sector_record, length_three_sector,
)

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", default=None)
    args = parser.parse_args()
    path = ROOT/"src/perfectjet/resources"/CERTIFICATE_RESOURCE
    existing = json.loads(path.read_text()) if path.is_file() else {"sectors": {}}
    jets = JetAlgebra()
    lattice = LatticeE8VOA(jets)
    for label, weight, target, dimension in SECTORS:
        if args.only and label not in args.only:
            continue
        if label in DERIVED_SECTORS:
            source, arc = DERIVED_SECTORS[label]
            record = derived_sector_record(label, existing["sectors"][source], arc)
            existing["sectors"][label] = json_ready(record)
            result = {"kernel_multiplicity": 1, "arc_multiplicity": arc}
        else:
            result = length_three_sector(jets, lattice, target, weight)
            lattice.clear_cache()
            existing["sectors"][label] = json_ready(_sector_record(result, label, dimension))
        existing["schema"] = "perfectjet/asterion-primitive-certificates/1"
        existing["scope"] = ("Exact length-three kernel representatives at conformal weights five and six, "
                             "with lower-length affine corrections; replayed by asterion_primitives.")
        existing["sectors"] = dict(sorted(existing["sectors"].items()))
        path.write_text(json.dumps(existing, indent=1, sort_keys=True)+"\n", encoding="utf-8")
        print(json.dumps({"label": label, "kernel_multiplicity": result["kernel_multiplicity"],
                          "arc_multiplicity": result["arc_multiplicity"]}), flush=True)


if __name__ == "__main__":
    main()
