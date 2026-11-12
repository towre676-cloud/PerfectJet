import gzip,json,time,hashlib
from fractions import Fraction
from sympy.polys.rings import ring
from sympy import QQ
from pathlib import Path
HERE=Path(__file__).resolve().parent
R,S,T=ring('s,t',QQ); ZERO=R.zero; ONE=R.one

def P(terms):return R.from_dict({(int(a),int(b)):QQ.convert(Fraction(c)) for a,b,c in terms})
class Rat:
 __slots__=('p','q')
 def __init__(self,p=ZERO,q=ONE,reduced=False):
  if isinstance(p,Rat):self.p,self.q=p.p,p.q;return
  if not q:raise ZeroDivisionError
  if not p:self.p,self.q=ZERO,ONE;return
  if not reduced:
   g=p.gcd(q);p=p.exquo(g);q=q.exquo(g)
  lc=q.LC
  if lc!=1:p=p/lc;q=q/lc
  self.p,self.q=p,q
 def __bool__(self):return bool(self.p)
 def __neg__(self):return Rat(-self.p,self.q,True)
 def __add__(self,o):
  o=o if isinstance(o,Rat) else Rat(R.ground_new(o))
  if not self:return o
  if not o:return self
  if self.q==o.q:return Rat(self.p+o.p,self.q)
  g=self.q.gcd(o.q);a=self.q.exquo(g);b=o.q.exquo(g);p=self.p*b+o.p*a
  if not p:return Rat()
  h=p.gcd(g);return Rat(p.exquo(h),a*o.q.exquo(h),True)
 __radd__=__add__
 def __sub__(self,o):return self+(-o)
 def __rsub__(self,o):return Rat(R.ground_new(o))-self
 def __mul__(self,o):
  o=o if isinstance(o,Rat) else Rat(R.ground_new(o))
  if not self or not o:return Rat()
  g1=self.p.gcd(o.q);g2=o.p.gcd(self.q)
  return Rat(self.p.exquo(g1)*o.p.exquo(g2),self.q.exquo(g2)*o.q.exquo(g1),True)
 __rmul__=__mul__
 def __truediv__(self,o):
  o=o if isinstance(o,Rat) else Rat(R.ground_new(o))
  if not o:raise ZeroDivisionError
  return self*Rat(o.q,o.p,True)
 def derivative(self,axis):
  x=S if axis=='s' else T
  return Rat(self.p.diff(x)*self.q-self.p*self.q.diff(x),self.q*self.q)
 def __eq__(self,o):
  o=o if isinstance(o,Rat) else Rat(R.ground_new(o))
  return self.p==o.p and self.q==o.q
 def eval(self,sv,tv):return Fraction(self.p.evaluate(S,QQ.convert(Fraction(sv))).evaluate(T,QQ.convert(Fraction(tv))))/Fraction(self.q.evaluate(S,QQ.convert(Fraction(sv))).evaluate(T,QQ.convert(Fraction(tv))))
 def __str__(self):return str(self.p) if self.q==ONE else f'({self.p})/({self.q})'

def dec(num,den):return Rat(P(num),P(den))
def terms(poly):
 return [[int(m[0]),int(m[1]),str(Fraction(str(c)))] for m,c in poly.terms()]
def enc(x):return [terms(x.p),terms(x.q)]
def rowdict(row):return {j:dec(num,den) for j,num,den in row}
def matrix(entries,n):
 A=[{} for _ in range(n)]
 for i,j,num,den in entries:A[i][j]=dec(num,den)
 return A
def zero(n=38):return [Rat() for _ in range(n)]
def reduce(v,basis,piv):
 v=list(v);co=[]
 for b,p in zip(basis,piv):
  c=v[p];co.append(c)
  if c:
   for j,a in b.items():v[j]=v[j]-c*a
 return v,co
def cov(v,axis,A):
 out=[a.derivative(axis) if a else Rat() for a in v]
 for i,a in enumerate(v):
  if a:
   for j,b in A[i].items():out[j]=out[j]+a*b
 return out

def sparse(A):return [[i,j,*enc(v)] for i,row in enumerate(A) for j,v in row.items() if v]

st=time.time()
with gzip.open(HERE/'integrated_connection.json.gz','rt') as f:src=json.load(f)
with gzip.open(HERE/'observable_quotient_jet0_rref.json.gz','rt') as f:q=json.load(f)
with gzip.open(HERE/'physical_quotient_jet0.json.gz','rt') as f:pq=json.load(f)
basis=[rowdict(r) for r in q['basis']];piv=q['pivots']
# residual pure J64 modulo scalar-observable 17 frame
v=zero();v[37]=Rat(ONE)
rem,_=reduce(v,basis,piv);newpivot=max(i for i,a in enumerate(rem) if a);scale=rem[newpivot]
r=[a/scale if a else Rat() for a in rem]
assert newpivot==30
# source matrices
Asrc={ax:matrix(src['matrices'][ax]['A0'],38) for ax in ['s','t']}
# universal quotient matrices 17
U={ax:matrix(q['matrices'][ax],17) for ax in ['s','t']}
coefs={};chi={}
for ax in ['s','t']:
 x=cov(r,ax,Asrc[ax]);x,co=reduce(x,basis,piv);c=x[newpivot]
 for j,a in enumerate(r):
  if a:x[j]=x[j]-c*a
 assert not any(x)
 coefs[ax]=co;chi[ax]=c
 # expected no top coupling from new row
 assert all(not co[i] for i in range(4))
