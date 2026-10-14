"""Self-contained real-data onset/travel experiment, with retained controls."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
def build():
    cells=[]
    def md(s):cells.append({'cell_type':'markdown','metadata':{},'source':s.splitlines(True)})
    def code(s):cells.append({'cell_type':'code','metadata':{},'source':s.splitlines(True),'outputs':[],'execution_count':None})
    names=['analysis.py','repo_predict.py','mechanism.py','observability.py','turn_transfer.py','front_transfer.py','phase_population.py','canonical_transfer.py','stress_features.py','stress_transfer.py','burst_motion.py','burst_transfer.py','burst_support.py','burst_controls.py','burst_diagnostics.py','render_burst.py']
    names+=['vendor/dynacomp_stress/src/dynacomp/'+s for s in ['__init__.py','bounds.py','rational.py','finite.py']]
    names+=['vendor/perfectpower_movement/python/perfectpower/'+s for s in ['__init__.py','movement_language.py','movement_features.py']]+['vendor/perfectpower_movement/scripts/run_movement_transfer.py']
    names+=['vendor/perfectjet_scouting/src/perfectjet/'+s for s in ['__init__.py','exact.py','readout.py']]
    modules={s:(ROOT/s).read_text() for s in names};hashes={x['file']:x['sha256'] for x in json.loads((ROOT/'receipts/actual/acquisition.json').read_text())['files']}
    md('''# The movement cue and the physical burst are different scouting questions

We ask whether observed Combine burst travel and acceleration predict a repeatable NFL mechanical response beyond conventional measurements. The previous pooled scouting audit did not establish a stable advantage. PerfectJet's accessible v0.10 branch adds exact scalar-readout methods and a synthetic scouting pipeline; synthetic success is not football evidence. We adapt the onset/travel idea independently and retain the donor source with revision provenance.

The cohort remains 74 defensive-front rookies across 2023–2025. All 2025 results are exploratory because the class has already informed the research program. No untouched scouting advantage, causal talent effect or contest victory is claimed.
''')
    code('''import os,sys,json,hashlib,tempfile,contextlib
from pathlib import Path
from IPython.display import display,Image
DATA=Path(os.environ.get('BDB_DATA_ROOT','/kaggle/input/nfl-big-data-bowl-2027')).resolve()
if not (DATA/'players.csv').exists():
    options=list(Path('/kaggle/input').rglob('players.csv')) if Path('/kaggle/input').exists() else []
    if len(options)!=1:raise FileNotFoundError('Attach official data or set BDB_DATA_ROOT')
    DATA=options[0].parent
WORK=Path(os.environ.get('BDB_WORK_ROOT',tempfile.mkdtemp(prefix='bdb_burst_'))).resolve();WORK.mkdir(exist_ok=True)
os.chdir(WORK);sys.path.insert(0,str(WORK))
MODULES='''+repr(modules)+'''
for name,text in MODULES.items():
    path=WORK/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
HASHES='''+repr(hashes)+'''
for name,expected in HASHES.items():
    h=hashlib.sha256()
    with (DATA/name).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    assert h.hexdigest()==expected,'Official source mismatch:'+name
OUT=WORK/'receipts/burst';OUT.mkdir(parents=True,exist_ok=True)
import front_transfer as F,stress_features as S,burst_motion as M,burst_transfer as B,burst_support as H,burst_controls as C,burst_diagnostics as D,render_burst as V
print('Nine official hashes verified;',len(MODULES),'source modules embedded.')
''')
    md('''## Define observable phases without guessing get-off semantics

The operational onset is the first of three contiguous frames at or above the speed gate after the snap. Reject already-active-at-snap records, incomplete traces, gaps and failure to travel one yard. The primary gate is 1 yard/second; 0.5 and 2 are sensitivity definitions. Travel begins at onset and reaches one yard of smoothed geometric arc length, interpolating the crossing. It is neither backfield-directed progress nor verified time to contact. Faster travel is a mechanical trait, not automatically better football play. The supplied get-off field is not assumed reaction time or a line-crossing annotation.

Combine attempts use nine source-only speed/smoothing scenarios, accepting at least five. Retain median travel time, speeds at 0.5/1 second and early acceleration, with sensitivity width. Shared drill attempt counts enter every baseline. The response population remains conditional on the earlier charted-get-off rookie eligibility cohort.

PerfectJet's unchanged exact readout module tests row-span membership of a declared bilinear response. Round raw demands first and multiply in exact arithmetic; independently rationalizing floating products could destroy structural dependencies. The player's empirical demand mean is supported by construction. A shared reference-demand mean may be unsupported. Planning examples assume an explicit isotropic prior and noise variance, not calibrated biology or a proved coaching intervention.
''')
    code('''with (WORK/'private_burst_source.log').open('w') as log,contextlib.redirect_stdout(log):
    if not (WORK/'private_front/private_rows.pkl').exists():F.prepare(DATA,'private_front')
    if not (WORK/'private_burst/private_game_bursts.pkl').exists():M.prepare(DATA)
    if not (WORK/'private_burst_turns/private_turns.pkl').exists():S.prepare(DATA,out='private_burst_turns',clock=True)
    support=H.run()
population=json.loads((OUT/'population.json').read_text())
print('Combine attempts:',population['source_attempts'],'primary game population:',population['population']['1.0'])
print('Scalar readouts identified:',support['own_empirical_mean_identified'],'own;',support['earlier_reference_identified'],'shared reference out of',support['panels'])
''')
    md('''## Compare inside whole-player training folds

Primary: mean context-adjusted post-onset one-yard travel. A fixed NFL context reference defines the target and is rebuilt within every inner/outer split. Training targets use player crossfits; evaluated targets use training players only. No NFL movement or context enters scouting predictors. Context cache identity hashes training records, context and labels, plus evaluated inputs excluding evaluated labels. Changing a training dataset cannot reuse an old fitted reference.

Compare conventional traits, raw observed burst profiles and repeat-precision profiles. The latter shrink source deviations toward a trait-predicted source mean using training-only repeat variance and between-player residual variance. These are empirical shrinkage conventions, not calibrated posteriors. Imputation, scales, source moments, physical residualization, PCA and Ridge choices are training-only; every family can choose conventional fallback. Four outer/three inner whole-player folds repeat across three earlier partitions. Forward choices use 2023→2024.

Supporting analyses retain onset and both alternative gates. After the initial onset scores, add explicit controls: trait-predicted source reference without individual observed movement, and reliability-scaled individual deviation alone. This adaptive control checks whether a favorable precision result is a changed trait basis rather than new motion information. It cannot become untouched confirmation. A posthoc top-quarter diagnostic reports all families and folds without replacing the primary error metric.
''')
    code('''with (WORK/'private_burst_models.log').open('w') as log,contextlib.redirect_stdout(log):
    for seed in [B.SEED,B.SEED+200,B.SEED+400]:B.run(seed=seed,forward=seed==B.SEED)
    B.run(target='burst_onset')
    for gate in [.5,2.]:B.run(threshold=gate)
    controls=C.run();repeat=D.run()
for seed in [B.SEED,B.SEED+200,B.SEED+400]:
    r=json.loads((OUT/f'burst_travel1_1.0_{seed}.json').read_text())
    print('Primary earlier partition',seed,{k:round(v['relative_gain']*100,3) for k,v in r['development']['comparisons'].items()})
print('Game-half repeatability:',repeat['game_half_rank_quantiles'])
print('Adaptive onset controls, forward:',{k:round(v['relative_gain']*100,3) for k,v in controls['exploratory_2025']['comparisons'].items()})
''')
    md('''## What is newly established

Post-onset travel is more repeatable across recorded game halves than onset or charted get-off. That supplies a clearer mechanical response for future work. It does not demonstrate incremental scouting accuracy. The primary burst models fail consistent earlier/forward improvement. A favorable supporting onset result is unstable and cannot establish hidden-talent detection.

Supported scalar measurements avoid claiming an unobserved individual stress curve, but mathematical observability alone cannot create predictive signal. Reserve independent outcomes and validate football relevance before a scout-facing rating. Faster arc travel may reflect lateral motion or a tactical assignment; a future directed-progress response needs its own stated validation. Restricted inputs and player outputs remain private. All aggregate trials and four figures are retained; nothing is submitted to Kaggle or integrated into betting.
''')
    code('''V.render()
for name in ['onset_and_travel.png','source_and_game.png','prediction_results.png','repeatability_and_support.png']:
    display(Image(filename=str(OUT/name)))
print('Complete onset/travel study and all controls retained.')
''')
    notebook={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'nbformat':4,'nbformat_minor':5}
    (ROOT/'notebooks/Onset_and_Travel_Scouting.ipynb').write_text(json.dumps(notebook,indent=1))
if __name__=='__main__':build()
