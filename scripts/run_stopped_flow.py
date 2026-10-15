"""Reproduce the stopped-flow study using the already-owned official checkpoint."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import pickle
import time
from perfectjet.applications.nfl_scouting import rolling, official, movement_targets
from perfectjet.applications.nfl_scouting.bridges import source_prefix
from perfectjet.stopped_jets import readout_receipt


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,default=str,allow_nan=False)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--preparation',type=Path,required=True)
    p.add_argument('--private',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--refits',type=int,default=0)
    p.add_argument('--skip-secondary',action='store_true')
    args=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    if args.private.resolve().is_relative_to(root):
        raise ValueError('restricted individual output directory must be outside the public repository')
    payload=args.checkpoint.read_bytes()
    preparation=json.loads(args.preparation.read_text())
    digest=hashlib.sha256(payload).hexdigest()
    if digest!=preparation['checkpoint_sha256']:raise ValueError('checkpoint differs from preparation')
    for module in (official,movement_targets):
        expected=preparation['extractor_sha256'][module.__name__]
        if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()!=expected:
            raise ValueError('checkpoint extraction code has changed')
    # Only deserialize this user's owned, provenance-checked checkpoint.
    data=pickle.loads(payload);ds=data['dataset'];movement=data['movement']
    protocol=root/'docs/nfl/ROLLING_PROTOCOL.json'
    started=time.monotonic()
    receipt={'schema':'perfectjet/stopped-flow-run/1','started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'checkpoint_sha256':digest,
        'source_bytes':sum(v['bytes'] for v in preparation['raw_source_manifest'].values() if isinstance(v,dict) and 'bytes' in v),
        'source_code_sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (
            root/'src/perfectjet/stopped_jets.py',Path(rolling.__file__),Path(__file__))},
        'official_source_manifest':preparation['raw_source_manifest'],
        'cohorts_have_prior_adaptive_use':True}
    write(args.out/'run-start.json',receipt)
    windows,rejections=rolling.source_windows(ds,tuple(official.FRONT_DRILLS))
    forty=[w for w in windows if w.drill=='FORTY_YARD_DASH']
    write(args.private/'source-windows.json',[vars(w) for w in windows])
    write(args.out/'exact-readout-identities.json',readout_receipt())
    write(args.out/'source-coverage.json',rolling.coverage(ds,windows))
    write(args.out/'source-repeatability.json',rolling.attempt_repeatability(windows))
    write(args.out/'source-rejections.json',rejections)
    mechanism,ma=rolling.movement_dataset(ds,movement)
    write(args.out/'motor-target-coverage.json',ma)
    runs=[('primary',ds,True,('FORTY_YARD_DASH',)),
          ('without-ngs',ds,False,('FORTY_YARD_DASH',)),
          ('matched-motor',mechanism,True,('FORTY_YARD_DASH',))]
    if not args.skip_secondary:runs.append(('front-drills',ds,True,tuple(official.FRONT_DRILLS)))
    model_fits=0
    for name,target,ngs,drills in runs:
        print(f'Stopped-flow experiment: {name}',flush=True)
        result=rolling.experiment(target,windows=windows,include_ngs=ngs,drills=drills)
        model_fits+=result['model_fits']
        write(args.private/f'{name}.json',result)
        write(args.out/f'{name}.json',rolling.public_result(result))
        print(json.dumps({k:{'gain':v['gain'],'interval90':v['fixed_prediction_interval_90']} for k,v in result['comparisons'].items()}),flush=True)
    if args.refits:
        result=rolling.full_refits(ds,draws=args.refits)
        write(args.out/'full-refits.json',result)
    receipt.update(completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        elapsed_seconds=time.monotonic()-started,model_fits_excluding_refits=model_fits,
        requested_full_refits=args.refits,
        run_outputs={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(args.out.glob('*.json')) if f.name not in ('run-start.json','execution-receipt.json')})
    write(args.out/'execution-receipt.json',receipt)
    print(json.dumps({'complete':True,'seconds':receipt['elapsed_seconds'],'model_fits_excluding_refits':model_fits}),flush=True)


if __name__=='__main__':main()
