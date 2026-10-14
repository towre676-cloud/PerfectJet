from pathlib import Path
import json,ast
root=Path(__file__).parent
cells=[]
def md(s):cells.append({'cell_type':'markdown','metadata':{},'source':s.splitlines(True)})
def code(s):
 ast.parse(s);cells.append({'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':s.splitlines(True)})
md('''# Braking that travels: do Combine cuts predict rookie receiver separation?

**OBSERVED RESEARCH ACCOUNT — OCTOBER 13, 2026.** The official files have been downloaded and the retained primary experiment and diagnostics have run. The original single-drill model failed. The expanded model improves the observed score against the original baseline, while its incremental motion value remains uncertain. This notebook reproduces the analysis from the official input. It has not been publicly published or submitted.

A coach sees a receiver arrive at a break, reduce speed, change direction, and escape. The forty-yard time summarizes straight-line speed; it does not describe that tradeoff. We ask whether a shared Combine route drill supplies useful information about rookie separation after accounting for conventional tests and game situations.

The official description reports 510 prospects from 2023–2025, 6,310 Combine attempts, and 316,338 player-play rows. Downloaded bytes confirm 510 prospects and 6,310 Combine attempts, but player-play records total 314,197 rather than 316,338. The analysis joins official player identifiers, retains WR rookie regular seasons and non-nullified cutting routes, and requires at least twenty measured routes per player. The shared drill is selected by Combine availability before NFL outcomes. We report opt-outs and rejected attempts; target-only measurement would narrow the claim to targeted routes.

The primary features describe entry speed, retained speed at the break, exit gain, integrated braking, turn angle, curvature energy, jerk, and signed trajectory area. The area is the antisymmetric second-level path signature. Field coordinates are normalized by translation, entry direction, and turn handedness. Tracking is sampled at 10 Hz, so derivative noise and smoothing sensitivity matter.

The conventional comparison includes body measurements, the forty and ten-yard split, jumps, three-cone and shuttle, plus route, cushion, formation, coverage, down and field context. A scouting reference adds college production. Matched random forests test whether motion gains survive a nonlinear conventional model; physical and coverage interactions are exploratory. Career totals and draft position are excluded.

Training is restricted to the 2023 class in its rookie season, tuning to the 2024 class in its rookie season, and testing to the 2025 class in its rookie season. Imputation, encoding and scaling are fitted on development data. All attempts and routes belonging to a player stay in one cohort. Each player receives equal total fitting weight and equal total evaluation weight.

Our primary estimate is the reduction in player-balanced mean squared error from adding movement to a regularized linear baseline. A paired player bootstrap supplies uncertainty. A positive point estimate with an interval crossing zero is inconclusive. Results from one draft class cannot establish universal transport or a causal coaching intervention. We retain negative results and do not replace the primary contrast with a better-looking exploratory model after seeing test results.

The provided separation metric is essential: game trajectories cover the rookie cohort, so the notebook does not invent missing defender paths. Secondary game-cut measurements are descriptive outcome-side checks. They never enter the pre-draft predictor.

**Observed results:** the shared availability-selected drill is DAGGER_ROUTE_LEFT. The final cohort comprises 26 training, 21 validation and 17 test receivers, with 3,326, 2,285 and 1,737 routes. Conventional linear RMSE is 1.738 yards; motion-augmented RMSE is 1.823 yards. The baseline-minus-motion MSE difference is −0.302 squared yards, with paired-player 95% interval [−0.616, −0.078]. The augmentation is worse on this held-out task. Conventional forest RMSE is 1.721 versus 1.725 with motion; its difference interval crosses zero. Five- and nine-frame smoothing also underperform. Thirty development-player block shuffles are diagnostic only, not a p-value. Across 2,538 qualifying game cuts, the tested receiver-median mechanics correlations are weak (absolute Spearman rho at most 0.110). There is no supported predictive gain. The visual explanation is designed for coaches and fans: path shape and speed, the brake-turn-recovery curve, and a speed/acceleration portrait. Actual plots below are generated only after official data are attached.

**Data use:** noncommercial research only. Do not redistribute raw tracking or per-player private result files. Public competition code must also be posted on Kaggle as required by the rules. This file has not been published or submitted. Before outcome filtering, 15.1% of non-targeted routes lack separation, versus none of the targeted routes. This coverage bias and a single small test class limit generalization. All post-primary diagnostics are explicitly labeled as reusing the test cohort. This account stays within 2,000 words and six composite figures. References: [official data](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/data), [rules](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/rules).
''')
code('''import sys, platform, json
from pathlib import Path
import numpy, pandas, scipy, sklearn, matplotlib
print({"python": platform.python_version(), "numpy": numpy.__version__, "pandas": pandas.__version__, "scipy": scipy.__version__, "sklearn": sklearn.__version__, "matplotlib": matplotlib.__version__})
''')
md('## Reproducible implementation\nThis appendix contains all analysis code, rather than depending on a moving upstream repository. Random seed, feature definitions, cohort filters, models and bootstrap are fixed.')
source=(root/'analysis.py').read_text()
code('import types\nA = types.ModuleType("bdb_analysis")\nexec(compile('+repr(source)+', "bdb_analysis.py", "exec"), A.__dict__)\n')
md('## Locate the attached official files\nAttach NFL Big Data Bowl 2027 as the Kaggle competition input. An approved local copy may be used by setting DATA_ROOT. No credentials are stored in this notebook.')
code('''import os
candidates=list(Path('/kaggle/input').rglob('players.csv')) if Path('/kaggle/input').exists() else []
DATA_ROOT=Path(os.environ['BDB_DATA_ROOT']) if os.environ.get('BDB_DATA_ROOT') else (candidates[0].parent if len(candidates)==1 else None)
required=['players.csv','combine_results.csv','combine_tracking.csv','player_career_successes.csv','player_play.csv','games.csv','game_tracking_2023.csv','game_tracking_2024.csv','game_tracking_2025.csv']
READY=DATA_ROOT is not None and all((DATA_ROOT/f).exists() for f in required)
print({'status':'official_files_available' if READY else 'BLOCKED_AUTHENTICATED_DATA_REQUIRED','data_root':str(DATA_ROOT) if DATA_ROOT else None})
''')
md('## Run the locked comparison\nThis cell streams a byte-level inventory, constructs features and preserves exclusions, selects model settings only on 2024, then evaluates the locked 2025 cohort. Intermediate player data remain private; show only approved aggregate summaries in a public notebook.')
code('''OUT=Path('/kaggle/working/private_notebook_original') if Path('/kaggle/working').exists() else Path('private_notebook_original')
if READY:
    report=A.run(DATA_ROOT,OUT)
    print(json.dumps(report,indent=2))
    summary=json.loads((OUT/'population_audit.json').read_text());summary['excluded_attempts_count']=len(summary.pop('excluded_attempts'));print(json.dumps(summary,indent=2))
else:
    report=None
    print('NOT RUN: no actual-data results, no claim of predictive value.')
''')
md('## Figure 1 — Explain the observed cut\nThe plotted attempt is selected by sorted identifier independently of NFL outcomes. It is one example, not an estimate of the average receiver.')
code('''if READY:
    from IPython.display import Image,display
    display(Image(filename=str(OUT/'actual_combine_geometry.png')))
    from IPython.display import HTML
    display(HTML((OUT/'actual_combine_geometry.html').read_text()))
''')
md('## Figure 2 — Held-out performance and uncertainty\nThe primary improvement is in squared yards; model RMSE is in yards. Exploratory models remain labeled separately. A confidence interval overlapping zero supports an inconclusive statement.')
code('''if report:
    import matplotlib.pyplot as plt
    names=[r['model'] for r in report['results']]
    errors=[r['test_rmse_yards'] for r in report['results']]
    fig,ax=plt.subplots(1,2,figsize=(14,5),layout='constrained')
    ax[0].barh(names,errors,color=['#2cbfa6' if 'tracking' in n else '#8298b0' for n in names]);ax[0].set_xlabel('Held-out player-balanced RMSE · yards')
    lo,hi=report['player_bootstrap_ci95'];value=report['primary_delta_mse_yards_squared']
    ax[1].plot([lo,hi],[0,0],lw=5,color='#2cbfa6');ax[1].scatter([value],[0],s=90,color='#e9b65d');ax[1].axvline(0,color='#8298b0',ls='--');ax[1].set_xlabel('Primary MSE reduction · squared yards');ax[1].set_yticks([]);ax[1].set_title('Paired player bootstrap · 95% interval')
    plt.show()
''')
md('## Secondary mechanics replication\nThis potentially expensive cell is off by default. Turn it on only after reviewing the primary population audit. No conclusions from it enter the pre-draft model. Missing/short/straight trajectories are rejected; coverage is not reconstructed.')
code('''RUN_SECONDARY=True
if READY and RUN_SECONDARY:
    rows=pandas.read_pickle(OUT/'private_analysis_rows.pkl')
    print(A.game_transfer(DATA_ROOT,rows,OUT))
''')
md('## Figure 3 — Population and missing outcomes\nSeparation is available on untargeted routes as well as targets, but missingness differs. These plots describe coverage; they do not repair the bias.')
code('''if READY:
    import numpy as np
    audit=json.loads((OUT/'population_audit.json').read_text())
    players=pandas.read_csv(DATA_ROOT/'players.csv');games=pandas.read_csv(DATA_ROOT/'games.csv');pp=pandas.read_csv(DATA_ROOT/'player_play.csv')
    z=pp.merge(players[['nfl_id','draft_year','nfl_position']],on='nfl_id',validate='many_to_one').merge(games[['game_id','season','season_type']],on='game_id',validate='many_to_one')
    z=z[z.nfl_position.eq('WR')&z.season.eq(z.draft_year)&z.season_type.eq('REG')&z.route_ran.isin(A.CUT_ROUTES)&z.play_nullified_by_penalty.eq('N')]
    missing=z.groupby('target').separation_at_pass_forward.apply(lambda v:float(v.isna().mean()))
    fig,ax=plt.subplots(1,2,figsize=(14,5),layout='constrained');x=np.arange(3)
    totals=players[players.nfl_position.eq('WR')].groupby('draft_year').size().reindex([2023,2024,2025]).to_numpy();kept=[audit['draft_class_players'][str(y)] for y in [2023,2024,2025]]
    ax[0].bar(x-.18,totals,.36,label='WR prospects');ax[0].bar(x+.18,kept,.36,label='Eligible study');ax[0].set_xticks(x,['2023 train','2024 tune','2025 test']);ax[0].set_ylabel('Players');ax[0].legend()
    ax[1].bar(['Targeted','Not targeted'],[100*missing.get(True,0),100*missing.get(False,0)]);ax[1].set_ylabel('Missing separation · %');plt.show()
''')
md('## Figure 4 — Post-primary sensitivity and negative control\nFive- and nine-frame smoothing and thirty development-player block shuffles reuse the test set as diagnostics. They cannot select a new test winner or provide a formal permutation p-value.')
source_checks=(root/'followup_checks.py').read_text()
code('sys.modules["analysis"]=A\nB=types.ModuleType("bdb_checks")\nexec(compile('+repr(source_checks)+',"bdb_checks.py","exec"),B.__dict__)\nif READY:\n    diagnostics=B.run_checks(DATA_ROOT,OUT)\n    print(json.dumps(diagnostics,indent=2))\n')
code('''if READY:
    fig,ax=plt.subplots(1,2,figsize=(14,5),layout='constrained')
    ss=diagnostics['smoothing_sensitivity'];ax[0].plot([v['smoothing_frames'] for v in ss],[v['test_rmse_yards'] for v in ss],'o-');ax[0].axhline(report['results'][0]['test_rmse_yards'],ls='--',color='green',label='Conventional baseline');ax[0].set(xlabel='Smoothing frames',ylabel='Test RMSE · yards');ax[0].legend()
    ax[1].hist(diagnostics['development_player_block_permutation']['test_mse_values'],bins=12);ax[1].axvline(report['results'][1]['test_player_balanced_mse'],color='orange',label='Observed motion');ax[1].axvline(report['results'][0]['test_player_balanced_mse'],color='green',ls='--',label='Conventional baseline');ax[1].set(xlabel='Test MSE · squared yards',ylabel='Development-player shuffles');ax[1].legend();plt.show()
''')
md('## Figure 5 — Do the mechanics travel?\nThis is descriptive across observed rookie receivers, not a causal or held-out scouting claim. Receiver medians aggregate repeated game turns; no game features enter the pre-draft model.')
code('''if READY and RUN_SECONDARY:
    from scipy.stats import spearmanr
    keys=['entry_speed','speed_retention','exit_gain','turn_angle']
    attempts=pandas.read_csv(OUT/'attempt_features.csv');selected=audit['selected_drill'];c=attempts[attempts.drill_name.eq(selected)].groupby('nfl_id')[keys].median();g=pandas.read_csv(OUT/'private_game_motion.csv').groupby('nfl_id')[keys].median();j=c.join(g,lsuffix='_combine',rsuffix='_game',how='inner')
    fig,ax=plt.subplots(2,2,figsize=(12,9),layout='constrained')
    for a,k in zip(ax.ravel(),keys):
        rho=spearmanr(j[k+'_combine'],j[k+'_game']).statistic;a.scatter(j[k+'_combine'],j[k+'_game']);a.set(xlabel='Combine '+k,ylabel='Game '+k,title=f'Spearman rho {rho:.3f}')
    plt.show()
''')

