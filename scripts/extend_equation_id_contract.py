"""Extend PerfectJet's equation ID contract coverage to the full catalogue.

The existing contract, data/equation_id_contract.json (schema
perfectjet/equation-id-contract/1), records a SHA-256 of the canonical
record for each equation PJ-E001 through PJ-E417. The catalogue in
data/equations.json now holds 710 equations: PJ-E001..PJ-E487,
PJ-A001..PJ-A040, PJ-D001..PJ-D035, PJ-H001..PJ-H088,
PJ-HB001..PJ-HB012 and PJ-X001..PJ-X048. The 293 equations outside the
E001..E417 range have no canonical hash in the contract, so a change
to their records would not be caught by the repository's own checks
(scripts/build_corpus.py and scripts/verify_release.py only verify
equations whose IDs are present in the contract).

This script does not modify the existing contract. It writes a
companion file, data/equation_id_contract_extension.json, covering
exactly the equations the base contract misses, using the repository's
own canonicalisation, taken from scripts/build_corpus.py and
scripts/verify_release.py:

    hashlib.sha256(json.dumps(record, sort_keys=True,
                              ensure_ascii=False,
                              separators=(',', ':')).encode()).hexdigest()

Modes:
    python3 scripts/extend_equation_id_contract.py           generate
    python3 scripts/extend_equation_id_contract.py --check   verify only

Verification (both modes) first recomputes every hash already in the
base contract and fails if any one disagrees with the current
catalogue record, so the extension is only ever built on a verified
base. In --check mode it additionally verifies the extension file:
every catalogue equation is covered by exactly one of the two files,
and every recorded hash matches the current record.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EQUATIONS = ROOT / "data" / "equations.json"
BASE_CONTRACT = ROOT / "data" / "equation_id_contract.json"
EXTENSION = ROOT / "data" / "equation_id_contract_extension.json"


def canonical_hash(record):
    return hashlib.sha256(
        json.dumps(record, sort_keys=True, ensure_ascii=False,
                   separators=(",", ":")).encode()
    ).hexdigest()


def load():
    equations = json.loads(EQUATIONS.read_text())["equations"]
    base = json.loads(BASE_CONTRACT.read_text())
    return equations, base


def verify_base(equations, base):
    by_id = {e["id"]: e for e in equations}
    if len(by_id) != len(equations):
        raise SystemExit("duplicate equation IDs in catalogue")
    recorded = base["sha256_of_canonical_records"]
    for eid, digest in recorded.items():
        if eid not in by_id:
            raise SystemExit(f"base contract ID not in catalogue: {eid}")
        if canonical_hash(by_id[eid]) != digest:
            raise SystemExit(f"base contract hash mismatch: {eid}")
    return recorded


def main():
    check_only = "--check" in sys.argv[1:]
    equations, base = load()
    recorded = verify_base(equations, base)
    print(f"base contract verified: {len(recorded)} hashes match "
          f"(through {base.get('through')})")
    missing = [e for e in equations if e["id"] not in recorded]
    print(f"catalogue equations: {len(equations)}; "
          f"not covered by base contract: {len(missing)}")
    if check_only:
        if not EXTENSION.exists():
            raise SystemExit("extension file not found")
        ext = json.loads(EXTENSION.read_text())
        ext_hashes = ext["sha256_of_canonical_records"]
        overlap = set(ext_hashes) & set(recorded)
        if overlap:
            raise SystemExit(f"extension overlaps base contract: {sorted(overlap)}")
        covered = set(recorded) | set(ext_hashes)
        all_ids = {e["id"] for e in equations}
        if covered != all_ids:
            raise SystemExit(
                f"coverage mismatch: missing {sorted(all_ids - covered)}, "
                f"extra {sorted(covered - all_ids)}")
        by_id = {e["id"]: e for e in equations}
        for eid, digest in ext_hashes.items():
            if canonical_hash(by_id[eid]) != digest:
                raise SystemExit(f"extension hash mismatch: {eid}")
        print(f"extension verified: {len(ext_hashes)} hashes match; "
              f"all {len(all_ids)} catalogue equations covered exactly once")
        return
    extension = {
        "schema": "perfectjet/equation-id-contract-extension/1",
        "base_contract": "data/equation_id_contract.json",
        "base_through": base.get("through"),
        "generated_from": "data/equations.json",
        "canonicalisation": (
            "sha256 of json.dumps(record, sort_keys=True, "
            "ensure_ascii=False, separators=(',', ':')) encoded as UTF-8, "
            "as used by scripts/build_corpus.py for the base contract"
        ),
        "count": len(missing),
        "sha256_of_canonical_records": {
            e["id"]: canonical_hash(e) for e in missing
        },
    }
    EXTENSION.write_text(json.dumps(extension, indent=2) + "\n")
    print(f"wrote {EXTENSION.name}: {len(missing)} canonical hashes")


if __name__ == "__main__":
    main()
