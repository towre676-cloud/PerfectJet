"""Regenerate the exact extension certificates, or compare their full bytes.

This replays the full 14,441-row affine relation test, the source Jacobi and
principal transport certificates, modular rank witnesses and all bounded
component checks.  Open global classifications are retained as open gates.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from perfectjet.asterion import json_ready, source_digests
from perfectjet.asterion_extension import extension_report

ROOT = Path(__file__).resolve().parents[1]


def encoded(value):
    return (json.dumps(json_ready(value), indent=2, sort_keys=True,
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


def compressed(value):
    raw = gzip.compress(encoded(value), mtime=0)
    return raw[:9] + b"\xff" + raw[10:]


def build(max_degree=30):
    result = extension_report(exhaustive=True, max_degree=max_degree)
    if not result["passed"]:
        failed = [name for name, report in result["components"].items()
                  if report.get("passed") is not True]
        raise ArithmeticError(f"Asterion extension replay failed: {failed}")
    if not result["components"]["relations"].get("nonzero_arc_kernel_generator_certified_in_this_run"):
        raise ArithmeticError("the full explicit arc relation certificate did not replay")
    sources = source_digests()
    payloads = {}
    for name, component in result["components"].items():
        payloads[name + ".json"] = encoded({"source_sha256": sources, **component})
    from perfectjet.asterion_higher import higher_receipt
    payloads["recoupling_tables.json.gz"] = compressed({
        "source_sha256": sources, **higher_receipt(exhaustive=True, include_tables=True)})
    from perfectjet.asterion_currents import AffineE8Currents
    payloads["cartan_conformal_relations.json.gz"] = compressed({
        "source_sha256": sources,
        **AffineE8Currents().cartan_conformal_receipt(include_coefficients=True)})
    payloads["validation.json"] = encoded(result)
    manifest = {"schema": "perfectjet/asterion-extension-receipts/1",
                "source_sha256": sources,
                "files": {name: {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                          for name, raw in payloads.items()},
                "scope": "Exact regeneration of the stated certificates; not a full differential-kernel or global-boundary classification."}
    payloads["manifest.json"] = encoded(manifest)
    return payloads, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--max-degree", type=int, default=30)
    parser.add_argument("--output", type=Path, default=ROOT / "results/asterion-extension")
    args = parser.parse_args()
    payloads, result = build(args.max_degree)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, raw in payloads.items():
        path = args.output / name
        if args.check:
            if not path.is_file() or path.read_bytes() != raw:
                raise ValueError(f"stale or corrupted extension certificate: {path}")
        else:
            path.write_bytes(raw)
    print(json.dumps({"passed": result["passed"], "mode": "check" if args.check else "write",
                      "components": list(result["components"]), "files": len(payloads),
                      "max_degree": args.max_degree,
                      "explicit_kernel_component_dimension": result["components"]["relations"]["generated_kernel_component_weyl_dimension"]}))


if __name__ == "__main__":
    main()
