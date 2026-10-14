#!/usr/bin/env python3
"""Run real public 2021 NFL movement tests, preserving raw inputs outside git."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path

from perfectjet.applications.nfl_scouting.external_tracking import (
    arrival_benchmarks, evaluate_predictive_state, extract_regional, repeatability,
)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--sequence-players",type=int,default=320)
    parser.add_argument("--sequence-attempts",type=int,default=4)
    parser.add_argument("--skip-forecast",action="store_true")
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    cache=args.output/"derived-records.json"
    if cache.exists():
        # Cache is a checkpoint for this exact explicit invocation; no hidden
        # reuse in the public API. Source manifest binds raw inputs separately.
        raise SystemExit("Output already contains a checkpoint; choose a fresh output directory")
    data=extract_regional(args.data,maximum_sequence_players=args.sequence_players,
                          maximum_sequences_per_player=args.sequence_attempts)
    cache.write_text(json.dumps({"records":data.records,"audit":data.audit,
                                "sequences":[asdict(s) for s in data.sequences]},indent=2))
    print(json.dumps({"extracted":data.audit}),flush=True)
    report={"audit":data.audit,"repeatability":repeatability(data.records),
            "arrival":arrival_benchmarks(data.records)}
    if not args.skip_forecast:
        report["predictive_state"]=evaluate_predictive_state(data.sequences)
    source=args.data/"manifest.json"
    if source.exists():
        report["source_manifest"]=json.loads(source.read_text())
    (args.output/"summary.json").write_text(json.dumps(report,indent=2))
    print(json.dumps({"saved":str(args.output/"summary.json")}),flush=True)


if __name__=="__main__":
    main()
