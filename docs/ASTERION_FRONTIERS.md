# Asterion next push: higher kernels, elliptic compatibility and monodromy

Version0.19.0 · 20October2026 · Exact mathematical research report

The next push determines exact arc-kernel characters through weight six, proves an
infinite translation tower and a further primitive-relation obstruction at
weight six, implements the classical rank-eight dynamical elliptic E8
r-matrix with an all-orders proof, and identifies the compact and complex
Zariski closures of the existing five-channel level-four KZ monodromy.
The full all-weight arc kernel and a constructed quantum elliptic E8
presentation remain open tasks in this programme. These results are new to
the programme; worldwide mathematical priority has not been established.

All64 earlier programme identifiers and acceptance gates are retained. The
companion closure audit records which portions have been completed and which
larger questions survive. Earlier exact bases, transports, integer lattices,
currents and weight-four null certificates are preserved.

## The higher kernel grows beyond its first generator

Let V=L1(E8), R=V/C2(V), A=J∞R, and K=ker(A→grLi V). The earlier
projected-polarization proof gives

\[
R=\mathbb Q\oplus\mathfrak e_8\oplus(\mathbf1\oplus V_{3875}),
\qquad R_{\text{ordinary degree}\ge3}=0.
\]

Thus dimR=4125. This is a finite nonreduced algebra, while its arc algebra
has infinitely many derivative variables. Ordinary polynomial degree, Li
degree and conformal weight must be kept distinct.

The new all-jet calculation fixes ordinary polynomial degree three and
lets the total derivative degree d vary. Its exact Hilbert series is

\[
\boxed{H_{A,\ell=3}(t)=
\frac{151373t+961248t^2+3321371t^3+4932875t^4
      +4123000t^5+1763125t^6}
 {(1-t)(1-t^2)(1-t^3)}.}
\]

This is an all-derivative theorem for one polynomial-length sector. The
proof uses the finite E8 pair projector and S3 covariants on three jet
positions. Its boundary restriction maps have exact ranks; the earlier
cubic multiplication certificate supplies the finite representation data.
It is not an asserted Hilbert series for the entire arc algebra.

At conformal weight five, the length-three piece has dimension1112621.
The length-two and length-one pieces have dimensions96008 and248. Higher
lengths vanish at that weight. Therefore

\[
\dim A_5=1208877,\qquad
\dim V_5=1057504,\qquad
\boxed{\dim K_5=151373.}
\]

The finite E8 character is

\[
K_5\cong V_{248}\oplus V_{3875}\oplus V_{147250}.
\]

The independent VOA character comes from the lattice realization:
weight μ occurs with multiplicity p8(5−|μ|²/2). Exact Freudenthal recursion,
folded to the Weyl chamber, subtracts finite irreducibles and gives

\[
V_5\cong2\mathbf1\oplus5V_{248}\oplus3V_{3875}
\oplus V_{27000}\oplus3V_{30380}\oplus V_{147250}\oplus V_{779247}.
\]

The scalar dimension agrees independently with E4/φ8. The recursion
retains complete norm bounds, dominant-weight rows and Weyl dimensions;
no large irreducible-character table is assumed without a computation.

## A lowering operator gives infinite certificates

For divided jets define derivations

\[
D x^{[r]}=(r+1)x^{[r+1]},\qquad
E x^{[r]}=x^{[r-1]}\ (r>0),\quad E x^{[0]}=0.
\]

They satisfy [E,D]=N, the ordinary polynomial-degree operator. For a
homogeneous ordinary relation q,
E(D^s q)=s·deg(q)D^(s−1)q, so E preserves the differential arc ideal and
descends to A. It is locally nilpotent on every fixed jet polynomial.

The earlier nonzero783-term symbol FQ has ordinary degree3 and EFQ=0.
Consequently

\[
E^rD^rF_Q=3^r r!F_Q,\qquad r\ge0.
\]

Every derivative remains nonzero. More generally D is injective on every
positive ordinary degree of A: if Dv=0 and Nv=pv, p>0, then
D^rE^rv=(−p)^r r!v; local nilpotence of E forces v=0. This is an all-weight
operator proof with finite exact replays, not an extrapolation of a few
computed derivatives.

The cubic-zero theorem also gives x[0]FQ=0 for every current x. The first
kernel module therefore contributes only DK4 at weight five. The primitive
quotient for the graded commutative differential ideal is exactly

\[
\boxed{K_5/(DK_4+\mathfrak e_8[0]K_4)
\cong V_{248}\oplus V_{147250},\quad \dim=147498.}
\]

This proves that the weight-four3875 module does not differentially
generate the kernel. It does not assert that this quotient classifies
unfiltered VOA strong generators. Differentiating x[0]FQ=0 also gives the
explicit infinite syzygy family

\[
\sum_{j=0}^r\binom rj D^j(x[0])D^{r-j}F_Q=0.
\]

