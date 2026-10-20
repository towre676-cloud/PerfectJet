"""Append the DELL research relations while retaining every earlier record."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX_COUNT = 640
PREFIX_SHA256 = "cf4fd30ac37c92e32cc6710ee4d4798287b4031d49f6cd334854e6bc250a43a4"

# Definitions, exact finite identities and analytic consequences are distinct.
ROWS = [
("multiplicative theta convention", "theta(Z;P)=(1-Z)*prod_(m>=1)(1-P^m)(1-P^m Z)(1-P^m/Z)", "definition", "P is the standard multiplicative coordinate nome; in Koroteev-Shakirov equation3.3 it equals the square of the paper's p. Theta ratios cancel the scalar product factors.", "DELL_RESEARCH.md"),
("momentum shell energy and charge", "E(n)=sum_i n_i(n_i-1)/2; charge(n)=sum_i n_i", "definition", "Integer n_i; E is nonnegative and the momentum nome is W. Position nome P and momentum nome W are independent formal parameters.", "DELL_RESEARCH.md"),
("signless normalized DELL current modes", "C_a=sum_(charge(n)=a) W^E(n)*F_n(X;T,P)*Y^n; F_n=prod_(i<j)theta(T^(n_i-n_j)Xi/Xj;P)/theta(Xi/Xj;P)", "definition", "The published Koroteev-Shakirov current is reconstructed with the common coordinate Vandermonde divided out and the overall (-1)^a mode sign removed. This defines the tested model; it is not a new DELL construction.", "DELL_RESEARCH.md"),
("common left-factor cancellation", "(M C0)^(-1)*(M Ca)=C0^(-1)*Ca", "derived", "Associative operator algebra; M and C0 are invertible in the declared completion. No commutativity of factors is assumed. This identifies raw and theta-ratio current conventions after left normalization.", "DELL_RESEARCH.md"),
("formal normalized Hamiltonian recurrence", "C0=1+sum_(r>=1)W^r A_r; H_a^[r]=C_a^[r]-sum_(j=1)^r A_j*H_a^[r-j]", "derived", "H_a=C0^(-1)*Ca; products are ordinary for classical functions and ordered for quantum difference operators. Every coefficient uses finitely many earlier coefficients.", "DELL_RESEARCH.md"),
("current charge recurrence", "C_(a+N)=W^a*(Y1*...*YN)*C_a", "derived", "For the literal signless current, shift every n_i by1. Ratios depend only on differences. In the quantum action convention the total shift commutes with all coordinate-ratio coefficients. Formal Laurent W interpretation handles negative a.", "DELL_RESEARCH.md"),
("finite shell completeness", "E(n)<=M => n_i(n_i-1)/2<=M for each i", "derived", "All scalar summands are nonnegative on integers. Enumerating precisely this finite coordinate range and filtering total E and charge is exhaustive at every declared momentum order.", "DELL_RESEARCH.md"),
("logarithmic canonical Poisson bracket", "{F,G}=sum_i[(Xi*d_Xi F)(Yi*d_Yi G)-(Yi*d_Yi F)(Xi*d_Xi G)]", "definition", "Classical independent nonzero multiplicative coordinates. Exact jet derivatives are computed before rational specialization; evaluating a zero bracket at finitely many points alone is not a global identity proof.", "DELL_RESEARCH.md"),
("integrable deformation compatibility", "{H_i^0,H_j^r}+{H_i^r,H_j^0}=-sum_(s=1)^(r-1){H_i^s,H_j^(r-s)}", "derived", "Coefficient equation for formal Poisson commutativity. The new order enters linearly; no general solvability or completeness is asserted.", "DELL_RESEARCH.md"),
("canonical deformation equivalence", "H_i^1 -> H_i^1+{H_i^0,G}", "derived", "An infinitesimal canonical change of coordinates. This is a gauge equivalence of first-order corrections, not a classification of all DELL systems.", "DELL_RESEARCH.md"),
("three-particle first-shell expansion", "C0=1+WA+O(W²); C1=h1+WB+O(W²); C2=h2+WC+O(W²); H1=h1+W(B-Ah1); H2=h2+W(C-Ah2)", "derived", "Coordinate nome P=0; A has six permutation shifts(-1,0,1), B has three shifts(-1,1,1), C has three shifts(2,0,0). Equations use signless oriented coefficients.", "DELL_NORMALIZATION.md"),
("exact first-shell Poisson cancellation", "{h1,h2}=0; {B,h2}+{h1,C}=h1*{A,h2}+h2*{h1,A}=R", "exact_checked", "Classical N=3,P=0. Sparse Laurent-polynomial numerator cancellation proves rational identities in symbolic T,X,Y; this is stronger than sampled evaluations, and is only first order in W.", "DELL_NORMALIZATION.md"),
("common-power normalization rigidity", "{C1/C0^s,C2/C0^s}=W*(1-s)*R+O(W²); R(2;(1,3,7);(2,5,11))=8356261/901120", "derived", "Classical P=0,N=3; common exponent s. The nonzero exact witness forces s=1 for an identity over generic parameters. Not a full normalizer classification outside this ansatz.", "DELL_NORMALIZATION.md"),
("six-mode first-order normalizer classification", "rho=sum_(n in perm(-1,0,1))lambda_n(T)*F_n*Y^n; {C1/(1+W rho),C2/(1+W rho)}=O(W²) iff all lambda_n=1", "derived", "Classical N=3,P=0. The lambda_n depend on coupling T only. Valid at T!=0,1; the exact rank certificate excludes further exceptional nonzero couplings within these six fixed functions.", "DELL_NORMALIZATION.md"),
("normalizer rank and coupling boundary", "det(M6(T))=-(T-1)^14/T^8; rank(M)=6 for T!=0,1; rank(M)|T=1=0", "exact_checked", "M6 is the retained six-row coefficient minor of the normalizer compatibility map. At T=1 the six coefficients are unconstrained at first order. Zero coupling is excluded by the Laurent current definition.", "DELL_NORMALIZATION.md"),
("standard trigonometric Ruijsenaars weights", "a_I(X;T)=prod_(i in I,j notin I)(T Xi-Xj)/(Xi-Xj); H1f=sum_i a_i f(Yi); H2f=sum_(i<j)a_ij f(Yi)f(Yj)", "definition", "N=3 and unchanged standard coordinate coefficients; one common meromorphic particlewise momentum profile f. This ansatz is narrower than a general DELL family.", "DELL_OBSTRUCTIONS.md"),
("particlewise momentum obstruction identity", "{H1f,H2f}|X=(1,3,7),Y=(u,v,v)=K(T)*(f(v)-f(u))*(f(v)*u*fprime(u)-f(u)*v*fprime(v))", "exact_checked", "K1(T)=(5T^4-26T^3+126T-105)/72. A second coordinate witness X=(1,2,5) has K2(T)=(7T^4-27T^3+90T-70)/16; a retained Bezout identity proves the only common coupling root is T=1.", "DELL_OBSTRUCTIONS.md"),
("classified particlewise profile", "{H1f,H2f}=0 and T!=1 => Y*fprime(Y)/f(Y)=lambda => f(Y)=C*Y^lambda locally", "derived", "Two independent coordinate witnesses and an exact Bezout identity close all exceptional couplings except T=1. Nonconstant meromorphic f on a connected logarithmic cover gives local powers; globally single-valued on C* forces integer lambda. At T=1 arbitrary momentum profiles commute.", "DELL_OBSTRUCTIONS.md"),
("particlewise ellipticization no-go", "f(PY)=f(Y),0<abs(P)<1 and f(Y)=C*Y^m,m in Z => m=0", "derived", "Together with the classified unchanged-coordinate ansatz this excludes nonconstant single-valued elliptic particlewise profiles at T!=1. It does not exclude general double-elliptic systems or coupled momentum interactions.", "DELL_OBSTRUCTIONS.md"),
("explicit failed momentum ellipticization direction", "f(Y)=Y+epsilon/Y => {H1f,H2f}|T=2,X=(1,3,7),Y=(2,3,3)=-95epsilon/216+95epsilon²/1296", "exact_checked", "An exact nonzero first-order direction within the particlewise ansatz. This is a Laurent test profile, not itself an elliptic function; monomial profiles provide positive controls.", "DELL_OBSTRUCTIONS.md"),
("forced mixed momentum Fourier mode", "[W Y^(-1,2,0)]H1=-F_(-1,1,0)*F_(0,1,0)", "derived", "N=3 signless normalized current; the numerator first shell has no(-1,2,0) mode, while C0^(-1)C1 supplies this product. Nonzero generic meromorphic coefficient; no assertion of a new unknown Hamiltonian.", "DELL_OBSTRUCTIONS.md"),
("ordered quantum coefficient multiplication", "(f(X)*S^n)*(g(X)*S^m)=f(X)*g(Q^n X)*S^(n+m)", "definition", "Literal action S_i f(X)=f(X1,...,Q Xi,...,XN). Q is the quantum shift parameter, distinct from both elliptic nomes; finite coefficient checks do not prove the full quantum commutativity conjecture.", "DELL_RESEARCH.md"),
("right normalization is simultaneous conjugacy", "Ca*C0^(-1)=C0*(C0^(-1)*Ca)*C0^(-1)", "derived", "Invertible C0 in an associative completed operator algebra. Left and right families have equivalent commutativity; right normalization is not a valid noncommutativity negative control.", "DELL_RESEARCH.md"),
("coefficientwise quantum commutator gate", "[H1,H2]_(W^r P^s)=sum_(a+b=r,c+d=s)(H1^[a,c]*H2^[b,d]-H2^[a,c]*H1^[b,d])", "definition", "Every ordered output-shift coefficient is tested exactly at the declared rational parameter specializations and finite truncation. The retained receipt, rather than this formula, records which bounded panels actually passed.", "DELL_RESEARCH.md"),
("global second momentum-order Poisson cancellation", "[W^2]{C0^(-1)C1,C0^(-1)C2}=0 at P=0", "exact_checked", "N=3, rational identity in symbolic T,X,Y. The three exact numerators over Delta^5 have19902,13548,19902terms and cancel coefficientwise. This is finite-order commutativity, not all-order integrability.", "DELL_NORMALIZATION.md"),
("second-order homogeneous normalizer rank", "det M21=-128*(T-1)^44*(T+1)^2*(T+2)^5*(T+3)^2*(T^2+T+1)^3/T^31", "exact_checked", "P=0,N=3. A21function ansatz of symmetric products of first-shell functions has generic full rank. Hence no nonzero W² denominator correction in that ansatz at couplings where this minor is nonzero. A vanishing minor alone does not prove a rank drop.", "DELL_NORMALIZATION.md"),
("global first mixed-nome compatibility", "[W^a P^b]{H1,H2}=0 for a,b in {0,1}", "exact_checked", "N=3. Exact Laurent-polynomial identities in all T,X,Y, with P the product nome. The mixed raw3696terms and normalizer6864terms cancel after denominator clearing; no extrapolation to all elliptic orders.", "DELL_NORMALIZATION.md"),
("coordinate-deformed first-shell rigidity", "lambda_n(T,P)=1 mod P² for all six first-shell functions", "derived", "The global mixed-nome identity supplies a solution; the invertible constant-coordinate-nome minor makes both coefficients unique for each fixed T!=0,1. Numerator modes and six-function normalizer ansatz are fixed.", "DELL_NORMALIZATION.md"),
("multiaffine profile obstruction", "sum_i zi Pi(z)=0 => {H1[f],H2[f]}|z2=z3=s=P1(z,s,s)*(g(u)-z*g(v)/s)", "derived", "g(y)=y*fprime(y),z=f(u),s=f(v),s!=0. Base Hamiltonians are multiaffine and commute in log-canonical variables. A nonzero restricted P1 polynomial forces a nonconstant common profile to be a local power.", "DELL_OBSTRUCTIONS.md"),
("local coordinate-elliptic no-go extension", "T!=0,1 and abs(P)<delta(T) => no nonconstant elliptic particlewise profile in the unchanged elliptic-RS ansatz", "derived", "Conditional on the standard commuting multiaffine elliptic-RS weights holomorphic near P=0 with the declared trigonometric limit. A nonzero P=0 witness persists analytically. No numerical delta or all-moduli classification is claimed.", "DELL_OBSTRUCTIONS.md"),
("DELL homogeneity and moment-map descent", "sum_i Xi*d_Xi H_a=0; sum_i Yi*d_Yi H_a=a*H_a; {H_a,Y_all}=0", "derived", "Directly from current coefficients depending on coordinate ratios and fixed momentum charge. The formal Hamiltonians descend under regular simultaneous-position-scaling reduction at fixed nonzero Y_all.", "DELL_STRUCTURE.md"),
("generic formal functional independence", "det d(e1,...,eN)/d(logY1,...,logYN)=(prod_i Yi)*prod_(i<j)(Yi-Yj)", "derived", "At P=W=0,T=1 the normalized currents give elementary symmetric polynomials. This nonzero specialization proves generic independence of H1,...,H_(N-1),Y_all and their regular reduced family in the formal deformation; it does not prove commutativity or convergence.", "DELL_STRUCTURE.md"),
("complete second-order normalizer boundary", "dim ker(T on actual productfunctions)=1 at T=-1;19 at T=1;0 at all other nonzero T", "derived", "The first denominator shell is fixed to A and the second correction lies in products of its six functions. Three symbolic21minors and exact exceptional-field rank certificates classify all nonzero couplings. Function-space dependencies are quotiented out.", "DELL_NORMALIZATION.md"),
("resonant freedom is an existing integral", "rho_star=H1^0*H2^0/Y_all at T=-1; {rho_star,H1^0/H2^0}=0", "exact_checked", "A retained nine-product expansion proves membership in the second-order normalizer ansatz. This is one nonzero homogeneous normalizer direction, not a new independent conserved quantity.", "DELL_NORMALIZATION.md"),
("cube-root coefficient redundancy", "f1*f4=f0*f5; f2*f3=f0*f5 when T²+T+1=0", "exact_checked", "Zero-based f_i order is lexicographic perm(-1,0,1). The21nominal products span19actual functions. The two coefficient-kernel directions represent identically zero functions, so they give no new normalizer freedom.", "DELL_NORMALIZATION.md"),
]


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    path = ROOT / "data/equations.json"
    source = json.loads(path.read_text())
    own_ids = {f"PJ-D{i:03d}" for i in range(1, len(ROWS) + 1)}
    earlier = [row for row in source["equations"] if row["id"] not in own_ids]
    if len(earlier) < PREFIX_COUNT or hashlib.sha256(canonical(earlier[:PREFIX_COUNT])).hexdigest() != PREFIX_SHA256:
        raise ValueError("the preserved 640-record research prefix changed")
    records = [{"id": f"PJ-D{i:03d}", "domain": "double-elliptic", "title": title,
                "equation": equation, "status": status, "assumptions": assumptions,
                "source": f"docs/{doc}; docs/dell_sources.json; python -m perfectjet.dell --exhaustive"}
               for i, (title, equation, status, assumptions, doc) in enumerate(ROWS, 1)]
    source["equations"] = earlier + records
    if len({r["id"] for r in source["equations"]}) != len(source["equations"]):
        raise ValueError("equation identifier collision")
    write(ROOT / "data/dell_equations.json", {
        "schema": "perfectjet/dell-equations/1", "research_date": "2026-10-20",
        "preserved_prefix": {"equation_count": PREFIX_COUNT, "sha256_of_canonical_records": PREFIX_SHA256},
        "scope": "Published current reconstruction, exact scoped obstruction and normalization theorems, and definitions for bounded replay. No global DELL solution or worldwide priority claim.",
        "equations": records})
    for relative in ("data/equations.json", "src/perfectjet/resources/equations.json"):
        write(ROOT / relative, source)
    ranking = json.loads((ROOT / "data/equation_power.json").read_text())
    if not any(row["rank"] == 27 for row in ranking["families"]):
        ranking["families"].append({"rank":27,"name":"Double-elliptic normalization and obstruction"})
    for row in records:
        ranking["assignments"][row["id"]] = 27
        ranking["callable_labs"][row["id"]] = ["dell"]
    for relative in ("data/equation_power.json", "src/perfectjet/resources/equation_power.json"):
        write(ROOT / relative,ranking)
    atlas = ["# Equation atlas", "", "Status describes evidence in this repository. Exact checking is not Lean verification.", "",
             "| ID | Domain | Title | Equation | Status | Assumptions and limits |",
             "|---|---|---|---|---|---|"]
    for row in source["equations"]:
        atlas.append("| " + " | ".join(str(row[k]).replace("|", "\\|").replace("\n", " ")
                     for k in ("id", "domain", "title", "equation", "status", "assumptions")) + " |")
    (ROOT / "docs/EQUATION_ATLAS.md").write_text("\n".join(atlas) + "\n", encoding="utf-8")
    print(json.dumps({"equations": len(source["equations"]), "new_records": len(records),
                      "preserved_prefix_sha256": PREFIX_SHA256}))


if __name__ == "__main__":
    main()
