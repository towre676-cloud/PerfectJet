"""Aggregate geometric figures and uncertainty for the scouting entry."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.signal import savgol_filter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import front_transfer as F

def geometry(data):
    p=pd.read_csv(Path(data)/'players.csv');ids=set(p.loc[p.nfl_position.isin(F.POSITIONS),'nfl_id']);t=pd.read_csv(Path(data)/'combine_tracking.csv');t=t[t.nfl_id.isin(ids)&t.entity_type.eq('PLAYER')&t.drill_name.isin(F.DRILLS)];paths={k:[] for k in F.DRILLS};speeds={k:[] for k in F.DRILLS}
    for _,g in t.groupby(['nfl_id','event_id'],sort=True):
        g=g.sort_values('time');s=g.s.to_numpy();on=next((i for i in range(len(s)-2) if np.all(s[i:i+3]>.5)),None)
        if on is None or len(s)-on<16:continue
        q=savgol_filter(g[['x','y']].to_numpy(float)[on:on+51],7,3,axis=0);q-=q[0];u=q[min(5,len(q)-1)].copy();u/=max(np.linalg.norm(u),1e-9);q=q@np.array([[u[0],-u[1]],[u[1],u[0]]]);q[:,1]*=1 if q[:,1].mean()>=0 else -1;arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(q,axis=0),axis=1))];arc/=max(arc[-1],1e-9);progress=np.linspace(0,1,51);paths[g.drill_name.iloc[0]].append(np.c_[np.interp(progress,arc,q[:,0]),np.interp(progress,arc,q[:,1])]);speeds[g.drill_name.iloc[0]].append(np.interp(progress,arc,s[on:on+51]))
    return {k:{'attempts':len(v),'mean_xy':np.mean(v,axis=0).tolist(),'mean_speed':np.mean(speeds[k],axis=0).tolist()} for k,v in paths.items()}

def render(data,out,front,diagnostics):
    out=Path(out);out.mkdir(exist_ok=True);plt.rcParams.update({'font.family':'DejaVu Sans','figure.dpi':140,'axes.spines.top':False,'axes.spines.right':False});geom=geometry(data);(out/'geometry_aggregate.json').write_text(json.dumps(geom,indent=2));fig,axes=plt.subplots(2,2,figsize=(11,8));titles={'PASS_RUSH_DRILL':'Pass-rush drill','RUN_THE_HOOP_DRILL':'Run the hoop','FOUR_BAG_AGILITY_DRILL':'Four-bag agility','FRONT_START_WAVE_DRILL_AND_LATERAL_REACTION':'Start, wave and lateral reaction'}
    for ax,(name,g) in zip(axes.flat,geom.items()):
        q=np.array(g['mean_xy']);s=np.array(g['mean_speed']);segments=np.stack([q[:-1],q[1:]],axis=1);lc=LineCollection(segments,cmap='viridis',norm=plt.Normalize(0,8),linewidth=4);lc.set_array((s[:-1]+s[1:])/2);ax.add_collection(lc);ax.autoscale();ax.scatter(*q[0],color='#222',marker='o');ax.scatter(*q[-1],color='#222',marker='>');ax.set_aspect('equal',adjustable='datalim');ax.set(xlabel='Along initial direction (yards)',ylabel='Lateral movement (yards)');ax.set_title(f"{titles[name]}\n{g['attempts']} attempts",fontsize=11);ax.grid(alpha=.12)
    fig.subplots_adjust(top=.86,hspace=.55,wspace=.38,right=.84);cax=fig.add_axes([.90,.2,.025,.55]);fig.colorbar(lc,cax=cax,label='Mean tracked speed (yd/s)');fig.suptitle('Combine movement geometry: aligned mean paths\nFirst 5 seconds after sustained motion onset; arc-progress alignment, mirrored turns',fontsize=12);fig.savefig(out/'01_drill_geometry.png',bbox_inches='tight');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    for ax,metric in zip(axes,['play','player']):
        rows=[]
        for split in ['nested','exploratory_2025']:
            bank=front['pressure_event'][split] if metric=='play' else diagnostics['scouting_rates'][split]
            for family in ['sprint','skills','combined']:rows.append((family+' / '+('earlier players' if split=='nested' else '2025'),bank['comparisons'][family]))
        means=np.array([v['delta_mse'] for _,v in rows]);bounds=np.array([v['ci95'] for _,v in rows]);ax.errorbar(means,np.arange(len(rows)),xerr=np.maximum(0,np.c_[means-bounds[:,0],bounds[:,1]-means].T),fmt='o',capsize=3,color='#176b8c');ax.axvline(0,color='gray',lw=1);ax.set_yticks(range(len(rows)),[name for name,_ in rows]);ax.invert_yaxis();ax.set_xlabel('Conventional MSE minus tracking MSE');ax.set_title('Individual rush records' if metric=='play' else 'Player pressure-rate estimates (secondary)')
    fig.suptitle('Where the candidate scouting gain appears: same predictions, two questions');fig.tight_layout();fig.savefig(out/'02_pressure_uncertainty.png',bbox_inches='tight');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4));ctrl=diagnostics['profile_controls'];axes[0].hist(ctrl['within_position_shuffled_mse'],bins=12,color='#8fb5c5');axes[0].axvline(ctrl['real_mse'],color='#aa4030',lw=2,label='Real profiles');axes[0].set(xlabel='Player pressure-rate MSE',ylabel='Profile shuffles',title='Whole held-out profiles swapped within position');axes[0].legend();rr=diagnostics['development_repeated_partitions'];means=[]
    for row in rr['details']:means.append(row['comparisons']['combined']['delta_mse'])
    axes[1].bar(range(1,len(means)+1),means,color='#176b8c');axes[1].axhline(0,color='gray',lw=1);axes[1].set_xticks(range(1,len(means)+1));axes[1].set(xlabel='Earlier-player split partition',ylabel='Conventional minus combined player-rate MSE',title='Repeated development splits: same players');fig.tight_layout();fig.savefig(out/'03_identity_and_stability.png',bbox_inches='tight');plt.close(fig)
    return [str(out/name) for name in ['01_drill_geometry.png','02_pressure_uncertainty.png','03_identity_and_stability.png']]
