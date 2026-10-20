# Asterion extensions: currents, relations, recoupling and controlled boundaries

The finite Asterion programme now has a concrete starting point: an explicit mixed integral basis of E8, complete principal-polynomial and two-component polynomial multiplication laws, and exact transport among the reference descriptions. The extension problem is no longer whether a collection of polynomial labels can be made to resemble 248 directions. It is how the certified bracket, invariant form, integer lattices and finite grading interact with genuinely larger structures. Those structures include current algebras, a simple vertex algebra, jet relations, a five-channel differential connection, controlled contractions, bialgebra twists and transferred higher operations. They have different dimensions, coefficient rings and proof obligations. Their compatibility must be established by maps and identities rather than by shared notation.

The finite receipts in `results/asterion/` are retained as the base evidence. Extension receipts belong to `results/asterion-extension/`, with component subreports in the numerical export. The machine-readable discovery ledger distinguishes a computed certificate, a derivation from certified finite data, an already published result and a candidate awaiting its stated certificate. The companion programme supplies 64 stable research gates, each with dependencies, explicit acceptance criteria and a boundary on the resulting claim. None of these labels asserts worldwide priority. The modern comparison literature includes Geck's February 2026 canonical-basis preprint, Kollross's May 2026 E8 bracket revision, Song and Zeng's June 2026 classical-freeness theorem, the May 2026 derived-jet revision of Docampo, Miller and Overton-Walker, and an October 2026 associator/6j preprint. Their precise reviewed scopes are recorded in `asterion_extension_sources.json`.

## 1. The arithmetic distinction that must survive every extension

The designated response basis begins with the eight seeds \(e_i+f_i\), probes by the sixteen ordered simple positive and negative generators, and retains primitive independent commutator words in breadth-first order. It selects 248 vectors after 3,943 examined candidates, maximum selected depth 28, with determinant -1. It is therefore a Z-basis of the same Chevalley lattice. Its full unordered bracket tensor has 9,062 output terms, compared with 8,347 in the reference basis; it is about 8.57% denser by that metric. This negative result matters. An exact basis can be useful because its generators carry an operational meaning and its lattice is controlled while still losing a raw sparsity comparison.

An alternate run from the single Cartan seed \(H_1+2H_2+\cdots+8H_8\) reaches full rational rank with determinant -5. It selects 248 vectors after 3,935 candidates, at depth 29, but its Z-span has index 5. A rational basis inverse does not remove that index. To turn this observation into a structural result, one must compute a quotient functional, a missing integral vector, and whether the sublattice is closed under brackets. An index-five quotient of abelian groups is not automatically a quotient Lie algebra.

A second, established occurrence of index 5 comes from the full-rank root subsystem \(A_4\oplus A_4\subset E_8\). In fundamental-weight coset notation, the even unimodular overlattice is assembled from five cosets of the form

\[
(A_4+\omega_i)\oplus(A_4+\omega_{2i}),\qquad i\in\mathbb Z/5\mathbb Z.
\]

For A4 the norm of the relevant fundamental-weight class is \(i(5-i)/5\); pairing the classes indexed by i and 2i produces even integral glue. The subsystem lattice has determinant 25, so an index-five overlattice has determinant 1. The existing exact chart transport also finds index 5 in the two-A4 Cartan embedding. These are maps with explicit coordinates. The compound-seed index and the root-lattice gluing index become the same phenomenon only if a specific integral comparison proves it. Retaining both observations without conflating them is the starting point of AST-P002 and AST-P003 [AST-S030].

The principal divided-chain basis supplies a contrasting arithmetic outcome. All its displayed coordinates are integral, yet its absolute determinant has 21,186 bits and is not a unit. The Jordan basis supplies a different success: every compiled coefficient belongs to \(\mathbb Z[\zeta_5]\), with power-basis integer entries of magnitude at most 2, so its 248 vectors span a closed free rank 248 Lie lattice over \(\mathbb Z[\zeta_5]\). That module has Z-rank 992. It is not an identified rank 248 Chevalley Z-lattice. Every subsequent current, quantum or geometric extension must state which of these rings and lattices it uses.

## 2. Currents and the simple level-one quotient

Fix the invariant form B in the convention where long roots have squared length 2. The affine extension is

\[
[x\otimes t^m,y\otimes t^n]
=[x,y]\otimes t^{m+n}
+m\delta_{m+n,0}B(x,y)K.
\]

