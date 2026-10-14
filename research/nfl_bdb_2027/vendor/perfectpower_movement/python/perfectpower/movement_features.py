"""Source-only movement features and uncertain explicit-duration phase summaries.

Numpy is optional to the core language, required for this observation adapter.
Times are seconds and coordinates/speed yards and yards/second. No NFL outcomes
are accepted. Phase templates are operational models, not labeled ground truth.
"""
import math
import numpy as np
from scipy.signal import savgol_filter
from .movement_language import segment_channel,phase_summary,tensor_signature


def trajectory(time,xy,speed=None,smoothing=7):
    time=np.asarray(time,float);xy=np.asarray(xy,float)
    if time.ndim!=1 or xy.shape!=(len(time),2) or len(time)<12 or not np.isfinite(time).all() or not np.isfinite(xy).all():raise ValueError('finite trajectory with at least twelve frames required')
    dt=np.diff(time)
    if (dt<=0).any() or not np.allclose(dt,.1,atol=.002,rtol=0):raise ValueError('contiguous 10 Hz frames required; split gaps explicitly')
    if smoothing not in (5,7,9) or smoothing>len(time):raise ValueError('smoothing window')
    p=savgol_filter(xy,smoothing,2,axis=0);v=np.gradient(p,time,axis=0);geometric=np.linalg.norm(v,axis=1)
    if speed is None:s=geometric
    else:
        s=np.asarray(speed,float)
        if s.shape!=time.shape or not np.isfinite(s).all() or (s<0).any():raise ValueError('finite nonnegative speed required')
        s=savgol_filter(s,smoothing,2);s=np.maximum(s,0)
    a=np.gradient(s,time);theta=np.unwrap(np.arctan2(v[:,1],v[:,0]));w=np.gradient(theta,time)
    # Heading is undefined at rest: interpolate from observed moving frames.
    good=geometric>.5
    if good.sum()<5:raise ValueError('insufficient observed motion')
    w=np.interp(time,time[good],w[good]);w=np.clip(w,-math.pi*3,math.pi*3)
    return {'time':time,'xy':p,'speed':s,'acceleration':a,'angular_rate':w,'geometric_speed':geometric,'heading_reliability':float(good.mean())}


def attempt_features(time,xy,speed=None,onset=.5,temperature=1.,smoothing=7,window=61,degree=3):
    z=trajectory(time,xy,speed,smoothing);s=z['speed'];active=np.flatnonzero((s[:-2]>onset)&(s[1:-1]>onset)&(s[2:]>onset))
    if not len(active):raise ValueError('no sustained onset')
    start=int(active[0]);end=min(len(s),start+window)
    if end-start<16:raise ValueError('short active window')
    t=z['time'][start:end];s=s[start:end];a=z['acceleration'][start:end];w=np.abs(z['angular_rate'][start:end]);p=z['xy'][start:end];n=len(s)
    # Fixed scale choices; no cohort statistics or outcomes enter extraction.
    aa=np.clip(a/5,-3,3);ww=np.clip(w/math.pi,0,3)
    centers=np.array([[.3,0],[-.7,.1],[0,.7],[.7,0]])
    obs=np.c_[aa,ww];cost=((obs[:,None,:]-centers[None,:,:])**2).sum(axis=2)/2
    dt=.1;reward=[]
    for acceleration,turn in zip(a,w):
        row=[]
        for k in range(4):
            v=[0.]*12;v[k]=dt;v[4+k]=acceleration*dt;v[8+k]=turn*dt;row.append(v)
        reward.append(row)
    c=segment_channel(cost,[2]*4,[max(2,n-6)]*4,reward,temperature=temperature)
    summary=phase_summary(c);duration=np.array(summary['mean'][:4]);accel=np.array(summary['mean'][4:8])/duration;turn=np.array(summary['mean'][8:12])/duration
    points=np.c_[(t-t[0])/max(t[-1]-t[0],.1),s/10,aa,ww]
    sig=tensor_signature(points,degree)
    features={'frames':float(n),'onset_seconds':float(t[0]-z['time'][0]),'path_length':float(np.linalg.norm(np.diff(p,axis=0),axis=1).sum()),'peak_speed':float(np.quantile(s,.95)),
              'speed_gain':float(s[-1]-s[0]),'mean_acceleration':float(np.mean(a)),'braking_impulse':float(np.maximum(-a,0).sum()*dt),'turn_work':float((w*s).sum()*dt),
              'recovery_accel':float(accel[3]),'brake_accel':float(accel[1]),'redirect_turn':float(turn[2]),'phase_entropy_per_frame':summary['entropy_nats']/n,
              'map_probability':summary['map_probability'],'heading_reliability':z['heading_reliability'],'speed_disagreement':float(np.mean(np.abs(s-z['geometric_speed'][start:end])))}
    for k in range(4):
        features[f'phase_duration_{k}']=float(duration[k]);features[f'phase_sd_{k}']=math.sqrt(summary['variance'][k]);features[f'phase_boundary_width_{k}']=(summary['boundary_quantiles'][k][2]-summary['boundary_quantiles'][k][0])*dt
    if degree>=2:
        for i in range(4):
            for j in range(i+1,4):features[f'order_area_{i}_{j}']=(sig[2][(i,j)]-sig[2][(j,i)])/2
    if degree>=3:
        # Six triple-order coordinates; avoid a 64-feature small-cohort expansion.
        import itertools
        for word in itertools.permutations((1,2,3)):features['order_triple_'+''.join(map(str,word))]=sig[3][word]
    return features,{'phase':summary,'population':str(c.population),'edges':len(c.edges),'frames':n,'start':start,'end':end,'temperature':temperature,'onset':onset,'scales':{'speed':10,'acceleration':5,'turn':math.pi},'model_scope':'Operational phase templates, not calibrated physiological phase probabilities.'}


def ensemble_features(time,xy,speed=None,onsets=(.5,1.,2.),temperature=1.,smoothing=7):
    runs=[];audit=[]
    for onset in onsets:
        try:f,r=attempt_features(time,xy,speed,onset,temperature,smoothing);runs.append(f);audit.append({'onset':onset,'population':r['population'],'edges':r['edges'],'frames':r['frames']})
        except ValueError as error:audit.append({'onset':onset,'rejected':str(error)})
    if not runs:raise ValueError('all source-only onset scenarios rejected')
    names=runs[0].keys();features={name:float(np.mean([r[name] for r in runs])) for name in names}
    for name in ('recovery_accel','brake_accel','redirect_turn','order_area_1_2','order_area_1_3','order_area_2_3'):
        if name in features:features['onset_range_'+name]=float(np.ptp([r[name] for r in runs]))
    features['onset_scenarios']=float(len(runs))
    return features,{'scenarios':audit,'weight_scope':'Equal sensitivity scenarios, not calibrated probability weights.'}
