"""Aggregate canonical comparison and training-uncertainty figures."""
from pathlib import Path
import json,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LABELS={'onset_summaries':'Onset summaries','duration_kinematic':'Kinematics','duration_ordered':'Order signatures','duration_uncertain':'Phase uncertainty','duration_combined':'Duration combined','merged':'Both feature sets','selected':'Training-selected model'}

def render(out='receipts/canonical'):
    out=Path(out);out.mkdir(exist_ok=True);r=json.loads(Path('private_canonical/results.json').read_text());rep=json.loads(Path('receipts/canonical/repeated_partitions.json').read_text());refit=json.loads(Path('receipts/canonical/refits.json').read_text());families=list(LABELS)
    fig,axes=plt.subplots(1,2,figsize=(14,5.5),layout='constrained')
    for ax,split,title in zip(axes,['development','exploratory_2025'],['Earlier classes ·45 athletes','2025 ·29 athletes ·exploratory']):
        for i,f in enumerate(families):
            c=r[split]['comparisons'][f];lo,hi=np.array(c['athlete_bootstrap_95'])*1e4;ax.plot([lo,hi],[i,i],color='#64748b',lw=2);ax.scatter(c['absolute_gain']*1e4,i,color='#b45309' if f=='duration_combined' else '#0284c7',s=42,zorder=3)
        ax.axvline(0,color='#111827',ls='--',lw=1);ax.set_yticks(range(len(families)),[LABELS[f] for f in families]);ax.invert_yaxis();ax.set_title(title);ax.set_xlabel('Error reduction against same scouting baseline (MSE ×10⁻⁴)');ax.grid(axis='x',alpha=.15)
    fig.suptitle('Two engines, one player population and one scouting-input comparison',fontsize=15);fig.savefig(out/'common_comparison.png',dpi=150,bbox_inches='tight');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained');x=np.arange(3);g=rep['families']['duration_combined']['split_relative_gains'];s=rep['families']['selected']['split_relative_gains'];axes[0].plot(x,np.array(g)*100,'o-',color='#b45309',label='Duration combined');axes[0].plot(x,np.array(s)*100,'s--',color='#0284c7',label='Training-selected');axes[0].axhline(0,color='#111827',lw=1);axes[0].set_xticks(x,['Partition1','Partition2','Partition3']);axes[0].set_ylabel('Relative error reduction (%)');axes[0].set_title('Earlier players reused in three partitions');axes[0].legend(frameon=False)
    axes[1].hist(np.array(refit['joint_training_test_delta'])*1e4,bins=30,color='#0284c7',alpha=.8);axes[1].axvline(0,color='#111827',ls='--',lw=1);observed=r['exploratory_2025']['comparisons']['duration_combined']['absolute_gain']*1e4;axes[1].axvline(observed,color='#b45309',lw=2,label='Observed forward gain');axes[1].set_xlabel('Refit +test-resample error reduction (MSE ×10⁻⁴)');axes[1].set_ylabel('Bootstrap replicates');axes[1].set_title('512 training-player refits; configurations fixed');axes[1].legend(frameon=False)
    fig.suptitle('A positive point estimate still needs stable transport',fontsize=15);fig.savefig(out/'stability_and_refits.png',dpi=150,bbox_inches='tight');plt.close(fig)
    events=pd.read_pickle('private_canonical_vendor/events.pkl');drills=list(events.drill_name.unique());fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained');names=['Pass rush' if 'PASS_RUSH' in d else 'Hoop' if 'HOOP' in d else 'Four-bag' if 'FOUR_BAG' in d else 'Lateral reaction' for d in drills];width=.18
    for phase in range(3):
        values=[events.loc[events.drill_name.eq(d),f'phase_boundary_width_{phase}'].median() for d in drills];ax.bar(np.arange(len(drills))+(phase-1)*width,values,width,label=['Approach→brake','Brake→redirect','Redirect→recover'][phase])
    ax.set_xticks(range(len(drills)),names);ax.set_ylabel('Median assumed 5–95% boundary width (seconds)');ax.set_title('Boundary ambiguity measured on actual Combine attempts');ax.legend(frameon=False,ncol=3,loc='upper center',bbox_to_anchor=(.5,-.08));ax.grid(axis='y',alpha=.15);fig.savefig(out/'boundary_ambiguity.png',dpi=150,bbox_inches='tight');plt.close(fig)
if __name__=='__main__':render()
