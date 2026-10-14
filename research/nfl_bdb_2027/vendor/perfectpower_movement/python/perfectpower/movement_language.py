"""Finite weighted movement languages with exact populations and numerical inference.

This is a generic DAG/explicit-duration model, not a claim of athlete quantum
physics. Counts and ranks are exact; log-weight posteriors use binary64.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import exp, log, factorial, isfinite, inf
import random

@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    log_weight: float = 0.
    reward: tuple = ()
    label: object = None


def logsum(values):
    values=list(values)
    if not values:return -inf
    maximum=max(values)
    return maximum+log(sum(exp(v-maximum) for v in values)) if maximum!=-inf else -inf


class MovementLanguage:
    """An acyclic, finite word channel; parallel edges are labeled alternatives."""
    def __init__(self, nodes, edges, start, terminals, max_edges=200000):
        if type(nodes) is not int or not 1<=nodes<=100000:raise ValueError('node budget')
        if type(max_edges) is not int or max_edges<0:raise ValueError('edge budget')
        self.nodes=nodes;self.edges=list(edges);self.start=start;self.terminals=frozenset(terminals)
        if len(self.edges)>max_edges:raise ValueError('edge budget')
        if type(start) is not int or not 0<=start<nodes or any(type(v) is not int or not 0<=v<nodes for v in self.terminals):raise ValueError('invalid endpoint')
        self.dimension=len(self.edges[0].reward) if self.edges else 0
        if self.dimension>128:raise ValueError('reward budget')
        self.out=[[] for _ in range(nodes)];self.inc=[[] for _ in range(nodes)]
        for i,e in enumerate(self.edges):
            if type(e.source) is not int or type(e.target) is not int or not 0<=e.source<e.target<nodes:raise ValueError('edges must advance topological order')
            if not isfinite(e.log_weight) or len(e.reward)!=self.dimension or any(not isfinite(x) for x in e.reward):raise ValueError('nonfinite or inconsistent reward')
            if e.source in self.terminals:raise ValueError('terminal must be absorbing')
            self.out[e.source].append(i);self.inc[e.target].append(i)
        self.count=[0]*nodes;self.backward=[-inf]*nodes;self.best=[-inf]*nodes
        for v in range(nodes-1,-1,-1):
            if v in self.terminals:self.count[v]=1;self.backward[v]=self.best[v]=0.
            else:
                self.count[v]=sum(self.count[self.edges[i].target] for i in self.out[v])
                self.backward[v]=logsum(self.edges[i].log_weight+self.backward[self.edges[i].target] for i in self.out[v])
                self.best[v]=max((self.edges[i].log_weight+self.best[self.edges[i].target] for i in self.out[v]),default=-inf)
        self.forward=[-inf]*nodes;self.forward[start]=0.
        for v in range(nodes):
            if v!=start:self.forward[v]=logsum(self.forward[self.edges[i].source]+self.edges[i].log_weight for i in self.inc[v])
        self.log_partition=self.backward[start]

    @property
    def population(self):return self.count[self.start]

    def conditional_count(self,prefix=()):
        node=self.start
        for i in prefix:
            if type(i) is not int or i not in self.out[node]:return 0
            node=self.edges[i].target
        return self.count[node]

    def unrank(self,index):
        if type(index) is not int or not 0<=index<self.population:raise ValueError('rank outside language')
        node=self.start;path=[]
        while node not in self.terminals:
            for i in self.out[node]:
                target=self.edges[i].target
                if index<self.count[target]:path.append(i);node=target;break
                index-=self.count[target]
            else:raise RuntimeError('inconsistent counts')
        return path

    def rank(self,path):
        node=self.start;rank=0
        for i in path:
            if type(i) is not int or i not in self.out[node]:raise ValueError('invalid path')
            for j in self.out[node]:
                if j==i:break
                rank+=self.count[self.edges[j].target]
            node=self.edges[i].target
        if node not in self.terminals:raise ValueError('incomplete path')
        return rank

    def sample(self,seed=None,weighted=True):
        if not self.population:raise ValueError('empty language')
        rng=random.Random(seed)
        if not weighted:return self.unrank(rng.randrange(self.population))
        node=self.start;path=[]
        while node not in self.terminals:
            bank=[i for i in self.out[node] if self.count[self.edges[i].target]]
            probabilities=[exp(self.edges[i].log_weight+self.backward[self.edges[i].target]-self.backward[node]) for i in bank]
            u=rng.random()*sum(probabilities);i=bank[-1]
            for j,p in zip(bank,probabilities):
                u-=p
                if u<0:i=j;break
            path.append(i);node=self.edges[i].target
        return path

    def map_path(self):
        if not self.population:raise ValueError('empty language')
        node=self.start;path=[]
        while node not in self.terminals:
            i=max(self.out[node],key=lambda i:self.edges[i].log_weight+self.best[self.edges[i].target])
            path.append(i);node=self.edges[i].target
        return path

    def edge_posterior(self):
        if not self.population:return [0.]*len(self.edges)
        return [exp(self.forward[e.source]+e.log_weight+self.backward[e.target]-self.log_partition) if self.forward[e.source]!=-inf and self.backward[e.target]!=-inf else 0. for e in self.edges]

    def moments(self):
        """Additive reward means, marginal variances and all-path support bounds."""
        if not self.population:raise ValueError('empty language')
        d=self.dimension;mean=[[0.]*d for _ in range(self.nodes)];variances=[[0.]*d for _ in range(self.nodes)]
        lower=[[inf]*d for _ in range(self.nodes)];upper=[[-inf]*d for _ in range(self.nodes)]
        for v in range(self.nodes-1,-1,-1):
            if v in self.terminals:lower[v]=upper[v]=[0.]*d;continue
            branches=[]
            for i in self.out[v]:
                e=self.edges[i];t=e.target
                if not self.count[t]:continue
                p=exp(e.log_weight+self.backward[t]-self.backward[v]);branches.append((e,p))
                for j,r in enumerate(e.reward):
                    mean[v][j]+=p*(r+mean[t][j])
                    lower[v][j]=min(lower[v][j],r+lower[t][j]);upper[v][j]=max(upper[v][j],r+upper[t][j])
            # Conditional variance avoids subtracting nearly equal raw moments.
            for e,p in branches:
                for j,r in enumerate(e.reward):variances[v][j]+=p*(variances[e.target][j]+(r+mean[e.target][j]-mean[v][j])**2)
        m=mean[self.start];variance=variances[self.start]
        expected_log=sum(p*e.log_weight for p,e in zip(self.edge_posterior(),self.edges))
        return {'mean':m,'variance':variance,'support_min':lower[self.start],'support_max':upper[self.start],
                'entropy_nats':max(0.,self.log_partition-expected_log),'map_probability':exp(self.best[self.start]-self.log_partition)}

    def exact_weighted(self,weights,rewards=None):
        """Rational reference calculation; never rationalize floating likelihoods."""
        if len(weights)!=len(self.edges):raise ValueError('weight length')
        if any(not isinstance(w,(int,Fraction)) or isinstance(w,bool) or w<0 for w in weights):raise ValueError('nonnegative rational weights required')
        rewards=[e.reward for e in self.edges] if rewards is None else rewards
        if len(rewards)!=len(self.edges) or any(len(r)!=self.dimension for r in rewards) or any(not isinstance(x,(int,Fraction)) or isinstance(x,bool) for r in rewards for x in r):raise ValueError('rational rewards required')
        z=[Fraction(0)]*self.nodes;a=[[Fraction(0)]*self.dimension for _ in range(self.nodes)];b=[[Fraction(0)]*self.dimension for _ in range(self.nodes)]
        for v in range(self.nodes-1,-1,-1):
            if v in self.terminals:z[v]=Fraction(1)
            else:
                for i in self.out[v]:
                    e=self.edges[i];t=e.target;w=weights[i];z[v]+=w*z[t]
                    for j,r in enumerate(rewards[i]):a[v][j]+=w*(r*z[t]+a[t][j]);b[v][j]+=w*(r*r*z[t]+2*r*a[t][j]+b[t][j])
        total=z[self.start]
        if not total:return {'partition':total,'mean':None,'variance':None}
        m=[x/total for x in a[self.start]]
        return {'partition':total,'mean':m,'variance':[s/total-x*x for s,x in zip(b[self.start],m)]}


def segment_channel(costs,min_duration,max_duration,rewards=None,temperature=1.,boundary_windows=None,max_edges=200000):
    """Compile all contiguous ordered phase segmentations into a DAG.

    Every frame belongs to one nonempty phase. Window k restricts the end of
    phase k (inclusive integers). Costs/rewards are per-frame observations.
    """
    costs=[tuple(row) for row in costs];n=len(costs)
    if not 1<=n<=4096:raise ValueError('observation window requires 1..4096 frames')
    k=len(costs[0]);minimum=list(min_duration);maximum=list(max_duration)
    if not 1<=k<=16 or len(minimum)!=k or len(maximum)!=k or any(type(a) is not int or type(b) is not int or not 1<=a<=b for a,b in zip(minimum,maximum)):raise ValueError('duration constraints')
    if not isfinite(temperature) or temperature<=0:raise ValueError('temperature must be positive')
    if any(len(c)!=k or any(not isfinite(x) for x in c) for c in costs):raise ValueError('invalid phase costs')
    windows=[(0,n)]*k if boundary_windows is None else boundary_windows
    if len(windows)!=k or any(len(w)!=2 or any(type(x) is not int for x in w) or not 0<=w[0]<=w[1]<=n for w in windows):raise ValueError('boundary windows')
    if rewards is None:rewards=[[tuple(1 if j==phase else 0 for j in range(k)) for phase in range(k)] for _ in range(n)]
    else:rewards=[[tuple(v) for v in row] for row in rewards]
    d=len(rewards[0][0])
    if len(rewards)!=n or any(len(row)!=k or any(len(v)!=d or any(not isfinite(x) for x in v) for v in row) for row in rewards):raise ValueError('invalid rewards')
    prefix=[[0.]*(n+1) for _ in range(k)];rp=[[[0.]*(n+1) for _ in range(d)] for _ in range(k)]
    for phase in range(k):
        for t in range(n):
            prefix[phase][t+1]=prefix[phase][t]+costs[t][phase]
            for j in range(d):rp[phase][j][t+1]=rp[phase][j][t]+rewards[t][phase][j]
    edges=[]
    for phase in range(k):
        for start in range(n):
            for end in range(start+minimum[phase],min(n,start+maximum[phase])+1):
                if not windows[phase][0]<=end<=windows[phase][1]:continue
                remain=n-end
                if not sum(minimum[phase+1:])<=remain<=sum(maximum[phase+1:]):continue
                if phase==0 and start!=0:continue
                r=tuple(rp[phase][j][end]-rp[phase][j][start] for j in range(d))
                edges.append(Edge(phase*(n+1)+start,(phase+1)*(n+1)+end,-(prefix[phase][end]-prefix[phase][start])/temperature,r,(phase,start,end)))
                if len(edges)>max_edges:raise ValueError('edge budget')
    channel=MovementLanguage((k+1)*(n+1),edges,0,[k*(n+1)+n],max_edges)
    channel.frames=n;channel.phases=k
    return channel


def phase_summary(channel):
    if not channel.population:raise ValueError('empty phase language')
    n,k=channel.frames,channel.phases;boundary=[{} for _ in range(k)];occupancy=[[0.]*k for _ in range(n)]
    for e,p in zip(channel.edges,channel.edge_posterior()):
        phase,a,b=e.label;boundary[phase][b]=boundary[phase].get(b,0.)+p
        for t in range(a,b):occupancy[t][phase]+=p
    def quantile(bank,q):
        total=sum(bank.values());c=0.
        for value,p in sorted(bank.items()):
            c+=p
            if c>=q*total:return value
        return max(bank)
    return {'count':str(channel.population),'log_partition':channel.log_partition,'boundary_quantiles':[[quantile(b,q) for q in (.05,.5,.95)] for b in boundary],
            'boundary_probability':boundary,'occupancy':occupancy,**channel.moments()}


def tensor_signature(points,degree=3):
    """Chen signature of a piecewise-linear path, up to degree three.

    Floating observations stay floating; order-dependent coordinates are not
    physiological quantum phases. A straight segment uses tensor exponential.
    """
    points=[tuple(map(float,p)) for p in points]
    if not points or degree not in (1,2,3):raise ValueError('points and degree 1..3 required')
    dim=len(points[0])
    if not 1<=dim<=6 or any(len(p)!=dim or any(not isfinite(x) for x in p) for p in points):raise ValueError('point dimension or finiteness')
    words=[list(product(range(dim),repeat=k)) for k in range(degree+1)]
    s=[{():1.}]+[{w:0. for w in words[k]} for k in range(1,degree+1)]
    for a,b in zip(points,points[1:]):
        delta=[y-x for x,y in zip(a,b)];e=[{():1.}]
        for k in range(1,degree+1):
            e.append({w:prod_float(delta[i] for i in w)/factorial(k) for w in words[k]})
        s=[{w:sum(s[j][w[:j]]*e[k-j][w[j:]] for j in range(k+1)) for w in words[k]} for k in range(degree+1)]
    return s


def prod_float(values):
    p=1.
    for v in values:p*=v
    return p


def main():
    import argparse,json
    parser=argparse.ArgumentParser(description='Finite movement segmentation populations and weighted uncertainty')
    parser.add_argument('input',help='JSON costs, min_duration, max_duration and optional rewards/temperature/boundary_windows')
    parser.add_argument('--rank',type=int);parser.add_argument('--samples',type=int,default=0);parser.add_argument('--seed',type=int,default=0)
    args=parser.parse_args()
    if not 0<=args.samples<=1000:parser.error('samples must be in 0..1000')
    with open(args.input) as f:spec=json.load(f)
    c=segment_channel(**spec)
    result=phase_summary(c) if c.population else {'count':'0','status':'empty_language'}
    if args.rank is not None:result['ranked_segments']=[c.edges[i].label for i in c.unrank(args.rank)]
    result['samples']=[[c.edges[i].label for i in c.sample(args.seed+j)] for j in range(args.samples)]
    result['arithmetic_scope']='Counts and ranks exact; likelihood-derived uncertainty uses floating arithmetic.'
    print(json.dumps(result))

if __name__=='__main__':main()
