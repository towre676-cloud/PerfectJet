"""Build the self-contained public, aggregate-only ordered-channel notebook."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
def build():
    cells=[]
    def md(s):cells.append(dict(cell_type='markdown',metadata={},source=s.splitlines(True)))
    def code(s):cells.append(dict(cell_type='code',metadata={},source=s.splitlines(True),outputs=[],execution_count=None))
    md('''# Does the order of a cut travel?

We test whether braking, redirection and recovery sequences in Combine receiver drills carry information beyond conventional measurements and recorded football context. This adapts the finite-state ordered-language idea from PerfectPower arithmetic modes, pinned to Git commit 85f8dea557a95a5a01682f50d63a0ac6438e6d78. It does not attach prime numbers or quantum spin to players. The numerical motion implementation is new; the donor's Lean proofs do not certify it.

This is adaptive exploratory research. Earlier analyses inspected 2025. The first round concatenates ordered features; the second responds to its development diagnostics by learning only corrections to baseline errors. Both rounds and every candidate loss remain visible. Model choices use earlier seasons, but this is not a fresh blind test or a claim of guaranteed competition victory.
''')
    files=['analysis.py','repo_predict.py','mechanism.py','observability.py','turn_transfer.py','post_release_transfer.py','yac_reference_correction.py','ordered_motion.py'];modules={n:(ROOT/n).read_text() for n in files};hashes={r['file']:r['sha256'] for r in json.loads((ROOT/'receipts/actual/acquisition.json').read_text())['files']}
    code('''import os,sys,json,hashlib,tempfile,contextlib
from pathlib import Path
import numpy as np,pandas as pd
from IPython.display import display,Image
DATA=Path(os.environ.get('BDB_DATA_ROOT','/kaggle/input/nfl-big-data-bowl-2027')).resolve()
if not (DATA/'players.csv').exists():
    candidates=list(Path('/kaggle/input').rglob('players.csv')) if Path('/kaggle/input').exists() else []
    if len(candidates)!=1:raise FileNotFoundError('Attach the official competition input or set BDB_DATA_ROOT.')
    DATA=candidates[0].parent
WORK=Path(tempfile.mkdtemp(prefix='bdb_ordered_private_'));SRC=WORK/'sources';SRC.mkdir()
MODULES='''+repr(modules)+'''
for name,text in MODULES.items():(SRC/name).write_text(text)
sys.path.insert(0,str(SRC))
EXPECTED='''+repr(hashes)+'''
for name,expected in EXPECTED.items():
    h=hashlib.sha256()
    with (DATA/name).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    if h.hexdigest()!=expected:raise ValueError('Official snapshot differs: '+name)
os.chdir(WORK)
import turn_transfer as T,post_release_transfer as P,ordered_motion as M
print('Verified nine official inputs. All individual records stay in temporary private files.')
''')
    md('''## Ordered motion and a constrained phase language

Keep the established first qualifying 25–150° heading-change anchor, approach speed at least 2.5 yd/s, and fixed IN/OUT/SLANT/HITCH drill mapping. Extend response observation after release, preserving the original anchor. This anchor can be an initial adjustment rather than the semantic playbook break; its scope is explicit.

For Combine windows of radius 0.6, 1.0 or 1.4 seconds around that anchor, construct a four-channel path: speed divided by entry speed, speed derivative divided by 5, absolute heading derivative, and cumulative normalized distance. Compute channel means, standard deviations, endpoint differences and six signed second-order areas. For two channels x,y the area is one half of the sum of midpoint(x) times increment(y) minus midpoint(y) times increment(x). Reversing order flips its sign even when summary distributions remain unchanged.

A four-state grammar allows approach → brake → redirect → recover, with stays and single-phase advances. Every path starts in approach and ends in recovery. Gaussian-shaped fixed emission costs use normalized acceleration and absolute angular rate; these are hypotheses, not validated biomechanical labels. Forward/backward dynamic programming sums all admissible paths in log space. Features include expected phase occupancy, phase-conditioned acceleration and normalized log path mass. The latter includes combinatorial length effects. No hard segmentation is declared ground truth. Irregular or stationary-heading artifacts remain an anchor-level limitation.
''')
    code('''with (WORK/'extraction.log').open('w') as log,contextlib.redirect_stdout(log):
    T.prepare(DATA,'private_turn_transfer')
    P.prepare(DATA,'private_turn_transfer','private_post_release')
    source=M.extract(DATA,'private_ordered_motion')
print('Combine attempts:',len(source),'receivers:',source.nfl_id.nunique())
''')
    md('''## Genuine player holdout and adaptive corrections

Require ten NFL turn windows per player. For YAC require three targeted catches with finite measured and supplied expected YAC. Give each player equal total weight. Four outer and three inner folds keep all observations of a player together. Conventional body, timed and NGS measurements, football context and source turn demands form the mechanical baseline. Supplied expected YAC is the strong catch-context reference; it is not an unconditional pre-draft prediction.

Fit source aggregation scales and physical residualization on training players only. Round one adds squared motion innovations to the shared predictor. Its bank contains four baseline ridge penalties, nine ordered window/penalty combinations and the same zero YAC correction option. The ordered family also retains baseline candidates.

Round two preserves a fixed baseline: development-selected ridge 10 for mechanical burden, and supplied expected YAC for catches. Train its correction on three-fold player-held-out baseline errors. Include motion squares, entry-speed and angle interactions, and body-mass interactions. Inner folds choose among nine corrections and no correction. A separate 2023 training/2024 tuning split selects a configuration before exploratory 2025 evaluation. Nested earlier-player estimates do not establish new-season generalization. Bootstrap intervals resample players conditional on fitted predictions; they omit full refitting and adaptive-search uncertainty.
''')
    code('''results={}
with (WORK/'experiments.log').open('w') as log,contextlib.redirect_stdout(log):
    for label,correction in [('concatenation',False),('correction',True)]:
        out='private_ordered_motion' if not correction else 'private_ordered_correction';Path(out).mkdir(exist_ok=True)
        results[label]={target:M.run(source,out,target,correction) for target in ['burden','yac_residual']}
for label,bank in results.items():
    for target,r in bank.items():
        for split in ['nested','exploratory_2025']:
            v=r[split];print(label,target,split,'players',v['players'],'MSE',v['mse'],'delta/CI',v['increment']['delta_mse'],v['increment']['ci95'])
''')
    code('''import matplotlib.pyplot as plt
plt.rcParams.update({'figure.dpi':140,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(12,4.5))
for ax,target in zip(axes,['burden','yac_residual']):
    labels=[];means=[];bounds=[]
    for label in results:
        for split in ['nested','exploratory_2025']:
            v=results[label][target][split]['increment'];labels.append(label+' / '+('earlier players' if split=='nested' else '2025'));means.append(v['delta_mse']);bounds.append(v['ci95'])
    bounds=np.array(bounds);means=np.array(means);ax.errorbar(means,np.arange(4),xerr=np.maximum(0,np.c_[means-bounds[:,0],bounds[:,1]-means].T),fmt='o',capsize=4,color='#156985');ax.axvline(0,color='gray',lw=1);ax.set_yticks(range(4),labels);ax.set_xlabel('Baseline MSE minus ordered MSE');ax.set_title('Half-second speed deficit' if target=='burden' else 'Expected-YAC residual');ax.invert_yaxis()
fig.suptitle('Ordered channels: player-level uncertainty, both adaptive rounds');fig.tight_layout();plt.show()
fig,axes=plt.subplots(1,2,figsize=(12,4))
for j,label in enumerate(['approach','brake','redirect','recover']):axes[0].hist(source[f'order_10_{18+j}'],bins=20,histtype='step',label=label)
axes[0].legend();axes[0].set(xlabel='Expected fraction of frames in hypothesized phase',ylabel='Combine attempts',title='Soft phase language: receiver drill population')
axes[1].hist(source['order_10_12'],bins=30,color='#156985');axes[1].set(xlabel='Signed speed–acceleration channel area',ylabel='Combine attempts',title='An order-sensitive geometric measurement');fig.tight_layout();plt.show()
''')
    md('''## Adapt the population, not the desired answer

The turn-selected 2025 catch sample contains only 11 receivers. A third development step removes the NFL-turn requirement: all non-nullified rookie regular-season targeted catches with finite YAC and supplied expected YAC, at least ten per receiver, and an available Combine drill profile. Pool source-drill descriptors into a player profile and preserve actual game route as shared context. No NFL turn-demand measurements enter this broader model; empty demand columns are constants. Repeat both the concatenated and baseline-error correction banks. This is a broader task and cohort, not a directly comparable re-estimate of the turn-specific contrast.
''')
    code('''broad=M.catch_population(DATA,source);pooled=source.copy();pooled['route_ran']='ALL';oldcats=M.R.CAT;M.R.CAT=oldcats+['actual_route'];broad_results={}
try:
    with (WORK/'broad.log').open('w') as log,contextlib.redirect_stdout(log):
        for label,correction in [('concatenation',False),('correction',True)]:
            out='private_all_catch_'+label;Path(out).mkdir(exist_ok=True);broad_results[label]=M.run(pooled,out,'yac_residual',correction,broad)
finally:M.R.CAT=oldcats
for label,r in broad_results.items():
    for split in ['nested','exploratory_2025']:
        v=r[split];print('All-catch',label,split,'players/catches',v['players'],v['rows'],'MSE',v['mse'],'versus reference delta/CI',v['vs_reference']['delta_mse'],v['vs_reference']['ci95'])
fig,ax=plt.subplots(figsize=(10,4));labels=[];means=[];bounds=[]
for label,r in broad_results.items():
    for split in ['nested','exploratory_2025']:
        v=r[split]['vs_reference'];labels.append(label+' / '+('earlier players' if split=='nested' else '2025'));means.append(v['delta_mse']);bounds.append(v['ci95'])
bounds=np.array(bounds);means=np.array(means);ax.errorbar(means,np.arange(4),xerr=np.maximum(0,np.c_[means-bounds[:,0],bounds[:,1]-means].T),fmt='o',capsize=4);ax.axvline(0,color='gray');ax.set_yticks(range(4),labels);ax.set_xlabel('Supplied expected-YAC MSE minus model MSE');ax.set_title('Broader rookie receiving workload: the strong reference');fig.tight_layout();plt.show()
''')
    md('''## Football interpretation

The plausible scouting signal is how a receiver sequences braking and redirection for a specified demand, rather than a universal “more braking is better” score. A usable development protocol would require repeatable phase measurements at comparable speeds and angles, followed by prospective validation of the resulting training advice. These experiments measure associations, not causal improvement from an intervention.

A gain must survive comparison with the supplied expected-YAC reference and conventional measurements, player and season transport, and uncertainty. Zero correction is a legitimate adaptive choice. Report actual figures above; do not select only favorable trials. The earlier analysis notebooks and this complete candidate ledger preserve the research history. Raw competition data and individual predictions are excluded from the public package. This notebook has not been submitted or publicly published.
''')
    nb=dict(nbformat=4,nbformat_minor=5,metadata={'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'},'language_info':{'name':'python','version':'3.11'}},cells=cells);(ROOT/'notebooks/Ordered_Motion_Channels.ipynb').write_text(json.dumps(nb,indent=1))
if __name__=='__main__':build()
