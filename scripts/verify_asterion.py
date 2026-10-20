"""Generate or independently recompute complete Asterion numerical receipts.

All retained tables are deterministic gzip streams with mtime zero.  --check
reconstructs the actual algebras, kernels, basis and exhaustive checks before
comparing the retained bytes.  It does not merely trust stored pass flags.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from perfectjet.asterion import report


ROOT = Path(__file__).resolve().parents[1]


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def compressed(value):
    raw = gzip.compress(encoded(value), mtime=0)
    # Python 3.11/3.12 can expose the host OS byte when mtime is zero.
    return raw[:9] + b'\xff' + raw[10:]


def build():
    result = report(exhaustive=True, include_tables=True)
    if not result["passed"]:
        raise ArithmeticError("Asterion exhaustive verification failed")
    kernels = result.pop("jordan_grade_kernels")
    cartans = result.pop("jordan_cartan_certificates")
    transports = result.pop("transport_columns")
    response = result["asterion_e8_basis"].pop("certificate")
    payloads = {
        "jordan_kernels.json.gz": compressed({
            "schema": "perfectjet/asterion-jordan-kernels/1",
            "source_sha256": result["source_sha256"],
            "coefficient_basis": "1,zeta5,zeta5^2,zeta5^3",
            "maps": kernels,
        }),
        "response_basis.json.gz": compressed({
            "schema": "perfectjet/asterion-e8-certificate/1",
            "source_sha256": result["source_sha256"],
            "certificate": response,
        }),
        "cartan_normalizers.json.gz": compressed({
            "schema": "perfectjet/asterion-cartan-certificates/1",
            "source_sha256": result["source_sha256"],
            "certificates": cartans,
        }),
        "transport_columns.json.gz": compressed({
            "schema": "perfectjet/asterion-chart-columns/1",
            "source_sha256": result["source_sha256"],
            "column_convention": "Chevalley basis vectors in trace-free 2A4 ambient coordinates",
            "columns": transports,
        }),
        "validation.json": encoded(result),
    }
    manifest = {
        "schema": "perfectjet/asterion-receipts/1",
        "scope": "deterministic exact full replay; no performance or mathematical-priority inference",
        "files": {name: {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                  for name, raw in payloads.items()},
    }
    payloads["manifest.json"] = encoded(manifest)
    return payloads, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT/"results/asterion")
    args = parser.parse_args()
    payloads, result = build()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, raw in payloads.items():
        path = args.output/name
        if args.check:
            if not path.is_file() or path.read_bytes() != raw:
                raise ValueError(f"stale or corrupted Asterion receipt: {path}")
        else:
            path.write_bytes(raw)
    print(json.dumps({"passed": result["passed"], "mode": "check" if args.check else "write",
                      "files": len(payloads), "output": str(args.output),
                      "principal_couplings": result["principal_polynomials"]["allowed_coupling_slots"],
                      "jordan_grade_maps": result["jordan_polynomials"]["grade_pair_maps"],
                      "asterion_determinant": result["asterion_e8_basis"]["determinant"]}))


if __name__ == "__main__":
    main()
