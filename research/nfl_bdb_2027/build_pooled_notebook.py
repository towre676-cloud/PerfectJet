"""Self-contained executable scouting audit with all adaptive trials retained."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
def build():
    cells=[]
    def md(text):cells.append({'cell_type':'markdown','metadata':{},'source':text.splitlines(True)})
    def code(text):cells.append({'cell_type':'code','metadata':{},'source':text.splitlines(True),'execution_count':None,'outputs':[]})
    names=['analysis.py','repo_predict.py','mechanism.py','observability.py','turn_transfer.py','front_transfer.py','phase_population.py','canonical_transfer.py','stress_features.py','stress_transfer.py','capacity_stress.py','pooled_recovery.py','pooled_transfer.py','pooled_safe_blend.py','pooled_schur_blend.py','pooled_stability.py','pooled_getoff.py','pooled_refits.py','render_pooled.py']
    names += ['vendor/dynacomp_stress/src/dynacomp/'+s for s in ['__init__.py','bounds.py','rational.py','finite.py']]
    names += ['vendor/perfectpower_movement/python/perfectpower/'+s for s in ['__init__.py','movement_language.py','movement_features.py']]+['vendor/perfectpower_movement/scripts/run_movement_transfer.py']
    modules={s:(ROOT/s).read_text() for s in names};hashes={s['file']:s['sha256'] for s in json.loads((ROOT/'receipts/actual/acquisition.json').read_text())['files']}
    md('''# When does a movement signal deserve a scouting adjustment?

We test sparse Combine turn-response profiles against conventional scouting traits and our previous duration/sequence lead. The cohort comprises 74 defensive-front rookies: 23 in 2023, 22 in 2024 and 29 in 2025. Pressure is the supplied recorded timestamp indicator averaged over eligible rookie records; missing timestamps are not independently established negative events. Charted get-off is supporting, not a replacement primary outcome or pure reaction-time measurement.

The 2025 class has already informed prior investigations. Every result here is exploratory. No untouched confirmation or contest-win claim follows from these computations. Public outputs contain aggregate diagnostics; private player profiles remain temporary.
''')
    code('''import os,sys,json,hashlib,tempfile,contextlib
from pathlib import Path
from IPython.display import display,Image
DATA=Path(os.environ.get('BDB_DATA_ROOT','/kaggle/input/nfl-big-data-bowl-2027')).resolve()
if not (DATA/'players.csv').exists():
    options=list(Path('/kaggle/input').rglob('players.csv')) if Path('/kaggle/input').exists() else []
    if len(options)!=1:raise FileNotFoundError('Attach official competition data or set BDB_DATA_ROOT')
    DATA=options[0].parent
WORK=Path(os.environ.get('BDB_WORK_ROOT',tempfile.mkdtemp(prefix='bdb_pooled_'))).resolve();WORK.mkdir(exist_ok=True)
os.chdir(WORK);sys.path.insert(0,str(WORK))
MODULES='''+repr(modules)+'''
for name,text in MODULES.items():
    path=WORK/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
HASHES='''+repr(hashes)+'''
for name,expected in HASHES.items():
    h=hashlib.sha256()
    with (DATA/name).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    assert h.hexdigest()==expected,'Official data mismatch: '+name
OUT=WORK/'receipts/pooled';OUT.mkdir(parents=True,exist_ok=True)
import numpy as np,pandas as pd
import front_transfer as F,stress_features as S,capacity_stress as A,canonical_transfer as C
import pooled_transfer as P,pooled_safe_blend as B,pooled_schur_blend as J,pooled_stability as L,pooled_getoff as G,pooled_refits as R,render_pooled as V
print('Nine official input hashes verified;27 source modules embedded.')
''')
    md('''## Pool assumptions rather than invent individual identification

Detect source-only heading changes and measure recovery after 80% estimated angular progress. Entry speed and turn angle define demand. Earlier work found 34.1% narrower sensitivity across declared alignment/smoothing scenarios; this is not predictive improvement or calibrated sensor uncertainty.

Fit a shared nonlinear nuisance response using training-player body/timed traits and entry-speed/angle terms. Training-player residuals use three whole-player source crossfits; evaluated-player residuals use the full training source reference. For each player/drill, describe deviations with four regularized coefficients on standardized speed, angle and their product. Penalize those coefficients, balance turns within an attempt, and reduce weight for broad processing sensitivity. Source repeats estimate a noise scale inside training data. These regularized curves depend on assumptions; sparse panels remain structurally underidentified.

Compare conventional, capacity, duration, pooled and combined models. All share availability and attempt-count predictors. Imputation, scaling, source residualization, PCA, penalties and fallback selection occur within training folds. Four outer/three inner player splits are repeated over three declared partitions. Forward choices use 2023→2024 only. Repeating partitions does not multiply the sample size.
''')
    code('''with (WORK/'private_pooled_extraction.log').open('w') as log,contextlib.redirect_stdout(log):
    if not (WORK/'private_front/private_rows.pkl').exists():F.prepare(DATA,'private_front')
    if not (WORK/'private_stress_clock/private_turns.pkl').exists():S.prepare(DATA,out='private_stress_clock',clock=True)
    if not (WORK/'private_stress_clock/private_capacity.pkl').exists():A.capacity(DATA)
    if not (WORK/'private_canonical_vendor/players.pkl').exists():C.V.extract(DATA,WORK/'private_front/private_rows.pkl',WORK/'private_canonical_vendor')
units,turns=P.prepare()
with (WORK/'private_pooled_models.log').open('w') as log,contextlib.redirect_stdout(log):
    for seed in [P.SEED,P.SEED+200,P.SEED+400]:
        r=P.evaluate(units,turns,f'private_pooled_{seed}',seed,seed==P.SEED)
        (OUT/f'results_{seed}.json').write_text(json.dumps(r,indent=2))
print('Source reconstructed:',len(units),'players;',len(turns),'turns. Primary nested models completed.')
''')
    md('''## Adapt, preserve the failed trials, and isolate the correction

The initial pooled comparison did not establish predictive benefit. A subsequent high-shrinkage convex blend altered baseline and movement penalties together; preserve it as a diagnostic. The next calculation fixes the conventional penalty at 100 and penalizes added movement at 1000. Schur elimination is exactly equivalent to this block-penalized joint regression, with zero motion returning the unchanged conventional prediction.

Enumerate a finite grid of nonnegative correction weights whose sum is at most one. Select mean improvement, worst-class improvement, or worst-class improvement minus one standard error using inner training predictions. These guards are selection heuristics, not calibrated guarantees. Zero correction is legitimate. All three policies remain reported.

Expand the original duration model to twelve declared partitions under its original five-availability baseline. This benchmark differs from the new count-controlled one. Check recorded-outcome repeatability by splitting games within players 200 times. Test charted get-off using the same pooled bank without clipping time predictions to probability bounds. Finally, 64 class-stratified 80% training subsets per outcome refit source and scouting transforms with fixed configurations. Their quantile ranges describe sensitivity, not nominal confidence intervals or complete selection uncertainty.
''')
    code('''with (WORK/'private_pooled_followups.log').open('w') as log,contextlib.redirect_stdout(log):
    for seed in [P.SEED,P.SEED+200,P.SEED+400]:B.run(units,turns,seed,seed==P.SEED)
    J.run();L.run();G.run();refits=R.run()
expanded=json.loads((OUT/'canonical_stability.json').read_text())
gains=[r['development']['comparisons']['duration_combined']['relative_gain'] for r in expanded['results']]
print('Twelve duration partitions: mean relative gain',round(np.mean(gains)*100,3),'%; positive partitions',sum(g>0 for g in gains))
for outcome in ['pressure_event','player_get_off']:
    print(outcome,'64 training-subset sensitivity gain quantiles:',refits['results'][outcome]['relative_gain_quantiles'])
print('Pressure game-half repeatability:',json.loads((OUT/'outcome_repeatability.json').read_text())['rank_correlation_quantiles'])
print('Get-off game-half repeatability:',json.loads((OUT/'getoff_repeatability.json').read_text())['rank_correlation_quantiles'])
''')
    md('''## What the evidence supports

Better turn alignment and a tested observation engine do not automatically identify hidden talent. The original three duration gains reproduce, but the expanded partition audit weakens that lead. Pooled recovery is not consistently better than the conventional model. A favorable supporting get-off forward result requires earlier-class stability and independent confirmation before scouting use.

Game-half diagnostics help prioritize a more repeatable target, while documented field semantics and context differences still matter. They do not establish a physical ceiling on prediction. Reserve independent athletes/outcomes before confirmatory model selection; validate turn completion and collect distinct demands and repeats where individual curves are needed. A coach-facing development intervention would require causal evidence.
''')
    code('''V.render()
for name in ['demand_geometry.png','model_stability.png','signal_and_outcome.png','forward_results.png']:
    display(Image(filename=str(OUT/name)))
print('All adaptive stages and aggregate receipts retained; no public submission or betting-app integration.')
''')
    nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'nbformat':4,'nbformat_minor':5}
    (ROOT/'notebooks/Pooled_Recovery_Scouting_Audit.ipynb').write_text(json.dumps(nb,indent=1))
if __name__=='__main__':build()
