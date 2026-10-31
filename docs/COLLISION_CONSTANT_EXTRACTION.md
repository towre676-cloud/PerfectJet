# Cubic prime tails for the conductor-two counting constants

The finite-input theorem in [COLLISION_FINITE_X.md](COLLISION_FINITE_X.md)
turns the conductor-two asymptotic into a guaranteed count enclosure. Its
constant calculation can be sharpened by extracting one ordinary zeta
factor. The resulting prime tails decay quadratically in the prime cutoff,
while retaining every small-prime factor exactly.

Write

\[
 M(X)=CX\log X+KX,\qquad K=C(2\gamma-1+D),
\]

\[
 H(s)=\prod_p\left(1-\frac{2p^{-2s}}{(1+p^{-s})^2}\right),
 \qquad C=H(1),\quad D=H'(1)/H(1).
\]

The direct constant calculation bounds omitted prime terms by
\(O(P^{-1})\) and \(O(\log(P)P^{-1})\). The following finite extraction
replaces these by \(O(P^{-2})\) and \(O(\log(P)P^{-2})\), respectively.
At cutoff 10,000, its intervals for \(C,D,K\) are approximately 9,899,
6,940 and 7,061 times narrower than the direct intervals.

## Exact extraction and the signs of the residual tails

For every admissible \(x\), the rational identity

\[
 1-\frac{2x^2}{(1+x)^2}=(1-x^2)^2 R(x),
 \qquad
 R(x)=\frac{1+2x-x^2}{(1-x)^2(1+x)^4}
 \tag{1}
\]

gives

\[
 H(s)=\zeta(2s)^{-2}\mathcal R(s),\qquad
 \mathcal R(s)=\prod_pR(p^{-s}).
 \tag{2}
\]

The residual satisfies \(R(x)=1+4x^3+O(x^4)\) near zero. Its product
therefore converges absolutely in a neighborhood of \(s=1\), and its
derivative can be taken term by term there. Equation (2) follows initially
from ordinary absolutely convergent Euler products and then by their values
and derivatives at one. Only the single factor \(\zeta(2s)^{-2}\) is
extracted; the entire rational residual is retained.

For \(0\le x\le1/2\),

\[
 R(x)-1=
 \frac{x^3(4+x-2x^2-x^3)}{(1-x)^2(1+x)^4}\ge0,
\]

