"""Audited direction-change demands and source-only recovery stress profiles."""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
from scipy.signal import savgol_filter,find_peaks
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler,OneHotEncoder
import front_transfer as F,repo_predict as R,turn_transfer as T
sys.path.insert(0,str(Path(__file__).resolve().parent/'vendor/dynacomp_stress/src'))
from dynacomp.bounds import absolute_apply
from dynacomp.rational import q
from dynacomp.finite import FiniteModel,compile_finite,distinguish,replay_finite

SMOOTHINGS=[5,7,9];SHIFTS=[-2,-1,0,1,2]
TRAP=np.array([.05,.1,.1,.1,.1,.05])

def measure(g,center,window=7,clock=False):
    p=savgol_filter(g[['x','y']].to_numpy(float),window,3,axis=0);v=np.gradient(p,.1,axis=0);s=g.s.to_numpy(float);c=center
    if c<7 or c+13>=len(s):raise ValueError('incomplete_turn_window')
    vi=v[c-6:c-3].mean(0);vo=v[c+3:c+6].mean(0)
    if min(np.linalg.norm(vi),np.linalg.norm(vo))<1:raise ValueError('unreliable_flank_heading')
    ei=vi/np.linalg.norm(vi);eo=vo/np.linalg.norm(vo);angle=float(np.arccos(np.clip(ei@eo,-1,1)));entry=float(s[c-6:c-3].mean())
    if not np.deg2rad(30)<=angle<=np.deg2rad(170) or entry<2:raise ValueError('outside_turn_demands')
    start=c+4
    if clock:
        indices=np.arange(c-6,c+10);local=v[indices];good=np.linalg.norm(local,axis=1)>=1
        if good.sum()<6:raise ValueError('insufficient_progress_heading')
        theta=np.unwrap(np.arctan2(local[:,1],local[:,0]));theta=np.interp(indices,indices[good],theta[good]);heading=np.arctan2(ei[1],ei[0]);heading+=2*np.pi*round((theta[0]-heading)/(2*np.pi));direction=np.sign(ei[0]*eo[1]-ei[1]*eo[0]);progress=np.maximum.accumulate(np.clip(direction*(theta-heading),0,angle))
        first=np.flatnonzero(progress>=.2*angle);last=np.flatnonzero(progress>=.8*angle)
        if not len(first) or not len(last):raise ValueError('incomplete_angular_progress')
        begin=int(indices[first[0]]);start=int(indices[last[0]])
        if begin<4 or start+8>=len(s) or not c-4<=start<=c+8:raise ValueError('unsupported_angular_clock')
        entry=float(s[begin-4:begin-1].mean())
        if entry<2:raise ValueError('low_progress_entry_speed')
    projected=v[start:start+6]@eo;eta=float(TRAP@projected/(.5*entry));retention=float(s[start:start+3].mean()/entry);late=float((s[start+8]-s[start+3])/entry)
    # Coordinates relative to approach; reflection makes exit lateral direction positive.
    rotation=np.array([[ei[0],-ei[1]],[ei[1],ei[0]]]);xy=(p[c-7:c+14]-p[c])@rotation
    if (eo@rotation)[1]<0:xy[:,1]*=-1
    return {'entry':entry,'angle':angle,'eta':eta,'retention':retention,'late_gain':late,'recovery_start':int(start),'projected':projected.tolist(),'normalized_trace':(projected/entry).tolist(),'path':xy.tolist()}

