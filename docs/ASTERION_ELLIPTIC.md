# The rank-eight classical dynamical elliptic E8 r-matrix

`src/perfectjet/asterion_elliptic.py` implements the classical Felder r-matrix for the actual 248-dimensional E8 algebra, with a spectral parameter and eight independent dynamical coordinates. It computes exact rational coefficients of its theta-product expansion, all eight dynamical derivatives, the full tensor classical dynamical Yang–Baxter equation (CDYBE), and its trigonometric and rational degenerations. The analytic all-orders statement is a classical theorem: the proof below reduces every possible E8 tensor coefficient to the theta addition identity. The finite series checks are additional implementation evidence, with their precision and specialization recorded explicitly.

This closes a classical dynamical elliptic compatibility problem. It does not construct a quantum R-matrix, an elliptic quantum group, an all-genus quantization, or a deformation of the 248-dimensional Lie bracket. In particular it does not remove the previously established obstruction to obtaining the principal Drinfeld–Jimbo cobracket merely by changing the Asterion basis.

## Theta normalization and domain

Put \(p=e^{2\pi i\tau}\), with \(\operatorname{Im}\tau>0\), and use additive coordinates \(z,x\) and multiplicative coordinates \(X=e^z,Y=e^x\). Define

\[
 B(X;p)=\prod_{n\ge1}
 \frac{(1-p^nX)(1-p^n/X)}{(1-p^n)^2},\qquad
 \Theta(z;p)=(e^{z/2}-e^{-z/2})B(e^z;p).
\]

