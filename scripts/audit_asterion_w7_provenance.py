"""Compare regenerated mathematical payloads with the original PR certificates.

Source metadata is the only excluded field. Run the exhaustive generators
before this audit; the integration workflow enforces that order.
"""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from perfectjet.asterion import source_digests

ROOT=Path(__file__).resolve().parents[1]
BASELINE='081ee6d76726ead700eb87fb423835afa5ac8ba4'


def strip(value):
    if isinstance(value,dict):return {k:strip(v) for k,v in value.items() if k!='source_sha256'}
    if isinstance(value,list):return [strip(v) for v in value]
    return value


def main():
    payloads={}
    for folder in ('asterion','asterion-extension','asterion-frontiers'):
        for path in sorted((ROOT/'results'/folder).iterdir()):
            if path.name.startswith('.') or path.name=='manifest.json':continue
            name=path.relative_to(ROOT).as_posix()
            before=subprocess.check_output(['git','show',BASELINE+':'+name],cwd=ROOT)
            load=lambda raw:json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
            old=strip(load(before));new=strip(load(path.read_bytes()))
            if old!=new:raise ArithmeticError('mathematical payload changed: '+name)
            payloads[name]=hashlib.sha256(json.dumps(old,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    old=json.loads(subprocess.check_output(['git','show',BASELINE+':results/asterion/validation.json'],cwd=ROOT))['source_sha256']
    new=source_digests()
    audit={'schema':'perfectjet/asterion-w7-provenance-audit/1','original_pr_commit':BASELINE,
        'preserved_main_commit':'9b69eab9beff3011bc6216b30a460c2c6d0e97be',
        'added_source_bindings':{k:new[k] for k in new.keys()-old.keys()},
        'changed_source_bindings':{k:{'before':old[k],'after':new[k]} for k in old.keys()&new.keys() if old[k]!=new[k]},
        'mathematical_payload_sha256':payloads,'mathematical_payloads_unchanged':True,
        'scope':'Compare exhaustive regenerated receipts against original PR mathematical payloads; only source metadata excluded. Historical cubic boundary binding preserved.'}
    (ROOT/'results/asterion-primitives/w7-provenance-audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'passed':True,'unchanged_mathematical_payloads':len(payloads)}))


if __name__=='__main__':main()
