"""Direct exact highest-space, differential-ideal and full lattice ranks.

Four-current enumeration uses a meet-in-the-middle weight join. Full8
Cartan support keeps every final lattice coordinate; no projection remains.
"""
from fractions import Fraction as Q
from collections import defaultdict
from math import factorial
from pathlib import Path
import argparse,json,time
from perfectjet.asterion_primitives import (JetAlgebra,jet_shapes,omega_pair,_add,
    exact_rank,encode_polynomial,rational_kernel,solve_combination)
from perfectjet.asterion_lattice_projection4 import ProjectedLatticeE8VOA4

class QuarticJets(JetAlgebra):
    def monomials(self,shape,target):
        if len(shape)!=4:return super().monomials(shape,target)
        shape=tuple(sorted(shape))
        def table(a,b):
            if a==b:return self._multisets(2,a)
            key=('mixed',a,b)
            if key not in self._pair_cache:
                out=defaultdict(list)
                for i in range(248):
                    for j in range(248):
                        w=tuple(x+y for x,y in zip(self.weights[i],self.weights[j]))
                        out[w].append(((i,a),(j,b)))
                self._pair_cache[key]=out
            return self._pair_cache[key]
        a=table(*shape[:2]);b=table(*shape[2:]);out=set()
        for w,left in a.items():
            right=b.get(tuple(x-y for x,y in zip(target,w)),())
            for x in left:
                for y in right:out.add(tuple(sorted(x+y)))
        return sorted(out)

def I_project(j,p):
    out={};C={m:z for m,z in __import__('perfectjet.asterion_primitives',fromlist=['_contraction'])._contraction(j,None,0,0).items()}
    for monomial,z in p.items():
        pair=[i for i,r in monomial if r==0];extra=tuple(x for x in monomial if x[1]!=0)
        assert len(pair)==2
        a,b=pair;_add(out,{monomial:z*Q(372,434)})
        for (u,v),c in omega_pair(j,a,b).items():
            _add(out,{tuple(sorted(((u,0),(v,0))+extra)):z*c*Q(31,434)})
        f=j.form(a,b)
        if f:
            for q,c in C.items():_add(out,{tuple(sorted(q+extra)):z*f*c*Q(6,434)})
    return out

SOURCES=((0,0,3),(0,1,2),(1,0,2),(1,1,1),(2,0,1),(3,0,0))
def ideal_images(j,sources):
    out=[]
    for p in sources:
        for k,a,b in SOURCES:
            image={}
            for monomial,z in p.items():
                pair=tuple(x for x in monomial if x[1]==0)
                freea=next(i for i,r in monomial if r==9);freeb=next(i for i,r in monomial if r==10)
                q={pair:Q(1)}
                for _ in range(k):q=j.derivative(q)
                free=tuple(sorted(((freea,a),(freeb,b))))
                for m,c in q.items():_add(image,{tuple(sorted(m+free)):z*c})
            out.append(image)
    return out

