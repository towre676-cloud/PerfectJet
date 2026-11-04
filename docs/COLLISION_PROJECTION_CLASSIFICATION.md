# Prime-local collision projections: the exceptional conductor four

The all-character average of a **local** collision factor has an exact
classification. For every positive integer \(L\), put

\[
C_L(x)=\sum_{\substack{0\le r,s<L\\L\mid rs}}x^{r+s},\qquad
F_L(x)=\sum_{\substack{a,b\ge0\\L\mid ab}}x^{a+b}.
\]

Then

\[
F_L(x)=\frac{C_L(x)}{(1-x^L)^2}.
\]

**Theorem.** All roots of \(C_L\) are roots of unity if and only if

\[
\boxed{L=1\quad\text{or}\quad L=4.}
\]

Consequently the Euler product \(\mathcal P_L(s)=\prod_pF_L(p^{-s})\), initially
absolutely convergent for \(\Re s>1\), has exactly the following alternatives:

| Conductor | Euler product | Meromorphic continuation |
|---|---|---|
| \(1\) | \(\zeta(s)^2\) | Entire complex plane |
| \(4\) | \(\zeta(s)^2\zeta(4s)/\zeta(2s)\) | Entire complex plane |
| Every other \(L\) | No finite product of factors \(\zeta(ns)^{e_n}\) with integer \(e_n\) | \(\Re s>0\), with every point of \(\Re s=0\) a natural boundary |

These are written mathematical proofs with exact implementation checks, not
Lean formalization or a historical-priority claim. The natural-boundary input
is the classical Estermann theorem; the classification of this explicit local
family is proved below.

## The arithmetic condition is prime-local

Root-of-unity orthogonality gives

\[
\frac1L\sum_{j=0}^{L-1}\zeta_L^{jab}
=\mathbf1_{L\mid ab}.
\]

Thus \(C_L\) is the local all-character average of the cyclotomic collision
numerators in `collision.py`. The Euler product counts pairs of positive
integers (m,n) satisfying

\[
\boxed{L\mid v_p(m)v_p(n)\quad\text{for every prime }p.}
\]

This differs from the global condition

\[
L\mid\kappa(m,n),\qquad \kappa(m,n)=\sum_pv_p(m)v_p(n).
\]

For example \(L=2,m=n=6\) has total collision \(\kappa(6,6)=2\), but its
contributions at primes 2 and 3 are both 1. The global divisibility condition
holds and the prime-local condition fails. Averaging local factors before
multiplying over primes permits an independent character choice at each
prime; averaging a single character after taking the global product does not.
No equality between those two operations is asserted.

Unique residue decompositions \(a=r+Li,b=s+Lj\) preserve \(ab\pmod L\).
Summing \(i,j\ge0\) proves the rational formula for \(F_L\). In particular

\[
[x^q]F_L(x)=\#\{0\le a\le q:L\mid a(q-a)\}\ge0.
\]

## Exact degree and leading coefficient

For a residue \(r\in\{0,\ldots,L-1\}\), let \(d=\gcd(r,L)\), including
\(d=L\) when \(r=0\). The condition \(L\mid rs\) is equivalent to
\(L/d\mid s\). Therefore

\[
r\le L-d,\qquad s\le L-L/d.
\]

For each divisor \(d\mid L\), equality is attained simultaneously by

\[
(r,s)=(L-d,L-L/d).
\]

The first coordinate has gcd \(d\) with \(L\), so this is a permitted pair.
It follows that

\[
D_L:=\deg C_L=2L-\min_{d\mid L}(d+L/d).
\]

The minimum occurs at the divisor or divisors closest to \(\sqrt L\).
For a nonsquare \(L\), the minimizing divisors form a distinct pair \(d,L/d\).
They yield exactly two maximal-degree pairs, so the leading coefficient is 2.
For a square \(L=k^2\), the unique minimizer is \(d=k\), the leading
coefficient is 1, and

\[
D_L=2L-2k.
\]

