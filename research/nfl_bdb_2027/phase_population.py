"""Finite movement-language sums over uncertain onsets and phase paths.

Weights are explicit sensitivity assumptions, not calibrated phase probabilities.
Only source sensors enter new profiles. No NFL outcomes select these features.
"""
from pathlib import Path
import json,itertools,math
import numpy as np,pandas as pd
from scipy.signal import savgol_filter
from scipy.special import logsumexp
import front_transfer as F,analysis as A
from mechanism import player_splits

ONSETS=[.5,1.,1.5,2.]
TEMPERATURES=[.5,1.,2.]
FAMILIES=['conventional','summaries','sequence','shuffled']

def phase_population(z,temperature=1.):
    """Exact sum-product over stay/advance paths, forced start0/end3."""
    if len(z)<4 or not np.isfinite(z).all():raise ValueError('invalid_channels')
    # Normalized channels: speed/10 yd/s, acceleration/10 yd/s², |rotation|/pi rad/s.
    a,w=z[:,1],z[:,2]
    cost=np.c_[a*a+w*w,(a+.5)**2+w*w,a*a+(w-.5)**2,(a-.5)**2+w*w]/(2*temperature)
    n=len(z);f=np.full((n,4),-np.inf);b=f.copy();f[0,0]=-cost[0,0];b[-1,3]=0
    for t in range(1,n):
        f[t]=np.logaddexp(f[t-1],np.r_[-np.inf,f[t-1,:3]])-cost[t]
    for t in range(n-2,-1,-1):
        future=b[t+1]-cost[t+1]
        b[t]=np.logaddexp(future,np.r_[future[1:],-np.inf])
    p=np.exp(f+b-f[-1,3]);occupancy=p.mean(axis=0)
    conditional=(p.T@z)/p.sum(axis=0)[:,None]
    entropy=-np.sum(p*np.log(np.maximum(p,1e-300)))/n
    return np.r_[occupancy,conditional.ravel(),entropy],p,float(f[-1,3])

def sequence_features(z,temperature):
    mid=(z[1:]+z[:-1])/2;delta=np.diff(z,axis=0)
    areas=[np.sum(mid[:,i]*delta[:,j]-mid[:,j]*delta[:,i])/2 for i,j in itertools.combinations(range(3),2)]
    f,_,_=phase_population(z,temperature);return np.r_[areas,f]

def channels(g,onset):
    g=g.sort_values('time');t=pd.to_datetime(g.time,utc=True,format='ISO8601').astype('int64').to_numpy()/1e9
    s=g.s.to_numpy(float)
    if len(g)<16 or not np.allclose(np.diff(t),.1,atol=.015) or not np.isfinite(s).all():raise ValueError('invalid_trace')
    start=next((i for i in range(len(s)-2) if np.all(s[i:i+3]>onset)),None)
    if start is None or len(s)-start<16:raise ValueError('incomplete_onset')
    stop=min(len(s),start+51);xy=g[['x','y']].to_numpy(float)[start:stop]
    if not np.isfinite(xy).all():raise ValueError('nonfinite_xy')
    xy=savgol_filter(xy,7,3,axis=0);v=np.gradient(xy,.1,axis=0);w=np.abs(np.gradient(np.unwrap(np.arctan2(v[:,1],v[:,0])),.1));w[np.linalg.norm(v,axis=1)<1]=0
    z=np.c_[s[start:stop]/10,np.gradient(s[start:stop],.1)/10,np.minimum(w,np.pi*4)/np.pi]
    return z,start

def pooled(g,event_seed):
    ordinary=[];ordered=[];shuffled=[];starts=[]
    for onset in ONSETS:
        try:z,start=channels(g,onset);f=F.skill_features(g,onset)
        except ValueError:continue
        ordinary.append(list(f.values()));starts.append(start)
        # One joint frame permutation preserves the exact channel multiset.
        rng=np.random.default_rng(event_seed+int(onset*100));control=z[rng.permutation(len(z))]
        for temp in TEMPERATURES:
            ordered.append(sequence_features(z,temp));shuffled.append(sequence_features(control,temp))
    if not ordinary:raise ValueError('no_plausible_window')
    def moments(arr,prefix):
        x=np.asarray(arr);return {f'{prefix}_{stat}_{j}':float(v) for stat,values in [('mean',np.nanmean(x,axis=0)),('sd',np.nanstd(x,axis=0))] for j,v in enumerate(values)}
    return {**moments(ordinary,'summary'),**moments(ordered,'sequence'),**moments(shuffled,'shuffle')},starts

