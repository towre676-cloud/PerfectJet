"""Self-contained Combine-to-NFL turn analysis, preserving unfavorable results."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
def build():
    nb={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'},'language_info':{'name':'python','version':'3.11'}},'cells':[]}
    def md(s):nb['cells'].append({'cell_type':'markdown','metadata':{},'source':s.splitlines(keepends=True)})
    def code(s):nb['cells'].append({'cell_type':'code','metadata':{},'source':s.splitlines(keepends=True),'outputs':[],'execution_count':None})
    md('''# Where a cut ends and recovery begins

**Can Combine execution identify how a receiver handles NFL turning demands?** A timed drill cannot distinguish approach speed, braking, and reacceleration. But a repeatable movement signature is not automatically a transferable talent signal. We separate those questions using measured source curves, matched football demands, player-held-out experiments, a strong yards-after-catch reference, and explicit measurement ambiguity.

This continues an exploratory research program that previously inspected WR 2025 outcomes. The initial turn protocol was fixed before these responses were extracted. A development-only timeline audit motivated extending follow-up after pass release; the original negative analysis remains below. Subsequent YAC-reference corrections are exploratory after initial YAC inspection. No rerun is described as a fresh blind test, and no synthetic curve is presented as a discovered athlete characteristic.
''')
    files=['analysis.py','repo_predict.py','mechanism.py','observability.py','turn_transfer.py','post_release_transfer.py','yac_reference_correction.py','turn_diagnostics.py','turn_observability_design.py','render_turn_transfer.py','vendor/__init__.py','vendor/pp/__init__.py','vendor/pp/exact_linear.py','vendor/pp/LICENSE'];modules={n:(ROOT/n).read_text() for n in files};hashes={r['file']:r['sha256'] for r in json.loads((ROOT/'receipts/actual/acquisition.json').read_text())['files']}
    code('''import os,sys,json,hashlib,tempfile,contextlib
from pathlib import Path
import numpy as np,pandas as pd
from IPython.display import display,Image
DATA=Path(os.environ.get('BDB_DATA_ROOT','/kaggle/input/nfl-big-data-bowl-2027'))
if not (DATA/'players.csv').exists():
    candidates=list(Path('/kaggle/input').rglob('players.csv')) if Path('/kaggle/input').exists() else []
    if len(candidates)!=1:raise FileNotFoundError('Attach the official competition input or set BDB_DATA_ROOT.')
    DATA=candidates[0].parent
OUT=Path(tempfile.mkdtemp(prefix='bdb_turn_private_'));SRC=OUT/'sources';SRC.mkdir()
MODULES='''+repr(modules)+'''
for name,text in MODULES.items():
    file=SRC/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(text)
sys.path.insert(0,str(SRC))
import turn_transfer as T,post_release_transfer as P,yac_reference_correction as Y
import turn_diagnostics as D,turn_observability_design as E,render_turn_transfer as V
EXPECTED='''+repr(hashes)+'''
for name,expected in EXPECTED.items():
    h=hashlib.sha256()
    with (DATA/name).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    if h.hexdigest()!=expected:raise ValueError('Official snapshot differs: '+name)
ORIGINAL=OUT/'pre_release';EXTENDED=OUT/'full_followup'
print('All nine official hashes verified; player-level intermediates stay outside public output directories.')
''')
    md('''## A demand-adjusted measurement

Use the first qualifying heading-change peak, rather than the largest turn anywhere in a route. The fixed rule requires a 25–150° turn, approach speed at least 2.5 yd/s, continuous 10 Hz samples, and sufficient flanking motion. NFL anchors occur 0.5–3 seconds after snap on non-nullified rookie regular-season IN, OUT, SLANT, and HITCH routes. Fixed corresponding Combine drills include Dagger, Speed Out, Slant, Curl and Comeback, with one documented name alias. Require ten fully observed turn windows per player.

The primary response is half-second normalized speed deficit: integrate max(0,1−speed/approach-speed) from the turn through 0.5 seconds. Entry speed, turn angle, and redirection impulse describe the demand. Source responses also measure minimum retention, exit-speed ratio, and normalized curve area. Lower deficit is not a universal ability score: an intentional stop route can require strong braking.

Train-only source regressions remove expected effects of entry speed and angle from four execution descriptors. Player/route medians are then residualized against conventional physical attributes, with fixed quadratic, demand and mass interactions. Compare conventional context, added source-demand information, and added execution. The primary execution contrast controls source speed, angle, impulse, attempt availability, all conventional measurements and shared NFL context. These NFL demands are measured outcome-side covariates, not live pre-snap information.
''')
    code('''with (OUT/'original.log').open('w') as log,contextlib.redirect_stdout(log):
    initial_burden,initial_separation=T.run(DATA,ORIGINAL)
initial_population=json.loads((ORIGINAL/'population.json').read_text())
print('Original pre-release response completeness:',initial_population['all_qualifying_game_turns']-initial_population['incomplete_half_second_turns'],'/',initial_population['all_qualifying_game_turns'])
print('Original 2025 execution difference:',initial_burden['exploratory_2025']['execution_increment'])
''')
    md('''## Correct the clock before claiming transfer

A development-only audit found tracking continues beyond release. Truncating there removed 1,234 of 2,630 qualifying half-second responses. Keep exactly the same pre-release turn anchors and extend only observation of the response using the supplied trace. This restores every anchored half-second window, before the unchanged per-player threshold. It does not recover turns whose centers occur after release, and does not remove the original anchor-selection limitation.

Observe 90% speed recovery through 1.5 seconds, retaining genuine right censoring. Distribution-free bounds treat a receiver whose trace ends early as unresolved, avoiding an independent-censoring assumption. Post-release motion can include catching or route termination. Separation at release is tested as a separate source-feature association; later recovery cannot cause that earlier measurement.

Every prospect receives equal total fitting and evaluation weight. Four class-stratified outer player folds and three inner player folds tune identical five-candidate ridge/forest/extra-tree budgets. All routes of a player remain together; source calibration, scaling and physical residualization use training players only. Separate 2023 training/2024 tuning precedes exploratory 2025 transport. Pooled earlier-player folds establish unseen-player testing, not a wholly new-season guarantee.
''')
    code('''with (OUT/'extended.log').open('w') as log,contextlib.redirect_stdout(log):
    burden,separation,yac=P.run(DATA,ORIGINAL,EXTENDED)
population=json.loads((EXTENDED/'population.json').read_text())
print('Full-follow-up population:',population['players_by_year'],population['turns_by_year'])
print('Turn deficit:',burden['nested']['execution_increment'],burden['exploratory_2025']['execution_increment'])
print('Separation:',separation['nested']['execution_increment'],separation['exploratory_2025']['execution_increment'])
print('Raw YAC:',yac['nested']['execution_increment'],yac['exploratory_2025']['execution_increment'])
''')
    md('''## A favorable score must beat a meaningful reference

YAC analysis requires three targeted catches per player and at least ten players in each class. Shared context includes supplied expected YAC and pass length. The raw execution model improves 2025 MSE by about 16.4% against our fitted demand comparator, but earlier-player validation is unfavorable. That comparison alone cannot establish a scouting gain.

Test corrections to the supplied expected-YAC reference on catches where both observed and expected YAC exist. Give every family the same additional zero-correction option, so fitting a model is not compulsory. This stronger comparison yields about 1.6% exploratory improvement, with an interval spanning zero. Earlier nested execution selection retains the reference unchanged. Only eleven 2025 receivers support the YAC result; a favorable point estimate is not a demonstrated transferable advantage.
''')
    code('''with (OUT/'reference.log').open('w') as log,contextlib.redirect_stdout(log):reference=Y.run(EXTENDED)
print('Reference-matched catches:',reference['population'])
print('Strong-reference comparison:',reference['exploratory_2025'])
''')
    md('''## Repeatability, source identity, and what is observable

Repeat the primary nested experiment on two additional earlier-player partitions. These reuse players and are not independent replications. Swap whole training-player source profiles within class thirty times under a fixed selected raw-YAC configuration; retain every score. This identity diagnostic is not a formal permutation p-value with complete reselection. Paired player intervals use 5,000 resamples and condition on fitted models.

Compare first/last attempts within the same drill, never treating Curl and Comeback as repeated identical tests. Plot the NFL and source demands directly: only 2–17% of 2025 route turns fall inside earlier-source central speed/angle rectangles. These rectangles diagnose limited support; they are not established biological boundaries.

PerfectPower's licensed exact rational calculus checks an explicit six-parameter quadratic demand-response surrogate. Quantized source conditions form observation rows; NFL demands form target rows. An invisible coefficient direction demonstrates when source measurements cannot determine the target under this model. Minimum-cardinality extra condition sets complete its row space; a numerical noise criterion chooses among those sets. These are conditional measurement-design statements, not proofs of athlete physiology, training efficacy, or forecast accuracy. Pooling route intent makes the surrogate deliberately optimistic.
''')
    code('''with (OUT/'diagnostics.log').open('w') as log,contextlib.redirect_stdout(log):
    stability=P.repeats(EXTENDED)
    diagnostics=D.run(EXTENDED,DATA)
    design=E.run(EXTENDED)
print('Repeated turn-transfer difference:',stability['three_partition_mean_delta_mse'],stability['conditional_ci95'])
print('Profile controls:',diagnostics['raw_yac_identity_shuffles']['mean_mse'],diagnostics['raw_yac_identity_shuffles']['real_profile_mse'])
print('Source-demand support:',diagnostics['source_game_demand_overlap_2025'])
print('Exact surrogate design:',design['ambiguous_NFL_target_maps'],'ambiguous players of',design['players_with_source_and_game_demands'],design['minimum_additional_measurement_histogram'])
''')
    md('''## Coaching interpretation and honest findings

The five figures connect a paired receiver's observed geometry, response-window coverage, demand mismatch, model uncertainty, strong YAC references, and exact surrogate ambiguity. The player example is selected from development data by sorted identifiers and source availability, without selecting on NFL responses. The two hypothetical response surfaces illustrate ambiguity; they are not fitted biological discoveries.

The completed experiments do not establish a substantial Combine prediction gain. Correct timing nearly doubles measurable turn responses, while source execution does not improve turn-transfer prediction reliably and harms separation prediction. The raw YAC improvement deserves investigation, but the stronger reference and earlier-player evidence prevent a winning-edge claim. Repeatable traits, comparable demands, and actual football consequences must all hold together.

For evaluators, these results argue for testing a proposed trait at the speeds and turn demands where NFL decisions will use it, rather than assigning draft value from an isolated curve. The conditional design tool specifies how an assumed response family could be measured more completely. A coaching intervention or reduced bust rate requires new evidence. This first-peak detector can include an initial heading adjustment; it does not establish correspondence with a complete playbook route break. Pre-release anchor selection, small cohorts, vendor processing, route intent, catch involvement and prior test inspection remain limitations.

Official [data](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/data) and [rules](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/rules). Embedded code and source hashes support authorized reproduction. Restricted raw files and private player outputs are excluded from the archive. No betting-application integration, public Kaggle publication, or formal submission is implied.
''')
    code('''figures=V.run(EXTENDED,ORIGINAL,OUT/'figures')
for figure in figures:display(Image(filename=str(figure)))
''')
    path=ROOT/'notebooks/Turn_Translation_Lab.ipynb';path.write_text(json.dumps(nb,indent=1));words=sum(len(''.join(c['source']).split()) for c in nb['cells'] if c['cell_type']=='markdown');assert words<2000;print(json.dumps({'path':str(path),'narrative_words':words,'code_cells':6,'composite_figures':5}));return path
if __name__=='__main__':build()
