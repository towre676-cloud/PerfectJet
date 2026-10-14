"""Combine-to-game research. No competition data are bundled or fabricated."""
from pathlib import Path
import json, hashlib, argparse, platform
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor

SEED=20271006
BASE=['combine_height','combine_weight','ten_yd_split','forty','vertical','broad_jump','three_cone','short_shuttle']
CONTEXT=['cushion','down','yards_to_go','yardline_number','pre_snap_home_score','pre_snap_visitor_score']
CATS=['route_ran','team_coverage_man_zone','offense_formation','in_motion_at_ball_snap']
MOTION=['entry_speed','speed_retention','exit_gain','braking_impulse','turn_angle','curvature_energy','jerk_rms','signature_area']
CUT_ROUTES={'OUT','SLANT','POST','CORNER','HITCH'}

def movement(g,window=7):
    """Largest interior heading change; fixed +/-0.5s event window, yards/seconds."""
    g=g.sort_values('time').copy()
    t=pd.to_datetime(g.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9
    if len(t)<21 or np.any(np.diff(t)<=0): raise ValueError('short or duplicate/nonmonotone trajectory')
    dt=np.diff(t)
    if not np.allclose(dt,.1,atol=.015): raise ValueError('irregular sampling; do not interpolate missing cuts')
    p=g[['x','y']].to_numpy(float)
    if not np.isfinite(p).all(): raise ValueError('nonfinite coordinates')
    p=savgol_filter(p,window,3,axis=0)
    v=np.gradient(p,.1,axis=0);a=np.gradient(v,.1,axis=0)
    speed=np.linalg.norm(v,axis=1)
    theta=np.unwrap(np.arctan2(v[:,1],v[:,0]))
    k=np.arange(5,len(p)-5)
    score=np.abs(theta[k+3]-theta[k-3]);score[(speed[k-3]<1)|(speed[k+3]<1)]=0
    if score.max()<np.deg2rad(25): raise ValueError('no qualifying turn')
    c=int(k[np.flatnonzero(np.isclose(score,score.max(),rtol=0,atol=1e-10))[0]]);sl=slice(c-5,c+6)
    turn=theta[c+3]-theta[c-3]
    tangent=v[c-3]/speed[c-3];normal=np.array([-tangent[1],tangent[0]])
    q=(p[sl]-p[c-5])@np.stack([tangent,normal],axis=1)
    q[:,1]*=1 if turn>=0 else -1
    # Antisymmetric level-two path signature, equal to signed area with closing chord.
    area=.5*np.sum(q[:-1,0]*q[1:,1]-q[:-1,1]*q[1:,0])
    sp=speed[sl];at=np.gradient(sp,.1)
    omega=np.gradient(theta,.1)[sl];curv=omega/np.maximum(sp,1)
    out=dict(entry_speed=float(np.mean(sp[:3])),speed_retention=float(sp.min()/np.mean(sp[:3])),
      exit_gain=float(np.mean(sp[-3:])-sp.min()),braking_impulse=float(np.trapezoid(np.maximum(-at,0),dx=.1)),
      turn_angle=float(abs(turn)),curvature_energy=float(np.trapezoid(curv**2*sp,dx=.1)),
      jerk_rms=float(np.sqrt(np.mean(np.gradient(a[sl],.1,axis=0)**2))),signature_area=float(area))
    diag={'t':np.arange(-5,6)*.1,'q':q,'speed':sp,'tangential_acceleration':at,'cut_index':c}
    return out,diag

def inventory(root):
    """Stream all CSVs; retain observed counts/schema/hash, never treat descriptions as measured counts."""
    rows=[]
    for p in sorted(Path(root).glob('*.csv')):
        count=0;ids=set();years=set();cols=None
        for c in pd.read_csv(p,chunksize=200000):
            count+=len(c);cols=list(c.columns)
            if 'nfl_id' in c: ids.update(c.nfl_id.dropna().astype(int))
            for key in ('season','draft_year'):
                if key in c:years.update(c[key].dropna().astype(int))
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
        rows.append(dict(file=p.name,rows=count,unique_players=len(ids),years=sorted(years),columns=cols,sha256=h.hexdigest()))
    return rows

def prepare(root,out):
    root,out=Path(root),Path(out);out.mkdir(parents=True,exist_ok=True)
    players=pd.read_csv(root/'players.csv');combine=pd.read_csv(root/'combine_results.csv');games=pd.read_csv(root/'games.csv')
    for d,key in [(players,['nfl_id']),(combine,['nfl_id','draft_year']),(games,['game_id'])]:
        if d.duplicated(key).any():raise ValueError('duplicate metadata join key')
    ids=set(players.loc[players.nfl_position.eq('WR'),'nfl_id']);pieces=[]
    drill_counts={}
    for c in pd.read_csv(root/'combine_tracking.csv',chunksize=200000):
        c=c[c.nfl_id.isin(ids)&c.entity_type.eq('PLAYER')&c.drill_type.eq('SKILL_DRILLS_WR')]
        pieces.append(c)
        for name,n in c.drill_name.value_counts().items():drill_counts[name]=drill_counts.get(name,0)+int(n)
    track=pd.concat(pieces,ignore_index=True);features=[];rejects=[]
    for keys,g in track.groupby(['nfl_id','draft_year','event_id'],sort=True):
        try:
            f,_=movement(g);features.append(dict(nfl_id=keys[0],draft_year=keys[1],event_id=keys[2],drill_name=g.drill_name.iloc[0],**f))
        except ValueError as e:rejects.append(dict(event_id=keys[2],reason=str(e)))
    f=pd.DataFrame(features)
    if f.empty:raise ValueError('no qualifying WR turns; inspect drill availability before changing protocol')
    f.to_csv(out/'attempt_features.csv',index=False)
    # Choose one homologous drill using Combine availability only, before NFL outcomes.
    availability=f.groupby(['drill_name','draft_year']).nfl_id.nunique().unstack(fill_value=0).reindex(columns=[2023,2024,2025],fill_value=0)
    minimum=availability.min(axis=1);eligible=minimum[minimum>=5]
    if eligible.empty:raise ValueError('no qualifying drill shared by >=5 WRs in every class; inspect availability')
    selected=sorted(eligible.index,key=lambda k:(-eligible[k],k))[0]
    f=f[f.drill_name.eq(selected)]
    agg=f.groupby(['nfl_id','draft_year'])[MOTION].median().reset_index()
    pp=pd.read_csv(root/'player_play.csv')
    if pp.duplicated(['game_id','play_id','nfl_id']).any():raise ValueError('duplicate player-play key')
    pp=pp.merge(games[['game_id','season','season_type']],on='game_id',validate='many_to_one').merge(players[['nfl_id','draft_year','nfl_position']],on='nfl_id',validate='many_to_one')
    d=pp[pp.nfl_position.eq('WR')&pp.season.eq(pp.draft_year)&pp.season_type.eq('REG')&pp.route_ran.isin(CUT_ROUTES)&pp.play_nullified_by_penalty.eq('N')].copy()
    d=d[np.isfinite(d.separation_at_pass_forward)&(d.separation_at_pass_forward>=0)]
    d=d.merge(combine,on=['nfl_id','draft_year'],validate='many_to_one').merge(agg,on=['nfl_id','draft_year'],validate='many_to_one')
    # Each player must have >=20 measured routes. Threshold is frozen before labels are inspected.
    n=d.groupby('nfl_id').size();d=d[d.nfl_id.isin(n[n>=20].index)]
    audit={'status':'actual_data_prepared','draft_class_players':d.groupby('draft_year').nfl_id.nunique().to_dict(),
      'draft_class_routes':d.groupby('draft_year').size().to_dict(),'wr_roster_players':len(ids),'qualifying_attempts':len(f),
      'selected_drill':selected,'drill_player_availability':availability.to_dict(),'excluded_attempts':rejects,'drill_frame_counts':drill_counts,'target_only_fraction':float(d.target.mean()) if len(d) else None,
      'game_tracking_use':'Primary outcome uses official separation; game trajectory replication remains secondary and unrun.'}
    temp=out/'private_analysis_rows.csv.tmp';d.to_csv(temp,index=False);temp.replace(out/'private_analysis_rows.csv');
    if len(pd.read_csv(out/'private_analysis_rows.csv'))!=len(d):raise ValueError('analysis CSV roundtrip row mismatch')
    d.to_pickle(out/'private_analysis_rows.pkl');(out/'population_audit.json').write_text(json.dumps(audit,indent=2))
    return d,f,audit

def model(d,nums,kind,alpha=10):
    numeric=Pipeline([('impute',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)),('scale',StandardScaler())])
    cats=Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore',sparse_output=False))])
    pre=ColumnTransformer([('numeric',numeric,nums),('category',cats,CATS)])
    reg=Ridge(alpha=alpha) if kind=='ridge' else RandomForestRegressor(n_estimators=200,min_samples_leaf=20,max_depth=6,max_features=.8,random_state=SEED,n_jobs=2)
    return Pipeline([('pre',pre),('reg',reg)])

