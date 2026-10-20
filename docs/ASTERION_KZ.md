# Exact five-channel E8 KZ and classical Racah calculus

`perfectjet.asterion_kz` derives an executable rational presentation of the classical four-adjoint E8 Knizhnik–Zamolodchikov connection. The connection, tensor decomposition and Racah calculus are established mathematics. The module claims an explicit arithmetic implementation and replay certificates, not a new Racah matrix, new exceptional algebra, new conformal field theory or worldwide priority. It depends on the actual `E8LieAlgebra` bracket in `asterion_e8.py`.

The invariant bilinear form is normalized so long roots have squared length two. Thus the adjoint quadratic Casimir is 60 and the dual Coxeter number is 30. In the Chevalley coordinates used here, the Cartan Gram matrix is the E8 Cartan matrix and opposite root vectors pair to one. The code verifies the complete lowered structure tensor is alternating and verifies the quadratic Casimir on all 248 generators. This establishes the normalization from the implemented algebra rather than an unverified scalar convention.

The classical decomposition is

\[
248\otimes248=1\oplus248\oplus3875\oplus30380\oplus27000.
\]

All summands are self-dual and occur once, so the invariant space in the fourth tensor power has dimension five. The code uses the five tensors

\[
T_1=B(a,b)B(c,d),\quad T_2=B(a,c)B(b,d),\quad T_3=B(a,d)B(b,c),
\qquad T_4=B([a,b],[c,d]),\quad T_5=B([a,c],[b,d]).
\]

Their evaluation matrix on five displayed quadruples is invertible. This proves independence; the known decomposition supplies the dimension and therefore spanning. Each Casimir contraction is invariant because of the checked metric invariance. Its coordinates are consequently determined by the five evaluations. An additional independently selected panel of balanced root quadruples replays the contractions directly. No array of size \(248^4\) is formed, and five sample evaluations alone are not presented as proof for an arbitrary tensor outside the established invariant span.

With columns representing input tensors, one residue in this basis is

\[
A_T=\begin{pmatrix}
-60&0&0&0&12\\0&0&0&0&12\\0&0&0&0&12\\
0&0&-1&-30&-10\\0&1&1&0&-10
\end{pmatrix}.
\]

The other two pair residues are derived independently by sparse contraction. The crossing interchanges the first and third tensor arguments. An exact rational eigenvector matrix diagonalizes \(A_T\), with first nonzero coordinate of each eigenvector normalized to one. In this channel basis the equations are

\[
F'(z)=\hbar\left(\frac{A}{z}+\frac{B}{z-1}\right)F(z),\qquad
A=\operatorname{diag}(-60,-30,-12,0,2).
\]

The corresponding channel dimensions are \((1,248,3875,30380,27000)\). The rational crossing \(R\) obeys \(R^2=I\) and \(B=RAR\). It is a classical, unnormalized invariant-channel convention, not an assertion that its entries equal a published orthonormal or quantum Racah convention. The independently derived third residue satisfies \(A+B+C=-60I\); infinitesimal braid relations and all five polynomial projectors are checked exactly. Each projector has rank one on the five-dimensional invariant multiplicity space, not rank one on the full tensor square.

The canonical serialization records rational strings, basis conventions and a SHA-256 digest. The displayed tensor and channel matrices have denominator primes \(2,3,5,7,31\). This is a sufficient localization for this presentation; minimality and an optimal integral normalization are not proved. The coefficient 31 is arithmetic data, and does not assert the presence of a primitive 31st-root phase.

## Local solutions, resonances and actual logarithms

For \(F=z^\rho\sum_{n\ge0}v_nz^n\), the power-series recurrence is

\[
((n+\rho)I-\hbar A)v_n=-\hbar B\sum_{m<n}v_m.
\]

The implementation does not divide by a resonant zero. It instead permits polynomial coefficients in \(L=\log z\). The exact recurrence in each diagonal channel is

