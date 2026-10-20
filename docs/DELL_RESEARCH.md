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