def event_turns(g,clock=False):
    g=g.sort_values('time').reset_index(drop=True);time=pd.to_datetime(g.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9;s=g.s.to_numpy(float)
    if len(g)<25 or not np.allclose(np.diff(time),.1,atol=.002) or not np.isfinite(g[['x','y','s']].to_numpy()).all() or (s<0).any():raise ValueError('invalid_10Hz_trace')
    p=savgol_filter(g[['x','y']].to_numpy(float),7,3,axis=0);v=np.gradient(p,.1,axis=0);signal=np.zeros(len(g))
    for c in range(7,len(g)-13):
        a=v[c-6:c-3].mean(0);b=v[c+3:c+6].mean(0)
        if min(np.linalg.norm(a),np.linalg.norm(b))>=1:signal[c]=np.arccos(np.clip(a@b/(np.linalg.norm(a)*np.linalg.norm(b)),-1,1))
    peaks,_=find_peaks(signal,distance=12,prominence=.15,height=np.deg2rad(30));turns=[]
    for c in peaks:
        branches=[]
        for window in SMOOTHINGS:
            for shift in SHIFTS:
                try:branches.append(dict(window=window,shift=shift,**measure(g,int(c+shift),window,clock=clock)))
                except ValueError:continue
        if len(branches)<5:continue
        record={k:float(np.mean([b[k] for b in branches])) for k in ['entry','angle','eta','retention','late_gain']};record['center']=int(c);record['branches']=branches
        record['eta_min']=min(b['eta'] for b in branches);record['eta_max']=max(b['eta'] for b in branches);record['eta_width']=record['eta_max']-record['eta_min'];record['demand']=record['entry']*record['angle']/np.pi
        # Conservative declared branch box for projected velocities and entry speed.
        z=np.array([b['projected'] for b in branches]);mid=(z.min(0)+z.max(0))/2;radius=(z.max(0)-z.min(0))/2;bound=float(absolute_apply([tuple(q(str(a)) for a in TRAP)],tuple(str(x) for x in radius))[0]);nom=float(TRAP@mid);entries=[b['entry'] for b in branches];ratios=[n/(.5*e) for n in [nom-bound,nom+bound] for e in [min(entries),max(entries)]];record['box_eta_min']=min(ratios);record['box_eta_max']=max(ratios)
        if record['eta_min']<record['box_eta_min']-1e-10 or record['eta_max']>record['box_eta_max']+1e-10:raise AssertionError('branch escaped declared box')
        turns.append(record)
    return turns

def prepare(data='data',base='private_front',out='private_stress',clock=False):
    out=Path(out);out.mkdir(exist_ok=True);d=pd.read_pickle(Path(base)/'private_rows.pkl');tracking=pd.read_csv(Path(data)/'combine_tracking.csv');tracking=tracking[tracking.entity_type.eq('PLAYER')&tracking.nfl_id.isin(d.nfl_id)&tracking.drill_name.isin(F.DRILLS)];rows=[];reject={};attempts=0
    for key,g in tracking.groupby(['nfl_id','draft_year','event_id'],sort=True):
        attempts+=1
        try:turns=event_turns(g,clock=clock)
        except ValueError as e:reject[str(e)]=reject.get(str(e),0)+1;continue
        for turn in turns:rows.append(dict(nfl_id=key[0],draft_year=key[1],event_id=key[2],drill=g.drill_name.iloc[0],**turn))
    turns=pd.DataFrame(rows)
    if turns.empty:raise ValueError('no eligible turns')
    turns.to_pickle(out/'private_turns.pkl');d.to_pickle(out/'private_rows.pkl');audit={'source_attempts':attempts,'turns':len(turns),'turn_players':int(turns.nfl_id.nunique()),'NFL_players':int(d.nfl_id.nunique()),'NFL_records':len(d),'turns_by_drill':turns.groupby('drill').size().to_dict(),'entry_speed_quantiles':turns.entry.quantile([.05,.5,.95]).to_dict(),'angle_degrees_quantiles':(turns.angle*180/np.pi).quantile([.05,.5,.95]).to_dict(),'eta_width_quantiles':turns.eta_width.quantile([.05,.5,.95]).to_dict(),'rejections':reject,'angular_progress_clock':clock,'assumptions':'Operational heading-change peaks; 5/7/9-frame smoothing and centers±.2s. Five or more valid branches. No labeled plant or calibrated sensor probabilities. Response is0.5s projected-velocity integral divided by entry speed*.5s. Clock version begins at80% monotone angular progress and measures entry before20%; initial version begins center+.4s.','bounds':'Unchanged DynaComp rational absolute_apply transports a declared Cartesian branch box. Bounds cover computed scenario vectors, not all sensor/physiology errors.'};(out/'population.json').write_text(json.dumps(audit,indent=2));return turns,audit

class StressEncoder:
    def __init__(self,turns):self.turns=turns
    def fit(self,units):
        if hasattr(self,'capacity_fill'):del self.capacity_fill
        self.ids=set(units.nfl_id);self.phys=T.numeric().fit(units[R.PHYS]);self.meta=units.set_index('nfl_id');self.events=self.turns[self.turns.nfl_id.isin(self.ids)].copy();self.cat=OneHotEncoder(handle_unknown='ignore',sparse_output=False).fit(np.array(F.DRILLS).reshape(-1,1));self.scale=StandardScaler().fit(self._unscaled(self.events,units));x=self.scale.transform(self._unscaled(self.events,units));w=1/self.events.groupby('nfl_id').nfl_id.transform('size');self.model=Ridge(alpha=10).fit(x,self.events[['eta','retention','late_gain']],sample_weight=w*len(self.events)/w.sum());return self
    def _unscaled(self,events,units):
        lookup=units.set_index('nfl_id');phys=self.phys.transform(lookup.reindex(events.nfl_id)[R.PHYS]);s=events.entry.to_numpy();a=events.angle.to_numpy();mass=phys[:,R.PHYS.index('combine_weight')];x=np.c_[s,a,s*a,s*s,a*a,phys,mass*s,mass*a,self.cat.transform(events[['drill']].to_numpy())]
        if 'sprint__ceiling' in units:
            # Missing capacity receives training-unit median, never test-cohort imputation.
            if not hasattr(self,'capacity_fill'):self.capacity_fill=float(units['sprint__ceiling'].median())
            ceiling=lookup.reindex(events.nfl_id)['sprint__ceiling'].fillna(self.capacity_fill).to_numpy();x=np.c_[x,ceiling,s/np.maximum(ceiling,2),(s/np.maximum(ceiling,2))*a]
        return x
    def transform(self,units):
        result=units[['nfl_id']].copy().set_index('nfl_id');ev=self.turns[self.turns.nfl_id.isin(units.nfl_id)].copy();pred=self.model.predict(self.scale.transform(self._unscaled(ev,units)));ev[['eta_r','retention_r','late_r']]=ev[['eta','retention','late_gain']].to_numpy()-pred
        # Branch extrema evaluate the same fitted demand/trait map at each branch.
        lows=[];highs=[]
        for row in ev.itertuples():
            b=pd.DataFrame(row.branches);b['nfl_id']=row.nfl_id;b['drill']=row.drill;p=self.model.predict(self.scale.transform(self._unscaled(b,units)))[:,0];res=b.eta.to_numpy()-p;lows.append(float(res.min()));highs.append(float(res.max()))
        ev['lower']=lows;ev['upper']=highs
        for drill in F.DRILLS:
            sub=ev[ev.drill.eq(drill)];group=sub.groupby('nfl_id');values=group[['eta','retention','late_gain','entry','angle','eta_r','retention_r','late_r','lower','upper']].mean();values['width']=values.upper-values.lower;values['count']=group.size();values['demand_span']=group.demand.max()-group.demand.min();slopes={}
            for player,g in group:
                x=g.demand.to_numpy();y=g.eta_r.to_numpy();x-=x.mean();slopes[player]=float(x@y/(x@x+2))
            values['slope']=pd.Series(slopes)
            attempt_means=sub.groupby(['nfl_id','event_id']).eta_r.mean()
            values['attempt_dispersion']=attempt_means.groupby('nfl_id').std()
            for c in values:result['stress__'+drill+'__'+c]=values[c]
        return result.reset_index()

def finite_audit(turns,out='receipts/stress'):
    # Source-only most ambiguous windows, never selected from NFL outcomes.
    reports=[]
    for row in turns.sort_values('eta_width',ascending=False).head(20).itertuples():
        z=np.array([b['normalized_trace'] for b in row.branches]);labels=tuple(int(round(v*20)) for v in z.ravel());n,m=z.shape
        trans=tuple((i*m+min(j+1,m-1),) for i in range(n) for j in range(m))
        model=FiniteModel(observations=labels,transitions=trans)
        packet=compile_finite(model);assert replay_finite(packet);pairs=0;later=0
        for a in range(n):
            for b in range(a+1,n):
                if labels[a*m]==labels[b*m]:
                    pairs+=1;w=distinguish(model,a*m,b*m)
                    if w is not None:later+=1
        reports.append({'branches':n,'full_states':n*m,'quotient_states':len(packet['quotient_observations']),'same_initial_pairs':pairs,'later_distinguishable_pairs':later})
    r={'audited_windows':len(reports),'windows':reports,'scope':'Actual branch traces quantized at0.05 normalized velocity. DynaComp all-future equivalence applies to the declared six-frame absorbing finite machine only. It does not certify unobserved athlete behavior. Quantization changes trapezoidal normalized recovery by at most0.025.'};Path(out,'finite_observation_audit.json').write_text(json.dumps(r,indent=2));return r
if __name__=='__main__':turns,audit=prepare();print(json.dumps(audit,indent=2))