md('## Repo extension — ordered movement, state memory and route-conditioned readouts\nThis exploratory extension uses eight shared drills and 856 predictors: cubic time/space/speed path signatures, Legendre speed modes, Hankel spectra, velocity-memory coefficients, and basic mechanics. PerfectPower’s pinned Apache-2.0 rational observable-machine implementation replays 1,109 fitted surrogate certificates and twelve source/quotient readouts each. That certifies the supplied quantized linear surrogate, not real biomechanics or scouting performance. DynaComp’s memory/Hankel architecture informed the design; no unlicensed source was copied. Prospect preprocessing and four/eight-dimensional PCA are fitted on unique training players, not repeated routes.\n\nFive identical model candidates per family are selected using 2023 training and 2024 validation. Four outer and three inner player-group folds assess the two earlier cohorts. The drill dictionary was fixed from supplied Combine availability across all three classes; the nested fits exclude 2025 outcome labels. Because 2025 was inspected before this expansion, its new results are exploratory, not a fresh holdout.\n\nThe expanded full model has observed 2025 RMSE 1.677 yards, versus the original forest’s 1.721 and strengthened conventional model’s 1.688. The 4.98% MSE decrease relative to the original model includes better conventional predictors and learner selection. Incremental motion gain versus the strengthened comparator is 0.0377 squared yards with interval [−0.0434, 0.1099]; earlier nested validation does not confirm it. A separate route-matched experiment maps IN to Dagger, OUT to the explicit Speed Out name alias, SLANT to Slant, and HITCH to Curl/Comeback. Its small positive differences in both earlier nested and 2025 checks remain inconclusive. That changed population is evaluated only against its own matched conventional baseline. No independently established motion advantage is claimed.')
bootstrap_source='import types,sys\n'
bootstrap_source+='vp=types.ModuleType("vendor");vp.__path__=[];sys.modules["vendor"]=vp\npp=types.ModuleType("vendor.pp");pp.__path__=[];sys.modules["vendor.pp"]=pp\n'
for name in ['divisor_square','exact_linear','observable_machine']:
    source_vendor=(root/'vendor'/'pp'/f'{name}.py').read_text()
    bootstrap_source+=f'm=types.ModuleType("vendor.pp.{name}");m.__package__="vendor.pp";sys.modules[m.__name__]=m;setattr(pp,"{name}",m)\nexec(compile({source_vendor!r},"{name}.py","exec"),m.__dict__)\n'
