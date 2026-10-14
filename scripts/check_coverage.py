"""Fail on missing canonical content, stale generated chapters, or broken source hashes."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    topics=json.loads((ROOT/'data/topics.json').read_text())['topics']
    eq=json.loads((ROOT/'data/equations.json').read_text())['equations']
    assert len(eq)>=295 and len(topics)>=300
    assert len({x['id'] for x in eq})==len(eq)
    assert len({x['id'] for x in topics})==len(topics)
    mono=(ROOT/'docs/MONOGRAPH.md').read_text()
    for t in topics:assert (ROOT/t['chapter']).exists(),t
    for chapter in (ROOT/'docs/chapters').glob('*.md'):
        assert chapter.read_text() in mono,chapter.name
    for e in eq:assert e['id'] in mono,e['id']
    for source in json.loads((ROOT/'archive/SOURCES.json').read_text())['sources']:
        p=ROOT/source['path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256'],p
    expected=['first_audit','first_equation_pass','first_enhancement','second_archive_pass','second_enhancement']
    capture=json.loads((ROOT/'archive/session/coverage.json').read_text())
    assert all(x in capture['passes'] for x in expected)
    print(json.dumps({'chapters':len(list((ROOT/'docs/chapters').glob('*.md'))),
                      'equations':len(eq),'topics':len(topics),'source_hashes':'passed','session_passes':expected}))

if __name__=='__main__':main()
