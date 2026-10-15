#!/usr/bin/env python3
"""Replay the frozen public-source manifest, with per-file SHA256 checks.

The snapshot URL may be mutable. A future changed source fails its frozen hash
rather than silently substituting newer data. No credentials are required.
"""
from pathlib import Path
import argparse,concurrent.futures,hashlib,json,urllib.request

def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',default='research/public_nfl/SOURCE_MANIFEST.json');p.add_argument('--output',required=True);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
 m=json.loads(Path(a.manifest).read_text());root=Path(a.output).resolve();root.mkdir(parents=True,exist_ok=True)
 def fetch(r):
  rel=Path(r['path'])
  if rel.is_absolute() or '..' in rel.parts:raise ValueError('unsafe manifest path')
  target=root/rel;target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():b=target.read_bytes()
  else:
   with urllib.request.urlopen(r['url'],timeout=30) as response:b=response.read()
  if len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']:raise ValueError('frozen source hash mismatch: '+r['path'])
  target.write_bytes(b);return r['path']
 good=[r for r in m['files'] if 'error' not in r]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
  for path in pool.map(fetch,good):print(path,flush=True)
 (root/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print('Verified',len(good),'source files')
if __name__=='__main__':main()
