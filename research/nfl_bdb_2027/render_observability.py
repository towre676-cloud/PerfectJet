"""Scientific figures from newly reproduced outputs; no synthetic discovery plots."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import observability as O
from scipy.stats import spearmanr

LABELS={'conventional_without_state':'Conventional only','conventional_with_state':'+ Early game movement','pca_with_state':'+ Combine · PCA','target_motion_with_state':'+ Combine · target modes','pca_without_state':'Scouting + Combine · PCA','target_motion_without_state':'Scouting + Combine · target modes'}
def run(out,figures):
    out,figures=Path(out),Path(figures);figures.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f7f9fc','axes.facecolor':'#f7f9fc','axes.titleweight':'bold'})
    example=json.loads((out/'private_source_example.json').read_text());attempts=pd.read_pickle(out/'private_attempts.pkl');result=json.loads((out/'absolute_speed/results.json').read_text());diag=json.loads((out/'diagnostics.json').read_text());t=np.array(example['t']);s=np.array(example['speed']);xy=np.array(example['xy']);xy-=xy[0]
    fit=attempts.sort_values(['nfl_id','draft_year','event_id']).iloc[0];v=xy[-1];u=v/max(np.linalg.norm(v),1e-9);q=xy@np.array([[u[0],-u[1]],[u[1],u[0]]]);a=np.gradient(s,.1)
    fig,ax=plt.subplots(1,3,figsize=(16,5),layout='constrained');sc=ax[0].scatter(q[:,0],q[:,1],c=s,cmap='viridis',s=23);ax[0].plot(q[:,0],q[:,1],alpha=.25);ax[0].set(xlabel='Along sprint · yards',ylabel='Across sprint · yards',title='Measured sprint geometry');ax[0].set_aspect('equal',adjustable='datalim');fig.colorbar(sc,ax=ax[0],label='Speed · yd/s')
    ax[1].plot(t,s,lw=3,color='#097b79',label='Observed · smoothed')
    for order in (1,2):ax[1].plot(t,O.response(t,*[fit[f'motion__order{order}_{k}'] for k in ['V','tau','delay']],order),lw=2,ls='--',label=f'Order {order} fit')
    ax[1].set(xlabel='Seconds from first tracked frame',ylabel='Speed · yd/s',title='Timing alone hides the profile');ax[1].legend(fontsize=9)
    ax[2].plot(s,a,lw=2,color='#4659a7');sc=ax[2].scatter(s,a,c=t,cmap='plasma',s=22);ax[2].set(xlabel='Speed · yd/s',ylabel='Acceleration · yd/s²',title='The speed–acceleration state');fig.colorbar(sc,ax=ax[2],label='Time · seconds');fig.suptitle('A measured Combine attempt · chosen without NFL outcomes',fontsize=17);fig.savefig(figures/'01_motion_geometry.png',dpi=160);plt.close(fig)
    pairs=[(g.iloc[0],g.iloc[-1]) for _,g in attempts.sort_values('event_id').groupby('nfl_id') if len(g)>=2]
    fig,ax=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    for axis,c,title in zip(ax,['motion__order2_V','motion__order2_tau'],['Speed capacity repeats more consistently','Response time is less stable']):
        x=np.array([p[c] for p,r in pairs]);y=np.array([r[c] for p,r in pairs]);axis.scatter(x,y,s=35,alpha=.65,color='#097b79');lo,hi=min(x.min(),y.min()),max(x.max(),y.max());axis.plot([lo,hi],[lo,hi],ls=':',color='gray');axis.set(xlabel='First attempt',ylabel='Last attempt',title=f'{title}\nSpearman ρ = {spearmanr(x,y).statistic:.3f} · {len(pairs)} players')
    fig.suptitle('Repeatability includes alignment, effort and preprocessing · not sensor error alone',fontsize=14);fig.savefig(figures/'02_repeatability.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(1,2,figsize=(16,6),layout='constrained');names=list(result['nested']['mse'])
    for axis,key,title in zip(ax,['nested','exploratory_2025'],['Earlier players · nested validation','2025 players · exploratory transport']):
        values=[result[key]['mse'][n] for n in names];colors=['#9aacbd','#087f7b','#d09e3d','#5561aa','#d09e3d','#5561aa'];axis.barh(range(len(names)),values,color=colors);axis.set_yticks(range(len(names)),[LABELS[n] for n in names]);axis.invert_yaxis();axis.set(xlabel='Player-balanced MSE · (yd/s)²',title=title)
        for i,z in enumerate(values):axis.text(z+.008,i,f'{z:.3f}',va='center')
        axis.set_xlim(0,max(values)*1.14)
    fig.suptitle('Future speed at 1.3–1.5 seconds · all models use matched tuning budgets',fontsize=16);fig.savefig(figures/'03_prediction_comparison.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(1,3,figsize=(17,5),layout='constrained')
    for axis,comp,title in zip(ax[:2],['state_channel','target_motion_increment'],['Early game state supplies information','Incremental Combine value remains uncertain']):
        for i,key in enumerate(['nested','exploratory_2025']):
            z=result[key]['comparisons'][comp];axis.plot(z['ci95'],[i,i],lw=5,color='#097b79');axis.scatter(z['delta_mse'],i,s=80,color='#4659a7')
        axis.axvline(0,color='gray',ls=':');axis.set_yticks([0,1],['Earlier nested','2025 exploratory']);axis.set(xlabel='Conventional − augmented MSE',title=title);axis.margins(y=.5)
    z=diag['training_profile_shuffles'];ax[2].hist(z['mse'],bins=10,color='#9aacbd',edgecolor='white');ax[2].axvline(z['real_profile_mse'],color='#9b4560',lw=3,label='Real profiles');ax[2].set(xlabel='2025 prediction MSE',ylabel='Training shuffles',title='Does the actual Combine profile matter?');ax[2].legend();fig.suptitle('Positive differences favor added information · intervals condition on fitted models',fontsize=15);fig.savefig(figures/'04_uncertainty_controls.png',dpi=160);plt.close(fig)
    pred=pd.read_pickle(out/'absolute_speed/private_forward_conventional_with_state.pkl');fig,ax=plt.subplots(1,2,figsize=(13,5),layout='constrained');sc=ax[0].hexbin(pred.truth,pred.prediction,gridsize=25,mincnt=1,cmap='viridis');lo=min(pred.truth.min(),pred.prediction.min());hi=max(pred.truth.max(),pred.prediction.max());ax[0].plot([lo,hi],[lo,hi],ls=':',color='#c65c73');ax[0].set(xlabel='Measured future speed · yd/s',ylabel='Predicted future speed · yd/s',title='2025 calibration · unseen players');fig.colorbar(sc,ax=ax[0],label='Route windows')
    lines=['Combine → game: evidence remains uncertain.','Early game state → future speed: useful information.','Tracking benefit ≠ pre-draft scouting benefit.','Do not infer separation or coverage quality from speed alone.','Small player cohorts limit season-wide conclusions.'];ax[1].axis('off')
    for i,line in enumerate(lines):ax[1].text(0,.92-i*.17,line,fontsize=12,color='#17344c',wrap=True)
    fig.savefig(figures/'05_coach_readout.png',dpi=160);plt.close(fig)
    # An offline explorer for the fitted response surrogate, never a live NFL predictor.
    V,tau=[float(fit[f'motion__order2_{k}']) for k in ['V','tau']]
    html='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Movement response explorer</title><style>body{font:18px system-ui;background:#071a2b;color:#e6f1fa;padding:4vw}main{max-width:1000px;margin:auto}canvas{width:100%;background:#102c40;border-radius:20px}input{width:100%;accent-color:#44d7b7}strong{color:#44d7b7}small{color:#acc4d6}</style><main><h1>Speed alone does not describe the next step.</h1><p>Change current speed and acceleration to see the response of one fitted Combine surrogate. This is a mathematical illustration, <strong>not a prediction for an NFL play</strong>.</p><label>Current speed <span id="sv"></span> yd/s<input id="s" type="range" min="0" max="12" step=".1" value="5"></label><label>Current acceleration <span id="av"></span> yd/s²<input id="a" type="range" min="-2" max="8" step=".1" value="2"></label><canvas id="plot" width="960" height="420" aria-label="Modeled speed over the next second"></canvas><p id="result"></p><small>Curve: V − exp(−h/τ)[(V−s) + ((V−s)/τ−a)h]. Parameters fitted to the source example selected independently of game outcomes. Extrapolations may be physically implausible; no clipping hides them.</small></main><script>const V=VV,tau=TT;const c=document.querySelector('#plot'),ctx=c.getContext('2d');function draw(){let s=+document.querySelector('#s').value,a=+document.querySelector('#a').value;document.querySelector('#sv').textContent=s.toFixed(1);document.querySelector('#av').textContent=a.toFixed(1);const ys=Array.from({length:101},(_,i)=>V-Math.exp(-i/100/tau)*((V-s)+((V-s)/tau-a)*i/100));let lo=Math.min(0,...ys),hi=Math.max(14,...ys);ctx.clearRect(0,0,960,420);ctx.strokeStyle='#335369';ctx.lineWidth=1;ctx.font='16px system-ui';ctx.fillStyle='#b9d0df';for(let k=0;k<5;k++){let y=360-k*75;ctx.beginPath();ctx.moveTo(70,y);ctx.lineTo(920,y);ctx.stroke();ctx.fillText((lo+(hi-lo)*k/4).toFixed(1),10,y+5)}ctx.strokeStyle='#44d7b7';ctx.lineWidth=4;ctx.beginPath();ys.forEach((z,i)=>{let x=70+i*8.5,y=360-300*(z-lo)/(hi-lo);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke();ctx.fillText('Now',70,400);ctx.fillText('+1 second',810,400);document.querySelector('#result').textContent='Modeled speed after one second: '+ys[100].toFixed(2)+' yd/s · change '+(ys[100]-s).toFixed(2)+' yd/s';}document.querySelector('#s').oninput=draw;document.querySelector('#a').oninput=draw;draw();</script>'''
    (figures/'response_state_explorer.html').write_text(html.replace('VV',repr(V)).replace('TT',repr(tau)))
    return [figures/f'{i:02d}_{name}.png' for i,name in enumerate(['motion_geometry','repeatability','prediction_comparison','uncertainty_controls','coach_readout'],1)]
if __name__=='__main__':run(Path(__file__).parent/'private_observability',Path(__file__).parent/'receipts/observability_reproduced')
