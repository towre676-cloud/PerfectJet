#!/usr/bin/env python3
"""Replay the first seventh-mass-response minimality theorem.

The theorem concerns the selected physical threshold-nine ordinary scalar at
rho=1, where m_7^2=M rho and d_rho I|_1 = M J64.  It proves that the joint
physical observable (I, M J64) has exact rational flat rank 16 over C(s,t).
"""
from __future__ import annotations
import json, gzip, hashlib, subprocess, sys
from pathlib import Path
from fractions import Fraction

HERE=Path(__file__).resolve().parent
THRESH=(HERE/'threshold9_physical_seed_certificate.json' if (HERE/'threshold9_physical_seed_certificate.json').exists() else HERE/'recovered-research/annular-periods/physics/causal_activation/field/threshold9_physical_seed_certificate.json')
SCRIPTS=['joint_mass_response_build.py','verify_full_relation_ring.py','build_direct_mass_readout.py']

def run(name):
    p=subprocess.run([sys.executable,str(HERE/name)],cwd=HERE,text=True,capture_output=True)
    if p.returncode:
        print(p.stdout); print(p.stderr,file=sys.stderr); raise SystemExit(p.returncode)
    return p.stdout

def load(path):
    path=Path(path)
    if path.suffix=='.gz':
        with gzip.open(path,'rt') as f:return json.load(f)
    return json.load(open(path))

def sha(path):
    h=hashlib.sha256(); h.update(Path(path).read_bytes()); return h.hexdigest()

def frac(x): return Fraction(str(x))

# Recompute the three exact algebraic layers.
logs={name:run(name) for name in SCRIPTS}
joint=load(HERE/'joint_mass_response_certificate.json')
hyp=load(HERE/'physical_mass_response_hyperplane_certificate.json')
readout=load(HERE/'physical_J64_readout_certificate.json')
threshold=load(THRESH)
physical=load(HERE/'physical_minimality_certificate.json')

# The rational splitting coefficients have possible denominators only in the
# listed lower-sector letters after cancellation.  Check them at (9,-3).
s=Fraction(9); t=Fraction(-3)
letters={
 's':s,
 'Q=3s^2+4st+4t^2':3*s*s+4*s*t+4*t*t,
 '7s+4t':7*s+4*t,
 's^2+st-t':s*s+s*t-t,
 '3s-4t':3*s-4*t,
 'st-s-t':s*t-s-t,
}
regular={k:str(v) for k,v in letters.items() if v!=0}
assert len(regular)==len(letters)
q2=s/(t*(s+t))
assert q2!=0
expected_support=[9,10,12,23,24,25,26,33,34,35,36,51,52,54,55,57]

checks={
 'universal_joint_rank_18': joint['all_checks_passed'] and joint['universal_joint_dimension']==18,
 'physical_Gram_restriction_rank_17': joint['physical_joint_dimension']==17 and joint['checks']['physical_Gram_relation_omits_new_row'],
 'lower_joint_rank_13_before_boundary': joint['physical_lower_dimension']==13,
 'mass_character_exact': joint['new_row_connection']['s']['self_coefficient'] and joint['new_row_connection']['t']['self_coefficient'],
 'hyperplane_24_exact_PDE_identities': hyp['all_checks_passed'] and len(hyp['checks'])==24 and all(hyp['checks'].values()),
 'mass_hyperplane_support_exact': readout['Hmass_source_support_original_indices']==expected_support,
 'mass_hyperplane_uses_no_dotted64_or_top60_64': all(i<60 for i in expected_support) and 64 not in expected_support,
 'splitting_coefficients_regular_at_threshold': len(regular)==len(letters),
 'mass_character_unit_nonzero_at_threshold': q2==Fraction(-1,2),
 'physical_threshold_certificate_passes': threshold['all_checks_passed'] and threshold['physical_ordinary_threshold_solution_identified'],
 'threshold_certificate_identifies_only_index64_as_squared': threshold['checks']['only index64 has a squared physical propagator'],
 'threshold_germ_is_O_h2_for_undotted_entries': 'undotted entries are h^(2-2epsilon)' in threshold['analytic_reason'].lower().lower(),
 'physical_J64_readout_exact_in_16_frame': readout['all_checks_passed'] and readout['checks']['physical_direct_readout_identity'],
 'ordinary_scalar_minimum_16_dependency': physical['all_checks_passed'] and physical['ordinary_physical_minimum']==16 and physical['physical_minimality_proved']['ordinary'],
}
assert all(checks.values()), {k:v for k,v in checks.items() if not v}

