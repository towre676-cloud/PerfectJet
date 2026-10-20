# Exact research frontiers: arithmetic symmetry, finite spectra and all-degree partners

**Research checkpoint, 20 October 2026 UTC.** This chapter adds 23 equations to the 675-record source catalogue without changing any preceding record. They stand as mathematical research: exact correspondences, finite uniqueness certificates, structural obstructions and all-degree boundary classifications. The historical literature already contains cyclotomic E8 lattices, Coxeter centralizer results and finite moment reconstruction methods. No worldwide priority, new Lean theorem, classifier improvement or enlarged Math Lab tool count is asserted here.

## Arithmetic information beyond the Coxeter spectrum

Let \(K=\mathbb Q(\zeta)\), \(\zeta=\zeta_{30}\), \(O=\mathbb Z[\zeta]\), and let \(C,A\) be the supplied E8 Coxeter and Cartan matrices. The integral Krylov basis \(B=(v,Cv,\ldots,C^7v)\), with \(v\) the eighth simple root, satisfies \(CB=BD\) for multiplication by \(\zeta\), and \(G=B^TAB\). The actual bilinear form has the arithmetic description

\[
G_{ij}=\operatorname{Tr}_{K/\mathbb Q}(\alpha\zeta^{i-j}),\qquad
\alpha=\frac{5-\zeta-2\zeta^2-2\zeta^3-\zeta^4+\zeta^6+2\zeta^7}{15}.
\]

These are finite rational identities, not a match of complex eigenvalues. The element \(\alpha\) is real and totally positive, with \(N(\alpha)=1/1265625\), \(\operatorname{disc}(K)=1265625\) and \(\det G=1\). Consequently \(\alpha O\) is the codifferent: the trace pairing remains integral and self-dual despite the displayed denominator. This arithmetic metric is information that a bare spectrum does not contain.

An integral map commuting with \(C\) is fixed by its value at 1 in the cyclic basis and equals multiplication by an element of \(O\). Thus the integral commutant is \(O\). A commuting map is an isometry exactly when \(u\bar u=1\). Every conjugate then has modulus one; Kronecker's theorem makes \(u\) a root of unity, and the roots of unity in \(K\) are \(\mu_{30}\). Therefore the isometry centralizer is exactly \(\langle C\rangle\), of order 30. This recovers a classical centralizer result in explicit coordinates.

A normalizing map with \(UC=C^aU\), \(a\in(\mathbb Z/30)^\times\), has the semilinear form \(x\mapsto u_a\sigma_a(x)\), \(\sigma_a(\zeta)=\zeta^a\). Trace nondegeneracy proves the precise isometry condition

\[
\alpha u_a\bar u_a=\sigma_a(\alpha).
\]

The direction of the norm ratio is essential. An arbitrary field automorphism need not preserve this metric. To find every integral lift, enumerate the 240 actual roots \(r\) and set

\[
K_a(r)=(r,C^ar,\ldots,C^{7a}r),\qquad
U=K_a(r)B^{-1},\qquad K_a(r)^TAK_a(r)=G.
\]

The complete finite enumeration yields 30 lifts for each of the eight unit exponents. Completeness follows because an isometry sends \(v\) to a root, and that root image fixes every column of an intertwiner in the cyclic basis. Hence the normalizer \(N\) has order 240 and fits into

\[
1\longrightarrow C_{30}\longrightarrow N\longrightarrow(\mathbb Z/30)^\times\longrightarrow1.
\]

This extension is **nonsplit**. An explicit lift of7 is

\[
S(x)=(\zeta^2+\zeta^3+\zeta^4+\zeta^5-\zeta^7)\sigma_7(x),
\qquad SC=C^7S,\quad S^4=C^{25}.
\]

Every other lift of7 is \(C^iS\), and

\[
(C^iS)^4=C^{25+10i}\ne I.
\]

