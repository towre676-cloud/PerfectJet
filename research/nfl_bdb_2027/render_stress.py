"""Aggregate geometric recovery, demand support, prediction and observability plots."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import stress_features as S,stress_transfer as T

NAMES=['Pass rush','Hoop','Four-bag agility','Lateral reaction']

def render(out='receipts/stress'):
    out=Path(out);out.mkdir(exist_ok=True);turns=pd.read_pickle('private_stress_clock/private_turns.pkl');d=pd.read_pickle('private_stress_clock/private_rows.pkl');units=T.unit_rows(d).merge(pd.read_pickle('private_stress_clock/private_capacity.pkl'),on='nfl_id',how='left');train=units[units.draft_year.isin([2023,2024])];enc=S.StressEncoder(turns).fit(train)
    fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
    for ax,drill,title in zip(axes.flat,S.F.DRILLS,NAMES):
        g=turns[turns.drill.eq(drill)];paths=[];clocks=[]
        for row in g.itertuples():
            paths.append(np.mean([b['path'] for b in row.branches],axis=0));clocks.append(np.mean([b['recovery_start']-(row.center+b['shift'])+7 for b in row.branches]))
        p=np.mean(paths,axis=0);clock=float(np.mean(clocks));index=np.arange(len(p));segments=np.stack([p[:-1],p[1:]],axis=1);line=LineCollection(segments,cmap='viridis',norm=plt.Normalize(-.7,1.3),linewidth=4);line.set_array((index[:-1]-7+.5)*.1);ax.add_collection(line);ax.scatter(*p[int(round(clock))],marker='D',color='#b45309',s=45,label='Mean 80% rotation crossing');ax.scatter(*p[0],color='#111827',s=25);ax.autoscale();ax.set_aspect('equal',adjustable='datalim');ax.set_title(f'{title} · {len(g)} turns');ax.set_xlabel('Along entry heading (yards)');ax.set_ylabel('Lateral (yards)');ax.grid(alpha=.15);ax.legend(frameon=False,fontsize=8)
    fig.colorbar(line,ax=axes.ravel().tolist(),shrink=.65,label='Seconds from operational turn center');fig.suptitle('Recover after completing the direction change',fontsize=16);fig.savefig(out/'recovery_geometry.png',dpi=160,bbox_inches='tight');plt.close(fig)
    grid_s=np.linspace(2,5,45);grid_a=np.linspace(np.deg2rad(30),np.deg2rad(170),45);ss,aa=np.meshgrid(grid_s,grid_a);reference=train.iloc[[0]].copy();reference['nfl_id']=-999
    for c in S.R.PHYS+['sprint__ceiling','sprint__speed1','sprint__speed3']:reference[c]=train[c].median()
    fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
    for ax,drill,title in zip(axes.flat,S.F.DRILLS,NAMES):
        events=pd.DataFrame({'nfl_id':-999,'drill':drill,'entry':ss.ravel(),'angle':aa.ravel()});prediction=enc.model.predict(enc.scale.transform(enc._unscaled(events,reference)))[:,0].reshape(ss.shape);source=turns[turns.nfl_id.isin(train.nfl_id)&turns.drill.eq(drill)];supported=np.zeros(ss.shape,bool)
        for i in range(ss.shape[0]):
            for j in range(ss.shape[1]):supported[i,j]=source.loc[(np.abs(source.entry-ss[i,j])<.6)&(np.abs(source.angle-aa[i,j])<.4),'nfl_id'].nunique()>=5
        prediction=np.ma.masked_where(~supported,prediction);image=ax.pcolormesh(ss,aa*180/np.pi,prediction,cmap='viridis',vmin=.2,vmax=1.4,shading='auto');ax.set_facecolor('#e2e8f0');ax.set_title(title);ax.set_xlabel('Entry speed (yards/s)');ax.set_ylabel('Turn angle (degrees)')
    fig.colorbar(image,ax=axes.ravel().tolist(),shrink=.65,label='Fitted normalized recovery ·reference body');fig.suptitle('Demand-response surface: gray regions lack source support',fontsize=15);fig.savefig(out/'stress_surface.png',dpi=160,bbox_inches='tight');plt.close(fig)
    families=['capacity_only','raw_motion','matched_recovery','stress_curve','robust_recovery','selected'];names=['Sprint capacity','Raw movement','Matched recovery','Stress slope','Ambiguity/repeats','Training-selected'];fig,axes=plt.subplots(1,2,figsize=(14,5.5),layout='constrained');r=json.loads(Path('private_stress_capacity_controlled/pressure_event/results.json').read_text())
    for ax,split,title in zip(axes,['development','exploratory_2025'],['Earlier 45 players','2025: 29 players · exploratory']):
        for i,f in enumerate(families):
            v=r[split]['comparisons'][f];lo,hi=np.array(v['conditional_ci95'])*1e4;ax.plot([lo,hi],[i,i],color='#64748b',lw=2);ax.scatter(v['absolute_gain']*1e4,i,color='#b45309' if f=='capacity_only' else '#0284c7',s=45)
        ax.axvline(0,color='#111827',ls='--',lw=1);ax.set_yticks(range(len(names)),names);ax.invert_yaxis();ax.set_title(title);ax.set_xlabel('Context-adjusted pressure error reduction (MSE ×10⁻⁴)');ax.grid(axis='x',alpha=.15)
    fig.suptitle('Context-adjusted pressure: test capacity and recovery separately',fontsize=15);fig.savefig(out/'scouting_results.png',dpi=160,bbox_inches='tight');plt.close(fig)
    m=json.loads((out/'measurement.json').read_text());o=json.loads((out/'observability.json').read_text());fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained');axes[0].bar(['Fixed offset','Angular progress'],[m['initial_median_width'],m['clock_median_width']],color=['#64748b','#0284c7']);axes[0].set_ylabel('Median recovery sensitivity span');axes[0].set_title(f"Same 582 turns · {m['median_width_reduction']*100:.1f}% smaller span");counts=o['rank_counts'];axes[1].bar(list(counts),list(counts.values()),color=['#64748b','#64748b','#64748b','#b45309']);axes[1].set_xlabel('Observed bilinear demand-design rank');axes[1].set_ylabel('Player/drill panels');axes[1].set_title('Four coefficients need four independent demands');fig.suptitle('A more stable readout and a map of missing trial conditions',fontsize=15);fig.savefig(out/'measurement_and_observability.png',dpi=160,bbox_inches='tight');plt.close(fig)
if __name__=='__main__':render()
