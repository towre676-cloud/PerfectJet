"""Baseline-preserving Schur-complement motion correction.

Only the added movement coefficients receive stronger regularization. This
avoids changing conventional coefficient shrinkage when testing a correction.
"""
import json
from pathlib import Path
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.decomposition import PCA
import pooled_transfer as P
import pooled_safe_blend as B

def schur(x,z,y,xt,zt,penalty):
    x=np.c_[np.ones(len(x)),x];xt=np.c_[np.ones(len(xt)),xt]
    prior=np.diag([0.]+[100.]*(x.shape[1]-1))
    gram=x.T@x+prior
    beta=np.linalg.solve(gram,x.T@y)
    transport=np.linalg.solve(gram,x.T@z)
    gamma=np.linalg.solve(z.T@z-z.T@x@transport+penalty*np.eye(z.shape[1]),z.T@(y-x@beta))
    return xt@beta+(zt-xt@transport)@gamma,xt@beta
def predict(a,b,family,penalty=1000.):
    cols=P.C.V.PHYS+[c for c in a if c.startswith('available__')]
    imp=SimpleImputer(strategy='median',keep_empty_features=True);sc=StandardScaler()
    x=sc.fit_transform(imp.fit_transform(a[cols]));xt=sc.transform(imp.transform(b[cols]));enc=OneHotEncoder(handle_unknown='ignore',sparse_output=False)
    x=np.c_[x,enc.fit_transform(a[['combine_position']].fillna('MISSING'))];xt=np.c_[xt,enc.transform(b[['combine_position']].fillna('MISSING'))]
    features={'capacity':[c for c in a if c.startswith('sprint__')],'duration':P.duration_columns(a),'pooled':[c for c in a if c.startswith('pool__') and '__b' in c]}[family]
    mi=SimpleImputer(strategy='median',keep_empty_features=True);ms=StandardScaler();z=ms.fit_transform(mi.fit_transform(a[features]));zt=ms.transform(mi.transform(b[features]))
    nuisance=Ridge(alpha=10).fit(x,z);z-=nuisance.predict(x).reshape(z.shape);zt-=nuisance.predict(xt).reshape(zt.shape)
    pca=PCA(n_components=min(2,z.shape[1],len(a)-1),svd_solver='full');z=pca.fit_transform(z);zt=pca.transform(zt)
    motion,base=schur(x,z,a.target.to_numpy(),xt,zt,penalty)
    return np.clip(motion,0,1),np.clip(base,0,1)
def fit(tr,te,turns):
    a,b=P.augment(tr,te,turns,10.);motion=[]
    for family in ['capacity','duration','pooled']:
        p,base=predict(a,b,family);motion.append(p)
    return base,np.column_stack(motion)
def run():
    B.fit=fit;B.SPECS=[(family,'baseline100_motion1000',2,10.) for family in ['capacity','duration','pooled']]
    units,turns=P.prepare()
    for seed in [P.SEED,P.SEED+200,P.SEED+400]:B.run(units,turns,seed,seed==P.SEED,prefix='schur')
if __name__=='__main__':run()
