# Conductor-two collision arithmetic: constants and asymptotics

This note derives the analytic consequences of the conductor-two collision
factor. The results concern a specific arithmetic Dirichlet series, not an NFL
forecasting model, a new physical law, or a claim of historical priority. The
proof below uses elementary Euler products, Dirichlet convolution and the
Dirichlet hyperbola estimate; it does not require importing a Tauberian theorem.

## Positive coefficients from signed collisions

Write `kappa(m,n)=sum_p v_p(m)v_p(n)` and

\[
Z_2(s)=\sum_{m,n\ge1}\frac{(-1)^{\kappa(m,n)}}{(mn)^s}
      =\sum_{n\ge1}\frac{A(n)}{n^s},\qquad \Re s>1.
\]

The rearrangement is legitimate there because the absolute double series is
`zeta(Re s)^2`. The grouped coefficient is multiplicative. At a prime power,

\[
 A(p^e)=\sum_{j=0}^{e}(-1)^{j(e-j)}
 =\begin{cases}1&e\text{ even},\\e+1&e\text{ odd}.\end{cases}
\]

For odd e, j and e-j have opposite parity, so every sign is positive. For even
e, the signs alternate and their odd-length sum is one. Consequently

\[
 L_2(x)=\sum_{e\ge0}A(p^e)x^e
       =\frac{1+2x-x^2}{(1-x^2)^2}.
\]

All grouped coefficients are positive integers. If
`n_odd=prod_(v_p(n) odd) p^v_p(n)`, then `A(n)=tau(n_odd)`. This is a genuine
count: divisors of n_odd, or ordered factorizations of n_odd. Thus the weighted
population through X can equivalently be represented by pairs `(n,d)` with
`1<=n<=X` and `d|n_odd`. It is not the unsigned population of all original
factor pairs `(m,n)`. Negative individual collision weights must not be used as
probabilities; positivity appears after grouping.

## The leading and secondary constants

Multiplying each local factor by `(1-x)^2` gives

\[
 Z_2(s)=\zeta(s)^2H(s),\qquad
 H(s)=\prod_p\left(1-\frac{2p^{-2s}}{(1+p^{-s})^2}\right).
\]

The product defining H converges normally on compact subsets of `Re s>1/2`:
each factor differs from one by `O(p^(-2 Re s))`, uniformly on such subsets.
Its denominators do not vanish there. H is holomorphic there; it need not be
nonvanishing at every complex point. In particular, do not assume a global
holomorphic logarithm without checking local zeros.

At s=1 its factors are strictly positive and

\[
 C=H(1)=\prod_p\left(1-\frac{2}{(p+1)^2}\right)>0,
\]

