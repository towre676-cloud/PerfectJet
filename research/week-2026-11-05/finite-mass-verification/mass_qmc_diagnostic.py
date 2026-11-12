#!/usr/bin/env python3
"""Independent quasi-Monte Carlo *diagnostic*, not a certified enclosure.

Samples uniform 6-simplex from six scrambled Sobol coordinates using the
exact stick-breaking Beta(1,k) transformation. The exact theorem does not
rely on any numerical output from this script.
"""
import json, argparse
from pathlib import Path
import numpy as np
from scipy.stats import qmc

def one_rep(seed,power):
    v=qmc.Sobol(d=6,scramble=True,seed=seed).random_base2(power)
    a=np.empty((len(v),7),float)
    remaining=np.ones(len(v),float)
    for j in range(6):
        f=1-np.power(1-v[:,j],1/(6-j))
        a[:,j]=remaining*f
        remaining*=1-f
    a[:,6]=remaining
    a1,a2,a3,a4,a5,a6,a7=a.T
    U=(a1+a2+a3+a6+a7)*(a4+a5+a6+a7)-(a6+a7)**2
    Ps=a1*a3*(a4+a5+a6+a7)+a1*a5*a7+a3*a4*a6
    Pt=a2*a5*a6
    Pu=a2*a4*a7
    F1=U-3*Ps+Pt+2*Pu
    b=a7*U/F1
    assert np.min(F1)>0 and np.min(b)>=0 and np.max(b)<1+1e-12
    base=(-2/720)*U/F1**3
    vals=[base,base*(-3*b),base*(12*b**2)]
    vals += [base/(1+(rho-1)*b)**3 for rho in [7/8,9/8]]
    return np.array([x.mean() for x in vals])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--power',type=int,default=17);ap.add_argument('--replicas',type=int,default=12);args=ap.parse_args()
    results=np.array([one_rep(20261103+37*i,args.power) for i in range(args.replicas)])
    means=results.mean(0);errs=results.std(0,ddof=1)/np.sqrt(args.replicas)
    I,Ip,Ipp,I7,I9=means
    lo7=I-sp(169,1029)*Ip;hi7=I-Ip/8
    lo9=I+sp(217,2187)*Ip;hi9=I+Ip/8
    # The prior exact inequality is pointwise, hence each replicate also satisfies it.
    assert np.all(results[:,3]>=results[:,0]-169/1029*results[:,1]-1e-12)
    assert np.all(results[:,3]<=results[:,0]-results[:,1]/8+1e-12)
    assert np.all(results[:,4]>=results[:,0]+217/2187*results[:,1]-1e-12)
    assert np.all(results[:,4]<=results[:,0]+results[:,1]/8+1e-12)
    d={
     'purpose':'QMC crosscheck only; not a proof or rigorous numeric enclosure',
     'sample_design':{'scrambled_sobol_replicas':args.replicas,'samples_per_replica':2**args.power,'simplex':'6D uniform stick-breaking'},
     'means':dict(zip(['I_1','I_prime_1','I_double_prime_1','I_7_8','I_9_8'],means.tolist())),
     'replica_standard_errors':dict(zip(['I_1','I_prime_1','I_double_prime_1','I_7_8','I_9_8'],errs.tolist())),
     'bounds_from_sampled_I_and_Iprime':{'rho_7_8':[lo7,hi7],'rho_9_8':[lo9,hi9]},
     'sampled_second_derivative_bounds':{'lower':4/3*Ip**2/abs(I),'value':-Ipp,'upper':4*Ip},
     'all_replicate_bounds_pass':True,
    }
    p=Path(__file__).parent/'mass_qmc_diagnostic.json';p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))

def sp(x,y):return x/y
if __name__=='__main__':main()
