import sys,json,gzip,hashlib
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).parent))
import joint_mass_response_build as jb
R,S,T=jb.R,jb.S,jb.T; Rat=jb.Rat
HERE=Path(__file__).resolve().parent

def poly_from_coeff(path,index=0):
 d=json.load(open(path));mons=[tuple(x) for x in d['mons']];cc=[Fraction(x) for x in d['coeffs']];n=len(mons)
 vals=cc[index*n:(index+1)*n]
 return R.from_dict({(a,b):jb.QQ.convert(c) for (a,b),c in zip(mons,vals) if c})

def build_g():
 Q=3*S*S+4*S*T+4*T*T; A1=S*S+S*T-T
 g=[Rat() for _ in range(12)]
 g[0]=Rat(T*(S+T)*(S+2*T), S*Q)
 g[1]=Rat(S*T*(S+T)*(S+2*T), Q)
 D=Q*(7*S+4*T)*A1*(S*S+S*T-9*T)*S*T
 for ii,j in enumerate([3,4,5]):g[j]=Rat(poly_from_coeff(HERE/'g345_coeffs.json',ii),D)
 A4=S*S+S*T-4*T; B2=S*T-2*S-4*T; B4=S*T-4*S-4*T; B9=S*T-9*S-9*T; B1=S*T-S-T
 D=S*Q*(7*S+4*T)*A1*(3*S-4*T)*A4*B2*B4*B9*B1
 for ii,j in enumerate([7,8]):g[j]=Rat(poly_from_coeff(HERE/'g78_coeffs_big.json',ii),D)
 A2=S*S+S*T-2*S-4*T; A9=S*S+S*T-9*T
 D=S*T*(S+T)*(3*S-4*T)*(7*S+4*T)*Q*A2*A4*A9*A1*B2*B4*B9*B1
 for j in [10,11]:g[j]=Rat(poly_from_coeff(HERE/f'g{j}_coeffs_big.json'),D)
 return g

def encrow(vals):
 return [[i,*jb.enc(x)] for i,x in enumerate(vals) if x]

def sha(path):
 h=hashlib.sha256(); h.update(Path(path).read_bytes()); return h.hexdigest()

def evalrat(x,sv,tv):
 def ev(poly):
  total=Fraction(0)
  for (a,b),c in poly.terms(): total += Fraction(str(c))*(Fraction(sv)**a)*(Fraction(tv)**b)
  return total
 return ev(x.p)/ev(x.q)

g=build_g()
# Recompute exact J64 reduction against universal scalar17.
v=jb.zero();v[37]=Rat(R.one)
rem,co=jb.reduce(v,jb.basis,jb.piv)
scale=rem[30]
assert all((rem[j] == scale*jb.r[j]) for j in range(38))
# Replace new line by physical hyperplane relation r = -sum g_k z_{5+k}.
d=list(co)
for k in range(12):
 d[5+k]=d[5+k]-scale*g[k]
# Physical Gram relation eliminates universal coordinate 4.
rel=[Rat() for _ in range(17)]
with gzip.open(HERE/'physical_quotient_jet0.json.gz','rt') as f:pq=json.load(f)
for j,num,den in pq['constraint_covector']:rel[j]=jb.dec(num,den)
assert rel[4]
ret=[i for i in range(17) if i!=4]
dp={j:d[j]-d[4]*(rel[j]/rel[4]) for j in ret}
# Construct H source row and Gram source row.
H=[Rat() for _ in range(38)]
for j,a in enumerate(jb.r):H[j]=H[j]+a
for k in range(12):
 if g[k]:
  for j,a in jb.basis[5+k].items():H[j]=H[j]+g[k]*a
G=[Rat() for _ in range(38)]
for i,a in enumerate(rel):
 if a:
  for j,b in jb.basis[i].items():G[j]=G[j]+a*b
# Direct source-row identity.
res=jb.zero();res[37]=Rat(R.one)
for i,c in dp.items():
 if c:
  for j,a in jb.basis[i].items():res[j]=res[j]-c*a
rhs=[scale*H[j]+(d[4]/rel[4])*G[j] for j in range(38)]
checks={
 'J64_reduction_exact': all(rem[j]==scale*jb.r[j] for j in range(38)),
 'physical_direct_readout_identity': all(res[j]==rhs[j] for j in range(38)),
 'hyperplane_source_has_no_top_or_dotted_support': all(not H[j] for j,o in enumerate(jb.src['original_indices']) if o>=60),
 'hyperplane_source_support_is_expected': [jb.src['original_indices'][j] for j,a in enumerate(H) if a]==[9,10,12,23,24,25,26,33,34,35,36,51,52,54,55,57],
 'physical_readout_has_16_coordinates': len(dp)==16,
}
assert all(checks.values()),checks
out={
 'all_checks_passed':True,
 'checks':checks,
 'target':'J64, equivalently M J64 at fixed nonzero M after scalar multiplication',
 'universal_scalar_basis_dimension':17,
 'physical_scalar_basis_dimension':16,
 'eliminated_Gram_universal_index':4,
 'physical_retained_universal_indices':ret,
 'J64_universal_scalar_reduction_coefficients':encrow(co),
 'J64_new_line_scale':jb.enc(scale),
 'mass_hyperplane_lower_coefficients':encrow(g),
 'physical_J64_readout_coefficients':[[i,*jb.enc(dp[i])] for i in ret],
 'identity': 'e37 - sum_i dphys_i*basis_i = scale*Hmass_source + (d4/rel4)*Gram_source',
 'Hmass_source_support_original_indices':[jb.src['original_indices'][j] for j,a in enumerate(H) if a],
 'Hmass_source_row':[[j,jb.src['original_indices'][j],*jb.enc(a)] for j,a in enumerate(H) if a],
 'Gram_source_row':[[j,jb.src['original_indices'][j],*jb.enc(a)] for j,a in enumerate(G) if a],
 'basepoint':[12,-3],
 'physical_J64_readout_basepoint_coefficients':[[i,str(evalrat(dp[i],12,-3))] for i in ret],
 'dependency_sha256':{p.name:sha(p) for p in [HERE/'joint_mass_response_certificate.json',HERE/'physical_quotient_jet0.json.gz',HERE/'observable_quotient_jet0_rref.json.gz',HERE/'g345_coeffs.json',HERE/'g78_coeffs_big.json',HERE/'g10_coeffs_big.json',HERE/'g11_coeffs_big.json']},
 'scope':'Exact readout on the distinguished physical branch once the independently verified Gram relation and mass-response hyperplane vanish. This does not assert rank16 away from rho=1.'
}
(HERE/'physical_J64_readout_certificate.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'all_checks_passed':True,'physical_dimension':16,'H_support':out['Hmass_source_support_original_indices'],'base_coefficients':out['physical_J64_readout_basepoint_coefficients']},indent=2))