def prepare(data='data',base='private_front',out='private_phase_population'):
    out=Path(out);out.mkdir(exist_ok=True);d=pd.read_pickle(Path(base)/'private_rows.pkl');tr=pd.read_csv(Path(data)/'combine_tracking.csv');tr=tr[tr.entity_type.eq('PLAYER')&tr.nfl_id.isin(d.nfl_id)&tr.drill_name.isin(F.DRILLS)];records=[];starts=[];rejected={}
    for index,(key,g) in enumerate(tr.groupby(['nfl_id','draft_year','event_id'],sort=True)):
        try:f,ss=pooled(g,F.SEED+9000+index)
        except ValueError as e:rejected[str(e)]=rejected.get(str(e),0)+1;continue
        records.append(dict(nfl_id=key[0],draft_year=key[1],event_id=key[2],drill=g.drill_name.iloc[0],**f));starts.append({'drill':g.drill_name.iloc[0],'onset_span_s':(max(ss)-min(ss))*.1,'valid_onsets':len(ss)})
    q=pd.DataFrame(records);cols=[c for c in q if c.startswith(('summary_','sequence_','shuffle_'))];panel=q.groupby(['nfl_id','draft_year','drill'])[cols].median().unstack('drill');panel.columns=[f'population__{drill}__{col}' for col,drill in panel.columns];d=d.merge(panel.reset_index(),on=['nfl_id','draft_year'],how='left',validate='many_to_one');d.to_pickle(out/'private_rows.pkl');q.to_pickle(out/'private_source.pkl');s=pd.DataFrame(starts)
    audit={'attempts':len(q),'source_players':int(q.nfl_id.nunique()),'NFL_players':int(d.nfl_id.nunique()),'NFL_rows':len(d),'onsets_yd_per_s':ONSETS,'temperatures':TEMPERATURES,'rejections':rejected,'onset_span_quantiles_s':s.onset_span_s.quantile([0,.5,.9,1]).to_dict(),'source_dimensions':len(panel.columns),'weights':'Equal onset and temperature sensitivity mixture; Gibbs path costs. These are assumed weights, not empirically calibrated semantic phase probabilities. Each legal path has uniform base weight; duration multiplicity is a prior.','phase_language':'stay or advance: approach/brake/redirect/recover, fixed start and finish. Operational single-transition summary of first up-to-5s, not ground-truth drill segmentation.','order_control':'Joint frame permutation before signed-area and phase features, preserving per-window channel multiset. Ordinary summaries identical in sequence/shuffled families.','inference_scope':'Rookie pressure-event rate conditional on recorded NFL workloads; prior 2025 inspection. No untouched test class remains.'}
    (out/'population.json').write_text(json.dumps(audit,indent=2));return d,audit

def columns(d):
    sprint=[c for c in d if c.startswith('motion__')];summary=[c for c in d if c.startswith('population__') and '__summary_' in c];seq=[c for c in d if c.startswith('population__') and '__sequence_' in c];shuf=[c for c in d if c.startswith('population__') and '__shuffle_' in c]
    return {'conventional':[],'summaries':sprint+summary,'sequence':sprint+summary+seq,'shuffled':sprint+summary+shuf}

