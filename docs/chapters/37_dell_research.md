# 37. Double-elliptic normalization and obstruction

# Double-elliptic research: exact normalization and obstruction boundaries

This programme reconstructs a precise published double-elliptic (DELL) current and uses it to prove restricted normalization and obstruction results. It accompanies the E8 research without changing its kernel claims. The weight-five and weight-six relation-lift programme remains separate. The current is attributed to Koroteev and Shakirov, with the theta-ratio convention of Grekov and Zotov. The present project does not identify this reconstruction with every model called DELL, or claim to solve the self-dual system discussed by Mironov and Morozov. Primary sources and convention decisions are retained in [dell_sources.json](dell_sources.json).

The substantive mathematical output is a finite-ansatz normalizer classification and an analytic no-go theorem for particlewise ellipticization. Independently replayable finite calculations test the declared current. Those calculations support implementation correctness at their stated orders and parameter points; they do not establish a global identity merely by returning exact zeros.

## Declared current and conventions

Let \(X_i,Y_i,T\) be nonzero multiplicative coordinates and coupling. Let \(P\) be the coordinate elliptic nome and \(W\) the momentum elliptic nome. Our standard multiplicative theta is

\[
\theta(Z;P)=(1-Z)\prod_{m\geq1}(1-P^m)(1-P^mZ)(1-P^m/Z).
\]

The coordinate nome in this formula is the square of the parameter called \(p\) in Koroteev–Shakirov equation 3.3. That change matters when comparing truncation orders. The quantum shift parameter is called \(Q\), and is distinct from both nomes. Fourier-mode signs are removed throughout; multiplying a Hamiltonian by its fixed mode sign does not change commutativity.

For integer vectors \(n\in\mathbb Z^N\), write

\[
E(n)=\sum_i\frac{n_i(n_i-1)}2,\qquad
F_n(X;T,P)=\prod_{i<j}
\frac{\theta(T^{n_i-n_j}X_i/X_j;P)}{\theta(X_i/X_j;P)},
\]
\[
C_a=\sum_{\sum_i n_i=a}W^{E(n)}F_n(X;T,P)Y^n,
\qquad H_a=C_0^{-1}C_a.
\]

At \(W=0\), \(C_0=1\), so the formal inverse is well defined away from the coordinate theta divisors. Each integer summand \(n_i(n_i-1)/2\) is nonnegative. Therefore a fixed momentum order has finite support, with a rigorous coordinate bound obtained from this scalar inequality. The compiler enumerates and filters that finite set rather than guessing a momentum cutoff.

Dividing the original raw modes by their common left coordinate factor causes no quantum ambiguity:

\[
(M C_0)^{-1}(M C_a)=C_0^{-1}C_a.
\]

No commutativity of the factors is used. Likewise right-normalized modes are a simultaneous conjugate family,

\[
C_aC_0^{-1}=C_0(C_0^{-1}C_a)C_0^{-1}.
\]

Consequently right normalization cannot serve as a noncommutativity negative control. A meaningful control removes the normalizer entirely or perturbs an actual compatibility condition.

Uniformly translating the integer vector by \((1,\ldots,1)\) preserves every pair coefficient and changes its energy by its previous charge. Thus the literal signless current satisfies the all-order formal recurrence

\[
C_{a+N}=W^a(Y_1\cdots Y_N)C_a.
\]

This identity is derived directly from the declared current. It should not be replaced by a printed quasiperiodicity factor belonging to a different gauge, spectral variable or convention. In the quantum model the total shift commutes with coefficients depending only on coordinate ratios.

## First-order normalization is forced in a classified ansatz

Work classically with \(N=3\) and \(P=0\). The first momentum shell has

\[
C_0=1+WA+O(W^2),\quad C_1=h_1+WB+O(W^2),\quad
C_2=h_2+WC+O(W^2).
\]

Here \(A\) contains the six shifts permuting \((-1,0,1)\), \(B\) the three shifts permuting \((-1,1,1)\), and \(C\) the three shifts permuting \((2,0,0)\). The project proves the rational identities

\[
\{h_1,h_2\}=0,\qquad
\{B,h_2\}+\{h_1,C\}
=h_1\{A,h_2\}+h_2\{h_1,A\}=R.
\]

The proof clears denominators and checks exact sparse Laurent-polynomial coefficients in symbolic coupling and coordinates. It is not an inference from a sample panel. The defect is not identically zero: at \(T=2\), \(X=(1,3,7)\), \(Y=(2,5,11)\),

\[
R=\frac{8356261}{901120}.
\]

It follows that a common power normalizer \(C_0^{-s}\) yields a first-order bracket \(W(1-s)R\); the exponent is uniquely \(s=1\).

The stronger result allows independent coupling-dependent coefficients in the normalizer:

\[
\rho=\sum_{n\in\operatorname{perm}(-1,0,1)}
\lambda_n(T)F_nY^n,
\qquad \widetilde H_a=\frac{C_a}{1+W\rho}.
\]

For every nonzero \(T\ne1\), first-order involutivity forces all six \(\lambda_n=1\). A retained coefficient minor has determinant

\[
\det M_6(T)=-\frac{(T-1)^{14}}{T^8}.
\]

At \(T=1\) the complete compatibility map vanishes, so all six coefficients are free at this order. This gives the exact exceptional-coupling boundary within the six fixed normalizer functions. It is not a classification of arbitrary normalizers with coordinate-dependent coefficients, of arbitrary canonical transformations, or of all orders in either nome. The proof and exact matrices are documented in [DELL_NORMALIZATION.md](DELL_NORMALIZATION.md).

The unrestricted first-order freedom has an explicit description. On the open set where \(h_2\ne0\), write \(\rho=A+\chi\). The first-order compatibility condition is precisely

\[
\{\chi,h_1/h_2\}=0.
\]

Thus the six-mode theorem eliminates freedom within its declared coefficient space, while the larger Poisson centralizer can still supply other normalizers. This distinction prevents converting a finite-ansatz uniqueness statement into an unjustified universal uniqueness claim.

## Unchanged coordinate weights forbid particlewise ellipticization

Consider the standard trigonometric Ruijsenaars coordinate weights

\[
a_I(X;T)=\prod_{i\in I,j\notin I}\frac{TX_i-X_j}{X_i-X_j},
\]
\[
H_{1,f}=\sum_i a_i f(Y_i),\qquad
H_{2,f}=\sum_{i<j}a_{ij}f(Y_i)f(Y_j).
\]

The ansatz keeps the coordinate coefficients fixed and changes every particle momentum through one common meromorphic function \(f\). With the log-canonical Poisson convention, an exact specialization is

\[
\{H_{1,f},H_{2,f}\}\big|_{X=(1,3,7),Y=(u,v,v)}
=K(T)(f(v)-f(u))
\bigl(f(v)u f'(u)-f(u)v f'(v)\bigr),
\]
\[
K(T)=\frac{5T^4-26T^3+126T-105}{72}.
\]

A second coordinate witness at \(X=(1,2,5)\) has coefficient

\[
K_2(T)=\frac{7T^4-27T^3+90T-70}{16}.
\]

Writing \(A=72K\) and \(B=16K_2\), the exact identity

\[
(-529875-72145T+142128T^2)A
+(835114+187859T-101520T^2)B
=2821105(T-1)
\]