The quotient element7 has order four, but no lift has fourth power one. A section would have to provide such a lift, which is impossible. The normalizer has two root orbits of size 120; its 240 elements are not identified with the 240 roots by cardinality. Complete proofs, conventions and exact replay belong to the [trace-form and normalizer account](https://github.com/towre676-cloud/perfectpower/blob/main/docs/COXETER_TRACE_NORMALIZER.md). These statements are PJ-E465–PJ-E470.

## A finite and sharp spectral certificate

For the existing Raghava coordinates define ordinary positive moments

\[
\mu_j=\frac{(2j)!}{4^j}r_j=\sum_q w_qx_q^j,
\qquad x_q=(q-\tfrac12)^2,\qquad\mu_0=r_0.
\]

Here \(0\le q<1\) and \(w_q\ge0\). Equal folded nodes are combined. For an \(s\)-node positive measure, the Hankel matrix \(H_{ij}=\mu_{i+j}\), \(0\le i,j<s\), is positive definite: its quadratic form is a positive sum of squares of a polynomial of degree below \(s\), which cannot vanish at all \(s\) distinct nodes unless it is zero. Solve

\[
H(p_0,\ldots,p_{s-1})^T=-(\mu_s,\ldots,\mu_{2s-1})^T
\]

and put \(p(X)=X^s+\sum_{j<s}p_jX^j\). The first \(2s\) coordinates determine this monic annihilator. The extra coordinate \(\mu_{2s}\) supplies the global certificate

\[
\sum_q w_qp(x_q)^2=0.
\]

Every nonnegative competitor with the same \(\mu_0,\ldots,\mu_{2s}\) must therefore be supported on the roots of \(p\). Vandermonde inversion fixes the weights. No conductor bound or bound on the competing support size is assumed. Signed competitors would invalidate the square argument. Once recovered, \(p\) gives every subsequent moment by \(\mu_{n+s}+\sum_{j<s}p_j\mu_{n+j}=0\).

For E8 reflection the folded nodes are \(1,4,16,49\), divided by 225, each with weight 2. Thus **mass and the first eight Raghava moments** certify the folded spectrum among every nonnegative finite phase profile. Nine coordinates including mass suffice, without restricting competitors to conductor 30.

The count is sharp among positive rational weighted profiles. Take the increasing nodes

\[
0,\ 1/225,\ 1/100,\ 4/225,\ 1/25,\ 16/225,\ 1/9,\ 49/225,\ 1/4,
\qquad\delta_i=\frac1{\prod_{j\ne i}(x_i-x_j)}.
\]

Comparing the degree-eight coefficient in Lagrange interpolation gives \(\sum_i\delta_ix_i^k=0\) for \(0\le k<8\), and1 at \(k=8\). With

\[
\varepsilon=\frac{14144}{3243658447265625}
=\min_{i\text{ odd}}\frac1{-\delta_i},\qquad
w'_i=2\mathbf1_{i\text{ odd}}+\varepsilon\delta_i,
\]

all nine weights are positive. All offsets are rational and the corresponding symmetric phases have conductor dividing30. This profile has mass8 and matches \(r_0,\ldots,r_7\), but differs in \(\mu_8\) by \(\varepsilon\). The weights are rational, so minimality among actual dimension-eight integer representations is not established.

Even coordinates lose orientation between \(q\) and \(1-q\). Restore it with absolutely convergent odd Mellin observations, at weights at least three:

\[
y_k=\pi^{-(2k+1)}\operatorname{Im}\sum_{n\ge1}\frac{\operatorname{Tr}(T^n)}{n^{2k+1}}
=\frac{(-1)^{k+1}2^{2k}}{(2k+1)!}\sum_qw_qB_{2k+1}(q),\quad k\ge1.
\]

The Bernoulli factorization \(B_{2k+1}(1/2+t)=t(t^2-1/4)P_{k-1}(t^2)\), with \(P_{k-1}\) monic, gives a scaled Vandermonde system on the interior folded nodes. If there are \(s_*\) such nodes, \(s_*\) odd rows recover their pair-weight differences; the two self-dual endpoints already have no orientation ambiguity. Reflection has four interior nodes, so nine even coordinates plus odd weights3,5,7,9 suffice. The adjoint has 16 folded nodes and 14 interior nodes, so 33 even and 14 odd coordinates suffice. These are spectral conclusions, not recovery of the integral metric or Lie bracket. See the [finite reconstruction proof](https://github.com/towre676-cloud/perfectpower/blob/main/docs/COXETER_RECONSTRUCTION.md). These statements are PJ-E471–PJ-E477.

## All-degree sextic structure from local polynomial identities

Let \(K_N(f)=\{g\in S_N:(f,g)_3=(f,g)_5=0\}\), with nonzero binary sextic \(f\), characteristic zero and \(N\ge3\). Activity additionally requires \((f,g)_1\ne0\). With \(f=y^6F(t)\), \(g=y^NG(t)\), \(t=x/y\), the unnormalized affine gate is

\[
(f,g)_r\big|_{y=1}=\sum_{i=0}^r(-1)^i\binom ri
(6-r+i)_i(N-i)_{r-i}F^{(r-i)}G^{(i)}.
\]

Falling factorials are used. Verification on pure powers proves the identity by bilinearity because pure powers span in characteristic zero. The third equation is

\[
-120FG'''+60(N-2)F'G''-12(N-1)(N-2)F''G'+N(N-1)(N-2)F'''G=0.
\]

At a point of exact multiplicity \(k\) in \(f\), write \(F=at^k+\cdots\), \(G=bt^s+\cdots\), \(ab\ne0\). The leading gate coefficient is

\[
I_{r,k}(N,s)=\sum_i(-1)^i\binom ri(6-r+i)_i(N-i)_{r-i}(k)_{r-i}(s)_i.
\]

Both \(I_{3,k}\) and \(I_{5,k}\) must vanish. Remove their displayed common factors in \(s\). The remaining resultants are exact polynomials in \(N\): for \(k=1,5\) they are respectively \(-4(N-4)(N-2)(N-1)\) and its negative; for \(k=2,4\), \(-(N-6)(N-2)^3(N-1)^3(N+8)\); for \(k=3\), \((N-12)^2(N-2)^2(N-1)^4\); and for \(k=0,6\),1. These identities, not finite-degree extrapolation, prove for all \(N\ge13\):

| Exact multiplicity \(k\) of \(f\) | Allowed valuation \(s\) of a nonzero partner |
|---|---|
|0|0,1,2|
|1|0,1|
|2|0|
|3|\(N/2\), requiring even \(N\)|
|4|\(N\)|
|5|\(N-1,N\)|
|6|\(N-2,N-1,N\)|

For exact multiplicity \(k=4,5,6\), write \(f=\ell^kh\), \(\ell\nmid h\). The complete partner space is

\[
K_N(f)=\ell^{N-k+4}S_{k-4},\qquad\dim K_N(f)=k-3.
\]

The respective ranges are \(N\ge7,5,3\). Necessity follows from the local resultants. For sufficiency choose \(\ell=x\): the transverse degrees of \(f\) and every proposed partner sum to at most 2, so every third or fifth transvectant term differentiates more times transversely than the inputs allow. This proves a whole unbounded-degree stratum, rather than checking additional examples.

A particularly clean geometric equivalence holds for every \(N\ge3\):

\[
\ell^N\in K_N(f)\quad\Longleftrightarrow\quad\ell^4\mid f.
\]

After \(\ell=x\), the third gate is \(-(N)_3x^{N-3}\partial_y^3f\). Its vanishing is exactly the fourfold-root condition; the fifth gate then vanishes too. Its first gate is \(-Nx^{N-1}\partial_yf\), so the pure-power partner is active precisely when \(f\) is not proportional to \(\ell^6\).

Finite jet evaluation is injective: at a regular point a nonzero solution cannot vanish to order 3, so \(\dim K_N(f)\le3\). A simple root gives \(\dim K_N(f)\le2\) for \(N\ge5\); a double root gives \(\dim K_N(f)\le1\) for \(N\ge7\). A triple root excludes every odd \(N\ge13\). For two independent triple-root factors,

\[
K_N((\ell m)^3)=\operatorname{span}((\ell m)^{N/2})\quad(N\ge14\text{ even}),
\]

and it is zero for odd \(N\ge13\). The even partner is inactive. Divisibility at both roots proves necessity; cancellation of paired odd-transvectant terms proves sufficiency.

Finally, monomial sextics have complete dimension series \(H_f(t)=\sum_{N\ge3}\dim K_N(f)t^N\):

\[
H_{x^6}=\frac{3t^3}{1-t},\quad
H_{x^5y}=\frac{2t^3}{1-t}+t^4,\quad
H_{x^4y^2}=\frac{t^3}{1-t}+t^6,\quad
H_{x^3y^3}=\frac{t^4}{1-t^2}+2t^{12}.
\]

Each monomial partner has distinct gate output exponents, so common indicial roots give the full basis, including exceptional degrees 4,6,12. No graded-algebra or module structure is asserted for the kernels. Full factors, resultant certificates, thresholds and exact replay appear in the [partner structure proof](../PARTNER_STRUCTURE.md). These statements are PJ-E478–PJ-E487. They do not claim a global squarefree classification in degree 21 and above and do not upgrade the trust status of the archived external-solver classification.

## Research consequence and evidence boundaries

The spectral question now has a finite positive uniqueness theorem, a sharp counterexample and an orientation inverse. The lattice question retains the arithmetic form and a nonsplit symmetry extension. The sextic question now has exact local obstructions in every degree, complete high-multiplicity strata and complete two-root dimension series. These are complementary mathematical advances with their own standards of success.

The next serious targets are an explicit E8-to-H4 arithmetic restriction of scalars over the golden subfield, carrying the metric and lifts, and a global finite-type or differential-operator-gcd theorem for squarefree sextic partners. More finite searches would remain evidence until they supplied the missing all-degree argument. The chapter supplies exact solved boundary cases with which any such global theorem must agree.

The catalogue stores these claims as `derived`, with explicit assumptions and proof links. Exact Python checks accompany their separate implementation receipts; they are not Lean kernel formalization. The 23 new rows are present in the installed searchable equation resources, while the existing 29 Math Lab tools retain their previous supported parameter ranges. Every preceding 675 record and all 27 family ranks are preserved.
