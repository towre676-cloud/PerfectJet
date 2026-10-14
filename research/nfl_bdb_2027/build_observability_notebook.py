"""Build a self-contained public notebook with private temporary intermediates."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
def build():
    nb={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'},'language_info':{'name':'python','version':'3.11'}},'cells':[]}
    def md(s):nb['cells'].append({'cell_type':'markdown','metadata':{},'source':s.splitlines(keepends=True)})
    def code(s):nb['cells'].append({'cell_type':'code','metadata':{},'source':s.splitlines(keepends=True),'outputs':[],'execution_count':None})
    md('''# What carries from the Combine to the game?

**A receiver movement study with matched conventional baselines, player-held-out validation, and negative controls.** Detailed tracking can describe an athlete beautifully without improving scouting predictions. We ask whether sprint response signatures contain information beyond ordinary Combine measurements, and distinguish that question from forecasting a receiver after observing the beginning of an NFL route.

This is an exploratory continuation. Earlier experiments already inspected the 2025 WR class; this notebook does not create a fresh blind test. Its reconstructed implementation strictly excludes nonunique snap/release events, retaining one fewer 2023 route than the earlier lost implementation. Historical aggregate outputs remain a separate record and are not silently substituted for this execution. The cells below recompute every result from the supplied official data. No synthetic data are used for scientific findings.
''')
    modules={n:(ROOT/n).read_text() for n in ['analysis.py','repo_predict.py','mechanism.py','observability.py','observability_diagnostics.py','render_observability.py']}
    modules['exact_linear.py']=(ROOT/'vendor/pp/exact_linear.py').read_text();modules['PERFECTPOWER_LICENSE.txt']=(ROOT/'vendor/pp/LICENSE').read_text()
    hashes={x['file']:x['sha256'] for x in json.loads((ROOT/'receipts/actual/acquisition.json').read_text())['files']}
    code('''import os, sys, json, hashlib, tempfile, contextlib
from pathlib import Path
import numpy as np, pandas as pd
from IPython.display import display, Image, HTML
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
DATA = Path(os.environ.get('BDB_DATA_ROOT','/kaggle/input/nfl-big-data-bowl-2027'))
if not (DATA/'players.csv').exists():
    candidates = list(Path('/kaggle/input').rglob('players.csv')) if Path('/kaggle/input').exists() else []
    if len(candidates)!=1: raise FileNotFoundError('Attach the official competition dataset or set BDB_DATA_ROOT.')
    DATA=candidates[0].parent
OUT=Path(tempfile.mkdtemp(prefix='bdb_movement_private_'))
SRC=OUT/'sources'; SRC.mkdir()
MODULES='''+repr(modules)+'''
for name,source in MODULES.items(): (SRC/name).write_text(source)
sys.path.insert(0,str(SRC))
import observability as O, observability_diagnostics as D, render_observability as V
EXPECTED='''+repr(hashes)+'''
for name,expected in EXPECTED.items():
    h=hashlib.sha256()
    with (DATA/name).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
    if h.hexdigest()!=expected: raise ValueError('Official source snapshot differs: '+name)
print('Verified nine official inputs. Private intermediates stay in a temporary directory.')
''')
    md('''## Population and measurements

Combine attempts are restricted to WRs and the forty-yard dash. Repeated attempts are aggregated by player median. Game windows come from non-nullified rookie regular-season routes, with unique snap/release events, continuous 10 Hz samples from snap through 1.5 seconds, and release at or after 1.5 seconds. Require at least twenty qualifying windows per receiver. This conditions on recorded plays with sufficient duration; it is not a population of every prospect or every NFL situation.

The outcome is absolute mean speed at 1.3–1.5 seconds. Inputs from NFL tracking end at 0.5 seconds: snap speed, mean speed at 0.3–0.5 seconds, a backward-looking acceleration estimate, and traveled distance. Absolute speed avoids mathematical coupling from subtracting an input speed from the target. Charted route/coverage attributes and vendor-derived speed may not be causally available online, so we do not call this a deployable live predictor.
''')
    code('''with (OUT/'extraction.log').open('w') as log, contextlib.redirect_stdout(log):
    rows, population = O.prepare(DATA,OUT)
print(json.dumps(population,indent=2))
''')
    md(r'''## Motion signatures and meaningful comparators

Fit two nonlinear responses to each smoothed speed trace: $s_1(t)=V(1-e^{-z})$ and $s_2(t)=V[1-(1+z)e^{-z}]$, with $z=\max((t-d)/\tau,0)$. Capacity $V$, response time $\tau$, onset offset $d$, fit residual, and Jacobian conditioning accompany fixed-time speed/acceleration samples, Legendre profile coefficients, and a speed ratio: twenty-six features. These are descriptive response surrogates, not established biomechanical laws.

The conventional model includes height, weight, timed tests, jumps, hand/arm measurements, bench reps, NGS scores, and shared football context. We compare this baseline with and without early game movement. Each receives the same five candidates: three ridge penalties, a random forest, and extra trees. Combine-augmented models receive exactly the same budget. Median imputation, scaling, percentile clipping, physical-attribute residualization, quadratic lifting, and compression are fitted on training players only. PCA supplies an unsupervised comparator; PLS compresses toward training-player response innovations from an additional player-separated nuisance fit. No held-out outcome trains either compression.

Every player receives equal total fitting and evaluation weight. Four outer folds and three inner folds split unique players within draft class, then keep all their routes together. Forward selection trains on 2023 and tunes on 2024, then refits both before evaluating 2025. Pooled earlier-player folds assess unseen-player generalization; they do not establish future-season generalization. The 2025 comparison is exploratory transport because earlier research inspected that class.
''')
    code('''with (OUT/'models.log').open('w') as log, contextlib.redirect_stdout(log):
    result=O.experiment(rows,OUT/'absolute_speed')
for key in ['nested','exploratory_2025']:
    print(key, json.dumps({k:result[key][k] for k in ['players','rows','mse','comparisons']},indent=2))
''')
    md('''## Challenge the result before interpreting it

Compare against holding early speed constant and extrapolating early acceleration. Swap complete Combine profiles among training players within class thirty times, retaining the chosen configuration. This tests attribution to the actual source profile; it is a diagnostic, not a permutation p-value with full model reselection. First/last-attempt correlations expose response instability without treating it as pure sensor noise. A paired player bootstrap uses 5,000 resamples; team-cluster resampling probes another dependence structure. These intervals condition on fitted models and do not estimate uncertainty across future draft classes.
''')
    code('''with (OUT/'controls.log').open('w') as log, contextlib.redirect_stdout(log):
    diagnostics=D.run(OUT)
print(json.dumps(diagnostics,indent=2))
''')
    md('''## Geometry, uncertainty, and the coaching interpretation

The first source attempt in sorted identifiers is selected independently of NFL outcomes. Its trajectory, speed response, and speed–acceleration phase portrait show what a timed forty misses. Repeatability plots distinguish capacity from response time. Model comparisons and paired intervals separate observation-channel benefit from incremental Combine benefit; shuffled profiles challenge a tempting scouting story. Calibration uses route counts for display, while model losses remain player-balanced.
''')
    code('''figures=V.run(OUT,OUT/'figures')
for figure in figures: display(Image(filename=str(figure)))
test=result['exploratory_2025']; baseline=test['mse']['conventional_without_state']; state=test['mse']['conventional_with_state']
print(f'Observed early-state relative MSE reduction: {100*(1-state/baseline):.2f}%')
print('Incremental Combine result:',test['comparisons']['target_motion_increment'])
''')
    md('''## Why a movement history can help—and what exact algebra cannot prove

For a supplied two-state linear response, an instantaneous speed observation can hide acceleration. Exact target recovery requires the future target row to lie in the row span of the observation map. Two histories may resolve the hidden direction. The licensed PerfectPower rational calculus checks that finite algebra below; it does not prove that NFL movement follows the surrogate or that a learned model generalizes. This motivates a testable observation design, rather than importing an unrelated number-theory theorem as a football guarantee.
''')
    code('''from fractions import Fraction as Q
import exact_linear as E
q=Q(869479,1000000)
transition=E.matrix([[q,q/10],[0,q]])
observation=E.matrix([[1,0]])
future=E.multiply(observation,transition)
print('One observation:',E.target_factor(observation,future))
history=E.matrix([observation[0],future[0]])
print('Two observations:',E.target_factor(history,E.multiply(future,transition)))
print('Exact only for the supplied rational surrogate; no real-athlete theorem claimed.')
''')
    md('''## Findings and boundaries

The completed reconstruction reduces future-speed MSE from 0.97226 to 0.64689 in eighteen 2025 receivers when early game state is observed: 33.47%. Earlier-player nested validation improves by 26.52%. The 2025 state-channel difference interval is [0.26236, 0.39855], and team-cluster resampling remains positive. This demonstrates information in the recorded game-state channel, not an added pre-draft Combine advantage. The incremental target-conditioned Combine difference is only 0.00220, with interval [−0.00226, 0.00707]; earlier nested prediction worsens slightly. Shuffled training profiles have lower average test MSE than the real profiles. Across eighty-one repeat participants, fitted capacity has rank correlation 0.825, but response time only 0.373. These results keep the scouting hypothesis uncertain. Faster subsequent movement also does not automatically mean better separation, coverage, or team outcomes. The retained historical receiver-separation study and defensive-back transition study did not establish a scouting improvement; their aggregate record is preserved separately and those studies are not rerun by this notebook.

Our contribution is the distinction between a measurable motion signature, a repeatable player characteristic, and a transferable predictive variable. Coaches can use the geometric views to inspect acceleration strategies; scouts should require stable, out-of-player evidence before assigning draft value. Small cohorts, conditional play availability, shared team effects, charted context, and prior test inspection limit broad claims. Future validation must use a genuinely new class or independently held-out target and a frozen protocol.

Official sources: [competition data](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/data), [rules](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/rules). Competition data and private player-level outputs are excluded from the distributed package; notebook intermediates stay outside public output directories. No integration with the betting application, public Kaggle publication, or formal entry is implied by local execution. Source modules and source hashes are embedded above; pinned local dependencies are supplied in the package.
''')
    path=ROOT/'notebooks/Movement_Observability.ipynb';path.write_text(json.dumps(nb,indent=1));words=sum(len(''.join(c['source']).split()) for c in nb['cells'] if c['cell_type']=='markdown');assert words<=2000
    print(json.dumps({'notebook':str(path),'narrative_words':words,'composite_figures':5,'code_cells':sum(c['cell_type']=='code' for c in nb['cells'])}));return path
if __name__=='__main__':build()
