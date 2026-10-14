"""Build the versioned equation atlas, topic coverage, and master monograph."""
import json,re,hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

EQUATIONS=r'''
arithmetic|perfect-power equation|S(n)+k=m^d|definition|Integer polynomial S; integer n,k,m; d>=2.
arithmetic|hit count|A_{F,d}(N)=#{n in N:n<=N, exists m in Z:F(n)=m^d}|definition|Positive inputs; existential m avoids double-counting signed witnesses.
arithmetic|hit density|H_d^S(k)=limsup_{N->infinity} A_{S+k,d}(N)/N|definition|Density claim depends on the sequence class.
arithmetic|polynomial identity case|S(x)+k=G(x)^d|derived|G in Z[x] supplies a hit at each positive input.
arithmetic|historical geometric exponent|e=gcd(d,m_i); A(N)=O(N^(e/d+epsilon))|historical_report|Multiplicity notation and hypotheses must be restored before using this bound.
arithmetic|growth taxonomy|bounded; c log N+O(1); c sqrt(N)+O(1); N|historical_report|Retained square-hit classification; not a universal classification of every sequence.
arithmetic|Mordell curve|y^2=x^3+k|definition|Rational group structure and integral completeness are separate questions.
arithmetic|generalized Pell|y^2-Dx^2=N_0|definition|Nonsquare D>0 for standard unit-orbit analysis.
arithmetic|triangular reduction|(2y+1)^2=8F(n)+1|derived|Equivalent to y(y+1)/2=F(n) with odd-square reconstruction.
arithmetic|completed square|(2y+1)^2=4F(n)+1|derived|Equivalent to y^2+y=F(n).
arithmetic|quadratic discriminant|Delta(n)=b^2-4a(c-F(n)); y=(-b +/- sqrt(Delta))/(2a)|derived|a nonzero; discriminant square AND numerator divisible by 2a.
arithmetic|coefficient power chart|2x^2=3y^3; x=+/-18t^3,y=6t^2|derived|Integer parametrization; retain signs and t=0.
arithmetic|cusp power chart|x^2=y^3; x=t^3,y=t^2|derived|Integer t carries the sign of x.
pell|quadratic norm|N(x+y sqrt(D))=x^2-Dy^2|derived|Quadratic extension convention.
pell|unit orbit|x_j+y_j sqrt(D)=alpha epsilon^j|historical_report|Seed inventory and index domain must be complete.
pell|unit matrix|[x';y']=[[a,Db],[b,a]][x;y]|derived|epsilon=a+b sqrt(D); multiplication identity.
pell|sqrt2 hit recurrence|n'=3n+2m; m'=4n+3m; m^2-2n^2=1|derived|A single orbit step; seeds/domain still matter.
pell|Pell7|x^2-2y^2=-7|derived|Equivalent to (x^2+7)/2=y^2.
pell|orbit coordinate|X_j=(eta epsilon^j+(Delta/eta)epsilon^(-j))/2|historical_report|Original seed/norm convention required.
pell|input asymptotic|n_j=eta epsilon^j/(4A)-B/(2A)+O(epsilon^(-j))|historical_report|Original quadratic pullback coefficients required.
pell|filtered orbit population|A_orbit(N)=g log(N)/(pi_period log(epsilon))+O(1)|historical_report|Reachable cycle with period pi_period and g admissible positions.
pell|filtered infinitude|reachable admissible cycle iff infinitely many admissible orbit hits|historical_report|For retained finite-state orbit encoding, not arbitrary automata.
pell|unit identity|(1+sqrt(2))^6=99+70sqrt(2)|derived|Exact binomial expansion.
descent|general Weierstrass|y^2+a1xy+a3y=x^3+a2x^2+a4x+a6|definition|Nonsingular elliptic model when discriminant nonzero.
descent|Weierstrass coefficients|b2=a1^2+4a2; b4=2a4+a1a3; b6=a3^2+4a6|definition|Standard model coefficients.
descent|square completion|(2y+a1x+a3)^2=4x^3+b2x^2+2b4x+b6|derived|Direct polynomial identity.
descent|two-torsion cubic|psi2(x)=4x^3+b2x^2+2b4x+b6|definition|Leading coefficient 4; use monic normalization for the norm.
descent|cubic discriminant|disc(psi2)=16Delta_E|derived|Standard discriminant normalization.
descent|cubic etale norm|N(x-theta)=((2y+a1x+a3)/2)^2|derived|theta is root of monic psi2/4; norm-square is necessary, not sufficient for Selmer membership.
descent|squareclasses|L^*/L^(*2)|definition|Product algebra when cubic splits; do not silently assume a field.
descent|local Kummer condition|loc_v(alpha) in image(delta_v)|definition|Actual complete local images, not sampled signatures.
descent|Selmer intersection|Sel2={alpha in appropriate global squareclasses:loc_v(alpha) in image(delta_v) for all v}|definition|S-unit/class-group/norm conditions must also be supplied.
descent|unit-class sequence|O_{L,S}^*/O_{L,S}^{*2}->L(S,2)->Cl(O_{L,S})[2]|historical_report|Recover exact sequence conventions before downstream proof.
descent|Selmer exact sequence|0->E(Q)/2E(Q)->Sel2(E/Q)->Sha(E/Q)[2]->0|derived|Standard 2-Selmer interpretation.
descent|anonymous model|y^2=x^3+2x^2-12x+16|historical_report|v1.67 report; not imported as a complete descent implementation.
descent|anonymous field|u^3+8u^2-192u+1024=0|historical_report|Field discriminant reported -107; polynomial and field discriminants differ.
transport|affine pullback|F(n)=(rn+s)^3+k|definition|r nonzero for inverse transport.
transport|transported list|W={((t-s)/r,y):(t,y) in L_k, r divides t-s}|derived|L_k must be complete to conclude complete pullback.
transport|list contract|m^2=F(n) iff (n,m) in W|conditional|Requires complete source list and preserved domains.
transport|Thue23 first|-u^3-3u^2v+6uv^2+4v^3=1|historical_report|Retained descent leaf; all branches/reconstruction needed.
transport|Thue23 second|-u^3-6u^2v+69uv^2+46v^3=1|historical_report|Retained descent leaf.
transport|field621|theta^3-6theta-3=0|historical_report|Associated field representation in archive.
transport|D72 leaf|H(u,v)=-3u^3+9uv^2-2v^3=+/-1|historical_report|Residual branch, not a closure claim.
transport|D72 field|beta^3-27beta-18=0|historical_report|Coordinates and order matter.
transport|D72 norm|gamma=-3u-beta v; N(gamma)=9H(u,v)=+/-9|historical_report|Exact identity attached to the selected field/order.
transport|D72 units|gamma=zeta alpha_j epsilon1^e1 epsilon2^e2|historical_report|Need representatives and effective global exponent bounds.
transport|D72 reconstruction|C=0; 3 divides A; u=-A/3; v=-B|historical_report|Coordinate restrictions are part of completeness.
transport|scaled rational kernel|K=det(BB^T)I-B^T adj(BB^T)B|derived|Full row rank for nondegenerate projector interpretation.
transport|kernel identities|BK=0; Bx=0 implies Kx=det(BB^T)x|derived|Rational-span statement does not prove integral saturation.
transport|Smith form|UBV=D|exact_checked|Unimodular U,V; d_1|d_2|...; replayed in lattice.py against gcd-of-minors divisors.
transport|integral solvability|d_i divides (Ub)_i; remaining coordinates (Ub)_i=0|exact_checked|For Smith form of Bx=b; failure returns a certificate row.
counting|resource polynomial|P(z)=product_j(1+product_k z_k^{c_jk})|derived|Nonnegative integral costs; extra compatibility requires extra factors/state.
counting|capacity population|#F=sum_{a<=b}[z^a]P(z)|derived|Componentwise capacity bound.
counting|profit polynomial|P(z,t)=product_j(1+t^{p_j}product_k z_k^{c_jk})|proposal|Laurent t exponents if profits negative.
counting|completion recurrence|C(q)=C(q0)+C(q1)|exact_checked|Disjoint binary prefixes; populations.py and exhaustive comparisons.
counting|terminal count|C(q)=1 if complete and feasible else 0|exact_checked|Original objects counted once.
counting|ranking|rank(x)=sum_{i:x_i=1} C(x_<i 0)|exact_checked|Lexicographic original project order.
counting|unranking|r<C(q0):choose0; else choose1 and r<-r-C(q0)|exact_checked|0<=r<C(q).
counting|uniform sampling|Pr(0|q)=C(q0)/C(q)|derived|Exact uniformity over original objects, not quotient representatives.
counting|factor population|Z=sum_x product_j f_j(x_scope_j)|definition|Finite domains and specified weight algebra.
counting|variable elimination|g(x_rest)=sum_{x_i}product_{j containing i}f_j|derived|No duplicated auxiliary witnesses.
counting|auxiliary uniqueness|for every original legal x, #{y:encoding(x,y)}=1|definition|Needed to preserve population under functional encodings.
counting|Petersen historical total|702508860122761; optimum=16537; tie_count=1|historical_report|Upstream retained result; original 50-project data not included here.
counting|population aggregation|Z_{A disjoint-union B}=Z_A+Z_B; Z_{A times B}=Z_A Z_B|derived|Disjointness / independence essential.
counting|exponent-pattern polynomial|product_i(1+q+...+q^{a_i})|definition|Prime-exponent populations.
counting|power-exponent criterion|d divides gcd(a_1,...,a_s)|derived|Positive integer prime factorization; handle 1 separately.
series|weighted transfer series|G(z)=H(I-sum_c z^c A_c)^(-1)s|derived|Positive integral costs; finite-dimensional formal series.
series|resolvent expansion|(I-M(z))^(-1)=sum_{ell>=0}M(z)^ell|derived|M has zero constant term, or other convergence hypotheses.
series|Fibonacci series|1/(1-z-z^2)|definition|Initialization determines sequence offset.
series|zero-series initialization|z/(1-z)=0+z+z^2+...|historical_report|Zero initial sample can change minimal realization size.
series|linear response|G(z)=C(I-zA)^(-1)B; coefficients=CA^kB|derived|Linear input/output convention.
series|Hankel matrix|H_{u,v}=f(uv)|exact_checked|Word-indexed predictive state; finite rank over a field; exact on the supplied block only.
series|linear word realization|f(w)=alpha^T A_{a1}...A_{aell} beta|derived|Minimal field realization dimension equals finite Hankel rank; positivity is separate.
semantics|semantic fibre|pi:I->S; I_s=pi^(-1)(s) intersect L|definition|Legal implementations of a meaning.
semantics|cost realization|i*=argmin_{i in I_s}cost(i)|proposal|Minimum must exist or infimum used.
semantics|future equivalence|x~y iff all finite permitted words have equal behavior|exact_checked|Partial definedness included; finite machine replay.
semantics|quotient dynamics|qF_a=Fbar_a q|exact_checked|Observation and definedness preserved.
semantics|quotient observation|O=Obar q|exact_checked|Chosen output family only.
semantics|completeness|q(x)=q(y) iff x~y|exact_checked|Finite Python quotient, not new Lean theorem.
semantics|distinguishing word|exists w:behavior(x,w)!=behavior(y,w)|exact_checked|Shortest witness via pair BFS.
semantics|question refinement|Q subset Q' implies equivalence(Q') subset equivalence(Q)|derived|More questions can only refine the state partition.
semantics|joint representation|q=(q1,q2)|proposal|Then remove redundant distinctions relative to joint questions.
observability|row closure|O=span{rows(CA^k):k>=0}|exact_checked|Finite rational matrices; exact observable-space compiler.
observability|hidden space|N=intersection_{k>=0}ker(CA^k)|derived|Linear all-future output equivalence.
observability|target recovery|ker(O) subset ker(G) iff G=L O|exact_checked|Finite dimensions; hidden-vector failure witness.
observability|hidden target amplitude|max_{delta in ker(H) intersect ker(M),norm(delta)<=1}|g^T delta||derived|Norm must be declared; Euclidean formula uses orthonormal hidden basis.
observability|quadratic fibre constancy|N^T(g+Qx0)=0 and N^T QN=0|derived|T=g^Tx+1/2 x^TQx, symmetric Q, full affine fibre x0+image(N).
observability|sensor repair|ker(Hnew N) subset ker(GN)|derived|Repairs target-affecting hidden directions.
observability|information matrix|J=H^T R^(-1)H|definition|Positive noise covariance; prior added separately.
observability|sensor sensitivity|d(g^T P g)/dw=-(h^T P g)^2|derived|P=(J0+w hh^T)^(-1), nonsingular.
observability|stable recovery|G^*G <= lambda O^*O|historical_report|Bounded-operator assumptions; exact recovery and stable recovery differ.
observability|delay coordinates|Psi_L=[O;O F;...;O F^(L-1)]|proposal|Linear observability rows become [C;CA;...]; nonlinear sufficiency needs hypotheses.
features|finite feature closure|p_i composed F in span_Q{p_j}|exact_checked|Exact coefficient replay, not fitted regression.
features|feature evolution|p(F(x))=G p(x)|exact_checked|Output must belong to retained feature span.
features|all-time feature evolution|p(F^t(x))=G^t p(x)|derived|Induction from exact closure.
features|closure defect|psi(F(x))=G psi(x)+r(x)|definition|Explicit residual rather than silent truncation.
features|defect state augmentation|[psi';chi']=[[G,B],[C,D]][psi;chi]|proposal|r=Bchi and chi'=Cpsi+Dchi; closure may never terminate.
features|parameter sensitivity|S_{t+1}=D_xF S_t+D_theta F|derived|Differentiable parameterized dynamics.
features|linear sensitivity|S'=A S+A_theta x+B_theta u|derived|Discrete-time prime notation means next state; input fixed relative to parameter.
dynamics|reconstruction error|e=x-Vz|definition|State error versus output error distinguished.
dynamics|evolution defects|R=AV-VG; S=B-VH|exact_checked|Compatible linear model/reconstruction matrices.
dynamics|error recurrence|e_next=Ae+Rz+Su|derived|Direct substitution into full and reduced dynamics.
dynamics|error convolution|e_t=A^t e0+sum_{j<t}A^(t-1-j)(Rz_j+Su_j)|derived|Exact finite-time identity.
dynamics|continuous Lyapunov|A^T P+PA<=-2alpha P; P>0|derived|Continuous time; alpha positive for decay.
dynamics|discrete Lyapunov|A^T PA<=gamma^2 P; 0<=gamma<1|derived|Discrete time; fixed metric.
dynamics|contractive error|norm(e_t)<=gamma^t norm(e0)+sum gamma^(t-1-j)delta_j|exact_checked|Defects nonnegative bounds in the same contracting norm.
dynamics|uniform defect bound|norm(e_t)<=gamma^t norm(e0)+delta(1-gamma^t)/(1-gamma)|derived|Supremum defect delta and gamma<1.
dynamics|composed error|epsilon_total<=epsilon1+norm(V1)epsilon2|derived|Compatible reconstruction stages.
dynamics|nonlinear composed error|epsilon_total<=epsilon1+L1 epsilon2|derived|First reconstruction Lipschitz with constant L1.
dynamics|decision certificate|Jhat(a*)-epsilon_a*>max_{b!=a*}(Jhat(b)+epsilon_b)|exact_checked|Deterministic interval bounds; empirical uncertainty separate.
energy|mass energy|E=1/2 u^T M u|definition|Constant symmetric positive-definite M.
energy|symmetric energy operator|S_M=(A^T M+MA)/2|exact_checked|u'=Au+f.
energy|energy derivative|E'=u^T S_M u+u^T M f|exact_checked|Direct identity; boundaries/sources in A or f.
energy|corrected decay dial|lambda=-2u^T S_Mu/(u^TMu)|exact_checked|Nonzero state; sign chosen for predicted decay.
energy|corrected source term|zeta=2u^T Mf/(u^TMu)|exact_checked|Positive source reduces net decay when lambda>0.
energy|corrected residue|d log(E)/dt=-lambda+zeta; rho=1-zeta/lambda|exact_checked|rho undefined at lambda=0; historical plus-sign formula rejected.
energy|CRO measured rate|alpha_hat=-(log E_k-log E_{k-1})/Delta_t|definition|Positive energies; window and integration scheme retained.
energy|CRO residual|R1=|alpha_hat-alpha||definition|Diagnostic, not proof of physical universality.
energy|rank-one crystalline matrix|S(t)=I+t11^T; det(S)=1+nt|derived|n-dimensional all-ones vector.
energy|invariant-space leakage|(I-P)AP|definition|Zero iff range(P) invariant when P is a projection.
imp|SVD projector|M=U Sigma V^T; P=QQ^T|historical_report|Unit singular vectors do not establish invariant fixed modes.
imp|rejected SVD limit|all selected singular values=1 implies M^k->P|rejected|Orthogonal rotation counterexample.
imp|sufficient fixed-mode split|M=P+T; P^2=P; PT=TP=0; rho(T)<1|derived|Then M^k=P+T^k and M^k x->Px.
imp|general invariant reduction|MQ=QG|derived|Retained dynamics may evolve instead of remaining fixed.
imp|exact retained evolution|M^k Q=QG^k|derived|Induction from intertwining.
psg|potential|L=-log cos(x); U=x^2+L^2; K_alpha=U^(-alpha/2)|definition|0<x<pi/2; global contraction is not assumed.
psg|support functions|T=tan(x); H=x+LT; A=xH/(2U)|definition|Archive A<1/2 claim contradicts retained root A*=0.674... .
psg|corrected derivative|K_alpha'=-alpha H K_alpha/U|derived|U'=2H; factor-of-two repaired.
psg|flip parameter|alpha=1/(2A)|numerical_checked|At a fixed point with multiplier -1.
psg|scalar balance|F(L)=log U(L)+4A(L)log x(L)=0|numerical_checked|x=acos(exp(-L)); bracket replay only, not uniqueness/transcendence proof.
psg|coordinate derivatives|x'=1/sqrt(exp(2L)-1); L_x'=tan x; T_x'=1+T^2|derived|Positive L and admissible angle.
psg|root receipt|L*=0.531916689243299; x*=0.942857679982338; alpha*=0.741804515087895|numerical_checked|Floating root reproduction, historical higher precision not re-certified.
psg|coefficient curve|a(v)=x(x+(v/2)T)/(2(x^2+v^2/4)); x=acos(exp(-v/2)); T=sqrt(exp(v)-1)|historical_report|Correct v=2L convention; archive typography inconsistent in places.
psg|exponential extraction|E F1+F0=0; E=exp(v)-1=-F0/F1|historical_report|p=a'; F1 nonzero; original numerator and certificates needed.
psg|F0|a(2a-1)(v+4-8a)^2|historical_report|Factor structure preserved.
psg|F1|(av-2a-2pv+1)(2av+4a-4pv-v-2)|historical_report|Factor structure preserved.
psg|cleared jet field|Xtilde=D partial_v+Dp partial_a+N partial_p|historical_report|D=2av^2(2a-1)(v+4-8a)^2; full N absent from read document.
psg|Darboux equation|Xtilde(H)=KH|definition|Listed identities do not by themselves establish unrestricted classification.
psg|PSG source elimination|P(x,L,T)=0; T^2=Y^2-1; T=-A/B|historical_report|26-term source/100-term elimination reported; B=0 and integer-image branches must remain.
psg|normalized amplitude jet|A/A*=1+.3282804759delta+.0800766090delta^2+.0108819139delta^3+...|historical_report|Root-centered finite jet; not an origin-germ coefficient table.
psg|normalized balance jet|F/(L*F')=delta-.3793897467delta^2+.3008496421delta^3-.2807207864delta^4+...|historical_report|Declared normalization required.
psg|logarithmic derivative|I=F''/F'|definition|Derivative ratio; archive sometimes conflates Taylor factorial conventions.
jets|Schroeder equation|Psi(f(x))=-Psi(x)|conditional|Locally invertible exact solution requires f^2=id.
jets|reflection criterion|Psi=(x-f(x))/2; f^2=id implies Psi composed f=-Psi|derived|Centered analytic f with f'(0)=-1 gives Psi'(0)=1.
jets|flip obstruction|f=-x+ax^2+bx^3+...; f^2-x=-2(b+a^2)x^3+...|exact_checked|Centered coordinates; coefficient convention without factorials.
jets|two-cycle leading sign|f_nu=-(1+nu)x+kappa x^3+...; x^2~nu/kappa|derived|Real small cycle requires positive ratio; parameter-dependent fixed point recentered.
jets|Riccati coefficient law|(n+1)i_{n+1}=a 1_{n=0}+b i_n+c sum_{j=0}^n i_j i_{n-j}|exact_checked|Specific ODE I'=a+bI+cI^2; not a transcendence test.
jets|Riccati rejection residual|r_n=(n+1)i_{n+1}-a1_{n=0}-b i_n-c sum i_j i_{n-j}|exact_checked|Nonzero exact residual rejects this fixed model.
jets|Puiseux series|xi=a1 sqrt(epsilon)+a2 epsilon+a3 epsilon^(3/2)+...|proposal|Check second-iterate signs before claiming a real branch.
jets|seventh-order freedom|b7 leaves orders0..6 unchanged; order7 coefficient=1/128|historical_report|Specific archived wall normalization; not recomputed here.
recurrences|Padovan|P_n=P_{n-2}+P_{n-3}; characteristic=x^3-x-1|definition|Initial conditions fixed separately.
recurrences|Padovan modes|P_n=A psi^n+B q^n+conjugate(B q^n)|derived|Distinct characteristic roots and real initial data.
recurrences|Fibonacci kernel|F_{n+1}=sum_{k=0}^{floor(n/2)} binomial(n-k,k)|derived|Standard finite combinatorial identity.
recurrences|Tribonacci|T_n=T_{n-1}+T_{n-2}+T_{n-3}; x^3-x^2-x-1=0|definition|Separate family from Catmull-Clark operator spectra.
recurrences|Escher-Pisot proposal|F_{n+1}(z)=lambda F_n(exp(2pi i alpha)conj(z))+sum_k(-1)^k theta^(-2k-1)binomial(n-k,k)q^(k(k+1)/2)+Phi(F_n(z))|proposal|Finite k range for given n; no global contraction from lambda>1.
recurrences|mode stability|abs(lambda exp(-im alpha)+a)<1|conditional|Specified linearized mode only.
topology|MMHW wavelet|psi_{alpha,beta}(x)=(1-alpha x^2)exp(-x^2/2)(1+beta sin(pi x^2)exp(-abs(x)^3))|proposal|Wavelet admissibility and topological accuracy need separate analysis.
topology|subdivision block|M=[[-7/48,3(1+i sqrt3)/32],[5(1-i sqrt3)/16,-9/8]]|historical_report|Particular local block, not established full refinement operator.
topology|block characteristic|chi=x^2+61x/48+3/64|derived|Trace/determinant checked in session; one root magnitude>1 prevents naive contraction claim.
topology|finite quadratic phases|b(x,y)=q(x+y)-q(x)-q(y)|definition|Finite nondegenerate quadratic module conventions.
topology|finite S,T|S_xy=|A|^(-1/2)exp(-2pi i b(x,y)); T_xx=exp(2pi i q(x))|definition|Choice of sign fixes relations.
topology|modular relations|S^2=C; (ST)^3=xi C; xi=|A|^(-1/2)sum_x exp(2pi i q(x))|conditional|Correct quadratic-module hypotheses and convention.
conductor|rotation algebra|UV=exp(2pi i theta)VU|definition|Generator conventions explicit.
conductor|clock shift convention|Ue_j=e_{j+1}; Ve_j=omega^j e_j; VU=omega UV|derived|Corrects sign/order mismatch with alternate UV convention.
conductor|irrational trace range|Z+theta Z|historical_report|K-theory/trace conventions for A_theta.
conductor|Weil commutant|c=dim{X:XS=SX,XT=TX}|definition|Operator pair must be specified, particularly dyadic case.
conductor|odd prime law|c(p^a)=a+1|historical_report|Specific Weil core; not imported formal theorem.
conductor|multiplicativity|c(mn)=c(m)c(n), gcd(m,n)=1|conditional|Requires product representation compatibility.
conductor|model-specific dyadic|c(2^a)=2a-1|historical_report|Different archive cyclic dyadic pair gives 1,3,8,19,...; do not conflate models.
conductor|DAT hardware gates|C_cond<C_Pauli and p_eff<p_th|proposal|Illustrative rates are not measured native hardware.
conductor|continued-fraction tower|chi(theta)=limsup log(q_{n+1})/log(q_n)|definition|Growth diagnostic, not an inverse system without supplied bonding maps.
conductor|bounded type tower|a_n<=A implies q_{n+1}<=(A+1)q_n and chi=1|derived|Irrational continued fractions.
conductor|finite phase approximation|abs(j theta-j p_n/q_n)<=1/q_{n+1}, j<=q_n|derived|From convergent error bound; trace claims require output continuity.
conductor|su2 quantum dimension|D^2=L/(2sin^2(pi/L))|derived|L=k+2>=3; direct sine-sum identity.
conductor|Weyl volume|D^2=|P/Q| L^r/product_{alpha>0}(2sin(pi<rho,alpha^vee>/L))^2|historical_report|Archived simply-laced scope; nonsimply-laced normalization separate.
conductor|volume asymptotic|D^2~C_g L^(r+2|Phi+|)=C_g L^dim(g)|derived|For fixed valid root-data formula.
conductor|fusion wall corrected variable|U_{L-1}(X/2)=0; X=2cos(theta)|derived|Use monic integer polynomial, rather than silently treating nonmonic U_m(x) as a monic Z[x] quotient.
collision|valuation kernel|kappa(m,n)=sum_p v_p(m)v_p(n)|exact_checked|Positive integers; arithmetic dot product.
collision|coprime orthogonality|kappa(m,n)=0 iff gcd(m,n)=1|exact_checked|Nonnegative valuations.
collision|multiplicative bilinearity|kappa(mn,r)=kappa(m,r)+kappa(n,r)|exact_checked|Valuation additivity.
collision|divisor collision defect|F_{m,n}(q)=R_m(q)R_n(q)-R_mn(q)|derived|R_n product over prime-exponent intervals.
collision|collision zeta|Z_t(s)=sum_{m,n} exp(t kappa(m,n))/(mn)^s|definition|t real<=0 and Re(s)>1 ensures absolute convergence.
collision|Euler factor|product_p sum_{a,b>=0} exp(tab)p^(-s(a+b))|derived|Absolute convergence or appropriate formal interpretation.
collision|positive-temperature divergence|exp(tN^2)p^(-2sN) does not tend to zero for real t>0|derived|Single-prime diagonal suffices.
collision|coprime endpoint|Z_{-infinity}(s)=zeta(s)^2/zeta(2s)|derived|Re(s)>1; monotone/dominated limit for real parameters.
collision|historical thermal factor|Z_t(s)=zeta(s)^2 H_t(s)|historical_report|t<0; analytic continuation/remainders require original hypotheses.
collision|historical count asymptotic|A_t(X)=H_t(1)Xlog X+((2gamma-1)H_t(1)+H_t'(1))X+...|historical_report|Original Tauberian/analytic bounds not imported.
collision|finite numerator|N_L(x)=sum_{r,s=0}^{L-1}zeta_L^(rs)x^(r+s)|exact_checked|Exact ring implementation and series convolution comparisons.
collision|rational closure|L_L(x)=N_L(x)/(1-x^L)^2|exact_checked|Formal series or abs(x)<1.
collision|direct coefficient|a_n=sum_{j=0}^n zeta_L^(j(n-j))|exact_checked|Retains full and partial residue blocks.
collision|affine-periodic coefficient|a_{dL+r}=dG_r+B_r|exact_checked|G complete sum, B partial sum, 0<=r<L.
collision|stride recurrence|a_{n+2L}-2a_{n+L}+a_n=0|exact_checked|All n>=0; finite exact state.
collision|numerator checkpoints|N_L(0)=1; N_L(1)=L; leading coefficient=zeta_L|exact_checked|For L>=2; L=1 special but implemented.
collision|rejected penalty PSD|exp(-beta kappa(m,n)) is always PSD|rejected|On {1,2}, determinant exp(-beta)-1<0 for beta>0.
collision|positive valuation kernel|K_beta(m,n)=exp(-beta norm(v(m)-v(n))^2)|derived|beta>=0, finite valuation supports; Gaussian PSD.
collision|Gaussian factorization|K=e^(-beta norm(v(m))^2)e^(-beta norm(v(n))^2)e^(2beta kappa(m,n))|derived|Similarity role differs from collision suppression.
collision|prime-zeta decomposition|log Z_Gamma,L=r log zeta(Ls)+sum_m a_m P(ms)|historical_report|Original numerator/branch conventions; P prime zeta.
collision|branch-stripped product|FPbr= zeta(L)^r product_p[N(1/p)exp(-a1/p)]|historical_report|Finite factors, zeros, and branch conventions explicit.
collision|finite-part tail|abs(log tail)<=C/P; abs(tail-1)<=exp(C/P)-1|derived|Requires proved local remainder bound abs(r_p)<=C/p^2 beyond cutoff.
collision|failed dimension weld|FPbr != D^2 under retained projection/normalization sweep|historical_report|Bounded tested family, not exclusion of every possible relationship.
core|core cubic|alpha^3-alpha^2+1=0|exact_checked|Transported from cubic quotient ring.
core|critical cubic|u^3-4u^2+5u-1=0|exact_checked|Canonical ring modulus in rings.py.
core|plastic transport|u=1+alpha; beta=-1/alpha; beta^3-beta-1=0|exact_checked|Explicit inverse maps; not discriminant-only identification.
core|critical factorization|(z-1)^2(z^3-4z^2+5z-1)|historical_report|Critical ideal elimination source retained; not recomputed full ideal.
core|abelian shadow cubic|z^3-2z^2-z+1; disc=49|historical_report|Conductor7 cyclic shadow versus nonabelian core.
core|Hessian element|h=(-2u^2+3u-2)/(-u^2+u); h^3+4h^2-23h+23=0|exact_checked|Denominators invertible; field coordinates retained.
core|vertex element|v=(6u-8)/(3u^2-8u+5); 23v^3+4v+200=0|exact_checked|Archived quantity, no new physical loop prediction.
core|corner family|P_{a,b}(z)=(1-z)^a-z^b|definition|Bounded divisibility census not global isolation.
core|regulator volume report|3D(alpha)=2.8281220883307831628...|historical_report|Selected complex embedding/orientation; volume identification requires geometric input.
core|Bloch conjugation|D(conjugate(z))=-D(z)|derived|All-conjugate unweighted sum cancels.
core|oriented regulator|R(xi)=(D(sigma1 xi),...,D(sigmar xi)); scalar=c^T R|proposal|One embedding per conjugate pair; c from geometry.
core|regulator magnitude|norm(R(xi))^2|proposal|Conjugation-choice independent magnitude, not automatically volume.
deformation|cotangent fibre|L_{B/Q} tensor k(p)=[I/I^2 tensor k(p) -> Omega tensor k(p)]|historical_report|Local complete-intersection convention; differential df_p.
deformation|point lift|df_p(v)+g(p)=0|derived|Square-zero deformation f+epsilon g and marked point p+epsilon v.
deformation|cusp|f=y^2-x^3; Tjurina=Q[x,y]/(f,f_x,f_y)=span{1,x}|historical_report|Characteristic0 or suitable good characteristic.
deformation|E37 model|Y^2=X^3-16X+16; Delta=151552; j=110592/37|derived|Standard short-Weierstrass invariants.
deformation|E37 tangent|dj=(559872/1369,373248/1369); gauge=(64,-96); moduli=(96,64)|historical_report|dj(gauge)=0; dj(moduli)=77635584/1369.
deformation|discriminant formula|Delta=-16(4a^3+27b^2); j=1728(4a^3)/(4a^3+27b^2)|derived|Nonsingular short model; coordinate scaling can alter Delta while preserving j.
deformation|Zsqrt-5 divisors|(2)=p2^2; (3)=p3+ p3-; (1+/-sqrt(-5))=p2 p3+/-|historical_report|Archive weight-one Picard/K0 comparison; not arbitrary higher weights.
deformation|stationary sensitivity|dx*/d epsilon=-(Hessian V0)^(-1)gradient W|derived|Nonsingular Hessian; symmetry zero modes require quotient/gauge fixing.
deformation|relation response|dR/d epsilon=-gradient R^T(Hessian V0)^(-1)gradient W|derived|Allowed perturbation space must be specified.
codes|Artin-Schreier-Witt|0->Z/p^n->W_n --F-1-->W_n->0|historical_report|Characteristic p etale sheaf setting; not mixed-characteristic elliptic descent.
codes|Hermitian curve|y^p+y=x^(p+1)|definition|Over F_{p^2}; code divisor/evaluation set needed.
codes|Hermitian code reports|[8,4,4]_4; [27,6,19]_9; [125,3,119]_25|historical_report|Retained numerical/exact reports, implementation not imported.
codes|p5 weight enumerator|12000z^119+600z^120+3000z^124+24z^125|historical_report|Nonzero words; add constant1 for full enumerator.
codes|alternate curve|X_q:y^q+y=x^2; n_q=2q^2-q|historical_report|Point-count convention and q conditions must be supplied.
prefix|normal binary64|x=(-1)^s(2^52+F)2^(E-1075)|derived|Normal finite values only; subnormals special.
prefix|monotone integer encoding|MIE(raw)=raw xor 2^63 if nonnegative; raw xor(2^64-1) if negative|historical_report|Frozen bit convention; NaNs/signed zeros explicitly handled in original model.
prefix|prefix depth|lcp(a,b)=clz(MIE(a) xor MIE(b)); k(x)=lcp(x,+0); D=64-k|definition|Same bit depth can mean different numerical precision across binades.
prefix|prefix distance|d(a,b)=2^(-lcp(a,b)) for a!=b; d(a,a)=0|derived|Ultrametric on finite bit encodings, not ordinary real distance.
prefix|dyadic power test|x=+/-u2^e, u odd; u=v^d and d divides e|derived|Rational dth powers; negative sign allowed only odd d; zero separate.
prefix|restricted transfer heuristics|ADD=min(kA,kB); MUL=max(0,kA+kB-53); DIV=max(0,kA-kB); SQRT=max(0,kA-1)|historical_report|Not universal IEEE754 guarantee; binade/cancellation cases matter.
prefix|prefix bookkeeping|Delta_pflux=k_result-k_in; Ksys_new=Ksys_old-k_old+k_result|definition|Register selection and meanings explicit.
prefix|prefix Fermat proposal|k(f(x+delta),f(x))>=k(delta)-kappa_f|proposal|Restricted operation/domain hypotheses and exact bit semantics needed.
physics|SYMMETRON Hamiltonian|H=L0-c/24+sum_g gamma_g T_g+kappa log L0|proposal|Positive spectral domain for logarithm; not a validated gravity theory.
physics|log-periodic coupling|g(E)~E^alpha[1+A cos(2pi log(E/E0)/log C)]|proposal|Parameters and units specified before physical interpretation.
physics|L-value constant proposals|alpha=L(E,1)/(2pi); beta=L(f,3/2)/pi^(3/2); kappa=L'(g,1)/L(g,1)|proposal|Underlying objects not recovered; cannot use as determined constants.
physics|activation model|F(x)=1/(1+exp(-x/.0712)); H*=H+alpha abs(H)^beta F(H/Ep)|proposal|Functional calculus, units, and physical fit not established.
physics|spectral dimension model|d_s(E)=4-alpha(E/Ep)^beta F(E/Ep)|proposal|Model ansatz, not observed dimension law.
physics|six-term potential|U(theta)=cos2theta+(2/3)cos3theta+(2/5)cos5theta+(1/4)cos8theta-(2/9)cos9theta-(1/6)cos12theta|historical_report|Local phase check distinct from physical CKM prediction/global proof.
physics|phase derivative|U'=-2sin2theta-2sin3theta-2sin5theta-2sin8theta+2sin9theta+2sin12theta|derived|Direct derivative.
physics|golden phase identity|theta*=11pi/30; 1-2cos(12theta*)=(3-sqrt5)/2=phi^(-2)|derived|Shared by other phase points; does not alone select66degrees.
physics|observable ratio|Ceff=|Uub|(1-|Uub|^2)/(|Uus||Ucb|)|definition|Nonzero denominator; model must enforce value.
physics|conditional observable polynomial|c^2(1-c^2)^2-3abc(1-c^2)+a^2b^2=0|conditional|a=|Uus|,b=|Ucb|,c=|Uub|, if Ceff=phi^-2.
physics|unresolved archived polynomial|c^2 t^4-7abc t^2+a^2b^2=0|open|Original a,b,c,t definitions unrecovered; do not equate with coefficient3 relation.
physics|unresolved phase polynomials|4t^2 J^2=4K-N^2; N^8-7N^6K+14N^4K^2-8N^2K^3+K^4=0|open|Original N,K,t,J definitions missing.
physics|allowed perturbation|V_epsilon=V0+epsilon x|historical_report|A CP-even deformation changed the golden relation; protection unresolved.
physics|coercivity certificate|f-L=sigma0+sum_i sigma_i g_i+sum_j q_j h_j|proposal|SOS positivity and constraint conventions needed; no universal optimizer guarantee.
physics|wall threshold law|Gamma proportional (M-2m)^3 near threshold|historical_report|Specific channels/model, not universal decay law.
wind|vorticity|zeta=v_x-u_y|definition|Coordinates and velocity components explicit.
wind|stretch tilt divergence|S=(zeta+f)w_z; T=-v_z w_x+u_z w_y; D=-(zeta+f)div(u)|historical_report|Saved signed-source ledger; governing equation convention must match.
wind|baroclinicity|B=(rho_x p_y-rho_y p_x)/rho^2|historical_report|Density positive; coordinate signs fixed.
wind|forcing beta source|F=(curl forcing)_z; P_beta=-beta v; S_zeta=S+T+D+B+F+P_beta|historical_report|Budget term ledger, not full unobserved atmosphere reconstruction.
wind|exact SDE|F=exp(A Delta_t); Qd=int_0^Delta_t exp(As)LL^T exp(A^Ts) ds|derived|Linear constant-coefficient SDE.
wind|innovation support|I=sum_i K_i nu_i^T S_i^(-1)nu_i|historical_report|K_i spatial support kernel, not necessarily Kalman gain.
wind|constraint injection|C=delta_xC^T Q delta_xC|definition|Declared metric; mechanism and causality separate.
wind|dynamic residual|R=norm(W[partial_t x+N(x)-F(x)])^2|definition|Units, supports, operators required.
wind|expiry rule|t_exp=inf{t:A_struct^2/V0>=eta_s or Vplus/V0>=eta_p}|historical_report|Baseline positive; model expiry criterion.
wind|exterior law|v=c r^(-p); p=1+2h|historical_report|Quadrant envelopes are not pointwise wind samples.
wind|pressure adequacy|Delta_t<=L/(2U); quadratic fit needs at least7 stations|historical_report|Six coefficients plus residual degree of freedom, rank/conditioning separately checked.
wind|assimilation commutator|[A,F]x|proposal|Order effects between assimilation and dynamics.
sequence|Pauli product|(a.sigma)(b.sigma)=(a.b)I+i(a cross b).sigma|derived|Standard Pauli convention.
sequence|commutator|[a.sigma,b.sigma]=2i(a cross b).sigma|derived|Order-sensitive interaction, not automatically empirical predictive feature.
sequence|symmetric-order split|AB=1/2{A,B}+1/2[A,B]|derived|Algebraic identity.
sequence|nested interaction|[A,[B,C]]|proposal|Higher-order feature; test against commutative ablation.
graphs|weighted histogram|Z_N(u)=sum_n c_n exp(n.u)|exact_checked|Histogram partition exact for rational multiplicative weights; log derivatives mathematical.
graphs|gradient covariance|grad log Z=E[n]; Hessian log Z=Cov(n)>=0|derived|Finite positive partition function.
graphs|phase domination|abs(Z_N(u+i phi))<=Z_N(u)|derived|Positive multiplicities; triangle inequality.
graphs|subcritical tail|sum_{ell>=d}C(mu eta)^ell=C(mu eta)^d/(1-mu eta)|derived|mu eta<1 and justified graph-count domination.
graphs|finite histogram compression|4133166 walks ->66 type vectors|historical_report|Specific retained length10 graph; order-specific observables require richer state.
finsler|dead-zone action|phi(v)=0 if abs(v)<=c; (abs(v)-c)^2/(4D) otherwise|definition|D>0,c>=0.
finsler|convex conjugate|phi*(p)=c abs(p)+D p^2|derived|Exact Legendre transform of declared dead-zone action.
finsler|Hamiltonian|H=b.p+sum_i(c_i abs(p_i)+D_i p_i^2)|derived|Normalization tied to the displayed Lagrangian.
finsler|Hamilton-Jacobi|H(x,grad W)=0|proposal|Viscosity/subgradient treatment at nonsmooth facets.
finsler|FW action|S=1/4 int (xdot-b)^T D^(-1)(xdot-b) dt|definition|Noise normalization fixes epsilon and diffusion factors.
finsler|escape proxy|lambda_FW=exp(-Wmin/epsilon); P_T=1-exp(-T lambda)|historical_report|Asymptotic exponential rate/prefactors and Poisson assumptions separate.
thermal|energy deformation|H_i=E_i+cE_i^a|definition|Energy domain for fractional powers and units required.
thermal|partition and purity|Z(beta)=sum_i exp(-beta H_i); F(beta)=log Z(2beta)-2log Z(beta)|derived|Finite Gibbs spectrum.
thermal|purity identity|exp(F)=Tr(rho_beta^2)|derived|Normalized Gibbs density matrix.
thermal|variance objective|V=Var_{t uniform}[F(exp(t))]|definition|Grid/range/clipping specified; different historical objectives not conflated.
thermal|finite-size intercept|spread(N)=A+B/N|proposal|Model fit, not automatically an asymptotic theorem.
thermal|weak exponent identification|c=0 implies H_i independent of a|derived|Near-zero c undermines preferred-exponent inference.
closure|finite closure|cl(A)=intersection{B superset A:B stable}|definition|Finite closure-system implementation proposal.
closure|closure debt|D(A)=mu(cl(A))-mu(A)|definition|Monotone nonnegative measure mu.
closure|admitted state|adm=c_{R_sound(w)}(X) intersect(S intersect w)|historical_report|Original finite atom/rule semantics required.
closure|obstruction partition|Omega=Omega_miss disjoint-union Omega_ung disjoint-union Omega_rule|historical_report|Missing support, ungrounded claims, rule gaps.
closure|closure-cost invariant|I_tau=(K_tau*,Lambda_tau,B_tau)|proposal|Minimal admitted closure cost, cheaper-route witnesses, fake-work spectrum; invariance tests needed.
closure|comparison cochains|gamma_ij=C_i-C_j; eta_i(f)=Psi(f)C_i-C_i Phi(f)|proposal|Linear/additive setting required for subtraction/cohomology.
closure|total differential|D=delta_Cech+(-1)^p d_I; D^2=0|conditional|Compatible double-complex structure, not arbitrary nonlinear constraint sheaves.
closure|cohomological trichotomy|DDelta!=0 incoherent; Delta=Dh removable; closed nonexact obstruction|derived|For an actual declared cochain complex.
closure|null-labor efficiency|eta(E)=1-K(residue)/K(expansion)|definition|Cost model and correctness preservation must be explicit.
closure|representation profile|P(q)=(Q_exact,Q_bounded,E,D,C)|proposal|Preserved questions, bounds, domain, and cost.
closure|question-dependent height|h_q(x)=h(q(x))|proposal|Organizes search, does not replace a global completeness bound.
closure|adaptive local sieve|R_m={e mod m:retained constraints hold}; next test by eliminated_population/cost|exact_checked|Implemented for F(n)=m^d in sieve.py; exclusions independent of test order; counts replayed against integer roots.
closure|repair pipeline|question->candidate->closure test->exact model / bounded model / repair witness|proposal|Master architecture; not one universal theorem.
transport|integer infeasibility certificate|y in Q^m, yB in Z^n, yb not in Z => Bx=b has no integer solution|exact_checked|y=U_i/d_i from a failing Smith coordinate; yB=0, yb!=0 when the system already fails over Q.
transport|saturation index|[(Q-span(G) intersect Z^n):Z-span(G)]=d_1 d_2...d_r|exact_checked|Rows of G independent or not; witness row of V^{-1} at the first d_i>1.
transport|integer kernel|ker_Z B=Z-span(V e_{r+1},...,V e_n)|exact_checked|UBV=D with rank r; the basis is saturated.
series|Hankel realization|x_{pa}=x_p M^{-1}H_a; f(p)=x_p M^{-1}h; alpha=x_empty|exact_checked|M invertible Hankel block on chosen prefixes/suffixes; agreement beyond the block is a held-out check with a witness word.
series|coarsest exact lumping|sum_{i in B}A_c[i][j] constant over j in C for all blocks B,C and all costs c; H constant on blocks|exact_checked|Partition refinement from output labels; every valid lumping refines the result.
transport|Hermite normal form|H=UB; echelon, pivots positive, entries above pivots in [0,pivot)|exact_checked|U unimodular; equal row lattices iff equal nonzero Hermite rows.
series|multi-output Hankel realization|H_{u,(v,j)}=f_j(uv); f(w)=alpha A_w Beta with Beta n-by-k|exact_checked|Stacked block; shared state can exceed each single-output rank.
invariants|parametric rank locus|{t:rank A(t)<r}=Z(gcd of r-minors) subset Z(M_0)|exact_checked|One variable over Q; elimination over Q[t]/(squarefree M_0) with zero-divisor splitting.
invariants|C3 family exceptional parameters|degree5 correction locus lambda^2-1600/49; degree3 lambda(lambda^2-400); degree10 lambda|exact_checked|Degrees3..12 over Q; degree4 lambda^2+50 and degree12 lambda^2+5 have no rational points.
arithmetic|local power exclusion|F(n) mod q not a d-th power residue mod q => F(n) is not a d-th power|derived|Exact for every modulus q>=2; the sieve only orders these tests.
invariants|comprehensive rank cells|parameter space = disjoint union of V(S_i) minus V(prod N_i), rank constant on each|exact_checked|Several parameters over the algebraic closure; S_i saturated by N_i; branch on pivot zero/nonzero.
invariants|Rabinowitsch saturation|I:q^infinity = (I+<1-zq>) intersect Q[t]|derived|Elimination order on z; cell nonempty iff saturated ideal is not 1.
invariants|two-parameter partner surface|f=x^6+y^6+a x^3y^3+b(x^4y^2+x^2y^4); rational exceptional points (+/-16,-9),(0,3),(0,15),(0,-5),(0,0),(+/-20,0),(+/-40/7,0)|exact_checked|Degrees3..12 of the correction gates; degree3 has a drop curve, degree8 has drop curves including b=0.
invariants|fourfold-root exceptional sextic|x^6+y^6+16x^3y^3-9(x^4y^2+x^2y^4)=(x-y)^4(x^2+4xy+y^2)|exact_checked|Correction rank drops at this point in degrees5,6,7,9,10,11.
invariants|active strata|dim A_N=rank[L_N;P_N]-rank L_N constant on refined cells; commuting=dim ker L_N-dim A_N|exact_checked|Two-parameter sextic surface, degrees3..12; partners replayed at rational samples only.
invariants|surface discriminant|Res_x(f(x,1),f_x(x,1)) in Q[a,b], total degree8|exact_checked|Bareiss determinant of the Sylvester matrix; vanishes exactly at repeated roots since f is monic in x.
invariants|perfect-cube commuting exceptions|f=(x^2+y^2)^3: ker L_N=span{(x^2+y^2)^(N/2)} with A_N=0 for N=4,6,8,10|exact_checked|Correction-rank exception that adds no active capacity; degree12 kernel3 active2.
invariants|degree8 partner curve|a^2b-4b^3+6a^2-28b^2+20b+300=0; rational points (+/-11,6),(+/-16,-9),(0,-5)|exact_checked|Bounded-height scan, height<=12; not a complete rational point list.
invariants|degree12 partner curve|b^4+24b^3+81a^2-126b^2+405=0; rational points (+/-4,-3),(+/-32/25,-9/5),(+/-16,-9)|exact_checked|(+/-4,-3) has a double root; (+/-32/25,-9/5) is squarefree.
observability|readout identifiability|h^T beta determined by X beta iff h in row(X); else Xn=0, h^T n!=0|exact_checked|Noiseless linear response; witness gives two fits with different readouts.
observability|demand-supported readout|theta_i=sum_k q_k phi(d_k)^T beta_i=h_q^T beta_i|definition|q a declared training-derived demand distribution.
observability|repeat versus new condition|row in row(X) leaves identifiability unchanged|exact_checked|Repeats sharpen precision only; minimal identifying sets by exhaustive search up to a size bound.
observability|Gaussian value of information|VOI(e)=h^T Sigma h-h^T(Sigma^{-1}+e e^T/s^2)^{-1}h|exact_checked|Linear Gaussian model; reduction independent of the unseen outcome; conditional on prior and noise.
decisions|settled decision|Jhat(a*)-eps(a*)>max_{b!=a*}(Jhat(b)+eps(b))|exact_checked|Valid intervals; refinement restricted to overlapping contenders.
decisions|evolution-defect split|e_{t+1}=A e_t+(AV-VG)z_t+(B-VH)u_t|exact_checked|Replayed at every step in rational arithmetic with an infinity-norm bound.
closure|adaptive monomial closure|add supp(psi o F) minus current features until empty; minimal space span{C,CK,CK^2,...}|exact_checked|Stops on degree growth or budget with the residual support.
transport|quadratic square transport|k y^2=an^2+bn+c <=> X^2-4ak Y^2=b^2-4ac, X=2an+b, Y=y; n=(X-b)/(2a)|exact_checked|Integers; X=b mod 2a required; branches a=0, definite, square D, N0=0 handled separately.
pell|Nagell class bound|N0>0: 0<=y<=y1 sqrt(N0/(2(x1+1))); N0<0: 0<y<=y1 sqrt(-N0/(2(x1-1)))|derived|x^2-Dy^2=N0, D>0 nonsquare, (x1,y1) fundamental unit; classical theorem, cited.
pell|compiled quadratic population|hits = {(X-b)/(2a): (X,Y) in seeds*eps^Z, X=b mod 2a}|exact_checked|Complete for the Pell branch; checked against brute force on 158 equations; remote indices replayed exactly.
invariants|Clebsch invariants of the sextic|i=(f,f)_4; A=(f,f)_6; B=(i,i)_4; C=(i,(i,i)_2)_4; D=(y3,y1)_2 with y1=(f,i)_4,y2=(i,y1)_2,y3=(i,y2)_2|definition|Unnormalized transvectants; degrees2,4,6,10; scale by det^(3k) under GL2.
invariants|weighted orbit test|(A:B:C:D) equal in P(1,2,3,5) iff I_i^{w_j}J_j^{w_i}=J_i^{w_j}I_j^{w_i}|derived|Proves GL2(Qbar)-equivalence only for squarefree sextics.
invariants|Cayley-Sylvester count|dim Cov_{d,m}(n)=p(w;d,n)-p(w-1;d,n), w=(nd-m)/2|derived|p counts partitions into at most d parts of size at most n.
invariants|cubic partner theorem|det L_3(f)=(A^2-B/6)/16|exact_checked|Every binary sextic; degree-4 invariants spanned by A^2,B; constants fixed and confirmed on random sextics.
invariants|quartic covariant partner|(f,(f,f)_4)_3=(f,(f,f)_4)_5=0|exact_checked|Every binary sextic; no covariants of degree3 and order4 or0; active iff (f,(f,f)_4)_1!=0.
invariants|surface drop curves as invariant loci|deg3: A^2=B/6; deg12: A^2=25B/96; deg8: AB^2+BC/6-9D/2=0|exact_checked|On the two-parameter family only; whether the deg8/deg12 relations hold in the full moduli is open.
invariants|named exceptional sextics|(0,15)~x^6+y^6; (0,-5)~xy(x^4-y^4)|exact_checked|Equal Clebsch points of squarefree sextics; GL2 over the algebraic closure.
empirical|normalized recovery travel|eta_ij=sum_k w_k v_ijk/(0.5 s_ij,entry)|definition|Velocity projected on the outgoing direction over 0.5s after a detected plant; trapezoid weights; not force or efficiency.
empirical|recovery response model|eta=phi(s,a)^T(beta+u_i)+e, phi=(1,s',a',s'a'), u_i~N(0,T)|proposal|Linear mixed model fitted by EM on training athletes; pooling assumptions reported as pooling reliance.
empirical|context-adjusted target|r_i=(1/n_i) sum_p [y_ip-m(x_ip)]; shrunk by n_i/(n_i+k)|definition|Cross-fitted for training athletes; training-only m and k for validation athletes; observed participants only.
empirical|paired predictive gain|G=1-MSE_movement/MSE_baseline|definition|Same availability indicators, missing-data rule and tuning grid in both models; athlete-grouped temporal folds.
empirical|scouting advantage|G>=0.03 with fixed-prediction 90% lower bound >0 on an untouched class|open|Proposed threshold awaiting owner confirmation; synthetic runs test the pipeline only.
'''

