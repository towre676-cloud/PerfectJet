# Asterion higher arithmetic and the boundary of the 248-dimensional algebra

The executable module `src/perfectjet/asterion_higher.py` extends the Asterion program from a verified bracket table to exact recoupling equations, finite differential graded current algebras, and explicit obstructions to several tempting quantization shortcuts. These constructions use rational arithmetic throughout. Half-integral spins are supported. A Wigner symbol is represented by its sign and rational square, so an irrational normalization is never silently replaced by a decimal. The implementation does not claim a new complex simple algebra, a new quantum group, or an elliptic quantum solution.

## Racah arithmetic and a finite hypergeometric evaluator

For admissible integer or half-integer spins the engine computes the Racah formula

\[
\begin{Bmatrix}a&b&e\\c&d&f\end{Bmatrix}
=\Delta(a,b,e)\Delta(a,d,f)\Delta(c,b,f)\Delta(c,d,e)
\sum_z\frac{(-1)^z(z+1)!}{\prod_{i=1}^4(z-t_i)!\prod_{j=1}^3(u_j-z)!},
\]

where \(t=(a+b+e,a+d+f,c+b+f,c+d+e)\) and \(u=(a+b+c+d,a+c+e+f,b+d+e+f)\). All factorial arguments are integers. The triangle factor is stored through

\[
\Delta(a,b,c)^2=\frac{(a+b-c)!(a-b+c)!(-a+b+c)!}{(a+b+c+1)!}.
\]

There is an independent exact replay through a terminating balanced \({}_4F_3(1)\). Put \(z_0=\max t_i\). Its four upper parameters are \(z_0+2,z_0-u_1,z_0-u_2,z_0-u_3\). Its three lower parameters are the multiset \(\{z_0-t_i+1\}_{i=1}^4\) with one occurrence of 1 removed. The missing factor is the factorial \(k!\) of the hypergeometric summand. The sum of lower parameters minus the sum of upper parameters is exactly 1. A nonpositive upper integer terminates the sum, and denominator poles before that termination are rejected. This construction is useful because it transforms every admissible Racah range into a finite hypergeometric problem without choosing a potentially singular alternative parametrization.

