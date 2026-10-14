"""Package only tracked research files plus Git history, never restricted data."""
from pathlib import Path
import subprocess,json,hashlib,zipfile,shutil
ROOT=Path(__file__).resolve().parent
def package():
    dest=ROOT.parent/'deliverables';dest.mkdir(exist_ok=True)
    subprocess.run(['git','bundle','create',str(ROOT/'research_history.bundle'),'--all'],cwd=ROOT,check=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0');paths=[p for p in paths if p and p not in ('VERSION.json','MANIFEST.json','research_history.bundle')]
    forbidden=['data/','private_','.git/']
    assert all(not any(p.startswith(t) for t in forbidden) for p in paths)
    (ROOT/'VERSION.json').write_text(json.dumps({'commit':commit,'raw_data_included':False,'private_player_outputs_included':False,'git_bundle_sha256':hashlib.sha256((ROOT/'research_history.bundle').read_bytes()).hexdigest()},indent=2))
    paths+=['research_history.bundle','VERSION.json'];(ROOT/'MANIFEST.json').write_text(json.dumps({p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},indent=2));paths+=['MANIFEST.json']
    with zipfile.ZipFile(dest/'NFL_Big_Data_Bowl_2027_Research_Package.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in paths:z.write(ROOT/p,'nfl_bdb_2027/'+p)
    with zipfile.ZipFile(dest/'NFL_Big_Data_Bowl_2027_Research_Package.zip') as z:assert z.testzip() is None
    shutil.copyfile(ROOT/'docs/MONOGRAPH.md',dest/'NFL_Big_Data_Bowl_2027_Monograph.md')
    print(json.dumps({'commit':commit,'files':len(paths),'zip_bytes':(dest/'NFL_Big_Data_Bowl_2027_Research_Package.zip').stat().st_size}))
if __name__=='__main__':package()
