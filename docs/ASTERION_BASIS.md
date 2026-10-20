# Asterion basis calculus

Asterion is the name introduced by this project for a **certified prescription for choosing, transporting and evaluating a Lie-algebra basis**. Its elements are written \(\mathsf A_{\sigma, j}\). The label \(\sigma\) records a seed, sector or commutator word; \(j\) records a position within its explicitly defined family. The name does not assert a new complex simple Lie algebra, a new classification, or historical priority for principal triples, Coxeter bases or Jordan gradings. The mathematical object delivered by a run is a concrete basis with a reproducible construction and an independently checkable multiplication law. A collection of alternative coordinate charts is not itself one basis: each chart must have the full declared rank, and a basis compiled from mixed candidates must undergo its own rank and transport checks.

The program's distinct prescription begins with ordered seeds and permitted operations, generates candidate commutator words, retains candidates by exact independent-column selection, and optionally improves a declared arithmetic cost through reversible integral basis moves. The prescribed E8 **Asterion response basis** now exists concretely: eight seeds e_i+f_i and sixteen ordered simple-root probes produce 248 integral vectors with determinant-1. It therefore supplies a new explicit mixed basis of the same Chevalley integer lattice, not merely a proposed name for a future construction. It carries the chosen field, sign conventions, seed normalization, basis matrix, inverse, bracket law, workload and evidence together. The E8 root, principal-polynomial, Coxeter and two-component polynomial constructions supply different candidate families and independent ways to replay the same algebra. They retain their established mathematical attribution. A change in the name of a vector is not the research contribution; a short explicit multiplication law, a rigorously controlled lattice, or a demonstrable arithmetic advantage can be.

## 1. The object being designed

Let \(\mathfrak g\) be a Lie algebra over a characteristic-zero field \(K\), with reference basis \(e_1,\ldots, e_n\) and structure constants \([e_i, e_j]=\sum_k c_{ij}^{k}e_k\). A basis specification includes an invertible column matrix \(S\), with \(\mathsf A_a=\sum_iS_{ia}e_i\). Coordinate conversion is \(x_e=Sx_{\mathsf A}\), and the transported bracket is

\[
[x,y]_{\mathsf A}=S^{-1}[Sx,Sy]_e,
\qquad
c'{}_{ab}^{d}=\sum_{i, j, k}S_{ia}S_{jb}c_{ij}^{k}(S^{-1})_{dk}.
\]

The certificate checks both products \(SS^{-1}\) and \(S^{-1}S\), as well as every bracket-intertwining identity claimed in its declared scope. This equation proves skew symmetry and Jacobi in the new coordinates whenever they hold in the reference algebra. Conversely, a correct-looking coordinate matrix does not validate an incorrect reference bracket. The run therefore records how the reference law was constructed and which independent checks were performed. Rational arithmetic is exact arithmetic, but the words “exact” and “exhaustive” describe different properties of a check.

A Lie automorphism is a special invertible map that preserves the bracket. An arbitrary basis change is allowed and generally changes the displayed tensor. The algebra's dimension, rank and abstract isomorphism type do not change. For E8, the 240 roots live in an eight-dimensional root space, while the Lie algebra has 248 independent directions. Each full E8 chart in this program has 248 vectors. Eight binary forms still contain 248 independent coefficients; a short list of orbit seeds specifies many vectors but does not lower that dimension.

When the reference integer lattice is part of the contract, \(S\in\mathrm{GL}_n(\mathbb Z)\) is a sufficient same-lattice certificate. A column shear \(S\mapsto S(I+kE_{ij})\), with \(i\ne j\) and \(k\in\mathbb Z\), has inverse update \((I-kE_{ij})S^{-1}\). Every finite sequence of these moves is reversible and unimodular. A rational matrix of full rank proves a vector-space basis; it does not prove equality with the Chevalley lattice. The compiler keeps denominator and lattice questions separate from rank.

## 2. An exact E8 reference law

