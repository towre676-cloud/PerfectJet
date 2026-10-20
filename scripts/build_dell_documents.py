"""Assemble the DELL proof chapter without rewriting earlier research chapters."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='<!-- BEGIN DELL RESEARCH CHAPTER -->'


def build(check=False):
    documents=('DELL_RESEARCH.md','DELL_NORMALIZATION.md','DELL_OBSTRUCTIONS.md','DELL_STRUCTURE.md')
    chapter='# 37. Double-elliptic normalization and obstruction\n\n'
    chapter+='\n\n'.join((ROOT/'docs'/name).read_text().rstrip() for name in documents)
    rows=json.loads((ROOT/'data/dell_equations.json').read_text())['equations']
    chapter+='\n\n## Stable DELL relation records\n\n| ID | Relation | Status and hypotheses |\n|---|---|---|\n'
    for row in rows:
        clean=lambda v:str(v).replace('|','\\|').replace('\n',' ')
        chapter+='| '+clean(row['id'])+' | '+clean(row['equation'])+' | '+clean(row['status']+': '+row['assumptions'])+' |\n'
    target=ROOT/'docs/chapters/37_dell_research.md'
    monograph=ROOT/'docs/MONOGRAPH.md'
    earlier=monograph.read_text().split(MARKER,1)[0].rstrip()
    assembled=earlier+'\n\n'+MARKER+'\n\n'+chapter
    for path,value in ((target,chapter),(monograph,assembled)):
        if check:
            if not path.is_file() or path.read_text()!=value:
                raise ValueError('stale DELL proof document: '+str(path))
        else:
            path.write_text(value,encoding='utf-8')
    print(json.dumps({'dell_equations':len(rows),'proof_documents':len(documents),
                      'mode':'check' if check else 'build'}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    build(parser.parse_args().check)
