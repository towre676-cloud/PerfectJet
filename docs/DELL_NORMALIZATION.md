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