# Logic of the last step:
# Hmass/q is locally constant; q is finite/nonzero at the threshold, while all
# source coordinates in Hmass are undotted and hence O(h^2).  Thus Hmass=0 on
# the distinguished germ, and analytic continuation preserves zero.  The exact
# readout then supplies a rank-16 upper bound for (I,J64); I alone already has
# rank16, supplying the lower bound.
cert={
 'all_checks_passed':True,
 'theorem':'First seventh-mass-response minimum on the selected threshold-nine physical branch',
 'deformation':{'m7_squared':'M*rho','derivative_at_rho_1':'M*J64','fixed_parameters':['s','t','M']},
 'coefficient_field':'C(s,t)',
 'ranks':{
   'universal_joint_observable_I_J64':18,
   'after_physical_Gram_constraint':17,
   'lower_projection_before_mass_boundary':13,
   'selected_physical_joint_I_J64':16,
   'selected_physical_joint_I_d_rho_I':16,
 },
 'rank_filtration':'18 -> 17 -> 16',
 'mass_character':{
   'one_form':'(1/2) dlog[s/(t(s+t))]',
   'chi_s':'t/[2 s(s+t)]',
   'chi_t':'-(s+2t)/[2 t(s+t)]',
   'threshold_square_value':str(q2),
 },
 'physical_mass_hyperplane':{
   'definition':'H_mass = w + sum_{i=0}^{11} g_i z_i',
   'equation':'d H_mass = (1/2)dlog[s/(t(s+t))] H_mass',
   'source_support_original_indices':expected_support,
   'threshold_regular_denominator_values':regular,
   'boundary_argument':'All source coordinates in H_mass are lower undotted masters, hence O((s-9)^2) on the certified threshold germ. The character sqrt(s/[t(s+t)]) is finite and nonzero there, so the locally constant quotient has zero limit and H_mass vanishes identically on the selected germ and its analytic continuations.',
 },
 'direct_readout':{
   'certificate':'physical_J64_readout_certificate.json',
   'physical_frame_dimension':16,
   'identity':readout['identity'],
   'basepoint':readout['basepoint'],
   'basepoint_coefficients':readout['physical_J64_readout_basepoint_coefficients'],
 },
 'minimality_argument':{
   'upper_bound':'The exact direct readout reconstructs J64 from the existing physical 16-state scalar frame after the two physical invariant hyperplanes are imposed.',
   'lower_bound':'The first component I alone already has certified minimal rational flat rank 16.',
   'conclusion':'rank_phys(I,M J64)=rank_phys(I,d_rho I|_{rho=1})=16.',
 },
 'checks':checks,
 'scope':[
   'This is an infinitesimal first-mass-response theorem at rho=1.',
   'It does not prove that a finite unequal-mass family at rho != 1 has rank16.',
   'It does not transfer equal-mass differential-field minimality to the full unequal-mass family.',
   'It uses the selected threshold-nine physical boundary and its ordered analytic continuation.'
 ],
 'dependencies_sha256':{},
 'replay_logs_tail':{k:'\n'.join(v.splitlines()[-8:]) for k,v in logs.items()},
}
for p in [
 HERE/'joint_mass_response_certificate.json', HERE/'physical_mass_response_hyperplane_certificate.json',
 HERE/'physical_J64_readout_certificate.json', HERE/'physical_minimality_certificate.json', THRESH,
 HERE/'observable_quotient_jet0_rref.json.gz', HERE/'physical_quotient_jet0.json.gz', HERE/'integrated_connection.json.gz',
]: cert['dependencies_sha256'][str(p.relative_to(HERE))]=sha(p)
(HERE/'first_mass_response_minimum_certificate.json').write_text(json.dumps(cert,indent=2)+'\n')
print(json.dumps({'all_checks_passed':True,'rank_filtration':cert['rank_filtration'],'physical_minimum':16,'check_count':len(checks)},indent=2))
