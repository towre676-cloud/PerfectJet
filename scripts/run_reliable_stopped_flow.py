"""Explore repeated-attempt calibration after the fixed stopped-flow study."""
import argparse,datetime,hashlib,json,pickle,time
from pathlib import Path
from perfectjet.applications.nfl_scouting import rolling as R,rolling_reliability as M
from perfectjet.applications.nfl_scouting import official,movement_targets

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--preparation',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--private',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    if a.private.resolve().is_relative_to(root):raise ValueError('private output must be outside the repository')
    b=a.checkpoint.read_bytes();receipt=json.loads(a.preparation.read_text())
    if hashlib.sha256(b).hexdigest()!=receipt['checkpoint_sha256']:raise ValueError('checkpoint changed')
    for mod in (official,movement_targets):
        if hashlib.sha256(Path(mod.__file__).read_bytes()).hexdigest()!=receipt['extractor_sha256'][mod.__name__]:raise ValueError('extractor changed')
    write(a.out/'reliability-protocol.json',M.PROTOCOL)
    write(a.out/'reliability-run-start.json',{'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'protocol_sha256':hashlib.sha256(json.dumps(M.PROTOCOL,sort_keys=True).encode()).hexdigest(),
        'status':'secondary adaptive refinement after initial stopped-flow outcomes'})
    data=pickle.loads(b);ds=data['dataset'];motor,_=R.movement_dataset(ds,data['movement']);t=time.monotonic()
    write(a.out/'repeat-prediction.json',M.repeat_prediction(ds))
    for name,target,ngs in [('reliable-primary',ds,True),('reliable-without-ngs',ds,False),('reliable-motor',motor,True)]:
        print(name,flush=True);r=M.experiment(target,include_ngs=ngs)
        write(a.private/(name+'.json'),r);write(a.out/(name+'.json'),M.public_result(r))
        print(json.dumps({k:v['gain'] for k,v in r['comparisons'].items()}),flush=True)
    write(a.out/'reliability-execution.json',{'elapsed_seconds':time.monotonic()-t,'model_fits':288,
        'checkpoint_sha256':hashlib.sha256(b).hexdigest(),
        'source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (
            root/'src/perfectjet/reliable_modes.py',Path(M.__file__),Path(__file__))}})

if __name__=='__main__':main()
