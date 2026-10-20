"""Append the extension equations while preserving all 504 earlier records.

Re-running updates only this named extension and its generated presentations.
Open goals remain proposals; a callable family does not certify every goal.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# title, equation, evidence status, precise hypotheses and implementation scope
GROUPS = [
("boundary", [
("principal Rees bracket", "[P_a,Q_b]_t=sum_c kappa_ab^c t^(a+b-c-1) T_(a+b-c)(P_a,Q_b)", "derived", "Use the actual 170 rational couplings and the eight principal spins; t is a deformation parameter, not a current mode."),
("nonnegative Rees exponents", "a+b-c-1>=0 and a+b-c-1 is even on every allowed channel", "exact_checked", "All eight spins are odd and the actual bracket has positive odd transvectant order."),
("punctured-family scaling", "S_t|V_m=t^(m-1); [x,y]_t=S_t^-1[S_t x,S_t y] for t!=0", "derived", "Every nonzero fiber is isomorphic to E8; this integer-power gauge creates no automatic new monodromy."),
("polynomial Jacobi specialization", "Jacobi_t=0 for t!=0 => Jacobi_t=0 in Q[t] => Jacobi_0=0", "derived", "Polynomial structure constants over an infinite characteristic-zero field and a verified reference bracket."),
("boundary channel support", "support([ , ]_0)={a+b-c=1}; card(support)=16", "exact_checked", "Count reduced principal channels, not basis tensor entries; the other 154 channels vanish at this boundary."),
("nilradical lower-central dimensions", "dim gamma_i(n)=(245,207,145,59,0)", "exact_checked", "The concrete leading-channel algebra is sl2 semidirect n; nilpotency class four follows from nonzero channel images and vanishing next term."),
("boundary center", "Z(n)=V_29; dim Z(n)=59", "derived", "Center of the nilradical, not of the full semidirect product; sl2 acts nontrivially on V_29."),
("Killing-form valuations", "B_t|V_m=t^(2m-2)B_1|V_m", "derived", "Pull back the E8 invariant form through S_t. Its specialization has rank three."),
("all invariant forms at the boundary", "n subset rad B for every invariant symmetric B on g_0; rank B<=3", "derived", "Multiplicity-free sl2 types are orthogonal, and [V_m,V_m]_0 has no V_1 output for m>1."),
("quadratic completion lower bound", "dim D>=dim g_0+dim rad(B|g_0)>=493", "derived", "Assume g_0 embeds as a Lie subalgebra in finite-dimensional D with a nondegenerate invariant symmetric form; isotropic embeddings require dimension at least 496."),
("cotangent Lie extension", "[(x,alpha),(y,beta)]=([x,y],ad_x^* beta-ad_y^* alpha)", "derived", "The coadjoint action is (ad_x^* beta)(z)=-beta([x,z]); this classical construction gives dimension 496."),
("canonical nondegenerate pairing", "<(x,alpha),(y,beta)>=alpha(y)+beta(x)", "derived", "On g semidirect g*, the canonical symmetric form is invariant and nondegenerate for every family parameter."),
("quadratic Casimir braid identities", "[Omega_12,Omega_13+Omega_23]=0; [Omega_ij,Omega_kl]=0 for disjoint pairs", "derived", "A nondegenerate invariant symmetric form supplies the Casimir; these identities imply the usual configuration-space connection is flat."),
("diagonal valuation cone", "w_a+w_b-w_c>=0 whenever kappa_ab^c!=0", "definition", "A declared integral valuation satisfying all inequalities defines a polynomial contraction; the full cone classification is a separate research gate."),
]),
("currents", [
("affine current bracket", "[X[m],Y[n]]=[X,Y][m+n]+m delta_(m+n,0)(X,Y)K", "derived", "The normalized invariant form is transported through the actual Jordan chart; K is central and mode indices are integers."),
("affine cocycle", "omega(X[m],Y[n])=m delta_(m+n,0)(X,Y)", "derived", "Skew symmetry uses the mode-sum condition; the cocycle identity uses invariance of the bilinear form."),
("mode derivation", "[d,X[m]]=m X[m]; [d,K]=0", "derived", "The derivation extends the current algebra; it is not a derivation of an arbitrary nonideal jet truncation."),
("level-one Sugawara central charge", "c=k dim(g)/(k+h_dual)=248/(1+30)=8", "derived", "Use the simple affine E8 vertex algebra at level one; this does not permit independent adjoint primary insertions at level one."),
("simple E8 state character", "H(q)=E4(q)/phi(q)^8; phi(q)=product_(m>=1)(1-q^m)", "derived", "Unshifted conformal grading: coefficients begin 1,248,4124,34752,213126. The normalized character includes q^(-1/3)."),
("colored-partition recurrence", "n p_r(n)=r sum_(j=1)^n sigma_1(j)p_r(n-j)", "exact_checked", "p_r(0)=1 and r is a nonnegative integer; all coefficients use exact integer arithmetic."),
("universal current population", "U(q)=product_(m>=1)(1-q^m)^(-248)", "derived", "PBW dimensions of the universal affine vacuum module; simple-quotient null relations have not yet been imposed."),
("basis-independent state retention", "rho_n=dim L_1(E8)_n / dim V^1(E8)_n", "definition", "This fixed-graded-algebra density differs from coordinate-dependent bracket sparsity and from geometric packing density."),
("A4 root-lattice theta enumeration", "Theta_A4(q)=sum_(x in Z^5,sum x_i=0) q^(sum x_i^2/2)", "exact_checked", "The enumeration uses a proved norm bound for each requested finite coefficient; the full identity is a formal theta series."),
("simple Jordan twining series", "T(q)=(5 Theta_A4(q)^2-E4(q))/(4 phi(q)^8)", "derived", "All 124 nonidentity dual-grading automorphisms are conjugate to the fixed-dimension-48 order-five class; the A4+A4 gluing identifies its trace."),
("all-order twining eta identity", "5 Theta_A4(tau)^2-E4(tau)=4 eta(tau)^10/eta(5tau)^2", "derived", "Both sides are holomorphic weight-four forms on Gamma0(5); the Sturm bound is two. Cusp holomorphy and matching coefficients through q squared give an all-order proof."),
("universal Jordan twining series", "U_T(q)=phi(q)^2/phi(q^5)^50", "derived", "A nonidentity grading automorphism has eigenmultiplicities 48,50,50,50,50 on E8; PBW gives this all-order trace."),
("finite Fourier grade populations", "d_(n,0)=(H_n+124T_n)/125; d_(n,a!=0)=(H_n-T_n)/125", "derived", "Use the 125-character Fourier inversion for G=F5^3; all nonidentity twines coincide. The same formula applies to universal PBW counts."),
("graded relation deficit", "r_(n,a)=u_(n,a)-d_(n,a); sum_a r_(n,a)=U_n-H_n", "definition", "The deficit counts the full null ideal at a degree and grade; it is not the arc-kernel dimension."),
("neutral-sector imbalance", "r_(n,0)-r_(n,a!=0)=[q^n](U_T-T)", "derived", "This is exact Fourier algebra and gives an all-order test of whether discarded states are grade-uniform."),
("asymptotic retention", "log rho_n ~ (4*pi/sqrt(3)-2*pi*sqrt(248/6))*sqrt(n)", "derived", "Character asymptotics describe n tending to infinity for the fixed level-one simple quotient and universal PBW population."),
]),
("kz", [
("split Casimir from exact metric", "Omega=sum_(a,b) G^ab ad(X_a) tensor ad(X_b)", "definition", "G is the normalized invariant metric with roots of squared length two; large fourth-order arrays are unnecessary."),
("five adjoint tensor channels", "248 tensor 248=1+248+3875+27000+30380", "derived", "Multiplicity-free E8 representation decomposition; four adjoint invariant tensors therefore form a five-dimensional space."),
("spectral projectors", "P_lambda=product_(mu!=lambda)(Omega-mu I)/(lambda-mu)", "derived", "The five actual split-Casimir eigenvalues are -60,-30,-12,0,2; denominator primes lie among 2,3,5,7,31."),
("KZ pair residues", "A=Omega_12|Inv(g^tensor4); B=Omega_23|Inv(g^tensor4)", "exact_checked", "The implementation reconstructs matrices from invariant-tensor evaluations and checks additional evaluations independently."),
("five-channel KZ system", "F'(z)=(A/z+B/(z-1))F(z)/(k+30)", "derived", "Generic complex level k!=-30. All five classical tensor channels survive the integrable fusion interpretation when k>=4."),
("five invariant tensor frame", "t=(G_ab G_cd,G_ac G_bd,G_ad G_bc,B([a,b],[c,d]),B([a,c],[b,d]))", "definition", "A certified invertible evaluation minor fixes the frame. Tensor identities must be checked beyond the interpolation points."),
("crossing involution", "C^2=I; B=C A C^-1 for the declared pair permutation", "exact_checked", "The exact permutation convention accompanies the matrices; crossing does not by itself prove every desired quantum identity."),
("residue characteristic identity", "A(A+60I)(A+30I)(A+12I)(A-2I)=0", "exact_checked", "The factors encode eigenvalues 0,-60,-30,-12,2 in root-length-squared-two normalization."),
("Frobenius recurrence", "((n+rho)I-h A)v_n=-h B sum_(m<n)v_m; h=1/(k+30)", "derived", "F=z^rho sum_n v_n z^n near zero. Singular recurrence matrices require compatibility or logarithmic terms."),
("resonance condition", "rho_j-rho_i in positive integers with rho_i=lambda_i/(k+30)", "definition", "Resonance is a candidate for logarithms, not a proof that logarithms occur; compatibility must be evaluated on the actual residues."),
("resonance compatibility witness", "ell^T M=0 and ell^T rhs!=0 => M v=rhs has no solution", "derived", "An exact left-kernel row certifies failure of a log-free Frobenius recurrence at the specified order and level."),
("logarithmic Frobenius ansatz", "F=z^rho sum_n sum_j v_(n,j) z^n (log z)^j", "definition", "Generalized recurrence coefficients must be solved when resonance blocks an ordinary series; unresolved log orders remain explicit."),
("certified noncommuting holonomy pair", "||UV-VU||>=positive rational lower bound at k=4", "exact_checked", "Gaussian-rational Taylor transport, rational Cauchy bounds and reflected-path crossing enclose both generator holonomies. This certifies a nonabelian image, not a classification or density theorem for the full monodromy group."),
]),
("higher", [
("terminating hypergeometric sum", "_4F_3(a,b,c,-N;d,e,f;1)=sum_(j=0)^N (a)_j(b)_j(c)_j(-N)_j/((d)_j(e)_j(f)_j j!)", "exact_checked", "Use rising factorials, nonnegative integer N, and no zero denominator on the sum's support."),
("Racah factorial sum", "{a b p;c d q}=Delta(a,b,p)Delta(a,d,q)Delta(c,b,q)Delta(c,d,p) sum_z (-1)^z(z+1)!/(four lower factorials times three upper factorials)", "derived", "Admissible triangle data fix all factorial arguments and summation bounds; rational normalization can avoid unnecessary radicals."),
("principal recoupling", "F_pq=(-1)^(a+b+c+d)*sqrt((2p+1)(2q+1))*{a b p;c d q}", "derived", "Clebsch-Gordan normalization and phase conventions must be fixed before comparing the polynomial implementation."),
("recoupling orthogonality", "sum_q F_pq F_rq=delta_pr", "derived", "Use normalized coordinates or the declared rational-frame Gram matrix; a nonorthonormal polynomial frame uses a weighted identity."),
("associativity pentagon", "F_(12)3,4 F_1,2,(34)=F_2,3,4 F_1,(23),4 F_1,2,3", "derived", "The symbol denotes compatible recouplings of four representations; pentagon consistency alone does not impose E8 Jacobi on arbitrary reduced constants."),
("reduced Jacobi constraints", "sum_channels recoupling_factor * kappa_ab^p * kappa_pc^d + cyclic=0", "definition", "Compile all components of Hom_sl2(V_a tensor V_b tensor V_c,V_d), including intermediate spins outside the eight E8 exponents."),
("forbidden-channel cancellation", "Jacobi_component_q=0 also for q notin M", "derived", "Only the first bracket's actual output is restricted to M; recoupling intermediate spaces can contain additional spins."),
("differential current Lie algebra", "L=Omega^*(M) tensor (t g[t]/t^(N+1)); d=d_dR tensor 1", "derived", "The bracket is wedge times Lie bracket with graded signs. Positive current order makes the coefficient ideal nilpotent."),
("homotopy transfer contract", "p i=1; 1-i p=d h+h d", "definition", "Actual cochain maps and a homotopy are required before transferring a DGLA to an L-infinity algebra."),
("finite higher brackets by current order", "ell_n=0 for n>N on positive-order currents modulo t^(N+1)", "derived", "Every n-input transferred tree has current order at least n; the chosen homotopy acts on the geometric factor only."),
("Moyal enveloping closure", "[x tensor f,y tensor g]_star=([x,y] tensor (f star g+g star f)+(xy+yx) tensor (f star g-g star f))/2", "derived", "The identity holds in U(g) tensor A_star. Symmetric products force directions beyond bare g when scalar multiplication is noncommutative."),
("E8 symmetric closure obstruction", "S^2(248)=1+3875+27000; Hom_E8(S^2(g),g)=0", "derived", "There is no E8-equivariant symmetric multiplication into the adjoint that closes the generic Moyal correction inside 248 directions."),
("principal quantum embedding obstruction", "delta(sum_i e_i)=sum_i h_i wedge e_i notin wedge^2(sl2_principal)", "derived", "For the standard Drinfeld-Jimbo cobracket, the principal embedding is not a Lie-bialgebra embedding. This does not exclude every twisted or quasi-Hopf alternative."),
("compatible twist search", "delta^f(s) subset wedge^2(s); delta^f(x)=delta(x)+[x tensor1+1tensor x,f]", "proposal", "The classical twist equation and higher quantization obligations must also hold; solving the linear inclusion alone is insufficient."),
("elliptic E8 dynamical dependence", "R=R(z,lambda), lambda in h^*, dim h=8", "proposal", "Use an established dynamical or half-current elliptic framework. An ordinary theta rescaling of the existing finite brackets does not prove Yang-Baxter consistency."),
]),
("relations", [
("affine PBW straightening", "X[-m]Y[-n]=Y[-n]X[-m]+[X,Y][-(m+n)]", "exact_checked", "Negative modes acting on the vacuum; a declared total order and exact commutators produce PBW normal forms."),
("vacuum annihilation", "X[m]|0>=0 for m>=0; K|0>=k|0>", "definition", "A positive-mode action can introduce central terms while commuting through negative modes."),
("level-one singular vector", "s=(e_theta[-1])^2|0>; s=0 in L_1(E8)", "derived", "The vector is nonzero in the universal level-one vacuum module and generates the standard integrability null submodule."),
("null descendant propagation", "s=0 => X_1[m_1]...X_r[m_r]s=0", "derived", "Exact PBW replay certifies each displayed descendant; a null descendant is not automatically a new arc-kernel generator."),
("Li leading symbol", "sigma_Li(v)=leading filtration component of the exact PBW relation", "definition", "Conformal degree, PBW length and Li degree are distinct gradings and must be recorded separately."),
("arc-to-Li map", "pi:J_infinity(V/C2(V)) surjects onto gr_Li(V)", "derived", "This canonical map can have nonzero kernel even when the vertex algebra has a simple character formula."),
("arc relation defect", "Delta(q)=sum_n dim(ker pi)_n q^n", "definition", "The arc-kernel differs from the entire affine null ideal. Computing characters alone does not identify these missing relations."),
("complete weight-four arc kernel", "dim J_infinity(R)_4-dim V_4=217001-213126=3875", "exact_checked", "Projected polarization proves the cubic ideal and mixed-jet quotient dimensions; the explicit3875 null-symbol submodule therefore exhausts the weight-four kernel. The infinite differential kernel remains unclassified."),
("exact nonmembership functional", "ell^T M=0; ell^T v!=0 => v notin image M", "derived", "A fully enumerated sector's relation matrix M and exact functional certify that a new relation is not generated by the declared old relations."),
("complete kernel presentation gate", "ker pi=<explicit generators and their differential consequences>", "proposal", "Requires inclusion in both directions and a completeness argument; finitely many computed degrees alone do not close the global gate."),
("projected polarization spectrum", "mu P_I delta|_(248,30380,779247,1763125)=(54/31,3/7,13/7,3)", "exact_checked", "Four explicit highest vectors exhaust Sym^3(g). The complementary scalars39/31,18/7,8/7,0 identify the projected-gradient kernel and prove the complete weight-four arc dimension."),
("relation entropy", "S_rel(n)=log(dim U_n/dim V_n)=-log rho_n", "definition", "This logarithmic retention measure is a declared interpretation of exact graded counts; it does not assign physical entropy without further assumptions."),
("index-five lattice gluing", "E8=union_(i mod5) (A4+omega_i) direct-sum (A4+omega_(2i))", "derived", "The union consists of five cosets of A4+A4; weight one realizes 48+4*50=248."),
("hypergeometric modular period", "E4=(1-lambda+lambda^2)*(_2F_1(1/2,1/2;1;lambda))^4", "derived", "Choose the branch near the modular cusp and compatible theta conventions. The hypergeometric period cancels in the unrefined normalized character E4/eta^8."),
]),
]

# These records describe concrete consequences found during the extension run.
# They supplement, rather than silently strengthen, the general-purpose gates.
GROUPS += [
("relations", [
("explicit quadratic highest vector", "e_i Q=0 for i=1..8; wt(Q)=omega_3875; Q in Sym^2(g)", "exact_checked", "The primitive seven-term quadratic is constructed by exact raising-map nullspace; its finite irreducible module has dimension 3875."),
("equivariant cubic jet generator", "F_Q=sum_a (ad(t_a)Q)*partial(t^a)", "exact_checked", "Use the actual invariant dual basis. The displayed highest vector has 783 nonzero terms and Li degree one at conformal weight four."),
("reduced affine Gram certificate", "G=[[45696,-336,-2016],[-336,210,84],[-2016,84,112]]; G*(1,-8,24)^T=0", "exact_checked", "The frame is Sym(F_Q), Q_(3,1), Q_(2,2). Full-sector pairing, not only this reduced matrix, certifies the null relation."),
("explicit weight-four null lift", "R=Sym(F_Q)-8 Q_(3,1)+24 Q_(2,2)", "exact_checked", "The actual PBW lift has 804 terms. Its leading Li symbol is F_Q and it vanishes in the level-one simple quotient."),
("complete root-weight radical check", "<w,R>=0 for all 14441 PBW monomials of conformal weight4 and root weight omega_3875", "exact_checked", "The exhaustive flag regenerates the complete sector; other root weights pair to zero by Cartan invariance. Counts are not a full infinite-kernel presentation."),
("old-source highest-weight exclusion", "ker(raise on Sym^3(g)_omega)=0; ker(raise and Omega12-2 on (Sym^2(g) tensor g)_omega)=0", "exact_checked", "Full-column-rank modular certificates at prime1009 prove rational injectivity and exclude a 3875 component from the old differential relation sources."),
("recoupling constraint loss certificate", "rank J_(7,11,13;17)=13; rank J_restricted=4", "exact_checked", "All 15 intermediate equation coordinates are retained. Keeping only exponent-labelled coordinates loses nine independent quadratic constraints in this specific problem."),
("first graded relation imbalance", "U_T(q)-T(q)=48 q^5+O(q^6)", "derived", "Together with finite Fourier inversion, null removal is uniform across all125 grades through degree4 and first differs by48 between neutral and each nonneutral grade at degree5."),
]),
("rigidity", [
("equivariant two-cochain dimension", "dim Hom_sl2(wedge^2(g),g)=170; dim End_sl2(g)=8", "derived", "The multiplicity-free principal decomposition and Clebsch-Gordan rules give these finite dimensions; all eight spins occur once."),
("actual diagonal gauge derivative", "G_(a,b,c),m=kappa_ab^c*(delta_am+delta_bm-delta_cm)", "exact_checked", "Columns are the derivatives of diagonal basis scalings in the actual principal coordinates; the exact matrix has rank eight."),
("principal-action fixed gauge", "s_1=0 => dim im G_fixed=7 in a 162-dimensional coefficient slice", "exact_checked", "All eight principal action coefficients are fixed. On gauge tangents their variation depends on the single parameter s_1."),
("Whitehead equivariant exactness", "H^2(g,g)=0 => Z^2(g,g)^sl2=d(End_sl2(g))", "derived", "Uses Whitehead's lemma and exactness of taking invariants for finite-dimensional semisimple sl2 modules. The principal centralizer is zero."),
("reduced tangent rank", "dim ker D(Jacobi)_fixed=7; rank D(Jacobi)_fixed=162-7=155", "exact_checked", "155 literal independent selected Jacobian rows and seven actual gauge columns give matching bounds. The complete grid is not assembled; Whitehead supplies an independent theoretical cross-check."),
("reconstructed gauge tangent", "s=G_pivot^-1 v_pivot; v is tangent iff v=G s", "derived", "The supplied invertible gauge minor gives an exact membership test and a failing row functional; completeness uses the declared Whitehead dependency."),
("Cartan conformal null relations", "s_l=(1/2)sum_(i,j in l)G^ij J_i[-1]J_j[-1]|0>; s_l-s_0=0 in L_1(E8)", "derived", "The31Jordan Cartans have disjoint quadratic supports, giving30independent neutral null relations; they do not exhaust the216neutral quadratic null states."),
("Cartan average and Sugawara", "omega=(1/31)sum_(l=1)^31 s_l=s_l in L_1(E8)", "derived", "The universal Sugawara expression is the average; equality of individual rank-eight Cartan states holds in the simple level-one quotient. No unrestricted mod31 equivalence is asserted."),
])]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    source = json.loads((ROOT / "data/equations.json").read_text())
    frontier = [r for r in source["equations"] if r["id"].startswith("PJ-X")]
    prefix = [r for r in source["equations"] if not r["id"].startswith(("PJ-H","PJ-X"))]
    if len(prefix) != 504:
        raise ValueError("expected the immutable 504-record pre-extension catalogue")
    digest = hashlib.sha256(json.dumps(prefix, sort_keys=True, ensure_ascii=False,
                                       separators=(",", ":")).encode()).hexdigest()
    records = []
    for component, rows in GROUPS:
        for title, equation, status, assumptions in rows:
            records.append({"id": f"PJ-H{len(records)+1:03d}", "domain": "asterion-extension",
                            "title": title, "equation": equation, "status": status,
                            "assumptions": assumptions,
                            "source": f"docs/ASTERION_{component.upper()}.md; docs/ASTERION_EXTENSION.md; src/perfectjet/asterion_{component}.py"})
    if len(records) != 88:
        raise AssertionError(f"expected 88 substantive equations, found {len(records)}")
    crosslinks = {
        "quadratic Casimir braid identities": "docs/ASTERION_KZ.md; src/perfectjet/asterion_kz.py",
        "index-five lattice gluing": "docs/ASTERION_CURRENTS.md; src/perfectjet/asterion_currents.py",
        "hypergeometric modular period": "docs/ASTERION_PERIODS.md; src/perfectjet/asterion_periods.py; https://dlmf.nist.gov/19.5",
        "recoupling constraint loss certificate": "docs/ASTERION_HIGHER.md; src/perfectjet/asterion_higher.py",
        "first graded relation imbalance": "docs/ASTERION_CURRENTS.md; src/perfectjet/asterion_currents.py",
        "Cartan conformal null relations": "docs/ASTERION_CURRENTS.md; src/perfectjet/asterion_currents.py",
        "Cartan average and Sugawara": "docs/ASTERION_CURRENTS.md; src/perfectjet/asterion_currents.py",
    }
    for row in records:
        if row["title"] in crosslinks:
            row["source"] += "; " + crosslinks[row["title"]]
    write_json(ROOT / "data/asterion_extension_equations.json", {
        "schema": "perfectjet/asterion-extension-equations/1",
        "preserved_prefix": {"equation_count": len(prefix), "sha256_of_canonical_records": digest},
        "scope": "Evidence-aware extensions; proposal records explicitly retain their open obligations.",
        "equations": records})
    source["equations"] = prefix + records + frontier
    for rel in ("data/equations.json", "src/perfectjet/resources/equations.json"):
        write_json(ROOT / rel, source)
    ranking = json.loads((ROOT / "data/equation_power.json").read_text())
    ranking["families"] = [r for r in ranking["families"] if r["rank"] != 26] + [
        {"rank": 26, "name": "Asterion fields, hypergeometric transport and higher relations"}]
    for row in records:
        ranking["assignments"][row["id"]] = 26
        ranking["callable_labs"][row["id"]] = ["asterion", "asterion-extension"]
    ranking["date"] = "2026-10-20"
    for rel in ("data/equation_power.json", "src/perfectjet/resources/equation_power.json"):
        write_json(ROOT / rel, ranking)
    atlas = ["# Equation atlas", "", "Status describes evidence in this repository. Exact checking is not Lean verification.", "",
             "| ID | Domain | Title | Equation | Status | Assumptions and limits |", "|---|---|---|---|---|---|"]
    for row in source["equations"]:
        atlas.append("| " + " | ".join(str(row[k]).replace("|", "\\|").replace("\n", " ")
                                      for k in ("id", "domain", "title", "equation", "status", "assumptions")) + " |")
    (ROOT / "docs/EQUATION_ATLAS.md").write_text("\n".join(atlas) + "\n", encoding="utf-8")
    print(json.dumps({"equations": len(source["equations"]), "new_records": len(records),
                      "ranked_families": len(ranking["families"]), "preserved_prefix_sha256": digest}))


if __name__ == "__main__":
    main()