Fix an ordered E8 Cartan matrix \(A\), with diagonal entries2 and adjacent entries-1. Roots are represented by integer coefficient columns in the simple roots. The complete root set is \(\Phi=\{\alpha\in\mathbb Z^8:\alpha^TA\alpha=2\}\), containing 240 roots. Simple reflection \(s_i\) sends \(\alpha\) to \(\alpha-(A\alpha)_ie_i\). Starting from simple roots and their negatives, repeated reflections enumerate the finite system; termination, cardinality, norms and reflection closure are all available as replayable checks. The reference vector-space slots consist of eight Cartan vectors followed by the ordered root vectors.

The sign rule starts from the triangular lattice cocycle

\[
\varepsilon(\alpha,\beta)=(-1)^{\sum_i\alpha_i\beta_i+\sum_{i>j}\alpha_iA_{ij}\beta_j}.
\]

Set \(s_\alpha=1\) for positive roots and \(s_\alpha=-1\) for negative roots. With the corresponding gauge, the nonopposite root-addition bracket is

\[
[E_\alpha,E_\beta]
=\frac{s_\alpha s_\beta}{s_{\alpha+\beta}}
\varepsilon(\alpha,\beta)E_{\alpha+\beta}
\quad(\alpha+\beta\in\Phi).
\]

The remaining defining cases are \([H_i, H_j]=0\), \([H_i, E_\alpha]=(A\alpha)_iE_\alpha\), and \([E_\alpha, E_{-\alpha}]=\sum_i\alpha_iH_i\); a nonzero nonroot sum gives zero. In particular, the simple positive and negative vectors satisfy \([e_i, f_j]=\delta_{ij}H_i\). The particular ordering and gauge are part of the data. Root-lattice cocycle constructions and their relation to canonical Chevalley signs are established mathematics; Geck's 2026 paper is a modern primary reference [1]. This implementation provides a fixed convention against which the other coordinates can be checked.

A useful Jacobi replay writes the identity as a derivation equation, \(\operatorname{ad}_x[y, z]=[\operatorname{ad}_xy, z]+[y,\operatorname{ad}_xz]\). The concrete reference law now passes **all 2,511,496 unordered triples of distinct basis vectors**, in exact integer arithmetic. Verified skew symmetry handles repeated-index triples. This is complete basis coverage for this finite law. Smaller generator checks and deterministic panels remain explicitly distinguished from the full run. No Python receipt is represented as a new Lean theorem.

## 3. Coxeter coordinates and a finite difference kernel

For the fixed product order, form the Chevalley lift

\[
C=\prod_{i=1}^{8}\exp(\operatorname{ad}e_i)
\exp(-\operatorname{ad}f_i)\exp(\operatorname{ad}e_i).
\]

Each exponential is a finite sum on the adjoint representation. The order of a Weyl-group lift must be addressed rather than inferred from a picture of its roots. For E8 a Coxeter lift has order 30, as covered by the lifting results of Adams and He [2]. The actual signed action has been replayed: C^30 fixes all 248 basis vectors, and C preserves all 30,628 unordered basis brackets. The 240 root spaces form eight signed cycles of length30. Taking one vector \(u_i\) from each cycle gives \(u_{i, a}=C^au_i\), and the Cartan subspace supplies eight additional directions.

The rational module description is

\[
\mathfrak e_{8,\mathbb Q}\cong
\bigl(\mathbb Q[t]/(t^{30}-1)\bigr)^8
\oplus\mathbb Q[t]/\Phi_{30}(t),
\qquad tx=Cx.
\]

It is a module decomposition, not ordinary polynomial multiplication. In particular, \([tx, ty]=t[x, y]\) because \(t=C\) is an automorphism; a bilinear product over \(\mathbb Q[t]\) would instead produce \(t^2[x, y]\). The correct compact data are the difference kernels

\[
K_{ij}(d)=[u_i, C^du_j],
\qquad
[C^au_i,C^bu_j]=C^aK_{ij}(b-a).
\]

