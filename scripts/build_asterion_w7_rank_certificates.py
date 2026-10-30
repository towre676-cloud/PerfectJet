"""Build exact projected lattice rank certificates for the two missing sectors.

The polynomial columns and every projected image are retained. Intermediate
lattice states are unprojected. A projected-rank lower bound is combined with
known exact null lifts; projection alone cannot prove a vector is null.
Run from the repository root with PYTHONPATH=src.
"""
import gzip
import json,time
from perfectjet.asterion import source_digests
from perfectjet.asterion_kernel_tower import tensor_cube_character_receipt
import perfectjet.asterion_primitives as p
from perfectjet.asterion_lattice_projection import ProjectedLatticeE8VOA
from perfectjet.asterion import json_ready
j=p.JetAlgebra();l=ProjectedLatticeE8VOA(j)
reconstruction=tensor_cube_character_receipt()
open('results/asterion-primitives/w7-schur-reconstruction.json','w').write(json.dumps(reconstruction,indent=2,sort_keys=True)+'\n')
for d,t in [(1,p.ZERO),(248,p.THETA)]:
 print('start',d,flush=True);start=time.time()
 top,nt=j.highest_vectors(p.jet_shapes(3,4),t); lower=[]
 for length in (2,1):
  lower.extend(j.highest_vectors(p.jet_shapes(length,7-length),t)[0])
 print('columns',len(top),len(lower),flush=True)
 images=[]
 for i,c in enumerate(top+lower):
  images.append(l.symmetric_lift(c));print('image',i,len(images[-1]),time.time()-start,flush=True)
 rank=p.exact_rank(images)
 result={'schema':'perfectjet/asterion-w7-projected-rank/1','source_sha256':source_digests(),'dimension':d,'top_columns':nt,'top_highest':len(top),'lower_highest':len(lower),'projected_rank_Q':rank,'projected_nullity':len(top+lower)-rank,'support':sorted(l.support),'columns':[p.encode_polynomial(c) for c in top+lower],'images':[[[list(k[0]),[list(x) for x in k[1]],str(z)] for k,z in sorted(im.items())] for im in images]}
 open(f'results/asterion-primitives/w7-{d}-projected-rank.json.gz','wb').write(gzip.compress((json.dumps(json_ready(result),indent=2,sort_keys=True)+'\n').encode(),mtime=0))
 print('RESULT',d,rank,len(top+lower)-rank,flush=True);l.clear_cache()