def evaluate(q):
    p=q.groupby('nfl_id').mean(numeric_only=True);errors={k:(p.pressure_event-p[k])**2 for k in FAMILIES};rng=np.random.default_rng(F.SEED+9500);comparisons={}
    for baseline,feature in [('conventional',k) for k in FAMILIES[1:]]+[('summaries','sequence'),('shuffled','sequence')]:
        v=(errors[baseline]-errors[feature]).to_numpy();comparisons[baseline+'->'+feature]={'delta_mse':float(v.mean()),'relative_reduction':float(v.mean()/errors[baseline].mean()),'ci95':np.quantile(rng.choice(v,(5000,len(v)),replace=True).mean(1),[.025,.975]).tolist()}
    return {'players':len(p),'player_rate_mse':{k:float(e.mean()) for k,e in errors.items()},'comparisons':comparisons,'uncertainty':'Paired resampling of fixed player predictions only. No model-refitting, adaptive-search or onset-model uncertainty is covered.'}

def run(out='private_phase_population',count=16,phase=None):
    out=Path(out);d=pd.read_pickle(out/'private_rows.pkl');cc=columns(d);old=json.loads(Path('private_front_macro/pressure_event/results.json').read_text());dev=d[d.draft_year.isin([2023,2024])].reset_index(drop=True);test=d[d.draft_year.eq(2025)].reset_index(drop=True)
    stages=[(str(fold),dev.iloc[i],dev.iloc[j],next(x['config'] for x in old['folds'] if x['family']=='conventional' and x['fold']==fold)) for fold,(i,j) in enumerate(player_splits(dev,4,F.SEED))]
    stages.append(('forward',dev,test,next(x['config'] for x in old['selection'] if x['family']=='conventional')))
    for label,tr,te,config in stages:
        if phase is not None and str(phase)!=label:continue
        if set(tr.nfl_id)&set(te.nfl_id):raise ValueError('original player leakage')
        groups={k:g for k,g in tr.groupby('nfl_id')};units=tr[['nfl_id','draft_year']].drop_duplicates();rng=np.random.default_rng(F.SEED+2300+int(label) if label!='forward' else F.SEED+2400)
        checkpoint=out/f'private_checkpoint_{label}.json';pred={k:np.zeros(len(te)) for k in FAMILIES};start=0
        if checkpoint.exists():
            saved=json.loads(checkpoint.read_text());assert saved['count']==count and saved['ids']==te.nfl_id.tolist();pred={k:np.array(v) for k,v in saved['pred'].items()};rng.bit_generator.state=saved['rng'];start=saved['done']
        for iteration in range(start,count):
            blocks=[];replica=0
            for _,g in units.groupby('draft_year'):
                for player in rng.choice(g.nfl_id.to_numpy(),len(g),replace=True):
                    q=groups[player].copy();q['nfl_id']=-1-replica;replica+=1;blocks.append(q)
            boot=pd.concat(blocks,ignore_index=True)
            for family in FAMILIES:pred[family]+=F.fit_predict(boot,te,cc[family],F.CONFIGS[config],'pressure_event')/count
            checkpoint.write_text(json.dumps({'count':count,'done':iteration+1,'ids':te.nfl_id.tolist(),'rng':rng.bit_generator.state,'pred':{k:v.tolist() for k,v in pred.items()}}));print(label,'replicate',iteration+1,flush=True)
        q=te[['nfl_id','pressure_event']].copy()
        for k,v in pred.items():q[k]=v
        q.to_pickle(out/f'private_predictions_{label}.pkl')
    if not all((out/f'private_predictions_{k}.pkl').exists() for k in ['0','1','2','3','forward']):return {'status':'checkpointed'}
    result={'protocol':'Previously conventional-selected fold-local and 2024 configs locked, identical 16 whole-athlete bootstraps per family. No new feature/config search. All scaling, physical residualization and PCA refitted inside each training resample. Four source availability flags and sprint availability shared.','bag_count':count,'prior_2025_inspection':True,'families':{k:len(v) for k,v in cc.items()},'nested':evaluate(pd.concat([pd.read_pickle(out/f'private_predictions_{k}.pkl') for k in range(4)])),'exploratory_2025':evaluate(pd.read_pickle(out/'private_predictions_forward.pkl'))}
    (out/'results.json').write_text(json.dumps(result,indent=2));return result

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--phase');args=ap.parse_args()
    if args.prepare:prepare()
    else:print(json.dumps(run(phase=args.phase),indent=2))
