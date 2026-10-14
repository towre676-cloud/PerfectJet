import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'archive/SOURCE_METADATA.json').read_text())
for s in data['sources']:
    p=ROOT/s['path'];s['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();s['size_bytes']=p.stat().st_size
(ROOT/'archive/SOURCES.json').write_text(json.dumps(data,indent=2)+'\n')
print(len(data['sources']),'source extracts indexed')