def weights(d):return 1/d.groupby('nfl_id').nfl_id.transform('size').to_numpy()
def score(d,p):return float(np.average((d.separation_at_pass_forward.to_numpy()-p)**2,weights=weights(d)))

def compare(d,out):
    """Player-disjoint, rookie-season-disjoint validation and locked 2025 test."""
    out=Path(out);out.mkdir(parents=True,exist_ok=True);d=d.copy()
    if not (d.season==d.draft_year).all():raise ValueError('rookie seasons required')
    for col in MOTION:
        d[col+'_mass']=d[col]*d.combine_weight/200
        d[col+'_man']=d[col]*d.team_coverage_man_zone.eq('MAN_COVERAGE').astype(int)
    families={'conventional':BASE+CONTEXT,'tracking':BASE+CONTEXT+MOTION,
      'physical_context_interactions':BASE+CONTEXT+MOTION+[c+s for c in MOTION for s in ('_mass','_man')],
      'scouting_reference':BASE+CONTEXT+['ngs_college_production_score']}
    a,b,t=[d[d.draft_year.eq(y)] for y in (2023,2024,2025)]
    if min(x.nfl_id.nunique() for x in (a,b,t))<10:raise ValueError('fewer than ten WRs in a class; insufficient locked-cohort study')
    assert not(set(a.nfl_id)&set(b.nfl_id) or set(a.nfl_id)&set(t.nfl_id) or set(b.nfl_id)&set(t.nfl_id))
    dev=pd.concat([a,b]);results=[];pred={};selections={}
    for kind in ('ridge','forest'):
      for family,nums in families.items():
        options=(1,10,100) if kind=='ridge' else (10,)
        vals=[]
        for alpha in options:
            m=model(a,nums,kind,alpha);m.fit(a,a.separation_at_pass_forward,reg__sample_weight=weights(a));vals.append((score(b,m.predict(b)),alpha))
        _,alpha=min(vals);selections[kind+'_'+family]={'alpha':alpha,'validation_mse':min(vals)[0]}
        m=model(dev,nums,kind,alpha);m.fit(dev,dev.separation_at_pass_forward,reg__sample_weight=weights(dev));p=m.predict(t)
        name=kind+'_'+family;pred[name]=p
        results.append({'model':name,'test_player_balanced_mse':score(t,p),'test_rmse_yards':score(t,p)**.5,'validation_mse':min(vals)[0]})
    # Primary contrast is ridge tracking vs ridge conventional. Others exploratory.
    losses=pd.DataFrame({'nfl_id':t.nfl_id,'baseline':(t.separation_at_pass_forward-pred['ridge_conventional'])**2,'tracking':(t.separation_at_pass_forward-pred['ridge_tracking'])**2}).groupby('nfl_id').mean()
    delta=(losses.baseline-losses.tracking).to_numpy();rng=np.random.default_rng(SEED)
    boots=np.mean(rng.choice(delta,(5000,len(delta)),replace=True),axis=1)
    report={'status':'actual_data_completed','primary_delta_mse_yards_squared':float(delta.mean()),'player_bootstrap_ci95':np.quantile(boots,[.025,.975]).tolist(),
      'test_players':len(delta),'test_routes':len(t),'results':results,'selection':selections,
      'interpretation':'positive delta favors motion; CI crossing zero is inconclusive; cohort-generalization requires more years',
      'selection_warning':'Exploratory models cannot replace the preregistered primary contrast after observing test labels.'}
    pd.DataFrame(results).to_csv(out/'model_comparisons.csv',index=False)
    (out/'experiment_results.json').write_text(json.dumps(report,indent=2))
    pp=t[['nfl_id','game_id','play_id']].copy()
    for k,v in pred.items():pp[k]=v
    pp.to_csv(out/'private_test_predictions.csv',index=False)
    return report