The central term is a cocycle because B is symmetric and invariant. The degree derivation acts by \([d,x\otimes t^m]=m x\otimes t^m\). This is an infinite-dimensional algebra even though its color directions use a 248-vector basis. A finite query can be exact, but a symmetric cutoff in positive and negative modes need not be a quotient: discarded high modes can bracket back into the retained range. The positive-current and Takiff quotient \(\mathfrak g\otimes K[t]/(t^{N+1})\) instead has a genuine truncation ideal. It is a different object and must not silently inherit the affine central term.

For E8 the dual Coxeter number is 30. The Sugawara central charge at level k is

\[
c(k)=\frac{248k}{k+30},\qquad c(1)=8,
\]

away from the critical level -30. At level 1 the simple affine vertex algebra is the E8 lattice VOA. If \(\phi(q)=\prod_{n\ge1}(1-q^n)\), its vacuum-normalized character and the universal 248-current PBW character are

\[
Z(q)=\frac{E_4(q)}{\phi(q)^8},\qquad
U(q)=\frac1{\phi(q)^{248}}.
\]

The initial exact coefficient populations are

| Weight | Universal PBW | Simple level-one | Removed by the simple quotient |
|---|---:|---:|---:|
|0|1|1|0|
|1|248|248|0|
|2|31,124|4,124|27,000|
|3|2,634,752|34,752|2,600,000|
|4|169,205,626|213,126|168,992,500|

The enormous removal is a representation-theoretic quotient, not a failure of the finite 248-dimensional Lie bracket. Universal PBW monomials specify the source vacuum module; the simple integrable VOA imposes singular-vector relations and their descendants. This distinction is the basis for the density and arc-kernel calculations rather than an obstacle to suppress.

The finite \(\mathbb F_5^3\) grading supplies a strong refinement. The 124 nonidentity grading automorphisms lie in the same relevant order-five conjugacy class, with fixed finite Lie algebra of dimension 48 and four other eigenspaces of dimension 50. Thus all nontrivial twining traces agree. For the simple VOA, fixed lattice momenta and oscillators yield

\[
T(q)=\frac{5\Theta_{A_4\oplus A_4}(q)-E_4(q)}{4\phi(q)^8}.
\]

Fourier inversion on the 125-element grading group gives the neutral and each nonzero-grade population series:

\[
Z_0=\frac{Z+124T}{125},\qquad
Z_a=\frac{Z-T}{125}\quad(a\ne0).
\]

The initial populations are \(Z_0=(1,0,32,280,1706,\ldots)\) and \(Z_a=(0,2,33,278,1705,\ldots)\). Their sum recovers the ungraded character, while their first weight recovers precisely the 124 two-dimensional planes of the finite Lie algebra. This all-degree description depends on the conjugacy and twining argument, not on extrapolating a few integer coefficients. Its established VOA and grading ingredients retain attribution [AST-S004, AST-S007, AST-S008].

A certified modular-form identity simplifies this twine for all orders:

\[
5\Theta_{A_4\oplus A_4}-E_4
=4\frac{\eta(\tau)^{10}}{\eta(5\tau)^2},
\qquad
T(q)=\frac{\phi(q)^2}{\phi(q^5)^2}.
\]

The proof explicitly separates modularity from coefficient comparison. Newman's eta-product criterion gives weight 4 on \(\Gamma_0(5)\), trivial character, congruence sums 0 and 48 modulo 24, and cusp orders 0 and 2. The A4 theta series is a weight-two form with quadratic character; its square has trivial character. The group index is 6, so the weight-four Sturm bound is 2. The eta-quotient coefficients through degree 2 are 1, -10, 35, the theta-square coefficients are 1, 40, 460, and the E4 coefficients are 1, 240, 2160. These exact coefficients prove the identity once the stated modularity and holomorphy inputs are applied. The receipt records those inputs, the bound and the coefficient comparison, as well as additional finite coefficients [AST-S029, AST-S031].

The universal twine follows directly from the finite eigenvalue multiplicities:

\[
U_T(q)=\prod_{n\ge1}(1-q^n)^{-48}
\prod_{r=1}^{4}(1-\zeta_5^r q^n)^{-50}
=\frac{\phi(q)^2}{\phi(q^5)^{50}}.
\]

For the null ideal \(N=U-Z\), the neutral-versus-nonneutral difference is therefore exactly

\[
N_0-N_a=U_T-T
=\phi(q)^2\left(\phi(q^5)^{-50}-\phi(q^5)^{-2}\right).
\]

