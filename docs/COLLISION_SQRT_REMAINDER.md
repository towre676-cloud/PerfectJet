# An effective square-root collision remainder

The conductor-two summatory function and its two-term main term are

\[
 S(X)=\sum_{n\le X}A(n),\qquad
 M(X)=CX\log X+C(2\gamma-1+D)X.
\]

The [finite-input convolution theorem](COLLISION_FINITE_X.md) gives an
explicit \(B_\sigma X^\sigma\) remainder for every \(1/2<\sigma<1\).
The square-supported structure of its absolute coefficients permits the
stronger growth estimate

\[
 \boxed{S(X)=M(X)+O\bigl(\sqrt X(1+\log X)^2\bigr),}
\]

with the completely explicit constant below. The executable certificate can
compare this bound with the earlier sigma-dependent bounds and retain the
smallest rigorous radius.

## Explicit theorem

Put \(k=6/5\), \(c=2\gamma-1\), and define the convergent positive product

\[
 G=\prod_p(1+4p^{-3/2}+3p^{-2}).
\]

Set

\[
 \kappa(c)=-\frac49-\frac c3+
       \frac{32}{9}\exp\left(-\frac{3(1-c)}4\right),
\]

\[
 P(\ell)=\frac k2\ell^2+
       [k(1+c)+c+2]\ell
       +k(c+2k)+(c+2)(c+1)+c+4
       +\max\{0,k(\kappa(c)-k)\}.
\]

For every real \(X\ge1\),

\[
 \boxed{|S(X)-M(X)|\le
 G\sqrt X\max\left\{10,P\!\left(\frac{\log X}{2}\right)\right\}.}
 \tag{1}
\]

The leading coefficient of the explicit polynomial in \(\log X\) is
\(3G/20\). Both \(G\) and every coefficient of \(P\) admit rigorous
outward rational evaluation. The statement concerns the same main term and
the same grouped positive arithmetic function as the original asymptotic.

## Square-supported coefficient transport

Write \(h\) for the multiplicative convolution coefficient in \(A=d*h\).
Its absolute local factor satisfies the exact identity

\[
 \sum_{e\ge0}|h(p^e)|x^e
 =\frac{1+4x^3+3x^4}{(1-x^2)^2}.
\]

Let \(g\) be the nonnegative multiplicative function with local polynomial
\(1+4x^3+3x^4\). Then, coefficient by coefficient,

\[
 |h(n)|=\sum_{a^2b=n}d(a)g(b),\qquad
 \sum_b\frac{g(b)}{\sqrt b}=G<\infty.
 \tag{2}
\]

The latter product converges because its local loss begins at \(p^{-3/2}\).
This transport retains the square-supported divisor coefficients exactly;
it does not evaluate the divergent norm \(B_{1/2}\).

Let \(\Delta(y)=\sum_{n\le y}d(n)-y\log y-cy\). The already proved
elementary estimate is \(|\Delta(y)|\le k\sqrt y\) for \(y\ge1\).
The exact convolution-error identity and (2) give

\[
 |S(X)-M(X)|\le\sum_b g(b)J(X/b),
\]

where, for \(Y>0\),

\[
 J(Y)=\sum_{a^2\le Y}d(a)|\Delta(Y/a^2)|
 +Y\sum_{a^2>Y}\frac{d(a)}{a^2}
       \left|c-\log\frac{a^2}{Y}\right|.
 \tag{3}
\]

All terms here are nonnegative, so rearrangement needs no conditional
summation argument. The bounds below also prove that the rearranged series
is finite.

## The large-argument kernel

Assume \(Y\ge1\), and put \(T=\sqrt Y\), \(\ell=\log T\).
Partial summation with \(D(t)=t\log t+ct+\Delta(t)\) yields

\[
 \sum_{a\le T}\frac{d(a)}a
 =\frac{D(T)}T+\int_1^T\frac{D(t)}{t^2}\,dt
 \le\frac12\ell^2+(1+c)\ell+c+2k-\frac{k}{\sqrt T}.
 \tag{4}
\]

Indeed, the error contributions are at most
\(k/\sqrt T+2k(1-1/\sqrt T)=2k-k/\sqrt T\).
Consequently the first range of (3) is at most

\[
 kT\left[\frac12\ell^2+(1+c)\ell+c+2k\right]-k^2\sqrt T.
 \tag{5}
\]

For the tail, enlarge the absolute logarithmic kernel to
\(c+2\log(a/T)\), which is positive for \(a>T\). Define

\[
 f(t)=\frac{c+2\log(t/T)}{t^2}.
\]

Exact Stieltjes partial summation gives

