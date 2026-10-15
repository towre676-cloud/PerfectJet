"""Build a source-complete replay notebook; optionally execute its public cells."""
import argparse,hashlib,json
from pathlib import Path
import nbformat

ROOT=Path(__file__).resolve().parents[1]

def build(execute=False):
    files=sorted((ROOT/'src/perfectjet').rglob('*.py'))
    files += [ROOT/'scripts'/name for name in ('prepare_official_bridge_data.py','run_stopped_flow.py',
        'run_motor_sensitivity.py','run_reliable_stopped_flow.py','run_repeat_controls.py')]
    files += [ROOT/'docs/nfl/ROLLING_PROTOCOL.json',ROOT/'results/real-nfl/preparation.json']
    files += sorted((ROOT/'results/stopped-flow').glob('*.json'))
    # Self-referential whole-package manifests are not executable input.
    files=[p for p in files if p.name not in ('release-evidence.json',)]
    payload={p.relative_to(ROOT).as_posix():p.read_text() for p in files}
    digests={k:hashlib.sha256(v.encode()).hexdigest() for k,v in payload.items()}
    md=nbformat.v4.new_markdown_cell;code=nbformat.v4.new_code_cell
    cells=[md('''# PerfectJet 0.14 — Stopped-flow readouts

This notebook contains the complete runnable Python source, the new study's runners and retained aggregate evidence. It does not contain restricted raw tracking or individual prospect predictions. The official experiments were executed separately; these cells replay exact mathematics and display those hash-bound aggregate results, not a new independent football experiment.

The result is more source coverage and useful repeated-measurement denoising, **not an established scouting edge**. Read the full study in `docs/nfl/STOPPED_FLOW.md`.''')]
    cells.append(code('''import hashlib, json, pathlib, sys, tempfile
SOURCES = '''+repr(payload)+'''
EXPECTED = '''+repr(digests)+'''
CORE = pathlib.Path(tempfile.mkdtemp(prefix="perfectjet-stopped-flow-"))
for relative, text in SOURCES.items():
    if hashlib.sha256(text.encode()).hexdigest() != EXPECTED[relative]:
        raise ValueError("Source digest mismatch: " + relative)
    destination = CORE / relative
    if not destination.resolve().is_relative_to(CORE.resolve()):
        raise ValueError("Unsafe source path")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text)
sys.path.insert(0, str(CORE / "src"))
print("Verified embedded files:", len(SOURCES))
def result(name):
    return json.loads(SOURCES["results/stopped-flow/" + name + ".json"])
'''))
    cells.append(md('''## An exact hidden-launch witness

The two histories have a common stationary starting point, nonnegative velocity and acceleration, and the identical recorded tail $x(t)=t+t^2/2$ for $t\\ge0$. Their launch times are −2 and −1. Exact boundary matching proves C² regularity; the positive polynomial factors in the receipt prove the sign constraints throughout each interval. This is nonidentifiability in a declared model, not a claim about every possible force law.'''))
    cells.append(code('''from perfectjet.launch_ambiguity import ambiguity_receipt, state
from fractions import Fraction as Q
print(json.dumps(ambiguity_receipt(), indent=2))
assert state("early", Q(-3,2), 1) > 0
assert state("late", Q(-3,2), 1) == 0
for t in (Q(0), Q(1,5), Q(10)):
    assert all(state("early", t, k) == state("late", t, k) for k in range(3))
'''))
    cells.append(code('''import matplotlib.pyplot as plt
times = [Q(k,100) for k in range(-250,101)]
fig, ax = plt.subplots(figsize=(9,4.5))
for name in ("early", "late"):
    ax.plot([float(t) for t in times], [float(state(name,t)) for t in times], label=name+" launch")
ax.axvline(0, linestyle=":", label="recording begins")
ax.set(xlabel="Time (seconds)", ylabel="Position (yards)", title="Different launches; identical recorded tails")
ax.legend(); fig.tight_layout(); plt.show()
'''))
    cells.append(md('''## Exact order-sensitive acceleration

The antisymmetric time-position area cancels constant position and constant velocity. With a C² path it is a positive weighted mean acceleration. The sampled correction and minimum-variance cubic jet are checked in rational arithmetic. Their 1/50 and 1/56 noise ratios are conditional algebraic statements under independent equal-variance position errors and the stated polynomial/window assumptions, not football prediction gains.'''))
    cells.append(code('''from perfectjet.stopped_jets import readout_receipt, minimum_variance_jet, area_acceleration_weights
print(json.dumps(readout_receipt(), indent=2, default=str))
t = tuple(Q(i,10) for i in range(6))
area = area_acceleration_weights(t)
assert list(area) == list(map(Q,[20,-10,-10,-10,-10,20]))
assert sum(area) == 0 and sum(w*x for w,x in zip(area,t)) == 0
weights = minimum_variance_jet(t,2,3)["weights"]
assert sum(w*w for w in weights) == Q(7500,7)
assert sum(w*w for w in weights)/60000 == Q(1,56)
'''))
    cells.append(md('''## Actual coverage and temporal outcome results

Each forty gate supports 177 attempts, 93 source players, 57 eligible NFL players and 84 players with independent repeats. Three overlapping gates are not three independent attempts. Each temporal NFL comparison below evaluates 51 players; the thousands of underlying plays are not extra independent scouting cases.'''))
    cells.append(code('''import pandas as pd
from IPython.display import display
coverage = pd.DataFrame(result("source-coverage")["by_drill_gate"])
display(coverage[coverage.drill == "FORTY_YARD_DASH"])
rows=[]
for experiment in ("primary", "matched-motor", "matched-motor-without-ngs"):
    for name, comparison in result(experiment)["comparisons"].items():
        rows.append({"experiment":experiment,"comparison":name,"gain_percent":100*comparison["gain"],
                     "fixed_90_percent":[round(100*x,2) for x in comparison["fixed_prediction_interval_90"]]})
display(pd.DataFrame(rows))
print("Matched-movement kinematic FULL-REFIT interval (%):",
      [round(100*x,2) for x in result("motor-full-refits")["intervals_90"]["kinematics_vs_conventional"]])
'''))
    cells.append(md('''## Repeated-measurement denoising with strong controls

A three-coordinate noise-aware estimator improves independent-attempt MSE over raw observations. It does not beat ordinary multivariate ridge. Every calibration uses earlier classes; inner tuning keeps all orientations and copies of one player together. The following plot uses complete original-player refits, not fixed-model intervals. It remains an adaptive development sensitivity, not a prospective guarantee.'''))
    cells.append(code('''study=result("repeat-controls"); refits=result("repeat-controls-refits")
rows=[]
for name,c in study["comparisons"].items():
    rows.append({"comparison":name,"gain_percent":100*c["gain"],
                 "full_refit_90_percent":[100*x for x in refits["intervals_90"][name]]})
display(pd.DataFrame(rows))
fig,ax=plt.subplots(figsize=(9,4.5))
for i,row in enumerate(rows):
    lo,hi=row["full_refit_90_percent"]
    ax.plot([lo,hi],[i,i],linewidth=2)
    ax.plot(row["gain_percent"],i,marker="o")
ax.axvline(0,linestyle=":")
ax.set_yticks(range(len(rows)),[r["comparison"].replace("reliable_vs_","") for r in rows])
ax.set(xlabel="MSE reduction versus comparator (%)",title="Repeat denoising: gain depends on the comparator")
fig.tight_layout();plt.show()
'''))
    cells.append(md('''## Reproduce the private official experiment

The embedded source can run the study after installing NumPy, pandas, SciPy and scikit-learn (the repository's `scouting` extra). Supply your already-owned official input or the provenance-checked owned checkpoint, never an untrusted pickle. The preparation receipt is embedded; restricted individual outputs must be outside the public repository.

Run `scripts/run_stopped_flow.py`, `scripts/run_motor_sensitivity.py`, `scripts/run_reliable_stopped_flow.py` and `scripts/run_repeat_controls.py` from the reconstructed `CORE`, passing `--checkpoint`, `--preparation`, `--out` and `--private`. The first two use `--refits 32`; repeat controls use `--refits 64`. Their complete command lines and all mathematical qualifications are in the monograph. No credentials are requested by this notebook.'''))
    nb=nbformat.v4.new_notebook(cells=cells,metadata={
        'kernelspec':{'name':'python3','language':'python','display_name':'Python 3'},
        'language_info':{'name':'python'},'perfectjet':{'version':'0.14.0','source_sha256':digests,
          'scope':'exact replay and retained aggregate display; official runs recorded separately'}})
    if execute:
        from nbclient import NotebookClient
        NotebookClient(nb,timeout=120,kernel_name='python3').execute()
    output=ROOT/'notebooks/PerfectJet_Stopped_Flow.ipynb';nbformat.write(nb,output)
    print(json.dumps({'notebook':str(output.relative_to(ROOT)),'embedded_files':len(payload),'executed':execute,'bytes':output.stat().st_size}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');a=p.parse_args();build(a.execute)