The actual \(8^2\cdot30=1920\) seed brackets have been computed and used to reconstruct **every one of the 57,600 ordered root brackets**, each checked against the direct cocycle law. This is a certified reduction in table redundancy. Wall-clock speed, conversion costs and coefficient growth are separate quantities. Coxeter-root bases themselves have established prior art [3].

Over a field containing \(\zeta_{30}\), Fourier sums \(F_{i, k}=\sum_a\zeta_{30}^{-ka}C^au_i\) satisfy \(CF_{i, k}=\zeta_{30}^kF_{i, k}\). The Cartan spectrum contributes one additional direction at each exponent \(1,7,11,13,17,19,23,29\). Thus \(\dim\mathfrak g_k=9\) for the eight primitive residues and 8 for the other22 residues, with \([\mathfrak g_k,\mathfrak g_l]\subseteq\mathfrak g_{k+l}\). The primitive sectors contain72 dimensions and the remaining sectors176. An eight-dimensional reflection-spectrum correspondence alone is not a reconstruction of the full Lie algebra.

## 4. Principal polynomial coordinates

Solve \(Ar=2\mathbf1\), and put \(e=\sum_i e_i\), \(h=\sum_ir_iH_i\), \(f=\sum_ir_if_i\). The simple-generator relations give \([h, e]=2e\), \([h, f]=-2f\), and \([e, f]=h\). For each E8 exponent \(m\) in

\[
M=\{1,7,11,13,17,19,23,29\},
\]

choose a highest vector \(z_m\in\ker\operatorname{ad}e\) of \(h\)-weight \(2m\). An executable normalization fixes a primitive integer representative with a stated sign, taking \(z_1=e\). Define

\[
\mathsf A_{m,j}=\frac{(\operatorname{ad}f)^jz_m}{j!},
\qquad0\le j\le2m.
\]

The three-term laws are \([h,\mathsf A_{m, j}]=(2m-2j)\mathsf A_{m, j}\), \([f,\mathsf A_{m, j}]=(j+1)\mathsf A_{m, j+1}\), and \([e,\mathsf A_{m, j}]=(2m-j+1)\mathsf A_{m, j-1}\), with out-of-range vectors zero. Each irreducible chain contributes one class to \(\mathfrak e_8/(\operatorname{ad}f)\mathfrak e_8\). Consequently exactly eight seeds are necessary and sufficient for generation under this fixed lowering operator. This is a statement about that operator, not a claim that eight vectors form a vector-space basis of E8.

Associate \(\mathsf A_{m, j}\) with \(\binom{2m}{j}x^{2m-j}y^j\). The eight polynomial degrees are2,14,22,26,34,38,46,58, with dimensions 3,15,23,27,35,39,47,59. The direct sum has dimension 248. Highest-vector equations and coordinate conversions can be solved separately at each height; the largest height slice is only eight-dimensional. This avoids treating basis inversion as an opaque dense248-by 248 operation.

For the unnormalized transvectant convention,

\[
T_r(P, Q)=\sum_{j=0}^r(-1)^j\binom rj
(\partial_x^{r-j}\partial_y^jP)
(\partial_x^j\partial_y^{r-j}Q),
\]

representation theory gives

\[
[P_a,Q_b]
=\sum_{\substack{c\in M\\|a-b|\le c\le a+b}}
\kappa_{ab}^{c}T_{a+b-c}(P_a,Q_b).
\]

Every admissible transvection order is odd because all E8 exponents are odd. To extract a scalar, let \(r=a+b-c\), bracket \(z_a\) with \(\mathsf A_{b, r}\), and read the \(z_c\) coordinate. Under the binomial convention, divide that coordinate by \((2a)_r(2b)_r\), where parentheses denote falling factorials. This provides a direct exact extraction formula, after the highest vectors and inverse basis have been fixed. All170 couplings have now been extracted, and every one is nonzero in the chosen normalization. The transvectant law agrees with the reference bracket on **all 30,876 unordered pairs including diagonals**. All744 raising, lowering and weight relations, and all 248 inverse columns, replay exactly. The principal block has coefficient \(1/2\) for \(T_1\) in this convention: \(e, h, f\) correspond to \(x^2,-2xy,-y^2\).

