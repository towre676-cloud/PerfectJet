"""Deterministic complete source package; excludes git/cache/previous release archives."""
import hashlib,json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION=re.search(r'__version__ = "([^"]+)"',(ROOT/'src/perfectjet/__init__.py').read_text()).group(1)
NAME=f'PerfectJet-v{VERSION}.zip'

def eligible(path):
    rel=path.relative_to(ROOT)
    return (path.is_file() and not any(x in {'.git','__pycache__','.venv','.pytest_cache','dist','build'}
                                      or x.endswith('.egg-info') for x in rel.parts)
            and not (rel.parts[0]=='releases' and path.suffix in {'.zip','.sha256'})
            and rel.as_posix()!='MANIFEST.json')

def main():
    files=sorted(p for p in ROOT.rglob('*') if eligible(p))
    manifest={'schema':'perfectjet/release-manifest/1','version':VERSION,'files':[
        {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
         'size_bytes':p.stat().st_size} for p in files]}
    (ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    files.append(ROOT/'MANIFEST.json')
    release=ROOT/'releases';release.mkdir(exist_ok=True)
    dest=release/NAME
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for p in sorted(files):
            info=zipfile.ZipInfo('PerfectJet/'+p.relative_to(ROOT).as_posix(),(2026,10,14,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            archive.writestr(info,p.read_bytes())
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    (release/(NAME+'.sha256')).write_text(digest+'  '+NAME+'\n')
    with zipfile.ZipFile(dest) as archive:
        assert archive.testzip() is None
        for entry in manifest['files']:
            assert hashlib.sha256(archive.read('PerfectJet/'+entry['path'])).hexdigest()==entry['sha256']
    print(json.dumps({'files':len(files),'zip_bytes':dest.stat().st_size,'sha256':digest}))

if __name__=='__main__':main()