def plot_motion(diag,path,label):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':'#e6edf6','axes.labelcolor':'#c2cfde','xtick.color':'#8aa0b6','ytick.color':'#8aa0b6','axes.edgecolor':'#304359','axes.facecolor':'#102236','figure.facecolor':'#071421'})
    fig,ax=plt.subplots(1,3,figsize=(16,5),layout='constrained');q=diag['q'];t=diag['t'];s=diag['speed'];a=diag['tangential_acceleration']
    sc=ax[0].scatter(q[:,0],q[:,1],c=s,cmap='plasma',s=80,zorder=3);ax[0].plot(q[:,0],q[:,1],color='#39dbbd',alpha=.8);ax[0].set_aspect('equal');ax[0].set(xlabel='Along entry direction · yards',ylabel='Across entry direction · yards',title='THE SHAPE OF THE CUT');fig.colorbar(sc,ax=ax[0],label='Speed · yd/s',shrink=.7)
    ax[1].plot(t,s,lw=3,color='#39dbbd');ax[1].axvline(0,color='#efb455',ls=':');ax[1].set(xlabel='Seconds from largest turn',ylabel='Speed · yd/s',title='BRAKE → TURN → RECOVER')
    ax[2].plot(s,a,lw=2,color='#efb455');ax[2].scatter(s,a,c=t,cmap='cool',s=40);ax[2].axhline(0,color='#304359');ax[2].set(xlabel='Speed · yd/s',ylabel='Tangential acceleration · yd/s²',title='MOVEMENT PHASE PORTRAIT')
    for z in ax:z.grid(alpha=.12)
    fig.suptitle(label,fontsize=17,fontweight='bold');fig.savefig(path,dpi=150);plt.close(fig)