for name in ['repo_motion','repo_predict','route_matched','repo_robustness','mechanism']:
    source_module=(root/f'{name}.py').read_text()
    bootstrap_source+=f'm=types.ModuleType("{name}");sys.modules["{name}"]=m\nexec(compile({source_module!r},"{name}.py","exec"),m.__dict__)\n'
code(bootstrap_source)
code('''if READY:
    import repo_motion as RM,repo_predict as RP,route_matched as RT,repo_robustness as RR
    REPO_OUT=OUT.parent/'private_repo_results';MATCH_OUT=OUT.parent/'private_repo_matched'
    RM.build_features(DATA_ROOT,REPO_OUT)
    repo_cohort=RP.cohort_trial(OUT.parent,REPO_OUT,data_root=DATA_ROOT,analysis_out=OUT)
    repo_nested=RP.nested_development(OUT.parent,REPO_OUT,data_root=DATA_ROOT,analysis_out=OUT)
    RM.build_features(DATA_ROOT,MATCH_OUT,aliases=True)
    matched_trial=RT.run(OUT.parent,MATCH_OUT,data_root=DATA_ROOT)
    team_diagnostic=RR.run(OUT.parent,REPO_OUT,analysis_out=OUT)
    print(json.dumps(team_diagnostic,indent=2))
''')
md('## Figure 6 — Improvement over the previous version; uncertain incremental motion benefit\nLeft: comparable observations from the original five-route population. Right: paired motion increments for each specified study, with its own population. All intervals shown are exploratory; the route-matched population differs and is not ranked against the original task.')
code('''if READY:
    fig,ax=plt.subplots(1,2,figsize=(15,6),layout='constrained')
    vals=[report['results'][4]['test_rmse_yards'],repo_cohort['selected']['baseline']['test_rmse_yards'],repo_cohort['selected']['all']['test_rmse_yards']]
    ax[0].barh(['Original forest','Strengthened conventional','Full repo-motion model'],vals,color=['#8298b0','#39dbbd','#efb455']);ax[0].invert_yaxis();ax[0].set_xlabel('Exploratory 2025 RMSE · yards')
    intervals=[repo_nested['paired_improvement'],repo_cohort['selected']['all']['paired_vs_strong_conventional'],matched_trial['nested_earlier_data']['paired_improvement'],matched_trial['paired_improvement']]
    labels=['Multi-drill · nested earlier players','Multi-drill · exploratory 2025','Route-matched · nested earlier players','Route-matched · exploratory 2025']
    for i,v in enumerate(intervals):ax[1].plot(v['ci95'],[i,i],lw=4);ax[1].scatter(v['delta_mse'],i,s=70)
    ax[1].set_yticks(range(4),labels);ax[1].axvline(0,ls=':',color='#8298b0');ax[1].set_xlabel('Conventional − motion MSE · squared yards');plt.show()
''')

