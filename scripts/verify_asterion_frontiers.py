"""Regenerate or independently replay the complete next-push certificates."""
import argparse
import hashlib
import json
from pathlib import Path

from perfectjet.asterion import json_ready, source_digests
from perfectjet.asterion_frontiers import frontiers_report

ROOT = Path(__file__).resolve().parents[1]


def encoded(value):
    return (json.dumps(json_ready(value),indent=2,sort_keys=True,
                       ensure_ascii=False,allow_nan=False)+"\n").encode()


def build(max_degree=4):
    result = frontiers_report(exhaustive=True,max_degree=max_degree)
    group = result["components"]["monodromy"]
    if group.get("group_closure_certified_in_this_run") is not True:
        raise ArithmeticError("the actual specialized monodromy closure did not replay")
    sources = source_digests()
    payloads = {name+".json":encoded({"source_sha256":sources,**component})
                for name,component in result["components"].items()}
    payloads["validation.json"] = encoded(result)
    manifest = {"schema":"perfectjet/asterion-frontier-receipts/1",
                "source_sha256":sources,"files":{
                    name:{"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
                    for name,raw in payloads.items()},
                "scope":"Higher-weight kernel, classical elliptic compatibility, specialized monodromy closure and refined Jacobi certificates; infinite kernel and quantum presentation remain explicit gates."}
    payloads["manifest.json"] = encoded(manifest)
    return payloads,result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--max-degree",type=int,default=4)
    parser.add_argument("--output",type=Path,default=ROOT/"results/asterion-frontiers")
    args = parser.parse_args()
    payloads,result = build(args.max_degree)
    args.output.mkdir(parents=True,exist_ok=True)
    for name,raw in payloads.items():
        path = args.output/name
        if args.check:
            if not path.is_file() or path.read_bytes() != raw:
                raise ValueError(f"stale or corrupted frontier certificate: {path}")
        else:
            path.write_bytes(raw)
    print(json.dumps({"passed":result["passed"],"mode":"check" if args.check else "write",
                      "components":list(result["components"]),"files":len(payloads),
                      "max_degree":args.max_degree,"monodromy_identity_component":
                      result["components"]["monodromy"]["compact_identity_component"]}))


if __name__ == "__main__":
    main()