def run(root,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'inventory.json').write_text(json.dumps(inventory(root),indent=2))
    d,f,audit=prepare(root,out);report=compare(d,out)
    # Selected example by sorted ID, independent of outcomes. Read only WR tracking rows.
    chosen=f.sort_values(['nfl_id','event_id']).iloc[0];parts=[]
    for c in pd.read_csv(Path(root)/'combine_tracking.csv',chunksize=200000):parts.append(c[c.event_id.eq(chosen.event_id)&c.entity_type.eq('PLAYER')])
    g=pd.concat(parts);_,diag=movement(g);plot_motion(diag,out/'actual_combine_geometry.png','Observed Combine trajectory · selected without NFL outcomes')
    (out/'actual_combine_geometry.html').write_text(motion_html(diag,'Observed Combine attempt · selected independently of NFL outcomes'))
    return report


def game_transfer(root,d,out):
    """Secondary descriptive mechanics replication; game motion never a prospect predictor."""
    out=Path(out);pieces=[];ids=set(d.nfl_id)
    keys=d[['game_id','play_id','nfl_id']].drop_duplicates()
    for year in (2023,2024,2025):
        p=Path(root)/f'game_tracking_{year}.csv';parts=[]
        for c in pd.read_csv(p,chunksize=200000):
            c=c[c.nfl_id.isin(ids)].merge(keys,on=['game_id','play_id','nfl_id'],how='inner',validate='many_to_one');parts.append(c)
        frames=pd.concat(parts,ignore_index=True)
        for key,g in frames.groupby(['game_id','play_id','nfl_id']):
            g=g.sort_values('time');snap=g[g.event.eq('ball_snap')];release=g[g.event.eq('pass_forward')]
            if snap.empty or release.empty:continue
            g=g[g.time.ge(snap.time.iloc[0])&g.time.le(release.time.iloc[0])]
            try:
                f,_=movement(g);pieces.append(dict(game_id=key[0],play_id=key[1],nfl_id=key[2],**f))
            except ValueError:continue
    pd.DataFrame(pieces).to_csv(out/'private_game_motion.csv',index=False)
    return {'status':'descriptive_only','qualifying_game_turns':len(pieces),'note':'No 22-player coverage reconstruction. Game movement is outcome-side diagnostic, never a pre-draft predictor.'}

def motion_html(diag,label):
    """Offline SVG animation of measured samples, not a generated football replay."""
    import html
    data=json.dumps({k:diag[k].tolist() for k in ('t','q','speed','tangential_acceleration')})
    template='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Inside the cut</title><style>
