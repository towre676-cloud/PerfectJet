"""Build a source-complete official-data notebook for the 0.13 math bridge.

Syntax-checking cells is distinct from executing the notebook cells; real-input runner receipts are stored separately.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    sources = {str(p.relative_to(ROOT / 'src')): p.read_text()
               for p in sorted((ROOT / 'src/perfectjet').rglob('*.py'))}
    hashes = {p: hashlib.sha256(s.encode()).hexdigest() for p, s in sources.items()}
    cells = []

    def cell(kind, source):
        item = {'cell_type': kind, 'id': f'bridge-{len(cells):03d}',
                'metadata': {}, 'source': source}
        if kind == 'code':
            item.update(execution_count=None, outputs=[])
        cells.append(item)

    cell('markdown', r'''# PerfectJet: causal movement, predictive state and scouting decisions

**Official-data runner executed; no incremental scouting advantage established.** This notebook embeds and hashes the actual 0.13 source. The real-data aggregate receipts are in `results/real-nfl/`; this notebook itself has not been executed. The analytic receipt can run without competition input; its exact package result and synthetic predictive-state examples do not constitute NFL evidence.

The football question is whether a Combine-derived movement forecast improves rookie snap-to-LOS get-off beyond all fifteen conventional measurements, position and shared availability. Previously inspected classes remain development evidence. Operational tracking onset is not physiological reaction time. Missing participation and unsupported histories remain visible.''')
    cell('code', 'SOURCES=' + repr(sources) + '\nHASHES=' + repr(hashes) + '\n' + '''import hashlib,json,sys,tempfile
from pathlib import Path
WORK=Path(tempfile.mkdtemp(prefix="perfectjet-bridges-"))
for name,source in SOURCES.items():
    assert hashlib.sha256(source.encode()).hexdigest()==HASHES[name]
    path=WORK/"src"/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(source)
sys.path.insert(0,str(WORK/"src"))
print("Verified",len(SOURCES),"embedded source modules")
''')
    cell('markdown', r'''The measured source includes a post-onset half-second functional $A_T=2[Delta x_parallel-Tv_parallel(t_o)]/T^2$. A train-player-only numerical delay model forecasts physical movement outputs. Physical coordinates remain meaningful when SVD bases rotate between fits. Its finite horizon and descriptive support distance are explicit.

The exact sensing receipt includes a counterexample to isolated-value greedy allocation: $21/32$ target variance reduction for the greedy pair versus $110/131$ for the best pair. A nuisance measurement with zero standalone benefit unlocks the mixed observation. This is a declared Gaussian example with synthetic costs.''')
    cell('code', '''from perfectjet.applications.nfl_scouting.bridge_receipt import build_bridge_receipt
analytic=build_bridge_receipt()
(WORK/"analytic_receipt.json").write_text(json.dumps(analytic,indent=2,allow_nan=False))
print(json.dumps({"scope":analytic["evidence_scope"],
                 "allocation":analytic["joint_measurement_allocation_bridge"]["result"],
                 "noisy_state_fixture":analytic["numerical_predictive_state_bridge"]["noisy_fixture"]},indent=2))
''')
    cell('markdown', r'''Attach the official nine-file NFL Big Data Bowl 2027 input and install the pinned scouting dependencies from the repository before executing the following cells. There is no synthetic fallback for this experiment.

The adapter retains the supplied primary outcome. Movement extraction uses explicit snap and LOS geometry, rejects invalid depth and records coverage. A two-pass tracking reader retains bounded selected-player windows. NFL context is a target adjustment, never a prospect input. Fewer than two games gives unknown cluster covariance.''')
    cell('code', '''import os
from perfectjet.applications.nfl_scouting.official import OFFICIAL_FILES,load_official_directory
from perfectjet.applications.nfl_scouting.movement_targets import load_movement_targets
DATA=Path(os.environ.get("BDB_DATA_ROOT","/kaggle/input/nfl-big-data-bowl-2027"))
if not all((DATA/name).is_file() for name in OFFICIAL_FILES):
    candidates=[p.parent for p in Path("/kaggle/input").rglob("players.csv")
                if all((p.parent/name).is_file() for name in OFFICIAL_FILES)] if Path("/kaggle/input").exists() else []
    if len(candidates)!=1:
        raise FileNotFoundError("Attach all official nine-file inputs or set BDB_DATA_ROOT; no synthetic fallback")
    DATA=candidates[0]
ds=load_official_directory(DATA,minimum_plays=30,verify_known_hashes=True)
movement=load_movement_targets(DATA,ds)
print(json.dumps({"official_input_audit":ds.manifest["official_adapter"]["audit"],
                 "movement_target_audit":movement.audit},indent=2))
''')
    cell('markdown', r'''Every temporal/inner/stacking fold rebuilds its NFL movement state, source transforms and movement target maps on training players. The decoder trains on out-of-player predicted movement, then receives predicted movement at evaluation. The comparison shares derived availability and support flags. Held-out NFL movement is read only after prospect predictions are frozen.

For a frozen decoder, $widehat y-y=[g(B,widehat q)-g(B,q)]+[g(B,q)-y]$. The two terms diagnose movement transfer and decoding. The exposed source-to-movement-to-get-off Jacobian can guide conditional measurement allocation, with caller-supplied prior/noise/cost assumptions. It does not turn fitted coefficients into exact athlete physiology.''')
    cell('code', '''from perfectjet.applications.nfl_scouting.bridges import experiment,full_refit_sensitivity
import contextlib,io
with contextlib.redirect_stdout(io.StringIO()):
    result=experiment(ds,movement,include_ngs=True,seed=81114)
    result["full_refit_sensitivity"]=full_refit_sensitivity(ds,movement,draws=64,include_ngs=True,seed=81114)
    without_ngs=experiment(ds,movement,include_ngs=False,seed=81114)
result["embedded_source_hashes"]=HASHES
result["without_NGS_chronology_sensitivity"]=without_ngs
(WORK/"private_bridge_results.json").write_text(json.dumps(result,indent=2))
print(json.dumps({key:value for key,value in result.items() if key not in {"folds","without_NGS_chronology_sensitivity","embedded_source_hashes"}},indent=2))
''')
    cell('markdown', r'''The file contains aggregate development evidence and private player-level outputs. Report paired equal-player prediction errors, calibration, coverage, class comparisons and the frozen-budget shortlist; expose losses and nulls. A positive continuation result is a mechanism result. A positive exact allocation result is conditional information theory. A real scouting advantage requires practical NFL prediction/decision improvement and independent future confirmation. Existing adaptive use of a class is not undone by refitting.

The repository preserves failed duration, phase/order and pooled profiles alongside the new bridge. A failed primary endpoint remains a failed primary endpoint. Use the transfer decomposition to locate the next repair rather than replacing the headline after seeing outcomes.''')
    notebook = {'nbformat': 4, 'nbformat_minor': 5,
                'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
                             'language_info': {'name': 'python'},
                             'perfectjet': {'version': '0.13.0',
                                           'execution_status': 'unexecuted_notebook_runner_evidence_separate',
                                           'source_sha256': hashes}}, 'cells': cells}
    path = ROOT / 'notebooks/PerfectJet_Math_Bridges.ipynb'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notebook, indent=1) + '\n')
    for row in cells:
        if row['cell_type'] == 'code':
            compile(row['source'], str(path), 'exec')
    print(json.dumps({'embedded_sources': len(sources),
                      'code_cells_syntax_checked': sum(x['cell_type'] == 'code' for x in cells),
                      'executed_on_NFL_data': False}))


if __name__ == '__main__':
    build()