proves that the two witness coefficients have no common root except \(T=1\). Thus for every \(T\ne1\), involutivity and nonconstant \(f\) force \(Yf'(Y)/f(Y)\) to be constant on the connected regular domain. Analytic continuation gives \(f(Y)=CY^\lambda\) on a logarithmic cover; single-valued meromorphic functions on \(\mathbb C^\times\) require integer \(\lambda\). If additionally \(f(PY)=f(Y)\) with \(0<|P|<1\), that integer must vanish. Therefore this unchanged-coordinate, common-particle-profile ansatz admits no nonconstant elliptic momentum profile. At \(T=1\), all coordinate coefficients equal one, so arbitrary profiles commute. The two-witness argument therefore classifies the exact exceptional-coupling boundary of this ansatz.

For a simple nontrivial direction \(f(Y)=Y+\epsilon/Y\), the same bracket at \(T=2\), \(u=2\), \(v=3\) is exactly

\[
-\frac{95}{216}\epsilon+\frac{95}{1296}\epsilon^2.
\]

Monomials supply positive controls. The no-go result does not exclude general DELL models: coupled momentum dependence and changes in the coordinate functions lie outside its hypotheses. See [DELL_OBSTRUCTIONS.md](DELL_OBSTRUCTIONS.md) for the proof and exact implementation.

The normalized current itself exhibits a specific mixed Fourier mode. In its first correction to \(H_1\), the coefficient of \(Y^{(-1,2,0)}\) is

\[
-F_{(-1,1,0)}F_{(0,1,0)}.
\]

The numerator's first shell has no such mode, so this term is forced by normalization. It is generically nonzero. This is a structural property of the reconstructed current, not a previously unknown construction; by itself a mixed Fourier mode does not prove interacting dynamics.

## Exact replays and their limits

The classical compiler expands both nomes, evaluates exact rational logarithmic derivatives and forms the full Poisson bracket within the requested rectangle of orders. The quantum compiler instead multiplies normal-ordered shifts according to

\[
(f(X)S^n)(g(X)S^m)=f(X)g(Q^nX)S^{n+m},
\]

using the action \(S_i f(X)=f(X_1,\ldots,QX_i,\ldots,X_N)\). Freezing the shifted coefficient would change the operator algebra. In fact frozen scalar-coefficient Laurent multiplication is commutative by construction, so a zero commutator there is not a useful correctness test.

Run the declared report with `PYTHONPATH=src python -m perfectjet.dell --exhaustive`. The retained report records the exact orders, parameter specializations, all coefficient tests and negative controls that actually ran. Read its scope before interpreting a result. Exact rational zeros at a finite collection of points are bounded evidence; the separate symbolic normalization proof and analytic no-go argument are the global results under their stated hypotheses.

The general deformation equation makes the next step concrete:

\[
\{H_i^{(0)},H_j^{(r)}\}+\{H_i^{(r)},H_j^{(0)}\}
=-\sum_{s=1}^{r-1}\{H_i^{(s)},H_j^{(r-s)}\}.
\]

After a justified finite function space is chosen, the left side is linear in the unknown correction. A cokernel witness can then prove an obstruction within that space. Infinitesimal canonical changes \(H_i^{(1)}\mapsto H_i^{(1)}+\{H_i^{(0)},G\}\) must be quotiented out before counting inequivalent deformations. This general method is not presented as an implemented complete deformation classification.

## Remaining mathematical gates

A full DELL result would require more than the completed first-shell classification. The open gates include coordinate-elliptic symbolic normalization identities, higher-order normalizer and deformation classification, a proved all-order quantum commuting family in the declared formulation, functional independence on a specified symplectic phase space, and an explicit global position–momentum duality. The exceptional-root extension to E8 would additionally need its own phase space, commuting Hamiltonians and compatibility construction. An E8 dynamical tensor alone does not provide these objects.

All 640 previous equation records are preserved. The new PJ-D series records definitions, proved scoped consequences and finite-replay gates separately; neither a guessed formula nor a finite panel is labeled an all-order solution. Worldwide priority has not been established for the project theorems.


## Second-order classification and the first mixed-nome theorem

The next symbolic calculation proves the complete momentum-order-two
Poisson identity at coordinate nome zero, globally in the coupling and all
phase variables. Its three numerators over Delta^5 contain 19902, 13548
and 19902 terms; every coefficient cancels. Allowing a homogeneous
second-order normalizer built from the 21 symmetric products of the six
first-shell functions gives a second, completely classified boundary.
For every nonzero coupling except -1 and 1, no nonzero correction in that
function space survives. At -1 there is one surviving function, exactly
h1*h2/Y_all, built from existing commuting integrals. At 1 the actual
19-dimensional product space is unconstrained. Primitive cube roots make
two of the nominal 21 products redundant; after quotienting these zero
functions, they create no freedom. The proof combines symbolic coefficient
minors with exact rational and quadratic-field exceptional-rank certificates.
See DELL_NORMALIZATION.md for the matrices, identities and limitations.

The first coordinate-nome correction is also computed symbolically:
S_n=sum_(i<j)[(1-T^(n_i-n_j))*Xi/Xj+(1-T^(n_j-n_i))*Xj/Xi].
Using F_n(P)=F_n(0)*(1+P*S_n+O(P^2)), exact numerator cancellation proves
all four Poisson coefficients W^a P^b vanish for a,b in {0,1}, globally in
T,X,Y. The mixed coefficient has 3696 raw terms and 6864 normalizer terms
before cancellation. This is a finite two-nome functional identity,
stronger than a parameter-point test but weaker than an all-order theorem.
For fixed T!=0,1 the invertible six-column constant-nome minor forces
lambda_n(T,P)=1 modulo P^2 within the specified first-shell ansatz.

The formal family also descends under simultaneous-position-scaling
reduction, and its generic functional independence follows from the
nonzero elementary-symmetric Jacobian at P=W=0,T=1. This establishes a
necessary structural property, separately from the open all-order
commutativity, convergence and position-momentum duality questions.
The proof is in DELL_STRUCTURE.md.

The finite classical panel reaches W^6 P^4 for three particles, W^3 P^2
for four, and W^2 P for five, with every Hamiltonian pair checked at its
specified exact phase point. The independent quantum panel reaches W^4 P^3
at two three-particle position/coupling/shift points and checks all three
four-particle Hamiltonian pairs through W^2 P. Every output shift coefficient
is tested in the quantum panel; the receipts declare the actual support.
Neither panel converts point evaluations into global meromorphic identities.

# A classified first-shell normalizer for the three-body KS current

This result concerns the classical Koroteev–Shakirov current in its **coordinate-trigonometric limit**. The coordinate nome is exactly zero; the second, momentum nome is retained through first order. It proves a global rational identity and classifies the normalizer in one explicit six-function ansatz. It neither proves all-order DELL integrability nor claims worldwide priority.

## Source and conventions

Use the normalized current in Grekov and Zotov, [*Characteristic determinant and Manakov triple for the double elliptic integrable system*](https://arxiv.org/abs/2010.08077), equation (1.1). Its coordinate theta function degenerates to `theta_0(z)=1-z`. Their source coefficients satisfy `O_a=(-1)^a C_a` when `C_a` denotes the coefficient of `(-z)^a`; we use the signless `C_a` below. The source's `O_0^-1 O_a` prescription is historical input, not a newly discovered definition. The original Koroteev–Shakirov paper, [*The Quantum DELL System*](https://arxiv.org/abs/1906.10354), equations (3.2), (3.7), uses a current without the common theta denominator, which cancels in its left-normalized Hamiltonians. Our classification is classical and does not justify rearranging quantum factors.

Take nonzero coupling `t`, distinct positions `x_i`, nonzero momenta `y_i`, and the log-canonical Poisson bracket

\[
\{x_i,y_j\}=\delta_{ij}x_i y_j,\qquad
\{x_i,x_j\}=\{y_i,y_j\}=0.
\]

Put

\[
\Delta=\prod_{i<j}(x_i-x_j),\qquad
P_n=\prod_{i<j}(t^{n_i-n_j}x_i-x_j),\qquad
f_n=\frac{P_n}{\Delta}y_1^{n_1}y_2^{n_2}y_3^{n_3}.
\]

Then the current is

\[
C(z,\omega)=\sum_{n\in\mathbb Z^3}
\omega^{\sum_i n_i(n_i-1)/2}(-z)^{\sum_i n_i}f_n.
\]

All coefficient calculations are formal in the momentum nome `omega`. No analytic convergence of the full series is asserted here.

## The first shell is complete

Write `C_0=1+omega A+O(omega^2)`, `C_1=h_1+omega B+O(omega^2)`, and `C_2=h_2+omega C+O(omega^2)`. Their exact supports are

| Function | Momentum vectors n |
|---|---|
|h1|permutations of (1,0,0)|
|h2|permutations of (1,1,0)|
|A|permutations of (-1,0,1)|
|B|permutations of (-1,1,1)|
|C|permutations of (2,0,0)|

For each row, sum `f_n` over the listed distinct permutations. The shell count is exhaustive: `n(n-1)/2` is nonnegative on integers and exceeds one outside `{-1,0,1,2}`. Cost zero has entries in `{0,1}`. Cost one has exactly one entry equal to `-1` or `2`; imposing total momentum zero, one or two gives precisely the stated six, three and three vectors.

## Exact global compatibility identity

The finite polynomial calculation proves

\[
\{h_1,h_2\}=0,
\qquad
R:=\{B,h_2\}+\{h_1,C\}
=h_1\{A,h_2\}+h_2\{h_1,A\}.
\]

These are identities in the rational function field of `t,x_i,y_i`; they are not inferred from numerical samples. Indeed, the source uses `P_n/Delta` as every coefficient. The bracket of two terms has denominator `Delta^3` and explicit numerator

\[
\sum_i\left[
\Delta\bigl(m_i(x_i\partial_iP_n)P_m
-n_iP_n(x_i\partial_iP_m)\bigr)
+(n_i-m_i)P_nP_m(x_i\partial_i\Delta)
\right]y^{n+m}.
\]

Multiplication by `Delta` clears the extra denominator in the two right-hand products. Sparse Laurent polynomial arithmetic over the integers then gives zero for every coefficient of both claimed differences. The unnormalized numerator of `R` has 1,128 retained terms. The product-side numerator, before cancellation against `Delta R`, has 2,652 retained terms. The optional complete receipt records all these coefficients, and the compact receipt records their exact canonical SHA-256 digests.

Consequently the source-normalized Hamiltonians

\[
H_1=h_1+\omega(B-Ah_1)+O(\omega^2),\qquad
H_2=h_2+\omega(C-Ah_2)+O(\omega^2)
\]

Poisson commute through first order. The discarded denominator matters: at the rational point

\[
t=2,\quad x=(1,3,7),\quad y=(2,5,11),
\qquad R=\frac{8356261}{901120}\ne0.
\]

In the source's signed channels the raw first-order bracket is the negative of this number. In either channel convention a common power normalization `C_a/C_0^s` has first-order bracket proportional to `(1-s)R`; it therefore requires `s=1` as a formal identity.

## The full six-coefficient classification

Keep the two numerator corrections `B,C` fixed and replace the first denominator correction by

\[
\rho=\sum_{n\in\operatorname{perm}(-1,0,1)}\lambda_n f_n,
\qquad
\widetilde H_a=\frac{C_a}{1+\omega\rho}+O(\omega^2).
\]

The scalar coefficients `lambda_n` may depend on `t` but not on the positions or momenta. The equation for commutativity is

\[
T(\rho):=h_1\{\rho,h_2\}+h_2\{h_1,\rho\}=R=T(A).
\]

The six columns of `T`, after clearing `Delta^4`, have a six-by-six coefficient minor with determinant

\[
\boxed{-\frac{(t-1)^{14}}{t^8}.}
\]

The module constructs the columns from the actual symbolic bracket, selects the recorded rows, computes its determinant by exact sparse cofactor expansion, and compares every Laurent coefficient with the binomial expansion of this expression. Thus the determinant itself is globally certified.

For an explicit readable form, set

\[
a=\frac{(t-1)^2}{t},\qquad
b=\frac{(t-1)^2}{t^2},\qquad
c=\frac{(t-1)^3}{t}.
\]

Order the columns by `(-1,0,1),(-1,1,0),(0,-1,1),(0,1,-1),(1,-1,0),(1,0,-1)`. The selected matrix is

\[
\begin{pmatrix}
a&-a&0&0&0&0\\
0&b&0&0&0&0\\
0&0&-b&0&0&0\\
0&0&0&-c&0&0\\
0&0&0&0&c&0\\
-a&a&0&0&a&-a
\end{pmatrix},
\qquad \det=-a^2b^2c^2.
\]

Each row selects a momentum monomial and a position monomial in the denominator-cleared numerator:

| Row | Momentum exponent | Position exponent |
|---|---|---|
|1|(-1,2,2)|(0,5,7)|
|2|(-1,2,2)|(1,3,8)|
|3|(0,0,3)|(0,5,7)|
|4|(0,2,1)|(0,6,6)|
|5|(1,0,2)|(2,2,8)|
|6|(1,1,1)|(0,5,7)|

It follows that for every complex `t` other than zero and one, `T` is injective on this six-dimensional space. Since `A` supplies a solution, it supplies the unique solution:

\[
\boxed{\lambda_n=1\quad\text{for all six momentum vectors}.}
\]

At `t=1`, every `P_n/Delta` equals one, so all coefficients depend only on the momenta. Every Poisson bracket is zero and all six `lambda_n` are arbitrary. This classifies the entire exceptional coupling boundary of the stated ansatz. The value `t=0` is excluded because the original Laurent coefficients are undefined there. The result does not assert nonsingularity at collision positions `Delta=0`.

## Why this is not global normalizer uniqueness

For arbitrary position- and momentum-dependent `rho`, write `rho=A+chi`. Directly from the quotient rule,

\[
R-T(\rho)=h_2^2\{\chi,h_1/h_2\}.
\]

Thus, on the open set `h_2!=0`, the homogeneous freedom is the Poisson centralizer of `h_1/h_2`. In particular, constants and functions of `h_1,h_2` supply additional normalizers outside the six-function ansatz. This elementary identity prevents extending the proved finite classification to an unjustified global uniqueness claim.

## Reproduce and limits

Run `PYTHONPATH=src python -m unittest discover -s tests -p test_dell_normalization.py`. The public `normalization_receipt()` returns the global zero checks, exhaustive first-shell vectors, nonzero rational witness, symbolic minor, determinant factorization and explicit scope. Set `include_numerators=True` to retain all raw and product-side polynomial coefficients. The independent scalar-gradient test differentiates the original rational factors directly at three rational points, including the nontrivial negative coupling `t=-2`; it supplements the symbolic proof rather than replacing it.

This is a finite first-order structural theorem about a published DELL degeneration, new to this project's verified record. It does not construct an unknown self-dual DELL model, establish equivalence with other DELL formulations, prove full coordinate ellipticity, settle quantum ordering or establish all-order convergence. Its research value is an exact relation and a complete coupling boundary within a nontrivial normalization ansatz, together with a small independently replayable proof engine.

## Second momentum order is globally compatible

The finite polynomial proof was extended independently to the next momentum-nome coefficient. At coordinate nome zero, the complete cost-two shell gives

\[
C_0=1+\omega A+O(\omega^3),\quad
C_1=h_1+\omega B+\omega^2E+O(\omega^3),\quad
C_2=h_2+\omega C+\omega^2F+O(\omega^3),
\]

where `E` sums `f_n` over permutations of `(-1,0,2)` and `F` over permutations of `(-1,1,2)`. In particular there is no cost-two contribution to `C_0`. Expanding the actual quotient gives

\[
H_1=h_1+\omega(B-Ah_1)+\omega^2(E-AB+A^2h_1)+O(\omega^3),
\]
\[
H_2=h_2+\omega(C-Ah_2)+\omega^2(F-AC+A^2h_2)+O(\omega^3).
\]

The global `omega^2` coefficient of their Poisson bracket is a sum of three terms over `Delta^5`. Their denominator-cleared sparse numerators have respectively 19,902, 13,548 and 19,902 terms; their sum has zero terms. This is a rational identity in all positions, momenta and nonzero coupling, not a pointwise check. The public `second_order_normalization_receipt()` retains exact hashes of the three intermediate numerators and the zero result.

Now change the common denominator to `1+omega A+omega^2 rho2`, keeping the numerator modes fixed. Let `f_0,...,f_5` be the six first-shell functions in the earlier column order, and restrict

\[
\rho_2=\sum_{0\le i\le j\le5}\mu_{ij}f_i f_j.
\]

The new second-order bracket differs by the homogeneous linear expression `-T(rho2)`. The operator has 21 coefficient columns. One exact symbolic coefficient minor is

\[
-\frac{128(t-1)^{44}(t+1)^2(t+2)^5(t+3)^2(t^2+t+1)^3}{t^{31}}.
\]

Its value at `t=2` is `-77175/16384`. Thus the homogeneous correction is zero at generic coupling. The determinant is recomputed over integer Laurent polynomials and its entire factorization is checked coefficientwise; symbolic computer-algebra software is not needed for the retained proof.

## Complete second-order coupling boundary

The apparent exceptional values `t=-2,-3` in this minor are artifacts of the chosen rows. Exact full coefficient elimination at those two points supplies other nonzero 21-by-21 minors. All other possible nonzero exceptions are therefore `t=1,-1` and the primitive cubic roots of unity. At the cubic roots, the computation takes place in the exact quadratic field `Q(zeta)` with `zeta^2+zeta+1=0`.

The public `dell_normalization_boundary.quadratic_boundary_receipt()` replays the global determinant, constructs exact minors at the exceptional values, retains every parameter-kernel vector, and evaluates the corresponding functions themselves. This last step is essential: a dependency among the 21 chosen expressions is not a nonzero new normalizer.

| Coupling | Dimension of represented product functions | Rank of T | Dimension of nonzero functional normalizers |
|---|---:|---:|---:|
|all nonzero t outside 1,-1 and primitive cubic roots|21|21|0|
|t=-1|21|20|1|
|primitive cubic roots|19|19|0|
|t=1|19|0|19|

The `t=-1` case has one actual nonzero freedom. It is exactly an existing commuting integral:

\[
\boxed{\rho_2=c\,\frac{h_1h_2}{y_1y_2y_3},\qquad t=-1.}
\]

The product `Y=y_1y_2y_3` Poisson commutes with all functions of position ratios and momenta, so the quotient indeed commutes with `h_1` and `h_2`. Its representation in the 21-product ansatz is certified globally at `t=-1`. Explicitly, the generator is

\[
f_0f_3+f_0f_4+f_0f_5+f_1f_2+f_1f_4+f_1f_5
+f_2f_3+f_2f_5+f_3f_4.
\]

At either primitive cubic root, the two parameter-kernel directions are instead the zero-function identities

\[
f_1f_4-f_0f_5=0,\qquad f_2f_3-f_0f_5=0.
\]

Thus these couplings add no nonzero correction. At `t=1`, all coefficients reduce to one, and the 21 product expressions represent only 19 distinct momentum monomials. Every such momentum-only function is permitted. This completes the coupling classification of the stated second-order ansatz, while explicitly separating actual functional freedom from redundant parameters. None of these exceptional relations is promoted to a claim about an unknown full DELL system.

## A genuinely mixed two-nome identity

The polynomial proof also reaches beyond the coordinate-trigonometric degeneration. With the standard multiplicative nome `p`,

\[
\theta_p(z)=(1-z)\bigl[1-p(z+z^{-1})+O(p^2)\bigr].
\]

Consequently the coefficient of the actual coordinate-elliptic current is

\[
f_n(p)=f_n(0)\bigl[1+pS_n+O(p^2)\bigr],
\qquad
S_n=\sum_{i<j}\left[
(1-t^{n_i-n_j})\frac{x_i}{x_j}
+(1-t^{n_j-n_i})\frac{x_j}{x_i}\right].
\]

All `S_n` are explicit Laurent polynomials, so the same global denominator-clearing method applies. The public `mixed_nome_normalization_receipt()` verifies that every coefficient of the normalized Poisson bracket in the rectangle `0<=deg_p<=1`, `0<=deg_omega<=1` is zero. At mixed degree `p*omega`, the raw numerator has 3,696 terms and the normalizer product has 6,864 terms before their complete coefficientwise cancellation over `Delta^4`. The `p*omega^0` coefficient vanishes independently over `Delta^3`.

This is a finite **two-nome functional identity**, global in the other phase-space variables. It still does not establish the full elliptic identity at every coordinate-nome order. Combining the mixed identity with the earlier nonzero six-column minor gives a further finite classification: for every fixed `t!=0,1`, scalar coefficient series in the six-function denominator ansatz must satisfy

\[
\lambda_n(p)=1\pmod{p^2}.
\]

Indeed the constant coefficient equation fixes `lambda_n(0)=1`, and the next coefficient reduces to the invertible constant-order normalizer operator applied to `lambda'_n(0)`. This is a formal uniqueness statement through the specified order, not a convergence or all-order uniqueness theorem.

# A classified boundary for particlewise ellipticization

This result classifies one deliberately restrictive construction attempt.
It is new to this programme; worldwide priority has not been established.
It does not exclude double-elliptic systems, the Koroteev–Shakirov current,
position-dependent momentum moduli, changed coordinate weights, spin
variables, or non-particlewise couplings. Its purpose is to prove exactly
why replacing each Ruijsenaars momentum by one common elliptic profile is
insufficient when the old coordinate coefficients are retained.

The theorem concerns the full three-particle phase space. It is not asserted
as a theorem about a separately constrained or Dirac-reduced phase space.

## Setup and conventions

Use multiplicative canonical coordinates with

\[
 \{x_i,y_j\}=\delta_{ij}x_i y_j,\qquad
 \{x_i,x_j\}=\{y_i,y_j\}=0.
\]

For three distinct nonzero positions and coupling \(T\), put

\[
 a_I(x;T)=\prod_{i\in I,\,j\notin I}
                 \frac{Tx_i-x_j}{x_i-x_j}.
\]

The standard trigonometric RS Hamiltonians are
\(H_a=\sum_{|I|=a}a_I\prod_{i\in I}y_i\), for \(a=1,2\).
Their classical involutivity is the imported, attributed RS construction;
this project does not claim that classical result. Replace the momenta by
one scalar meromorphic profile \(f\):

\[
 H_1[f]=\sum_i a_{\{i\}}f(y_i),\qquad
 H_2[f]=\sum_{i<j}a_{\{i,j\}}f(y_i)f(y_j).
\]

Here and below, involutivity means an identity for all permitted positions
and independent momenta, rather than an equality on a finite point panel.
No momentum-dependent correction to \(a_I\) is allowed in this ansatz.

## Theorem: the complete coupling/profile boundary

Let \(f\) be meromorphic on a connected cover of \(\mathbb C^*\).
Suppose the above Hamiltonians Poisson commute identically.

If \(T=1\), all \(a_I=1\), so every profile works: the Hamiltonians depend
only on the mutually commuting momenta.

If \(T\ne1\), then either \(f\) is constant, or on every suitable local
logarithm chart

\[
 \boxed{f(y)=C y^\lambda.}
\]

The same \(\lambda\) continues throughout the connected cover. Conversely,
such a power profile multiplies the standard RS Poisson bracket by
\(\lambda\), so the imported RS involutivity supplies sufficiency.
If \(f\) is globally single-valued and meromorphic on \(\mathbb C^*\), then
\(\lambda\in\mathbb Z\). A nonconstant meromorphic function on a genuine
momentum elliptic curve \(\mathbb C^*/P^{\mathbb Z}\), \(0<|P|<1\), is
therefore impossible in this ansatz for every \(T\ne1\).

This is a sharp boundary of the declared ansatz. It is not a classification
of DELL systems.

## Exact two-witness proof

Write \(z_i=f(y_i)\), \(g_i=y_i f'(y_i)\), and
\(D_i=x_i\partial_{x_i}\). Direct differentiation gives

\[
 \{H_1[f],H_2[f]\}=\sum_i g_i P_i(z),\qquad
 P_i=(D_iH_1)\partial_{z_i}H_2-a_{\{i\}}D_iH_2.
\]

Every \(P_i\) is quadratic in \(z\) and of coupling degree at most four:
each \(a_I\) and \(D_i a_I\) has coupling degree at most two.

At \(x=(1,3,7)\), set \(z=(z,s,s)\). The exact identities are

\[
 P_1=K_1(T)s(s-z),\qquad
 P_2+P_3=-K_1(T)z(s-z),
\]

where indices in this document start at one, and

\[
 K_1(T)=\frac{5T^4-26T^3+126T-105}{72}.
\]

At \(x=(1,2,5)\), the same identities hold with

\[
 K_2(T)=\frac{7T^4-27T^3+90T-70}{16}.
\]

These are not numerical fits. The derivative compiler constructs every
quadratic monomial coefficient with rational arithmetic. For each witness,
the identities are replayed at the five distinct couplings \(0,1,2,3,4\).
The proved degree bound of four makes those five exact evaluations a
polynomial identity certificate valid for every complex coupling.

Let \(A=72K_1\) and \(B=16K_2\). Exact integer polynomial multiplication
certifies the Bezout identity

\[
\begin{aligned}
 &A(-529875-72145T+142128T^2)\\
 &\quad+B(835114+187859T-101520T^2)
       =2821105(T-1).
\end{aligned}
\]

Thus \(K_1\) and \(K_2\) have no common zero except \(T=1\). For every
other coupling, at least one coordinate witness gives, on substituting
\(y=(u,v,v)\),

\[
\boxed{
 \{H_1[f],H_2[f]\}
 =K(T)(f(v)-f(u))
       \bigl(f(v)u f'(u)-f(u)v f'(v)\bigr).
}
\]

If \(f\) is nonconstant, on a patch away from its zeros and poles the first
factor is nonzero for generic \(u,v\). Hence

\[
 \frac{u f'(u)}{f(u)}=\frac{v f'(v)}{f(v)}=\lambda.
\]

The identity theorem extends this relation across the connected domain.
Solving \(y f'=\lambda f\) gives the claimed local powers. Single-valued
continuation around zero requires \(e^{2\pi i\lambda}=1\), so \(\lambda\)
is integral on \(\mathbb C^*\). Momentum ellipticity would require
\(f(Py)=f(y)\), hence \(P^\lambda=1\). Since \(0<|P|<1\), the only integral
possibility is \(\lambda=0\), giving a constant profile. This completes the
analytic proof; the finite code certificate verifies its exact algebraic
premises, not the identity theorem itself.

## Abstract multiaffine lemma and persistence into the elliptic regime

The scalar-profile obstruction does not require the special form of the
trigonometric coefficients once one nonzero witness has been found.
Let

\[
 h_1(z)=\sum_i a_i(x)z_i,\qquad
 h_2(z)=\sum_{i<j}a_{ij}(x)z_i z_j
\]

be any multiaffine Hamiltonian pair on the same multiplicative canonical
phase space. Assume \(\{h_1(y),h_2(y)\}=0\) identically. The same derivative
formula defines quadratic polynomials \(P_i\), and base involutivity says

\[
 z_1P_1+z_2P_2+z_3P_3=0.
\]

At \(z=(z,s,s)\), therefore,

\[
 P_2+P_3=-\frac zs P_1,
\qquad
 \{h_1[f],h_2[f]\}
 =P_1(f(u),f(v),f(v))
       \left(uf'(u)-\frac{f(u)}{f(v)}vf'(v)\right).
\]

**Lemma.** If, at some permitted coordinate point, the polynomial
\(P_1(z,s,s)\) is not identically zero, any nonconstant common meromorphic
profile preserving commutativity must satisfy \(yf'/f=\lambda\).

To prove the lemma, restrict away from zeros and poles of \(f\). A
nonconstant meromorphic function has open image there. Consequently the
substitution of two independent values \(f(u),f(v)\) into a nonzero
polynomial cannot vanish identically. On the resulting nonempty open set
the second factor must vanish; the meromorphic identity theorem extends
that equality. This reproduces the scalar ODE and the power classification.
The lemma is conditional on base involutivity and on a nonzero witness.
It does not assert either premise for an arbitrary proposed model.

Now suppose the coefficients are holomorphic in the coordinate elliptic
nome \(P\) near zero, remain multiaffine in the momenta, commute before
substitution, and specialize to the above standard RS coefficients at
\(P=0\). Standard elliptic RS, in a consistently normalized momentum
chart, supplies the motivating example. For every fixed nonzero
\(T\ne1\), choose
one of our two coordinate witnesses with \(K_r(T)\ne0\). At \(z=2,s=3\),

\[
 P_1(2,3,3;P)=3K_r(T)+O(P).
\]

The constant term is nonzero. Thus there exists \(\delta(T)>0\) such that
the abstract lemma applies for every \(|P|<\delta(T)\), including genuinely
elliptic \(P\ne0\). This is an analytic neighborhood theorem, not an
extrapolation from finitely many nome coefficients. No explicit radius is
computed. On any connected domain on which this same witness is
holomorphic and extends from zero, its zero set is discrete. The lemma
therefore also applies away from that discrete set. No assertion is made
at the exceptional zeros, at poles of the chosen chart, or uniformly for
all elliptic moduli.

There is a parallel formal statement. If the coefficients are formal power
series in \(P\), and \(f(y;P)\) has nonconstant leading profile, the nonzero
constant witness makes \(P_1(f(u;P),f(v;P),f(v;P))\) a nonzero formal
series of meromorphic functions. Cancellation in that integral domain
again forces

\[
 y\partial_y f(y;P)=\lambda(P)f(y;P),\qquad
 f(y;P)=C(P)y^{\lambda(P)}
\]

on a logarithm cover. If every coefficient is globally single-valued and
meromorphic on \(\mathbb C^*\), the leading exponent is integral and every
higher coefficient of \(\lambda(P)\) must vanish: its first nonzero term
would introduce a forbidden \(\log y\). Thus only \(C(P)y^m\), with a fixed
integer \(m\), survives. This formal assertion assumes a nonconstant
leading profile and does not classify singular expansions whose leading
profile degenerates to a constant.

## First-order obstruction and exact negative control

For a formal scalar substitution
\(f_\epsilon(y)=y+\epsilon h(y)+O(\epsilon^2)\), the same witness gives

\[
\begin{aligned}
 [\epsilon]\{H_1,H_2\}
  =K(T)(v-u)\bigl[&v(uh'(u)-h(u))\\
                 &-u(vh'(v)-h(v))\bigr].
\end{aligned}
\]

Thus a first-order correction in this ansatz satisfies
\(y h'(y)-h(y)=\kappa y\), and therefore

\[
 h(y)=y(c+\kappa\log y).
\]

The logarithmic term changes the local exponential slope; it is excluded
for single-valued meromorphic corrections on \(\mathbb C^*\). Only the
overall scaling \(h=cy\) survives there. Any nontrivial positive or negative
Laurent mode is obstructed in this unchanged-weight scalar ansatz.

For a completely explicit negative control, take \(T=2\), \(x=(1,3,7)\),
\(y=(2,3,3)\), and \(f_\epsilon(y)=y+\epsilon/y\). Exact expansion gives

\[
 \boxed{\{H_1,H_2\}=-\frac{95}{216}\epsilon
                         +\frac{95}{1296}\epsilon^2.}
\]

The constant and cubic coefficients are exactly zero. This one example is
not the classification proof; it is a replayable sign-sensitive control.
The implementation also checks multiple power profiles as positive controls
and verifies that \(T=1\) has zero coordinate derivatives for every profile.

## Relation to published DELL constructions

Koroteev and Shakirov, *The Quantum DELL System*,
[arXiv:1906.10354](https://arxiv.org/abs/1906.10354), equations (1.10)–(1.11),
define Hamiltonians by normalized Fourier modes of an infinite current.
That current introduces mixed momentum shifts and changes the interaction
coefficients together with the shifts. It lies outside the ansatz classified
here, so the theorem neither contradicts nor proves their conjecture.

The standard RS involutivity used for sufficiency is classical: see
S. N. M. Ruijsenaars, *Complete integrability of relativistic Calogero–Moser
systems and elliptic function identities*, Communications in Mathematical
Physics **110** (1987), 191–213,
[doi:10.1007/BF01207363](https://doi.org/10.1007/BF01207363).
Our elementary obstruction proof fixes the nonsymmetric multiplicative
coefficient convention explicitly and does not identify its momentum chart
with an unadjusted oriented-theta current convention.

The theorem motivates testing coupled corrections, altered coordinate
coefficients, or position-dependent momentum geometry. It does not establish
that any one of those enlargements is sufficient, nor does it select a unique
new interaction or prove a quantum double-elliptic identity.

## A forced mixed harmonic in the normalized current

The normalization itself produces mixed momentum harmonics. To make signs
unambiguous, write the sign-stripped classical current modes as

\[
 A_a=\sum_{\sum n_i=a}
 W^{\sum_i n_i(n_i-1)/2}
 \prod_{i<j}\frac{\theta(T^{n_i-n_j}x_i/x_j;P)}
                       {\theta(x_i/x_j;P)}\,y^n.
\]

The actual Fourier mode of the KS current with \((-z)^{\sum n_i}\) is
\(O_a=(-1)^a A_a\). At order \(W^0\), \(A_0=1\). At order \(W^1\), the
charge-one numerator \(A_1\) has precisely the three permutations of
\((-1,1,1)\); the charge-zero denominator has precisely the six permutations
of \((-1,1,0)\). This enumeration is exhaustive because each cost
\(n_i(n_i-1)/2\) is nonnegative and cost at most one forces
\(n_i\in\{-1,0,1,2\}\).

For the positive-sign Hamiltonian \(\widetilde H_1=A_0^{-1}A_1\), the first
nome correction is \(A_1^{[1]}-A_0^{[1]}A_1^{[0]}\). Its momentum harmonic
\((-1,2,0)\) receives no contribution from \(A_1^{[1]}\), and exactly one
contribution from the normalization product:

\[
 [W y_1^{-1}y_2^2]\widetilde H_1
 =-c_{(-1,1,0)}c_{(0,1,0)},\qquad
 c_n=\prod_{i<j}\frac{\theta(T^{n_i-n_j}x_i/x_j;P)}
                              {\theta(x_i/x_j;P)}.
\]

At \(P=0,T=2,x=(1,3,7)\), these factors are exactly
\(143/384\) and \(5/16\), giving \(-715/6144\). For the actual KS
Hamiltonian \(H_1=O_0^{-1}O_1=-\widetilde H_1\), the coefficient is
\(+715/6144\). The sign is a Hamiltonian convention; nonvanishing is not.
The theta-product expression establishes generic nonvanishing, and the
exact rational value supplies an independent replay.

This mode is forced within the specified normalized current; it cannot be
represented by its original finite positive subset momentum support.
It is not by itself evidence of a novel interaction: even at \(T=1\), where
all coefficients become position-independent and commutativity is trivial,
the same normalization creates mixed harmonics. Nor does this support
calculation prove full classical or quantum DELL commutativity.

## Reproduction

`src/perfectjet/dell_obstructions.py` contains the exact differentiation
compiler, the two coupling-polynomial certificates, the integer Bezout
identity, the negative control and JSON-safe receipt.
`tests/test_dell_obstructions.py` independently checks diagonal identities
outside the interpolation panel, alternative position witnesses, power
profiles, the complete inverse-mode counterexample and input rejection.

Run `PYTHONPATH=src python -m unittest discover -s tests -p test_dell_obstructions.py -v`.

# Formal structure, independence and reduction

These statements concern the literal normalized Koroteev–Shakirov current
defined in DELL_RESEARCH.md. They are structural properties of that published
family, not a new construction of an integrable system. In particular,
functional independence is logically separate from Poisson commutativity.

## Finite shells and all-order identities

For an integer vector n, let E(n)=sum_i n_i(n_i-1)/2 and a=sum_i n_i.
Each summand is nonnegative. Therefore every coefficient of a fixed power
of the momentum nome W is a finite sum, at every particle number N.
The current and its inverse normalization are well-defined formal series
over the meromorphic coefficient field away from theta denominator divisors.
No analytic convergence is inferred from this formal construction.

The pair coefficients depend on X_i/X_j and n_i-n_j. Consequently

\[
\sum_i X_i\partial_{X_i}C_a=0,\qquad
\sum_i Y_i\partial_{Y_i}C_a=aC_a.
\]

Since C_0 has momentum charge zero, its formal inverse does also. Thus
the same identities hold for H_a=C_0^{-1}C_a. For the convention
{log X_i,log Y_j}=delta_ij and Y_all=product_i Y_i,

\[
\{H_a,Y_{\rm all}\}=Y_{\rm all}\sum_i X_i\partial_{X_i}H_a=0.
\]

Simultaneous scaling of every X_i is the Hamiltonian symmetry generated
locally by log Y_all. On its regular symplectic quotient at fixed nonzero
Y_all, the H_a descend to N-1 degrees of freedom. This establishes descent,
not full integrability. In the quantum action convention, the total shift
likewise commutes with all coefficient functions of coordinate ratios.

Shifting n to n+(1,...,1) adds a to E(n) and N to the charge. This proves
the all-order signless recurrence

\[
C_{a+N}=W^aY_{\rm all}C_a.
\]

For negative a it is interpreted in the formal Laurent extension; the
minimum energy in the relevant modes makes the literal sums consistent.
The original signed modes acquire the additional factor (-1)^N.

## Generic functional independence

At P=W=0 and T=1, every coefficient F_n equals one. Only entries n_i=0,1
have zero momentum energy, hence H_a=e_a(Y_1,...,Y_N), the elementary
symmetric polynomial. The Jacobian identity is

\[
\boxed{\det\frac{\partial(e_1,\ldots,e_N)}
{\partial(\log Y_1,\ldots,\log Y_N)}
=\Bigl(\prod_iY_i\Bigr)\prod_{i<j}(Y_i-Y_j).}
\]

For a proof, the ordinary-coordinate determinant is alternating under a
permutation of variables, has degree N(N-1)/2, and its leading coefficient
agrees with the displayed Vandermonde. Multiplying column j by Y_j gives
the logarithmic formula. In particular it is nonzero for distinct nonzero
momenta. The code independently constructs all elementary derivatives and
checks the determinant at exact rational momenta for N=2,...,8. Those finite
replays accompany the polynomial proof; they do not replace it.

The leading rational Jacobian in T,X,Y therefore is not identically zero.
Adding formal powers of P,W cannot erase that nonzero leading coefficient.
This proves generic formal functional independence of
H_1,...,H_(N-1),Y_all for every N. The nonzero locus is understood in the
parameter-dependent meromorphic function field; no claim is made that all
couplings or all phase points are regular. On regular moment-map levels,
independence of these N functions gives independence of the N-1 descended
H_a after symplectic reduction. Our finite classical receipts also retain
actual nonzero leading determinants at interacting rational couplings.

This conclusion holds for the normalized formal family regardless of
whether the outstanding all-order commutativity question is solved. It is
not a convergence theorem, a global action-angle construction, or a proof
of position–momentum self-duality.

## The quantum and classical sign convention

For coefficient-left shifts, (f S^n)(g S^m)=f g(Q^n X) S^(n+m).
Writing Q=exp(h), its first commutator coefficient is
f sum_i n_i X_i partial_i g - g sum_i m_i X_i partial_i f.
This equals minus the classical bracket used above on the symbols
fY^n and gY^m. Thus Q=exp(-h) gives the positive semiclassical convention.
An overall Poisson sign does not affect involutivity, but the action and
the sign must be fixed before comparing formulas. Freezing the translated
coefficient would destroy this semiclassical correspondence.

## Stable DELL relation records

| ID | Relation | Status and hypotheses |
|---|---|---|
| PJ-D001 | theta(Z;P)=(1-Z)*prod_(m>=1)(1-P^m)(1-P^m Z)(1-P^m/Z) | definition: P is the standard multiplicative coordinate nome; in Koroteev-Shakirov equation3.3 it equals the square of the paper's p. Theta ratios cancel the scalar product factors. |
| PJ-D002 | E(n)=sum_i n_i(n_i-1)/2; charge(n)=sum_i n_i | definition: Integer n_i; E is nonnegative and the momentum nome is W. Position nome P and momentum nome W are independent formal parameters. |
| PJ-D003 | C_a=sum_(charge(n)=a) W^E(n)*F_n(X;T,P)*Y^n; F_n=prod_(i<j)theta(T^(n_i-n_j)Xi/Xj;P)/theta(Xi/Xj;P) | definition: The published Koroteev-Shakirov current is reconstructed with the common coordinate Vandermonde divided out and the overall (-1)^a mode sign removed. This defines the tested model; it is not a new DELL construction. |
| PJ-D004 | (M C0)^(-1)*(M Ca)=C0^(-1)*Ca | derived: Associative operator algebra; M and C0 are invertible in the declared completion. No commutativity of factors is assumed. This identifies raw and theta-ratio current conventions after left normalization. |
| PJ-D005 | C0=1+sum_(r>=1)W^r A_r; H_a^[r]=C_a^[r]-sum_(j=1)^r A_j*H_a^[r-j] | derived: H_a=C0^(-1)*Ca; products are ordinary for classical functions and ordered for quantum difference operators. Every coefficient uses finitely many earlier coefficients. |
| PJ-D006 | C_(a+N)=W^a*(Y1*...*YN)*C_a | derived: For the literal signless current, shift every n_i by1. Ratios depend only on differences. In the quantum action convention the total shift commutes with all coordinate-ratio coefficients. Formal Laurent W interpretation handles negative a. |
| PJ-D007 | E(n)<=M => n_i(n_i-1)/2<=M for each i | derived: All scalar summands are nonnegative on integers. Enumerating precisely this finite coordinate range and filtering total E and charge is exhaustive at every declared momentum order. |
| PJ-D008 | {F,G}=sum_i[(Xi*d_Xi F)(Yi*d_Yi G)-(Yi*d_Yi F)(Xi*d_Xi G)] | definition: Classical independent nonzero multiplicative coordinates. Exact jet derivatives are computed before rational specialization; evaluating a zero bracket at finitely many points alone is not a global identity proof. |
| PJ-D009 | {H_i^0,H_j^r}+{H_i^r,H_j^0}=-sum_(s=1)^(r-1){H_i^s,H_j^(r-s)} | derived: Coefficient equation for formal Poisson commutativity. The new order enters linearly; no general solvability or completeness is asserted. |
| PJ-D010 | H_i^1 -> H_i^1+{H_i^0,G} | derived: An infinitesimal canonical change of coordinates. This is a gauge equivalence of first-order corrections, not a classification of all DELL systems. |
| PJ-D011 | C0=1+WA+O(W²); C1=h1+WB+O(W²); C2=h2+WC+O(W²); H1=h1+W(B-Ah1); H2=h2+W(C-Ah2) | derived: Coordinate nome P=0; A has six permutation shifts(-1,0,1), B has three shifts(-1,1,1), C has three shifts(2,0,0). Equations use signless oriented coefficients. |
| PJ-D012 | {h1,h2}=0; {B,h2}+{h1,C}=h1*{A,h2}+h2*{h1,A}=R | exact_checked: Classical N=3,P=0. Sparse Laurent-polynomial numerator cancellation proves rational identities in symbolic T,X,Y; this is stronger than sampled evaluations, and is only first order in W. |
| PJ-D013 | {C1/C0^s,C2/C0^s}=W*(1-s)*R+O(W²); R(2;(1,3,7);(2,5,11))=8356261/901120 | derived: Classical P=0,N=3; common exponent s. The nonzero exact witness forces s=1 for an identity over generic parameters. Not a full normalizer classification outside this ansatz. |
| PJ-D014 | rho=sum_(n in perm(-1,0,1))lambda_n(T)*F_n*Y^n; {C1/(1+W rho),C2/(1+W rho)}=O(W²) iff all lambda_n=1 | derived: Classical N=3,P=0. The lambda_n depend on coupling T only. Valid at T!=0,1; the exact rank certificate excludes further exceptional nonzero couplings within these six fixed functions. |
| PJ-D015 | det(M6(T))=-(T-1)^14/T^8; rank(M)=6 for T!=0,1; rank(M)\|T=1=0 | exact_checked: M6 is the retained six-row coefficient minor of the normalizer compatibility map. At T=1 the six coefficients are unconstrained at first order. Zero coupling is excluded by the Laurent current definition. |
| PJ-D016 | a_I(X;T)=prod_(i in I,j notin I)(T Xi-Xj)/(Xi-Xj); H1f=sum_i a_i f(Yi); H2f=sum_(i<j)a_ij f(Yi)f(Yj) | definition: N=3 and unchanged standard coordinate coefficients; one common meromorphic particlewise momentum profile f. This ansatz is narrower than a general DELL family. |
| PJ-D017 | {H1f,H2f}\|X=(1,3,7),Y=(u,v,v)=K(T)*(f(v)-f(u))*(f(v)*u*fprime(u)-f(u)*v*fprime(v)) | exact_checked: K1(T)=(5T^4-26T^3+126T-105)/72. A second coordinate witness X=(1,2,5) has K2(T)=(7T^4-27T^3+90T-70)/16; a retained Bezout identity proves the only common coupling root is T=1. |
| PJ-D018 | {H1f,H2f}=0 and T!=1 => Y*fprime(Y)/f(Y)=lambda => f(Y)=C*Y^lambda locally | derived: Two independent coordinate witnesses and an exact Bezout identity close all exceptional couplings except T=1. Nonconstant meromorphic f on a connected logarithmic cover gives local powers; globally single-valued on C* forces integer lambda. At T=1 arbitrary momentum profiles commute. |
| PJ-D019 | f(PY)=f(Y),0<abs(P)<1 and f(Y)=C*Y^m,m in Z => m=0 | derived: Together with the classified unchanged-coordinate ansatz this excludes nonconstant single-valued elliptic particlewise profiles at T!=1. It does not exclude general double-elliptic systems or coupled momentum interactions. |
| PJ-D020 | f(Y)=Y+epsilon/Y => {H1f,H2f}\|T=2,X=(1,3,7),Y=(2,3,3)=-95epsilon/216+95epsilon²/1296 | exact_checked: An exact nonzero first-order direction within the particlewise ansatz. This is a Laurent test profile, not itself an elliptic function; monomial profiles provide positive controls. |
| PJ-D021 | [W Y^(-1,2,0)]H1=-F_(-1,1,0)*F_(0,1,0) | derived: N=3 signless normalized current; the numerator first shell has no(-1,2,0) mode, while C0^(-1)C1 supplies this product. Nonzero generic meromorphic coefficient; no assertion of a new unknown Hamiltonian. |
| PJ-D022 | (f(X)*S^n)*(g(X)*S^m)=f(X)*g(Q^n X)*S^(n+m) | definition: Literal action S_i f(X)=f(X1,...,Q Xi,...,XN). Q is the quantum shift parameter, distinct from both elliptic nomes; finite coefficient checks do not prove the full quantum commutativity conjecture. |
| PJ-D023 | Ca*C0^(-1)=C0*(C0^(-1)*Ca)*C0^(-1) | derived: Invertible C0 in an associative completed operator algebra. Left and right families have equivalent commutativity; right normalization is not a valid noncommutativity negative control. |
| PJ-D024 | [H1,H2]_(W^r P^s)=sum_(a+b=r,c+d=s)(H1^[a,c]*H2^[b,d]-H2^[a,c]*H1^[b,d]) | definition: Every ordered output-shift coefficient is tested exactly at the declared rational parameter specializations and finite truncation. The retained receipt, rather than this formula, records which bounded panels actually passed. |
| PJ-D025 | [W^2]{C0^(-1)C1,C0^(-1)C2}=0 at P=0 | exact_checked: N=3, rational identity in symbolic T,X,Y. The three exact numerators over Delta^5 have19902,13548,19902terms and cancel coefficientwise. This is finite-order commutativity, not all-order integrability. |
| PJ-D026 | det M21=-128*(T-1)^44*(T+1)^2*(T+2)^5*(T+3)^2*(T^2+T+1)^3/T^31 | exact_checked: P=0,N=3. A21function ansatz of symmetric products of first-shell functions has generic full rank. Hence no nonzero W² denominator correction in that ansatz at couplings where this minor is nonzero. A vanishing minor alone does not prove a rank drop. |
| PJ-D027 | [W^a P^b]{H1,H2}=0 for a,b in {0,1} | exact_checked: N=3. Exact Laurent-polynomial identities in all T,X,Y, with P the product nome. The mixed raw3696terms and normalizer6864terms cancel after denominator clearing; no extrapolation to all elliptic orders. |
| PJ-D028 | lambda_n(T,P)=1 mod P² for all six first-shell functions | derived: The global mixed-nome identity supplies a solution; the invertible constant-coordinate-nome minor makes both coefficients unique for each fixed T!=0,1. Numerator modes and six-function normalizer ansatz are fixed. |
| PJ-D029 | sum_i zi Pi(z)=0 => {H1[f],H2[f]}\|z2=z3=s=P1(z,s,s)*(g(u)-z*g(v)/s) | derived: g(y)=y*fprime(y),z=f(u),s=f(v),s!=0. Base Hamiltonians are multiaffine and commute in log-canonical variables. A nonzero restricted P1 polynomial forces a nonconstant common profile to be a local power. |
| PJ-D030 | T!=0,1 and abs(P)<delta(T) => no nonconstant elliptic particlewise profile in the unchanged elliptic-RS ansatz | derived: Conditional on the standard commuting multiaffine elliptic-RS weights holomorphic near P=0 with the declared trigonometric limit. A nonzero P=0 witness persists analytically. No numerical delta or all-moduli classification is claimed. |
| PJ-D031 | sum_i Xi*d_Xi H_a=0; sum_i Yi*d_Yi H_a=a*H_a; {H_a,Y_all}=0 | derived: Directly from current coefficients depending on coordinate ratios and fixed momentum charge. The formal Hamiltonians descend under regular simultaneous-position-scaling reduction at fixed nonzero Y_all. |
| PJ-D032 | det d(e1,...,eN)/d(logY1,...,logYN)=(prod_i Yi)*prod_(i<j)(Yi-Yj) | derived: At P=W=0,T=1 the normalized currents give elementary symmetric polynomials. This nonzero specialization proves generic independence of H1,...,H_(N-1),Y_all and their regular reduced family in the formal deformation; it does not prove commutativity or convergence. |
| PJ-D033 | dim ker(T on actual productfunctions)=1 at T=-1;19 at T=1;0 at all other nonzero T | derived: The first denominator shell is fixed to A and the second correction lies in products of its six functions. Three symbolic21minors and exact exceptional-field rank certificates classify all nonzero couplings. Function-space dependencies are quotiented out. |
| PJ-D034 | rho_star=H1^0*H2^0/Y_all at T=-1; {rho_star,H1^0/H2^0}=0 | exact_checked: A retained nine-product expansion proves membership in the second-order normalizer ansatz. This is one nonzero homogeneous normalizer direction, not a new independent conserved quantity. |
| PJ-D035 | f1*f4=f0*f5; f2*f3=f0*f5 when T²+T+1=0 | exact_checked: Zero-based f_i order is lexicographic perm(-1,0,1). The21nominal products span19actual functions. The two coefficient-kernel directions represent identically zero functions, so they give no new normalizer freedom. |
