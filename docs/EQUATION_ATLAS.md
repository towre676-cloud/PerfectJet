# Equation atlas

Status describes the evidence available in this repository. Exact checking is not Lean verification.

| ID | Domain | Title | Equation | Status | Assumptions and limits |
|---|---|---|---|---|---|
| PJ-E001 | arithmetic | perfect-power equation | S(n)+k=m^d | definition | Integer polynomial S; integer n,k,m; d>=2. |
| PJ-E002 | arithmetic | hit count | A_{F,d}(N)=#{n in N:n<=N, exists m in Z:F(n)=m^d} | definition | Positive inputs; existential m avoids double-counting signed witnesses. |
| PJ-E003 | arithmetic | hit density | H_d^S(k)=limsup_{N->infinity} A_{S+k,d}(N)/N | definition | Density claim depends on the sequence class. |
| PJ-E004 | arithmetic | polynomial identity case | S(x)+k=G(x)^d | derived | G in Z[x] supplies a hit at each positive input. |
| PJ-E005 | arithmetic | historical geometric exponent | e=gcd(d,m_i); A(N)=O(N^(e/d+epsilon)) | historical_report | Multiplicity notation and hypotheses must be restored before using this bound. |
| PJ-E006 | arithmetic | growth taxonomy | bounded; c log N+O(1); c sqrt(N)+O(1); N | historical_report | Retained square-hit classification; not a universal classification of every sequence. |
| PJ-E007 | arithmetic | Mordell curve | y^2=x^3+k | definition | Rational group structure and integral completeness are separate questions. |
| PJ-E008 | arithmetic | generalized Pell | y^2-Dx^2=N_0 | definition | Nonsquare D>0 for standard unit-orbit analysis. |
| PJ-E009 | arithmetic | triangular reduction | (2y+1)^2=8F(n)+1 | derived | Equivalent to y(y+1)/2=F(n) with odd-square reconstruction. |
| PJ-E010 | arithmetic | completed square | (2y+1)^2=4F(n)+1 | derived | Equivalent to y^2+y=F(n). |
| PJ-E011 | arithmetic | quadratic discriminant | Delta(n)=b^2-4a(c-F(n)); y=(-b +/- sqrt(Delta))/(2a) | derived | a nonzero; discriminant square AND numerator divisible by 2a. |
| PJ-E012 | arithmetic | coefficient power chart | 2x^2=3y^3; x=+/-18t^3,y=6t^2 | derived | Integer parametrization; retain signs and t=0. |
| PJ-E013 | arithmetic | cusp power chart | x^2=y^3; x=t^3,y=t^2 | derived | Integer t carries the sign of x. |
| PJ-E014 | pell | quadratic norm | N(x+y sqrt(D))=x^2-Dy^2 | derived | Quadratic extension convention. |
| PJ-E015 | pell | unit orbit | x_j+y_j sqrt(D)=alpha epsilon^j | historical_report | Seed inventory and index domain must be complete. |
| PJ-E016 | pell | unit matrix | [x';y']=[[a,Db],[b,a]][x;y] | derived | epsilon=a+b sqrt(D); multiplication identity. |
| PJ-E017 | pell | sqrt2 hit recurrence | n'=3n+2m; m'=4n+3m; m^2-2n^2=1 | derived | A single orbit step; seeds/domain still matter. |
| PJ-E018 | pell | Pell7 | x^2-2y^2=-7 | derived | Equivalent to (x^2+7)/2=y^2. |
| PJ-E019 | pell | orbit coordinate | X_j=(eta epsilon^j+(Delta/eta)epsilon^(-j))/2 | historical_report | Original seed/norm convention required. |
| PJ-E020 | pell | input asymptotic | n_j=eta epsilon^j/(4A)-B/(2A)+O(epsilon^(-j)) | historical_report | Original quadratic pullback coefficients required. |
| PJ-E021 | pell | filtered orbit population | A_orbit(N)=g log(N)/(pi_period log(epsilon))+O(1) | historical_report | Reachable cycle with period pi_period and g admissible positions. |
| PJ-E022 | pell | filtered infinitude | reachable admissible cycle iff infinitely many admissible orbit hits | historical_report | For retained finite-state orbit encoding, not arbitrary automata. |
| PJ-E023 | pell | unit identity | (1+sqrt(2))^6=99+70sqrt(2) | derived | Exact binomial expansion. |
| PJ-E024 | descent | general Weierstrass | y^2+a1xy+a3y=x^3+a2x^2+a4x+a6 | definition | Nonsingular elliptic model when discriminant nonzero. |
| PJ-E025 | descent | Weierstrass coefficients | b2=a1^2+4a2; b4=2a4+a1a3; b6=a3^2+4a6 | definition | Standard model coefficients. |
| PJ-E026 | descent | square completion | (2y+a1x+a3)^2=4x^3+b2x^2+2b4x+b6 | derived | Direct polynomial identity. |
| PJ-E027 | descent | two-torsion cubic | psi2(x)=4x^3+b2x^2+2b4x+b6 | definition | Leading coefficient 4; use monic normalization for the norm. |
| PJ-E028 | descent | cubic discriminant | disc(psi2)=16Delta_E | derived | Standard discriminant normalization. |
| PJ-E029 | descent | cubic etale norm | N(x-theta)=((2y+a1x+a3)/2)^2 | derived | theta is root of monic psi2/4; norm-square is necessary, not sufficient for Selmer membership. |
| PJ-E030 | descent | squareclasses | L^*/L^(*2) | definition | Product algebra when cubic splits; do not silently assume a field. |
| PJ-E031 | descent | local Kummer condition | loc_v(alpha) in image(delta_v) | definition | Actual complete local images, not sampled signatures. |
| PJ-E032 | descent | Selmer intersection | Sel2={alpha in appropriate global squareclasses:loc_v(alpha) in image(delta_v) for all v} | definition | S-unit/class-group/norm conditions must also be supplied. |
| PJ-E033 | descent | unit-class sequence | O_{L,S}^*/O_{L,S}^{*2}->L(S,2)->Cl(O_{L,S})[2] | historical_report | Recover exact sequence conventions before downstream proof. |
| PJ-E034 | descent | Selmer exact sequence | 0->E(Q)/2E(Q)->Sel2(E/Q)->Sha(E/Q)[2]->0 | derived | Standard 2-Selmer interpretation. |
| PJ-E035 | descent | anonymous model | y^2=x^3+2x^2-12x+16 | historical_report | v1.67 report; not imported as a complete descent implementation. |
| PJ-E036 | descent | anonymous field | u^3+8u^2-192u+1024=0 | historical_report | Field discriminant reported -107; polynomial and field discriminants differ. |
| PJ-E037 | transport | affine pullback | F(n)=(rn+s)^3+k | definition | r nonzero for inverse transport. |
| PJ-E038 | transport | transported list | W={((t-s)/r,y):(t,y) in L_k, r divides t-s} | derived | L_k must be complete to conclude complete pullback. |
| PJ-E039 | transport | list contract | m^2=F(n) iff (n,m) in W | conditional | Requires complete source list and preserved domains. |
| PJ-E040 | transport | Thue23 first | -u^3-3u^2v+6uv^2+4v^3=1 | historical_report | Retained descent leaf; all branches/reconstruction needed. |
| PJ-E041 | transport | Thue23 second | -u^3-6u^2v+69uv^2+46v^3=1 | historical_report | Retained descent leaf. |
| PJ-E042 | transport | field621 | theta^3-6theta-3=0 | historical_report | Associated field representation in archive. |
| PJ-E043 | transport | D72 leaf | H(u,v)=-3u^3+9uv^2-2v^3=+/-1 | historical_report | Residual branch, not a closure claim. |
| PJ-E044 | transport | D72 field | beta^3-27beta-18=0 | historical_report | Coordinates and order matter. |
| PJ-E045 | transport | D72 norm | gamma=-3u-beta v; N(gamma)=9H(u,v)=+/-9 | historical_report | Exact identity attached to the selected field/order. |
| PJ-E046 | transport | D72 units | gamma=zeta alpha_j epsilon1^e1 epsilon2^e2 | historical_report | Need representatives and effective global exponent bounds. |
| PJ-E047 | transport | D72 reconstruction | C=0; 3 divides A; u=-A/3; v=-B | historical_report | Coordinate restrictions are part of completeness. |
| PJ-E048 | transport | scaled rational kernel | K=det(BB^T)I-B^T adj(BB^T)B | derived | Full row rank for nondegenerate projector interpretation. |
| PJ-E049 | transport | kernel identities | BK=0; Bx=0 implies Kx=det(BB^T)x | derived | Rational-span statement does not prove integral saturation. |
| PJ-E050 | transport | Smith form | UBV=D | exact_checked | Unimodular U,V; d_1\|d_2\|...; replayed in lattice.py against gcd-of-minors divisors. |
| PJ-E051 | transport | integral solvability | d_i divides (Ub)_i; remaining coordinates (Ub)_i=0 | exact_checked | For Smith form of Bx=b; failure returns a certificate row. |
| PJ-E052 | counting | resource polynomial | P(z)=product_j(1+product_k z_k^{c_jk}) | derived | Nonnegative integral costs; extra compatibility requires extra factors/state. |
| PJ-E053 | counting | capacity population | #F=sum_{a<=b}[z^a]P(z) | derived | Componentwise capacity bound. |
| PJ-E054 | counting | profit polynomial | P(z,t)=product_j(1+t^{p_j}product_k z_k^{c_jk}) | proposal | Laurent t exponents if profits negative. |
| PJ-E055 | counting | completion recurrence | C(q)=C(q0)+C(q1) | exact_checked | Disjoint binary prefixes; populations.py and exhaustive comparisons. |
| PJ-E056 | counting | terminal count | C(q)=1 if complete and feasible else 0 | exact_checked | Original objects counted once. |
| PJ-E057 | counting | ranking | rank(x)=sum_{i:x_i=1} C(x_<i 0) | exact_checked | Lexicographic original project order. |
| PJ-E058 | counting | unranking | r<C(q0):choose0; else choose1 and r<-r-C(q0) | exact_checked | 0<=r<C(q). |
| PJ-E059 | counting | uniform sampling | Pr(0\|q)=C(q0)/C(q) | derived | Exact uniformity over original objects, not quotient representatives. |
| PJ-E060 | counting | factor population | Z=sum_x product_j f_j(x_scope_j) | definition | Finite domains and specified weight algebra. |
| PJ-E061 | counting | variable elimination | g(x_rest)=sum_{x_i}product_{j containing i}f_j | derived | No duplicated auxiliary witnesses. |
| PJ-E062 | counting | auxiliary uniqueness | for every original legal x, #{y:encoding(x,y)}=1 | definition | Needed to preserve population under functional encodings. |
| PJ-E063 | counting | Petersen historical total | 702508860122761; optimum=16537; tie_count=1 | historical_report | Upstream retained result; original 50-project data not included here. |
| PJ-E064 | counting | population aggregation | Z_{A disjoint-union B}=Z_A+Z_B; Z_{A times B}=Z_A Z_B | derived | Disjointness / independence essential. |
| PJ-E065 | counting | exponent-pattern polynomial | product_i(1+q+...+q^{a_i}) | definition | Prime-exponent populations. |
| PJ-E066 | counting | power-exponent criterion | d divides gcd(a_1,...,a_s) | derived | Positive integer prime factorization; handle 1 separately. |
| PJ-E067 | series | weighted transfer series | G(z)=H(I-sum_c z^c A_c)^(-1)s | derived | Positive integral costs; finite-dimensional formal series. |
| PJ-E068 | series | resolvent expansion | (I-M(z))^(-1)=sum_{ell>=0}M(z)^ell | derived | M has zero constant term, or other convergence hypotheses. |
| PJ-E069 | series | Fibonacci series | 1/(1-z-z^2) | definition | Initialization determines sequence offset. |
| PJ-E070 | series | zero-series initialization | z/(1-z)=0+z+z^2+... | historical_report | Zero initial sample can change minimal realization size. |
| PJ-E071 | series | linear response | G(z)=C(I-zA)^(-1)B; coefficients=CA^kB | derived | Linear input/output convention. |
| PJ-E072 | series | Hankel matrix | H_{u,v}=f(uv) | exact_checked | Word-indexed predictive state; finite rank over a field; exact on the supplied block only. |
| PJ-E073 | series | linear word realization | f(w)=alpha^T A_{a1}...A_{aell} beta | derived | Minimal field realization dimension equals finite Hankel rank; positivity is separate. |
| PJ-E074 | semantics | semantic fibre | pi:I->S; I_s=pi^(-1)(s) intersect L | definition | Legal implementations of a meaning. |
| PJ-E075 | semantics | cost realization | i*=argmin_{i in I_s}cost(i) | proposal | Minimum must exist or infimum used. |
| PJ-E076 | semantics | future equivalence | x~y iff all finite permitted words have equal behavior | exact_checked | Partial definedness included; finite machine replay. |
| PJ-E077 | semantics | quotient dynamics | qF_a=Fbar_a q | exact_checked | Observation and definedness preserved. |
| PJ-E078 | semantics | quotient observation | O=Obar q | exact_checked | Chosen output family only. |
| PJ-E079 | semantics | completeness | q(x)=q(y) iff x~y | exact_checked | Finite Python quotient, not new Lean theorem. |
| PJ-E080 | semantics | distinguishing word | exists w:behavior(x,w)!=behavior(y,w) | exact_checked | Shortest witness via pair BFS. |
| PJ-E081 | semantics | question refinement | Q subset Q' implies equivalence(Q') subset equivalence(Q) | derived | More questions can only refine the state partition. |
| PJ-E082 | semantics | joint representation | q=(q1,q2) | proposal | Then remove redundant distinctions relative to joint questions. |
| PJ-E083 | observability | row closure | O=span{rows(CA^k):k>=0} | exact_checked | Finite rational matrices; exact observable-space compiler. |
| PJ-E084 | observability | hidden space | N=intersection_{k>=0}ker(CA^k) | derived | Linear all-future output equivalence. |
| PJ-E085 | observability | target recovery | ker(O) subset ker(G) iff G=L O | exact_checked | Finite dimensions; hidden-vector failure witness. |
| PJ-E086 | observability | hidden target amplitude | max_{delta in ker(H) intersect ker(M),norm(delta)<=1}\|g^T delta\| | derived | Norm must be declared; Euclidean formula uses orthonormal hidden basis. |
| PJ-E087 | observability | quadratic fibre constancy | N^T(g+Qx0)=0 and N^T QN=0 | derived | T=g^Tx+1/2 x^TQx, symmetric Q, full affine fibre x0+image(N). |
| PJ-E088 | observability | sensor repair | ker(Hnew N) subset ker(GN) | derived | Repairs target-affecting hidden directions. |
| PJ-E089 | observability | information matrix | J=H^T R^(-1)H | definition | Positive noise covariance; prior added separately. |
| PJ-E090 | observability | sensor sensitivity | d(g^T P g)/dw=-(h^T P g)^2 | derived | P=(J0+w hh^T)^(-1), nonsingular. |
| PJ-E091 | observability | stable recovery | G^*G <= lambda O^*O | historical_report | Bounded-operator assumptions; exact recovery and stable recovery differ. |
| PJ-E092 | observability | delay coordinates | Psi_L=[O;O F;...;O F^(L-1)] | proposal | Linear observability rows become [C;CA;...]; nonlinear sufficiency needs hypotheses. |
| PJ-E093 | features | finite feature closure | p_i composed F in span_Q{p_j} | exact_checked | Exact coefficient replay, not fitted regression. |
| PJ-E094 | features | feature evolution | p(F(x))=G p(x) | exact_checked | Output must belong to retained feature span. |
| PJ-E095 | features | all-time feature evolution | p(F^t(x))=G^t p(x) | derived | Induction from exact closure. |
| PJ-E096 | features | closure defect | psi(F(x))=G psi(x)+r(x) | definition | Explicit residual rather than silent truncation. |
| PJ-E097 | features | defect state augmentation | [psi';chi']=[[G,B],[C,D]][psi;chi] | proposal | r=Bchi and chi'=Cpsi+Dchi; closure may never terminate. |
| PJ-E098 | features | parameter sensitivity | S_{t+1}=D_xF S_t+D_theta F | derived | Differentiable parameterized dynamics. |
| PJ-E099 | features | linear sensitivity | S'=A S+A_theta x+B_theta u | derived | Discrete-time prime notation means next state; input fixed relative to parameter. |
| PJ-E100 | dynamics | reconstruction error | e=x-Vz | definition | State error versus output error distinguished. |
| PJ-E101 | dynamics | evolution defects | R=AV-VG; S=B-VH | exact_checked | Compatible linear model/reconstruction matrices. |
| PJ-E102 | dynamics | error recurrence | e_next=Ae+Rz+Su | derived | Direct substitution into full and reduced dynamics. |
| PJ-E103 | dynamics | error convolution | e_t=A^t e0+sum_{j<t}A^(t-1-j)(Rz_j+Su_j) | derived | Exact finite-time identity. |
| PJ-E104 | dynamics | continuous Lyapunov | A^T P+PA<=-2alpha P; P>0 | derived | Continuous time; alpha positive for decay. |
| PJ-E105 | dynamics | discrete Lyapunov | A^T PA<=gamma^2 P; 0<=gamma<1 | derived | Discrete time; fixed metric. |
| PJ-E106 | dynamics | contractive error | norm(e_t)<=gamma^t norm(e0)+sum gamma^(t-1-j)delta_j | exact_checked | Defects nonnegative bounds in the same contracting norm. |
| PJ-E107 | dynamics | uniform defect bound | norm(e_t)<=gamma^t norm(e0)+delta(1-gamma^t)/(1-gamma) | derived | Supremum defect delta and gamma<1. |
| PJ-E108 | dynamics | composed error | epsilon_total<=epsilon1+norm(V1)epsilon2 | derived | Compatible reconstruction stages. |
| PJ-E109 | dynamics | nonlinear composed error | epsilon_total<=epsilon1+L1 epsilon2 | derived | First reconstruction Lipschitz with constant L1. |
| PJ-E110 | dynamics | decision certificate | Jhat(a*)-epsilon_a*>max_{b!=a*}(Jhat(b)+epsilon_b) | exact_checked | Deterministic interval bounds; empirical uncertainty separate. |
| PJ-E111 | energy | mass energy | E=1/2 u^T M u | definition | Constant symmetric positive-definite M. |
| PJ-E112 | energy | symmetric energy operator | S_M=(A^T M+MA)/2 | exact_checked | u'=Au+f. |
| PJ-E113 | energy | energy derivative | E'=u^T S_M u+u^T M f | exact_checked | Direct identity; boundaries/sources in A or f. |
| PJ-E114 | energy | corrected decay dial | lambda=-2u^T S_Mu/(u^TMu) | exact_checked | Nonzero state; sign chosen for predicted decay. |
| PJ-E115 | energy | corrected source term | zeta=2u^T Mf/(u^TMu) | exact_checked | Positive source reduces net decay when lambda>0. |
| PJ-E116 | energy | corrected residue | d log(E)/dt=-lambda+zeta; rho=1-zeta/lambda | exact_checked | rho undefined at lambda=0; historical plus-sign formula rejected. |
| PJ-E117 | energy | CRO measured rate | alpha_hat=-(log E_k-log E_{k-1})/Delta_t | definition | Positive energies; window and integration scheme retained. |
| PJ-E118 | energy | CRO residual | R1=\|alpha_hat-alpha\| | definition | Diagnostic, not proof of physical universality. |
| PJ-E119 | energy | rank-one crystalline matrix | S(t)=I+t11^T; det(S)=1+nt | derived | n-dimensional all-ones vector. |
| PJ-E120 | energy | invariant-space leakage | (I-P)AP | definition | Zero iff range(P) invariant when P is a projection. |
| PJ-E121 | imp | SVD projector | M=U Sigma V^T; P=QQ^T | historical_report | Unit singular vectors do not establish invariant fixed modes. |
| PJ-E122 | imp | rejected SVD limit | all selected singular values=1 implies M^k->P | rejected | Orthogonal rotation counterexample. |
| PJ-E123 | imp | sufficient fixed-mode split | M=P+T; P^2=P; PT=TP=0; rho(T)<1 | derived | Then M^k=P+T^k and M^k x->Px. |
| PJ-E124 | imp | general invariant reduction | MQ=QG | derived | Retained dynamics may evolve instead of remaining fixed. |
| PJ-E125 | imp | exact retained evolution | M^k Q=QG^k | derived | Induction from intertwining. |
| PJ-E126 | psg | potential | L=-log cos(x); U=x^2+L^2; K_alpha=U^(-alpha/2) | definition | 0<x<pi/2; global contraction is not assumed. |
| PJ-E127 | psg | support functions | T=tan(x); H=x+LT; A=xH/(2U) | definition | Archive A<1/2 claim contradicts retained root A*=0.674... . |
| PJ-E128 | psg | corrected derivative | K_alpha'=-alpha H K_alpha/U | derived | U'=2H; factor-of-two repaired. |
| PJ-E129 | psg | flip parameter | alpha=1/(2A) | numerical_checked | At a fixed point with multiplier -1. |
| PJ-E130 | psg | scalar balance | F(L)=log U(L)+4A(L)log x(L)=0 | numerical_checked | x=acos(exp(-L)); bracket replay only, not uniqueness/transcendence proof. |
| PJ-E131 | psg | coordinate derivatives | x'=1/sqrt(exp(2L)-1); L_x'=tan x; T_x'=1+T^2 | derived | Positive L and admissible angle. |
| PJ-E132 | psg | root receipt | L*=0.531916689243299; x*=0.942857679982338; alpha*=0.741804515087895 | numerical_checked | Floating root reproduction, historical higher precision not re-certified. |
| PJ-E133 | psg | coefficient curve | a(v)=x(x+(v/2)T)/(2(x^2+v^2/4)); x=acos(exp(-v/2)); T=sqrt(exp(v)-1) | historical_report | Correct v=2L convention; archive typography inconsistent in places. |
| PJ-E134 | psg | exponential extraction | E F1+F0=0; E=exp(v)-1=-F0/F1 | historical_report | p=a'; F1 nonzero; original numerator and certificates needed. |
| PJ-E135 | psg | F0 | a(2a-1)(v+4-8a)^2 | historical_report | Factor structure preserved. |
| PJ-E136 | psg | F1 | (av-2a-2pv+1)(2av+4a-4pv-v-2) | historical_report | Factor structure preserved. |
| PJ-E137 | psg | cleared jet field | Xtilde=D partial_v+Dp partial_a+N partial_p | historical_report | D=2av^2(2a-1)(v+4-8a)^2; full N absent from read document. |
| PJ-E138 | psg | Darboux equation | Xtilde(H)=KH | definition | Listed identities do not by themselves establish unrestricted classification. |
| PJ-E139 | psg | PSG source elimination | P(x,L,T)=0; T^2=Y^2-1; T=-A/B | historical_report | 26-term source/100-term elimination reported; B=0 and integer-image branches must remain. |
| PJ-E140 | psg | normalized amplitude jet | A/A*=1+.3282804759delta+.0800766090delta^2+.0108819139delta^3+... | historical_report | Root-centered finite jet; not an origin-germ coefficient table. |
| PJ-E141 | psg | normalized balance jet | F/(L*F')=delta-.3793897467delta^2+.3008496421delta^3-.2807207864delta^4+... | historical_report | Declared normalization required. |
| PJ-E142 | psg | logarithmic derivative | I=F''/F' | definition | Derivative ratio; archive sometimes conflates Taylor factorial conventions. |
| PJ-E143 | jets | Schroeder equation | Psi(f(x))=-Psi(x) | conditional | Locally invertible exact solution requires f^2=id. |
| PJ-E144 | jets | reflection criterion | Psi=(x-f(x))/2; f^2=id implies Psi composed f=-Psi | derived | Centered analytic f with f'(0)=-1 gives Psi'(0)=1. |
| PJ-E145 | jets | flip obstruction | f=-x+ax^2+bx^3+...; f^2-x=-2(b+a^2)x^3+... | exact_checked | Centered coordinates; coefficient convention without factorials. |
| PJ-E146 | jets | two-cycle leading sign | f_nu=-(1+nu)x+kappa x^3+...; x^2~nu/kappa | derived | Real small cycle requires positive ratio; parameter-dependent fixed point recentered. |
| PJ-E147 | jets | Riccati coefficient law | (n+1)i_{n+1}=a 1_{n=0}+b i_n+c sum_{j=0}^n i_j i_{n-j} | exact_checked | Specific ODE I'=a+bI+cI^2; not a transcendence test. |
| PJ-E148 | jets | Riccati rejection residual | r_n=(n+1)i_{n+1}-a1_{n=0}-b i_n-c sum i_j i_{n-j} | exact_checked | Nonzero exact residual rejects this fixed model. |
| PJ-E149 | jets | Puiseux series | xi=a1 sqrt(epsilon)+a2 epsilon+a3 epsilon^(3/2)+... | proposal | Check second-iterate signs before claiming a real branch. |
| PJ-E150 | jets | seventh-order freedom | b7 leaves orders0..6 unchanged; order7 coefficient=1/128 | historical_report | Specific archived wall normalization; not recomputed here. |
| PJ-E151 | recurrences | Padovan | P_n=P_{n-2}+P_{n-3}; characteristic=x^3-x-1 | definition | Initial conditions fixed separately. |
| PJ-E152 | recurrences | Padovan modes | P_n=A psi^n+B q^n+conjugate(B q^n) | derived | Distinct characteristic roots and real initial data. |
| PJ-E153 | recurrences | Fibonacci kernel | F_{n+1}=sum_{k=0}^{floor(n/2)} binomial(n-k,k) | derived | Standard finite combinatorial identity. |
| PJ-E154 | recurrences | Tribonacci | T_n=T_{n-1}+T_{n-2}+T_{n-3}; x^3-x^2-x-1=0 | definition | Separate family from Catmull-Clark operator spectra. |
| PJ-E155 | recurrences | Escher-Pisot proposal | F_{n+1}(z)=lambda F_n(exp(2pi i alpha)conj(z))+sum_k(-1)^k theta^(-2k-1)binomial(n-k,k)q^(k(k+1)/2)+Phi(F_n(z)) | proposal | Finite k range for given n; no global contraction from lambda>1. |
| PJ-E156 | recurrences | mode stability | abs(lambda exp(-im alpha)+a)<1 | conditional | Specified linearized mode only. |
| PJ-E157 | topology | MMHW wavelet | psi_{alpha,beta}(x)=(1-alpha x^2)exp(-x^2/2)(1+beta sin(pi x^2)exp(-abs(x)^3)) | proposal | Wavelet admissibility and topological accuracy need separate analysis. |
| PJ-E158 | topology | subdivision block | M=[[-7/48,3(1+i sqrt3)/32],[5(1-i sqrt3)/16,-9/8]] | historical_report | Particular local block, not established full refinement operator. |
| PJ-E159 | topology | block characteristic | chi=x^2+61x/48+3/64 | derived | Trace/determinant checked in session; one root magnitude>1 prevents naive contraction claim. |
| PJ-E160 | topology | finite quadratic phases | b(x,y)=q(x+y)-q(x)-q(y) | definition | Finite nondegenerate quadratic module conventions. |
| PJ-E161 | topology | finite S,T | S_xy=\|A\|^(-1/2)exp(-2pi i b(x,y)); T_xx=exp(2pi i q(x)) | definition | Choice of sign fixes relations. |
| PJ-E162 | topology | modular relations | S^2=C; (ST)^3=xi C; xi=\|A\|^(-1/2)sum_x exp(2pi i q(x)) | conditional | Correct quadratic-module hypotheses and convention. |
| PJ-E163 | conductor | rotation algebra | UV=exp(2pi i theta)VU | definition | Generator conventions explicit. |
| PJ-E164 | conductor | clock shift convention | Ue_j=e_{j+1}; Ve_j=omega^j e_j; VU=omega UV | derived | Corrects sign/order mismatch with alternate UV convention. |
| PJ-E165 | conductor | irrational trace range | Z+theta Z | historical_report | K-theory/trace conventions for A_theta. |
| PJ-E166 | conductor | Weil commutant | c=dim{X:XS=SX,XT=TX} | definition | Operator pair must be specified, particularly dyadic case. |
| PJ-E167 | conductor | odd prime law | c(p^a)=a+1 | historical_report | Specific Weil core; not imported formal theorem. |
| PJ-E168 | conductor | multiplicativity | c(mn)=c(m)c(n), gcd(m,n)=1 | conditional | Requires product representation compatibility. |
| PJ-E169 | conductor | model-specific dyadic | c(2^a)=2a-1 | historical_report | Different archive cyclic dyadic pair gives 1,3,8,19,...; do not conflate models. |
| PJ-E170 | conductor | DAT hardware gates | C_cond<C_Pauli and p_eff<p_th | proposal | Illustrative rates are not measured native hardware. |
| PJ-E171 | conductor | continued-fraction tower | chi(theta)=limsup log(q_{n+1})/log(q_n) | definition | Growth diagnostic, not an inverse system without supplied bonding maps. |
| PJ-E172 | conductor | bounded type tower | a_n<=A implies q_{n+1}<=(A+1)q_n and chi=1 | derived | Irrational continued fractions. |
| PJ-E173 | conductor | finite phase approximation | abs(j theta-j p_n/q_n)<=1/q_{n+1}, j<=q_n | derived | From convergent error bound; trace claims require output continuity. |
| PJ-E174 | conductor | su2 quantum dimension | D^2=L/(2sin^2(pi/L)) | derived | L=k+2>=3; direct sine-sum identity. |
| PJ-E175 | conductor | Weyl volume | D^2=\|P/Q\| L^r/product_{alpha>0}(2sin(pi<rho,alpha^vee>/L))^2 | historical_report | Archived simply-laced scope; nonsimply-laced normalization separate. |
| PJ-E176 | conductor | volume asymptotic | D^2~C_g L^(r+2\|Phi+\|)=C_g L^dim(g) | derived | For fixed valid root-data formula. |
| PJ-E177 | conductor | fusion wall corrected variable | U_{L-1}(X/2)=0; X=2cos(theta) | derived | Use monic integer polynomial, rather than silently treating nonmonic U_m(x) as a monic Z[x] quotient. |
| PJ-E178 | collision | valuation kernel | kappa(m,n)=sum_p v_p(m)v_p(n) | exact_checked | Positive integers; arithmetic dot product. |
| PJ-E179 | collision | coprime orthogonality | kappa(m,n)=0 iff gcd(m,n)=1 | exact_checked | Nonnegative valuations. |
| PJ-E180 | collision | multiplicative bilinearity | kappa(mn,r)=kappa(m,r)+kappa(n,r) | exact_checked | Valuation additivity. |
| PJ-E181 | collision | divisor collision defect | F_{m,n}(q)=R_m(q)R_n(q)-R_mn(q) | derived | R_n product over prime-exponent intervals. |
| PJ-E182 | collision | collision zeta | Z_t(s)=sum_{m,n} exp(t kappa(m,n))/(mn)^s | definition | t real<=0 and Re(s)>1 ensures absolute convergence. |
| PJ-E183 | collision | Euler factor | product_p sum_{a,b>=0} exp(tab)p^(-s(a+b)) | derived | Absolute convergence or appropriate formal interpretation. |
| PJ-E184 | collision | positive-temperature divergence | exp(tN^2)p^(-2sN) does not tend to zero for real t>0 | derived | Single-prime diagonal suffices. |
| PJ-E185 | collision | coprime endpoint | Z_{-infinity}(s)=zeta(s)^2/zeta(2s) | derived | Re(s)>1; monotone/dominated limit for real parameters. |
| PJ-E186 | collision | historical thermal factor | Z_t(s)=zeta(s)^2 H_t(s) | historical_report | t<0; analytic continuation/remainders require original hypotheses. |
| PJ-E187 | collision | historical count asymptotic | A_t(X)=H_t(1)Xlog X+((2gamma-1)H_t(1)+H_t'(1))X+... | historical_report | Original Tauberian/analytic bounds not imported. |
| PJ-E188 | collision | finite numerator | N_L(x)=sum_{r,s=0}^{L-1}zeta_L^(rs)x^(r+s) | exact_checked | Exact ring implementation and series convolution comparisons. |
| PJ-E189 | collision | rational closure | L_L(x)=N_L(x)/(1-x^L)^2 | exact_checked | Formal series or abs(x)<1. |
| PJ-E190 | collision | direct coefficient | a_n=sum_{j=0}^n zeta_L^(j(n-j)) | exact_checked | Retains full and partial residue blocks. |
| PJ-E191 | collision | affine-periodic coefficient | a_{dL+r}=dG_r+B_r | exact_checked | G complete sum, B partial sum, 0<=r<L. |
| PJ-E192 | collision | stride recurrence | a_{n+2L}-2a_{n+L}+a_n=0 | exact_checked | All n>=0; finite exact state. |
| PJ-E193 | collision | numerator checkpoints | N_L(0)=1; N_L(1)=L; leading coefficient=zeta_L | exact_checked | For L>=2; L=1 special but implemented. |
| PJ-E194 | collision | rejected penalty PSD | exp(-beta kappa(m,n)) is always PSD | rejected | On {1,2}, determinant exp(-beta)-1<0 for beta>0. |
| PJ-E195 | collision | positive valuation kernel | K_beta(m,n)=exp(-beta norm(v(m)-v(n))^2) | derived | beta>=0, finite valuation supports; Gaussian PSD. |
| PJ-E196 | collision | Gaussian factorization | K=e^(-beta norm(v(m))^2)e^(-beta norm(v(n))^2)e^(2beta kappa(m,n)) | derived | Similarity role differs from collision suppression. |
| PJ-E197 | collision | prime-zeta decomposition | log Z_Gamma,L=r log zeta(Ls)+sum_m a_m P(ms) | historical_report | Original numerator/branch conventions; P prime zeta. |
| PJ-E198 | collision | branch-stripped product | FPbr= zeta(L)^r product_p[N(1/p)exp(-a1/p)] | historical_report | Finite factors, zeros, and branch conventions explicit. |
| PJ-E199 | collision | finite-part tail | abs(log tail)<=C/P; abs(tail-1)<=exp(C/P)-1 | derived | Requires proved local remainder bound abs(r_p)<=C/p^2 beyond cutoff. |
| PJ-E200 | collision | failed dimension weld | FPbr != D^2 under retained projection/normalization sweep | historical_report | Bounded tested family, not exclusion of every possible relationship. |
| PJ-E201 | core | core cubic | alpha^3-alpha^2+1=0 | exact_checked | Transported from cubic quotient ring. |
| PJ-E202 | core | critical cubic | u^3-4u^2+5u-1=0 | exact_checked | Canonical ring modulus in rings.py. |
| PJ-E203 | core | plastic transport | u=1+alpha; beta=-1/alpha; beta^3-beta-1=0 | exact_checked | Explicit inverse maps; not discriminant-only identification. |
| PJ-E204 | core | critical factorization | (z-1)^2(z^3-4z^2+5z-1) | historical_report | Critical ideal elimination source retained; not recomputed full ideal. |
| PJ-E205 | core | abelian shadow cubic | z^3-2z^2-z+1; disc=49 | historical_report | Conductor7 cyclic shadow versus nonabelian core. |
| PJ-E206 | core | Hessian element | h=(-2u^2+3u-2)/(-u^2+u); h^3+4h^2-23h+23=0 | exact_checked | Denominators invertible; field coordinates retained. |
| PJ-E207 | core | vertex element | v=(6u-8)/(3u^2-8u+5); 23v^3+4v+200=0 | exact_checked | Archived quantity, no new physical loop prediction. |
| PJ-E208 | core | corner family | P_{a,b}(z)=(1-z)^a-z^b | definition | Bounded divisibility census not global isolation. |
| PJ-E209 | core | regulator volume report | 3D(alpha)=2.8281220883307831628... | historical_report | Selected complex embedding/orientation; volume identification requires geometric input. |
| PJ-E210 | core | Bloch conjugation | D(conjugate(z))=-D(z) | derived | All-conjugate unweighted sum cancels. |
| PJ-E211 | core | oriented regulator | R(xi)=(D(sigma1 xi),...,D(sigmar xi)); scalar=c^T R | proposal | One embedding per conjugate pair; c from geometry. |
| PJ-E212 | core | regulator magnitude | norm(R(xi))^2 | proposal | Conjugation-choice independent magnitude, not automatically volume. |
| PJ-E213 | deformation | cotangent fibre | L_{B/Q} tensor k(p)=[I/I^2 tensor k(p) -> Omega tensor k(p)] | historical_report | Local complete-intersection convention; differential df_p. |
| PJ-E214 | deformation | point lift | df_p(v)+g(p)=0 | derived | Square-zero deformation f+epsilon g and marked point p+epsilon v. |
| PJ-E215 | deformation | cusp | f=y^2-x^3; Tjurina=Q[x,y]/(f,f_x,f_y)=span{1,x} | historical_report | Characteristic0 or suitable good characteristic. |
| PJ-E216 | deformation | E37 model | Y^2=X^3-16X+16; Delta=151552; j=110592/37 | derived | Standard short-Weierstrass invariants. |
| PJ-E217 | deformation | E37 tangent | dj=(559872/1369,373248/1369); gauge=(64,-96); moduli=(96,64) | historical_report | dj(gauge)=0; dj(moduli)=77635584/1369. |
| PJ-E218 | deformation | discriminant formula | Delta=-16(4a^3+27b^2); j=1728(4a^3)/(4a^3+27b^2) | derived | Nonsingular short model; coordinate scaling can alter Delta while preserving j. |
| PJ-E219 | deformation | Zsqrt-5 divisors | (2)=p2^2; (3)=p3+ p3-; (1+/-sqrt(-5))=p2 p3+/- | historical_report | Archive weight-one Picard/K0 comparison; not arbitrary higher weights. |
| PJ-E220 | deformation | stationary sensitivity | dx*/d epsilon=-(Hessian V0)^(-1)gradient W | derived | Nonsingular Hessian; symmetry zero modes require quotient/gauge fixing. |
| PJ-E221 | deformation | relation response | dR/d epsilon=-gradient R^T(Hessian V0)^(-1)gradient W | derived | Allowed perturbation space must be specified. |
| PJ-E222 | codes | Artin-Schreier-Witt | 0->Z/p^n->W_n --F-1-->W_n->0 | historical_report | Characteristic p etale sheaf setting; not mixed-characteristic elliptic descent. |
| PJ-E223 | codes | Hermitian curve | y^p+y=x^(p+1) | definition | Over F_{p^2}; code divisor/evaluation set needed. |
| PJ-E224 | codes | Hermitian code reports | [8,4,4]_4; [27,6,19]_9; [125,3,119]_25 | historical_report | Retained numerical/exact reports, implementation not imported. |
| PJ-E225 | codes | p5 weight enumerator | 12000z^119+600z^120+3000z^124+24z^125 | historical_report | Nonzero words; add constant1 for full enumerator. |
| PJ-E226 | codes | alternate curve | X_q:y^q+y=x^2; n_q=2q^2-q | historical_report | Point-count convention and q conditions must be supplied. |
| PJ-E227 | prefix | normal binary64 | x=(-1)^s(2^52+F)2^(E-1075) | derived | Normal finite values only; subnormals special. |
| PJ-E228 | prefix | monotone integer encoding | MIE(raw)=raw xor 2^63 if nonnegative; raw xor(2^64-1) if negative | historical_report | Frozen bit convention; NaNs/signed zeros explicitly handled in original model. |
| PJ-E229 | prefix | prefix depth | lcp(a,b)=clz(MIE(a) xor MIE(b)); k(x)=lcp(x,+0); D=64-k | definition | Same bit depth can mean different numerical precision across binades. |
| PJ-E230 | prefix | prefix distance | d(a,b)=2^(-lcp(a,b)) for a!=b; d(a,a)=0 | derived | Ultrametric on finite bit encodings, not ordinary real distance. |
| PJ-E231 | prefix | dyadic power test | x=+/-u2^e, u odd; u=v^d and d divides e | derived | Rational dth powers; negative sign allowed only odd d; zero separate. |
| PJ-E232 | prefix | restricted transfer heuristics | ADD=min(kA,kB); MUL=max(0,kA+kB-53); DIV=max(0,kA-kB); SQRT=max(0,kA-1) | historical_report | Not universal IEEE754 guarantee; binade/cancellation cases matter. |
| PJ-E233 | prefix | prefix bookkeeping | Delta_pflux=k_result-k_in; Ksys_new=Ksys_old-k_old+k_result | definition | Register selection and meanings explicit. |
| PJ-E234 | prefix | prefix Fermat proposal | k(f(x+delta),f(x))>=k(delta)-kappa_f | proposal | Restricted operation/domain hypotheses and exact bit semantics needed. |
| PJ-E235 | physics | SYMMETRON Hamiltonian | H=L0-c/24+sum_g gamma_g T_g+kappa log L0 | proposal | Positive spectral domain for logarithm; not a validated gravity theory. |
| PJ-E236 | physics | log-periodic coupling | g(E)~E^alpha[1+A cos(2pi log(E/E0)/log C)] | proposal | Parameters and units specified before physical interpretation. |
| PJ-E237 | physics | L-value constant proposals | alpha=L(E,1)/(2pi); beta=L(f,3/2)/pi^(3/2); kappa=L'(g,1)/L(g,1) | proposal | Underlying objects not recovered; cannot use as determined constants. |
| PJ-E238 | physics | activation model | F(x)=1/(1+exp(-x/.0712)); H*=H+alpha abs(H)^beta F(H/Ep) | proposal | Functional calculus, units, and physical fit not established. |
| PJ-E239 | physics | spectral dimension model | d_s(E)=4-alpha(E/Ep)^beta F(E/Ep) | proposal | Model ansatz, not observed dimension law. |
| PJ-E240 | physics | six-term potential | U(theta)=cos2theta+(2/3)cos3theta+(2/5)cos5theta+(1/4)cos8theta-(2/9)cos9theta-(1/6)cos12theta | historical_report | Local phase check distinct from physical CKM prediction/global proof. |
| PJ-E241 | physics | phase derivative | U'=-2sin2theta-2sin3theta-2sin5theta-2sin8theta+2sin9theta+2sin12theta | derived | Direct derivative. |
| PJ-E242 | physics | golden phase identity | theta*=11pi/30; 1-2cos(12theta*)=(3-sqrt5)/2=phi^(-2) | derived | Shared by other phase points; does not alone select66degrees. |
| PJ-E243 | physics | observable ratio | Ceff=\|Uub\|(1-\|Uub\|^2)/(\|Uus\|\|Ucb\|) | definition | Nonzero denominator; model must enforce value. |
| PJ-E244 | physics | conditional observable polynomial | c^2(1-c^2)^2-3abc(1-c^2)+a^2b^2=0 | conditional | a=\|Uus\|,b=\|Ucb\|,c=\|Uub\|, if Ceff=phi^-2. |
| PJ-E245 | physics | unresolved archived polynomial | c^2 t^4-7abc t^2+a^2b^2=0 | open | Original a,b,c,t definitions unrecovered; do not equate with coefficient3 relation. |
| PJ-E246 | physics | unresolved phase polynomials | 4t^2 J^2=4K-N^2; N^8-7N^6K+14N^4K^2-8N^2K^3+K^4=0 | open | Original N,K,t,J definitions missing. |
| PJ-E247 | physics | allowed perturbation | V_epsilon=V0+epsilon x | historical_report | A CP-even deformation changed the golden relation; protection unresolved. |
| PJ-E248 | physics | coercivity certificate | f-L=sigma0+sum_i sigma_i g_i+sum_j q_j h_j | proposal | SOS positivity and constraint conventions needed; no universal optimizer guarantee. |
| PJ-E249 | physics | wall threshold law | Gamma proportional (M-2m)^3 near threshold | historical_report | Specific channels/model, not universal decay law. |
| PJ-E250 | wind | vorticity | zeta=v_x-u_y | definition | Coordinates and velocity components explicit. |
| PJ-E251 | wind | stretch tilt divergence | S=(zeta+f)w_z; T=-v_z w_x+u_z w_y; D=-(zeta+f)div(u) | historical_report | Saved signed-source ledger; governing equation convention must match. |
| PJ-E252 | wind | baroclinicity | B=(rho_x p_y-rho_y p_x)/rho^2 | historical_report | Density positive; coordinate signs fixed. |
| PJ-E253 | wind | forcing beta source | F=(curl forcing)_z; P_beta=-beta v; S_zeta=S+T+D+B+F+P_beta | historical_report | Budget term ledger, not full unobserved atmosphere reconstruction. |
| PJ-E254 | wind | exact SDE | F=exp(A Delta_t); Qd=int_0^Delta_t exp(As)LL^T exp(A^Ts) ds | derived | Linear constant-coefficient SDE. |
| PJ-E255 | wind | innovation support | I=sum_i K_i nu_i^T S_i^(-1)nu_i | historical_report | K_i spatial support kernel, not necessarily Kalman gain. |
| PJ-E256 | wind | constraint injection | C=delta_xC^T Q delta_xC | definition | Declared metric; mechanism and causality separate. |
| PJ-E257 | wind | dynamic residual | R=norm(W[partial_t x+N(x)-F(x)])^2 | definition | Units, supports, operators required. |
| PJ-E258 | wind | expiry rule | t_exp=inf{t:A_struct^2/V0>=eta_s or Vplus/V0>=eta_p} | historical_report | Baseline positive; model expiry criterion. |
| PJ-E259 | wind | exterior law | v=c r^(-p); p=1+2h | historical_report | Quadrant envelopes are not pointwise wind samples. |
| PJ-E260 | wind | pressure adequacy | Delta_t<=L/(2U); quadratic fit needs at least7 stations | historical_report | Six coefficients plus residual degree of freedom, rank/conditioning separately checked. |
| PJ-E261 | wind | assimilation commutator | [A,F]x | proposal | Order effects between assimilation and dynamics. |
| PJ-E262 | sequence | Pauli product | (a.sigma)(b.sigma)=(a.b)I+i(a cross b).sigma | derived | Standard Pauli convention. |
| PJ-E263 | sequence | commutator | [a.sigma,b.sigma]=2i(a cross b).sigma | derived | Order-sensitive interaction, not automatically empirical predictive feature. |
| PJ-E264 | sequence | symmetric-order split | AB=1/2{A,B}+1/2[A,B] | derived | Algebraic identity. |
| PJ-E265 | sequence | nested interaction | [A,[B,C]] | proposal | Higher-order feature; test against commutative ablation. |
| PJ-E266 | graphs | weighted histogram | Z_N(u)=sum_n c_n exp(n.u) | exact_checked | Histogram partition exact for rational multiplicative weights; log derivatives mathematical. |
| PJ-E267 | graphs | gradient covariance | grad log Z=E[n]; Hessian log Z=Cov(n)>=0 | derived | Finite positive partition function. |
| PJ-E268 | graphs | phase domination | abs(Z_N(u+i phi))<=Z_N(u) | derived | Positive multiplicities; triangle inequality. |
| PJ-E269 | graphs | subcritical tail | sum_{ell>=d}C(mu eta)^ell=C(mu eta)^d/(1-mu eta) | derived | mu eta<1 and justified graph-count domination. |
| PJ-E270 | graphs | finite histogram compression | 4133166 walks ->66 type vectors | historical_report | Specific retained length10 graph; order-specific observables require richer state. |
| PJ-E271 | finsler | dead-zone action | phi(v)=0 if abs(v)<=c; (abs(v)-c)^2/(4D) otherwise | definition | D>0,c>=0. |
| PJ-E272 | finsler | convex conjugate | phi*(p)=c abs(p)+D p^2 | derived | Exact Legendre transform of declared dead-zone action. |
| PJ-E273 | finsler | Hamiltonian | H=b.p+sum_i(c_i abs(p_i)+D_i p_i^2) | derived | Normalization tied to the displayed Lagrangian. |
| PJ-E274 | finsler | Hamilton-Jacobi | H(x,grad W)=0 | proposal | Viscosity/subgradient treatment at nonsmooth facets. |
| PJ-E275 | finsler | FW action | S=1/4 int (xdot-b)^T D^(-1)(xdot-b) dt | definition | Noise normalization fixes epsilon and diffusion factors. |
| PJ-E276 | finsler | escape proxy | lambda_FW=exp(-Wmin/epsilon); P_T=1-exp(-T lambda) | historical_report | Asymptotic exponential rate/prefactors and Poisson assumptions separate. |
| PJ-E277 | thermal | energy deformation | H_i=E_i+cE_i^a | definition | Energy domain for fractional powers and units required. |
| PJ-E278 | thermal | partition and purity | Z(beta)=sum_i exp(-beta H_i); F(beta)=log Z(2beta)-2log Z(beta) | derived | Finite Gibbs spectrum. |
| PJ-E279 | thermal | purity identity | exp(F)=Tr(rho_beta^2) | derived | Normalized Gibbs density matrix. |
| PJ-E280 | thermal | variance objective | V=Var_{t uniform}[F(exp(t))] | definition | Grid/range/clipping specified; different historical objectives not conflated. |
| PJ-E281 | thermal | finite-size intercept | spread(N)=A+B/N | proposal | Model fit, not automatically an asymptotic theorem. |
| PJ-E282 | thermal | weak exponent identification | c=0 implies H_i independent of a | derived | Near-zero c undermines preferred-exponent inference. |
| PJ-E283 | closure | finite closure | cl(A)=intersection{B superset A:B stable} | definition | Finite closure-system implementation proposal. |
| PJ-E284 | closure | closure debt | D(A)=mu(cl(A))-mu(A) | definition | Monotone nonnegative measure mu. |
| PJ-E285 | closure | admitted state | adm=c_{R_sound(w)}(X) intersect(S intersect w) | historical_report | Original finite atom/rule semantics required. |
| PJ-E286 | closure | obstruction partition | Omega=Omega_miss disjoint-union Omega_ung disjoint-union Omega_rule | historical_report | Missing support, ungrounded claims, rule gaps. |
| PJ-E287 | closure | closure-cost invariant | I_tau=(K_tau*,Lambda_tau,B_tau) | proposal | Minimal admitted closure cost, cheaper-route witnesses, fake-work spectrum; invariance tests needed. |
| PJ-E288 | closure | comparison cochains | gamma_ij=C_i-C_j; eta_i(f)=Psi(f)C_i-C_i Phi(f) | proposal | Linear/additive setting required for subtraction/cohomology. |
| PJ-E289 | closure | total differential | D=delta_Cech+(-1)^p d_I; D^2=0 | conditional | Compatible double-complex structure, not arbitrary nonlinear constraint sheaves. |
| PJ-E290 | closure | cohomological trichotomy | DDelta!=0 incoherent; Delta=Dh removable; closed nonexact obstruction | derived | For an actual declared cochain complex. |
| PJ-E291 | closure | null-labor efficiency | eta(E)=1-K(residue)/K(expansion) | definition | Cost model and correctness preservation must be explicit. |
| PJ-E292 | closure | representation profile | P(q)=(Q_exact,Q_bounded,E,D,C) | proposal | Preserved questions, bounds, domain, and cost. |
| PJ-E293 | closure | question-dependent height | h_q(x)=h(q(x)) | proposal | Organizes search, does not replace a global completeness bound. |
| PJ-E294 | closure | adaptive local sieve | R_m={e mod m:retained constraints hold}; next test by eliminated_population/cost | proposal | Valid exact exclusions independent of heuristic test order. |
| PJ-E295 | closure | repair pipeline | question->candidate->closure test->exact model / bounded model / repair witness | proposal | Master architecture; not one universal theorem. |
| PJ-E296 | transport | integer infeasibility certificate | y in Q^m, yB in Z^n, yb not in Z => Bx=b has no integer solution | exact_checked | y=U_i/d_i from a failing Smith coordinate; yB=0, yb!=0 when the system already fails over Q. |
| PJ-E297 | transport | saturation index | [(Q-span(G) intersect Z^n):Z-span(G)]=d_1 d_2...d_r | exact_checked | Rows of G independent or not; witness row of V^{-1} at the first d_i>1. |
| PJ-E298 | transport | integer kernel | ker_Z B=Z-span(V e_{r+1},...,V e_n) | exact_checked | UBV=D with rank r; the basis is saturated. |
| PJ-E299 | series | Hankel realization | x_{pa}=x_p M^{-1}H_a; f(p)=x_p M^{-1}h; alpha=x_empty | exact_checked | M invertible Hankel block on chosen prefixes/suffixes; agreement beyond the block is a held-out check with a witness word. |
| PJ-E300 | series | coarsest exact lumping | sum_{i in B}A_c[i][j] constant over j in C for all blocks B,C and all costs c; H constant on blocks | exact_checked | Partition refinement from output labels; every valid lumping refines the result. |
