"""Render aggregate observed results. Does not bundle original competition data."""
from pathlib import Path
import json
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,pandas as pd
root=Path(__file__).parent;out=root/'private_results';receipt=root/'receipts'/'actual';receipt.mkdir(parents=True,exist_ok=True)
R=json.loads((out/'experiment_results.json').read_text());S=json.loads((out/'followup_checks.json').read_text());P=json.loads((out/'paired_model_intervals.json').read_text());M=json.loads((out/'population_audit.json').read_text());O=json.loads((out/'outcome_missingness.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':'#e6edf6','axes.labelcolor':'#c2cfde','xtick.color':'#9bb0c5','ytick.color':'#9bb0c5','axes.edgecolor':'#304359','axes.facecolor':'#102236','figure.facecolor':'#071421','axes.titlepad':16})
fig,ax=plt.subplots(1,2,figsize=(16,6),layout='constrained');names=['Linear · conventional','Linear · + motion','Forest · conventional','Forest · + motion'];vals=[R['results'][i]['test_rmse_yards'] for i in [0,1,4,5]]
ax[0].barh(names,vals,color=['#8298b0','#efb455','#8298b0','#efb455']);ax[0].invert_yaxis();ax[0].set(xlabel='Player-balanced RMSE · yards',title='NO SUPPORTED GAIN FROM MOTION');ax[0].set_xlim(0,2.1)
for i,v in enumerate(vals):ax[0].text(v+.025,i,f'{v:.3f}',va='center')
for i,k in enumerate(['ridge','forest']):
 c='#efb455' if i==0 else '#39dbbd';v=P[k];ax[1].plot(v['ci95'],[i,i],lw=5,color=c);ax[1].scatter(v['delta_mse'],i,s=100,color=c,zorder=3)
ax[1].set(yticks=[0,1],yticklabels=['Primary · linear','Exploratory · forest'],xlabel='Baseline MSE − motion MSE · squared yards',title='GAIN IS TO THE RIGHT OF ZERO');ax[1].axvline(0,color='#9bb0c5',ls=':');ax[1].grid(alpha=.12)
fig.suptitle('Observed 2025 holdout · 17 receivers · 1,737 routes',fontsize=19,fontweight='bold');fig.savefig(receipt/'heldout_results.png',dpi=150);plt.close(fig)
fig,ax=plt.subplots(1,2,figsize=(16,5),layout='constrained');windows=[r['smoothing_frames'] for r in S['smoothing_sensitivity']];err=[r['test_rmse_yards'] for r in S['smoothing_sensitivity']];base=R['results'][0]['test_rmse_yards'];ax[0].plot(windows,err,'o-',color='#efb455',lw=3);ax[0].axhline(base,color='#39dbbd',ls='--',label='Conventional baseline');ax[0].set(xticks=windows,xlabel='Smoothing window · 10 Hz frames',ylabel='Held-out RMSE · yards',title='THE NEGATIVE RESULT SURVIVES SMOOTHING');ax[0].legend(facecolor='#102236',labelcolor='#e6edf6')
null=S['development_player_block_permutation']['test_mse_values'];ax[1].hist(null,bins=12,color='#8298b0',alpha=.8);ax[1].axvline(R['results'][1]['test_player_balanced_mse'],color='#efb455',lw=3,label='Observed motion model');ax[1].axvline(R['results'][0]['test_player_balanced_mse'],color='#39dbbd',ls='--',label='Conventional baseline');ax[1].set(xlabel='Test MSE · squared yards',ylabel='Permutations',title='PLAYER-BLOCK SHUFFLE · DIAGNOSTIC ONLY');ax[1].legend(facecolor='#102236',labelcolor='#e6edf6');fig.suptitle('Post-primary diagnostics · test reused for checks, never model selection',fontsize=16);fig.savefig(receipt/'sensitivity_results.png',dpi=150);plt.close(fig)
fig,ax=plt.subplots(1,2,figsize=(16,5),layout='constrained');allwr=[38,31,37];kept=[M['draft_class_players'][str(y)] for y in [2023,2024,2025]];x=np.arange(3);ax[0].bar(x-.18,allwr,.36,label='WR prospects',color='#8298b0');ax[0].bar(x+.18,kept,.36,label='Eligible study players',color='#39dbbd');ax[0].set(xticks=x,xticklabels=['2023 · train','2024 · tune','2025 · test'],ylabel='Players',title='PLAYS ARE NOT INDEPENDENT PROSPECTS');ax[0].legend(facecolor='#102236',labelcolor='#e6edf6');ax[1].bar(['Targeted','Not targeted'],[0,100*O['missing_by_target']['false']],color=['#39dbbd','#efb455']);ax[1].set(ylabel='Missing separation · %',title='OUTCOME COVERAGE IS UNEVEN');fig.suptitle('Observed selection and measurement coverage',fontsize=18);fig.savefig(receipt/'population_and_missingness.png',dpi=150);plt.close(fig)
a=pd.read_csv(out/'attempt_features.csv');c=a[a.drill_name.eq(M['selected_drill'])].groupby('nfl_id')[['entry_speed','speed_retention','exit_gain','turn_angle']].median();g=pd.read_csv(out/'private_game_motion.csv').groupby('nfl_id')[['entry_speed','speed_retention','exit_gain','turn_angle']].median();j=c.join(g,lsuffix='_combine',rsuffix='_game',how='inner');from scipy.stats import spearmanr
fig,ax=plt.subplots(2,2,figsize=(12,9),layout='constrained')
for z,k,label in zip(ax.ravel(),['entry_speed','speed_retention','exit_gain','turn_angle'],['Entry speed · yd/s','Speed retention · ratio','Exit gain · yd/s','Turn angle · radians']):
 rho=spearmanr(j[k+'_combine'],j[k+'_game']).statistic;z.scatter(j[k+'_combine'],j[k+'_game'],color='#39dbbd',alpha=.75,s=35);z.set(xlabel='Combine '+label,ylabel='Game '+label,title=f'Spearman ρ = {rho:.3f}');z.grid(alpha=.12)
fig.suptitle(f'Do the mechanics travel? · {len(j)} receivers · descriptive check',fontsize=17);fig.savefig(receipt/'mechanics_transfer.png',dpi=150);plt.close(fig)
# Aggregate-only receipts: no IDs, per-play predictions, or raw tracking.
for name in ['inventory.json','experiment_results.json','followup_checks.json','paired_model_intervals.json','outcome_missingness.json','mechanics_transfer.json','game_transfer_summary.json']:
 (receipt/name).write_bytes((out/name).read_bytes())
M['excluded_attempts']={'no_qualifying_turn':len(M.pop('excluded_attempts'))};(receipt/'population_audit.json').write_text(json.dumps(M,indent=2))
(receipt/'acquisition.json').write_bytes((root/'data'/'acquisition.json').read_bytes())
print('Rendered four aggregate figures and saved source hashes/results; raw data and per-player files excluded')
