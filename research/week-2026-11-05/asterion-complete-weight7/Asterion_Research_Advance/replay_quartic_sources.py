"""Fresh full lattice null replays supporting the small-sector product theorem."""
from pathlib import Path
import json
from perfectjet.asterion_primitives import (JetAlgebra,LatticeE8VOA,_weight_four_replay,
    load_certificates,verify_primitive_certificate,decode_polynomial,quartic_singlet_decision)
from perfectjet.asterion_quartic import quartic_receipt

j=JetAlgebra()
r4=_weight_four_replay(LatticeE8VOA(j));assert r4['passed']
Path('weight4_3875_source_replay.json').write_text(json.dumps(r4,indent=2)+'\n')
record=load_certificates()['sectors']['w5-248']
r5=verify_primitive_certificate(record,j,lattice_replay=True);assert r5['passed']
singlet=quartic_singlet_decision(j,decode_polynomial(record['representatives'][0]['symbol']))
assert singlet['passed']
Path('weight5_adjoint_source_replay.json').write_text(json.dumps({'source_replay':r5,'quartic_product':singlet},default=str,indent=2)+'\n')
r6=quartic_receipt();assert r6['passed']
Path('weight6_quartic_source_replay.json').write_text(json.dumps(r6,default=str,indent=2)+'\n')
print('Weight4 null, weight5 null, F0 product identity and weight6 quartic theorem replayed.')
