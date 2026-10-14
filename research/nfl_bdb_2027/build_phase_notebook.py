"""Self-contained raw-data-to-results notebook for the phase population test."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent

def build():
    cells=[]
    def md(s):cells.append({'cell_type':'markdown','metadata':{},'source':s.splitlines(True)})
    def code(s):cells.append({'cell_type':'code','metadata':{},'source':s.splitlines(True),'outputs':[],'execution_count':None})
    md('''# The movement between stopwatch ticks

Do defensive-front prospects organize approach, braking, direction change and recovery in a way that predicts rookie pressure performance? We test a finite movement-language adaptation of PerfectPower: sum over constrained possible histories rather than select a single noisy history. This experiment responds to the previous result's sensitivity to the definition of drill onset.

**Scope.** DE, DT, NT and OLB rookies with at least 30 eligible charted regular-season rush records. The target is each athlete's observed pressure-event frequency versus the mean model prediction over their actual NFL workload. This conditions on NFL snap geometry and game context; it is not an unconditional pre-draft production forecast or a causal training recommendation. The 2025 class has already been inspected. All transport results below are exploratory.
''')
    modules={name:(ROOT/name).read_text() for name in ['analysis.py','repo_predict.py','mechanism.py','observability.py','turn_transfer.py','front_transfer.py','phase_population.py','phase_correction.py','render_phase_population.py']}
    hashes={r['file']:r['sha256'] for r in json.loads((ROOT/'receipts/actual/acquisition.json').read_text())['files']}
    configs=json.loads((ROOT/'private_front_macro/pressure_event/results.json').read_text())
    # Embed only configuration receipts, not predictions or player identifiers.
    cfg={'folds':[{'fold':r['fold'],'family':'conventional','config':r['config']} for r in configs['folds'] if r['family']=='conventional'],'selection':[r for r in configs['selection'] if r['family']=='conventional']}
    code('''import os,sys,json,hashlib,tempfile,contextlib
from pathlib import Path
from IPython.display import display,Image
DATA=Path(os.environ.get('BDB_DATA_ROOT','/kaggle/input/nfl-big-data-bowl-2027')).resolve()
if not (DATA/'players.csv').exists():
    choices=list(Path('/kaggle/input').rglob('players.csv')) if Path('/kaggle/input').exists() else []
    if len(choices)!=1:raise FileNotFoundError('Attach the official competition dataset or set BDB_DATA_ROOT')
    DATA=choices[0].parent
WORK=Path(os.environ.get('BDB_WORK_ROOT',tempfile.mkdtemp(prefix='bdb_phase_'))).resolve();WORK.mkdir(exist_ok=True)
os.chdir(WORK);sys.path.insert(0,str(WORK))
MODULES='''+repr(modules)+'''
for name,text in MODULES.items():(WORK/name).write_text(text)
HASHES='''+repr(hashes)+'''
for name,expected in HASHES.items():
    h=hashlib.sha256()
    with (DATA/name).open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''):h.update(chunk)
    assert h.hexdigest()==expected,'Official source hash mismatch: '+name
import pandas as pd,numpy as np
import front_transfer as F,phase_population as P,phase_correction as C,render_phase_population as V
folder=WORK/'private_front_macro/pressure_event';folder.mkdir(parents=True,exist_ok=True)
if not (folder/'results.json').exists():(folder/'results.json').write_text(json.dumps('''+repr(cfg)+'''))
print('Verified nine official source files. Embedded code and fixed configurations loaded.')
''')
    md('''## Keep the uncertainty explicit

Four sustained onset thresholds (0.5, 1, 1.5 and 2 yards/s) supply up to five seconds of movement each. Smoothing positions uses a seven-frame cubic filter; acceleration comes from supplied speed and rotation from the smoothed trajectory. Slow-frame rotation is suppressed. Geometry remains invariant to position, rotation and reflection.

For each window, four states permit only staying or advancing: approach → brake → redirect → recover. Each path starts in approach and ends in recovery. A sum-product forward/backward calculation gives weighted phase occupancy and phase-conditioned channel means without enumerating all C(n−1,3) paths. Three cost temperatures and four onset thresholds yield feature means and sensitivity spreads. Signed speed/acceleration/rotation areas retain order information.

Weights are assumptions, **not calibrated probabilities of the true phases**. Equal weighting of legal paths induces a duration prior; the four-state language may poorly describe drills with several turns. A temperature/onset mixture is a sensitivity analysis, not a solution to semantic labeling. No official plant or start-cue labels were available to calibrate it.
''')
    code('''with (WORK/'phase_extraction.log').open('w') as log,contextlib.redirect_stdout(log):
    if not (WORK/'private_front/private_rows.pkl').exists():F.prepare(DATA,'private_front')
    if not (WORK/'private_phase_population/private_rows.pkl').exists():P.prepare(DATA)
pop=json.loads((WORK/'private_phase_population/population.json').read_text())
print('Athletes:',pop['NFL_players'],'NFL records:',pop['NFL_rows'],'skill attempts:',pop['attempts'])
print('Onset span quantiles (s):',pop['onset_span_quantiles_s'])
''')
    md('''## Compare identical statistical machinery

Four source families receive identical whole-athlete bootstrap samples and model budgets: conventional scouting plus snap/context controls; sprint and onset-averaged ordinary movement summaries; those summaries plus sequence features; and the same summaries plus features computed after jointly shuffling channel frames. Common summaries already include timed speeds, geometry and a simple speed/acceleration signed area. This is a strong baseline with some temporal information, not a purely unordered stopwatch comparison. Shuffling preserves every window's channel multiset while changing chronology in the added sequence coordinates; it does not erase temporal information from the common summaries. It also changes local smoothness, so a benefit over shuffling would support incremental order-related information without proving a physiological mechanism. One fixed shuffle per window is a diagnostic, not a permutation p-value.

Use four outer player folds on 2023/2024, with configurations previously chosen by conventional-model inner player folds. Apply that same configuration to all source families. For transport, use the conventional configuration previously selected with 2023 training/2024 validation. Sixteen class-stratified athlete resamples refit every scaler, physical residualizer, PCA and model. No new configuration is selected from 2025. Conventional selection may favor its own family; this is a deliberately constrained test, not an exhaustive search of sequence models. Missing drill availability flags are common to every family.

The comparison priorities were locked before this run: sequence versus ordinary summaries, sequence versus shuffled order, then each versus conventional. Paired player bootstrap intervals hold fitted predictions fixed and omit training, model-selection, source-weight and adaptive-search uncertainty. Repeated work on these cohorts means even earlier-class results are exploratory evidence.
''')
    code('''with (WORK/'phase_models.log').open('w') as log,contextlib.redirect_stdout(log):result=P.run()
for split in ['nested','exploratory_2025']:
    print(split, 'player-rate MSE:',result[split]['player_rate_mse'])
    for key in ['summaries->sequence','shuffled->sequence','conventional->sequence']:
        c=result[split]['comparisons'][key]
        print(key,'relative error reduction:',round(100*c['relative_reduction'],2),'%, delta 95% interval:',c['ci95'])
''')
    code('''OUT=WORK/'receipts/phase_population';OUT.mkdir(parents=True,exist_ok=True)
V.geometry(DATA,OUT);V.results(OUT)
display(Image(filename=str(OUT/'phase_geometry.png')))
display(Image(filename=str(OUT/'phase_comparisons.png')))
''')
    md('''## Adapt without replacing the benchmark

After the concatenation results were inspected, we locked a second experiment: retain the unchanged conventional ensemble and add a source-only correction. On each outer training set, three player-separated conventional ensembles supply out-of-fold residuals. Average residuals over each training player's actual workload. Fit a zero-intercept ridge with fixed alpha 100 to four physical-conditioned source components, their squares and mass interactions. Predict one correction per held-out athlete and clip final probabilities to [0,1]. All families receive the same residuals and shrinkage budget; zero source coefficients recover the exact baseline.

This is an adaptive follow-up, explicitly including knowledge of the first experiment's 2025 results. No correction hyperparameter is selected from these outcomes, and no new independent test class is created by changing the model. Player residualization changes the statistical target from individual rush fluctuations to persistent athlete calibration; it does not establish a causal movement effect.
''')
    code('''with (WORK/'phase_correction.log').open('w') as log,contextlib.redirect_stdout(log):corrected=C.run()
for split in ['nested','exploratory_2025']:
    print('Baseline-preserving correction',split,corrected[split]['player_rate_mse'])
    for key in ['conventional->sequence','summaries->sequence','shuffled->sequence']:
        c=corrected[split]['comparisons'][key]
        print(key,'relative reduction:',round(100*c['relative_reduction'],2),'%, delta 95% interval:',c['ci95'])
CORRECTED=OUT/'correction';CORRECTED.mkdir(exist_ok=True)
V.results(CORRECTED,'private_phase_correction',title='Keep the baseline; shrink the movement correction')
display(Image(filename=str(CORRECTED/'phase_comparisons.png')))
''')
    md('''The first correction leaves nonlinear coordinates unscaled, so a single ridge penalty does not shrink squared components and mass interactions equally. Preserve that failed fit and test a further locked adaptation: clip each correction coordinate at its training 1st/99th percentiles, then standardize using training players before the same zero-intercept ridge. Reuse the exact baseline residuals and compare all three source families. This is numerical conditioning and an empirical support restriction, not a calibrated measurement-error model. It was designed after seeing the first correction and therefore remains adaptive exploratory work.
''')
    code('''with (WORK/'phase_scaled_correction.log').open('w') as log,contextlib.redirect_stdout(log):scaled=C.run('private_phase_correction_scaled',scaled=True)
for split in ['nested','exploratory_2025']:
    print('Scaled, support-limited correction',split,scaled[split]['player_rate_mse'])
    for key in ['conventional->sequence','summaries->sequence','shuffled->sequence']:
        c=scaled[split]['comparisons'][key]
        print(key,'relative reduction:',round(100*c['relative_reduction'],2),'%, delta 95% interval:',c['ci95'])
SCALED=OUT/'scaled';SCALED.mkdir(exist_ok=True)
V.results(SCALED,'private_phase_correction_scaled',title='Standardize and bound the correction using training athletes')
display(Image(filename=str(SCALED/'phase_comparisons.png')))
''')
    md('''## Read the test as evidence

Positive reductions mean smaller prediction error, not more pressures produced. If ordering does not improve on ordinary summaries, the proposed PerfectPower linkage is unsupported by this test. If sequence features perform well only on earlier classes, transport remains unresolved. If shuffled features match or improve on the sequence family, do not attribute any source gain specifically to movement order.

A development protocol would require validated semantic phase labels, repeatability across attempts, and independent prospects or classes. These data can generate a candidate movement signal, but a causal coaching intervention or reliable hidden-talent ranking needs additional evidence. We retain all families and their uncertainty regardless of which is best.
''')
    nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}},'nbformat':4,'nbformat_minor':5}
    (ROOT/'notebooks/Movement_Phase_Populations.ipynb').write_text(json.dumps(nb,indent=1))
if __name__=='__main__':build()
