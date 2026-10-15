"""Reproduce no-NGS matched-movement sensitivity and full pipeline refits."""
import argparse,datetime,hashlib,json,pickle,time
from pathlib import Path
from perfectjet.applications.nfl_scouting import rolling as R,official,movement_targets

def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('checkpoint','preparation','out','private'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--refits',type=int,default=32);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.private.resolve().is_relative_to(root):raise ValueError('private directory must be outside repository')
    b=a.checkpoint.read_bytes();pr=json.loads(a.preparation.read_text())
    if hashlib.sha256(b).hexdigest()!=pr['checkpoint_sha256']:raise ValueError('checkpoint changed')
    for m in (official,movement_targets):
        if hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()!=pr['extractor_sha256'][m.__name__]:raise ValueError('extractor changed')
    t=time.monotonic();data=pickle.loads(b);ds,audit=R.movement_dataset(data['dataset'],data['movement'])
    result=R.experiment(ds,include_ngs=False)
    write(a.private/'matched-motor-without-ngs.json',result)
    write(a.out/'matched-motor-without-ngs.json',R.public_result(result))
    if a.refits:write(a.out/'motor-full-refits.json',R.full_refits(ds,draws=a.refits))
    write(a.out/'motor-sensitivity-execution.json',{
        'completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'elapsed_seconds':time.monotonic()-t,'model_fits_excluding_refits':120,'requested_refits':a.refits,
        'checkpoint_sha256':hashlib.sha256(b).hexdigest(),
        'source_sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (Path(__file__),Path(R.__file__))}})
if __name__=='__main__':main()
