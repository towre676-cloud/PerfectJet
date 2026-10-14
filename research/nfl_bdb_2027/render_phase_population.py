"""Aggregate movement geometry and uncertainty figures; no player identities."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.signal import savgol_filter
import phase_population as P,front_transfer as F

def geometry(data='data',out='receipts/phase_population'):
    out=Path(out);out.mkdir(exist_ok=True);d=pd.read_pickle('private_front/private_rows.pkl');tr=pd.read_csv(Path(data)/'combine_tracking.csv');tr=tr[tr.entity_type.eq('PLAYER')&tr.nfl_id.isin(d.nfl_id)&tr.drill_name.isin(F.DRILLS)]
    fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained');grid=np.linspace(0,1,51);audit={}
    titles=['Pass rush','Run the hoop','Four-bag agility','Lateral reaction']
    for ax,drill,title in zip(axes.flat,F.DRILLS,titles):
        curves=[];recover=[];spreads=[]
        for _,g in tr[tr.drill_name.eq(drill)].groupby(['nfl_id','event_id']):
            g=g.sort_values('time');positions=[];probs=[]
            for onset in P.ONSETS:
                try:z,start=P.channels(g,onset)
                except ValueError:continue
                xy=savgol_filter(g[['x','y']].to_numpy(float)[start:start+len(z)],7,3,axis=0);xy-=xy[0];v=xy[min(8,len(xy)-1)]
                if np.linalg.norm(v)<.2:continue
                angle=np.arctan2(v[1],v[0]);rotation=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]);xy=xy@rotation
                if xy[-1,1]<0:xy[:,1]*=-1
                path=np.c_[np.interp(grid,np.linspace(0,1,len(xy)),xy[:,0]),np.interp(grid,np.linspace(0,1,len(xy)),xy[:,1])];positions.append(path)
                probs.append(np.mean([np.interp(grid,np.linspace(0,1,len(z)),P.phase_population(z,t)[1][:,3]) for t in P.TEMPERATURES],axis=0))
            if positions:curves.append(np.mean(positions,axis=0));recover.append(np.mean(probs,axis=0));spreads.append(np.std(positions,axis=0))
        mean=np.mean(curves,axis=0);sd=np.mean(spreads,axis=0);color=np.mean(recover,axis=0);segments=np.stack([mean[:-1],mean[1:]],axis=1);line=LineCollection(segments,cmap='viridis',norm=plt.Normalize(0,1),linewidth=4);line.set_array((color[:-1]+color[1:])/2);ax.add_collection(line)
        ax.plot(mean[:,0]+sd[:,0],mean[:,1]+sd[:,1],color='gray',alpha=.5,lw=1);ax.plot(mean[:,0]-sd[:,0],mean[:,1]-sd[:,1],color='gray',alpha=.5,lw=1);ax.scatter(*mean[0],color='#111827',s=24);ax.autoscale();ax.set_aspect('equal',adjustable='datalim');ax.set_title(f'{title} · {len(curves)} attempts');ax.set_xlabel('Forward travel (yards)');ax.set_ylabel('Lateral travel (yards)');ax.grid(alpha=.15);audit[drill]={'attempts':len(curves),'mean_onset_coordinate_sd_yd':float(np.mean(sd))}
    fig.colorbar(line,ax=axes.ravel().tolist(),shrink=.7,label='Assumed recovery-phase occupancy');fig.suptitle('A movement profile is a population of possible alignments',fontsize=16);fig.savefig(out/'phase_geometry.png',dpi=160);plt.close(fig)
    (out/'geometry.json').write_text(json.dumps({'drills':audit,'scope':'Mean onset-averaged first-up-to-5s trajectories; initial approach rotated forward and final lateral direction reflected positive, normalized elapsed window. Gray coordinate-wise mean onset SD curves are sensitivity guides, not confidence bands. Recovery color follows assumed phase language, not validated semantic labels.'},indent=2))

def results(out='receipts/phase_population',source='private_phase_population',title='Does ordering add information beyond the same movement summaries?'):
    out=Path(out);r=json.loads((Path(source)/'results.json').read_text());fig,axes=plt.subplots(1,2,figsize=(14,5.2),layout='constrained');labels=['Summaries','Sequence','Shuffled order'];keys=['conventional->summaries','conventional->sequence','conventional->shuffled','summaries->sequence','shuffled->sequence'];names=['Summaries vs baseline','Sequence vs baseline','Shuffled vs baseline','Sequence vs summaries','Sequence vs shuffled']
    for ax,split,subtitle in zip(axes,['nested','exploratory_2025'],['Earlier classes · 45 athletes','2025 · 29 athletes · exploratory']):
        for i,key in enumerate(keys):
            c=r[split]['comparisons'][key];delta=c['delta_mse']*1e4;lo,hi=np.array(c['ci95'])*1e4;ax.plot([lo,hi],[i,i],color='#64748b',lw=2);ax.scatter(delta,i,color='#0284c7' if i<3 else '#b45309',s=45,zorder=3)
        ax.axvline(0,color='#111827',ls='--',lw=1);ax.set_yticks(range(len(keys)),names);ax.invert_yaxis();ax.set_xlabel('Reduction in player-rate MSE ×10⁻⁴');ax.set_title(subtitle);ax.grid(axis='x',alpha=.15)
    fig.suptitle(title,fontsize=15);fig.savefig(out/'phase_comparisons.png',dpi=160,bbox_inches='tight');plt.close(fig)
if __name__=='__main__':geometry();results()