It vanishes through weight 4 and starts with \(48q^5-96q^6\). Consequently null removal is uniform across all 125 grades through weight 4, with 216 removed states per grade at weight 2, 20,800 at weight 3 and 1,351,940 at weight 4. The first neutral-versus-nonneutral imbalance is 48 at weight 5: the neutral null space has dimension 70,318,880 and each nonzero-grade null space has dimension 70,318,832. This is an all-degree character statement derived from the proved twine identity, rather than an extrapolation from the first few grades.

The 31 Cartan subalgebras also give explicit relations. For each Cartan line \(\ell\), choose its eight-current basis and restricted Gram matrix \(B_\ell\), and form

\[
s_\ell=\frac12\sum_{i,j}(B_\ell^{-1})_{ij}
J_i[-1]J_j[-1]\mathbf1.
\]

Each is the conformal state of its rank-eight Heisenberg lattice subalgebra, and each equals the level-one E8 conformal state after inner Cartan conjugacy. The implementation retains all 31 universal states, each with four PBW terms, and verifies their rank 31. The 30 differences \(s_\ell-s_0\), each with eight terms, have rank 30 and are neutral quadratic null relations. They account for 30 of the 216 neutral quadratic nulls; 186 remain beyond this displayed set. The orthogonal Cartan decomposition gives the exact universal identity \(\omega_{\mathrm{Sug}}=\frac1{31}\sum_\ell s_\ell\). Modulo the 30 relations, it becomes \(\omega_{\mathrm{Sug}}=s_0\). This cancels the displayed denominator 31 in characteristic zero. An integral VOA lattice and torsion analysis would be needed to turn it into a theorem about reduction modulo 31.

## 3. The new target is an explicit jet relation, not a rediscovery of non-freeness

For a vertex algebra V, Li's filtration produces a commutative differential algebra gr_Li V generated in differential degree by the C2-algebra R_V. There is a natural surjection

\[
\pi:J_\infty R_V\twoheadrightarrow\operatorname{gr}_{Li}V.
\]

Classical freeness means that pi is an isomorphism. Song and Zeng's June 2026 paper already proves that a nontrivial holomorphic VOA of CFT type is not classically free, including level-one E8. Their Section 6 also gives a direct weight-four contradiction: a specifically defined mixed quotient would have dimension 147,498 under classical freeness but representation theory forces dimension at least 151,125. These are dimensions of that mixed quotient, not the full weight-four character 213,126. The proposed research contribution cannot be the assertion that E8 first fails classical freeness there [AST-S007].

The sharper result is now a concrete element of ker(pi), together with an exact null lift and an independent proof that its class survives the old differential relations. The compiled relation is

\[
R=\operatorname{Sym}(F_Q)-8Q_{31}+24Q_{22},
\]

with 804 PBW terms. In the recorded three-vector normalization, the reduced contravariant Gram matrix is

\[
\begin{pmatrix}
45696&-336&-2016\\
-336&210&84\\
-2016&84&112
\end{pmatrix},
\qquad
\ker G=\operatorname{span}(1,-8,24).
\]

The matrix identity is exact. More substantially, the relation pairs to zero against all 14,441 PBW monomials of conformal weight 4 and the relevant finite root weight; other weight spaces are orthogonal by the Cartan grading. Its leading Li symbol \(F_Q\) has 783 terms and is a nonzero highest vector of the 3875-dimensional finite module. The report retains the vector, the enumerated PBW sector and the exhaustive pairing result. The reduced three-by-three Gram matrix alone would not prove radical membership in the full affine module.

Nonmembership in the old arc ideal is certified independently. In the target highest-weight sector, the raising matrix on \(\operatorname{Sym}^3\mathfrak g\) has 791 rows and 364 columns and has full column rank 364 modulo 1009. On \(\operatorname{Sym}^2\mathfrak g\otimes\mathfrak g\), the combined raising and split-Casimir constraint matrix has 3,366 rows and 1,092 columns, again full column rank modulo 1009. The old quadratic singular module \(I\) lies in split-Casimir eigenvalue 2, verified first on \(e_\theta^2\) and then extended by invariance. Consequently the old sources \(\mathfrak g\,\partial I\), \(I\,\partial\mathfrak g\) and \(\partial\operatorname{Sym}^3\mathfrak g\) supply no highest 3875 component in the sector under consideration. Full column rank modulo a prime proves injectivity over the rationals; this is an exact rank certificate, not a numerical estimate.

Together, the exhaustive affine null pairing, the nonzero highest Li symbol and the independent old-ideal nonmembership prove an explicit 3875-dimensional submodule of \(\ker\pi\). A further exact dimension certificate proves completeness at conformal weight four. The cubic symmetric power decomposes into modules of dimensions 248, 30,380, 779,247 and 1,763,125, whose sum is \(\dim S^3\mathfrak g=2,573,000\). The implementation retains an explicit highest vector for each summand. For polarization \(\delta:S^3\mathfrak g\to S^2\mathfrak g\otimes\mathfrak g\), multiplication \(\mu\), and the 27000 projector

