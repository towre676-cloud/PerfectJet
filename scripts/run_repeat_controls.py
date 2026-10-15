"""Run the source-only repeat study with strong controls and full refits."""
import argparse,datetime,hashlib,json,pickle,time
from pathlib import Path
from perfectjet.applications.nfl_scouting import repeat_controls as C,official,movement_targets

def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('checkpoint','preparation','out','private'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--refits',type=int,default=64);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.private.resolve().is_relative_to(root):raise ValueError('private directory must be outside the repository')
    b=a.checkpoint.read_bytes();pr=json.loads(a.preparation.read_text())
    if hashlib.sha256(b).hexdigest()!=pr['checkpoint_sha256']:raise ValueError('checkpoint changed')
    for m in (official,movement_targets):
        if hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()!=pr['extractor_sha256'][m.__name__]:raise ValueError('extractor changed')
    write(a.out/'repeat-controls-protocol.json',C.PROTOCOL)
    receipt={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'checkpoint_sha256':hashlib.sha256(b).hexdigest(),
        'source_sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (Path(__file__),Path(C.__file__))}}
    write(a.out/'repeat-controls-start.json',receipt);t=time.monotonic();ds=pickle.loads(b)['dataset']
    result,folds=C.experiment(ds);write(a.out/'repeat-controls.json',result)
    write(a.private/'repeat-controls-folds.json',folds)
    print(json.dumps(result['comparisons']),flush=True)
    if a.refits:
        refits=C.full_refits(ds,draws=a.refits);write(a.out/'repeat-controls-refits.json',refits)
        print(json.dumps(refits['intervals_90']),flush=True)
    receipt['elapsed_seconds']=time.monotonic()-t;receipt['requested_refits']=a.refits
    write(a.out/'repeat-controls-execution.json',receipt)
if __name__=='__main__':main()