Every \(C_L\) has constant term 1. The product of its root moduli equals
the constant term divided by the modulus of the leading coefficient. Thus
every nonsquare \(L>1\) already has a root off the unit circle, and cannot
be a product of cyclotomic polynomials.

## The square conductors and a reciprocity obstruction

It remains to consider \(L=k^2\). Put

\[
S_L=C_L(1)=\sum_{r=0}^{L-1}\gcd(r,L).
\]

For a fixed \(r\), precisely \(\gcd(r,L)\) residues \(s\) are allowed. By
symmetry in (r,s) and then the reflection \(r\leftrightarrow L-r\),

\[
C_L'(1)=2\sum_{r=1}^{L-1}r\gcd(r,L)
=L\sum_{r=1}^{L-1}\gcd(r,L)=L(S_L-L).
\]

A real monic polynomial of constant term 1 whose roots all have modulus 1
is reciprocal: inversion of a root equals complex conjugation, and both
preserve its root multiset. Hence, if all the roots of \(C_L\) were on the
unit circle, then

\[
C_L(x)=x^{D_L}C_L(1/x),\qquad
C_L'(1)=\frac{D_L}{2}C_L(1).
\]

Using the degree formula and the exact derivative gives

\[
L(S_L-L)=(L-k)S_L
\quad\Longrightarrow\quad S_L=k^3.
\]

The gcd sum is multiplicative in \(L\), by the Chinese remainder theorem.
At a prime power \(p^b\), sorting \(r\) by its valuation gives

\[
\sum_{r=0}^{p^b-1}\gcd(r,p^b)
=p^b+b(p^b-p^{b-1})
=p^b\bigl(1+b(1-1/p)\bigr).
\]

Consequently, for \(L=k^2\),

\[
S_L=k^2\prod_{p^a\parallel k}\bigl(1+2a(1-1/p)\bigr).
\]

For every prime (p) and positive integer \(a\), the binomial theorem gives

\[
p^a\ge1+a(p-1)\ge1+2a(1-1/p).
\]

Equality in both inequalities occurs only for \(p=2,a=1\): the second
inequality is strict for \(p>2\), and the first is strict for \(a>1\).
Therefore \(S_L<k^3\) unless \(k=1\) or \(k=2\). This contradicts the
necessary reciprocity identity in every other square conductor. The proof
rules out all roots lying on the unit circle, which is stronger than ruling
out roots of unity alone.

The two surviving cases are explicit:

\[
C_1(x)=1,\qquad C_4(x)=1+2x+2x^2+2x^3+x^4=(1+x)^2(1+x^2).
\]

This completes the all-conductor classification without a search cutoff.

## Euler products and the analytic boundary

