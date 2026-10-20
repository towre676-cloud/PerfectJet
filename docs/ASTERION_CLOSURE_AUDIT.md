# Asterion closure audit

This audit preserves every AST-P001–AST-P064 programme gate from the v0.18 baseline. It adds next acceptance criteria without editing the shared discovery ledger, programme or equation catalogue. “Complete” always refers to the stated coefficient ring, parameter range and proof object. An implementation can finish a useful finite theorem while its larger research direction remains unfinished. No worldwide priority is asserted. Primary references and their reviewed scopes are recorded in [ASTERION_NEXT_PUSH_SOURCES.md](ASTERION_NEXT_PUSH_SOURCES.md) and [asterion_frontier_sources.json](asterion_frontier_sources.json).

## 1. Closure standards

| Level | What is sufficient | What it establishes |
|---|---|---|
| Definition | Explicit object, conventions and type-correct maps | A reproducible proposal |
| Finite certificate | Exact inputs, full declared enumeration, independent checker and corruption tests | The stated bounded instance |
| Parameter theorem | A proof reducing the entire parameter range to certified identities | The specified all-order or all-parameter statement |
| Classification | Exhaustion theorem and equivalence criteria in a declared category | Completeness within that category |

A large numerical rank, a small floating residual or a long finite character match is not automatically the next level. Conversely, a dimension theorem plus a matching exact lower-bound certificate can establish completeness without allocating the whole dense ambient matrix. The existing direct Jacobi rank proof and weight-four arc calculation use that second route.

## 2. Higher-weight arc kernel: translation and finite-sector completeness

Write A for the old arc algebra and K for the kernel of A onto the Li graded level-one E8 VOA. The baseline certifies K[4] as an explicit 3,875-dimensional module in Li differential degree one. Song–Zeng's published non-freeness theorem is the prior benchmark, not a new priority claim. [AST-S007](https://arxiv.org/html/2606.14407v1)

On divided jets define D*x[r]=(r+1)x[r+1], E*x[r]=x[r−1] and E*x[0]=0. These derivations satisfy [E,D]=N, the ordinary polynomial-degree operator. For an ordinary homogeneous relation q of degree p, E(D^s q)=spD^(s−1)q, so E descends to the source arc algebra and is locally nilpotent there. If Dv=0 with Nv=pv and p>0, then D^r E^r v=(−p)^r r!v; for large r this forces v=0. Thus D is injective on every positive ordinary-degree arc component. Only D is asserted to preserve the arc-map kernel.

For the weight-four generator F_Q, E F_Q=0 and N F_Q=3F_Q. Consequently

\[
E^rD^rF_Q=3^r r!F_Q\qquad(r\ge0).
\]

The finite monomial checks replay this all-order proof. It gives a kernel copy of dimension 3,875 at every conformal weight at least four, with at least 31 states in each of the 125 finite grades. It gives a lower bound, not the entire higher kernel.

Every ordinary cubic in g_0 vanishes in A. Since F_Q belongs to S²(g_0)g_1, all ordinary currents annihilate K[4]. Differentiating gives the exact syzygy family

\[
\sum_{j=0}^r\binom rj j!\,x^{[j]}D^{r-j}F_Q=0.
\]

The differential ideal generated at weight four therefore contributes exactly D K[4], of dimension 3,875, at weight five. These known relations cannot be silently substituted for the whole differential ideal.