\[
P_I=\frac{(\Omega+12)(\Omega+60)}{868},
\]

the scalars of \(\mu P_I\delta\) on these four summands are \(54/31,3/7,13/7,3\). All are nonzero, so \(I\mathfrak g=S^3\mathfrak g\): the quadratic ideal kills every cubic. The complementary map has scalars \(39/31,18/7,8/7,0\), with direct vanishing of the projected polarization on \(e_\theta^3\). Its image has dimension 809,875. This determines the mixed arc quotient as \(248\oplus3875\oplus147250\), of dimension 151,373. The weight-four arc pieces have dimensions 151,373, 65,380 and 248, totaling 217,001. The simple VOA weight-four space has dimension 213,126, independently consistent with the published basic-representation decomposition [AST-S032]. The entire weight-four kernel therefore has dimension 3,875 and equals the displayed highest-vector orbit.

The explicit 3875 module thus exhausts the conformal-weight-four kernel, rather than merely giving a lower bound. It lies in Li differential degree one. Its finite grading is also determined: the simple weight-two population has 32 neutral and 33 states per nonzero grade. Subtracting the derivative-current contribution, respectively 0 and 2, and the invariant singlet, respectively 1 and 0, leaves 31 states in every grade of the 3875 module. Therefore the entire weight-four arc kernel has 31 dimensions in each of the 125 finite grades, equivalently 31 regular representations of the grading automorphism group after adjoining fifth roots of unity. This is a representation and character certificate; the 783-term highest vector has not thereby been expanded into a full Jordan-coordinate basis. Its uniform defect of 31 at weight four is distinct from the full affine null ideal's first neutral excess of 48 at weight five.

This finite-weight completeness does not classify the infinite arc kernel, a minimal differential generating set, or its higher syzygies. AST-P018 through AST-P022 retain those targets, and the published non-freeness statement retains its attribution.

The 2026 derived-jet paper of Docampo, Miller and Overton-Walker gives a rigorous broader setting for the next step: derived jet and arc constructions, cotangent complexes and higher homotopy invariants. Agreement with classical jets and arcs holds for smooth schemes and, more generally, local complete intersections with log canonical singularities; the singularity hypothesis matters. Applying the vocabulary does not automatically construct a derived resolution of this particular VOA relation scheme. The programme therefore asks for explicit differentials, syzygy matrices and finite jet orders before any higher derived claim [AST-S009].

## 4. Five-channel KZ arithmetic and the number 31

The adjoint tensor square decomposes multiplicity freely as

\[
248\otimes248=1\oplus248\oplus3875\oplus27000\oplus30380.
\]

The symmetric part is \(1+3875+27000\), while the alternating part is \(248+30380\). Split-Casimir projectors compress appropriate invariant four-point tensors to five channels. In long-root-squared-two normalization, the ordinary Casimir values give pairwise split-Casimir eigenvalues

\[
-60,\ -30,\ -12,\ 0,\ 2.
\]

Universal adjoint Racah and split-Casimir formulas are established prior work [AST-S010, AST-S011]. The implementation now derives an exact five-by-five realization from the E8 tensor: all 8,088 lowered structure entries are alternating, all 248 adjoint Casimir actions equal \(60I\), the crossing matrix squares to the identity, and \(XAX=B\), \(A+B+C=-60I\), projector identities and infinitesimal braid identities hold exactly. The displayed channel order is \((1,248,3875,30380,27000)\). A rational crossing matrix in a nonorthonormal tensor basis can be correct while orthonormal formulas contain square roots; the retained diagonal metric and basis gauge specify the convention. The current matrix denominator has least common multiple 26,040, with primes 2, 3, 5, 7 and 31. No minimal localization is asserted.

With residues A and B, the four-point connection has the form

\[
\kappa\frac{dF}{dz}
=\left(\frac A z+\frac B{z-1}\right)F,
\qquad \kappa=k+30.
\]

Its local formal solutions can be computed exactly. If \(F=z^\lambda\sum_{n\ge0}v_nz^n\), then

\[
\bigl(\kappa(n+\lambda)I-A\bigr)v_n
=-B\sum_{j=0}^{n-1}v_j\quad(n\ge1).
\]

When the matrix on the left is singular, a left-nullspace pairing detects an obstruction to a logarithm-free solution. A correct solver must retain that obstruction and, when necessary, construct logarithmic terms. Merely skipping the step destroys the differential equation.

