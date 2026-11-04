"""Reconstruct the exact ideal rank and translated adjoint nonmembership."""
import gzip
import json
import perfectjet.asterion_primitives as p
from perfectjet.asterion import json_ready,source_digests
j=p.JetAlgebra(); gi=p.g_tensor_i_highest(j,p.THETA); ideal=p.ideal_highest_images(j,gi,7)
s=p.load_certificates()['sectors']['w5-248']['representatives'][0]
symbol=j.derivative(j.derivative(p.decode_polynomial(s['symbol'])))
correction=j.derivative(j.derivative(p.decode_polynomial(s['correction'])))
r={'source_sha256':source_digests(),'ideal_source_highest_vectors':len(gi),'ideal_rank_Q':p.exact_rank(ideal),'ideal_plus_D2P_rank_Q':p.exact_rank(ideal+[symbol]),'ideal_source_vectors':[p.encode_polynomial(v) for v in gi],'derivative_symbol':p.encode_polynomial(symbol),'derivative_correction':p.encode_polynomial(correction),'source':'w5-248','derivative_order':2,'representative_sha256':p.digest([p.encode_polynomial(symbol),p.encode_polynomial(correction)])}
open('results/asterion-primitives/w7-adjoint-ideal.json.gz','wb').write(gzip.compress((json.dumps(json_ready(r),indent=2,sort_keys=True)+'\n').encode(),mtime=0))
print({k:r[k] for k in ('ideal_source_highest_vectors','ideal_rank_Q','ideal_plus_D2P_rank_Q')},flush=True)