def build():
    equations=[]
    for line in EQUATIONS.strip().splitlines():
        domain,title,rest=line.split('|',2)
        expression,status,assumptions=re.split(r'\|(definition|derived|historical_report|conditional|exact_checked|numerical_checked|proposal|open|rejected)\|',rest,maxsplit=1)
        equations.append({'id':f'PJ-E{len(equations)+1:03d}','domain':domain,'title':title,
                          'equation':expression,'status':status,'assumptions':assumptions,
                          'source':'October 14 2026 session synthesis and recovered archival extracts'})
    statuses={'definition','derived','historical_report','conditional','exact_checked','numerical_checked','proposal','open','rejected'}
    for e in equations:
        if e['status'] not in statuses:raise ValueError(f"bad registry row {e}")
    (ROOT/'data/equations.json').write_text(json.dumps({'schema':'perfectjet/equations/1','equations':equations},indent=2)+'\n')
    lines=['# Equation atlas','','Status describes the evidence available in this repository. Exact checking is not Lean verification.','','| ID | Domain | Title | Equation | Status | Assumptions and limits |','|---|---|---|---|---|---|']
    for e in equations:
        lines.append('| '+' | '.join(str(e[k]).replace('|','\\|').replace('\n',' ') for k in ('id','domain','title','equation','status','assumptions'))+' |')
    (ROOT/'docs/EQUATION_ATLAS.md').write_text('\n'.join(lines)+'\n')
    chapters=sorted((ROOT/'docs/chapters').glob('*.md'))
    monograph=['# PerfectJet — Representations, Arithmetic, and Closure','','Version 0.8.0 · 14 October 2026','','A master synthesis of the two archival passes and both enhancement programs. The repository distinguishes mathematical identities, executable exact checks, numerical evidence, historical reports, and proposals. It imports neither a complete upstream solver nor new Lean proofs.','','## Contents','']
    monograph += [f'- [{p.stem}](chapters/{p.name})' for p in chapters]
    for p in chapters:monograph += ['','---','',p.read_text()]
    monograph += ['','---','','# Complete equation registry','', '\n'.join(lines[2:])]
    (ROOT/'docs/MONOGRAPH.md').write_text('\n'.join(monograph)+'\n')
    print(json.dumps({'equations':len(equations),'chapters':len(chapters)}))

if __name__=='__main__':build()