Enumerating unordered input pairs yields 170 possible channels. Organizing the invariant trilinear form through the Killing pairing yields 76 unordered triples \(a\le b\le c\le a+b\); eight involve exponent 1, leaving 68 nonprincipal slots before Jacobi and scale choices. The170 count initially describes permitted channels; the actual computation now finds all 170 nonzero. The76 and 68 counts organize trilinear possibilities and do not make those quantities freely adjustable parameters. Abdesselam and Thomas provide the modern transvectant construction and explicitly report only G2 calculations among exceptional types in their Section 6.3 [4]. The completed normalized E8 catalogue therefore extends those computations, without by itself establishing global novelty.

The arithmetic comparison is decisive. All displayed divided-chain vectors are integral in this fixed normalization, but their absolute basis determinant is

\[
2^{4380}3^{2177}5^{1020}7^{718}11^{484}13^{351}17^{289}19^{281}23^{207}29^{168}31^{68}37^{77}41^{58}43^{66}47^{35}53^{47}.
\]

Its numerator has 21,186 bits and denominator 1. The receipt stores the 59 exact height-block determinants, their prime factorization and a hash of the unsigned determinant bytes. The chain basis is therefore a basis over Q but **not a Z-basis of the Chevalley lattice**. Primitive rescaling of individual columns reduces the index and still leaves an index greater than 1. This explicit negative lattice result is retained alongside the successful polynomial bracket calculation.

## 5. Two-component polynomial coordinates modulo five

Let \(R=K[x, y, z]/(x^5-1, y^5-1, z^5-1)\), initially over a characteristic-zero field containing \(\zeta_5\). Write \(m_a=x^{a_1}y^{a_2}z^{a_3}\) for \(a\in\mathbb F_5^3\). Set

\[
W=\operatorname{span}_K\{m_a:a\ne0\},
\qquad V=K^2\otimes W,
\qquad\dim V=2(125-1)=248.
\]

The space W is the nonconstant monomial subspace. It is not the augmentation ideal, whose familiar basis would use \(m_a-1\), and it is not closed under ordinary polynomial multiplication. The Lie law is specified separately by bilinear two-component maps:

\[
[u[a],v[b]]=\beta_{a,b}(u,v)[a+b].
\]

The zero degree is absent. In the Jordan model, all brackets between collinear degrees vanish. Any remaining basis bracket has at most two output coordinates, whose label is found by addition in \(\mathbb F_5^3\). The finite-field labels do not place the Lie coefficients in characteristic five.

The implementation starts from the explicit two-A4 exterior construction. For five-dimensional spaces V and W,

\[
L_0=\mathfrak{sl}(V)\oplus\mathfrak{sl}(W),
\qquad
L_i=\Lambda^iV\otimes\Lambda^{[2i]_5}W\quad(1\le i\le4),
\]

where \([2i]_5\) is represented in 1,2,3,4. Its dimensions are48 followed by four 50-dimensional spaces. Exterior multiplication, contraction and the trace-dual endomorphism products specify the bracket with the source's fixed normalization. Cabrera, Draper and Garvín give this explicit construction and identify the doubled twisted \(\mathbb Z_5^3\) presentation as a research direction [5]. The program now extracts and certifies concrete polynomial coordinates and their entire kernel catalogue from that algebra. No unconstrained248-dimensional bracket ansatz is substituted for the source construction.

Let \(De_j=\zeta_5^je_j\) and \(Pe_j=e_{j+1}\), so \(DP=\zeta_5PD\). On the two five-dimensional spaces use clocks D and \(D^2\), with the common cyclic shift P. In exterior degree \((i,[2i]_5)\), the commutation phase is \(\zeta_5^{i+2[2i]_5}=1\). Their induced automorphisms therefore commute on L, together with the order-five automorphism acting by \(\zeta_5^i\) on \(L_i\). For the resulting action \(\sigma_s\), the exact simultaneous projector is

