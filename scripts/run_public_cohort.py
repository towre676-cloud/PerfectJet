#!/usr/bin/env python3
"""Run the real public Combine/NFL benchmark on a hash-manifested source folder."""
import argparse,json
from pathlib import Path
from perfectjet.applications.nfl_scouting.public_cohort import load_public_cohort,run_public_benchmark

def main():
 p=argparse.ArgumentParser();p.add_argument('--data-root',required=True);p.add_argument('--output',required=True)
 p.add_argument('--scope',choices=['DL','FRONT7','ALL'],default='DL');p.add_argument('--bootstrap-draws',type=int,default=1000)
 p.add_argument('--draft-sensitivity',action='store_true');a=p.parse_args()
 cohort=load_public_cohort(a.data_root)
 result=run_public_benchmark(cohort,position_scope=a.scope,bootstrap_draws=a.bootstrap_draws,draft_sensitivity=a.draft_sensitivity)
 out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 print(json.dumps({t:{k:v for k,v in r.items() if k not in ('folds','predictions')} for t,r in result['targets'].items()},indent=2))
if __name__=='__main__':main()