def run(dimension,ideal_only=False):
    character=json.loads(Path('quartic_schur_receipt.json').read_text())
    entry=next(x for x in character['weight7_length4_ambient']['irreducibles'] if x['dimension']==dimension)
    j=QuarticJets();labels=entry['dynkin_labels']
    target=tuple(int(sum(j.cartan_inverse[i][k]*labels[k] for k in range(8))) for i in range(8))
    middle,n=j.highest_vectors([(0,0,9,10)],target)
    print(dimension,'middle highests',len(middle),'monomials',n,flush=True)
    sources=[I_project(j,p) for p in middle]
    assert all(j.is_highest(p) for p in sources)
    ideal=ideal_images(j,sources);irank=exact_rank(ideal)
    print(dimension,'ideal rank',irank,flush=True)
    if ideal_only:
        result={'schema':'asterion/weight7-quartic-ideal-only/1','passed':True,
                'dimension':dimension,'target_root_coordinates':target,
                'source_multiplicity':entry['multiplicity'],'middle_source_multiplicity':len(middle),
                'ideal_rank_Q':irank,'arc_multiplicity':entry['multiplicity']-irank,
                'middle_highest_columns':[encode_polynomial(p) for p in middle],
                'projected_I_highest_columns':[encode_polynomial(p) for p in sources],
                'ideal_highest_columns':[encode_polynomial(p) for p in ideal],
                'source_completeness_by_character':True}
        Path(f'quartic_ideal_only_{dimension}.json').write_text(json.dumps(result,indent=2)+'\n')
        return
    if irank==entry['multiplicity']:
        result={'schema':'asterion/weight7-quartic-full-sector/1','passed':True,
                'dimension':dimension,'target_root_coordinates':target,
                'source_multiplicity':entry['multiplicity'],'middle_source_multiplicity':len(middle),
                'ideal_rank_Q':irank,'arc_multiplicity':0,'VOA_image_multiplicity':0,
                'kernel_multiplicity':0,'primitive_quotient_computed':True,
                'new_primitive_multiplicity':0,'source_completeness_by_character':True,
                'ideal_highest_columns':[encode_polynomial(p) for p in ideal],
                'lattice_evaluation_unnecessary':'The ideal already spans the complete character-certified source.'}
        Path(f'quartic_full_{dimension}.json').write_text(json.dumps(result,indent=2)+'\n')
        print('SECTOR',dimension,'arc0 image0 kernel0; ideal exhausts source',flush=True)
        return
    top,n=j.highest_vectors(jet_shapes(4,3),target)
    assert len(top)==entry['multiplicity']
    lower=[];lower_counts=[]
    for length in (1,2,3):
        vs,count=j.highest_vectors(jet_shapes(length,7-length),target)
        lower.extend(vs);lower_counts.append((length,len(vs),count))
    print(dimension,'top',len(top),'lower',len(lower),'top monomials',n,flush=True)
    lattice=ProjectedLatticeE8VOA4(j,support=tuple(range(8)))
    images=[]
    for i,p in enumerate(lower+top):
        images.append(lattice.symmetric_lift(p));print(dimension,'full image',i+1,'terms',len(images[-1]),flush=True)
    r0=exact_rank(images[:len(lower)]);r1=exact_rank(images);arc=len(top)-irank
    image_multiplicity=r1-r0;kernel=arc-image_multiplicity
    assert kernel>=0
    keys=sorted(set().union(*images));rows=[{i:im[k] for i,im in enumerate(images) if k in im} for k in keys]
    null=rational_kernel(rows,len(images));symbols=[]
    for v in null:
        symbol={}
        for i,z in v.items():
            if i>=len(lower):_add(symbol,top[i-len(lower)],z)
        symbols.append(symbol)
    assert exact_rank(ideal+symbols)-irank==kernel
    result={'schema':'asterion/weight7-quartic-full-sector/1','passed':True,
            'dimension':dimension,'target_root_coordinates':target,'source_multiplicity':len(top),
            'middle_source_multiplicity':len(middle),'ideal_rank_Q':irank,'arc_multiplicity':arc,
            'lower_counts':lower_counts,'lower_full_lattice_rank_Q':r0,'full_lattice_rank_Q':r1,
            'VOA_image_multiplicity':image_multiplicity,'kernel_multiplicity':kernel,
            'primitive_quotient_computed':False,'lattice_support':list(range(8)),
            'top_highest_columns':[encode_polynomial(p) for p in top],
            'lower_highest_columns':[encode_polynomial(p) for p in lower],
            'ideal_highest_columns':[encode_polynomial(p) for p in ideal],
            'nullspace_coordinates':[[[i,str(z)] for i,z in sorted(v.items())] for v in null],
            'full_lattice_columns':[[[list(beta),[list(v) for v in osc],str(z)] for (beta,osc),z in sorted(im.items())] for im in images]}
    path=Path(f'quartic_full_{dimension}.json');path.write_text(json.dumps(result,indent=2)+'\n')
    print('SECTOR',dimension,'arc',arc,'image',image_multiplicity,'kernel',kernel,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('dimension',type=int);p.add_argument('--ideal-only',action='store_true')
    a=p.parse_args();run(a.dimension,a.ideal_only)