At \(\kappa=31\), the extreme residue difference is 62, so the local exponents differ by 2. In the singlet branch, the exact order-two obstruction in the 27000 channel is \(12/6727\), which is nonzero: that branch requires a logarithm. At \(\kappa=32\), the 248 branch has a nonzero order-one obstruction \(3/1736\) in the 27000 channel. These are formal low-level connection results. The level-one E8 VOA is holomorphic, and its adjoint current states are descendants in its vacuum module rather than an independent adjoint primary module. Thus the five-channel connection at \(\kappa=31\) is not a five-primary fusion block for that VOA. The complete classical adjoint channel regime is valid at integer levels \(k\ge4\) [AST-S012].

In that regime the local conclusion is stronger and different. Since \(\kappa\ge34\) and the largest residue gap is 62, a positive-integer resonance can only occur at recurrence order one. The only candidate levels are \(k=18,30,32\), corresponding to gaps 48, 60 and 62; the exact obstruction sources vanish at each. All remaining recurrence steps are invertible. This proves local logarithm-free Frobenius solutions to every order for every integer \(k\ge4\). It is a local statement; it does not imply trivial global monodromy.

The continuation engine transports Gaussian-rational initial data along complex polygons using exact Taylor coefficients, a Cauchy-disk tail bound and a propagated rounding enclosure. At the recorded connection parameter \(h=1/34\), a 128-step, order-40 loop based at \(z=1/2\) around 0 has matrix error at most \(3.390\times10^{-12}\). Crossing gives the companion loop around 1 as \(V=XUX\). The commutator \(UV-VU\) has certified norm greater than 9.75, with propagated error below \(4.225\times10^{-10}\). Thus this specified monodromy image is nonabelian. Both matrices have rigorous enclosures; no group closure, density or complete classification is claimed. A canonically normalized 0-to-1 connection matrix remains a different task with endpoint-normalization requirements.

Derived KZ/Gauss-Manin comparison also has established prior theory [AST-S013]. The October 2026 preprint relating rationalized associators and quantum 6j matrices offers a current comparison target, with proved and checked smaller examples in its abstract. It is retained as a source lead, not imported as an E8 theorem [AST-S014].

## 5. Principal recoupling has more channels than the Lie bracket

The 170 nonzero principal couplings are exact data for a Lie bracket, but the associativity transformations used to compare nested tensor products live in larger intertwiner spaces. Ordinary 6j symbols have factorial-sum and terminating balanced \({}_4F_3\) descriptions. Crosschecking both conventions is an effective exact arithmetic test; root-of-unity and elliptic analogues require their own limiting and normalization data [AST-S015, AST-S016].

A recoupled Jacobi identity contains products of two kappa coefficients multiplied by a Racah transformation. The intermediate Lie-bracket output can only be an E8 exponent block, but a complete recoupling basis for the tensor products contains admissible spins outside the eight-exponent set. Their Lie couplings may be zero; their tensor channels do not thereby cease to exist. Requiring all coordinates of Jacobi to vanish includes equations in those outside channels. Clipping every intermediate label to the eight exponents loses actual constraints. In the panel \((7,11,13)\to17\), the complete system has 15 coordinate equations and 14 coupling-product monomials, with rank 13; clipping to E8 labels leaves rank 4, losing nine constraints. In \((11,13,17)\to19\), the rank falls from 17 to 6, losing eleven. The implementation checks factorial and balanced terminating \({}_4F_3\) formulas, rational recoupling with weighted orthogonality, and both paths of a multiplicity-three pentagon for four half-spins with output spin one. These are explicitly enumerated panels, rather than every possible spin quadruple. AST-P031 and AST-P032 preserve the broader target.

Highest-vector rescalings act as \(z_m\mapsto u_mz_m\) and \(\kappa_{ab}^{c}\mapsto(u_au_b/u_c)\kappa_{ab}^{c}\). They explain some coefficient freedom but not arbitrary zero patterns. The 76 unordered invariant trilinear slots and 68 nonprincipal slots organize data; they are not free deformation parameters. A useful next result would identify a minimal set of gauge-invariant coupling ratios and reconstruct all 170 constants from them under proved Jacobi and normalization constraints.

