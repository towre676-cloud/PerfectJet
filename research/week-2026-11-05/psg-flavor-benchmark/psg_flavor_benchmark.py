"""Mixed-mass flavor benchmark: exact GIM quotient and amplitude error.

Requires Python 3 and mpmath 1.3.0. Run with --dps 80 or --dps 100.
Inputs are fixed illustrative values. The coefficient omits the common
electroweak prefactor, QCD corrections and hadronic matrix elements.

Published kernel: Botella et al., EPJC 82 (2022) 360, Appendix B, eqs.69–70,
https://doi.org/10.1140/epjc/s10052-022-10299-9 .
The positive integral representation follows by partial fractions.
This is high-precision floating-point verification, not interval certification.
The closed-form evaluator covers the regular and diagonal cases in this
fixed benchmark; the separate positive integral supplies its comparison.
"""
import argparse
import json
import mpmath as m

parser=argparse.ArgumentParser()
parser.add_argument('--dps',type=int,default=80)
args=parser.parse_args()
if args.dps<40:parser.error('--dps must be at least 40 for this benchmark.')
m.mp.dps=args.dps

def S(x,y):
    if x==0 or y==0:return m.mpf(0)
    if x==y:
        if x==1:return m.mpf(3)/4
        return x*(1-m.mpf(11)*x/4+x*x/4)/(1-x)**2-3*x**3*m.log(x)/(2*(1-x)**3)
    if x==1 or y==1:raise ValueError('Off-diagonal unit arguments are outside this fixed closed-form benchmark.')
    a=lambda t:(1-2*t+t*t/4)/(1-t)**2
    return x*y*((a(x)*m.log(x)-a(y)*m.log(y))/(x-y)-m.mpf(3)/(4*(1-x)*(1-y)))

def integral(x,y):
    if x==0 or y==0:return m.mpf(0)
    f=lambda z:(z*z+8*z+4)/(4*(z+1)**2)*(x/(z+x))*(y/(z+y))
    return m.quad(f,sorted(set([m.mpf(0),x,y,m.mpf(1),m.inf])))

xs=[m.mpf(0),m.mpf(1)/4000,m.mpf(4)]
s12,s23,s13=m.mpf(9)/40,m.mpf(1)/25,m.mpf(7)/2000
c12,c23,c13=[m.sqrt(1-s*s) for s in (s12,s23,s13)]
e=m.mpc(m.mpf(1)/2,m.sqrt(3)/2)
V=m.matrix([[c12*c13,s12*c13,s13/e],
    [-s12*c23-c12*s23*s13*e,c12*c23-s12*s23*s13*e,s23*c13],
    [s12*s23-c12*c23*s13*e,-c12*s23-s12*c23*s13*e,c23*c13]])
lam=m.matrix([m.conj(V[i,1])*V[i,0] for i in range(3)])
M=m.matrix([[S(x,y) for y in xs] for x in xs])
R=m.matrix([[1/m.sqrt(2),1/m.sqrt(6)],[-1/m.sqrt(2),1/m.sqrt(6)],
    [0,-2/m.sqrt(6)]])
K=R.T*M*R
eig,U=m.eigsy(K)
z=R.T*lam
C=(lam.T*M*lam)[0]
C1=eig[1]*(U[:,1].T*z)[0]**2
discrepancies=[abs(S(x,y)-integral(x,y)) for x,y in
    [(xs[1],xs[1]),(xs[1],xs[2]),(xs[2],xs[2]),(m.mpf(1),m.mpf(1))]]
unitarity=max(abs(t) for t in V.H*V-m.eye(3))
quotient_error=abs(C-(z.T*K*z)[0])
tolerance=m.mpf(10)**(-args.dps+15)
assert max(discrepancies+[unitarity,abs(sum(lam)),quotient_error])<tolerance
absolute_error=abs(C1-C)
spectral_error_bound=m.norm(lam)**2*eig[0]
assert absolute_error<=spectral_error_bound*(1+tolerance)
n=lambda x:m.nstr(x,45)
print(json.dumps({'status':'PASS','all_checks_passed':True,'dps':args.dps,'mpmath_version':m.__version__,
    'scope':'Fixed illustrative inputs; high-precision floating-point verification. No physical fit or interval certificate.',
    'source':'https://doi.org/10.1140/epjc/s10052-022-10299-9, Appendix B, equations 69-70',
    'x':[n(x) for x in xs],'s12':'9/40','s23':'1/25','s13':'7/2000','delta':'pi/3',
    'kernel_cc':n(M[1,1]),'kernel_ct':n(M[1,2]),'kernel_tt':n(M[2,2]),
    'lambda':[n(x) for x in lam],'unitarity_max':n(unitarity),
    'integral_closed_formula_max_difference':n(max(discrepancies)),
    'gim_sum_residual':n(abs(sum(lam))),'quotient_identity_residual':n(quotient_error),
    'gim_plane_eigenvalues':[n(x) for x in eig],
    'coefficient_full':n(C),'coefficient_rank1':n(C1),
    'trace_fraction_discarded':n(eig[0]/sum(eig)),
    'frobenius_squared_fraction_discarded':n(eig[0]**2/sum(x*x for x in eig)),
    'coefficient_relative_error':n(abs(C1-C)/abs(C)),
    'coefficient_absolute_error':n(absolute_error),
    'coefficient_absolute_error_bound':n(spectral_error_bound),
    'imaginary_part_relative_error':n(abs(m.im(C1-C))/abs(m.im(C)))},indent=2))