`wigner_6j(1,1,1,1,1,1)` gives positive sign and square \(1/36\), while \(\{\frac12,\frac12,0;\frac12,\frac12,0\}=-1/2\). The published mathematical definitions and factorial and hypergeometric formulas are classical; see [NIST DLMF 34.4](https://dlmf.nist.gov/34.4) and the [orthogonality and symmetry identities in DLMF 34.5](https://dlmf.nist.gov/34.5).

## Rational changes between polynomial coupling trees

The principal basis identifies the spin-\(a\) module with the binary forms of degree \(2a\), using \(\binom{2a}{i}x^{2a-i}y^i\). Let \(T\) denote the unnormalized transvectant in the main Asterion engine. For fixed external spins \((a,b,c,d)\), define

\[
L_e=T_{e+c-d}(T_{a+b-e}(P_a,Q_b),R_c),\qquad
R_f=T_{a+f-d}(P_a,T_{b+c-f}(Q_b,R_c)).
\]

The program computes a rational matrix \(C\) with \(L_e=\sum_f C_{ef}R_f\). It chooses an exact independent interpolation panel and then verifies every coefficient of the highest-output functional, including inputs not used to determine the matrix. Equivariance makes that functional determine the whole intertwiner. The matrix therefore is an exact polynomial identity, not a fitted numerical transformation. Independent tests compare it with direct differentiation in the repository's separate polynomial/transvectant implementation.

With binomial-monomial norm \(\|b_i\|^2=\binom{2a}{i}\), the squared adjoint norm of a transvectant is a finite rational sum \(N_{ab}^e\). The matrices satisfy the weighted orthogonality identity

\[
C\,\operatorname{diag}(N_{bc}^fN_{af}^d)\,C^T
=\operatorname{diag}(N_{ab}^eN_{ec}^d).
\]

Every entry also passes an independent Racah check:

\[
C_{ef}^2\frac{N_{bc}^fN_{af}^d}{N_{ab}^eN_{ec}^d}
=(2e+1)(2f+1)
\begin{Bmatrix}a&b&e\\c&d&f\end{Bmatrix}^{\!2}.
\]

`pentagon_receipt()` constructs all five binary parenthesizations of four spin-one-half inputs with output spin 1. Their multiplicity is three. It checks the two-step and three-step paths around the associator pentagon against a direct change of basis. The resulting common matrix is nonidentity. These are classical representation associators, not newly constructed quantum associators.

## A computed loss of nine Jacobi constraints

The principal E8 sectors are \(M=\{1,7,11,13,17,19,23,29\}\), but a three-input recoupling problem has intermediate spins outside \(M\). A missing bracket sector means its bracket coupling is zero. It does **not** permit deletion of an intermediate coordinate in the space of trilinear maps.

`compile_jacobi_constraints(a,b,c,d)` expands all three cyclic bracket trees into a common exact recoupling basis. It returns sparse quadratic equations in the reduced couplings \(\kappa_{ab}^c\), with the same transvectant normalization as `asterion_principal.py`. For the external problem \((7,11,13)\to17\), there are 15 admissible intermediate equation coordinates and 14 distinct quadratic coupling monomials. The complete quadratic equation matrix has rank **13**. Keeping only intermediate coordinates that themselves lie in \(M\) leaves rank **4**, losing **nine independent polynomial equations**. The actual computed E8 products satisfy all 15 coordinates and lie in the unique one-dimensional kernel of the complete 14-column monomial-coordinate matrix.

The separate problem \((11,13,17)\to19\) has 18 quadratic monomials, complete rank **17**, and rank **6** after that truncation, losing **eleven** independent equations. These are exact finite computations and useful tests of any proposed coupling-reconstruction method. Rank here means linear rank of quadratic polynomials in distinct monomials; it is not a classification of all nonlinear coupling solutions or a historical-priority claim.

`linearized_jacobi_rows` additionally computes sparse exact Jacobian rows at the retained E8 couplings. Relative coordinates are \(\kappa_v(t)=\kappa_v(1+t\eta_v)\), which are valid because all 170 retained couplings are nonzero. Fixing the eight principal action channels leaves 162 coordinates. Each computed row is scaled to primitive integers and retains its exact scaling factor. Tests check these rows against the exact central finite difference of the quadratic equations and verify the diagonal module-scale tangent directions \(\eta_{ab}^c=s_a+s_b-s_c\). The function supplies actual rows; it does not infer an uncomputed global rank from rigidity theorems.

## A genuine finite differential graded current algebra

For \(N\ge1\), the module implements the commutative differential graded algebra

\[
A_N=\mathbb Q[t,dt]/(t^{N+1},t^Ndt),\qquad d(t^k)=kt^{k-1}dt,\qquad(dt)^2=0.
\]

The second ideal generator matters: the differential of the first is \((N+1)t^Ndt\), so this is a differential ideal. Tensoring with a Lie algebra gives the genuine current-form DGLA \(\mathfrak g\otimes A_N\), with bracket \([x\otimes a,y\otimes b]=[x,y]\otimes ab\). Projection to constants, inclusion of constants, and

\[
h(t^kdt)=\frac{t^{k+1}}{k+1},\qquad h(t^k)=0
\]

give \(dh+hd=1-ip\), together with the standard contraction side conditions. For \(\mathfrak{sl}_2\) and \(N=2\), the engine checks all 15 contraction columns, all 225 graded skew/Leibniz pairs and all 3,375 graded Jacobi triples. The differential has rank six and cohomology has dimension three. The larger retained panel \(N=3\) has dimension 21 and checks all 9,261 triples.

This transfer is actually implemented: `transfer_binary` computes \(p[ix,iy]\). Every transferred bracket of arity at least three vanishes, because a lowest internal vertex in every transfer tree has a constant bracket followed by \(h\), which is zero. It is a useful strict control example. A nonformal exterior-algebra model with \(dc=ab\), Massey products and nonzero transferred ternary operations remains a separate research target and is not represented as completed work.

## Two independently checked obstructions to staying inside 248 dimensions

`e8_symmetric_square_obstruction()` constructs the actual action of the eight simple raising operators on the adjoint-highest-weight space of \(\operatorname{Sym}^2\mathfrak e_8\). The full symmetric square has dimension 30,876. Its weight-\(\theta\) space has dimension **36**. The combined raising matrix has shape **50 by 36**, rank **36**, and zero kernel. Complete reducibility in characteristic zero therefore proves

\[
\operatorname{Hom}_{E_8}(\operatorname{Sym}^2\mathfrak e_8,\mathfrak e_8)=0.
\]

This conclusion uses the actual highest-weight map, not only a quoted dimension decomposition. `verify_symmetric_square_certificate` reconstructs that map and rejects altered matrices or rank claims. The result is a precise boundary on an equivariant symmetric product valued in the adjoint; it does not exclude a larger enveloping algebra.

The ordinary canonical Moyal commutator supplies a different concrete boundary. With \(\star=m\circ\exp(\hbar\Omega/2)\),

\[
[x^{58},y^{58}]_\star
=\sum_{\substack{1\le r\le57\\r\text{ odd}}}
\frac{2\hbar^r}{2^rr!}(58)_r^2x^{58-r}y^{58-r}.
\]

It has 29 nonzero terms, of which **21** have degrees outside the eight principal polynomial blocks. Its leading term is \(3364\hbar x^{57}y^{57}\), of degree **114**. Thus the ordinary Moyal product does not close on the eight binary forms that encode E8. The exact weighted E8 transvectant bracket and ordinary Moyal multiplication have different closure laws.

## Quantum and dynamical boundaries retained explicitly

For the standard Drinfeld-Jimbo cobracket, use the common-scale convention \(\delta(e_i)=e_i\wedge h_i\). The principal raising element is \(e=\sum_i e_i\), while its neutral element has simple-coroot coefficients \((92,182,270,220,168,114,58,136)\). The simple-positive-root/Cartan coefficient matrix of \(\delta(e)\) is the identity of rank eight; that of \(e\wedge h\) has rank one. The functional

\[
182\,[e_1\wedge h_1]^*-92\,[e_1\wedge h_2]^*
\]

vanishes on the principal exterior square but evaluates to **182** on \(\delta(e)\). The principal inclusion is therefore not a Lie bialgebra inclusion for that standard cobracket. A common nonzero normalization factor does not remove this obstruction. This does not prohibit other cobrackets or larger quantum constructions.

Finally, the exact rational dynamical example \(r(\lambda)=e\wedge f/\lambda\) satisfies

\[
\operatorname{CYB}(r)=\frac{h\wedge e\wedge f}{\lambda^2}\ne0,
\qquad
\operatorname{Alt}(h\otimes\partial_\lambda r)+\operatorname{CYB}(r)=0.
\]

At \(\lambda=2\), all six tensor coefficients cancel as \(\pm1/4\). This proves that dropping the dynamical derivative can turn a correct dynamical equation into an incorrect ordinary Yang-Baxter claim. An elliptic extension requires its own spectral/theta kernels, pole conditions, dynamical derivatives and quantum consistency certificates. None is claimed implemented. The classical and quantum dynamical distinction is developed in [Etingof and Schiffmann, Lectures on the dynamical Yang-Baxter equations](https://arxiv.org/abs/math/9908064).

## Replay and evidence scope

Run `PYTHONPATH=src python -m unittest tests.test_asterion_higher -v` for independent polynomial checks, exact Jacobian finite differences, malformed-input rejection and certificate-tampering tests. The callable `higher_receipt(exhaustive=True, include_tables=True)` returns a JSON-safe record containing the actual recoupling matrices, sparse Jacobi equations, contraction checks and symmetric-square matrix. Its `exhaustive` flag enlarges the explicitly listed panels and the finite DGLA. It does not purport to enumerate all E8 spin quadruples or to construct a full elliptic quantum theory. Each individual listed recoupling panel checks all its highest-output input coefficients, weighted orthogonality entries and six-j squares.
