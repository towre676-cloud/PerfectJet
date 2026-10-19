"""Deterministic complete source package; excludes git/cache/previous release archives."""
import hashlib,json,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION=re.search(r'__version__ = "([^"]+)"',(ROOT/'src/perfectjet/__init__.py').read_text()).group(1)
NAME=f'PerfectJet-v{VERSION}.zip'

def eligible(path):
    rel=path.relative_to(ROOT)
    return (path.is_file() and not any(x in {'.git','__pycache__','.venv','.pytest_cache','dist','build'}
                                      or x.endswith('.egg-info') or x.startswith('private_')
                                      or x in {'raw_data','restricted_data'} for x in rel.parts)
            and path.name not in {'combine_results.csv','combine_tracking.csv','player_play.csv',
                                  'players.csv','games.csv','player_career_successes.csv',
                                  'game_tracking_2023.csv','game_tracking_2024.csv','game_tracking_2025.csv',
                                  'kaggle.json'}
            and not (rel.parts[0]=='releases' and
                     (path.suffix in {'.zip','.sha256'} or path.name.startswith('PerfectJet-v')))
            and rel.as_posix()!='MANIFEST.json')

def main():
    files=sorted(p for p in ROOT.rglob('*') if eligible(p))
    manifest={'schema':'perfectjet/release-manifest/1','version':VERSION,'files':[
        {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
         'size_bytes':p.stat().st_size} for p in files]}
    (ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n', encoding='utf-8', newline='\n')
    files.append(ROOT/'MANIFEST.json')
    release=ROOT/'releases';release.mkdir(exist_ok=True)
    dest=release/NAME
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for p in sorted(files):
            info=zipfile.ZipInfo('PerfectJet/'+p.relative_to(ROOT).as_posix(),(2026,10,14,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            archive.writestr(info,p.read_bytes())
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    (release/(NAME+'.sha256')).write_text(digest+'  '+NAME+'\n', encoding='utf-8', newline='\n')
    if dest.stat().st_size > 40 * 1024 * 1024:
        parts=[]
        with dest.open('rb') as source:
            index=1
            while block := source.read(8 * 1024 * 1024):
                name=NAME+f'.part{index:02d}'
                (release/name).write_bytes(block)
                parts.append({'name':name,'bytes':len(block),'sha256':hashlib.sha256(block).hexdigest()})
                index+=1
        assembly={'schema':'perfectjet/release-parts/1','output':NAME,
                  'bytes':dest.stat().st_size,'sha256':digest,'parts':parts}
        (release/f'PerfectJet-v{VERSION}.parts.json').write_text(json.dumps(assembly,indent=2)+'\n', encoding='utf-8', newline='\n')
    with zipfile.ZipFile(dest) as archive:
        assert archive.testzip() is None
        for entry in manifest['files']:
            assert hashlib.sha256(archive.read('PerfectJet/'+entry['path'])).hexdigest()==entry['sha256']
    print(json.dumps({'files':len(files),'zip_bytes':dest.stat().st_size,'sha256':digest}))

if __name__=='__main__':main()
