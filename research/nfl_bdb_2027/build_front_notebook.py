"""Build a self-contained, aggregate-only defensive-front research entry."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
def build():
    cells=[]
    def md(s):cells.append(dict(cell_type='markdown',metadata={},source=s.splitlines(True)))
    def code(s):cells.append(dict(cell_type='code',metadata={},source=s.splitlines(True),outputs=[],execution_count=None))
    md('''# Burst, bend and the scouting question

**Do tracked Combine movements help identify rookie pass-rushing ability beyond the measurements scouts already have?** We examine defensive ends, tackles, nose tackles and outside linebackers. The proposed linkage combines sprint acceleration with movement through pass-rush, hoop, four-bag and lateral-reaction drills. It is a conditional prediction study, not proof that changing a drill technique causes more NFL pressures.

This is adaptive exploratory research. Other 2025 WR/DB outcomes were inspected earlier. The player pressure-rate metric was added after inspecting this program's play-level results. We retain the original results, add a baseline selected specifically for the player metric, test repeated development splits, swap complete profiles within position, and refit training-player bootstraps. No result is presented as a fresh confirmatory test or a guaranteed draft advantage.
''')
    files=['analysis.py','repo_predict.py','mechanism.py','observability.py','turn_transfer.py','front_transfer.py','front_diagnostics.py','render_front.py','front_bouts.py','front_player_bagging.py'];modules={name:(ROOT/name).read_text() for name in files};hashes={r['file']:r['sha256'] for r in json.loads((ROOT/'receipts/actual/acquisition.json').read_text())['files']}
    code('''import os,sys,json,hashlib,tempfile,contextlib
from pathlib import Path
import numpy as np,pandas as pd
from IPython.display import display,Image
DATA=Path(os.environ.get('BDB_DATA_ROOT','/kaggle/input/nfl-big-data-bowl-2027')).resolve()
if not (DATA/'players.csv').exists():
    choices=list(Path('/kaggle/input').rglob('players.csv')) if Path('/kaggle/input').exists() else []
    if len(choices)!=1:raise FileNotFoundError('Attach official competition files or set BDB_DATA_ROOT.')
    DATA=choices[0].parent
WORK=Path(os.environ['BDB_WORK_ROOT']) if 'BDB_WORK_ROOT' in os.environ else Path(tempfile.mkdtemp(prefix='bdb_front_private_'));WORK.mkdir(exist_ok=True,parents=True);SRC=WORK/'sources';SRC.mkdir(exist_ok=True)
MODULES='''+repr(modules)+'''
for name,text in MODULES.items():(SRC/name).write_text(text)
sys.path.insert(0,str(SRC))
EXPECTED='''+repr(hashes)+'''
for name,expected in EXPECTED.items():
    h=hashlib.sha256()
    with (DATA/name).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    if h.hexdigest()!=expected:raise ValueError('Official snapshot changed: '+name)
os.chdir(WORK)
import front_transfer as F,front_diagnostics as D,render_front as V
print('Verified all nine official inputs. Private individual outputs stay outside public notebook output directories.')
''')
    md('''## Measure movements and preserve football role

Use rookie regular-season, non-nullified records with finite charted get-off, a Combine profile, a unique ball-snap frame and at least 30 records per player. Outcomes are charted get-off seconds and the indicator that a time-to-pressure event was observed. Missing pressure timestamps define this recorded indicator; they are not modeled as censored pressure times. Results apply to this get-off-charted population.

For each skill drill define sustained movement onset as three consecutive speeds above 0.5 yd/s. Examine up to five seconds after onset. Derive early speeds and acceleration, high speed, braking, angular work, bending energy, straightness, jerk, speed–acceleration area, and times to accumulate one, three and five yards of path length. These are geometric path times, not guaranteed forward travel or reaction times to an official cue. Sprint curves add two nonlinear acceleration-response fits, timed speeds/accelerations and Legendre shape coefficients. Median repeated attempts within each player/drill.

The strong common baseline includes conventional timed/body/NGS measures, position and lined-up role, snap depth relative to the line of scrimmage, width, speed, situation, blitz indicator and teams. Starting alignment matters: closer is not automatically more explosive. Every family also receives the five source-drill availability flags. No pressure outcome or post-snap movement enters the predictor.

Standardize source profiles using training players only, remove their ridge-predictable physical component, and compress innovations into four or six principal components. Add squared components and body-mass interactions. Compare conventional, sprint, skill and combined families using identical five-candidate ridge/forest budgets. This tests physical-conditioned nonlinear source information; PCA modes are not established physiological mechanisms.
''')
    code('''if not (WORK/'private_front/private_rows.pkl').exists():
    with (WORK/'extraction.log').open('w') as log,contextlib.redirect_stdout(log):F.prepare(DATA,'private_front')
population=json.loads((WORK/'private_front/population.json').read_text())
print('Players by class:',population['players_by_year'],'records:',population['rush_records_by_year'])
print('Tracked sprint/skill attempts:',population['sprint_attempts'],population['skill_attempts'])
''')
    md('''## Player holdout, season transport and the right error

Give every player equal total weight. Four class-stratified outer player folds and three inner player folds tune models; all snaps of a player stay together. A separate 2023 train/2024 validation split chooses configurations before earlier-class refitting and exploratory 2025 transport. Scaling, imputation, physical residualization and PCA are all fitted on training players.

For a scout, systematic error about an athlete differs from error about one rush. Let e be observed pressure indicator minus predicted probability. Within player, mean(e²) = mean(e)² + variance(e). Player pressure-rate MSE averages mean(e)² over athletes, using each actual NFL workload. A source profile may improve persistent athlete calibration while barely changing noisy individual rush predictions. This is not a claim that pressure production rises by the relative MSE reduction.

Because that secondary metric was added after inspection, test it fairly: retain the original play-selected banks, then independently select the same candidate budgets on player-mean error using earlier-player folds and 2024. Repeat original development splits twice without further 2025 tuning. Thirty fixed-model held-out profile swaps within position check identity sensitivity; they are diagnostic, not exchangeability-certified significance tests. Bootstrap players and teams conditional on predictions, then run 80 class-stratified training-player refits. The latter refits all transformations but retains selected configurations, so model-selection and adaptive-search uncertainty remain outside its intervals.
''')
    code('''d=pd.read_pickle(WORK/'private_front/private_rows.pkl');cols=json.loads((WORK/'private_front/population.json').read_text())['source_features'];front={}
with (WORK/'models.log').open('w') as log,contextlib.redirect_stdout(log):
    for target in ['player_get_off','pressure_event']:
        file=WORK/'private_front_strong'/target/'results.json'
        front[target]=json.loads(file.read_text()) if file.exists() else F.experiment(d,cols,'private_front_strong',target)
print('Completed conventional and three movement families for both recorded outcomes.')
''')
    code('''repeat_files=[WORK/'private_front_strong'/('repeat_'+str(seed))/'pressure_event/results.json' for seed in [F.SEED+200,F.SEED+400]]
with (WORK/'diagnostics.log').open('w') as log,contextlib.redirect_stdout(log):diagnostics=D.run('private_front_strong',repeats=not all(file.exists() for file in repeat_files))
print('Completed repeated development partitions, 30 source-profile controls and team/player diagnostics.')
''')
    code('''with (WORK/'refits.log').open('w') as log,contextlib.redirect_stdout(log):refits=D.refit_bootstrap('private_front_strong',80)
print('Completed training-player refits:',refits['replicates'])
''')
    code('''d=pd.read_pickle(WORK/'private_front/private_rows.pkl');cols=json.loads((WORK/'private_front/population.json').read_text())['source_features']
with (WORK/'macro.log').open('w') as log,contextlib.redirect_stdout(log):macro=F.experiment(d,cols,'private_front_macro','pressure_event',objective='player')
diagnostics=json.loads((WORK/'private_front_strong/scouting_diagnostics.json').read_text());refits=json.loads((WORK/'private_front_strong/refit_bootstrap.json').read_text());front={target:json.loads((WORK/'private_front_strong'/target/'results.json').read_text()) for target in ['player_get_off','pressure_event']}
for split in ['nested','exploratory_2025']:
    v=diagnostics['scouting_rates'][split];print(split,'player pressure-rate MSE',v['mse'],'combined delta/CI',v['comparisons']['combined']['delta_mse'],v['comparisons']['combined']['ci95'])
    q=pd.read_pickle(Path('private_front_macro/pressure_event')/('private_'+split+'.pkl'));v=D.player_rates(q);print('Player-metric-selected',split,v['mse'],'combined delta/CI',v['comparisons']['combined']['delta_mse'],v['comparisons']['combined']['ci95'])
print('Three earlier partitions: combined mean delta/CI',diagnostics['development_repeated_partitions']['mean_player_rate_delta'],diagnostics['development_repeated_partitions']['conditional_ci95'])
print('Profile swaps better than real:',diagnostics['profile_controls']['shuffles_better_than_real'],'of 30')
print('Training-refit / joint training-and-forward-player intervals:',refits['fixed_forward_ci95'],refits['joint_ci95'])
print('Get-off MSE:',{split:front['player_get_off'][split]['mse'] for split in ['nested','exploratory_2025']})
''')
    code('''FIG=WORK/'aggregate_figures'
front={target:json.loads((WORK/'private_front_strong'/target/'results.json').read_text()) for target in ['player_get_off','pressure_event']};diagnostics=json.loads((WORK/'private_front_strong/scouting_diagnostics.json').read_text())
paths=V.render(DATA,FIG,front,diagnostics)
for path in paths:display(Image(filename=path))
''')
    md('''## Adapt measurement and average whole athletes

The source-only onset audit found that a 0.5 yd/s threshold can include preparatory movement. Test three consecutive samples above 2 yd/s, preserving the NFL cohort and shared availability controls. This is a second operational definition, not a verified official cue. Its forward comparison is retained even when unfavorable.

Training refits revealed instability, motivating whole-athlete averaging. Average sixteen class-stratified prospect-bootstrap models for each conventional and combined family, retaining earlier-selected configurations and original outer-player boundaries. Distinct replica IDs preserve multiplicity. Both families receive the same averaging budget. Keep improvements from the algorithm separate from the incremental value of tracking; all these adaptations follow prior inspection and remain exploratory.
''')
    code('''import front_bouts as E,front_player_bagging as B
with (WORK/'adaptations.log').open('w') as log,contextlib.redirect_stdout(log):
    if not (WORK/'private_front_bouts/pressure_event/results.json').exists():
        bout_d,bout_cols,bout_audit=E.prepare(DATA,'private_front_bouts');F.experiment(bout_d,bout_cols,'private_front_bouts','pressure_event',objective='player')
    bags={}
    for folder,out in [('private_front_macro','private_front_bagged'),('private_front_bouts','private_front_bouts_bagged')]:
        file=WORK/out/'results.json';bags[out]=json.loads(file.read_text()) if file.exists() else B.run(folder,out)
for name,r in bags.items():
    print(name,{split:r[split] for split in ['nested','exploratory_2025']})
import matplotlib.pyplot as plt
fig,axes=plt.subplots(1,2,figsize=(12,4.5))
for ax,split in zip(axes,['nested','exploratory_2025']):
    rows=[]
    for folder,label in [('private_front_macro','Initial onset'),('private_front_bouts','Faster onset')]:
        q=pd.read_pickle(WORK/folder/'pressure_event'/('private_'+split+'.pkl'));rows.append((label+' / single model',D.player_rates(q)['comparisons']['combined']))
        key='private_front_bagged' if folder=='private_front_macro' else 'private_front_bouts_bagged';rows.append((label+' / athlete average',bags[key][split]['combined']))
    means=np.array([v['delta_mse'] for _,v in rows])*1e4;bounds=np.array([v['ci95'] for _,v in rows])*1e4;ax.errorbar(means,np.arange(4),xerr=np.maximum(0,np.c_[means-bounds[:,0],bounds[:,1]-means].T),fmt='o',capsize=3);ax.axvline(0,color='gray',lw=1);ax.set_yticks(range(4),[name for name,_ in rows]);ax.invert_yaxis();ax.set_xlabel('Improvement over matched baseline (MSE ×10⁻⁴)');ax.set_title('Earlier player holdout' if split=='nested' else 'Exploratory 2025')
fig.suptitle('Source-onset sensitivity and whole-athlete averaging');fig.tight_layout();plt.show()
''')
    md('''## What a team could use—and what still needs confirmation

The intended scouting use is a defensive-front movement profile conditioned on body size and likely football role. It can supplement conventional evaluation when assessing sustained pressure tendency across a workload. The source plots show measured mean movement paths, not individual athlete animations or model-generated ghosts. They preserve physical yard units after initial-direction alignment and turn mirroring; colored speed is an attempt-population average.

Read the actual effect sizes and intervals above, including the baseline chosen for the player-level task and the training-refit uncertainty. Repeated split gains use the same earlier players, not independent replications. The population is only 74 participating rookies, and recorded workloads, schemes, opponents, selection into playing time and pressure-event missingness can affect the target. This does not establish reduced draft-bust risk, a causal development protocol, or unconditional pre-draft pressure production. A prospective untouched cohort and stable reference workload are necessary before treating the candidate gain as established scouting advantage.

The complete package preserves the WR angular-break and speed-ceiling follow-ups, initial defensive prototype, stronger-baseline trials and all aggregate candidate ledgers. It excludes restricted raw files, credentials and individual predictions. No learned model has been integrated into the betting application, and no competition publication or submission has occurred.
''')
    nb=dict(nbformat=4,nbformat_minor=5,metadata={'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'},'language_info':{'name':'python','version':'3.12'}},cells=cells);(ROOT/'notebooks/Defensive_Front_Movement_Lab.ipynb').write_text(json.dumps(nb,indent=1))
if __name__=='__main__':build()
