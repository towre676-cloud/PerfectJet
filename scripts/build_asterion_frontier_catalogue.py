"""Append48 substantive frontier relations while preserving the592-record base."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Each relation has a precise hypothesis; no open target is counted as proved.
GROUPS = [
('kernel_characters',[
('length-three jet ambient character','Hilb S^3(g tensor Q[t])=(dim S^3g+dim S21g*(t+t²)+dim wedge^3g*t³)/((1-t)(1-t²)(1-t³))','derived','t counts total derivative degree, with ordinary polynomial length fixed at3.'),
('complete length-three arc character','H3(t)=(151373t+961248t²+3321371t³+4932875t⁴+4123000t⁵+1763125t⁶)/((1-t)(1-t²)(1-t³))','exact_checked','The finite pair-projector covariance ranks and earlier cubic-polarization certificates determine this all-jet fixed-length sector.'),
('weight-five length-three population','dim A[weight5,length3]=1112621','exact_checked','A is the arc algebra of the level-one E8 C2 algebra; the derivative degree is2.'),
('weight-five complete arc population','dim A5=1112621+96008+248=1208877','derived','Lengths at least4 vanish at this weight because the ordinary cubic ideal contains all Sym³g.'),
('weight-five complete kernel','dim K5=1208877-1057504=151373','derived','The canonical arc-to-associated-graded map is a surjective E8-equivariant graded map.'),
('weight-five kernel character','K5=V248+V3875+V147250','derived','Exact arc finite-character comparison with independently computed lattice/Freudenthal VOA character; no explicit new highest null lifts are asserted.'),
('weight-five primitive quotient','K5/(D K4+g[0]*K4)=V248+V147250; dimension147498','derived','Primitive means for the graded commutative differential ideal. D is injective and g[0]*K4=0.'),
('weight-six exact arc and kernel characters','dim A6=4716373; K6=1+248+2*3875+30380+147250; dim K6=185629','derived','Complete finite characters through weight6: the quartic dual multiplication kernel is exactly1+3875 by two explicit nonzero witnesses and a Casimir cutoff. Minimal generator list and Li placement are not inferred; see ASTERION_QUARTIC.md and asterion_frontiers.py.'),
]),
('kernel_tower',[
('divided-jet translation','D x^[r]=(r+1)x^[r+1]; E x^[r]=x^[r-1] for r>0; E x^[0]=0','definition','D and E extend by the commutative Leibniz rule; this fixes the divided-jet normalization.'),
('translation Heisenberg relation','[E,D]=N; N|ordinary degree p=p','exact_checked','The operator identity holds on the polynomial jet algebra and descends to its homogeneous differential-ideal quotient.'),
('lowering preserves the arc ideal','E(D^s q)=s*degree(q)*D^(s-1)q','derived','q is any homogeneous ordinary relation; E q=0. This is an all-order operator consequence, not a finite extrapolation.'),
('highest kernel symbol is lowering primitive','E F_Q=0','exact_checked','F_Q is the retained783-term weight-four cubic jet symbol constructed using the invariant dual basis.'),
('exact translation-tower left inverse','E^r D^r F_Q=3^r r! F_Q','derived','Ordinary degree3, EF_Q=0 and [E,D]=3 on this homogeneous sector; the initial nonzero arc class is imported from the earlier full certificate.'),
('translation injectivity','D v=0 and ordinary degree p>0 => v=0','derived','E is locally nilpotent and [E,D]=p; iterating D^rE^r v=(-p)^r r!v proves injectivity in the arc quotient.'),
('annihilator syzygy tower','D^r(x[0]*F_Q)=sum_(j=0)^r binom(r,j) D^j(x[0])*D^(r-j)F_Q=0','derived','The undifferentiated product lies in the ordinary cubic ideal. This gives relations among descendants, not automatic new primitive generators.'),
('lattice-to-Freudenthal multiplicities','mult(V_n,mu)=p8(n-(mu,mu)/2)','exact_checked','For the E8 lattice VOA, then Weyl-chamber-folded exact Freudenthal subtraction. The code independently reconstructs scalar characters through weight6.'),
]),
('elliptic',[
('normalized elliptic theta product','Theta(z;p)=(exp(z/2)-exp(-z/2))*product_n[(1-p^n exp(z))(1-p^n exp(-z))/(1-p^n)^2]','definition','Im tau>0,p=exp(2pi i tau); Theta is odd with derivative1 at0 and has quasiperiods2pi i,log p.'),
('elliptic scalar kernels','rho(z)=Thetaprime(z)/Theta(z); Phi(z,x)=Theta(z+x)/(Theta(z)Theta(x))','definition','Meromorphic away from the theta divisors in spectral and dynamical parameters; numerator zeros are permitted.'),
('rank-eight E8 dynamical tensor','r(z,lambda)=rho(z)*Omega_h+sum_alpha Phi(z,lambda(h_alpha))*e_alpha tensor e_-alpha','derived','Actual normalized E8 metric, all240roots and64inverse-Cartan coefficients; this is the classical Felder tensor.'),
('dynamical elliptic Yang-Baxter equation','Alt(d r)+[r12,r13]+[r12,r23]+[r13,r23]=0','exact_checked','Alt uses h_i in slots1,-2,+3 with partial/lambda_i,lambda_i=lambda(h_i). Analytic all-orders proof uses theta addition; direct series replay is bounded.'),
('spectral unitarity and residue','r21(-z,lambda)=-r(z,lambda); Res_z=0 r=Omega','derived','Odd theta and the derivative-one normalization fix signs and the residue; all root and Cartan terms are retained.'),
('three-root elliptic Fay generator','Phi(u,-b)Phi(u+v,a+b)-Phi(u,a)Phi(v,a+b)+Phi(u+v,a)Phi(v,b)=0','exact_checked','The analytic theta-addition identity generates every three-root coefficient;13440ordered E8 root triples are checked against the actual bracket signs.'),
('opposite-root derivative generator','partial_a Phi(v,a)+(rho(u)-rho(u+v))*Phi(v,a)-Phi(u,-a)*Phi(u+v,a)=0','derived','A Laurent limit of Fay supplies all three Cartan-slot arrangements. Deleting dynamical derivatives leaves a nonzero ordinary CYBE tensor.'),
('rational degeneration','r_rat(z,lambda)=Omega/z+sum_alpha e_alpha tensor e_-alpha/lambda(h_alpha)','exact_checked','Sequential cusp p->0 followed by additive scaling; the independent full E8 rational CDYBE is replayed.'),
]),
('monodromy',[
('level-four exact local spectrum','Spec(U)=Spec(V)={zeta17^0,zeta17^1,zeta17^2,zeta17^4,zeta17^11}','derived','Five-channel connection hbar=1/34, log-free exact local Frobenius basis; based counterclockwise generators.'),
('actual and projective local order','U^17=V^17=I; po(U)=po(V)=17','derived','Five distinct local eigenvalues with exact17th-root exponents. Finite local orders do not imply finite group image.'),
('exact determinant image','det U=det V=zeta17; det Gamma=mu17','derived','Trace of each residue is-100; exponent sum18 is1mod17.'),
('actual-loop spectral projectors','P_i(U)=product_(j!=i)(U-lambda_j I)/(lambda_i-lambda_j)','exact_checked','Gaussian-rational loop enclosures and rigorous cyclotomic root balls propagate every matrix error.'),
('fixed-level irreducibility certificate','P_j V P_i !=0 for all i!=j;20certified blocks','exact_checked','The strongly connected spectral graph excludes every proper U-invariant spectral subset at hbar1/34 itself.'),
('compact connected monodromy closure','closure(Gamma)^0=SU(5)','derived','Specialized irreducibility, prime-dimensional primitivity, finite-primitive classification, level-four WZW unitarity and exclusion of projective self-duality.'),
('full compact monodromy closure','closure(Gamma)={g in U(5):det(g)^17=1}; projective closure PU(5)','derived','Up to a fixed unitarizing conjugacy; contains17SU5cosets. The countable dense image is not given a discrete presentation.'),
('complex Zariski closure','ZariskiClosure(Gamma)={g in GL5(C):det(g)^17=1}','derived','Complexify the connected SU5component and retain the exact17determinant cosets; identity component SL5(C).'),
]),
('monodromy_algebra',[
('residue associative algebra','Q<A,B>=M5(Q); dimension25','exact_checked','Explicit independent word matrices and exact closure replays for the actual five-channel E8 residues.'),
('residue Lie algebra','Lie_Q(A,B)=gl5(Q); dimension25','exact_checked','Actual nested commutator words, not a generic matrix substitution.'),
('centered residue Lie algebra','Lie_Q(A+20I,B+20I)=sl5(Q); dimension24','exact_checked','Each original residue has trace-100; centering removes its scalar part.'),
('connected residue coupling graph','support_offdiag(B)={0<->1,1<->2,2<->3,3<->4,1<->4}','exact_checked','The ten nonzero entries have distinct ad_A weights plus/minus30,18,12,2,32.'),
('spectral matrix-unit generator','L_ij(ad_A)(B)=B_ij E_ij','exact_checked','Degree10Lagrange polynomial vanishes at all other off-diagonal weights and0. Path commutators generate the remaining matrix units.'),
('cyclotomic self-duality obstruction','S={0,1,2,4,11}; no a modulo17 satisfies S=a-S','exact_checked','All17similitude factors are exhausted; every candidate bilinear form has rank at most3.'),
('residue-adjoint and invariant forms differ','A^T H=H A, B^T H=H B has a positive solution; A^T G+G A=B^T G+G B=0 has onlyG0','exact_checked','Selfadjoint residue metrics are not automatically monodromy-invariant metrics; the latter use the unitary WZW theorem.'),
('formal-parameter monodromy closure','ZariskiClosure(Gamma_formal)=GL5 over the algebraic closure of C((hbar))','derived','The documented torus/generic proof uses residue Lie generation. Pointwise differential Galois GL5 follows for small infinite-order parameters by Schlesinger; no rational-specialization transfer is made.'),
]),
('jacobi',[
('rank-eight refined character','H(tau,z)=Theta_E8(tau,z)/phi(q)^8; q=exp(2pi i tau)','derived','Eight Cartan chemical potentials retain every lattice charge; the finite248directions occur at conformal weight1.'),
('exact charge populations','dim V[N,alpha]=p8(N-|alpha|²/2)','exact_checked','Complete doubled-coordinate E8 lattice enumeration and oscillator convolution; alpha outside the lattice has multiplicity0.'),
('elliptic lattice translation','Theta(tau,z+tau*lambda+mu)=q^(-|lambda|²/2)*exp(-2pi i(lambda,z))*Theta(tau,z)','derived','lambda,mu in the integral E8 lattice; exact reindexing proves all orders without truncation-edge assumptions.'),
('oscillator-corrected heat identity','(2D_tau-sum_i D_zi²)H=(2/3)(1-E2)H','exact_checked','D_tau andD_zi mean derivatives divided by2pi i; the physical q^(-1/3)character has RHS-(2/3)E2chi.'),
('first angular defect polynomial','H8_root(u)=sum_root(alpha,u)^8-30|u|^8; Laplacian H8_root=0','derived','Root shell is a7design; H8_root(e1)=-3/2 proves a nonzero degree8angular defect.'),
('all-shell Ramanujan angular relation','M8_n(u)-N_n*n^4*|u|^8/8=tau(n)*H8_root(u)','exact_checked','Weighted harmonic theta modularity gives the all-order identity; whole degree8moment tensors are independently replayed at bounded shells.'),
('affine angular defect density','sum_n defect_H,n(u)q^n=H8_root(u)*q*phi(q)^16','derived','Oscillator convolution of H8_rootDelta divides byphi^8. This is a charge-angle observable, not a geometric packing gain.'),
('higher angular modular relation compiler','Theta_(E8,P_d) in S_(4+d)=Delta*Q[E4,E6]_(d-8)','exact_checked','Even2<=d<=30; full-rank Sturm panel of at most2qcoefficients. Computed multivariate moment tensors stop at8; higher displayed coefficients specializeu=e1.'),
])]


def write(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")


def main():
    source = json.loads((ROOT/"data/equations.json").read_text())
    prefix = [r for r in source["equations"] if not r["id"].startswith("PJ-X")]
    if len(prefix) != 592:
        raise ValueError("the immutable frontier prefix must have592records")
    digest = hashlib.sha256(json.dumps(prefix,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
    records = []
    for component,rows in GROUPS:
        for title,equation,status,assumptions in rows:
            records.append({"id":f"PJ-X{len(records)+1:03d}","domain":"asterion-frontiers",
                            "title":title,"equation":equation,"status":status,"assumptions":assumptions,
                            "source":f"docs/ASTERION_{component.upper()}.md; docs/ASTERION_FRONTIERS.md; src/perfectjet/asterion_{component}.py"})
    if len(records) != 48:
        raise ArithmeticError("frontier equation count changed")
    write(ROOT/"data/asterion_frontier_equations.json",{
        "schema":"perfectjet/asterion-frontier-equations/1",
        "preserved_prefix":{"equation_count":len(prefix),"sha256_of_canonical_records":digest},
        "scope":"Exact finite certificates and stated analytic/theoretical consequences; no worldwide priority or full infinite-kernel claim.",
        "equations":records})
    source["equations"] = prefix+records
    for rel in ("data/equations.json","src/perfectjet/resources/equations.json"):
        write(ROOT/rel,source)
    ranking = json.loads((ROOT/"data/equation_power.json").read_text())
    for row in records:
        ranking["assignments"][row["id"]]=26
        ranking["callable_labs"][row["id"]]=["asterion","asterion-frontiers"]
    for rel in ("data/equation_power.json","src/perfectjet/resources/equation_power.json"):
        write(ROOT/rel,ranking)
    atlas=["# Equation atlas","","Status describes evidence in this repository. Exact checking is not Lean verification.","",
           "| ID | Domain | Title | Equation | Status | Assumptions and limits |","|---|---|---|---|---|---|"]
    for row in source["equations"]:
        atlas.append("| "+" | ".join(str(row[k]).replace("|","\\|").replace("\n"," ")
                                     for k in ("id","domain","title","equation","status","assumptions"))+" |")
    (ROOT/"docs/EQUATION_ATLAS.md").write_text("\n".join(atlas)+"\n",encoding="utf-8")
    print(json.dumps({"equations":len(source["equations"]),"new_records":len(records),"preserved_prefix_sha256":digest}))


if __name__ == "__main__":
    main()