At weight six, the length-three series gives4585365 states. The complete
short-current arc sector has dimension127132 and injects into grLi V;
exact highest-weight affine Gram blocks verify this. Since dimV6=4530744,
the kernel in the length-three sector has dimension at least181753.
Injectivity of D gives151373 dimensions from DK5. Products of lower kernel
classes have greater ordinary length, so at least30380 further primitive
dimensions are necessary in this sector. The length-four sector is
classified independently by a new finite multiplication theorem below.

| Conformal weight | Arc dimension | Simple VOA dimension | Kernel dimension | New differential-ideal primitives |
|---|---:|---:|---:|---:|
|4|217001|213126|3875|3875|
|5|1208877|1057504|151373|147498|
|6|4716373|4530744|185629|at least30380 in the certified length-three sector|

The quartic sector is dual to the multiplication kernel
ker[Sym²(1+3875)→Sym⁴(g)]. Independent Newton/Freudenthal calculations give
source character2·1+2·3875+27000+147250+2450240+4881384 and target
1+3875+2·27000+147250+2450240+4096000+4881384+70680000+79143000.
Multiplicity forces at least1+3875 in the kernel. A compact-form Casimir
bound of168 excludes2450240 and4881384. Two actual nonzero multiplication
witnesses exclude27000 and147250; the latter is a1421-term highest quartic,
verified against all eight raising operators and Casimir eigenvalue144.
The remaining singlet and3875 image ranks are nonzero by C² and C·Q.
Thus the quartic kernel is exactly1+3875, dimension3876.

Lengths five and six at conformal weight six contain at least three zero
jets and vanish. Combining all four remaining lengths proves

\[
\boxed{\dim A_6=4716373,\qquad
 K_6\cong\mathbf1\oplus V_{248}\oplus2V_{3875}\oplus V_{30380}
 \oplus V_{147250},\quad\dim K_6=185629.}
\]

An explicit nonzero invariant quartic arc class is
F0(x,y)=2B(x,y)²−B([x,y],[x,y])−2B(x,x)B(y,y), with squared tensor norm
947856. Its individual VOA image is not computed. The exact total character
does not locate every kernel copy in Li degrees two and three, or settle
which quartic classes are products of earlier generators.

The next exact closure gates are the full Li-bigraded kernel embedding,
the minimal generator list through weight six, and explicit highest null
lifts for the weight-five248 and147250 modules.
An all-weight differential or vertex-Poisson presentation requires further
primitive generators, their syzygies and a completeness proof.

## Classical elliptic compatibility is now explicit

Use the derivative-one odd theta Θ with quasiperiods2πi and logp, and
ρ(z)=Θ′(z)/Θ(z), Φ(z,x)=Θ(z+x)/(Θ(z)Θ(x)). For λ_i=λ(h_i) and
xα=λ(hα), the actual normalized E8 tensor is

\[
\boxed{r(z,\lambda)=\rho(z)\sum_{i,j}(A^{-1})_{ij}h_i\otimes h_j
 +\sum_{\alpha\in R}\Phi(z,x_\alpha)e_\alpha\otimes e_{-\alpha}.}
\]

There are304 terms:64 Cartan coefficients and240 roots. The eight dynamical
derivatives use the root coordinates, with the inverse metric confined to
the Cartan Casimir. The meromorphic domain excludes theta divisors in the
spectral differences and root evaluations. Numerator zeros are allowed.

The full classical dynamical Yang–Baxter equation is

\[
\sum_i(h_i^{(1)}\partial_i r^{23}-h_i^{(2)}\partial_i r^{13}
 +h_i^{(3)}\partial_i r^{12})
 +[r^{12},r^{13}]+[r^{12},r^{23}]+[r^{13},r^{23}]=0.
\]

The analytic proof reduces every possible weight-zero tensor coefficient
to theta addition or its opposite-root derivative limit. It covers512
Cartan triples,5760 Cartan/opposite-root coordinates and13440 ordered
root triples. Exact finite series computations independently check the full
tensor through p² in exhaustive mode:84816 bracket products cancel,
including4290 components that remain nonzero when the dynamical derivative
term is omitted. Independent spectral specializations and reversed-sign
controls were also checked.

The cusp limit and additive scaling give, sequentially, trigonometric and
rational dynamical tensors. The rational limit is independently checked:
r_rat=Ω/z+Σα eα⊗e−α/xα. This is a classical Felder construction with its
historical attribution. A quantum E8 R-matrix, its shifted quantum identity,
and an explicit KZB flat connection remain separate implementation gates.

## The level-four monodromy closure is determined

For the existing five-channel equation

\[
F'=\frac1{34}\left(\frac A z+\frac B{z-1}\right)F,
\qquad\operatorname{spec}A=(-60,-30,-12,0,2),
\]

let Γ be generated by the two based counterclockwise local holonomies U,V.
Their exact spectrum is ζ17 to the exponents0,1,2,4,11. Both have actual
and projective order17, and detU=detV=ζ17. Rigorous rational complex loop
enclosures, together with rigorous cyclotomic balls, certify all20 blocks
Pj(U)VPi(U), i≠j, as nonzero. This proves irreducibility at this rational
parameter itself. The smallest block-center norm lower bound exceeds0.0547,
while the largest propagated block error is below0.000002852.

