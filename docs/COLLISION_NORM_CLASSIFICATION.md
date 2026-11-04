# All-conductor Galois norm classification

The collision numerator already present in `collision.py` is

\[
N_{L,\zeta}(x)=\sum_{0\le r,s<L}\zeta^{rs}x^{r+s},\qquad
\sum_{a,b\ge0}\zeta^{ab}x^{a+b}
=\frac{N_{L,\zeta}(x)}{(1-x^L)^2},
\]

where \(\zeta\) is primitive of order \(L\). The residue decomposition is an
exact identity of formal series and an analytic identity for \(|x|<1\).

Take the full Galois norm at each prime:

\[
P_L(x)=\prod_{u\in(\mathbb Z/L)^\times}N_{L,\zeta^u}(x),\qquad
\mathcal Z_L^{\rm norm}(s)
=\prod_p\frac{P_L(p^{-s})}{(1-p^{-Ls})^{2\varphi(L)}}.
\]

The initial product converges absolutely on \(\Re s>1\). For \(L=1\), use
the one-element trivial Galois group, so \(P_1=1\) and
\(\mathcal Z_1^{\rm norm}(s)=\zeta(s)^2\).

**Theorem.** For every integer \(L>1\), \(P_L\in\mathbb Z[x]\) has a
root off the unit circle. The function \(\mathcal Z_L^{\rm norm}\) extends
meromorphically to \(\Re s>0\), and every point of \(\Re s=0\) is a
natural boundary for meromorphic continuation. Thus \(L=1\) is the only
finite-zeta-product case in this norm family.

This is an application of the classical Estermann theorem, not a historical
priority claim. It classifies the **full Galois norm** product. It does not
assert meromorphic continuation or a natural boundary for each individual
complex-phase product separately.

## Proof of the obstruction for every primitive phase

Suppose \(L>1\) and write \(D=2L-2\). Four coefficients follow directly
from the residue sum:

\[
c_0=1,\qquad c_1=2,\qquad c_D=\zeta,
\qquad c_{D-1}=2\zeta^2.
\]

The last two come from the residue pairs \((L-1,L-1)\) and
\((L-1,L-2),(L-2,L-1)\). This includes \(L=2\).

If a polynomial of degree \(D\), constant coefficient one, and leading
coefficient \(c_D\) of modulus one has all roots on the unit circle, it is
self-inversive:

\[
c_{D-j}=c_D\overline{c_j}.
\]

Indeed, \(x^D\overline{N(1/\overline{x})}\) has the same roots as
\(N\); comparing leading coefficients gives the identity. At \(j=1\)
it requires \(2\zeta^2=2\zeta\), impossible for \(L>1\). Thus
every primitive-phase numerator has a root off the unit circle. The product
of root moduli is \(|c_0/c_D|=1\), so there are roots both inside and
outside that circle.

## Why the Galois norm meets Estermann's hypotheses

The conjugate product is fixed by the whole Galois group and each coefficient
is an algebraic integer. It therefore belongs to \(\mathbb Z[x]\). Its
constant coefficient is one, its degree is \((2L-2)\varphi(L)\), and its
leading coefficient is \(\operatorname{Norm}(\zeta)\), which is \(-1\)
for \(L=2\) and one otherwise. A root of an individual numerator is also
a root of their product. Consequently \(P_L\) is not a product of
cyclotomic polynomials.

Estermann's theorem applies to \(\prod_pP_L(p^{-s})\). The remaining
factor is \(\zeta(Ls)^{2\varphi(L)}\), globally meromorphic and not
identically zero. If it removed a boundary point, dividing the resulting
local meromorphic continuation by that zeta factor would continue the
numerator product there, contradicting Estermann. Possible isolated zeros
or poles do not invalidate this quotient argument.

For a second exact check, Galois conjugation gives

\[
[x]P_L=2\varphi(L),\qquad
[x^{\deg P_L-1}]P_L
=2\mu(L)\operatorname{Norm}(\zeta),\qquad
P_L(1)=L^{\varphi(L)}.
\]

Here \(\sum_u\zeta^u=\mu(L)\), and \(N_{L,\zeta}(1)=L\).
Since \(\mu(L)\ne\varphi(L)\) for every \(L>1\), these two end
coefficients also rule out the real reciprocal/anti-reciprocal identity
required by a unit-circle root set.

## Exact implementation and evidence

`src/perfectjet/collision_norm.py` multiplies the conjugate polynomials over
the existing exact cyclotomic quotient ring. It checks every resulting
coefficient is rational and integral. Results are immutable integer tuples
in ascending order; the displayed denominator is deliberately uncancelled.
The function also returns the unnormalized primitive Galois trace numerator.
That trace has constant coefficient \(\varphi(L)\), so it is not itself
a prime Euler factor normalized to constant one. Trace, normalized trace,
norm, and all-character projection must not be interchanged.

Default preflight limits are conductor 32, norm degree 1024, and 5,000,000
estimated scalar operations. The work limit can exclude a conductor below
32; callers must explicitly raise it. Tests verify exact low-conductor
polynomials, coefficient identities, the individual self-inversive
obstruction, and independently recompute field norms as determinants of
multiplication. Finite checks are separate from the all-conductor proof.

For example:

\[
P_2=1+2x-x^2,
\]

\[
P_3=1+4x+7x^2+4x^3-2x^4-8x^5+4x^6-2x^7+x^8.
\]

Run `PYTHONPATH=src python -m unittest discover -s tests -p test_collision_norm.py`.
No numerical root finding is used by the implementation or proof.

## Analytic source

L. Delabarre, *Extension of Estermann's theorem to Euler products associated
to a multivariate polynomial*, Bulletin de la Société Mathématique de France
141(2), 2013, 225–265, §1.2, page 227, states the one-variable Estermann
theorem with precisely the hypotheses used here: integer polynomial,
constant coefficient one, and some reciprocal root of modulus different
from one. [Full primary research text](https://numdam.org/item/10.24033/bsmf.2647.pdf).

Original theorem: T. Estermann, *On Certain Functions Represented by Dirichlet
Series*, Proceedings of the London Mathematical Society s2-27, 1928,
435–448, [DOI](https://doi.org/10.1112/plms/s2-27.1.435).