body{background:#071421;color:#e6edf6;font:17px system-ui;margin:0;padding:4vw}main{max-width:1000px;margin:auto}.tag{color:#39dbbd;font-size:12px;letter-spacing:2px}h1{font-size:clamp(28px,5vw,52px)}.layout{display:grid;grid-template-columns:2fr 1fr;gap:24px}svg{background:#102236;width:100%;border-radius:20px}button{background:#39dbbd;color:#071421;border:0;border-radius:9px;padding:12px 22px;font-weight:700}input{width:100%;accent-color:#39dbbd}small{color:#9cafc3}strong{font-size:40px;display:block}.metric{margin:22px 0}@media(max-width:650px){.layout{grid-template-columns:1fr}} </style>
<main><div class="tag">MOVEMENT LAB · FRAME BY FRAME</div><h1>Inside the cut.</h1><p>LABEL</p><div class="layout"><svg id="field" viewBox="0 0 600 400" role="img" aria-label="Canonical trajectory in yards"><g id="grid"></g><path id="path" fill="none" stroke="#39dbbd" stroke-width="3"/><g id="samples"></g><circle id="player" r="12" fill="#efb455" stroke="#071421" stroke-width="4"/><text x="22" y="380" fill="#9cafc3" font-size="14">Canonical entry frame · yards</text></svg><aside><div class="metric">Time from detected turn<strong id="time"></strong><small>seconds</small></div><div class="metric">Speed<strong id="speed"></strong><small>yards / second</small></div><div class="metric">Braking / reacceleration<strong id="acc"></strong><small>yards / second²</small></div></aside></div><p><button id="play">Play movement</button> <small>Eleven observed samples; interpolation animates the marker only.</small></p><input id="frame" type="range" min="0" max="10" step=".01" value="0" aria-label="Inspect tracking moment"><p><small>The line is the sampled path. Color indicates speed. A positive acceleration value means the athlete is regaining speed. The dot does not represent a defender or a missing NFL player.</small></p></main>
<script>const D=DATA;const ns='http://www.w3.org/2000/svg';const xs=D.q.map(p=>p[0]),ys=D.q.map(p=>p[1]);let xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);const scale=Math.min(500/Math.max(xmax-xmin,.2),280/Math.max(ymax-ymin,.2));const P=D.q.map(p=>[50+(p[0]-xmin)*scale,330-(p[1]-ymin)*scale]);function node(tag,attrs,parent){let e=document.createElementNS(ns,tag);for(let k in attrs)e.setAttribute(k,attrs[k]);parent.appendChild(e);return e}for(let x=Math.floor(xmin);x<=xmax;x++){const z=50+(x-xmin)*scale;node('line',{x1:z,y1:20,x2:z,y2:350,stroke:'#233c51'},document.querySelector('#grid'));const t=node('text',{x:z,y:365,fill:'#9cafc3','font-size':12},document.querySelector('#grid'));t.textContent=x;}document.querySelector('#path').setAttribute('d',P.map((p,i)=>(i?'L':'M')+p.join(',')).join(' '));let low=Math.min(...D.speed),high=Math.max(...D.speed);P.forEach((p,i)=>node('circle',{cx:p[0],cy:p[1],r:5,fill:`hsl(${180-140*(D.speed[i]-low)/Math.max(high-low,.01)} 75% 60%)`},document.querySelector('#samples')));let f=document.querySelector('#frame'),playing=false,last=0;function show(){let z=+f.value,i=Math.min(9,Math.floor(z)),a=z-i;let p=P[i].map((v,k)=>v+(P[i+1][k]-v)*a);document.querySelector('#player').setAttribute('cx',p[0]);document.querySelector('#player').setAttribute('cy',p[1]);for(let [id,key] of [['time','t'],['speed','speed'],['acc','tangential_acceleration']])document.querySelector('#'+id).textContent=(D[key][i]+(D[key][i+1]-D[key][i])*a).toFixed(2)}f.oninput=()=>{playing=false;document.querySelector('#play').textContent='Play movement';show()};document.querySelector('#play').onclick=()=>{playing=!playing;if(+f.value>=10)f.value=0;document.querySelector('#play').textContent=playing?'Pause':'Play movement';last=performance.now()};function tick(now){if(playing){f.value=Math.min(10,+f.value+(now-last)/300);show();if(+f.value>=10){playing=false;document.querySelector('#play').textContent='Replay movement'}}last=now;requestAnimationFrame(tick)}show();requestAnimationFrame(tick);</script>'''
    return template.replace('LABEL',html.escape(label)).replace('DATA',data)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--out',default='private_results');args=ap.parse_args();print(json.dumps(run(args.data,args.out),indent=2))
