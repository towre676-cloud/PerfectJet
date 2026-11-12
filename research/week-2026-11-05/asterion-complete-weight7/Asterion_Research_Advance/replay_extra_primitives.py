"""Fresh full null and nonmembership checks for the other source classes."""
from pathlib import Path
import json
from perfectjet.asterion_primitives import JetAlgebra,verify_primitive_certificate
for source,output in (('primitive_147250_source.json','weight5_147250_source_replay.json'),
                      ('primitive_30380_source.json','weight6_30380_source_replay.json')):
    record=json.loads(Path(source).read_text())
    r=verify_primitive_certificate(record,JetAlgebra(),lattice_replay=True)
    assert r['passed']
    Path(output).write_text(json.dumps(r,indent=2)+'\n')
    print('Replayed full source null and nonmembership:',record['label'])