# universal joint 18 rows: old17 + r
J={}
for ax in ['s','t']:
 A=[dict(row) for row in U[ax]]+[{}]
 for j,c in enumerate(coefs[ax]):
  if c:A[17][j]=c
 A[17][17]=chi[ax]
 J[ax]=A
# physical Gram relation in universal17 coords, zero new coefficient
relation=[Rat() for _ in range(18)]
for j,num,den in pq['constraint_covector']:relation[j]=dec(num,den)
removed=4
assert relation[removed]
retained=[i for i in range(18) if i!=removed];ratios=[relation[j]/relation[removed] for j in retained]
PH={}
for ax in ['s','t']:
 A=J[ax];B=[]
 for i in retained:
  row={}
  for jj,k in enumerate(retained):
   val=A[i].get(k,Rat())-A[i].get(removed,Rat())*ratios[jj]
   if val:row[jj]=val
  B.append(row)
 PH[ax]=B
# lower physical13 = old lower universal indices5..16? retained coordinate positions corresponding universal indices4..16 plus new17,
# but Gram eliminates universal4, leaving universal5..16 (12 rows) + new17 =13.
low_universal=list(range(5,17))+[17]
low_pos=[retained.index(i) for i in low_universal]
LOW={}
for ax in ['s','t']:
 B=PH[ax];C=[]
 for i in low_pos:
  row={}
  for jj,j in enumerate(low_pos):
   val=B[i].get(j,Rat())
   if val:row[jj]=val
  # verify closure: no outputs outside lower positions
  assert all((k in low_pos) for k in B[i] if B[i][k]),(ax,i,[k for k in B[i] if k not in low_pos])
  C.append(row)
 LOW[ax]=C
# checks: old lower12 physical + new r
checks={
 'new_target_independent_of_scalar17':bool(scale),
 'new_residual_pivot30':newpivot==30,
 'new_residual_six_sparse':sum(bool(a) for a in r)==6,
 'new_row_couples_only_to_old_lower13':all(not coefs[a][i] for a in ['s','t'] for i in range(4)),
 'physical_joint_dimension17':len(retained)==17,
 'physical_lower_dimension13':len(low_pos)==13,
 'physical_Gram_relation_omits_new_row':not relation[17],
 'all_checks_passed':True,
}
assert all(checks.values())
out={
 'all_checks_passed':True,'checks':checks,'source_dimension':38,'universal_scalar_dimension':17,'universal_joint_dimension':18,'physical_joint_dimension':17,'physical_lower_dimension':13,
 'targets':{'I_restricted_index':src['scalar_restricted_index'],'MJ64_restricted_index':37,'M_convention':'fixed nonzero mass scale; scalar multiplication does not alter closure rank'},
 'new_residual_row':[[i,*enc(a)] for i,a in enumerate(r) if a], 'new_residual_pivot':newpivot,'J64_reduction_scale':enc(scale),
 'new_row_connection':{ax:{'old_scalar_frame_coefficients':[[i,*enc(a)] for i,a in enumerate(coefs[ax]) if a],'self_coefficient':enc(chi[ax])} for ax in ['s','t']},
 'universal_joint_matrices':{ax:sparse(J[ax]) for ax in ['s','t']},
 'physical_retained_universal_indices':retained,'physical_joint_matrices':{ax:sparse(PH[ax]) for ax in ['s','t']},
 'physical_lower_universal_indices':low_universal,'physical_lower_matrices':{ax:sparse(LOW[ax]) for ax in ['s','t']},
 'scope':'Exact rational observable closure for pair (I,J64), plus physical Gram restriction. Universal rank18 is minimal as an observable row module because J64 has nonzero residual against the proven minimal scalar17 frame. Physical invariant upper bound is17; distinguished physical-solution minimality requires a lower-bound argument.',
 'elapsed_seconds':time.time()-st,
}
open(HERE/'joint_mass_response_certificate.json','w').write(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['all_checks_passed','universal_joint_dimension','physical_joint_dimension','physical_lower_dimension','elapsed_seconds']},indent=2))
print('chi_s',chi['s']);print('chi_t',chi['t'])
print('low index map',low_universal)
