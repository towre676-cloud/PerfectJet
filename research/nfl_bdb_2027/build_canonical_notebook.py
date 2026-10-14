"""Build the canonical two-session raw-data research notebook."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent

def build():
    cells=[]
    def md(s):cells.append({'cell_type':'markdown','metadata':{},'source':s.splitlines(True)})
    def code(s):cells.append({'cell_type':'code','metadata':{},'source':s.splitlines(True),'outputs':[],'execution_count':None})
    md('''# What survives two movement engines?

We combine the defensive-front movement study with PerfectPower's explicit-duration movement-language engine. Both read **the same 74 rookies, 361 Combine skill attempts and 14,665 eligible NFL rush records**. They are complementary calculations on one cohort, not independent replications. Our question is whether Combine-only motion profiles predict a player's recorded rookie pressure frequency beyond conventional scouting traits.

Earlier results require careful boundaries: athlete averaging improved a model that uses NFL context; one summary correction improved 2025 by 10.1% but lost earlier, while the parallel duration model improved its own 2025 baseline by 7.7% but lost earlier. Those gains cannot be added or compared as if their baselines were identical. The entire 2025 class has already been inspected, so this merged study is exploratory.
''')
    names=['analysis.py','repo_predict.py','mechanism.py','observability.py','turn_transfer.py','front_transfer.py','phase_population.py','canonical_transfer.py','canonical_diagnostics.py','render_canonical.py','vendor/perfectpower_movement/python/perfectpower/__init__.py','vendor/perfectpower_movement/python/perfectpower/movement_language.py','vendor/perfectpower_movement/python/perfectpower/movement_features.py','vendor/perfectpower_movement/scripts/run_movement_transfer.py'];modules={name:(ROOT/name).read_text() for name in names};hashes={r['file']:r['sha256'] for r in json.loads((ROOT/'receipts/actual/acquisition.json').read_text())['files']}
    code('''import os,sys,json,hashlib,tempfile,contextlib
from pathlib import Path
from IPython.display import display,Image
DATA=Path(os.environ.get('BDB_DATA_ROOT','/kaggle/input/nfl-big-data-bowl-2027')).resolve()
if not (DATA/'players.csv').exists():
    choices=list(Path('/kaggle/input').rglob('players.csv')) if Path('/kaggle/input').exists() else []
    if len(choices)!=1:raise FileNotFoundError('Attach official files or set BDB_DATA_ROOT')
    DATA=choices[0].parent
WORK=Path(os.environ.get('BDB_WORK_ROOT',tempfile.mkdtemp(prefix='bdb_canonical_'))).resolve();WORK.mkdir(exist_ok=True)
os.chdir(WORK);sys.path.insert(0,str(WORK))
MODULES='''+repr(modules)+'''
for name,text in MODULES.items():
    path=WORK/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
HASHES='''+repr(hashes)+'''
for name,expected in HASHES.items():
    digest=hashlib.sha256()
    with (DATA/name).open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''):digest.update(chunk)
    assert digest.hexdigest()==expected,'Official input mismatch: '+name
import front_transfer as F,phase_population as P,canonical_transfer as C,canonical_diagnostics as D,render_canonical as G
OUT=WORK/'receipts/canonical';OUT.mkdir(parents=True,exist_ok=True)
print('Verified nine official source files and loaded both source engines.')
''')
    md('''## Two ways of keeping phase ambiguity

The first engine averages four operational onsets and three phase-cost temperatures. It supplies speed/acceleration, turning geometry, signed areas and sensitivity spreads. The second engine partitions an up-to-61-frame observation into four positive-duration intervals with duration constraints. A finite DAG counts allowed segmentations exactly, ranks and samples them, and sums log-weighted paths. It supplies phase-boundary distributions, stable additive variances, deterministic all-path support bounds, and selected second- and third-order tensor-signature coordinates.

For a DAG edge with log weight ell and additive reward r, suffix mass sums exp(ell) times child mass; integer suffix counts sum child counts. Weighted means and variances follow the law of total variance. These identities make a large finite population tractable. Integer counts/ranks are exact; floating posterior summaries depend on assumed emission and duration models. Rational reference tests establish small-graph identities, not a verified likelihood for athlete physiology. Deterministic support bounds are not statistical confidence intervals.

Every source measurement is computed before joining outcome labels. Equal onset weights and phase templates remain operational sensitivity assumptions. No semantic plant labels calibrate them. Exact inference does not make the physical hypothesis correct, and arithmetic or Pauli identities provide no NFL prediction theorem.
''')
    code('''with (WORK/'private_canonical_extraction.log').open('w') as log,contextlib.redirect_stdout(log):
    if not (WORK/'private_front/private_rows.pkl').exists():F.prepare(DATA,'private_front')
    if not (WORK/'private_phase_population/private_rows.pkl').exists():P.prepare(DATA)
    if not (WORK/'private_canonical_vendor/players.pkl').exists():C.V.extract(DATA,WORK/'private_front/private_rows.pkl',WORK/'private_canonical_vendor')
unit,families=C.prepare()
audit=json.loads((WORK/'private_canonical_vendor/extraction.json').read_text())
print('Players:',len(unit),'skill attempts:',audit['accepted_attempts'],'duration-onset scenarios:',audit['scenarios'])
print('Allowed segmentations per scenario:',audit['phase_populations_min'],'to',audit['phase_populations_max'])
''')
    md('''## One common scouting comparison

The response is each athlete's observed pressure-indicator frequency in the same charted rookie-rush cohort. It remains conditional on actual NFL participation and observation. Predictors are fifteen supplied body/timed/NGS traits, the recorded **Combine position**, and five common source-availability indicators. This common test excludes NFL snap geometry, teams and game situations from all predictors. Cohort membership still uses the observed defensive-front role and eligible rookie workload, so it does not solve outcome selection for undrafted or unobserved prospects.

Compare onset summaries, duration kinematics, order signatures, phase uncertainty, their duration combination, and the merged feature set. Every family can choose a baseline-only fit. Training-only imputation, scaling, physical-conditioned residualization, PCA and ridge are refitted inside each split. There are 39 unique configurations: three conventional ridge penalties and six rank-two/rank-four choices per source family. A broader selected model chooses among all 39 inside training data; this extra search must earn its value in outer tests.

Four whole-athlete outer folds, class-stratified, contain three inner folds. Repeat the earlier-class partition twice more; these reuse the same 45 athletes and are not independent studies. Forward choices use 2023 training/2024 validation, refit on both, and then score the already-inspected 2025 cohort of 29 players. All configurations and feature families were declared before this common comparison's scores. A baseline option permits rejection of features but does not guarantee unseen improvement.
''')
    code('''with (WORK/'private_canonical_models.log').open('w') as log,contextlib.redirect_stdout(log):result=C.run()
for split in ['development','exploratory_2025']:
    print(split,'baseline MSE:',result[split]['baseline_mse'])
    for family,value in result[split]['comparisons'].items():
        print(family,'MSE:',value['candidate_mse'],'relative reduction:',round(value['relative_gain']*100,2),'%')
print('Forward globally selected specification:',next(x['selected'] for x in result['forward_selection'] if x['family']=='selected'))
''')
    md('''## Measure stability before declaring an advantage

The duration-combined family is the current exploratory lead because its point gain is positive in all three earlier partitions. It is not selected for having the lowest 2025 error. Average paired athlete errors over those partitions and resample athletes conditional on predictions. Then perform 512 class-stratified training-player bootstraps, refitting every transform and both conventional and duration-combined regressions with the earlier-selected configurations held fixed. Also resample test athletes to expose joint uncertainty.

These refits omit full model-selection and adaptive-program uncertainty. Positive conditional intervals from previous pushes cannot be treated as confirmation of this estimator. The forward class was reused repeatedly, and scouting benefit needs independent prospects or prospectively reserved outcomes.
''')
    code('''with (WORK/'private_canonical_diagnostics.log').open('w') as log,contextlib.redirect_stdout(log):
    repeated=D.repeated();refits=D.refits()
lead=repeated['families']['duration_combined']
print('Three earlier-partition reductions:',[round(v*100,2) for v in lead['split_relative_gains']])
print('Mean earlier reduction:',round(lead['relative_gain']*100,2),'%; conditional interval:',lead['fixed_prediction_ci95'])
print('512 training-player refits; joint training/test interval:',refits['joint_training_test_ci95'])
G.render(OUT)
for name in ['boundary_ambiguity.png','common_comparison.png','stability_and_refits.png']:display(Image(filename=str(OUT/name)))
''')
    md('''## Canonical interpretation

Duration-combined profiles offer a small, consistently positive development point signal and a positive exploratory forward point signal. The confidence intervals, particularly training refits, include meaningful losses. Order-only and uncertainty-only features do not establish a transferable advantage. Combining every coordinate is not automatically better. The globally selected model's forward deterioration demonstrates that tuning is still unstable in this small cohort.

We retain the stronger earlier conditional-NFL benchmark as a separate player-calibration result, and retain the 10.1% and 7.7% cohort-specific results with their failed development comparisons. The supported mathematical contribution is an exact finite observation framework with explicit assumptions. The scouting claim remains a testable hypothesis: phase-conditioned motion may carry incremental information beyond conventional traits. No hidden-talent ranking, causal coaching intervention, reliable betting edge or contest victory is established by these data.
''')
    nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}},'nbformat':4,'nbformat_minor':5};(ROOT/'notebooks/Canonical_Movement_Findings.ipynb').write_text(json.dumps(nb,indent=1))
if __name__=='__main__':build()