The infinitesimal gauge image is explicit. Its 170-by-eight matrix has entries \(\kappa_{ab}^{c}(u_a+u_b-u_c)\), rank eight and a retained left inverse. Fixing the eight principal action coefficients leaves 162 variables and a 162-by-seven gauge matrix of rank seven. A selected set of 155 actual nonprincipal Jacobi rows has rank 155 and annihilates all seven gauge directions. Adding seven principal-action Jacobi rows gives rank 162 in all 170 variables and annihilates the eight-dimensional gauge image. Therefore the fixed-principal and full tangent kernels equal those gauge images exactly. This uses literal Jacobi rows, not merely a dimension inferred from Whitehead's lemma, and it does not require allocation of the dense full grid.

Because the gauge orbit dimension equals the Zariski tangent dimension at the certified characteristic-zero law, the local Jacobi scheme is smooth there: dimension eight, or seven with principal action fixed. The corresponding gauge orbit is locally open. Whitehead H1/H2 and complete reducibility provide an independent conceptual explanation [AST-S027, AST-S028]. The direct scan uses 161 panels, 1,947 equations, including 1,379 equations outside the E8 intermediate labels. It selects 155 independent rows from 102 panels; 117 selected rows are outside those labels. The retained selected matrix has 1,858 nonzero coefficients.

There is a stronger full-support conclusion. Every self-channel \(\kappa_{mm}^{m}\) is nonzero and transforms by \(\lambda_m\), so each diagonal scale is uniquely recovered as \(\lambda_m=\kappa'_{mm}{}^{m}/\kappa_{mm}^{m}\). The diagonal stabilizer is trivial. All remaining orbit equations are the Laurent graph \(\kappa'_{ab}{}^{c}/\kappa_{ab}^{c}=\lambda_a\lambda_b/\lambda_c\). Hence the gauge orbit is closed in the torus where all 170 coefficients are nonzero. It is also open there by local smoothness and translation, and is connected. The full-support connected component containing the E8 law is exactly this gauge torus, with an explicit global inverse on the orbit. Other full-support components, zero-channel boundary strata, integral models and quantum schemes remain unclassified.

## 6. A controlled Rees degeneration and a metric-completion gap

The exact principal law defines a polynomial family

\[
[x_a,y_b]_t
=\sum_c\kappa_{ab}^{c}\,t^{a+b-c-1}
T_{a+b-c}(x_a,y_b).
\]

All exponents are nonnegative. For t nonzero, \(S_t|_{V_m}=t^{m-1}\) transports the family to the original bracket. Jacobi follows over the Laurent polynomial ring from that transport and then over the polynomial ring by coefficient identity. The existing full finite Jacobi and bracket certificates identify the constants used in this argument. No finite panel at a few t values is substituted for the polynomial proof. Since the scaling is explicitly single valued, isomorphism of the nonzero fibers does not create monodromy by itself.

Exactly 16 of the 170 channels survive at \(t=0\). Eight are the principal \(\mathfrak{sl}_2\) actions. The other surviving channels have output exponent a+b-1 and coefficient plus or minus \(1/2\) in the fixed normalization. The resulting algebra is

\[
\mathfrak g_0=\mathfrak{sl}_2\ltimes\mathfrak n,
\qquad\dim\mathfrak n=245.
\]

The certified lower-central dimensions of n are 245, 207, 145, 59, 0, so n is nilpotent of class 4. Its derived-series dimensions are 245, 207, 59, 0. Its center is the 59-dimensional exponent 29 block. The full algebra has zero center and is perfect: the principal \(\mathfrak{sl}_2\) brackets onto itself, and its action brackets onto every nontrivial n block.

The invariant-form loss is structural. Distinct principal modules are inequivalent, so an \(\mathfrak{sl}_2\)-invariant symmetric form is block diagonal by Schur's lemma. The boundary bracket of two nonprincipal blocks never returns to the principal block through the removed high-order channel. Invariance against a principal element then forces each nonprincipal block pairing to vanish. The invariant symmetric-form space is one-dimensional: forms have rank zero or three, and every nonzero form has radical n. A nondegenerate E8 form cannot simply be evaluated at the boundary and inverted for Sugawara or Casimir constructions.

There is a sharp finite-dimensional completion question. If \(\mathfrak g_0\) embeds into a quadratic Lie algebra D, its 245-dimensional restricted-form radical must pair injectively with directions outside \(\mathfrak g_0\). Consequently

\[
\dim D\ge248+245=493.
\]

The canonical cotangent double \(T^*\mathfrak g_0=\mathfrak g_0\ltimes\mathfrak g_0^*\) has dimension 496 and carries the nondegenerate invariant pairing \(\langle x+\alpha,y+\beta\rangle=\alpha(y)+\beta(x)\). It supplies an upper bound 496. The general minimum therefore lies in 493, 494, 495, 496; the current argument does not choose among them. If one requires the embedded \(\mathfrak g_0\) to be isotropic, the lower bound is 496 and the cotangent construction attains it. This three-dimensional gap is a specific research target, not a claim that the canonical double is always minimal.

