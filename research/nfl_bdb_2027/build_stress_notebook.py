"""Build raw-data movement stress, observability and scouting notebook."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent

def build():
    cells=[]
    def md(s):cells.append({'cell_type':'markdown','metadata':{},'source':s.splitlines(True)})
    def code(s):cells.append({'cell_type':'code','metadata':{},'source':s.splitlines(True),'outputs':[],'execution_count':None})
    md('''# How much movement capacity survives a turn?

Our defensive-front scouting question is whether repeatable recovery after direction change predicts rookie pressure performance beyond conventional traits and tracked sprint capacity. We distinguish better measurement, individual stress-curve identification and NFL prediction. These are separate achievements. The same 74-player cohort and the already-inspected 2025 class make this an adaptive exploratory program.

We draw on broader machinery concretely: DynaComp's unchanged rational bounds transport declared measurement boxes, its finite compiler preserves specified quantized readouts, and its rational algebra detects unobserved response directions. WIND-style target ambiguity motivates sensitivity/rank audits. PerfectPower-style finite planning evaluates complete small populations of additional demand trials. These calculations do not certify physiology or unseen NFL performance.
''')
    names=['analysis.py','repo_predict.py','mechanism.py','observability.py','turn_transfer.py','front_transfer.py','stress_features.py','stress_transfer.py','capacity_stress.py','stress_diagnostics.py','stress_summary.py','stress_refits.py','stress_contexts.py','stress_fixed_policy.py','render_stress.py','vendor/dynacomp_stress/src/dynacomp/__init__.py','vendor/dynacomp_stress/src/dynacomp/bounds.py','vendor/dynacomp_stress/src/dynacomp/rational.py','vendor/dynacomp_stress/src/dynacomp/finite.py'];modules={name:(ROOT/name).read_text() for name in names};hashes={r['file']:r['sha256'] for r in json.loads((ROOT/'receipts/actual/acquisition.json').read_text())['files']}
    code('''import os,sys,json,hashlib,tempfile,contextlib
from pathlib import Path
from IPython.display import display,Image
DATA=Path(os.environ.get('BDB_DATA_ROOT','/kaggle/input/nfl-big-data-bowl-2027')).resolve()
if not (DATA/'players.csv').exists():
    options=list(Path('/kaggle/input').rglob('players.csv')) if Path('/kaggle/input').exists() else []
    if len(options)!=1:raise FileNotFoundError('Attach official input or set BDB_DATA_ROOT')
    DATA=options[0].parent
WORK=Path(os.environ.get('BDB_WORK_ROOT',tempfile.mkdtemp(prefix='bdb_stress_'))).resolve();WORK.mkdir(exist_ok=True)
os.chdir(WORK);sys.path.insert(0,str(WORK))
MODULES='''+repr(modules)+'''
for name,text in MODULES.items():
    path=WORK/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
HASHES='''+repr(hashes)+'''
for name,expected in HASHES.items():
    h=hashlib.sha256()
    with (DATA/name).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    assert h.hexdigest()==expected,'Official data mismatch:'+name
import front_transfer as F,stress_features as S,stress_transfer as T,capacity_stress as C,stress_diagnostics as D,stress_summary as U,stress_refits as B,stress_contexts as H,stress_fixed_policy as J,render_stress as G
OUT=WORK/'receipts/stress';OUT.mkdir(parents=True,exist_ok=True)
print('Nine official source files verified; broader source modules embedded.')
''')
    md('''## Measure the whole direction change

Detect separated peaks in the angle between reliable incoming/outgoing geometric velocity, with entry speed at least 2 yards/s and turn angle 30–170°. Evaluate cubic smoothing over 5, 7 and 9 frames and centre shifts of −0.2 to +0.2 seconds. Accept at least five valid branches per turn. Our initial response integrates projected geometric velocity for 0.5 seconds, beginning centre+0.4 seconds, and divides by entry speed×0.5 seconds.

The adaptive angular-progress clock measures entry before 20% of estimated rotation and begins recovery at 80%. Heading at low geometric speed is interpolated, and progress is monotone. This is an operational geometric definition, not an annotated plant. Shared-turn comparison separates alignment improvement from changing the eligible turn population. Missing tracking and sparse repeat attempts remain explicit.

The sprint baseline uses three tracked descriptors: a p95 speed ceiling and speeds at one/three seconds after sustained motion onset. These are measured source capacities, not physiological maxima. Every corrected model receives the same capacity-availability flag and valid-turn counts; an earlier missingness-uncontrolled pilot is retained separately.
''')
    code('''with (WORK/'private_stress_extraction.log').open('w') as log,contextlib.redirect_stdout(log):
    if not (WORK/'private_front/private_rows.pkl').exists():F.prepare(DATA,'private_front')
    if not (WORK/'private_stress/private_turns.pkl').exists():S.prepare(DATA)
    if not (WORK/'private_stress_clock/private_turns.pkl').exists():S.prepare(DATA,out='private_stress_clock',clock=True)
    if not (WORK/'private_stress_clock/private_capacity.pkl').exists():C.capacity(DATA)
initial=json.loads((WORK/'private_stress/population.json').read_text());clock=json.loads((WORK/'private_stress_clock/population.json').read_text())
print('Initial/clock turns:',initial['turns'],clock['turns'],'players:',clock['turn_players'],'NFL records:',clock['NFL_records'])
print('Tracked sprint source:',json.loads((WORK/'private_stress_clock/capacity_population.json').read_text()))
import pandas as pd
rows=pd.read_pickle(WORK/'private_front/private_rows.pkl');checks={}
for field in ['quick_pressure','sack','time_to_qb_hurry']:
    positive=rows[field].notna() if field.startswith('time_') else rows[field].astype(str).str.lower().isin(['true','y','1','1.0'])|pd.to_numeric(rows[field],errors='coerce').gt(0)
    checks[field]={'positive_records':int(positive.sum()),'positive_with_missing_pressure_timestamp':int((positive&rows.time_to_pressure.isna()).sum())}
print('Outcome annotation consistency:',checks)
''')
    md('''## Match demands and build the outcome without leakage

Within each training fold, a source-only ridge explains recovery using entry speed, angle, their interaction and squares, body/timed/NGS traits, drill identity and mass interactions. The capacity-aware version adds entry/ceiling utilization. Player/drill profiles retain matched residuals, late recovery, a shrunk demand slope, branch extrema and repeat-attempt dispersion. These are partially pooled source descriptions; they do not identify individual biological thresholds.

For the primary outcome, subtract a context-reference prediction from the recorded pressure indicator and average by player. A fixed 120-tree forest uses snap alignment, situation, role and teams, excluding Combine traits. Every outer and inner scouting split rebuilds its reference: training targets use three player crossfits within that training set; evaluated targets use a reference fitted only on its training players. Thus evaluated outcomes cannot enter training-target construction. This is conditional performance relative to a chosen reference, not causal talent or unconditional draft success. Charted get-off is a supporting outcome.

Compare conventional, raw movement, matched recovery, stress slope and ambiguity/repeat profiles. Capacity experiments add a separate sprint-only baseline, with the same capacity descriptors in recovery families. Ridge penalties 10/100/1000 are selected inside four outer/three inner player splits. Every family can choose conventional fallback. Support clipping and scaling use training players. Forward tuning uses 2023→2024 before 2025 evaluation. Changing the model does not create a fresh holdout.
''')
    code('''with (WORK/'private_stress_models.log').open('w') as log,contextlib.redirect_stdout(log):
    for target in ['pressure_event','player_get_off']:
        T.run(target)
        C.run(target,share_capacity_availability=False)
        C.run(target,out='private_stress_capacity_controlled/'+target)
    for seed in [T.SEED+200,T.SEED+400]:C.run(seed=seed,forward=False,out='private_stress_capacity_repeat_'+str(seed))
    repeated=U.summarize()
for label,folder in [('Initial','private_stress'),('Capacity pilot','private_stress_clock'),('Availability-controlled','private_stress_capacity_controlled')]:
    for target in ['pressure_event','player_get_off']:
        r=json.loads((WORK/folder/target/'results.json').read_text())
        for split in ['development','exploratory_2025']:print(label,target,split,r[split]['mse'])
print('Capacity repeated-player result:',repeated['capacity_only'])
''')
    md('''## Preserve uncertainty and expose missing experiments

DynaComp's rational linear bound covers a declared Cartesian box around the computed branch velocity vectors. Entry-speed extrema then bound normalized recovery. This covers processing scenarios, not all sensor errors. Its finite quotient preserves all future observations in a six-frame absorbing machine whose velocities are quantized at 0.05. That rounding contributes at most 0.025 to normalized recovery; it does not establish equivalence of unobserved athlete behaviour.

For an individual bilinear stress model, the design row is (1,speed,angle,speed×angle). Exact rational rank/nullspace calculations on 0.1-rounded demands ask whether a new demand's response is identified. An alternative coefficient direction invisible on observed rows can still change the new response. Regularization chooses among such curves without adding observations. We also check unrounded numerical rank. Complete enumeration of 512 candidate trial subsets finds minimum declared-cost rank-completing plans for twelve examples; candidate conditions and costs are illustrative proposed evaluation protocols, not proven training benefits.

Compare similar prospects' finite matched-recovery intervals and evaluate hypothetical range reduction from resolving centre/smoothing branches. Overlap describes sensitivity, not a probability of talent misranking. Repeated attempts can have different conditions. A source-only earlier-trained adjustment supplies repeatability diagnostics without NFL outcome fitting.
''')
    code('''with (WORK/'private_stress_diagnostics.log').open('w') as log,contextlib.redirect_stdout(log):measurement,observability=D.run()
print('Matched-turn median sensitivity-span reduction:',round(measurement['median_width_reduction']*100,2),'%')
print('Repeatability:',measurement['repeatability'])
print('Player/drill design-rank counts:',observability['rank_counts'],'unidentified fraction:',observability['fraction_not_full_rank'])
with (WORK/'private_stress_refits.log').open('w') as log,contextlib.redirect_stdout(log):refits=B.run()
print('64 joint context/scout refits; interval:',refits['joint_training_test_ci95'])
with (WORK/'private_stress_contexts.log').open('w') as log,contextlib.redirect_stdout(log):situations=H.run()
for group,result in situations['groups'].items():
    if 'mse' in result:print('Fixed-penalty supporting situation',group,'players',result['players'],'MSE',result['mse'])
with (WORK/'private_stress_fixed.log').open('w') as log,contextlib.redirect_stdout(log):
    fixed=[J.run(seed,seed==T.SEED) for seed in [T.SEED,T.SEED+200,T.SEED+400]]
for result in fixed:print('Adaptive fixed1000 policy',result['seed'],'development MSE',result['development']['mse'])
print('Adaptive fixed1000 forward MSE',fixed[0]['exploratory_2025']['mse'])
G.render(OUT)
for name in ['recovery_geometry.png','stress_surface.png','scouting_results.png','measurement_and_observability.png']:display(Image(filename=str(OUT/name)))
''')
    md('''The supporting situation audit fixes ridge at1000 and reports third-and-long (down3, at least5yards) and the supplied blitzing flag with at least10records/player. The flag defines a record subset but reuses the same45/29players; it is not an independent cohort or a causal team-blitz intervention. Its forced-feature fits motivated an explicitly adaptive fixed1000 audit across all families and three earlier partitions. No family is selected by its2025score; these diagnostics do not replace the primary nested-selection results or create independent confirmation.

## What a scout can take from this

Better recovery alignment is a measured improvement in robustness, not proof of greater NFL predictive value. Most individual demand curves remain underidentified; a precise-looking threshold would depend heavily on assumptions. Tracked sprint capacity offers a small exploratory pressure-calibration lead, while recovery additions fail to establish an incremental benefit and the supporting get-off result does not confirm it. Keep all trials, fallback choices and broader uncertainty.

The actionable evaluation direction is to diversify measured entry speeds and turn angles, validate turn-completion labels, and reserve independent athletes/outcomes. Minimum candidate trial plans quantify what the stated response model lacks. Causal player-development benefit and reliable hidden-talent identification require additional evidence.
''')
    nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}},'nbformat':4,'nbformat_minor':5};(ROOT/'notebooks/Movement_Stress_and_Recovery.ipynb').write_text(json.dumps(nb,indent=1))
if __name__=='__main__':build()
