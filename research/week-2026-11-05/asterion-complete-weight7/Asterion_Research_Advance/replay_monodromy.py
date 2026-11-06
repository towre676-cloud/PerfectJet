import json
from pathlib import Path
from perfectjet.asterion_monodromy import monodromy_group_receipt
r=monodromy_group_receipt(exhaustive=True)
assert r['passed'] and r['group_closure_certified_in_this_run']
Path('monodromy_replay.json').write_text(json.dumps(r,indent=2)+'\n')
print({key:r[key] for key in ('passed','group_closure_certified_in_this_run',
                             'compact_identity_component','projective_compact_closure')})
