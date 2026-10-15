"""Bind the retained public evidence to its current source and recorded tests."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results/stopped-flow'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    for name,key in [('run-start.json','source_code_sha256'),('reliability-execution.json','source_sha256'),
                     ('motor-sensitivity-execution.json','source_sha256'),('repeat-controls-execution.json','source_sha256')]:
        receipt=json.loads((RESULTS/name).read_text())
        for path,digest in receipt[key].items():
            if sha(ROOT/path)!=digest:raise ValueError('execution/source mismatch: '+path)
    nb=json.loads((ROOT/'notebooks/PerfectJet_Stopped_Flow.ipynb').read_text())
    for path,digest in nb['metadata']['perfectjet']['source_sha256'].items():
        if sha(ROOT/path)!=digest:raise ValueError('notebook/source mismatch: '+path)
    test=(RESULTS/'unit-tests-v0.14.txt').read_text()
    if not test.rstrip().endswith('OK'):raise ValueError('retained local tests did not pass')
    tests=int(re.search(r'Ran (\d+) tests',test).group(1))
    getoff=json.loads((RESULTS/'full-refits.json').read_text())
    motor=json.loads((RESULTS/'motor-full-refits.json').read_text())
    repeat=json.loads((RESULTS/'repeat-controls-refits.json').read_text())
    sources=sorted((ROOT/'src/perfectjet').rglob('*.py'))
    sources+=sorted((ROOT/'scripts').glob('*stopped*.py'))+[ROOT/'scripts/run_motor_sensitivity.py',ROOT/'scripts/run_repeat_controls.py']
    outputs=sorted(p for p in RESULTS.glob('*') if p.is_file() and p.name!='release-evidence.json')
    result={'schema':'perfectjet/stopped-flow-release-evidence/1','version':'0.14.0',
        'base_commit':'cf2e28495fa3c05dc7fc90e8a4c2fd7ba459e33d',
        'official_source_bytes':2306804135,'effective_nfl_test_players':51,'repeat_test_players':55,
        'primary_and_motor_full_refits':{'successful':getoff['successful_draws']+motor['successful_draws'],
            'failed':getoff['failed_draws']+motor['failed_draws']},
        'repeat_full_refits':{'successful':repeat['successful_draws'],'failed':repeat['failed_draws']},
        'candidate_outcome_ridge_fits_excluding_context':600+288+120*(getoff['successful_draws']+motor['successful_draws']),
        'source_repeat_ridge_fits':32*(1+repeat['successful_draws']),
        'counts_note':'Unique retained procedures; duplicate exact reruns and tests are not extra scientific cases. Candidate-fit counts exclude context and covariance fits.',
        'local_unittest':{'tests':tests,'result':'passed'},
        'notebook':{'path':'notebooks/PerfectJet_Stopped_Flow.ipynb',
            'sha256':sha(ROOT/'notebooks/PerfectJet_Stopped_Flow.ipynb'),
            'executed_code_cells':sum(c.get('execution_count') is not None for c in nb['cells']),
            'scope':'exact mathematics and retained aggregate replay; official experiments executed separately'},
        'source_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in sources},
        'output_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in outputs},
        'status':'development evidence; no established incremental NFL scouting edge; no new Lean proof'}
    (RESULTS/'release-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('candidate_outcome_ridge_fits_excluding_context','source_repeat_ridge_fits','local_unittest')}))
if __name__=='__main__':main()
