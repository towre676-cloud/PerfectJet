"""Verify retained recovery theorems and P-521 searches without discovery tools."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def verify_all():
    from research.p521.curve import GX
    from research.p521_math import accepted_observer, portable_models, raw_observer, rotations
    from research.p521_math import verify_accepted_observer, verify_raw_observer

    folder = Path(__file__).with_name("results")
    documents = {name: json.loads((folder / (name + ".json")).read_text(encoding="utf-8"))
                 for name in ("raw-observer", "accepted-observer", "rotations", "portable-models")}
    results = {
        "raw_observer": raw_observer.verify_document(documents["raw-observer"]),
        "accepted_observer": accepted_observer.verify_document(documents["accepted-observer"]),
        "rotations": rotations.verify_document(documents["rotations"]),
        "portable_models": portable_models.verify_document(documents["portable-models"]),
    }
    if results["portable_models"] is not True:
        raise ValueError("Portable-source receipt failed exact verification")
    # These are separate implementations of the finite proofs.
    results["independent_raw"] = verify_raw_observer.verify_document(documents["raw-observer"])
    results["independent_accepted"] = verify_accepted_observer.verify_document(documents["accepted-observer"])
    if documents["rotations"]["public_x"] != hex(GX):
        raise ValueError("Rotation receipt does not target the published P-521 Gx")
    if (not results["rotations"]["full_rotation_orbit"]
            or not results["rotations"]["six_layouts"]
            or results["rotations"]["matches"] != 0
            or documents["rotations"]["complete"] is not True):
        raise ValueError("Retained rotation receipt lacks the claimed full exclusion")
    if (documents["portable-models"]["target"] != hex(GX)
            or documents["portable-models"]["candidate_count"] != 0
            or documents["portable-models"]["all_profiles_complete"] is not True):
        raise ValueError("Retained portable receipt lacks the claimed target exclusion")
    return {"verified": True, "results": results,
            "provenance_status": "Published P-521 base-point origin remains unknown."}


if __name__ == "__main__":
    print(json.dumps(verify_all(), indent=2))
