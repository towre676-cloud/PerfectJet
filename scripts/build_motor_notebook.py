"""Generate a standalone notebook; notebook execution is distinct from the recorded real-data runner."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def build():
    sources={str(p.relative_to(ROOT/'src')):p.read_text() for p in sorted((ROOT/'src/perfectjet').rglob('*.py'))}
    hashes={p:hashlib.sha256(s.encode()).hexdigest() for p,s in sources.items()}
    cells=[]
    def cell(kind,source):
        row={'cell_type':kind,'id':f'perfectjet-{len(cells):03d}','metadata':{},'source':source}
        if kind=='code':row.update(execution_count=None,outputs=[])
        cells.append(row)
    cell('markdown','# Can measured Combine launch movement improve NFL scouting?\n\n**Unexecuted notebook: no new real-data gain is claimed.** Attach the official NFL Big Data Bowl 2027 input. All actual source is embedded and hashed. The supplied get-off variable measures snap-to-line-of-scrimmage crossing, combining onset and travel depth. We test a post-onset half-second Combine readout against the full conventional comparator. Previously inspected 2025 remains development evidence.\n\nThe prior canonical study improved extraction sensitivity by 34.1% but did not establish dependable scouting lift. Its failed duration and pooled models remain preserved in the repository. This experiment changes the measured motor readout and integrates uncertainty from actual independent attempts.')
    setup='''import hashlib,json,sys,tempfile
from pathlib import Path
WORK=Path(tempfile.mkdtemp(prefix="perfectjet-motor-"))
for name,source in SOURCES.items():
    assert hashlib.sha256(source.encode()).hexdigest()==HASHES[name]
    path=WORK/"src"/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(source)
sys.path.insert(0,str(WORK/"src"))
print("Verified",len(SOURCES),"embedded source modules")
'''
    cell('code','SOURCES='+repr(sources)+'\nHASHES='+repr(hashes)+'\n'+setup)
    cell('markdown','The source functional is $A_T=2[x_\\parallel(t_0+T)-x_\\parallel(t_0)-Tv_\\parallel(t_0)]/T^2$, with $T=0.5$s. It equals acceleration for quadratic motion and otherwise weights post-onset acceleration. Launch history and straightness must be observed. Operational onset is not a known start cue; this is not a reaction-time estimate. Smoothing branches are descriptive scenarios and never independent repeats.\n\nPrimary extraction uses forty-yard starts; the separately declared secondary family adds front-drill starts with source-only adjustment. Both models receive all fifteen conventional measurements, Combine position and identical raw drill flags/counts. Supplied NGS grades use a declared pre-draft interpretation; repeat without them as a chronology sensitivity.')
    cell('code','''import os
from perfectjet.applications.nfl_scouting.official import load_official_directory,OFFICIAL_FILES
from perfectjet.applications.nfl_scouting.burst_transfer import PROTOCOL,experiment,full_refit_sensitivity
DATA=Path(os.environ.get("BDB_DATA_ROOT","/kaggle/input/nfl-big-data-bowl-2027"))
if not all((DATA/name).is_file() for name in OFFICIAL_FILES):
    candidates=[p.parent for p in Path("/kaggle/input").rglob("players.csv") if all((p.parent/name).is_file() for name in OFFICIAL_FILES)] if Path("/kaggle/input").exists() else []
    if len(candidates)!=1:raise FileNotFoundError("Attach the official nine-file input or set BDB_DATA_ROOT; no synthetic fallback")
    DATA=candidates[0]
ds=load_official_directory(DATA,minimum_plays=30,verify_known_hashes=True)
print(json.dumps({"protocol":PROTOCOL,"population":ds.manifest["official_adapter"]["audit"]},indent=2))
''')
    cell('markdown','Each temporal and inner player split rebuilds context labels, source references, repeat variance, imputation, scaling and selection. Starting depth and NFL context define targets only; they never enter the pre-draft predictor. The Gaussian correction uses $r_i\\mid D_i\\sim N(\\lambda m_i,\\sigma_{NFL}^2+\\nu_i^2+\\lambda^2V_i)$, accounting for source precision and descriptive game-cluster outcome precision. Original-player bootstrap copies remain together. Missing NFL participation remains missing.\n\nReport equal-player paired errors, source coverage, calibration, full-refit sensitivity and the frozen lower-quartile shortlist. Exact identifiability, conditional Gaussian uncertainty and empirical prediction gains are distinct claims. No diagnostic outcome may replace a failed get-off headline after seeing results.')
    cell('code','''import contextlib,io
with contextlib.redirect_stdout(io.StringIO()):
    result=experiment(ds,include_ngs=True,seed=81014)
    result["full_refit_sensitivity"]=full_refit_sensitivity(ds,draws=64,include_ngs=True,seed=81014)
    no_ngs=experiment(ds,include_ngs=False,seed=81014)
result["embedded_source_hashes"]=HASHES
(WORK/"private_results.json").write_text(json.dumps(result,indent=2))
summary={k:{"usable_attempts":v["usable_attempts"],"source_players":v["source_players"],"summary":{q:r for q,r in v["summary"].items() if q!="largest_influences"}} for k,v in result["families"].items()}
print(json.dumps({"families":summary,"full_refits":result["full_refit_sensitivity"],"no_NGS_sensitivity":{k:v["summary"]["gain"] for k,v in no_ngs["families"].items()},"conclusion":result["conclusion"]},indent=2))
''')
    cell('code','''import matplotlib.pyplot as plt
import numpy as np
fig,axes=plt.subplots(2,2,figsize=(14,9),layout="constrained")
families=list(result["families"]);labels=["Forty starts: primary","Front starts: secondary"]
axes[0,0].bar(labels,[result["families"][k]["source_players"] for k in families])
axes[0,0].set(title="Usable Combine coverage",ylabel="Players")
for j,k in enumerate(families):
    folds=result["families"][k]["folds"]
    gain=[100*(1-np.mean((np.array(f["y"])-f["movement"])**2)/np.mean((np.array(f["y"])-f["baseline"])**2)) for f in folds]
    axes[0,1].plot([f["year"] for f in folds],gain,"o-",label=labels[j])
    r=result["full_refit_sensitivity"]["families"][k]
    if r["percentile_90"]:
        lo,hi=r["percentile_90"];axes[1,0].plot([100*lo,100*hi],[j,j],lw=5);axes[1,0].plot(100*r["median"],j,"o")
    dec=result["families"][k]["summary"]["decisions"]
    axes[1,1].bar(np.array([0,1])+j*.35,[sum(d["hits"][m] for d in dec) for m in ("baseline","movement")],width=.33,label=labels[j])
axes[0,1].axhline(0,color="gray");axes[0,1].legend();axes[0,1].set(title="Development class comparisons",ylabel="Error reduction (%)")
axes[1,0].axvline(0,color="gray");axes[1,0].set(yticks=range(len(labels)),yticklabels=labels,title="Full pipeline refits",xlabel="Empirical 90% gain interval (%)")
axes[1,1].set(xticks=[.175,1.175],xticklabels=["Conventional","Movement"],title="Fixed-budget shortlist",ylabel="Hits");axes[1,1].legend()
fig.savefig(WORK/"aggregate_figures.png",dpi=180);plt.show()
''')
    cell('markdown','The four panels summarize coverage, development prediction gains, refit sensitivity and decision hits. Losses and null results receive the same visibility as gains. Refit intervals do not undo prior adaptive use or establish future transport. A true scouting advantage still requires held-out-player improvement against the equally informed baseline, practical decision value and independent future confirmation. No betting or causal developmental claim follows.')
    nb={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'},'perfectjet':{'version':'0.13.0','execution_status':'unexecuted_notebook_runner_evidence_separate','source_sha256':hashes}},'cells':cells}
    path=ROOT/'notebooks/PerfectJet_Motor_Transfer.ipynb';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(nb,indent=1)+'\n')
    for row in cells:
        if row['cell_type']=='code':compile(row['source'],str(path),'exec')
    print(json.dumps({'embedded_sources':len(sources),'code_cells_syntax_checked':4,'executed_on_NFL_data':False}))

if __name__=='__main__':build()
