"""Prepare a private, hash-bound checkpoint from the nine recovered official CSVs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import pickle
import time

from perfectjet.applications.nfl_scouting.official import load_official_directory
from perfectjet.applications.nfl_scouting.movement_targets import load_movement_targets
from perfectjet.applications.nfl_scouting.bridges import source_prefix
from perfectjet.applications.nfl_scouting import official, movement_targets


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',required=True,type=Path)
    p.add_argument('--private-output',required=True,type=Path)
    p.add_argument('--audit-output',required=True,type=Path)
    a=p.parse_args();a.private_output.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    ds=load_official_directory(a.data,minimum_plays=30,verify_known_hashes=True)
    if not ds.athletes or not ds.attempts or not ds.plays:
        raise ValueError("Official adapter produced an empty real-data population; inspect rejection audit before running models")
    print(json.dumps({'stage':'official_dataset','seconds':time.monotonic()-started,
                      'athletes':len(ds.athletes),'attempts':len(ds.attempts),'plays':len(ds.plays),
                      'audit':ds.manifest['official_adapter']['audit']}),flush=True)
    movement=load_movement_targets(a.data,ds)
    print(json.dumps({'stage':'movement_targets','seconds':time.monotonic()-started,
                      'audit':movement.audit}),flush=True)
    checkpoint=a.private_output/'official_bridge_data.pkl'
    temporary=checkpoint.with_suffix('.tmp')
    with temporary.open('wb') as f:pickle.dump({'dataset':ds,'movement':movement},f,protocol=5)
    temporary.replace(checkpoint)
    digest=hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    eligible={p.athlete_id for p in ds.plays}
    source_counts=Counter(attempt.drill for attempt in ds.attempts if source_prefix(attempt) is not None)
    source_players={attempt.athlete_id for attempt in ds.attempts if source_prefix(attempt) is not None}
    source_forty={attempt.athlete_id for attempt in ds.attempts if attempt.drill=='FORTY_YARD_DASH' and source_prefix(attempt) is not None}
    audit={'schema':'perfectjet/official-bridge-preparation/1','raw_real_data':True,
           'raw_source_manifest':ds.manifest,'movement_audit':movement.audit,
           'checkpoint_sha256':digest,'checkpoint_bytes':checkpoint.stat().st_size,
           'extractor_sha256':{module.__name__: hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
                               for module in (official, movement_targets)},
           'eligible_primary_players':len(eligible),
           'eligible_primary_players_by_class':dict(Counter(str(ds.athletes[i].draft_year) for i in eligible)),
           'observed_launch_prefix_attempts_by_drill':dict(source_counts),
           'players_with_observed_launch_prefix':len(source_players),
           'eligible_players_with_forty_launch_prefix':len(eligible&source_forty),
           'movement_usable_players':len({r.athlete_id for r in movement.records if r.usable}),
           'preparation_seconds':time.monotonic()-started,
           'private_checkpoint_is_not_public_source_data':True}
    a.audit_output.parent.mkdir(parents=True,exist_ok=True)
    a.audit_output.write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({'stage':'saved','seconds':time.monotonic()-started,'private_checkpoint':str(checkpoint),
                      'source_prefix_attempts':dict(source_counts),'eligible_forty_prefix_players':len(eligible&source_forty)}),flush=True)


if __name__=='__main__':main()