\[
 g(x):=\frac{xR'(x)}{R(x)}
 =\frac{4x^3(3-x)}{(1-x^2)(1+2x-x^2)}.
 \tag{3}
\]

The denominator in (3) is at least one, since

\[
 (1-x^2)(1+2x-x^2)-1
 =2x(1-x-x^2)+x^4\ge0.
\]

Consequently

\[
 0\le g(x)\le12x^3,\qquad
 0\le\log R(x)=\int_0^x\frac{g(t)}t\,dt\le4x^3.
 \tag{4}
\]

These inequalities apply to every prime, including two. They use the exact
rational function and a real integral, so evaluating a logarithm Taylor
series beyond its convergence disk is unnecessary.

At \(s=1\), (2) and (3) yield

\[
 C=\frac{\prod_pR(1/p)}{\zeta(2)^2},
 \qquad
 D=-4\frac{\zeta'(2)}{\zeta(2)}
   -\sum_p\log(p)\,g(1/p),
 \tag{5}
\]

where the finite local quantities are rational except for their logarithms:

\[
 R(1/p)=\frac{p^4(p^2+2p-1)}{(p-1)^2(p+1)^4},
 \qquad
 g(1/p)=\frac{4(3p-1)}{(p^2-1)(p^2+2p-1)}.
 \tag{6}
\]

The residual tails have opposite effects on the constants: omitted factors
increase \(C\), while omitted derivative terms decrease \(D\). The
certificate records these directions explicitly.

## Explicit finite-cutoff enclosures

For \(P\ge7\), define

\[
 R_P=\prod_{p\le P}R(1/p),\quad
 J_P=\sum_{p\le P}\log(p)g(1/p),
\]

\[
 U_3(P)\ge\sum_{p>P}p^{-3},\qquad
 V_3(P)\ge\sum_{p>P}\frac{\log p}{p^3}.
\]

Then (4) gives the complete enclosures

\[
 \boxed{\frac{R_P}{\zeta(2)^2}
 \le C\le\frac{R_P}{\zeta(2)^2}\exp(4U_3(P)),}
 \tag{7}
\]

\[
 \boxed{-4\frac{\zeta'(2)}{\zeta(2)}-J_P-12V_3(P)
 \le D\le -4\frac{\zeta'(2)}{\zeta(2)}-J_P.}
 \tag{8}
\]

One elementary choice is

\[
 U_3(P)=\frac1{2P^2},\qquad
 V_3(P)=\frac{2\log P+1}{4P^2},
 \tag{9}
\]

by the decreasing-function integral test. The implementation also computes
independent bounds from the 48 reduced residue classes modulo 210. Let
\(n_r\) be the first integer above \(P\) in class \(r\). Every omitted
prime lies in one of these classes, and

\[
 \sum_{p>P}p^{-3}\le\sum_{\gcd(r,210)=1}
 \left(\frac1{n_r^3}+\frac1{420n_r^2}\right),
 \tag{10}
\]

\[
 \sum_{p>P}\frac{\log p}{p^3}\le\sum_{\gcd(r,210)=1}
 \left(\frac{\log n_r}{n_r^3}
 +\frac{2\log n_r+1}{840n_r^2}\right).
 \tag{11}
\]

The right sides of (10) and (11) are valid choices of
\(U_3,V_3\); the implementation takes their minimum with (9). Each
progression is bounded by its first term plus one 210th of its integral.
For cutoffs below seven, the implementation includes the primes through
seven and reports that effective cutoff. This preserves all four exceptional
wheel primes explicitly.

## Certified zeta value and derivative

The zeta quantities in (7)--(8) are evaluated independently using
Euler--Maclaurin summation. For an integer \(N\ge1\) and order \(m\),

\[
 \zeta(2)=\sum_{n=1}^{N-1}\frac1{n^2}
 +\frac1N+\frac1{2N^2}
 +\sum_{k=1}^{m}\frac{B_{2k}}{N^{2k+1}}+E,
\]

\[
 \zeta'(2)=-\sum_{n=1}^{N-1}\frac{\log n}{n^2}
 -\frac{\log N+1}{N}-\frac{\log N}{2N^2}
 +\sum_{k=1}^{m}\frac{B_{2k}}{N^{2k+1}}
       (H_{2k}-1-\log N)+E'.
 \tag{12}
\]

With \(q=2m\), explicit absolute remainder bounds are

\[
 |E|\le |B_q|N^{-q-1},
\]

\[
 |E'|\le |B_q|N^{-q-1}
 \left(\log N+H_{q+1}-1+\frac1{q+1}\right).
 \tag{13}
\]

To derive them, the periodic Bernoulli polynomial has supremum at most
\(|B_q|\), by its absolutely convergent Fourier series. The usual
Euler--Maclaurin remainder is therefore bounded by
\(|B_q|/q!\) times the integral of the absolute \(q\)-th derivative.
For even \(q\), the two derivatives needed here are

\[
 (t^{-2})^{(q)}=(q+1)!t^{-q-2},
\]

\[
 (t^{-2}\log t)^{(q)}
 =(q+1)!t^{-q-2}(\log t-H_{q+1}+1).
\]

Integrating the first exactly proves the first bound in (13). Bounding the
absolute value in the second by
\(\log t+H_{q+1}-1\), then integrating, proves the second. This derivation
applies Euler--Maclaurin separately to the logarithmic series; it does not
differentiate an unsigned remainder bound.

Bernoulli numbers and harmonic sums are computed as exact fractions.
Logarithms, exponentials, divisions and products use the outward dyadic
interval arithmetic described in [COLLISION_FINITE_X.md](COLLISION_FINITE_X.md).
The default zeta calculation uses \(N=64,m=12\) through 128-bit output;
higher precision uses \(N=128,m=24\). The supplied finite values of
\(N,m\), absolute remainders and output precision appear in each receipt.

## Numerical effect and API

At 80-bit arithmetic the extracted interval widths obey the following
upward-rounded bounds. All widths are expressed in units of \(10^{-12}\).
The improvement column is the largest stated integer factor below the
ratio of the direct width to the extracted width.

| Prime cutoff | C width / 10^-12 | D width / 10^-12 | K width / 10^-12 | K width improvement |
|---:|---:|---:|---:|---:|
| 100 | 34,979,798 | 908,235,419 | 578,801,608 | 71 times |
| 1,000 | 309,623 | 11,598,593 | 7,220,671 | 684 times |
| 10,000 | 2,750 | 135,800 | 83,451 | 7,061 times |

The original direct intervals remain useful as an independent enclosure.
The counting engine intersects the direct and extracted intervals for
\(C,D,K\); intersection preserves their mathematical guarantee. At large
\(X\), the improvement reduces the constant part of the prediction's
uncertainty, which is multiplied by \(X\log X\) and \(X\). It leaves the
separately proved analytic remainder unchanged.

```python
from perfectjet.collision_constant_extraction import extracted_asymptotic_constants

constants = extracted_asymptotic_constants(prime_cutoff=10000, bits=80)
print(constants["C"].record())
print(constants["D"].record())
print(constants["K"].record())
print(constants["evidence"])
```

The prime cutoff is bounded by 10,000 and the interval precision by 32 through
256 bits, as in the original certificate engine. The evidence retains the
finite residual product, positive derivative-magnitude partial sum, positive logarithmic
tail, negative derivative tail and both zeta intervals. Regression checks use
literal rational differentiation, independent trial-division primes, longer
Decimal-evaluated residual products, and the direct constant enclosures.
