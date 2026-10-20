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
