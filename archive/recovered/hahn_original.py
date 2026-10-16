from math import comb

def ff(n,k):
    if k<0 or k>n:
        return 0
    out=1
    for s in range(k):
        out*=n-s
    return out

def S(i1,i2,j1,j2,k):
    return sum(((-1)**r)*comb(k,r)*ff(i1,k-r)*ff(i2,r)*ff(j1,r)*ff(j2,k-r) for r in range(k+1))

def kappa(i1,i2,j1,j2):
    return min(i1,j2)+min(i2,j1)

def poisson_scalar(i1,i2,j1,j2):
    return i1*j2-i2*j1

def exact(i1,i2,j1,j2):
    kap=kappa(i1,i2,j1,j2)
    return all(S(i1,i2,j1,j2,k)==0 for k in range(3,kap+1,2))

def classify(i1,i2,j1,j2):
    kap=kappa(i1,i2,j1,j2)
    terms=[]
    for k in range(3,kap+1,2):
        sk=S(i1,i2,j1,j2,k)
        if sk:
            terms.append((k,i1+j1-k,i2+j2-k,sk))
    if not terms:
        return "EXACT"
    if all(qp==0 and pp==0 for _,qp,pp,_ in terms):
        return "CENTRAL_DEFECT"
    return "NONCENTRAL_DEFECT"

if __name__ == "__main__":
    tests=[(1,3,5,1),(1,4,5,2),(3,0,0,3),(1,2,2,1)]
    for t in tests:
        print(t, "kappa=", kappa(*t), "poisson=", poisson_scalar(*t), "class=", classify(*t),
              "S3=", S(*t,3), "S5=", S(*t,5))