\[
P_a=\frac1{125}\sum_{s\in\mathbb F_5^3}
\zeta_5^{-a\cdot s}\sigma_s.
\]

Each nonzero homogeneous component has dimension 2 and the zero component vanishes. Ordered exact pivot selection supplies two vectors per component and hence a full248-vector basis. All248 basis columns undergo an inverse roundtrip, and each satisfies the three specified eigenconditions. The concrete grade kernels are checked against the exterior-model bracket, coefficient by coefficient. The uniform two-dimensional grading is established and unique up to equivalence by Elduque [6]. A new polynomial expression must retain that attribution.

Each one-dimensional \(\mathbb F_5\)-subspace \(\ell\) contains four nonzero degrees. In the established grading, \(H_\ell=\bigoplus_{a\in\ell\setminus\{0\}}L_a\) is an eight-dimensional Cartan subalgebra. There are 31 such lines, yielding pairwise Killing-orthogonal Cartans. A degree has 120 noncollinear partners; hence there are \(124\cdot120/2=7440\) unordered independent degree pairs. Each map \(K^2\otimes K^2\to K^2\) has eight scalar slots, so the raw catalogue permits 59520 coefficients before symmetries and gauge reductions. The complete actual census contains **7,440 maps,29,760 independent-grade basis brackets,34,080 nonzero scalar output entries, and 50 distinct nonzero cyclotomic coefficients**. Every coefficient has denominator 1 in the power basis 1, zeta5, zeta5^2, zeta5^3, with every integer entry of magnitude at most 2. These are measured counts of the displayed kernel catalogue, not just permitted-slot bounds. They do not imply a sparsity advantage over a Chevalley root basis.

Skew symmetry and Jacobi become explicit local equations:

\[
\beta_{a,b}(u,v)=-\beta_{b,a}(v,u),
\]

\[
\beta_{a+b,c}(\beta_{a,b}(u,v),w)
+\beta_{b+c, a}(\beta_{b, c}(v, w), u)
+\beta_{c+a, b}(\beta_{c, a}(w, u), v)=0,
\]

where zero-degree terms are zero. The actual kernel also passes a direct exhaustive Jacobi replay on **all 2,511,496 unordered triples of distinct basis labels**. The checker uses integer power-basis arithmetic reduced modulo Phi5, with no numerical tolerance or modular-prime inference. Verified skew symmetry supplies repeated-index cases. Separately, all 868 pairs inside the 31 Cartan blocks commute in the ambient model. The Cartan conclusion also has a computational certificate:3,720 exact rank-two minors exclude every outside-grade normalizer direction. Each abelian block is therefore self-normalizing of dimension 8, proving it is a Cartan subalgebra rather than relying only on an eight-dimensional commuting count. The grading supplies the mutual Killing-orthogonality argument. Timings belong to the execution receipt and its host; the mathematical certificate is the exact finite identity replay.

## 6. A necessary internal twist

There is a sharp obstruction to the simplest possible symmetry proposal. Suppose every \(g\in SL_3(\mathbb F_5)\) acts by \(u[a]\mapsto u[ga]\), leaving the internal two-dimensional vector unchanged, and suppose collinear brackets vanish. The group is transitive on ordered independent pairs. Equivariance therefore forces all \(\beta_{a, b}\) for independent a, b to equal one map \(\beta\). A determinant-one transformation can swap a and b by also negating a complementary basis vector. Skew symmetry then makes \(\beta\) alternating. It factors through \(\Lambda^2K^2\), so its image has dimension at most 1. Thus \([V, V]\) occupies at most one direction per nonzero degree and has dimension at most 124. This contradicts \([\mathfrak e_8,\mathfrak e_8]=\mathfrak e_8\) of dimension 248.

A compatible large symmetry must consequently act inside the fibers. Its local condition is

