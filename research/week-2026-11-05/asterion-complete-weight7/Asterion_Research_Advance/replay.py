"""Replay this bounded research checkpoint; standard-library Python only."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parent
os.chdir(root)
env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(root/'src'),str(root/'tests'))))
parser=argparse.ArgumentParser()
parser.add_argument('--tests',action='store_true')
parser.add_argument('--monodromy',action='store_true')
parser.add_argument('--quartic',action='store_true',help='recompute the three small quartic sectors and null dependencies')
parser.add_argument('--weight7',action='store_true',help='regenerate the complete weight-seven proof')
args=parser.parse_args()
for script in ('quartic_schur_replay.py','braid_infinite_order_replay.py'):
    subprocess.run([sys.executable,script],env=env,check=True)
if args.quartic or args.weight7:
    for script in ('replay_quartic_sources.py','quartic_adjoint_ideal.py',
                   'quartic_singlet_ideal.py','quartic_3875_ideal.py',
                   'quartic_adjoint_products.py','quartic_3875_products.py',
                   'verify_quartic_small_matrices.py'):
        subprocess.run([sys.executable,script],env=env,check=True)
if args.weight7:
    def run(script,*arguments):
        subprocess.run([sys.executable,script,*map(str,arguments)],env=env,check=True)
    for script in ('replay_extra_primitives.py','quartic_30380_ideal.py',
                   'quartic_30380_products.py','quartic_30380_VOA.py',
                   'quartic_casimir_cutoff.py','weight7_short_and_long.py'):
        run(script)
    for dimension in (27000,1763125,2450240,4096000,6696000):
        run('quartic_remaining_sectors.py',dimension)
    (root/'quartic_zero_arc_27000.json').write_bytes((root/'quartic_full_27000.json').read_bytes())
    for dimension in (147250,779247):
        run('quartic_remaining_sectors.py',dimension,'--ideal-only')
        run('quartic_old_products.py',dimension)
    for dimension in (27000,147250,779247,1763125,2450240,4096000,6696000):
        run('verify_polynomial_spans.py',dimension)
    for script in ('verify_30380_and_cutoff.py','replay_weight7_characters.py','assemble_weight7_theorem.py'):
        run(script)
if args.tests:
    subprocess.run([sys.executable,'-m','unittest',
       'test_asterion_quartic_characters','test_asterion_lattice_projection',
       'test_asterion_lattice_projection4',
       'test_quartic_covariant_checkpoint',
       'test_weight7_complete',
       'test_asterion_braid.HalfBraidTests.test_exact_descent_hypotheses_and_tensor_parity',
       'test_asterion_braid.HalfBraidTests.test_exact_tw_model_relations_and_simplicity',
       'test_asterion_braid.HalfBraidTests.test_independent_decode_and_corruption_rejection',
       'test_asterion_braid.HalfBraidTests.test_half_spectrum_has_actual_and_projective_order34',
       '-v'],env=env,check=True)
if args.monodromy:
    subprocess.run([sys.executable,'replay_monodromy.py'],env=env,check=True)
