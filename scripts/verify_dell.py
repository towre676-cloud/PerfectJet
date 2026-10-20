"""Recompute DELL proofs and bounded certificates, or check deterministic bytes."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path

from perfectjet.dell import report,source_digests
from perfectjet.dell_normalization import normalization_receipt

ROOT=Path(__file__).resolve().parents[1]


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()


def build():
    result=report(exhaustive=True)
    if result['passed'] is not True:
        raise ArithmeticError('a DELL certificate failed')
    sources=source_digests()
    payloads={name+'.json':encoded({'source_sha256':sources,**component})
              for name,component in result['components'].items()}
    payloads['validation.json']=encoded(result)
    stream=io.BytesIO()
    evidence=encoded({'source_sha256':sources,**normalization_receipt(include_numerators=True)})
    with gzip.GzipFile(fileobj=stream,mode='wb',filename='',mtime=0) as handle:
        handle.write(evidence)
    payloads['normalization_polynomials.json.gz']=stream.getvalue()
    manifest={'schema':'perfectjet/dell-receipts/1','source_sha256':sources,
              'files':{name:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
                       for name,raw in payloads.items()},
              'scope':'Symbolic rational identity and finite-ansatz proofs; analytic no-go theorem; separate finite exact classical/quantum parameter panels. General self-dual DELL remains open.'}
    payloads['manifest.json']=encoded(manifest)
    return payloads,result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'results/dell')
    args=parser.parse_args()
    payloads,result=build()
    args.output.mkdir(parents=True,exist_ok=True)
    for name,raw in payloads.items():
        path=args.output/name
        if args.check:
            if not path.is_file() or path.read_bytes()!=raw:
                raise ValueError('stale or corrupted DELL certificate: '+str(path))
        else:
            path.write_bytes(raw)
    print(json.dumps({'passed':result['passed'],'mode':'check' if args.check else 'write',
                      'components':list(result['components']),'files':len(payloads)}))


if __name__=='__main__':
    main()
