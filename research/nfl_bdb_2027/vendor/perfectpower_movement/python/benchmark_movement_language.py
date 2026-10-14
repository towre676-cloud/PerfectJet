"""Exact population benchmarks and finite-path posterior checks, public synthetic data."""
from pathlib import Path
import sys,json,time,math,random
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
from perfectpower.movement_language import segment_channel,phase_summary

def main():
    rows=[];rng=random.Random(19)
    for n,k in ((61,4),(120,6),(200,8),(300,12)):
        costs=[[rng.random() for _ in range(k)] for _ in range(n)];t=time.perf_counter();c=segment_channel(costs,[1]*k,[n]*k,max_edges=1000000);setup=time.perf_counter()-t
        assert c.population==math.comb(n-1,k-1);t=time.perf_counter()
        for _ in range(1000):rank=rng.randrange(c.population);assert c.rank(c.unrank(rank))==rank
        ranking=time.perf_counter()-t;t=time.perf_counter();r=c.moments();moment=time.perf_counter()-t
        assert abs(sum(r['mean'])-n)<1e-6
        rows.append({'frames':n,'phases':k,'count':str(c.population),'edges':len(c.edges),'build_seconds':setup,'rank_roundtrips':1000,'rank_seconds':ranking,'moment_seconds':moment,'duration_sum_error':abs(sum(r['mean'])-n),'scope':'Synthetic fixed observation weights; population and rank exact, posteriors floating.'})
        print(json.dumps(rows[-1]),flush=True)
    p=ROOT/'receipts/movement_language/benchmark.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'cases':rows,'rank_roundtrips':4000},indent=2)+'\n')
if __name__=='__main__':main()