Then \(\Theta\) is odd and \(\Theta'(0)=1\), since \(B(1;p)=1\). Its quasiperiods are \(2\pi i\) and \(\log p\), and its simple zeros form
\(\Lambda=2\pi i\mathbb Z+\log(p)\mathbb Z\). Explicitly,

\[
 \Theta(z+2\pi i)=-\Theta(z),\qquad
 \Theta(z+\log p)=-p^{-1/2}e^{-z}\Theta(z).
\]

This is the usual odd theta normalized to derivative one and rescaled from quasiperiods \((1,\tau)\): if \(\theta'(0)=1\) in that convention, then \(\Theta(z)=2\pi i\,\theta(z/(2\pi i))\). These quasiperiods are not assertions that theta is doubly periodic.

The scalar kernels are

\[
 \rho(z)=\frac{\Theta'(z)}{\Theta(z)},\qquad
 \Phi(z,x)=\frac{\Theta(z+x)}{\Theta(z)\Theta(x)}.
\]

The dynamical and spectral domain is the complement of \(x_\alpha\in\Lambda\) and \(z\in\Lambda\); for CDYBE the three differences \(u,v,w=u+v\) must avoid \(\Lambda\). Zeros of the numerator at \(z+x\in\Lambda\) are regular and permitted. The formula defines a meromorphic identity, so equality extends across removable exceptional points. Formal cusp computations require \(X,Y\ne0,1\); they do not claim that these conditions alone describe the analytic domain at a fixed nonzero nome.

The module's \(p\) is the conventional character nome \(q\), and equals \(Q^2\) in `asterion_periods.py`, where \(Q=e^{\pi i\tau}\). No half-nome substitution is made in the elliptic series.

## The actual E8 tensor and the derivative convention

Let \(A\) be the symmetric E8 Cartan matrix in `asterion_e8.py`. The invariant form is normalized by

\[
 B(h_i,h_j)=A_{ij},\qquad B(e_\alpha,e_{-\alpha})=1,\qquad (\alpha,\alpha)=2.
\]

The Cartan and full Casimir tensors are

\[
 \Omega_{\mathfrak h}=\sum_{i,j}(A^{-1})_{ij}h_i\otimes h_j,
 \qquad
 \Omega=\Omega_{\mathfrak h}+\sum_{\alpha\in R}e_\alpha\otimes e_{-\alpha}.
\]

The implementation checks invariance of the complete 304-term Casimir under all sixteen simple raising and lowering generators, and checks all 240 root-metric gradients. Since those generators generate E8, their invariance checks imply full Lie-algebra invariance. All 64 inverse-Cartan coefficients are retained.

Take \(\lambda\in\mathfrak h^*\) and use the coordinates \(\lambda_i=\lambda(h_i)\). Identifying roots and coroots through the normalized form gives

\[
 h_\alpha=\sum_i\alpha_i h_i,\qquad
 x_\alpha=(\lambda,\alpha)=\lambda(h_\alpha)=\sum_i\alpha_i\lambda_i.
\]

The implemented meromorphic tensor is

\[
 \boxed{r(z,\lambda)=\rho(z)\Omega_{\mathfrak h}
       +\sum_{\alpha\in R}\Phi(z,x_\alpha)e_\alpha\otimes e_{-\alpha}.}
\]

It has zero total Cartan weight, satisfies spectral unitarity
\(r^{21}(-z,\lambda)=-r(z,\lambda)\), and has residue
\(\operatorname{Res}_{z=0}r(z,\lambda)=\Omega\). Its eight derivatives are

\[
 \partial_{\lambda_i}r(z,\lambda)
 =\sum_\alpha\alpha_i\partial_x\Phi(z,x_\alpha)e_\alpha\otimes e_{-\alpha}.
\]

There is no additional inverse Cartan factor in this derivative: the chosen coordinates are the evaluations on \(h_i\). The inverse Cartan factor belongs in \(\Omega_{\mathfrak h}\). This is checked by \(A^{-1}A\alpha=\alpha\) for every root.

For \(r^{12}=r^{12}(u,\lambda)\), \(r^{13}=r^{13}(w,\lambda)\), \(r^{23}=r^{23}(v,\lambda)\), the precise equation is

\[
 \sum_{i=1}^8\left(h_i^{(1)}\partial_i r^{23}
 -h_i^{(2)}\partial_i r^{13}+h_i^{(3)}\partial_i r^{12}\right)
 +[r^{12},r^{13}]+[r^{12},r^{23}]+[r^{13},r^{23}]=0.
\]

This matches the plus-kernel convention in Etingof's Example 3. Felder's original \(\sigma(a,z)=\Theta(a-z)/(\Theta(a)\Theta(z))\) uses a different sign convention: our tensor is his \(\Omega(z,-\lambda)\), and changing \(\lambda\) to \(-\lambda\) changes the derivative sign accordingly.

## An analytic all-orders proof by scalar coefficients

The normalized odd theta obeys the classical addition identity

\[
 \Theta(A-C)\Theta(A+C)\Theta(B-D)\Theta(B+D)
 =\Theta(A-B)\Theta(A+B)\Theta(C-D)\Theta(C+D)
  +\Theta(A-D)\Theta(A+D)\Theta(B-C)\Theta(B+C).
\]

Its specialization with \(w=u+v\) gives the scalar Fay identity

\[
 F(u,v,a,b):=
 \Phi(u,-b)\Phi(w,a+b)
 -\Phi(u,a)\Phi(v,a+b)
 +\Phi(w,a)\Phi(v,b)=0. \tag{F}
\]

For completeness, multiplying (F) by
\(\Theta(u)\Theta(v)\Theta(w)\Theta(a)\Theta(b)\Theta(a+b)\) reduces it to

\[
 \Theta(w+a)\Theta(v+b)\Theta(u)\Theta(a+b)
 =\Theta(u-b)\Theta(w+a+b)\Theta(v)\Theta(a)
 +\Theta(u+a)\Theta(v+a+b)\Theta(w)\Theta(b).
\]

This is exactly the displayed addition identity after taking
\(A=(u+2v+a+b)/2\), \(B=(u+a+b)/2\),
\(C=(b-u-a)/2\), \(D=(a+b-u)/2\), using oddness for the two negative arguments in its first right-hand product.

The opposite-root limit uses \(b=-a+\varepsilon\) and
\(\Phi(z,\varepsilon)=\varepsilon^{-1}+\rho(z)+O(\varepsilon)\). The pole terms in (F) cancel. Its constant term, followed by interchanging \(u\) and \(v\), is

\[
 G(u,v,a):=\partial_a\Phi(v,a)
 +(\rho(u)-\rho(w))\Phi(v,a)
 -\Phi(u,-a)\Phi(w,a)=0. \tag{G}
\]

This derivative identity is essential. The ordinary CYBE, obtained by deleting the dynamical derivatives, does not hold for this tensor.

All summands have weight zero, and the bracket preserves weight, so a possible tensor coefficient has one of the following forms:

| Tensor type | Number of possible ordered coefficients | Reduction |
|---|---:|---|
| Three Cartan vectors | 512 | Zero because the Cartan subalgebra is abelian and the Cartan coefficients are independent of \(\lambda\) |
| One Cartan vector and two opposite roots | 5,760 | One of the three derivative identities below, multiplied by a root coordinate |
| Three roots summing to zero | 13,440 | A structure-constant sign times (F) |

There are 19,712 possible weight-zero coefficients in total. All other coefficients vanish by weight. These counts describe the possible weight-zero space; some of its opposite-root coordinates vanish individually because the corresponding root coordinate is zero.

For \(\alpha+\beta+\gamma=0\), write \(a=x_\alpha,b=x_\beta\). Invariance and skew symmetry give the nonzero sign relation

\[
 N_{-\beta,-\gamma}=-N_{-\alpha,-\gamma}=N_{-\alpha,-\beta}.
\]

The coefficient of \(e_\alpha\otimes e_\beta\otimes e_\gamma\) is consequently \(N_{-\beta,-\gamma}F(u,v,a,b)\). The program independently checks this sign relation against the actual E8 bracket table for all 13,440 ordered pairs with \(\alpha+\beta\) a root.

The coefficients with the Cartan vector in the first, second and third slot are, respectively, \(\alpha_i\) times

\[
 G(u,v,a),\qquad
 -\partial_a\Phi(w,a)+(\rho(u)+\rho(v))\Phi(w,a)
       -\Phi(u,a)\Phi(v,a),\qquad
 G(v,u,a).
\]

The middle expression equals \(-G(-u,w,a)\), using
\(\rho(-u)=-\rho(u)\) and \(\Phi(-u,-a)=-\Phi(u,a)\). Thus all three vanish analytically. The module also checks all three arrangements at every one of the 240 roots. This exhausts the CDYBE coefficients and proves the analytic identity to all nome orders from the classical theta addition theorem. Finite series agreement is not being used as a substitute for that theorem.

## Exact computation, degenerations and retained evidence

The exact series engine never evaluates theta numerically. The rational product ratio is

\[
 \Phi(X,Y;p)=\frac{XY-1}{(X-1)(Y-1)}
             \frac{B(XY;p)}{B(X;p)B(Y;p)},
\]

and

\[
 \rho(X;p)=\frac{X+1}{2(X-1)}
   +\sum_{m\ge1}\left(\sum_{k\mid m}(X^{-k}-X^k)\right)p^m.
\]

`dphi` differentiates with \(Y\partial_Y\). Its expression uses only derivatives of \(B\) and the rational prefactor, so it stays defined at \(XY=1\). In particular it avoids multiplying a zero kernel by the singular expression \(\rho(z+x)-\rho(x)\) at a numerator zero.

At \(p=0\),

\[
 \rho_0(z)=\tfrac12\coth(z/2),\qquad
 \Phi_0(z,x)=\rho_0(z)+\rho_0(x).
\]

After this trigonometric limit, scale \((z,\lambda)\) to \((\varepsilon z,\varepsilon\lambda)\) and multiply \(r\) by \(\varepsilon\). Then

\[
 \varepsilon\rho_0(\varepsilon z)\longrightarrow\frac1z,\qquad
 \varepsilon\Phi_0(\varepsilon z,\varepsilon x)\longrightarrow\frac1z+\frac1x,
\]

and the actual tensor limit is

\[
 r_{\mathrm{rat}}(z,\lambda)=\frac{\Omega}{z}
    +\sum_\alpha\frac{e_\alpha\otimes e_{-\alpha}}{x_\alpha}.
\]

The scaling preserves CDYBE, since its derivative and commutator terms both gain the same factor \(\varepsilon^2\). The receipt checks every root in both sequential limits and directly contracts the full rational CDYBE with its derivatives \(-\alpha_i/x_\alpha^2\). This is a sequential \(p\to0\), then \(\varepsilon\to0\) degeneration; no arbitrary simultaneous limiting path is claimed.

`elliptic_receipt(exhaustive=False)` uses \(p^1\) precision, while `exhaustive=True` uses \(p^2\). Both modes include all roots, all coefficient classes and a direct full tensor contraction. An explicit `order=0..4` overrides the precision. `full_tensor=False` omits only the redundant full elliptic contraction and reports that omission as `null`; it retains the complete root reduction, metric and rational checks. The default exact specialization is

\[
 (e^{\lambda_1},\ldots,e^{\lambda_8})=(2,3,5,7,11,13,17,19),
 \qquad(e^u,e^v,e^w)=(23,29,667).
\]

Prime independence prevents any nonzero root from having multiplier one. Public tensor APIs accept other exact rational specializations and reject poles and floating-point coordinates. The precision bound keeps coefficient growth predictable and is not a mathematical bound on the analytic construction.

Both retained \(p^1\) and \(p^2\) calculations have 304 nonzero entries in each r tensor and 84,816 nonzero bracket products across the three commutators. Before derivatives there are **4,290 nonzero tensor components**; the eight derivative families cancel all 4,290 exactly. The negative control `cdybe(derivative_scale=0)` leaves those components nonzero and supplies an exact witness. The rational tensor calculation exhibits the same cancellation counts at its declared rational specialization.

The six standalone tests cover independent first-nome coefficient and derivative formulas, scalar Fay through \(p^4\), numerator zeros, the full metric inverse, all eight dynamical gradients, direct E8 CDYBE and its negative control, \(p^2\) complete reduction, rational tensor CDYBE at another point, the sequential limit coefficients, pole rejection and JSON serialization.

## Primary sources and the boundary of the claim

- Giovanni Felder, [*Conformal field theory and integrable systems associated to elliptic curves*](https://arxiv.org/abs/hep-th/9407154), especially the elliptic \(\rho,\sigma\) kernels and their modified classical Yang–Baxter equation. This is the original classical dynamical elliptic construction.
- Pavel Etingof, [*On the dynamical Yang–Baxter equation*](https://arxiv.org/abs/math/0207008), equation (3) for the CDYBE and Example 3 for the plus-theta kernel with spectral parameter, unitarity, residue and degenerations. It fixes the convention used here directly.
- Sachin Gautam and Valerio Toledano Laredo, [*Elliptic quantum groups and their finite-dimensional representations*](https://arxiv.org/abs/1707.06469), section 2.2 for derivative-one theta normalization and the addition identity, and the introductory discussion distinguishing dynamical elliptic solutions for general semisimple Lie algebras from ordinary nondynamical elliptic solutions.

The completed result is a classical meromorphic E8 tensor with a checked implementation and a classical analytic proof. Constructing quantum exchange relations or proving their compatibility with the separate KZ, population and arithmetic engines remains additional work. This file does not identify the scalar period cancellation with a KZ monodromy representation or with the project's arithmetic 31 data.
