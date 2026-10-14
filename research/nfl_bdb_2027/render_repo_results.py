from pathlib import Path
import json
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).parent;src=root/'private_repo_results';matched=root/'private_repo_matched';out=root/'receipts'/'repo_push';out.mkdir(exist_ok=True)
r=json.loads((src/'cohort_trial.json').read_text());n=json.loads((src/'nested_development.json').read_text());m=json.loads((matched/'route_matched_trial.json').read_text());old=json.loads((root/'private_results'/'experiment_results.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':'#e6edf6','axes.labelcolor':'#c2cfde','xtick.color':'#9bb0c5','ytick.color':'#9bb0c5','axes.edgecolor':'#304359','axes.facecolor':'#102236','figure.facecolor':'#071421'})
fig,ax=plt.subplots(1,2,figsize=(18,6),layout='constrained');v=[old['results'][4]['test_rmse_yards'],r['selected']['baseline']['test_rmse_yards'],r['selected']['all']['test_rmse_yards']];ax[0].barh(['Original forest','Strengthened conventional','Full repo-motion model'],v,color=['#8298b0','#39dbbd','#efb455']);ax[0].invert_yaxis();ax[0].set(xlabel='Exploratory 2025 RMSE · yards',title='IMPROVEMENT OVER THE PREVIOUS VERSION',xlim=(0,1.95))
for i,value in enumerate(v):ax[0].text(value+.025,i,f'{value:.3f}',va='center')
intervals=[n['paired_improvement'],r['selected']['all']['paired_vs_strong_conventional'],m['nested_earlier_data']['paired_improvement'],m['paired_improvement']];labels=['Multi-drill · nested earlier players','Multi-drill · exploratory 2025','Route-matched · nested earlier players','Route-matched · exploratory 2025']
for i,entry in enumerate(intervals):ax[1].plot(entry['ci95'],[i,i],lw=5,color='#39dbbd' if i%2==0 else '#efb455');ax[1].scatter(entry['delta_mse'],i,s=80,color='#39dbbd' if i%2==0 else '#efb455')
ax[1].set(yticks=range(4),yticklabels=labels,xlabel='Conventional − motion MSE · squared yards',title='INCREMENTAL MOTION VALUE REMAINS UNCERTAIN');ax[1].axvline(0,color='#9bb0c5',ls=':');ax[1].grid(alpha=.12);fig.suptitle('Geometry + ordered paths + velocity memory + prospect-balanced compression',fontsize=18);fig.savefig(out/'repo_prediction_results.png',dpi=150);plt.close(fig)
for name in ['cohort_trial.json','nested_development.json','feature_audit.json','team_cluster_diagnostic.json']:(out/name).write_bytes((src/name).read_bytes())
(out/'route_matched_trial.json').write_bytes((matched/'route_matched_trial.json').read_bytes());(out/'route_matched_feature_audit.json').write_bytes((matched/'feature_audit.json').read_bytes())
print('Saved aggregate receipts and comparison figure')
