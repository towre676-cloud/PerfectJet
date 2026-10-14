"""Four aggregate football-facing figures; no player identities or predictions."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import burst_transfer as B
OUT=Path('receipts/burst')
def render():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f6f8fb','axes.facecolor':'#f6f8fb','axes.titleweight':'bold'})
    rows=pd.read_pickle('private_burst/private_rows_1.0.pkl');source=pd.read_pickle('private_burst/private_attempts.pkl')
    fig,axes=plt.subplots(1,2,figsize=(13,5),constrained_layout=True)
    h=axes[0].hist2d(rows.onset,rows.travel1,bins=[np.linspace(0,1.5,31),np.linspace(.1,1.2,23)],cmap='Blues',cmin=1);fig.colorbar(h[3],ax=axes[0],label='NFL records / bin');axes[0].set(xlabel='Snap → sustained-speed onset (seconds)',ylabel='Onset → next geometric yard (seconds)',title='Waiting and traveling are different measurements')
    for field,label,color in [('onset','Operational onset','#d06852'),('travel1','One-yard travel','#1b8b80'),('total1','Combined time','#304f85')]:axes[1].hist(rows[field],bins=np.linspace(0,2,41),density=True,histtype='step',linewidth=2,label=label,color=color)
    axes[1].set(xlabel='Seconds',ylabel='Record density',title='14,057 NFL records · 74 players');axes[1].legend()
    fig.suptitle('Separate the movement cue from the physical burst\nThe cue is an operational speed gate, not annotated reaction time',fontsize=17);fig.savefig(OUT/'onset_and_travel.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(13,5),constrained_layout=True)
    drills=sorted(source.drill.unique());labels=[s.replace('_DRILL','').replace('FRONT_START_WAVE_AND_LATERAL_REACTION','LATERAL').replace('_',' ').title() for s in drills]
    groups=[source[source.drill.eq(d)].travel1 for d in drills]
    axes[0].boxplot(groups,tick_labels=labels,showfliers=False,orientation='horizontal');axes[0].set(xlabel='Post-onset one-yard travel (seconds)',title='Combine bursts · 467 attempts')
    metric=source.groupby('nfl_id').travel1.median();game=rows.groupby('nfl_id').travel1.mean();q=pd.DataFrame({'source':metric,'game':game}).dropna()
    h=axes[1].hist2d(q.source,q.game,bins=9,cmap='Blues',cmin=1);fig.colorbar(h[3],ax=axes[1],label='Players / bin');axes[1].set(xlabel='Median Combine travel (seconds)',ylabel='Mean NFL travel (seconds)',title='Unadjusted relationship · not predictive lift')
    fig.suptitle('Similar physical measurements do not guarantee the same game response',fontsize=17);fig.savefig(OUT/'source_and_game.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(13,5),constrained_layout=True)
    for family,marker in [('burst','o'),('repeat_precision','s')]:
        gains=[]
        for seed in [B.SEED,B.SEED+200,B.SEED+400]:gains.append(json.loads((OUT/f'burst_travel1_1.0_{seed}.json').read_text())['development']['comparisons'][family]['relative_gain']*100)
        axes[0].plot([1,2,3],gains,marker=marker,label=family.replace('_',' '))
    axes[0].axhline(0,color='#303d50');axes[0].set(xticks=[1,2,3],xlabel='Earlier-player partition',ylabel='Error reduction (%)',title='Primary travel comparison');axes[0].legend()
    comparisons=[]
    for target,threshold,label in [('burst_travel1',.5,'Travel / 0.5 gate'),('burst_travel1',1.,'Travel / 1.0 gate'),('burst_travel1',2.,'Travel / 2.0 gate'),('burst_onset',1.,'Onset / 1.0 gate')]:
        r=json.loads((OUT/f'{target}_{threshold}_{B.SEED}.json').read_text());comparisons.append((label,r['exploratory_2025']['comparisons']['burst']['relative_gain']*100,r['exploratory_2025']['comparisons']['repeat_precision']['relative_gain']*100))
    y=np.arange(len(comparisons));axes[1].barh(y-.15,[x[1] for x in comparisons],height=.3,label='burst');axes[1].barh(y+.15,[x[2] for x in comparisons],height=.3,label='repeat precision');axes[1].axvline(0,color='#303d50');axes[1].set(yticks=y,yticklabels=[x[0] for x in comparisons],xlabel='Error reduction (%)',title='Exploratory 2025 · all definitions retained');axes[1].legend()
    fig.suptitle('Does observed burst motion add information beyond conventional scouting?',fontsize=17);fig.savefig(OUT/'prediction_results.png',dpi=160);plt.close(fig)
    repeat=json.loads((OUT/'repeatability.json').read_text())['game_half_rank_quantiles'];support=json.loads((OUT/'readout_support.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(13,5),constrained_layout=True)
    names=['onset','travel1','total1','player_get_off'];values=[repeat[n] for n in names]
    axes[0].errorbar(np.arange(4),[v[1] for v in values],yerr=[[v[1]-v[0] for v in values],[v[2]-v[1] for v in values]],fmt='o',color='#304f85',capsize=6);axes[0].set(xticks=np.arange(4),xticklabels=['Onset','Travel','Combined','Charted get-off'],ylabel='Player rank correlation across game halves',ylim=(0,1),title='Median and split range · 200 game splits')
    axes[1].bar(['Own observed mean','Shared reference mean'],[support['own_empirical_mean_identified'],support['earlier_reference_identified']],color=['#1b8b80','#d06852']);axes[1].set(ylabel='Player/drill panels with identified scalar',ylim=(0,support['panels']*1.1),title='Exact row-space test · 278 panels')
    fig.suptitle('Measure a supported response before extrapolating a scouting curve',fontsize=17);fig.savefig(OUT/'repeatability_and_support.png',dpi=160);plt.close(fig)
if __name__=='__main__':render()