The finite VOA character is independently reconstructed by exact Freudenthal recursion and lattice/Fock weight multiplicities. Its dimensions through weight six are 1,248,4124,34752,213126,1057504,4530744. Exact affine Gram blocks prove injection of the complete at-most-two-current arc sectors: dimension 96,256 at weight five and 127,132 at weight six. The irreducible blocks exhaust the symmetric and exterior squares, and the sole rank defect is the known differentiated 27,000-dimensional ordinary relation. This locates any additional low-weight kernel beyond the short-current sectors without building a dense full-weight PBW matrix. [ASTERION_KERNEL_TOWER.md](ASTERION_KERNEL_TOWER.md), [AST-S053](https://arxiv.org/html/1603.07196v2)

The complete length-three sector is now certified at every jet degree d. Dualizing turns the differential pair relations into restriction to t1=t2 in simultaneous S3-covariant polynomials. The invariant ring has generators of degrees one,two,three. The two standard covariants have degrees one,two, while alternating polynomials are the Vandermonde times symmetric polynomials. Their exact pair-diagonal images are Q[s,v²,v³], vQ[s,v] or Q[s,v], according to the independently reconstructed E8 pair-fixed type. These identities prove all degrees; a finite Gaussian-elimination panel replays the implementation.

With t marking jet degree, the resulting length-three Hilbert series is

\[
\frac{151373t+961248t^2+3321371t^3+4932875t^4+
4123000t^5+1763125t^6}{(1-t)(1-t^2)(1-t^3)}.
\]

Its first dimensions at d=0,1,2,3 are 0,151373,1112621,4585365. The complete E8 characters are independently reconstructed from the actual adjoint weights, Newton identities and Freudenthal recursion. The Lie-polarization scalars fixing the pair-line position are recomputed from the retained bracket. See [ASTERION_KERNEL_CHARACTERS.md](ASTERION_KERNEL_CHARACTERS.md).

At weight five all terms of factor length four and higher vanish. The exact arc dimensions are 1,112,621 at length three/Li degree two, 96,008 at length two/Li degree three, and 248 at length one/Li degree four. Thus

\[
\dim A[5]=1208877,\qquad \dim V[5]=1057504,
\]
\[
K[5]\simeq V_{248}\oplus V_{3875}\oplus V_{147250},
\qquad \dim K[5]=151373.
\]

The short-current injection places the entire kernel in Li degree two. D is injective and the ordinary current product vanishes, so the differential-ideal primitive quotient is exactly

\[
K[5]/(DK[4]+\mathfrak g_0K[4])
\simeq V_{248}\oplus V_{147250},\qquad \dim=147498.
\]

Therefore the weight-four module alone does not differentially generate the whole kernel. The all-order injection of its weight-five extension gives a kernel lower bound of 151,373 at every weight at least five. Twining and the finite representation decompositions give 1,209 neutral and 1,211 states in each of the 124 nonzero grades for K[5]. The primitive quotient has 1,178 neutral and 1,180 states in each nonzero grade. These are exact module distributions, not explicit Jordan-coordinate formulas for the new primitive highest vectors.

At weight six the known length-one,two,three arc pieces already total 4,712,497. Compared with the complete VOA character and injective short-current sector, their length-three/Li-degree-three kernel contains

\[
V_{248}\oplus V_{3875}\oplus V_{30380}\oplus V_{147250},
\qquad \dim=181753.
\]

The translated K[5] accounts for only 151,373 dimensions there. Earlier kernel products have ordinary degree at least four and cannot fill a degree-three component. Hence a new primitive V30380 is forced in this sector, with 248 neutral and 243 states in every nonzero finite grade. This is a submodule/lower-bound theorem: the length-four/Li-degree-two sector and the full weight-six kernel are not classified by this receipt.

The quartic boundary now also has an explicit completed proof. Its exact dual is ker[mu:Sym²(1+V3875)→Sym⁴(g)], obtained by exhausting the differential pair relations and the elementary four-slot symmetries. The invariant tensor

\[
F_0(x,y)=2B(x,y)^2-B([x,y],[x,y])-2B(x,x)B(y,y)
\]

has zero full symmetrization and satisfies every pair-null constraint. As an operator on Sym²(g), T0=2Id−Omega−2|C><C| has eigenvalues −434,14,0; these are not the split-Casimir eigenvalues, which remain −60,−12,2. Its exact self-pairing is 947,856. The tensor therefore annihilates the complete ideal in this sector but cannot itself belong to that ideal. This proves that the written polynomial is a nonzero arc class, rather than merely a nonzero dual vector. The invariant part of this quartic sector is exactly one-dimensional. [ASTERION_QUARTIC.md](ASTERION_QUARTIC.md)

This adds one arc dimension to the earlier length-at-most-three bound, giving dim A[6]≥4712498 and dim K[6]≥181754. There are at least five arc singlets versus four VOA singlets, so a weight-six kernel singlet exists. The individual VOA image of F0 is not computed; the singlet count does not locate the missing state in Li degree two or three and does not give F0 an unproved null lift.

The stronger quartic character comparison is now independently certified. Newton identities and exact Freudenthal reconstruction give

\[
\operatorname{Sym}^2(W)=2\cdot\mathbf1+2V_{3875}+V_{27000}
+V_{147250}+V_{2450240}+V_{4881384},
\]
\[
\operatorname{Sym}^4(\mathfrak g)=\mathbf1+V_{3875}+2V_{27000}
+V_{147250}+V_{2450240}+V_{4096000}+V_{4881384}
+V_{70680000}+V_{79143000}.
\]

The dimensions are 7,513,626 and 161,455,750. On both the trivial and V3875 multiplicity spaces, source multiplicity two and target multiplicity one force at least one kernel copy. The exact duality therefore proves at least 1+V3875, or 3,876 dimensions, in the quartic arc sector. This includes the invariant line already proved above; it is not an additional 3,876 dimensions beyond that line. The whole bounds are consequently

\[
\dim A[6]\ge4716373,\qquad \dim K[6]\ge185629.
\]

The character certificates reconstruct every dominant highest weight under proved norm bounds, rather than accepting a representation table because its dimensions sum correctly. The remaining multiplication ranks are now also certified. A positive compact-form pair-Casimir inequality bounds the total Casimir in the dual quartic kernel by 168. The source modules V2450240 and V4881384 have Casimirs 180 and 200, so neither can be in that kernel. The actual V27000 multiplication witness has coefficient 8/49. An explicit 1,421-term V147250 highest vector remains in the multiplication image; all eight raising equations, its highest weight and Casimir 144 are checked. The trivial and V3875 multiplicity spaces have explicit nonzero products. Every possible additional kernel summand is therefore excluded, proving

\[
\ker\mu\simeq\mathbf1\oplus V_{3875},\qquad
\dim A[6]_{\mathrm{length}\,4,\mathrm{Li}\,2}=3876.
\]

Lengths five and six vanish at weight six because each monomial contains an ordinary cubic in zero jets. Combining all lengths with the independent VOA character upgrades the whole bounds to exact finite character statements:

\[
\dim A[6]=4716373,\qquad \dim V[6]=4530744,
\]
\[
K[6]\simeq\mathbf1\oplus V_{248}\oplus2V_{3875}
\oplus V_{30380}\oplus V_{147250},
\qquad\dim K[6]=185629.
\]

The retained aggregate field `finite_weight_six_closure` records this exact character subtraction and its false stronger-claim fields. This completes the finite character calculation; it does not determine the full Li-bigraded kernel embedding, the minimal differential generator list or explicit new primitive affine null lifts. In particular the individual VOA image of F0 remains open. [ASTERION_QUARTIC.md](ASTERION_QUARTIC.md), [ASTERION_QUARTIC_CHARACTERS.md](ASTERION_QUARTIC_CHARACTERS.md)

The next closure targets are now the weight-six Li2/Li3 allocation, actual derivative and current-product images, minimal primitive modules and affine null lifts, followed by complete finite characters at weight seven. An all-order theorem for length three and exact characters through weight six do not establish the whole infinite arc kernel. Full closure still needs an all-order rewriting, resolution or generation theorem. The reviewed Kanade strategy and Laurie crystal model suggest a route; an actual map from augmented E8 normal monomials to that combinatorial model remains to be proved. [AST-S034](https://arxiv.org/html/2606.19234v1), [AST-S036](https://arxiv.org/pdf/2311.03905)

## 3. Level-four monodromy: completed closure of the chosen pure-loop representation

The exhaustive implementation now certifies the actual loop pair at h=1/34, not merely the residue algebra or a formal expansion near zero. It encloses U,V and evaluates the spectral projectors of U with rigorous root-of-unity balls. All twenty off-diagonal blocks P_j(U)V P_i(U) are nonzero: the smallest retained center-norm lower bound exceeds 0.0547440 and the largest propagated block error is below 0.000002852. Since U has distinct eigenvalues, a common invariant subspace is a subset of its five eigenspaces. The strongly connected block graph excludes every proper subset. These certified analytic gates are recorded only in an exhaustive receipt; the fast receipt explicitly leaves specialized irreducibility open.

The resulting proof chain does not require an uncomputed half-braid extension:

1. The exact U spectrum is zeta17 raised to {0,1,2,4,11}; both pure generators have order 17. A nontrivial imprimitivity system in prime dimension five consists of five lines. An order-17 permutation in S5 is trivial, so both generators would fix every line, contradicting irreducibility.
2. A finite primitive degree-five linear group has no projective element of order 17 by Rowell–Tuba Lemma 5.1(d). The determinant-normalizing central extension preserves this projective order. The primitive image is therefore infinite.
3. At level four all five multiplicity-one summands of the adjoint tensor square survive fusion, by Feingold's stability bound. Factorization identifies the full five-dimensional invariant fiber with the four-adjoint conformal-block fiber. The exact split-Casimir normalization is replayed. Belkale's theorem gives a common projective positive metric; if M*HM=cH, then c^5=|det M|². Root-of-unity determinants force c=1.
4. Clifford theory and prime dimension reduce the compact identity component to an irreducible action, a five-line system or a scalar action. Primitivity excludes the line system. Finite determinant makes a connected scalar subgroup trivial, which would make the compact closure finite. Hence the identity component acts irreducibly. Its center is trivial at Lie-algebra level, and prime dimension allows only one nontrivial simple factor.
5. The only proper connected simple candidates in degree five are SO5 and the fourth symmetric power of SU2. Both preserve a unique symmetric form. The full compact closure normalizes the identity component and thus would preserve that form up to a scalar. Consequently the U exponent set S would satisfy S=a−S modulo 17. Its sum is one, so 5a=2 and a=14; but 14−0 is absent from S. Both proper cases are excluded.
6. The connected compact closure is SU5. Both determinants equal zeta17, since their exponent sum is 18. The full compact closure, up to one unitarizing conjugation, is therefore

\[
\{g\in U(5):\det(g)^{17}=1\}.
\]

It has seventeen components and is abstractly SU5×C17: the determinant sequence splits by the scalar zeta17^(7a)I because 5·7=1 modulo 17. The projective closure is PU5. The complex Zariski closure is {g in GL5(C):det(g)^17=1}, with identity component SL5. These are closures of the specified countable pure-loop image, not a presentation of that image.

The proof is a theorem-dependent computational result: rigorous loop/projector enclosures supply the specialized analytic input, while the cited unitarity and finite/compact-group classification results supply the structural implications. Its evidence is [ASTERION_MONODROMY.md](ASTERION_MONODROMY.md), `monodromy_receipt(exhaustive=True)` and the retained frontier receipt. No explicit positive Hermitian matrix, effective word-approximation rate, discrete-image presentation, other-level closure theorem or higher-strand universality follows.

The separate exact residue compiler proves associative M5(Q), Lie gl5(Q) and centered Lie sl5(Q), using dimensions 25,25,24. It also proves that a sufficiently small analytic specialization with exp(4πi h) of infinite multiplicative order has GL5(C) Zariski closure, without computing a numerical neighborhood. Every rational specialization has a finite determinant obstruction, so that generic/formal statement cannot replace the fixed-level proof above. See [ASTERION_MONODROMY_ALGEBRA.md](ASTERION_MONODROMY_ALGEBRA.md).

## 4. Classical E8 elliptic compatibility is complete; quantum and KZB closure remain separate

The implementation now supplies the established rank-eight classical dynamical tensor

\[
r(z,\lambda)=\rho(z)\Omega_{\mathfrak h}
+\sum_{\alpha\in\Phi}\Phi(z,x_\alpha)e_\alpha\otimes e_{-\alpha},
\qquad
\Phi(z,x)=\frac{\Theta(z+x)}{\Theta(z)\Theta(x)},
\quad \rho(z)=\Theta'(z)/\Theta(z).
\]

Here the derivative-one odd theta has quasiperiods 2πi and log p. The eight coordinates are lambda_i=lambda(h_i), so x_alpha=sum alpha_i lambda_i; the inverse Cartan belongs in the Cartan Casimir, not a second time in this derivative. The complete normalized Casimir has 304 nonzero entries and is checked under all sixteen simple generators. All 240 root-metric gradients are checked.

The analytic proof exhausts the 19,712 possible weight-zero tensor coordinates: 512 three-Cartan, 5,760 one-Cartan/opposite-root and 13,440 three-root coefficients. They reduce to the theta Fay identity and its derivative/opposite-root limits, with the actual E8 bracket signs checked exhaustively. This is an all-nome meromorphic theorem from the classical theta identity, not an extrapolation from a truncated series. Its domain excludes spectral and root-dynamical theta poles; numerator zeros are allowed.

The additional exact p² replay contracts every tensor coefficient at a declared rational multiplicative specialization. Each r has 304 entries and the three commutators contain 84,816 nonzero bracket products. Deleting the dynamical derivatives leaves 4,290 nonzero tensor components; including all eight derivative families cancels all of them. This negative control is part of the certificate. The sequential trigonometric then rational limits are explicit and retain the derivative equation. See [ASTERION_ELLIPTIC.md](ASTERION_ELLIPTIC.md) and `elliptic_receipt(exhaustive=True)`.

The classical construction is Felder's existing all-type dynamical solution in the plus-kernel convention reviewed by Etingof. An implementation and exhaustive E8 transport certificate do not establish a new elliptic classification or a quantum R matrix. Analytic numerical values at a nonzero nome would additionally require pole separation and tail bounds; the current finite series engine computes exact rational coefficients.

For universal root-system KZB, the next gate remains a homomorphism from the universal generators t_alpha,x(u),y(v) into a specified algebra satisfying every defining relation. A finite adjoint action is not automatically such a homomorphism. The elliptic Casimir construction uses a completed deformed double current algebra; a finite quotient must preserve both its relations and its completion. To move in tau, the modular connection term and mixed curvature must be supplied. A quantum R matrix requires the actual dynamical shifts, coefficient field and full quantum dynamical identity. The reviewed 2018 Casimir paper still labels its quantum-toroidal monodromy comparison a conjecture.

## 5. Charged theta and shell arithmetic

The rank-eight charged character, heat/Ward identity and finite shell moments are classical identities adapted to the exact engine. Jacobi z uses exp(2πi(alpha,z)) in orthonormal Euclidean Cartan coordinates; the classical elliptic tensor uses exp(z_ell), periods 2πi and 2πi tau, and lambda_i=lambda(h_i). Their comparison therefore requires z_ell=2πi z_Jac and the normalized Cartan metric conversion. Identifying their variable names without these maps would lose the derivative normalization. Their analytic transformation laws should identify whether they apply to the lattice theta function, the vacuum-normalized character or the physical character with eta multiplier. The full weak W(E8)-Jacobi ring is already described by Sakai's published 2026 covariant theorem; implementing selected generators is a new software task, not a new finite-generation theorem.

For a harmonic polynomial P of degree eight, the E8 weighted theta series has weight twelve and lies in the one-dimensional cusp space. Comparing its first coefficient yields the all-shell identity sum_(x²=2n)P(x)=tau(n)sum_(alpha root)P(alpha). The shell is an 8-design exactly when tau(n)=0. Antipodality also kills every odd moment, so strength 8 and strength 9 coincide here. These statements are known. A finite range of nonzero defects cannot prove the all-n assertion equivalent to Lehmer's conjecture.

Those proof inputs are now retained: the exact harmonic projection, nonzero root coefficient, weighted-modularity and cusp hypotheses, Delta normalization and complete degree-eight tensor-pattern replay on the declared shell range. A further compiler treats every even angular degree from two through thirty. Its all-order modular sector is Delta·Q[E4,E6]_(d−8); it computes the e1 directional coefficients by full-rank Sturm panels and checks later coefficients. Angular degree twenty is the first two-dimensional cusp sector. The full multivariate coefficient arrays above degree eight are not computed. One may next study prime-power recurrences or conditional vanishing tests while stating their scope. The prime 31 from the Sugawara average,31 uniform kernel states per finite grade, and a denominator31 KZ resonance are separate proven appearances; a bridge among them requires an actual map or identity.

## 6. Preservation of all 64 existing gates

The following records copy each baseline title, state, dependencies and acceptance criteria. The appended “next closure” sentence is an audit proposal. No baseline item is removed or silently declared solved. A new source may show that a broad ambient theorem is already established while leaving the project's explicit realization unfinished.


Baseline ledger SHA256: `3f9c3a93fc5b4bd99b351f7d2fd964186bb099b771fd4303a1cc3e83233cdd86`. The source ledger is [ASTERION_DISCOVERIES.json](ASTERION_DISCOVERIES.json).

### AST-P001 — Cross-chart transport as one exact arithmetic interface

**Preserved baseline state:** `finite_core_completed;extension_target`.

**Preserved target:** Extend the existing complete Chevalley/principal/Jordan transforms to current modes, invariant tensors and published independent E8 models.

**Dependencies:** AST-D001, AST-D003, AST-D005.

**Preserved acceptance criteria:**

- Retain explicit transforms and inverses for every chart.
- Replay all finite basis brackets and form tensors.
- Test an independently sourced triality model rather than only transforms sharing one implementation.

**Preserved claim boundary:** A common abstract E8 label does not certify a specific isomorphism.

**Next closure:** Specify one exact cross-chart coefficient schema, declare each coefficient ring and replay all basis conversions, brackets and invariant forms through that interface.

### AST-P002 — The index-five response sublattice

**Preserved baseline state:** `research_target`.

**Preserved target:** Explain the compound-seed determinant-five lattice through explicit quotient coordinates and bracket closure.

**Dependencies:** AST-D009.

**Preserved acceptance criteria:**

- Compute Smith invariants and an explicit missing integral vector.
- Check whether the sublattice is bracket closed.
- Describe the quotient map and the mod-five obstruction to completing it by the original word grammar.

**Preserved claim boundary:** A lattice index is not automatically a Lie ideal or a quotient Lie algebra.

**Next closure:** Compute the Smith quotient functional, missing integral vector and bracket closure of the index-five compound-seed lattice.

### AST-P003 — A4-squared gluing and its two distinct index-five roles

**Preserved baseline state:** `research_target`.

**Preserved target:** Relate the two-A4 root-lattice overlattice and compound-seed sublattice only through an actual integral map.

**Dependencies:** AST-D009, AST-D011.

**Preserved acceptance criteria:**

- Construct all five cosets with exact Gram products.
- Verify evenness, unimodularity and norm-two roots.
- Produce a comparison or a counterexample identifying whether the two index-five phenomena share a map.

**Preserved claim boundary:** The same integer5 in two determinants is not evidence of the same gluing mechanism.

**Next closure:** Produce an integral map relating the compound-seed quotient to A4-squared glue, or certify that the two index-five observations are different.

### AST-P004 — Prime-by-prime saturation of principal chains

**Preserved baseline state:** `research_target`.

**Preserved target:** Resolve the large principal-chain lattice index by invariant factors and localized primitive bases.

**Dependencies:** AST-D004.

**Preserved acceptance criteria:**

- Compute exact Smith data by height blocks.
- Identify a primitive missing vector at each supported prime.
- Preserve polynomial bracket formulas under any saturation change.

**Preserved claim boundary:** Clearing denominators or individually primitivizing columns does not prove saturation.

**Next closure:** Compute the actual Smith factors or prime-local saturation indices of every principal chain block and retain explicit integral witnesses at each exceptional prime.

### AST-P005 — Descent of the fifth-cyclotomic Jordan basis

**Preserved baseline state:** `research_target`.

**Preserved target:** Find a rational or integral descent while recording which finite-grade splitting it sacrifices.

**Dependencies:** AST-D005, AST-D011.

**Preserved acceptance criteria:**

- Compute semilinear Galois descent maps explicitly.
- Check their composition cocycle.
- Give a rank 248 Z-form or an obstruction; distinguish it from rank 248 over Z[zeta5].

**Preserved claim boundary:** The existing Jordan lattice has Z-rank 992 and is not already the Chevalley Z-lattice.

**Next closure:** Construct an actual Galois-compatible lattice and descent map for the fifth-cyclotomic Jordan vectors, including preservation of bracket and invariant form.

### AST-P006 — A certified density Pareto frontier

**Preserved baseline state:** `research_target`.

**Preserved target:** Search bounded unimodular neighborhoods for a basis improving declared sparsity and coefficient-height costs.

**Dependencies:** AST-D007, AST-D008.

**Preserved acceptance criteria:**

- State the exact move set and input workload.
- Retain reversible transforms and all evaluated costs.
- Report a bounded optimum or a concrete failure; compare with the 8347-term Chevalley baseline.

**Preserved claim boundary:** The present mixed response basis is denser; no global optimum or runtime win is claimed.

**Next closure:** Publish the complete cost vectors and dominated/undominated basis list under one fixed normalization, rather than selecting a single favorable statistic.

### AST-P007 — Field-aware cost of the fifty Jordan coefficients

**Preserved baseline state:** `research_target`.

**Preserved target:** Exploit repeated cyclotomic coefficients without confusing table size with scalar operation count.

**Dependencies:** AST-D005.

**Preserved acceptance criteria:**

- Compile a multiplication/addition DAG over a fixed power basis.
- Count bit operations and coefficient growth for sparse and dense inputs.
- Measure conversion cost and repeated-query break-even.

**Preserved claim boundary:** Two-output locality alone does not establish speed superiority.

**Next closure:** Compare field operations, coefficient heights, common-denominator growth and exact bit cost for the 50 cyclotomic coefficients under declared workloads.

### AST-P008 — Reduction at bad primes and integral deformation

**Preserved baseline state:** `research_target`.

**Preserved target:** Classify which displayed integral laws retain intended properties after reduction, especially at 2,3,5.

**Dependencies:** AST-D001, AST-D005, AST-D007.

**Preserved acceptance criteria:**

- Check centers, derived dimensions and Jacobi exactly after each declared reduction.
- Track denominators and cyclotomic ramification before reduction.
- Separate a valid integral law from simplicity and smooth-group assertions.

**Preserved claim boundary:** Characteristic-zero E8 identification does not transfer every property to bad characteristic.

**Next closure:** Choose integral forms and primes, compute torsion and bracket reduction, then state the characteristic range in which simplicity or the claimed deformation survives.

### AST-P009 — Normalize the invariant form in every basis

**Preserved baseline state:** `research_target`.

**Preserved target:** Transport a fixed long-root-squared-two invariant form and its inverse into all charts.

**Dependencies:** AST-D001, AST-D011.

**Preserved acceptance criteria:**

- Replay invariance on a complete generating argument or all finite basis data.
- Record dual bases and the relation to the Killing form.
- Check hDual=30 normalization before introducing levels.

**Preserved claim boundary:** A Killing-form scalar error changes affine levels and KZ residues.

**Next closure:** Fix one normalized invariant form and retain its exact Gram matrices and transport maps across every chart.

### AST-P010 — Affine current extension with the exact central cocycle

**Preserved baseline state:** `research_target`.

**Preserved target:** Build all-mode current arithmetic from the finite bracket and normalized invariant form.

**Dependencies:** AST-P009.

**Preserved acceptance criteria:**

- Verify the cocycle and Jacobi symbolically for integer modes.
- Check degree derivation compatibility.
- Separate level specialization from a formal central generator.

**Preserved claim boundary:** Finite mode windows are not automatically Lie quotients.

**Next closure:** Fix the current central-cocycle convention and prove the cocycle identity for all modes from invariant-form invariance; finite mode checks alone are supporting evidence.

### AST-P011 — Honest finite jets and truncation maps

**Preserved baseline state:** `research_target`.

**Preserved target:** Construct Takiff or positive-current quotients whose discarded modes form an ideal.

**Dependencies:** AST-P010.

**Preserved acceptance criteria:**

- Prove the truncation ideal is bracket stable.
- Specify whether negative modes and the affine central term are absent.
- Replay quotient maps and degree bounds.

**Preserved claim boundary:** Symmetrically clipping affine modes can break Jacobi and is rejected.

**Next closure:** Use actual current/Takiff ideals for finite jets and distinguish them from cutoffs that fail to define an affine quotient.

### AST-P012 — Universal PBW states versus the simple level-one quotient

**Preserved baseline state:** `research_target`.

**Preserved target:** Transport the known integrable quotient relations into Asterion coordinates.

**Dependencies:** AST-P009, AST-P010.

**Preserved acceptance criteria:**

- Reproduce exact coefficient counts independently.
- Construct the first null-vector module and its descendants.
- Match quotient dimensions by weight and grade.

**Preserved claim boundary:** Universal PBW monomials are not a basis of the simple VOA.

**Next closure:** Retain separate universal PBW, simple VOA, C2 and arc-map objects with explicit quotient maps and relation ideals.

### AST-P013 — All-degree finite-grade characters

**Preserved baseline state:** `all_order_formula_derived_and_low_weights_computed`.

**Preserved target:** Use the single nontrivial order-five twine to compute every F5-cubed grade population.

**Dependencies:** AST-D005, AST-P012.

**Preserved acceptance criteria:**

- Prove the order-five conjugacy input.
- Derive the twine from A4-squared fixed weights and oscillators.
- Verify integer nonnegative populations and low-weight independent enumeration.

**Preserved claim boundary:** The character statement counts states; it does not give their multiplication law.

**Next closure:** Preserve the all-order modular proof and obtain an explicit finite-grade state basis only if that stronger output is claimed.

### AST-P014 — Graded null-ideal defect and its first imbalance

**Preserved baseline state:** `all_order_twining_defect_derived_and_first_imbalance_computed`.

**Preserved target:** Compare universal and simple twines to locate grade-dependent null removal.

**Dependencies:** AST-P012, AST-P013.

**Preserved acceptance criteria:**

- Prove the eta identity giving T, or retain it as conditional.
- Verify uniform null removal through weight 4 and the first weight 5 imbalance if the formula holds.
- Compute a generating series for the full defect.

**Preserved claim boundary:** A finite coefficient match alone is not an all-degree theorem.

**Next closure:** Keep the full null-ideal twine distinct from the arc-map kernel; compare their actual modules through a specified map.

### AST-P015 — Vertex-lattice cocycles across the five gluing cosets

**Preserved baseline state:** `research_target`.

**Preserved target:** Lift A4-squared coset coordinates to an explicit E8 lattice-VOA construction.

**Dependencies:** AST-P003, AST-P012.

**Preserved acceptance criteria:**

- Specify the lattice two-cocycle and locality signs.
- Verify five-coset multiplication and conformal weights.
- Identify the finite248 weight-one law with the existing bracket.

**Preserved claim boundary:** A root-lattice gluing identity alone does not verify all vertex axioms.

**Next closure:** Implement actual lattice-vertex cocycles on the five A4-squared gluing cosets and verify the bicharacter, locality and associativity identities.

### AST-P016 — Sugawara, Ward identities and central charge

**Preserved baseline state:** `research_target`.

**Preserved target:** Construct low-weight normal-ordered observables with the transported inverse form.

**Dependencies:** AST-P009, AST-P010.

**Preserved acceptance criteria:**

- Verify current OPE and Virasoro commutators in a declared mode range.
- Track normal-ordering constants.
- Derive Ward identities without treating discarded modes as zero silently.

**Preserved claim boundary:** The critical level k=-30 is excluded from this Sugawara formula.

**Next closure:** Retain the charged heat/Ward normalization and distinguish the vacuum-normalized character from the eta-multiplied physical character before comparing Sugawara operators.

### AST-P017 — Reproduce the known weight-four non-freeness witness

**Preserved baseline state:** `published_benchmark_recorded;stronger_weight4_dimension_certificate_completed`.

**Preserved target:** Use the 2026 theorem as a benchmark for the exact jet/VOA adapter.

**Dependencies:** AST-P012.

**Preserved acceptance criteria:**

- Match Song-Zeng Section6 quotient definitions exactly.
- Reproduce the representation-dimension bound and the conflicting mixed quotient.
- Label it as a replay of a published result.

**Preserved claim boundary:** Failure of classical freeness at level-one E8 is already known; its first detection is not a new discovery.

**Next closure:** Maintain attribution to Song–Zeng; use the complete217001-versus213126 project calculation as the stronger replay benchmark.

### AST-P018 — Explicit generators of the missing jet kernel

**Preserved baseline state:** `entire_weight4_kernel_explicit_and_complete;higher_weight_generators_target`.

**Preserved target:** Find concrete highest-weight relations in the canonical surjection from the arc algebra to the Li graded VOA.

**Dependencies:** AST-P017, AST-P013.

**Preserved acceptance criteria:**

- Retain the 783-term leading symbol and 804-term affine null lift with coefficients.
- Replay all 14441PBW-sector pairings and both old-source injectivity matrices.
- Prove completeness at weight 4 by exact projected-polarization dimensions; search higher weights separately.
- Transport the 3875-dimensional kernel to the finite grading and certify31 directions pergrade.

**Preserved claim boundary:** The whole conformal-weight-four kernel is now explicit and complete; higher-weight generation and the infinite differential kernel remain separate targets.

**Next closure:** Preserve the exact finite characters through weight six; determine the weight-six Li allocation and minimal generators, construct explicit null lifts, then compute the complete weight-seven kernel.

### AST-P019 — Differential syzygies and a certified finite presentation range

**Preserved baseline state:** `research_target`.

**Preserved target:** Resolve dependencies among the new kernel relations under translation and multiplication.

**Dependencies:** AST-P018.

**Preserved acceptance criteria:**

- Compute syzygies in a declared weight and jet order.
- Return exact normal-form reductions and S-pair certificates.
- State a finite-range result unless an all-order termination or generation theorem is proved.

**Preserved claim boundary:** Finite Groebner agreement does not establish the infinite differential ideal.

**Next closure:** Provide exact differential syzygies in a stated weight range with replayable normal-form or rank certificates.

### AST-P020 — Finite-grade decomposition of the arc-kernel defect

**Preserved baseline state:** `research_target`.

**Preserved target:** Use the 124 two-dimensional grades to localize missing differential relations.

**Dependencies:** AST-P013, AST-P018.

**Preserved acceptance criteria:**

- Verify the map and relations preserve finite grade.
- Compute kernel ranks per weight and Li degree.
- Compare with the null-ideal character defect while keeping the two filtrations distinct.

**Preserved claim boundary:** A current null state and a kernel class of the arc-to-Li map are different objects.

**Next closure:** Preserve the exact weight-five and forced weight-six finite-grade module distributions; transport actual primitive highest vectors into Jordan coordinates if coordinate formulas are claimed.

### AST-P021 — Cotangent complexes of the actual jet relations

**Preserved baseline state:** `research_target`.

**Preserved target:** Compute a derived presentation of the relation scheme to retain hidden dependencies.

**Dependencies:** AST-P019.

**Preserved acceptance criteria:**

- Specify a simplicial or dg resolution.
- Calculate finite jet cotangent homology with explicit differentials.
- Check the hypotheses before importing smooth or lci comparison results.

**Preserved claim boundary:** The 2026 derived-arc theorem does not identify this specific VOA kernel automatically.

**Next closure:** State a derived complex and its actual differential, verify d²=0 and compute the declared homology before claiming a resolution.

### AST-P022 — An all-order character or resolution theorem

**Preserved baseline state:** `research_target`.

**Preserved target:** Promote finite kernel data to a proven graded resolution or generating function.

**Dependencies:** AST-P018, AST-P019, AST-P020.

**Preserved acceptance criteria:**

- State exact finiteness and convergence/formal-series conventions.
- Prove generation and syzygy recurrences for all weights.
- Separate a conjectured series from a verified finite prefix.

**Preserved claim boundary:** Matching many coefficients is evidence, not an all-order proof.

**Next closure:** Extend the exact weight-six finite character calculation to weight seven and beyond, while proving a terminating differential rewriting or all-order resolution for any claimed infinite Hilbert comparison.

### AST-P023 — Adjoint tensor projectors with fixed normalization

**Preserved baseline state:** `finite_exact_five_channel_engine_completed`.

**Preserved target:** Build the five irreducible channels in248 tensor248 from the split Casimir.

**Dependencies:** AST-P009.

**Preserved acceptance criteria:**

- Verify dimensions, exchange parity and orthogonal idempotents.
- Record Casimir normalization and exact minimal polynomial.
- Compare with the primary universal formulas.

**Preserved claim boundary:** A five-dimensional invariant-channel space is not the full 61504-dimensional tensor square.

**Next closure:** Preserve exact finite tensor derivation and certify specialized analytic monodromy separately from residues.

### AST-P024 — Exact five-by-five crossing matrix

**Preserved baseline state:** `finite_exact_crossing_engine_completed`.

**Preserved target:** Construct the normalized adjoint Racah matrix in rational tensor coordinates.

**Dependencies:** AST-P023.

**Preserved acceptance criteria:**

- Record the diagonal metric and channel normalization.
- Verify crossing, duality and braid/permutation identities in the declared basis.
- Compare gauge-equivalent published universal matrices.

**Preserved claim boundary:** A rational nonorthonormal crossing matrix is not inconsistent with square roots in an orthonormal convention.

**Next closure:** Match any quantum Racah gauge and central character through actual intertwiners, not shared spectra alone.

### AST-P025 — KZ connection and infinitesimal braid relations

**Preserved baseline state:** `residue_and_braid_identities_completed`.

**Preserved target:** Compile the adjoint four-point equation and certify its flatness source.

**Dependencies:** AST-P023, AST-P024.

**Preserved acceptance criteria:**

- Check the split-Casimir infinitesimal braid relations.
- Fix signs at 0,1, infinity and kappa=k+30.
- Transport residues across coordinate charts exactly.

**Preserved claim boundary:** A local matrix ODE is not yet a global connection matrix or monodromy representation.

**Next closure:** Retain all exact residue/projector/braid identities and the convention dictionary needed for a half-braid extension.

### AST-P026 — Frobenius recurrence with resonant obstructions

**Preserved baseline state:** `formal_resonance_solver_completed`.

**Preserved target:** Solve formal local systems while detecting singular recurrence steps.

**Dependencies:** AST-P025.

**Preserved acceptance criteria:**

- Enumerate exponent differences and singular steps.
- Return exact left-null obstructions and logarithmic terms where required.
- Verify every retained coefficient by substitution.

**Preserved claim boundary:** Ignoring an unsolvable resonant step does not produce a solution; formal germs do not establish global continuation.

**Next closure:** Preserve the all-level local resonance exhaustion and exact logarithmic sources; add normalized endpoint continuation only as a separate certificate.

### AST-P027 — The arithmetic kappa=31 specialization

**Preserved baseline state:** `nonzero_order2_log_source_computed`.

**Preserved target:** Study the special denominator at hDual+1 in the mathematical adjoint connection.

**Dependencies:** AST-P026.

**Preserved acceptance criteria:**

- Compute the order-two resonance obstruction exactly.
- Determine whether logarithms appear in each local channel.
- Track rational31-adic denominators and explain the representation-theoretic level restriction.

**Preserved claim boundary:** At k=1 the adjoint is not an allowed integrable primary of the E8 level-one holomorphic VOA; this is not its five-primary conformal block.

**Next closure:** Keep the formal level-one connection distinct from forbidden level-one adjoint-primary fusion and from integral mod31 structures.

### AST-P028 — Global continuation with certified analytic errors

**Preserved baseline state:** `two_complex_generator_enclosures_and_noncommutativity_completed;normalized_connection_target`.

**Preserved target:** Connect local KZ germs along paths avoiding0,1, infinity.

**Dependencies:** AST-P025, AST-P026.

**Preserved acceptance criteria:**

- Retain exact Gaussian-rational path steps, Cauchy tail bounds and rounding enclosures.
- Replay the 128-step order 40 loop at h=1/34 and its crossing-related companion; bound the commutator away from zero.
- Construct independently normalized endpoint connection matrices and verify further path composition and inverse calibrations.

**Preserved claim boundary:** Two generator holonomies and a certified nonabelian image are computed. A full monodromy-group identification, density theorem or canonical endpoint associator is not established.

**Next closure:** Preserve the now completed exhaustive level-four compact and Zariski closure certificate; classify another level, an explicit Hermitian metric or the countable image only with additional proofs.

### AST-P029 — Associator and quantum Racah comparison

**Preserved baseline state:** `research_target`.

**Preserved target:** Test whether a precisely normalized E8 associator matches the relevant quantum recoupling data.

**Dependencies:** AST-P024, AST-P028.

**Preserved acceptance criteria:**

- Fix braiding parameter, normalization and multiplicities.
- Verify small examples from the October2026 preprint before E8.
- Supply perturbative or analytic E8 certificates with an explicit order/error bound.

**Preserved claim boundary:** The recent paper proves specified smaller cases; its abstract is not an E8 proof.

**Next closure:** Construct half-braid matrices and verify the braid relation, central scalar and Tuba–Wenzl class before identifying an associator.

### AST-P030 — Level-restricted fusion separate from classical channels

**Preserved baseline state:** `research_target`.

**Preserved target:** Compute the channel survival and truncation at positive integral levels.

**Dependencies:** AST-P023.

**Preserved acceptance criteria:**

- Check integrability of external and intermediate highest weights.
- Reproduce the stable classical regime and low-level truncations.
- Keep level-one current descendants distinct from adjoint primary modules.

**Preserved claim boundary:** Classical tensor dimensions cannot be substituted for fusion coefficients at every level.

**Next closure:** Preserve the level-four fusion/tensor identification and compute the explicitly truncated fusion spaces at lower levels before claiming physical five-channel blocks there.

### AST-P031 — Balanced four-F-three recoupling arithmetic

**Preserved baseline state:** `exact_factorial_and4F3_seed_completed`.

**Preserved target:** Express the exact principal recoupling coefficients through terminating balanced hypergeometric sums.

**Dependencies:** AST-D003.

**Preserved acceptance criteria:**

- Crosscheck factorial and hypergeometric formulas over exact rationals.
- Record triangle and parity zero conditions.
- Handle normalization signs and square roots explicitly.

**Preserved claim boundary:** A formally written4F3 is not a verified recoupling coefficient.

**Next closure:** Extend the checked recoupling panels only with a stated exhaustive domain and convention-independent checks.

### AST-P032 — Jacobi equations with outside intermediate spins

**Preserved baseline state:** `listed_full_channel_panels_completed;global_system_target`.

**Preserved target:** Translate all principal bracket Jacobi identities into a complete recoupling system.

**Dependencies:** AST-P031, AST-D003.

**Preserved acceptance criteria:**

- Include every admissible tensor-product intermediate spin, including spins outside the eight E8 exponents.
- Distinguish zero Lie couplings from absent tensor channels.
- Check the recoupled identities against direct basis Jacobi.

**Preserved claim boundary:** Restricting all internal spin sums to the E8 exponent set can omit required relations.

**Next closure:** Use all admissible tensor channels in the complete Jacobi system; the current direct rank155/162 witness demonstrates that outside channels are essential.

### AST-P033 — Gauge and independent coupling coordinates

**Preserved baseline state:** `full_support_E8_connected_component_identified_with_gauge_torus`.

**Preserved target:** Recover all diagonal scales explicitly and identify the full-support connected component containing E8.

**Dependencies:** AST-D003, AST-P032.

**Preserved acceptance criteria:**

- Verify all eight self-channels are nonzero and recover their unique diagonal scales.
- Check all 170Laurent orbit equations and the exact global membership test.
- Combine literal Jacobi rank certificates with the closed Laurent graph to prove the full-support connected-component statement.
- Treat other components and zero-channel limits as distinct classification questions.

**Preserved claim boundary:** The component containing E8 is exactly the gauge torus, with trivial stabilizer. Other full-support components and zero-channel boundaries are not classified; the 68nonprincipal slots are not68 free moduli.

**Next closure:** Preserve the established full-support E8 gauge-torus component and separate all other components and zero-channel boundaries.

### AST-P034 — The polynomial Rees family

**Preserved baseline state:** `all_parameter_Rees_identity_completed`.

**Preserved target:** Turn the principal grading into a controlled flat degeneration.

**Dependencies:** AST-D003.

**Preserved acceptance criteria:**

- Show every exponent is nonnegative.
- Verify S_t|Vm=t^(m-1) identifies all nonzero fibers.
- Prove Jacobi over K[t] and record the boundary bracket.

**Preserved claim boundary:** An invertible single-valued scaling for t!=0 does not create monodromy.

**Next closure:** Retain the all-parameter polynomial proof and classify any additional contraction ray only within its declared weight cone.

### AST-P035 — Boundary nilpotence and exact invariant forms

**Preserved baseline state:** `class4_and_form_degeneracy_completed`.

**Preserved target:** Determine the complete structure of g0=sl2 semidirect n245 and its filtration.

**Dependencies:** AST-P034.

**Preserved acceptance criteria:**

- Certify16 surviving channels and 154 vanishing channels.
- Compute lower and derived central series, center and full derived algebra.
- Prove every invariant symmetric form has radical containing n245.

**Preserved claim boundary:** The boundary is not semisimple E8, and its invariant form is not nondegenerate.

**Next closure:** Preserve the exact class-four boundary, one-dimensional invariant-form space and structural proof; compute any additional boundary invariant explicitly.

### AST-P036 — Minimal quadratic completion in a three-dimensional gap

**Preserved baseline state:** `research_target`.

**Preserved target:** Determine the smallest quadratic Lie algebra containing the contracted boundary.

**Dependencies:** AST-P035.

**Preserved acceptance criteria:**

- Prove the lower bound from the 245-dimensional form radical.
- Construct or exclude embeddings in dimensions493,494,495.
- Retain the 496-dimensional cotangent double as a certified upper bound.

**Preserved claim boundary:** The cotangent double is canonical but is not proved minimal for an arbitrary embedding. If the embedded g0 is required isotropic,496 is the sharp lower bound.

**Next closure:** Classify the general quadratic completion minimum in 493..496;496 is already minimal only for an isotropic embedding.

### AST-P037 — Affine currents across metric degeneration

**Preserved baseline state:** `research_target`.

**Preserved target:** Study which central extensions survive the Rees boundary and which require the double.

**Dependencies:** AST-P010, AST-P035, AST-P036.

**Preserved acceptance criteria:**

- Track a polynomial or rational family of invariant forms with exact pole orders.
- Verify cocycle identities at t=0.
- Distinguish a degenerate central extension from a nondegenerate Sugawara construction.

**Preserved claim boundary:** A boundary Lie law can remain valid when the usual inverse-metric stress tensor fails.

**Next closure:** Verify how the chosen current central cocycle behaves under the degenerate boundary form; do not invert the lost metric.

### AST-P038 — Boundary deformation cohomology and smoothing

**Preserved baseline state:** `research_target`.

**Preserved target:** Compute selected equivariant deformation spaces of g0 and determine which directions restore E8.

**Dependencies:** AST-P034, AST-P035.

**Preserved acceptance criteria:**

- Exploit block decomposition before allocating matrices.
- Separate coordinate gauge from genuine boundary deformations.
- Compute second-order obstructions and identify the known Rees smoothing direction.

**Preserved claim boundary:** Whitehead rigidity of semisimple E8 does not imply rigidity of the nonsemisimple boundary.

**Next closure:** Choose a boundary representation or cohomology problem and provide an exhaustive finite or structural certificate for it.

### AST-P039 — Principal sl2 obstruction for the standard Drinfeld-Jimbo cobracket

**Preserved baseline state:** `explicit_obstruction_completed`.

**Preserved target:** Certify the failure of the classical principal subalgebra to be a standard bialgebra subalgebra.

**Dependencies:** AST-D001, AST-D003.

**Preserved acceptance criteria:**

- Compute an exact quotient-space witness.
- Check normalization factors independently.
- Record which coproduct requirement fails before proposing q-couplings.

**Preserved claim boundary:** A principal Lie subalgebra need not inherit the standard bialgebra structure.

**Next closure:** Solve a declared twist/coideal compatibility problem beyond the existing standard-principal bialgebra obstruction.

### AST-P040 — Twists that might repair the principal obstruction

**Preserved baseline state:** `research_target`.

**Preserved target:** Search a stated ansatz of classical twists or coideal structures instead of replacing integers by q-numbers blindly.

**Dependencies:** AST-P039.

**Preserved acceptance criteria:**

- Solve the principal compatibility condition in a finite equivariant ansatz.
- Check the twist Maurer-Cartan/CYBE equation.
- Return an obstruction or a valid first-order object before quantization.

**Preserved claim boundary:** Solving the linear compatibility equation alone does not establish a quantum subgroup or all-order twist.

**Next closure:** Compute the twist obstruction equations and state whether the twist lives inside the principal image or the larger E8 algebra.

### AST-P041 — Quantum adjoint arithmetic with a declared ambient algebra

**Preserved baseline state:** `research_target`.

**Preserved target:** Implement a quantum Lie or enveloping presentation consistent with coproduct and braiding.

**Dependencies:** AST-P039, AST-P040.

**Preserved acceptance criteria:**

- Fix a published quantum convention and integral form.
- Verify quantum Serre and coproduct identities in a declared range.
- Check the hbar->0 limit against the 170 classical couplings.

**Preserved claim boundary:** Existing quantum Lie-algebra existence results retain attribution; new code is not a new existence theorem.

**Next closure:** Provide the actual ambient quantum algebra, coproduct and module specialization at the selected parameter.

### AST-P042 — Moyal color closure in the enveloping algebra

**Preserved baseline state:** `finite_color_closure_obstruction_completed`.

**Preserved target:** Retain the symmetric color products forced by the scalar star commutator.

**Dependencies:** AST-P041.

**Preserved acceptance criteria:**

- Exhibit a finite explicit closure obstruction in248 color directions.
- Use Sym 2(248)=1+3875+27000 to track added sectors.
- Construct a PBW-filtered U(e8)-valued star algebra and replay associativity/Jacobi to a stated order.

**Preserved claim boundary:** The 248-dimensional Lie color space is not closed under general Moyal multiplication.

**Next closure:** Retain the Sym² color obstruction and supply a closed enlarged enveloping/matrix target if a star product is claimed.

### AST-P043 — Polynomial-degree escape from the eight binary forms

**Preserved baseline state:** `finite_polynomial_escape_obstruction_completed`.

**Preserved target:** Measure the unavoidable closure growth of star products on high principal blocks.

**Dependencies:** AST-D003, AST-P042.

**Preserved acceptance criteria:**

- Verify the leading coefficient and degree 114 exactly.
- Classify the required enlarged polynomial spaces by order.
- Compare an honest filtered closure with a truncated projection counterexample.

**Preserved claim boundary:** Dropping the degree 114 term is a model truncation, not an exact closed E8 star bracket.

**Next closure:** Bound polynomial degree growth or prove Jacobi for the chosen truncation; the ordinary Moyal escape remains a real obstruction.

### AST-P044 — Rank-eight dynamical elliptic transport

**Preserved baseline state:** `research_target`.

**Preserved target:** Use the all-type half-current or dynamical framework for an elliptic E8 extension.

**Dependencies:** AST-P023, AST-P041.

**Preserved acceptance criteria:**

- State the dynamical shifts and zero-weight condition.
- Verify the dynamical Yang-Baxter equation in a controlled representation/order.
- Transport the classical bracket and Cartan data into Asterion coordinates.

**Preserved claim boundary:** The nondegenerate nondynamical Belavin-Drinfeld elliptic classification is typeA; it cannot simply be relabeled E8.

**Next closure:** Preserve the completed classical rank-eight dynamical tensor and full root/Fay reduction; construct an actual universal KZB realization or quantum exchange object as a separate gate.

### AST-P045 — Elliptic, trigonometric and rational limit certificates

**Preserved baseline state:** `research_target`.

**Preserved target:** Make the deformation limits of the chosen elliptic object explicit.

**Dependencies:** AST-P044.

**Preserved acceptance criteria:**

- Specify the order of limits and renormalizations.
- Prove convergence or formal degeneration in the declared topology.
- Check the resulting residues and coproduct against the intended rational/trigonometric models.

**Preserved claim boundary:** Names of limits do not guarantee commuting limits or preservation of every finite-sector basis.

**Next closure:** Prove the limiting maps, rescalings and convergence domain rather than comparing finitely many formal coefficients.

### AST-P046 — Toroidal E8 with its correct center and two directions

**Preserved baseline state:** `research_target`.

**Preserved target:** Implement finite queries in an actual two-loop or elliptic toroidal algebra.

**Dependencies:** AST-P010, AST-P044.

**Preserved acceptance criteria:**

- Retain both loop degrees and the appropriate central differential classes.
- Check horizontal and vertical affine embeddings.
- Use bounded queries without pretending the infinite algebra is a finite248-vector object.

**Preserved claim boundary:** Existing all-type elliptic toroidal constructions are prior art, not a new E8 invention.

**Next closure:** Specify the central differential classes and two loop directions, then verify the declared toroidal relations and module.

### AST-P047 — A concrete nonformal differential graded source

**Preserved baseline state:** `research_target`.

**Preserved target:** Build a genuine dg current algebra with nonzero differential and finite nilpotent current degree.

**Dependencies:** AST-P011, AST-D001.

**Preserved acceptance criteria:**

- Verify d2=0, graded Jacobi and the derivation law.
- Compute the finite cohomology model and graded signs.
- Use the nonformal source to test whether a transferred ternary operation actually survives.

**Preserved claim boundary:** This is a proposed nonformal extension; a strict dg demonstration with vanishing higher brackets does not already realize it.

**Next closure:** Construct the proposed nonformal finite dg source and contraction; the formal current-form seed is not that source.

### AST-P048 — Explicit contraction data before any higher bracket

**Preserved baseline state:** `strict_DGA_seed_completed;nonformal_contraction_target`.

**Preserved target:** Construct and verify inclusion, projection and homotopy for the selected dg source.

**Dependencies:** AST-P047.

**Preserved acceptance criteria:**

- Check every chain-map and side-condition identity.
- Record degree conventions and signs.
- Reject purported contractions of a proper subspace of an ordinary d=0 Lie algebra.

**Preserved claim boundary:** When d=0 the identity forces ip=1; a nontrivial projection is not an honest contraction.

**Next closure:** Verify every contraction identity and then compute a nonzero transferred higher bracket if nonformality is claimed.

### AST-P049 — Transferred binary and ternary operations

**Preserved baseline state:** `research_target`.

**Preserved target:** Compute the rooted-tree operations and their first homotopy-Jacobi identities.

**Dependencies:** AST-P048.

**Preserved acceptance criteria:**

- Evaluate all required graded permutations.
- Verify arity3 andarity4 identities exactly.
- Distinguish a nonzero ternary operation from a strict transferred Lie bracket.

**Preserved claim boundary:** An arbitrary projected Jacobi defect is not automatically an L-infinity ternary bracket.

**Next closure:** Provide exact rooted-tree operations and the required L-infinity identities through a stated arity or an all-order theorem.

### AST-P050 — Finite current degree as a tree-order bound

**Preserved baseline state:** `research_target`.

**Preserved target:** Use positive current powers to bound which transferred arities can contribute.

**Dependencies:** AST-P047, AST-P049.

**Preserved acceptance criteria:**

- Prove the nilpotent ideal bound.
- Enumerate all surviving rooted trees at the selected N.
- Verify the complete finite set of identities allowed by that bound.

**Preserved claim boundary:** A cutoff by numerical size or omitted arity is not an algebraic nilpotence certificate.

**Next closure:** Prove the current-order bound for the actual transferred trees and explain whether the chosen differential preserves the filtration.

### AST-P051 — BRST or BV extension with an actual differential

**Preserved baseline state:** `research_target`.

**Preserved target:** Extend the source only after specifying ghosts, grading, differential and invariant pairing.

**Dependencies:** AST-P036, AST-P048.

**Preserved acceptance criteria:**

- Write the full finite generator differential.
- Verify nilpotence and pairing compatibility.
- Identify the precise cohomology or reduction being claimed.

**Preserved claim boundary:** Invoking BV, BRST or derived language without those data adds no theorem.

**Next closure:** State the BRST/BV complex and pairing explicitly and verify its square-zero and master-equation claims.

### AST-P052 — Projected Lie operations versus genuine quotients

**Preserved baseline state:** `research_target`.

**Preserved target:** Classify when a selected sector set forms a subalgebra, quotient or only an approximate projection.

**Dependencies:** AST-P011, AST-P032, AST-P048.

**Preserved acceptance criteria:**

- Return a concrete nonclosure or Jacobi witness when closure fails.
- For quotients, prove the kernel is an ideal.
- For transfer, produce the complete dg contraction rather than only a projection.

**Preserved claim boundary:** The three constructions have different hypotheses and cannot substitute for one another.

**Next closure:** Check whether a proposed projection kernel is a Lie ideal or retain its explicit projected Jacobi defect; genuine transferred higher operations require an actual dg contraction.

### AST-P053 — Compatibility of contraction, current extension and transport

**Preserved baseline state:** `research_target`.

**Preserved target:** Determine which constructions commute and exhibit failures when the invariant form degenerates.

**Dependencies:** AST-P034, AST-P037.

**Preserved acceptance criteria:**

- Build an explicit commuting diagram of bracket maps.
- Track central generators and form rescalings.
- Retain a counterexample whenever the order of constructions changes the result.

**Preserved claim boundary:** An isomorphism of nonzero fibers does not identify all boundary central extensions.

**Next closure:** Give explicit commuting maps for the current/Rees construction and retain a counterexample when extension orders differ.

### AST-P054 — Independent proof certificates and selective formalization

**Preserved baseline state:** `research_target`.

**Preserved target:** Choose small complete certificates that can be replayed outside the generating engine.

**Dependencies:** AST-D001, AST-D003, AST-D005, AST-P032.

**Preserved acceptance criteria:**

- Specify a minimal trusted checker and exact input schema.
- Replay corrupted and valid data independently.
- Formalize only clearly stated finite theorems and maintain the boundary to unformalized source construction.

**Preserved claim boundary:** A hash proves byte identity, not mathematical correctness; Python replay is not Lean verification.

**Next closure:** Export independent checkers and negative/corruption fixtures for new statements; byte hashes do not replace mathematical checks.

### AST-P055 — Genus-one KZB and finite-grade modular data

**Preserved baseline state:** `research_target`.

**Preserved target:** Extend the connection problem to elliptic moduli while preserving the actual rank-eight Cartan dependence.

**Dependencies:** AST-P028, AST-P044.

**Preserved acceptance criteria:**

- State the chosen KZB construction and representation category.
- Check compatibility of z andtau directions.
- Compute a bounded certified modular/monodromy comparison with the finite-grade characters.

**Preserved claim boundary:** A matching eta quotient and a KZ residue denominator do not prove a genus-one correspondence.

**Next closure:** Construct the rank-eight modular KZB connection and compare its actual monodromy/characters; scalar period cancellation is insufficient.

### AST-P056 — Squarefree eta arithmetic as a separately certified bridge

**Preserved baseline state:** `research_target`.

**Preserved target:** Apply exact cusp-order and Eisenstein methods only to eta products genuinely arising from the current characters.

**Dependencies:** AST-P013, AST-P014.

**Preserved acceptance criteria:**

- Compute levels, weights, characters and all cusp orders.
- Use a justified Sturm bound for any claimed identity.
- Compare divisor-cube/Walsh formulas at squarefree levels without inferring a Lie correspondence from shared primes.

**Preserved claim boundary:** The 2026 eta-unit paper supplies arithmetic tools; its existence does not identify conductor31, level 5 and E8 automatically.

**Next closure:** Use the proved level-five eta identity and a declared arithmetic object; no conductor31 identification is inferred from shared notation.

### AST-P057 — Full rational cone and integral ray generators

**Preserved baseline state:** `finite_low_cube_censuses_completed;full_cone_target`.

**Preserved target:** Determine the extreme rays, Hilbert basis and face lattice of all principal diagonal contractions.

**Dependencies:** AST-P034.

**Preserved acceptance criteria:**

- Certify a complete polyhedral description and pointed dimension 7.
- Compute exact extreme-ray and integral-generator certificates.
- Check each proposed face against all 170 inequalities.

**Preserved claim boundary:** The binary and ternary box enumerations do not describe all rays or lattice points.

**Next closure:** Compute and certify the full extreme-ray/Hilbert-basis/face data, beyond the existing exact low-box censuses.

### AST-P058 — Boundary strata beyond the low cubes

**Preserved baseline state:** `research_target`.

**Preserved target:** Enumerate support patterns, nilpotence and invariant-form ranks across higher contraction strata.

**Dependencies:** AST-P057, AST-P035.

**Preserved acceptance criteria:**

- Reproduce the 128- and 2187-point exact censuses.
- Classify which leading channels survive on every selected face.
- Extend to higher boxes with coverage certificates, not extrapolated counts.

**Preserved claim boundary:** The 126 two-step radicals in the ternary cube do not imply every nonzero contraction is two-step.

**Next closure:** Record all surviving channels and structural invariants for each selected contraction stratum, with a coverage domain.

### AST-P059 — Isomorphism classes of diagonal contraction limits

**Preserved baseline state:** `research_target`.

**Preserved target:** Separate different weight vectors that yield isomorphic limits from genuinely different Lie algebras.

**Dependencies:** AST-P057, AST-P058.

**Preserved acceptance criteria:**

- Compute centers, derived series and Levi/radical structure as invariants.
- Construct explicit isomorphisms for identified classes.
- Use a stated complete parameter domain before claiming classification.

**Preserved claim boundary:** Coincident dimensions or support counts alone do not prove Lie-algebra isomorphism.

**Next closure:** Prove explicit Lie-isomorphism or nonisomorphism statements between contraction limits rather than matching dimensions.

### AST-P060 — Poisson invariants of the class-four boundary

**Preserved baseline state:** `research_target`.

**Preserved target:** Use the concrete semidirect product to study coadjoint stabilizers and polynomial Casimirs.

**Dependencies:** AST-P035.

**Preserved acceptance criteria:**

- Compute exact generic coadjoint rank with a specialization certificate and symbolic upper bound.
- Find and verify invariant polynomials.
- Prove algebraic independence and separate complete generators from a finite list.

**Preserved claim boundary:** A rank-three invariant bilinear form does not determine the full coadjoint index or Poisson center.

**Next closure:** Certify generic coadjoint rank with a symbolic upper bound and a specialization witness, then prove any proposed Casimir generators.

### AST-P061 — Thirty explicit neutral Cartan-conformal relations

**Preserved baseline state:** `explicit_states_and_rank_certificates_implemented`.

**Preserved target:** Exploit the 31 orthogonal Cartans to expose a concrete part of the neutral quadratic nullspace.

**Dependencies:** AST-D006, AST-P016.

**Preserved acceptance criteria:**

- Retain all 31 universal states and 30 independent differences.
- Check neutral finite grade, rank 31 and difference rank 30 exactly.
- Prove simple-quotient nullity using Cartan conjugacy and the lattice conformal vector.

**Preserved claim boundary:** These30 relations do not exhaust the 216-dimensional neutral quadratic nullspace.

**Next closure:** Retain all 31 states and 30 independent neutral nulls; identify the remaining 186 neutral quadratic nulls only with actual vectors.

### AST-P062 — Equivariant tangent rigidity without a dense Jacobi matrix

**Preserved baseline state:** `literal_Jacobi_ranks155_and162_completed;local_smoothness_derived`.

**Preserved target:** Identify the complete principal-equivariant tangent kernel with selected literal Jacobi rows and exact global gauge directions.

**Dependencies:** AST-D003, AST-P033.

**Preserved acceptance criteria:**

- Verify the 170x8 and 162x7 gauge matrices and left inverses.
- Replay 155 independent nonprincipal Jacobi rows and the 7principal-only augmentation rows, with ranks 155and162.
- Prove the matching rank upper bounds from basis-change gauge identities.
- Derive local smoothness and locally open gauge orbits from equality of tangent and orbit dimensions.

**Preserved claim boundary:** Literal rank certificates prove local smoothness and, with scale recovery, the E8 full-support gauge-torus component. Other components, singular boundary points and integral or quantum models remain outside the result.

**Next closure:** Retain the direct literal-row ranks155/162 and global self-channel scale inverse; other components are a separate classification.

### AST-P063 — Integral meaning of the cancelled Sugawara denominator

**Preserved baseline state:** `research_target`.

**Preserved target:** Determine which integral or localized VOA forms support the Cartan-conformal cancellation at the prime 31.

**Dependencies:** AST-P061.

**Preserved acceptance criteria:**

- Choose an integral VOA form and prove torsion properties.
- Check reduction or localization at 31 without dividing by31 silently.
- Separate the characteristic-zero relation from a genuine mod 31 theorem.

**Preserved claim boundary:** Cancellation in the complex quotient is not automatically an integral mod 31 VOA construction.

**Next closure:** Choose and control an integral VOA form and torsion at 31 before interpreting characteristic-zero denominator cancellation modulo31.

### AST-P064 — Elliptic period cancellation with a declared connection comparison

**Preserved baseline state:** `classical_finite_series_adapter_completed;KZ_comparison_target`.

**Preserved target:** Preserve the exact classical character-period adapter and formulate any comparison with the five-channel connection as a separate map.

**Dependencies:** AST-D032, AST-P028, AST-P055.

**Preserved acceptance criteria:**

- Replay the exact theta, lambda and hypergeometric compositions with the Q versus q nome convention.
- Keep two guard orders when cancelling the cusp poles and distinguish vacuum-normalized Z from physical chi.
- For any proposed KZ or genus-one bridge, specify the map, normalization, differential equations and monodromy compatibility.

**Preserved claim boundary:** The finite classical identities are implemented. They do not identify a scalar elliptic period with the five-channel E8 KZ system or prove a link among level 5, prime 31 and Coxeter order30.

**Next closure:** Preserve the exact nome convention and classical finite-series adapter; construct a map of differential systems for any KZ-period comparison.

## 7. Weight-six generator closure (post-v0.19 update)

The receipt `results/asterion-frontiers/primitives.json` and
[ASTERION_PRIMITIVES.md](ASTERION_PRIMITIVES.md) close the next-closure items
recorded for AST-P018 through weight six. The preserved gate texts above are
unchanged; the ledger records the new states inside each `frontier_update`
field as `primitives_update`.

| Gate | Closed item | Certificate |
|---|---|---|
| AST-P018 | Weight-five 248 and 147250 representatives, affine null lifts and nonmembership | lattice V_L null criterion; highest-vector and full-weight-space ranks |
| AST-P018 | Exact Li2/Li3 allocation of K6 | product functionals on length four; total character; direct length-three sectors |
| AST-P018 | Minimal differential generators through weight six | 3875 (w4); 248, 147250 (w5); 30380 (w6) |
| AST-P018 | Individual gr image of F0 | zero; F0=c·x^[0]-contraction of P₂₄₈ modulo the ideal |
| AST-P019 | First syzygies through weight six | g[0]F_Q=0 and x^[0]DF_Q=−x^[1]F_Q, replayed as dual-functional values 63 and −63 |
| AST-P020 | Explicit primitive modules for grade transport | P₂₄₈, P₁₄₇₂₅₀ and P₃₀₃₈₀ in Chevalley coordinates; Jordan transport not attempted |

Still open: the weight-seven length-four Li-degree-three character and
kernel; the weight-seven length-three sectors of types 248 and 1; the complete syzygy module; and any all-weight or finite-generation
theorem.

## Change control

Proposed additions and status changes are prepared separately in [asterion_frontier_ledger_proposals.json](asterion_frontier_ledger_proposals.json). They must cite frozen numerical receipts before merger. The preserved 64-gate snapshot remains a historical baseline even when the main ledger later adopts a narrower completed theorem or a new gate.