\[
(n+\rho-\hbar\lambda_i)v_{n,p,i}+(p+1)v_{n,p+1,i}
=-\hbar\sum_{m<n}(Bv_{m,p})_i.
\]

Nonresonant equations are solved downwards in log degree. At a resonance the source polynomial is integrated, with zero integration constant as the declared normalization. A nonzero source produces an actual stored logarithmic coefficient. `logarithms=False` stops at an incompatible canonical recurrence and returns its exact source. Every retained coefficient is substituted back into the differential recurrence. A computed prefix is distinguished from an all-order log-free certificate: the latter is returned only when all possible positive integer resonance orders have been passed and no logs were required.

At generic rational deformation parameters logarithms genuinely occur in this implementation; for example \(\hbar=1/2\), the branch with eigenvalue zero has a nonzero source at order one in the 27000 channel. This is an exact formal regular-singular calculation, not a floating-point resonance test.

For an integrable WZW interpretation one must set \(\hbar=1/(k+30)\). The adjoint primary has affine level two and is absent at level one. All five fusion channels are retained for \(k\ge4\): the tensor/fusion stability bound is \(k\ge\langle\theta+\theta,\theta^\vee\rangle=4\), and the 27000 representation has highest weight \(2\theta\), of level four. The module refuses to describe levels one, two or three as a five-channel integrable fusion theory; its generic formal KZ calculation can still be studied separately.

There is a finite all-level resonance certificate for integer \(k\ge4\). The largest Casimir gap is 62 and \(k+30\ge34\), so any positive integer resonance has order one. The only candidate levels are 18, 30 and 32. Their sources vanish exactly: the singlet branch does not couple at first order to the 3875, 30380 or 27000 target channels. The ordinary power solutions therefore pass these resonances and continue log-free to all orders. This is an explicit verification of the classical connection, not a new general unitarity theorem.

For the full formal five-channel system at the excluded low levels, genuine logarithms occur. At \(k=1\), the singlet branch has order-two source \(12/6727\) in the 27000 channel. At \(k=2\), the adjoint branch has order-one source \(3/1736\) there. These are diagnostics for the untruncated formal system; neither is an assertion about a physical five-channel fusion theory at those levels. The JSON receipt includes both exact computations.

## Controlled continuation and limits

`continue_real` transports a rational initial vector along a real interval strictly inside \((0,1)\). It constructs rational Taylor coefficients and returns a rational infinity-norm error bound. On a disk of radius half the distance to the singularities, a bound for the coefficient matrix and a rational upper bound for the exponential control the solution. Cauchy's estimate bounds the omitted Taylor tail, and a linear stability bound propagates previous error. Comparing two numerical resolutions is a regression check, not the source of the certified error estimate. This routine does not traverse a complex loop, identify branches globally, or certify a global monodromy matrix.

`continue_polygon` separately transports the identity fundamental matrix along an explicitly supplied complex polygon with rational real and imaginary coordinates. It rejects every segment intersecting zero or one using exact collinearity and interval tests. The default tensor chart reduces residue norms. If the center is \(c\), set \(r_j=\max(|\Re(c-j)|,|\Im(c-j)|)\) and \(R=\min(r_0,r_1)/2\). The ordinary complex modulus is at least \(r_j\), so on the entire disk the connection norm is bounded by

\[
L=|\hbar|\left(\frac{\|A_T\|_\infty}{r_0-R}+\frac{\|B_T\|_\infty}{r_1-R}\right).
\]

