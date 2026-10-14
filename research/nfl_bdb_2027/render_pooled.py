"""Aggregate figures; no player identities or individual predictions exported."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import front_transfer as F
import pooled_transfer as P

OUT=Path('receipts/pooled')
def render():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f6f8fb','axes.facecolor':'#f6f8fb','axes.titleweight':'bold'})
    turns=pd.read_pickle('private_stress_clock/private_turns.pkl')
    fig,axes=plt.subplots(2,2,figsize=(13,8),constrained_layout=True)
    names=['Pass rush','Run the hoop','Four-bag agility','Lateral reaction']
    for ax,drill,name in zip(axes.ravel(),F.DRILLS,names):
        g=turns[turns.drill.eq(drill)]
        h=ax.hist2d(g.entry,g.angle*180/np.pi,bins=[np.linspace(2,7,16),np.linspace(30,170,16)],cmap='Blues',cmin=1)
        ax.set(title=f'{name} · {len(g)} turns',xlabel='Entry speed (yards/second)',ylabel='Direction change (degrees)')
        fig.colorbar(h[3],ax=ax,label='Recorded turns / demand bin')
    fig.suptitle('A scouting curve needs more than repeated frames\nObserved demands are sparse and differ across drills',fontsize=18)
    fig.savefig(OUT/'demand_geometry.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(15,5),constrained_layout=True)
    for ax,prefix,title in zip(axes,['results','schur','getoff'],['Pooled pressure model','Isolated motion corrections','Supporting get-off model']):
        for label,marker in zip((['capacity','duration','pooled','duration_pooled'] if prefix!='schur' else ['capacity','duration','pooled','class_guard']),['o','s','^','D']):
            ys=[]
            for seed in [P.SEED,P.SEED+200,P.SEED+400]:
                r=json.loads((OUT/f'{prefix}_{seed}.json').read_text())
                comp=r['development'].get('versus_conventional',r['development'].get('comparisons'))
                ys.append(comp[label]['relative_gain']*100)
            ax.plot([1,2,3],ys,marker=marker,label=label.replace('_',' '))
        ax.axhline(0,color='#303d50',linewidth=1);ax.set(title=title,xlabel='Repeated player partition',ylabel='Prediction error reduction (%)',xticks=[1,2,3]);ax.legend(fontsize=8)
    fig.suptitle('Does movement add value in earlier players?\nPositive means less error; the same athletes recur across partitions',fontsize=17)
    fig.savefig(OUT/'model_stability.png',dpi=160);plt.close(fig)
    r=json.loads((OUT/'canonical_stability.json').read_text());gains=[x['development']['comparisons']['duration_combined']['relative_gain']*100 for x in r['results']]
    fig,axes=plt.subplots(1,2,figsize=(13,5),constrained_layout=True)
    axes[0].bar(np.arange(1,13),gains,color=['#1b8b80' if x>0 else '#d06852' for x in gains]);axes[0].axhline(0,color='#303d50');axes[0].set(title='Duration lead: expanded audit',xlabel='Declared partition',ylabel='Prediction error reduction (%)',xticks=np.arange(1,13))
    pressure=json.loads((OUT/'outcome_repeatability.json').read_text())['rank_correlation_quantiles'];getoff=json.loads((OUT/'getoff_repeatability.json').read_text())['rank_correlation_quantiles']
    axes[1].errorbar([0,1],[pressure[1],getoff[1]],yerr=[[pressure[1]-pressure[0],getoff[1]-getoff[0]],[pressure[2]-pressure[1],getoff[2]-getoff[1]]],fmt='o',markersize=9,color='#304f85',capsize=7)
    axes[1].set(title='How stable is the recorded game response?',xticks=[0,1],xticklabels=['Pressure rate','Charted get-off'],ylabel='Rank correlation across game halves',ylim=(0,1));axes[1].text(.5,.05,'Median and 2.5–97.5% range over 200 game splits\nA sensitivity range, not an accuracy ceiling',ha='center',transform=axes[1].transAxes,fontsize=9)
    fig.suptitle('A favorable partition is a hypothesis, not a scouting guarantee',fontsize=18)
    fig.savefig(OUT/'signal_and_outcome.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(13,5),constrained_layout=True)
    for ax,prefix,title in zip(axes,['results','getoff'],['Pressure rate · 29 evaluated players','Charted get-off · 29 evaluated players']):
        r=json.loads((OUT/f'{prefix}_{P.SEED}.json').read_text());comp=r['exploratory_2025']['versus_conventional'];labels=['capacity','duration','pooled','duration_pooled'];g=[comp[k]['relative_gain']*100 for k in labels]
        ax.barh(np.arange(4),g,color=['#1b8b80' if x>0 else '#d06852' for x in g]);ax.axvline(0,color='#303d50');ax.set(title=title,yticks=np.arange(4),yticklabels=[k.replace('_',' ') for k in labels],xlabel='Prediction error reduction (%)')
    fig.suptitle('Exploratory 2025 results\nThis class has already informed the research program',fontsize=18)
    fig.savefig(OUT/'forward_results.png',dpi=160);plt.close(fig)
if __name__=='__main__':render()