\[
 D=\frac{H'(1)}{H(1)}
   =\sum_p\frac{4p\log p}{(p+1)(p^2+2p-1)}.
\]

The derivative series is absolutely convergent; termwise differentiation is
valid in a neighborhood of one. Both sums and products have explicit tails.
For an integer prime cutoff P>=2 let C_P be the product over p<=P. Then

\[
 \boxed{C_P\left(1-\frac{2}{P+1}\right)\le C\le C_P.}
\]

Indeed, the missing losses `a_p=2/(p+1)^2` have sum at most
`2 sum_(n>P) 1/(n+1)^2 <= 2/(P+1)` by the integral test. Every finite product
of `(1-a_p)` is at least `1-sum a_p`; taking its limit proves the lower bound.
All displayed endpoints are rational, and they tend to C as P grows.

For P>=2, the positive derivative tail satisfies

\[
 0\le D-D_P\le \frac{4(\log P+1)}P.
\]

Use `(p+1)(p^2+2p-1)>=p^3`, followed by the decreasing-function integral
bound on `sum_(n>P) log(n)/n^2`. The executable API currently certifies C,
not D or Euler's constant gamma; an unqualified floating evaluation of the
secondary constant is not a certified interval.

## A summatory theorem with a proof

For real X tending to infinity, and every fixed `0<epsilon<1/2`,

\[
 \boxed{\sum_{n\le X}A(n)
 =CX\log X+C(2\gamma-1+D)X+O_\epsilon(X^{1/2+\epsilon}).}
\]

Here gamma is Euler's constant. This is an all-X asymptotic theorem, not a
finite-X accuracy promise from `constants_receipt`.

To prove it, expand `H(s)=sum h(n)n^(-s)`. Its multiplicative coefficients
are `h(1)=1`, `h(p)=0`, and

\[
 h(p^e)=2(-1)^{e-1}(e-1),\qquad e\ge2.
\]

For every sigma>1/2,

\[
 B_\sigma:=\sum_n\frac{|h(n)|}{n^\sigma}
 =\prod_p\left(1+\frac{2p^{-2\sigma}}{(1-p^{-\sigma})^2}\right)<\infty.
\]

The local identity proves `A=d*h`, with d the ordinary divisor function.
The Dirichlet hyperbola formula

\[
 \sum_{n\le y}d(n)
 =2\sum_{m\le\sqrt y}\lfloor y/m\rfloor-\lfloor\sqrt y\rfloor^2
 =y\log y+(2\gamma-1)y+O(\sqrt y)
\]

is elementary: insert `sum_(m<=r)1/m=log r+gamma+O(1/r)` and
`floor(y/m)=y/m+O(1)`, where r=floor(sqrt y). These estimates are uniform
for y>=1. Convolving gives a divisor-error term bounded by

\[
 O\!\left(\sqrt X\sum_{n\le X}|h(n)|n^{-1/2}\right)
 =O(B_\sigma X^\sigma),\qquad 1/2<\sigma<1.
\]

The main sum can be extended from n<=X to all n with the same order of error:
for n>X,

\[
 n^{-1}|\log(X/n)|
 \le \frac{X^{\sigma-1}n^{-\sigma}}{e(1-\sigma)},\qquad
 n^{-1}\le X^{\sigma-1}n^{-\sigma}.
\]

Finally `sum h(n)/n=C` and `sum h(n)log(n)/n=-H'(1)=-CD`.
Taking sigma=1/2+epsilon proves the theorem, including the sign of the
secondary coefficient. This proof does not establish an error of exactly
`O(sqrt X)` or give an optimized numerical remainder constant.

## Certified Dirichlet values at positive integer s

The standard-library module `perfectjet.collision_constants` returns exact
`Fraction` enclosures. For integer s>=2 and integer P>=2, put

\[
 Q_P(s)=\prod_{p\le P}L_2(p^{-s}),\qquad
 T=\frac{1}{(s-1)P^{s-1}}<1.
\]

Then

\[
 \boxed{Q_P(s)\le Z_2(s)\le Q_P(s)(1-T)^{-2}.}
\]

Every local factor exceeds one. Also `A(p^e)<=e+1`, so
`L_2(x)<=(1-x)^(-2)` for real `0<x<1`. The missing sum of `p^(-s)` is at
most `sum_(n>P)n^(-s)<=T`. The same product inequality used above now
bounds the reciprocal missing Euler product by `(1-T)^(-2)`.

```python
from perfectjet.collision_constants import (
    constant_bounds, conductor_two_zeta_bounds, constants_receipt,
)

c = constant_bounds(prime_cutoff=100)
z = conductor_two_zeta_bounds(s=2, prime_cutoff=100)
record = constants_receipt(prime_cutoff=100, s=2)  # Compact certified endpoints
```

`constant_bounds` and `conductor_two_zeta_bounds` return Fraction-valued
`lower`, `upper`, `partial_product` and their stated tail bound. The native bounds contain no rounding error. The JSON receipt rounds its lower
endpoint down and its upper endpoint up to a grid of spacing 2^-128, and encloses
the finite partial product on the same grid. Those compact fractions remain
rigorous bounds. Cutoffs are limited to 10,000; integer s is at most 32 and
s*cutoff at most 32,000, checked before prime enumeration or exponentiation.
They make no assertion at s=1, at noninteger s, or about analytic-continuation
values.

## Finite extracted zeta factors and small-prime safety

There are unique integers b_k for the formal identity

\[
 L_2(x)=\prod_{k\ge1}(1-x^k)^{-b_k}.
\]

The first twelve are

`2, -2, 4, -7, 16, -34, 68, -140, 308, -680, 1476, -3248`.

For example, let S_0=2, S_1=-2 and `S_n=-2S_(n-1)+S_(n-2)`. Then

\[
 a_n=4\,1_{2\mid n}-S_n,\qquad
 b_n=\frac1n\sum_{d\mid n}\mu(n/d)a_d.
\]

This follows by taking a formal logarithm of
`(1+2x-x^2)/(1-x^2)^2`; equivalently one can remove one integral Euler
factor at a time, which proves integrality without an analytic logarithm.
For any *finite* K define

\[
 R_K(x)=L_2(x)\prod_{k=1}^K(1-x^k)^{b_k}=1+O(x^{K+1}).
\]

Initially for Re s>1,

\[
 Z_2(s)=\left(\prod_{k=1}^K\zeta(ks)^{b_k}\right)
          \prod_p R_K(p^{-s}).
\]

The residual product converges normally for `Re s>1/(K+1)`, giving the
corresponding meromorphic continuation. This is a finite factorization;
it does not justify exchanging both infinite products or summing an
unrestricted prime-zeta logarithm near arbitrary parameters.

The numerator of L_2 has a zero at `x=1-sqrt(2)`, of modulus
`sqrt(2)-1`. A Taylor logarithm at zero therefore has radius
`sqrt(2)-1`, although the rational local factor remains defined beyond
that disk. For a log-series argument on `Re s>=sigma_0>0`, handle
**every prime with `p^sigma_0<=1+sqrt(2)` separately**, and retain exact
local factors and any zeros. At s=1 this includes p=2. A small-prime
exclusion for a logarithm is not a deletion from the original Euler
product; the finite omitted factors must be put back explicitly.
