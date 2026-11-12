"""Resolve the second arc copy by full lower-length corrected image ranks."""
from fractions import Fraction as Q
from pathlib import Path
import json,time
from perfectjet.asterion_primitives import (JetAlgebra,OMEGA_30380,THETA,jet_shapes,
    _contraction,_add,exact_rank,encode_polynomial)
from perfectjet.asterion_lattice_projection4 import ProjectedLatticeE8VOA4

def run():
    j=JetAlgebra();lower=[];counts=[]
    for length in (1,2,3):
        start=time.time();vs,n=j.highest_vectors(jet_shapes(length,7-length),OMEGA_30380)
        lower.extend(vs);counts.append({'length':length,'monomial_columns':n,'highest_count':len(vs)})
        print('Lower length',length,'highest',len(vs),'columns',n,'seconds',round(time.time()-start,2),flush=True)
    u=j.algebra.root_index[THETA];v=j.algebra.root_index[(2,4,6,5,4,3,1,3)]
    pair={tuple(sorted(((u,0),(v,1)))):Q(1,2),tuple(sorted(((v,0),(u,1)))):Q(-1,2)}
    symbol=j.multiply(pair,_contraction(j,None,0,2));assert j.is_highest(symbol)
    lattice=ProjectedLatticeE8VOA4(j,support=(0,1))
    images=[]
    for i,p in enumerate(lower+[symbol]):
        image=lattice.symmetric_lift(p);images.append(image)
        print('Projected column',i+1,'terms',len(image),flush=True)
    rank0=exact_rank(images[:-1]);rank1=exact_rank(images)
    print('Lower projected rank',rank0,'with quartic',rank1,flush=True)
    record={'schema':'asterion/weight7-quartic-30380-VOA/1','passed':rank1==rank0+1,
            'lower_highest_counts':counts,'lower_projected_rank_Q':rank0,
            'with_quartic_projected_rank_Q':rank1,'quartic_symbol':encode_polynomial(symbol),
            'lower_highest_columns':[encode_polynomial(p) for p in lower],
            'projected_image_columns':[[[list(beta),[list(x) for x in osc],str(z)] for (beta,osc),z in sorted(im.items())] for im in images],
            'support':[0,1],'arc_multiplicity':2,
            'known_product_kernel_multiplicity_lower_bound':1,
            'VOA_image_multiplicity':1 if rank1==rank0+1 else None,
            'kernel_multiplicity':1 if rank1==rank0+1 else None,
            'new_primitive_multiplicity':0 if rank1==rank0+1 else None,
            'argument':'A rank increase after adjoining the quartic to all lower-length '
                'highest columns proves a nonzero associated-graded VOA image. With arc '
                'multiplicity2 and a known nonzero old product class in the kernel, '
                'this forces image multiplicity1 and kernel multiplicity1.'}
    Path('quartic_30380_VOA_receipt.json').write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':run()