\[
T_g(a+b)\beta_{a, b}(u, v)
=\beta_{ga, gb}(T_g(a)u, T_g(b)v).
\]

Composition laws for these maps must also be checked; a nonsplit normalizer extension need not supply a globally chosen split action. The obstruction above is a necessary design constraint. It does not construct all internal maps, prove that a proposed family satisfies Jacobi, or classify every twist.

## 7. What the numerical program must record

Exact root, principal and polynomial kernels expose different arithmetic costs. Root brackets are already extremely sparse and have small integral constants. Principal coordinates organize the law into a small collection of intertwiners but can enlarge rational coefficients. Fifth-cyclotomic coordinates make finite symmetry and two-output locality explicit but introduce a number field and projector denominators. Any comparison must include input density, conversion, coefficient bit lengths, caching and the exact requested operation. A compact table is not automatically a fast implementation for arbitrary dense input.

The compiler's deterministic word order makes a run reproducible. Exact column selection records a spanning witness or a failure to reach full rank. Optional unimodular shears change the basis without changing the lattice; their accepted cost changes are retained with the evaluated workload. Bounded local improvement is reported as bounded local improvement. A proof of global optimality requires a complete search space and a certificate that every competitor was covered.

For a fifth-cyclotomic basis, Fourier projectors introduce \(\zeta_5\) and powers-of-five denominators. A full-rank coordinate chart over \(\mathbb Q(\zeta_5)\) does not establish rational descent, the same integral Chevalley form, or good reduction at 5. The complete coefficient census does prove something stronger than a field-only construction: the 248 displayed basis vectors span a **closed free rank 248 Lie lattice over Z[zeta5]**. Since Z[zeta5] has rank 4 over Z, that object has Z-rank 992. It has not been identified with the rank 248 Chevalley Z-lattice. Rational descent and equality with a specified integral Chevalley form remain separate targets. Likewise, a new formula for E8's bracket is a new presentation of the existing complex algebra. Scalar symmetric cocycle twists over an algebraically closed field can reduce to basis rescaling, as explained in the source construction [5].

The replayable evidence in `results/asterion/` includes ordered roots and signs, highest seeds, basis conversion maps, every extracted scalar coupling, homogeneous kernel maps, determinant or rank information, field arithmetic conventions and the check scope. Compressed complete tables and their manifest retain the actual finite data rather than only aggregate counts. Negative tests should corrupt a sign, inverse, coefficient or rank claim and verify rejection. The equation namespace PJ-A001 onward adds this material without changing the meanings of the archived PJ-E records. Family25 is an appended catalogue family; the ordinal is a registry placement, not a proof that this machinery is weaker or stronger than the preceding families.

## 8. Beyond coordinates: gauge, deformation and obstruction

To distinguish a new basis from a change in the algebra, write an alternating bracket family as \(\mu_t=\mu+t\phi+t^2\psi+\cdots\). An infinitesimal basis change \(S=I+tF\) produces the first-order term

\[
d_1F(x, y)=[x, Fy]+[Fx, y]-F[x, y].
\]

This is tangent to the coordinate-change orbit. The linearized Jacobi operator is

\[
d_2\phi(x, y, z)=\sum_{\mathrm{cyclic}}\bigl([x,\phi(y, z)]+\phi(x,[y, z])\bigr).
\]

Because the reference bracket satisfies Jacobi, \(d_2d_1=0\). Infinitesimal bracket changes satisfy \(d_2\phi=0\), while pure coordinate changes lie in \(\operatorname{im}d_1\). The quotient \(H^2(\mathfrak g,\mathfrak g)=\ker d_2/\operatorname{im}d_1\) identifies first-order directions after removing basis gauge. This is classical deformation theory [7]. Whitehead's second lemma makes this group vanish for semisimple characteristic-zero Lie algebras with finite-dimensional adjoint coefficients [8]. It does not prevent useful new presentations, different integral forms, contractions or structures outside those hypotheses.

