import sys,json,time
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import joint_mass_response_build as jb
R,S,T=jb.R,jb.S,jb.T; Rat=jb.Rat

def poly_from_coeff(path,index=0):
 d=json.load(open(path));mons=[tuple(x) for x in d['mons']];cc=[Fraction(x) for x in d['coeffs']];n=len(mons)
 vals=cc[index*n:(index+1)*n]
 return R.from_dict({(a,b):jb.QQ.convert(c) for (a,b),c in zip(mons,vals) if c})
def pp(*items):
 z=R.one
 for x in items:z*=x
 return z
Q=3*S*S+4*S*T+4*T*T
A1=S*S+S*T-T
# first formulas directly
g=[Rat() for _ in range(12)]
g[0]=Rat(T*(S+T)*(S+2*T), S*Q)
g[1]=Rat(S*T*(S+T)*(S+2*T), Q)
# g345 reconstructed ansatz denominator, Rat cancels exact gcds
D345=Q*(7*S+4*T)*A1*(S*S+S*T-9*T)*S*T
for ii,j in enumerate([3,4,5]):g[j]=Rat(poly_from_coeff(HERE/'g345_coeffs.json',ii),D345)
# g78 full ansatz denominator
A4=S*S+S*T-4*T; B2=S*T-2*S-4*T;B4=S*T-4*S-4*T;B9=S*T-9*S-9*T;B1=S*T-S-T
D78=S*Q*(7*S+4*T)*A1*(3*S-4*T)*A4*B2*B4*B9*B1
for ii,j in enumerate([7,8]):g[j]=Rat(poly_from_coeff(HERE/'g78_coeffs_big.json',ii),D78)
# final common D used in modular ansatz
A2=S*S+S*T-2*S-4*T;A9=S*S+S*T-9*T
Dfinal=S*T*(S+T)*(3*S-4*T)*(7*S+4*T)*Q*A2*A4*A9*A1*B2*B4*B9*B1
for j in [10,11]:g[j]=Rat(poly_from_coeff(HERE/f'g{j}_coeffs_big.json',0),Dfinal)
print('functions built',flush=True)
checks={}
for ax in ['s','t']:
 A=jb.LOW[ax];chi=A[12].get(12,Rat())
 for j in range(12):
  lhs=g[j].derivative(ax)
  for i in range(12):
   a=A[i].get(j)
   if a and g[i]:lhs=lhs+g[i]*a
  u=A[12].get(j)
  if u:lhs=lhs+u
  if g[j]:lhs=lhs-chi*g[j]
  ok=not lhs;checks[f'{ax}_{j}']=ok
  print(ax,j,ok,flush=True)
  if not ok: print('RES',lhs,flush=True);raise SystemExit(2)
# base exact values
vals=[]
def evalrat(x,sv,tv):
 def ev(poly):
  tot=Fraction(0)
  for (a,b),c in poly.terms(): tot += Fraction(str(c))*(Fraction(sv)**a)*(Fraction(tv)**b)
  return tot
 return ev(x.p)/ev(x.q)
for i,x in enumerate(g):
 v=evalrat(x,12,-3);vals.append(str(v));print('base',i,v,flush=True)
out={'all_checks_passed':all(checks.values()),'checks':checks,'relation_twist':{'s':str(jb.chi['s']),'t':str(jb.chi['t'])},'basepoint':[12,-3],'base_coefficients':vals}
open(HERE/'physical_mass_response_hyperplane_certificate.json','w').write(json.dumps(out,indent=2)+'\n')
print('PASS',flush=True)
