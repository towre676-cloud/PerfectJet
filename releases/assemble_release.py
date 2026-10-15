"""Rebuild the complete release ZIP from its verified parts, optionally downloading them."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request


def assemble(manifest_path, *, output=None, download=False):
    manifest_path=Path(manifest_path)
    manifest=json.loads(manifest_path.read_text())
    name=manifest['output']
    if Path(name).name != name or not name.startswith('PerfectJet-v') or not name.endswith('.zip'):
        raise ValueError('Invalid release filename')
    destination=Path(output) if output else manifest_path.parent/name
    if destination.exists():
        if hashlib.sha256(destination.read_bytes()).hexdigest() == manifest['sha256']:
            return destination
        raise FileExistsError('Existing destination differs; choose a fresh --output path')
    temporary=destination.with_suffix(destination.suffix+'.tmp')
    digest=hashlib.sha256();total=0
    try:
        with temporary.open('wb') as target:
            for part in manifest['parts']:
                part_name=part['name']
                if Path(part_name).name != part_name or not part_name.startswith(name+'.part'):
                    raise ValueError('Invalid part filename')
                local=manifest_path.parent/part_name
                if not local.exists() and download:
                    url='https://raw.githubusercontent.com/towre676-cloud/PerfectJet/main/releases/'+part_name
                    with urllib.request.urlopen(url,timeout=120) as response:
                        data=response.read()
                else:
                    data=local.read_bytes()
                if len(data)!=part['bytes'] or hashlib.sha256(data).hexdigest()!=part['sha256']:
                    raise ValueError('Part length/hash mismatch: '+part_name)
                target.write(data);digest.update(data);total+=len(data)
        if total!=manifest['bytes'] or digest.hexdigest()!=manifest['sha256']:
            raise ValueError('Assembled release length/hash mismatch')
        temporary.replace(destination)
        return destination
    finally:
        temporary.unlink(missing_ok=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--download',action='store_true')
    args=parser.parse_args()
    print(assemble(args.manifest,output=args.output,download=args.download))