The integer polynomial \(C_L\) has constant term 1. Estermann's theorem
therefore applies to \(\prod_pC_L(p^{-s})\): it continues meromorphically to
\(\Re s>0\); if a reciprocal root has modulus different from 1, every point
of \(\Re s=0\) prevents meromorphic continuation across a neighborhood.
The theorem is stated precisely in §1.2, p. 227 of
[Ludovic Delabarre, *Extension of Estermann's theorem to Euler products
associated to a multivariate polynomial*, BSMF 141 (2013), 225–265](https://numdam.org/item/10.24033/bsmf.2647.pdf).
The original paper is T. Estermann, *On Certain Functions Represented by
Dirichlet Series*, PLMS s2-27 (1928), 435–448,
[DOI 10.1112/plms/s2-27.1.435](https://doi.org/10.1112/plms/s2-27.1.435).

The remaining denominator contributes the globally meromorphic factor

\[
\mathcal P_L(s)=\zeta(Ls)^2\prod_p C_L(p^{-s}).
\]

It cannot remove a natural boundary: any meromorphic continuation of the
left side would, after division by the nonzero meromorphic function
\(\zeta(Ls)^2\), continue the numerator product as well.
For the exceptions, direct polynomial cancellation instead gives

\[
F_1(x)=\frac1{(1-x)^2},\qquad
F_4(x)=\frac{1-x^2}{(1-x)^2(1-x^4)},
\]

which prove the finite zeta formulas in the table. A finite product of
\(\zeta(ns)\) with integer exponents is globally meromorphic, so the natural
boundary excludes every such representation in the other conductors.

## Implementation and replay scope

`src/perfectjet/collision_projection.py` constructs the integer numerator
with a preflight \(L^2\) residue-census budget and immutable coefficients.
It preserves the unreduced denominator, supplies remote-index coefficient
queries, and reports exact degree, leading-coefficient, gcd-sum, derivative,
and reciprocity checks. The universal theorem record is explicitly a written
proof rather than an inference from the supported numerical range.

`tests/test_collision_projection.py` independently checks character
orthogonality in exact cyclotomic fields, unsplit exponent-pair counts,
the conductor-four rational identity, remote indices, strict input and
resource validation, immutability, and the distinction between prime-local
and total collision divisibility. Arithmetic checks do not assert a new
analytic theorem or evaluate an infinite Euler product numerically.

## A size-preserving fourth-power bijection at conductor four

The exceptional Euler product has a constructive arithmetic explanation.
Let \(\mathcal A_4\) be the ordered pairs \(m,n\ge1\) for which
\(4\mid v_p(m)v_p(n)\) at every prime. There is a bijection

\[
\boxed{
\mathcal A_4
\longleftrightarrow
\{(u,v,w)\in\mathbb N_{\ge1}^3:\gcd(u,v)=1\},
\qquad mn=uv\,w^4.
}
\]

The equality of products means the bijection preserves the Dirichlet-series
size, not that either original integer must remain individually unchanged.
This is a corollary of the explicit local construction, with no claim of
historical priority.

At a prime write \(a=v_p(m),b=v_p(n)\). The output consists of a common
fourth-power exponent \(c=v_p(w)\), a residual exponent \(h\ge0\), and,
when \(h>0\), a side specifying whether \(p^h\) belongs to \(u\) or \(v\).

* If \(a,b\) are both even, set
  \(c=\min(a,b)/2\) and \(h=|a-b|\). Put the residual on the side of the
  larger original exponent. If \(h=0\), there is no residual side.
* Otherwise exactly one exponent is odd, and the other is a multiple of
  four because \(4\mid ab\). Let \(h\) be the odd exponent, put the
  residual on its original side, and let \(c\) be the other exponent
  divided by four.

In both branches

\[
a+b=h+4c.
\]

There is an explicit inverse for every target \(h,c\ge0\). If \(h\) is
even, the exponent pair is \((h+2c,2c)\), with the first entry on the
residual side. If \(h\) is odd, it is \((h,4c)\), again with the first
entry on the residual side. For \(h=0\) the pair is \((2c,2c)\), so
orientation is immaterial. The inverse outputs have \(4\mid ab\), and
their parity selects exactly the original branch. Hence these formulas
give inverse maps without counting a tied orientation twice.

Applying the maps independently at each prime proves the global bijection.
At most one of \(u,v\) receives a positive exponent at any prime, which
proves \(\gcd(u,v)=1\); every coprime pair and every \(w\) provide valid
inverse local data.

Let \(A_4(N)\) count ordered admissible pairs with \(mn=N\), and let
\(\omega(M)\) be the number of distinct prime factors of \(M\), with
\(\omega(1)=0\). A fixed residual product \(M\) has exactly
\(2^{\omega(M)}\) coprime ordered factorizations: each prime power belongs
entirely to one of the two sides. Therefore

\[
\boxed{
A_4(N)=\sum_{d^4\mid N}2^{\omega(N/d^4)}.
}
\]

This also reproves
\(\mathcal P_4(s)=\zeta(4s)\zeta(s)^2/\zeta(2s)\).
The sum is finite and exact, so the exceptional conductor connects directly
to fourth-power extraction and ordinary coprime factorization.

The companion `src/perfectjet/collision_four.py` exposes exact local and
valuation-vector bijections. Independent finite replay checked 3,361 allowed
local exponent pairs, 6,601 target triples, and all coefficient identities for
products through 1,000. Those finite checks support the implementation; the
explicit inverse formulas above supply the unbounded mathematical proof.