\[
 \sum_{a>T}d(a)f(a)
 =\int_T^\infty(\log t+c+1)f(t)\,dt
       -\Delta(T)f(T)-\int_T^\infty\Delta(t)f'(t)\,dt.
 \tag{6}
\]

This convention includes the endpoint correctly even when \(T\) is an
integer, because \(D(T)\) counts that integer and the tail excludes it.
Direct integration, using \(v=\log(t/T)\), gives

\[
 \int_T^\infty(\log t+c+1)f(t)\,dt
 =\frac{(c+2)(\ell+c+1)+c+4}{T}.
\]

Since \(f'(t)=[2-2c-4\log(t/T)]/t^3\), the two error terms in (6)
have total absolute value at most

\[
 \frac{k}{T^{3/2}}\left[c+
   \int_0^\infty e^{-3v/2}|2-2c-4v|\,dv\right]
 =\frac{k\kappa(c)}{T^{3/2}}.
 \tag{7}
\]

The absolute-value integral splits at \(v=(1-c)/2\), giving the stated
closed expression for \(\kappa(c)\). Multiplying the tail by \(Y=T^2\)
and combining (5)--(7) yields

\[
 J(Y)\le T\left[\frac k2\ell^2+[k(1+c)+c+2]\ell
      +k(c+2k)+(c+2)(c+1)+c+4\right]
      +k(\kappa(c)-k)\sqrt T.
\]

Since \(\sqrt T\le T\), this proves
\(J(Y)\le\sqrt Y P(\log Y/2)\). Every polynomial coefficient is
positive, so \(P\) is increasing on the nonnegative real axis.

## The small-argument kernel

For \(0<Y<1\), the head of (3) is empty. Set \(u=-\log Y\ge0\).
Absolute convergence of the ordinary divisor series at two gives

\[
 J(Y)\le Y\left[(c+u)\zeta(2)^2-4\zeta(2)\zeta'(2)\right].
\]

Using \(ue^{-u/2}\le2/e<1\), \(\zeta(2)<5/3\),
\(-\zeta'(2)<1\), and \(0<c<1/6\), we obtain

\[
 \frac{J(Y)}{\sqrt Y}
 <(c+1)\frac{25}{9}+\frac{20}{3}
 <\frac{535}{54}<10.
 \tag{8}
\]

These numerical inequalities need no special-function computation.
The integral test gives
\(\zeta(2)\le\sum_{n=1}^5n^{-2}+1/5=5989/3600<5/3\).
The function \(\log t/t^2\) decreases for \(t\ge2\), and therefore

\[
 -\zeta'(2)\le\frac{\log2}{4}+\frac{4\log3}{9}+\frac13
 <\frac7{40}+\frac{22}{45}+\frac13=\frac{359}{360}<1.
\]

Here \(\log2<7/10\) and \(\log3<11/10\) follow by retaining
positive Taylor terms in \(e^{7/10}>2\) and \(e^{11/10}>3\).
The finite terms through degree four and degree five, respectively,
already establish these inequalities. Also \(\log2>1/2\) follows from
the positive atanh series, justifying the monotonicity assertion.

For \(b\le X\), the large-argument estimate has
\(P(\log(X/b)/2)\le P(\log X/2)\). For \(b>X\), use (8).
Thus (2)--(3) give (1) by summing
\(\sqrt X g(b)/\sqrt b\) over the two disjoint ranges.

## Executable certificate

`perfectjet.collision_sqrt_remainder.sqrt_remainder_bound` evaluates (1)
with the same outward rational interval arithmetic used by the existing
finite-input certificate. Its `remainder_upper` is an upper bound relative
to the exact mathematical main term \(M(X)\); uncertainty in the numerical
main-term coefficients must still be added when reporting error relative
to a point prediction.

The constant product uses every prime through the inclusive cutoff
\(P\), or through seven when the requested cutoff is smaller. The omitted
product is bounded by

\[
 \exp\!\left(4W_{3/2}(P)+3W_2(P)\right),
\]

where \(W_a(P)\) is the explicit modulo-210 progression bound proved in
[COLLISION_FINITE_X.md](COLLISION_FINITE_X.md). No estimate for prime density
and no empirical adjustment factor enters the result.

```python
from perfectjet.collision_sqrt_remainder import sqrt_remainder_bound

bound = sqrt_remainder_bound(10**12, prime_cutoff=10000)
```

The direct API accepts exact integers or `Fraction` values with at most
1024 input bits, prime cutoffs from 2 through 10,000, and dyadic precision
from 32 through 256 bits. The bound requires work only at the selected
prime cutoff; it does not enumerate integers through \(X\).