More general diagonal scalings assign seven nonprincipal weights w_m with w_1=0. The complete 170-channel condition is \(w_a+w_b-w_c\ge0\). It defines a full seven-dimensional pointed rational cone. The verified low-cube censuses are unusually restrictive: among 128 binary weight vectors only zero and all-one are admissible; among 2,187 ternary weight vectors exactly 129 are admissible, namely zero together with all 128 vectors having every nonprincipal weight 1 or 2. Two nonzero points have abelian radicals, and 126 have two-step nilpotent radicals. These finite enumerations do not classify the entire cone or all boundary isomorphism types. The primitive Rees ray, the cone fan, and the minimal quadratic completion remain distinct mathematical questions.

## 7. Quantum, star-product and elliptic routes require larger contracts

The principal \(\mathfrak{sl}_2\) is a Lie subalgebra of E8, but it is not a sub-bialgebra for the standard Drinfeld-Jimbo cobracket. Up to a fixed conventional scalar,

\[
\delta\Bigl(\sum_i e_i\Bigr)=\sum_iH_i\wedge e_i
\notin\Lambda^2\operatorname{span}(e,h,f).
\]

The weight-one part of the latter exterior square is spanned by h wedge e, whose cross terms do not match the diagonal sum on the left. The exact functional \(182[e_1\wedge H_1]-92[e_1\wedge H_2]\) annihilates the principal exterior square but takes value 182 on \(\delta(e)\), certifying the obstruction in the current normalization. Replacing classical coefficients by q-numbers therefore does not automatically restrict the standard quantum E8 coproduct. A twist or coideal proposal must solve compatibility and Yang-Baxter equations, including nonlinear obstruction conditions. Quantum Lie algebras themselves have established existence and uniqueness theory [AST-S017, AST-S018].

Scalar Moyal deformation presents a separate closure issue. For scalar functions f,g and matrix or enveloping color elements X,Y,

\[
[fX,gY]_\star
=\frac12(f\star g+g\star f)[X,Y]
+\frac12(f\star g-g\star f)(XY+YX).
\]

The second term requires symmetric color products. For E8, \(S^2(248)=1\oplus3875\oplus27000\), with no adjoint summand. The implementation independently certifies that absence: its highest-weight space has dimension 36 and the combined 50-by-36 raising matrix has rank 36. A generally closed target is an enveloping or full matrix-valued star algebra, with PBW filtration and extra sectors. At the scalar polynomial level, the ordinary Moyal commutator of \(x^{58}\) and \(y^{58}\) has 29 odd terms and 21 escaped polynomial degrees. Its leading term is \(3364\hbar x^{57}y^{57}\), of degree 114, outside the eight principal homogeneous spaces. Projecting it away defines a truncated model whose Jacobi and approximation error need their own analysis. Chiralization of star products has a relevant established framework [AST-S019].

An elliptic E8 direction is possible in an appropriate all-type half-current or dynamical framework. It requires the rank-eight Cartan variable, dynamical shifts and the corresponding Yang-Baxter or representation identities. A verified rational rank-one seed, \(r=e\wedge f/\lambda\), already illustrates the distinction: its ordinary CYBE is nonzero, while the dynamical derivative term cancels it exactly. That seed is not an elliptic rank-eight solution. The nondegenerate nondynamical Belavin-Drinfeld elliptic classification only admits type A in its stated setting; a type-A elliptic matrix cannot simply receive E8 labels. Gautam and Toledano-Laredo's all-type framework supplies a sound alternative [AST-S020]. A toroidal extension adds two loop directions and central differential classes; Konno and Oshima's 2024 all-type elliptic toroidal construction and Hopf-algebroid structure are prior art [AST-S021]. Neither extension is a finite new 248-dimensional Lie algebra.

The squarefree eta arithmetic in Raghava's July 2026 paper, revised in October 2026, may support certified cusp and Eisenstein calculations for eta products genuinely arising here [AST-S026]. It supplies tools, not a pre-existing identification between a level-five twine, a denominator 31 resonance and the order 30 Coxeter action. Any such bridge requires its own modular object and exact maps. The programme preserves that possibility with an explicit rejection gate against shared-prime numerology.

## 8. Honest higher brackets begin with a differential