Banach-valued Cauchy estimates bound the order-\(N\) tail by \(\|Y_0\|_\infty e^{LR}q^{N+1}/(1-q)\), where \(q\ge |\Delta z|/R\) is rational. Rational geometric-tail bounds enclose the exponentials, and the previous error grows by at most \(e^{L|\Delta z|}\). Gaussian-rational Taylor coefficients follow the three-term recurrence obtained from \(z(z-1)Y'=\hbar[A_T(z-1)+B_Tz]Y\). After each step, rounding to denominator \(2^b\) adds a certified matrix infinity-norm error of at most \(5/2^b\); error bounds themselves round outwards. These bounds use the ordinary complex-modulus matrix infinity norm, even though rational modulus upper bounds are used for their computation.

The return value distinguishes a completed calculation from a met tolerance. A closed polygon with a met tolerance certifies the holonomy of that one loop, in the stated chart and base point. It does not identify the whole monodromy group or prove a global density theorem; `global_monodromy_certified` remains false. The output stores the exact Gaussian-rational approximation, rational enclosure, full path and every local error bound.

`monodromy_pair_receipt()` uses the counterclockwise rectangle \((1/2,0)\to(1/2,1/2)\to(-1/2,1/2)\to(-1/2,-1/2)\to(1/2,-1/2)\to(1/2,0)\) about zero. Exact crossing symmetry sends the equation under \(z\mapsto1-z\) to itself by the constant gauge \(X\). The reflected loop about one has holonomy \(V=XUX\), at the same base point. This proves the path relation without a second numerical integration. If \(\widehat U\) approximates \(U\) with error \(e_U\), then \(\widehat V=X\widehat U X\) has error at most \(e_V=\|X\|_\infty^2e_U\). The stored lower bound for \(\|\widehat U\widehat V-\widehat V\widehat U\|_\infty\) is compared against the rigorous upper error

\[
2\big(\|\widehat U\|_\infty e_V+\|\widehat V\|_\infty e_U+e_Ue_V\big).
\]

At \(\hbar=1/34\), the default 128-step, order-40 calculation bounds the first loop's error by approximately \(3.390\times10^{-12}\). The commutator-difference lower bound exceeds9.759, while its error bound is below \(4.225\times10^{-10}\). This certifies noncommuting generator holonomies of the classical KZ connection. The false `global_monodromy_certified` flag records this component's narrower scope. The next-push [monodromy theorem](ASTERION_MONODROMY.md), implemented in `asterion_monodromy.py`, now proves the specialized level-four compact closure `{g in U(5):det(g)^17=1}`, with identity component SU(5) and projectively dense image in PU(5). Its actual-loop irreducibility and classification gates are independently replayed. `kz_receipt(exhaustive=True)` retains the earlier two-loop calculation; ordinary receipts do not perform that integration.

Typical use is `system = E8KZ()`, followed by `system.verify()`, `system.frobenius(Fraction(1,34), order=8, branch=0)`, `system.wzw_resonance_certificate()` or `kz_receipt(exhaustive=True)`. The detailed matrices are exposed as `A_tensor`, `B_tensor`, `C_tensor`, `channel_transform`, `A`, `B`, `C` and `crossing`.

## Primary sources

Isaev and Krivonos, *Split Casimir operator and universal formulation of the simple Lie algebras* (2021), [arXiv:2106.04470](https://arxiv.org/abs/2106.04470), supplies the split-Casimir identities, exceptional projector formulas and normalization comparison. Their Killing-form normalization has eigenvalues \(-1,-1/2,-1/5,0,1/30\); multiplying by 60 gives the convention used here.

Mironov and Morozov, *Universal Racah matrices and adjoint knot polynomials. I. Arborescent knots*, [arXiv:1511.09077](https://arxiv.org/abs/1511.09077), is prior work on universal adjoint Racah calculus. The present reconstruction must be assessed against that literature, rather than treating a different rational gauge as a new classical matrix.

Feingold, *Fusion Rules for Affine Kac–Moody Algebras*, [arXiv:math/0212387](https://arxiv.org/abs/math/0212387), Theorems 6.1–6.2, supplies the tensor/fusion stability criterion used to delimit \(k\ge4\). The five-channel formal connection and low-level integrable quotients are different mathematical objects.
