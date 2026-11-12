"""Reconstruct cubic arc input and the independent weight7 VOA character."""
from pathlib import Path
import json
from perfectjet.asterion_kernel_characters import kernel_characters_receipt
from perfectjet.asterion_kernel_tower import E8Freudenthal
r=kernel_characters_receipt(max_weight=6);assert r['passed']
Path('arc_length3_replay.json').write_text(json.dumps(r,default=str,indent=2)+'\n')
v=E8Freudenthal(7).voa_character(7);assert v['passed']
Path('VOA_weight7_character.json').write_text(json.dumps(v,default=str,indent=2)+'\n')
print('Cubic arc and VOA7 characters reconstructed:',v['reconstructed_dimension'])