md('## Receiver contribution after context adjustment\nThe next exploratory model expands each turn to three seconds: approach speed, retention, recovery, braking and propulsion integrals, heading change, bending energy, normalized area, and four Legendre speed modes. Route-specific drill medians supply twelve movement measures; weight and man-coverage interactions are predefined. Across 384 accepted attempts, 25.4% of study routes lack a matching usable motion record and retain imputation indicators.\n\nA fixed context-only ExtraTrees model predicts separation from situation and coverage. Three player-group folds generate training residuals without fitting on the receiver whose residual is measured. Receiver/route/coverage residual means then train a regularized correction using conventional prospect measures, optionally adding mechanics. Equal total prospect weight and shrinkage limit sparse-group influence. These residuals are context-adjusted associations, not causal receiver effects. Each family selects among the same three ridge penalties inside four outer/three inner player folds on 2023–2024. The 2025 class never selects settings.\n\nThe first nested split yields conventional MSE 3.17585 and mechanics MSE 3.17059; the tiny increment is 0.00526 squared yards. Context alone is better at 3.16602. In exploratory 2025 the mechanics increment is effectively zero, 0.000055 with interval [−0.002047,0.001911]. Neither predefined man-coverage subset improves. Repeating the entire nested selection across three player partitions checks split dependence; shared players make these dependent diagnostics, not independent replications. Missing outcomes and unmeasured quarterback/defender effects remain unresolved. Figures 7 and 8 explain the longer movement window and this comparison.')
code('''if READY:
    import mechanism as MF
    MECH_OUT=OUT.parent/'private_mechanism'
    mechanism_trial=MF.run(DATA_ROOT,MECH_OUT)
    split_stability=MF.split_stability(DATA_ROOT,MECH_OUT)
    print(json.dumps(split_stability,indent=2))
    display(Image(filename=str(MECH_OUT/'mechanism_geometry.png')))
    display(Image(filename=str(MECH_OUT/'mechanism_results.png')))
''')
md('The explicit player-randomized checks give negative motion increments in all three partitions: −0.000261, −0.000011 and −0.001775 squared yards. Averaging each player across splits gives −0.000683, with conditional interval [−0.002485,0.001124]. The initial small positive result is therefore partition-dependent. The context-only model beats both corrections in every randomized partition. Twenty software tests pass; these tests verify code behavior, not a scouting advantage.')
md('## Football implication and limits\nThe tested movement representations should not be marketed as established scouting improvements. The longer-window, context-adjusted model also fails to establish a transported advantage. Better cut annotations, opponent/missingness controls and independent future cohorts remain necessary. This study supports specific negative or uncertain results, not a universal conclusion about Combine tracking. Do not redistribute raw CSVs or private predictions.')
nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}},'nbformat':4,'nbformat_minor':5}
for i,c in enumerate(cells):c['id']=f'bdb-{i:03d}'
(root/'notebooks'/'Braking_That_Travels.ipynb').write_text(json.dumps(nb,indent=1))
print('notebook created',len(cells),'cells; all code cells parse')