The bounded exact implementation forms these matrices only for declared small dimensions. Its sl2 example has \(\operatorname{rank}d_1=6\), \(\operatorname{rank}d_2=3\), \(\dim H^2=0\), and a three-dimensional derivation space. For the abelian three-dimensional algebra both differentials vanish and \(\dim H^2=3\binom32=9\); the Heisenberg example yields 5, and the six-dimensional direct sum sl2+sl2 yields 0. The E8 sizes are reported before allocation: its alternating two-cochain space has 7595744 coordinates and its three-cochain space has 622851008. A replay of small examples is not a full E8 cohomology calculation.

A first-order cocycle need not extend. At second order Jacobi requires

\[
d_2\psi=-J_\phi,
\qquad
J_\phi(x, y, z)=\sum_{\mathrm{cyclic}}\phi(x,\phi(y, z)).
\]

Exact elimination either supplies a correction \(\psi\), or a left-nullspace witness \(\lambda\) with \(\lambda d_2=0\) but \(\lambda J_\phi\ne0\). On an abelian three-dimensional reference, take \(\phi(e_0, e_1)=e_0\), \(\phi(e_1, e_2)=e_1\), and \(\phi(e_0, e_2)=0\). Every first-order direction is a cocycle there, but \(J_\phi(e_0, e_1, e_2)=e_0\) in the cyclic convention above, so no second-order correction exists because \(d_2=0\). A checker using the opposite nested-bracket convention records the opposite sign and the same obstruction. This turns the difference between a plausible deformation and an actual family into a concrete falsifiable calculation.

## 9. The prescribed response basis is an actual integral E8 basis

For the fixed reference ordering, take seeds \(s_i=e_i+f_i\), i=1,...,8, and probes in the order \(e_1,\ldots, e_8, f_1,\ldots, f_8\). Apply the exact breadth-first commutator-word compiler, with its stated primitive sign normalization and independent-column selection. This prescription examines3,943 candidates and selects248 vectors; the longest selected word has depth 28. The actual basis matrix has determinant-1. All its columns are integral, so its inverse is integral and the new vectors form a Z-basis of the same Chevalley lattice. The labels \(\mathsf A_{\sigma, j}\) now refer to replayable selected words, not arbitrary names attached to unresolved vectors. The certificate retains the selected words, rejected candidates, pivot history and inverse; bracket transport passes on **all 30,628 unordered basis pairs**. Its tensor has 9,062 output terms across 8,200 nonzero input pairs. Under the same count, the Chevalley reference has 8,347 output terms across 7,752 nonzero pairs. The designated response basis is therefore about 8.57% denser in this metric. Its established advantage is a reproducible mixed-word prescription that preserves the integral lattice; this run does not establish a sparsity advantage.

The seed specification matters arithmetically. An alternate run starts from the single Cartan vector \(H_1+2H_2+\cdots+8H_8\) and the same sixteen probes. It reaches248 independent vectors after 3,935 candidates with maximum selected depth 29, but its determinant is-5. Thus it spans a sublattice of index 5 in the Chevalley lattice. Full rank alone would have missed that difference. These two explicit runs demonstrate why an Asterion record must carry its seeds, normalization and lattice evidence, and why the first run is the designated same-lattice response basis.

The principal, Jordan and response bases have different proven arithmetic contracts. Principal chains are integral but have a large nonunit determinant. The Jordan chart has small coefficients and a closed free Z[zeta5]-Lie lattice but no established rank 248 rational descent. The prescribed response basis is unimodular over Z. No single description is credited with the properties established only for another chart. The measured response-basis density penalty is preserved as a negative result; it is not hidden by the successful unimodularity and full transport checks.