Prime dimension and order17 exclude an imprimitive line system. The finite
primitive degree-five classification excludes projective element order17,
so Γ is infinite. At level four all five adjoint fusion channels survive;
the full five-dimensional invariant fiber is the conformal-block bundle.
Belkale's unitarity theorem supplies a preserved positive metric.

Clifford theory then forces the compact identity component to act
irreducibly. The proper connected irreducible compact candidates in degree
five preserve a symmetric form. But the exponent set S={0,1,2,4,11} has no
symmetry S=a−S modulo17, excluding projective self-duality. Hence the
identity component is SU(5). Up to one fixed unitarizing conjugacy,

\[
\boxed{\overline\Gamma=\{g\in U(5):\det(g)^{17}=1\},\qquad
 \overline\Gamma^{\mathrm{Zar}}=\{g\in GL_5(\mathbb C):\det(g)^{17}=1\}.}
\]

There are17 components; the complex connected component is SL5 and the
projective compact closure is PU5. The compact group is abstractly
SU5×C17. This determines closures, not a discrete presentation or a
faithfulness theorem for the countable dense image.
Regular-singular Schlesinger density also gives the same specialized
complex algebraic group as the pointwise differential Galois group.

An independent residue calculation gives associative algebra M5(Q), Lie
algebra gl5(Q), and centered Lie algebra sl5(Q). Degree-ten polynomials
in adA isolate the actual off-diagonal matrix units. These results support
a formal/small infinite-order-parameter GL5 theorem, but were not substituted
for the specialized rational-parameter loop proof. Finite determinant image
prevents GL5 closure at every rational parameter.

## A precise elliptic interpretation of density

The common extended carrier is the rank-eight charge character

\[
H(\tau,z)=\Theta_{E_8}(\tau,z)/\varphi(q)^8,
\quad \Theta_{E_8}(\tau,z)=\sum_{\alpha\in E_8}
q^{|\alpha|^2/2}e^{2\pi i(\alpha,z)}.
\]

Its weight-one component is the original248-dimensional algebra; higher
weights contain oscillator composites and further lattice charges. The
elliptic translation law follows by exact charge reindexing. The normalized
heat identity includes the oscillator correction

\[
(2D_\tau-\sum_iD_{z_i}^2)H=\tfrac23(1-E_2)H.
\]

The first angular defect is governed by an exact all-shell relation:

\[
\sum_{|\alpha|^2=2n}(\alpha,u)^8-
\frac{240\sigma_3(n)n^4}{8}|u|^8
=\tau(n)\left(\sum_{\alpha\text{ root}}(\alpha,u)^8-30|u|^8\right).
\]

After oscillator convolution its series is H8_root(u)qφ(q)^16. Thus the
extended density has a concrete charge-angle observable and an exact
arithmetic boundary: an E8 shell is an8-design if and only if τ(n)=0.
Universal nonvanishing is Lehmer's conjecture and remains open.

The harmonic-theta compiler further expresses each even angular sector
through degree30 in ΔQ[E4,E6]_(d−8), determined by a Sturm panel of at most
two coefficients. Degree20 is the first two-dimensional cusp sector.
Whole multivariate moment tensors are replayed through degree8; the higher
displayed coefficients specialize to the first coordinate direction.

## Evidence, preservation and next work

The executable entry point is `python -m perfectjet asterion frontiers
--exhaustive --max-degree 4`. Seven component receipts and the aggregate are
retained under `results/asterion-frontiers/`. The verifier script regenerates
all outputs and compares exact deterministic bytes in `--check` mode.
Earlier `results/asterion/` and `results/asterion-extension/` remain bound to
the current source hashes and independently replayable.

The focused source package includes the engines, tests, proofs,48 new
equation records, the preserved592-record prefix, source reviews, discovery
ledger and all64 original programme gates. A successful finite test is not
silently promoted to an all-order theorem; every all-order conclusion states
its operator, modular, theta-addition or representation-theoretic proof.

The outstanding priorities are now sharper: finish the explicit Li placement
and minimal generator classification through weight six, construct
the forced higher primitive lifts, determine whether differential generators
eventually stabilize, implement an actual quantum dynamical E8 identity and
KZB connection, and study the discrete dense monodromy image or other levels.
None of these remaining tasks is hidden by the completed closure results.

Detailed proofs are in `ASTERION_KERNEL_CHARACTERS.md`,
`ASTERION_KERNEL_TOWER.md`, `ASTERION_QUARTIC.md`,
`ASTERION_QUARTIC_CHARACTERS.md`, `ASTERION_ELLIPTIC.md`,
`ASTERION_MONODROMY.md`, `ASTERION_MONODROMY_ALGEBRA.md` and
`ASTERION_JACOBI.md`. Primary-source boundaries and the preservation audit
are in `ASTERION_NEXT_PUSH_SOURCES.md`, `asterion_frontier_sources.json`
and `ASTERION_CLOSURE_AUDIT.md`.