A proper projection of an ordinary Lie algebra with zero differential does not by itself define a homotopy transfer. A contraction requires chain maps i,p and a homotopy h satisfying \(pi=1\) and \(ip-1=dh+hd\). If \(d=0\), the second identity forces \(ip=1\), so a nontrivial discarded complement is impossible in that form. An arbitrary projected Jacobi defect is not automatically a ternary L-infinity bracket.

The implemented current-form seed is \(A_N=\mathbb Q[t,dt]/(t^{N+1},t^Ndt)\), with its genuine differential \(d(t^r)=rt^{r-1}dt\), tensored with \(\mathfrak{sl}_2\). At N=3 it has dimension 21, differential rank nine and cohomology dimension three. All 441 ordered pairs satisfy graded skewness and the Leibniz rule, and all 9,261 ordered triples satisfy graded Jacobi. The contraction and side conditions are explicit. Every higher transferred bracket vanishes: each transfer tree has a lowest binary vertex whose constant-current output is killed by h. This is a nonzero-differential example with a proved strict transfer, rather than a claimed nonformal example.

A concrete nonformal source for further work is the finite differential graded commutative algebra \(A=\Lambda(a,b,c)\), with all three generators of degree 1, \(da=db=0\) and \(dc=ab\), tensored with a finite positive-current nilpotent quotient \(t\mathfrak e_8[t]/t^{N+1}\). Its differential is nonzero, its bracket is graded, and its cohomology carries Massey-product information. A verified contraction can transfer the binary bracket and rooted-tree higher operations. The first ternary terms have the schematic form \(p[h[ix,iy],iz]\), with all signs and permutations specified by the chosen convention. Positive current degree provides an algebraic arity bound: an r-input tree has current order at least r and vanishes when that order exceeds N. These are feasible finite certificates, not an appeal to an infinite collection of untested identities.

The general transfer theorem and its tree formulas are established [AST-S022, AST-S023]. A strict dg example with vanishing higher transferred operations is a valid seed but does not already exhibit the proposed nonformal ternary effect. BRST, BV and derived reductions similarly require an explicit graded complex, a square-zero differential and the claimed pairing or cohomology. Those data determine whether the language adds a theorem.

The most immediate mathematical payoffs now include a complete weight-four arc-kernel calculation, an all-degree finite-grade null-ideal defect, exact low-level resonance obstructions and certified noncommuting global monodromy loops, direct local tangent rigidity, and a controlled boundary with a sharp three-dimensional quadratic-completion gap. The unsolved interfaces are equally concrete: higher-weight kernel generators and syzygies, normalized global connection data, arithmetic reduction, the contraction fan, internal quantum twists and genuine nonformal higher operations. The programme preserves the more distant elliptic and toroidal routes with explicit hypotheses and acceptance criteria.

## 9. A classical period adapter with the nome convention exposed

The period seed uses \(Q=e^{\pi i\tau}\) for theta series and \(q=Q^2\) for the affine character. Set \(\lambda=\theta_2^4/\theta_3^4\) and \(F={}_2F_1(1/2,1/2;1;\lambda)=\theta_3^2\). The classical identities are

\[
E_4=(1-\lambda+\lambda^2)F^4,\qquad
\Delta=\frac{\lambda^2(1-\lambda)^2F^{12}}{256}.
\]

For the physical character \(\chi=E_4/\eta^8=q^{-1/3}Z\), the period cancels: \(\chi^3=E_4^3/\Delta=j\), whereas the vacuum-normalized series obeys \(Z^3=qj\). The implementation composes the formal theta, lambda and hypergeometric series using exact rational arithmetic. At default order 16, two guard orders permit 19 coefficient checks for each period, E4 and discriminant identity and 17 checks for the character cube. These are finite replays of classical identities [AST-S033]. They are useful normalization tests, but no scalar elliptic-period formula identifies the five-channel KZ connection by itself. AST-P064 asks for an actual comparison map and compatibility of differential equations and monodromy before such a bridge is claimed.

## Source map and programme

Primary source IDs AST-S001 through AST-S033 resolve to full bibliographic records and reviewed scopes in [asterion_extension_sources.json](asterion_extension_sources.json). The discovery ledger [ASTERION_DISCOVERIES.json](ASTERION_DISCOVERIES.json) carries numerical assertions, evidence paths, statuses and dependencies. The 64 stable programme entries appear in [ASTERION_RESEARCH_PROGRAMME.md](ASTERION_RESEARCH_PROGRAMME.md). The finite construction and nomenclature are developed in [ASTERION_BASIS.md](ASTERION_BASIS.md).

The [equation leverage guide](ASTERION_EQUATION_GUIDE.md) ranks the new mechanisms by proof compression and composability, with stable formula identifiers and precise witness scopes.