The coordinate systems are connected by an explicit rational isomorphism in `asterion_transport.py`. It recovers the 240 root spaces of the two-A4 exterior model from their diagonal weights, computes a positive system and eight simple roots, matches the E8 diagram, and propagates their actual root-vector images through brackets. All 30,628 unordered Chevalley basis brackets intertwine, and all 744 basis round trips across the three transport directions pass. The root columns are signed monomials; the Cartan inverse is only 8 by 8. The numerical interface also composes this map with the principal and prescribed response bases, so all sixteen directed conversions among Chevalley, Asterion, principal and Jordan charts accept exact cyclotomic coefficients. For example, `python -m perfectjet asterion convert --source jordan --target principal --vector '[{"label":[1,0,0,0],"coefficient":1}]'` returns a complete exact vector and checks the reverse conversion.

The numerical entry point is `python -m perfectjet asterion`. `overview` constructs the exact coordinate systems and reports their dimensions and coupling counts. `report --exhaustive` requests the full finite replay. `bracket --chart principal --left '[7,3]' --right '[11,6]'` evaluates a specific polynomial basis bracket. `convert` checks coordinate transport, `compile` exercises the response compiler, and `deformations` exposes the bounded exact gauge and obstruction calculations. Exact rational and cyclotomic results are encoded without floating-point equality. The complete 40-equation extension is PJ-A001 through PJ-A040; each row's evidence describes the particular calculation or mathematical derivation it supports.

## Primary references

[1] Meinolf Geck, *On Lusztig's canonical bases of simple Lie algebras*, 2026 preprint, [arXiv:2602.19632](https://arxiv.org/abs/2602.19632). Root-lattice multiplicative cocycles and canonical Chevalley signs.

[2] Jeffrey Adams and Xuhua He, *Lifting of elements of Weyl groups*, [arXiv:1608.00510](https://arxiv.org/abs/1608.00510). Orders of lifts, including elliptic E8 elements.

[3] Alexander Kirillov Jr. and Jaimal Thind, *Coxeter Elements and Root Bases*, [arXiv:0811.2324](https://arxiv.org/abs/0811.2324). Coxeter-based root vectors and combinatorial brackets.

[4] Abdelmalek Abdesselam and Alexander Thomas, *Structure Constants for Simple Lie Algebras from a Principal sl2-Triple*, Journal of Lie Theory34(4), 829–862 (2024), [DOI:10.5802/jolt.1363](https://doi.org/10.5802/jolt.1363), [arXiv:2309.08213v3](https://arxiv.org/html/2309.08213v3). Principal bases and transvectants; Section 6.3 states the exceptional computations performed there.

[5] Yolanda Cabrera, Cristina Draper and Antonio Garvín, *Linear models of the exceptional Lie algebra e8*, published 2025, [DOI:10.1007/s13398-025-01768-3](https://doi.org/10.1007/s13398-025-01768-3), [arXiv:2308.09052](https://arxiv.org/abs/2308.09052). Proposition 3.1 gives the two-A4 model; Remark 3.5 identifies the doubled twisted Z5-cubed construction direction.

[6] Alberto Elduque, *Jordan gradings on exceptional simple Lie algebras*, Proceedings of the American Mathematical Society137 (2009), 4007–4017, [arXiv:0810.2737](https://arxiv.org/abs/0810.2737), [DOI:10.1090/S0002-9939-09-10017-5](https://doi.org/10.1090/S0002-9939-09-10017-5). Theorem 2.1 proves uniqueness of the two-dimensional Z5-cubed grading; the introduction establishes the associated orthogonal Cartan decompositions.

[7] Albert Nijenhuis and R. W. Richardson Jr., *Deformations of Lie Algebra Structures*, Journal of Mathematics and Mechanics17 (1967), 89–105, [publisher record](https://iumj.org/article/1789/), [DOI:10.1512/iumj.1968.17.17005](https://doi.org/10.1512/iumj.1968.17.17005). Classical bracket deformation and obstruction theory.

[8] Charles A. Weibel, *An Introduction to Homological Algebra*, Chapter 7, Corollary 7.8.12, [author-text chapter hosted by MIT](https://math.mit.edu/~hrm/palestine/weibel/07-lie_algebra_homology_and_cohomology.pdf). Whitehead's second lemma for finite-dimensional modules.
