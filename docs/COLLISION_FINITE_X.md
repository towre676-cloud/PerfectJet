# Certified finite-input conductor-two counts

The conductor-two summatory function is

\[
 S(X)=\sum_{n\le X}A(n),\qquad
 A(p^e)=\begin{cases}1,&e\text{ even},\\e+1,&e\text{ odd}.
 \end{cases}
\]

The constants and asymptotic proved in
[COLLISION_ASYMPTOTICS.md](COLLISION_ASYMPTOTICS.md) remain unchanged. This
extension supplies a finite-input guarantee for the same two-term main term

\[
 M(X)=CX\log X+KX,\qquad K=C(2\gamma-1+D),
\]

\[
 C=\prod_p\left(1-\frac{2}{(p+1)^2}\right),\qquad
 D=\sum_p\frac{4p\log p}{(p+1)(p^2+2p-1)}.
\]

All statements below hold for real \(X\ge1\). The executable interface accepts
integers, rational strings and `Fraction` inputs, so its input value is exact.

## The explicit theorem

Put \(c=2\gamma-1\). For \(1/2<\sigma<1\), define

\[
 B_\sigma=\prod_p\left(1+
             \frac{2p^{-2\sigma}}{(1-p^{-\sigma})^2}\right),
\qquad
 k_\sigma=\max\left\{\frac65,
       \frac{\exp[-1-(1-\sigma)c]}{1-\sigma}\right\}.
\]

Then

\[
 \boxed{|S(X)-M(X)|\le k_\sigma B_\sigma X^\sigma.}
\]

This improves the proposed coefficient
\(12+1/[e(1-\sigma)]\) in two separate ways: the divisor error has an
elementary coefficient \(6/5\), and the two convolution ranges have disjoint
coefficient populations, allowing their uniform constants to be combined by
a maximum. A slightly simpler version replaces \(k_\sigma\) by
\(\max\{6/5,1/[e(1-\sigma)]\}\).

### An elementary divisor bound

Write \(T(y)=\sum_{m\le y}d(m)\), where \(d\) is the ordinary divisor
function, and \(\Delta(y)=T(y)-y\log y-cy\). We prove

\[
 \boxed{|\Delta(y)|\le\frac65\sqrt y\quad(y\ge1).}
\]

Let \(r=\lfloor\sqrt y\rfloor\), \(t=\sqrt y-r\),
\(u=\sqrt y/r\), and \(\epsilon_r=H_r-\log r-\gamma\). Thus
\(r\ge1\), \(0\le t<1\), and \(1\le u<2\). The harmonic inequalities

\[
 \frac1{2r}-\frac1{12r^2}\le\epsilon_r\le\frac1{2r}
 \tag{1}
\]

are justified directly below. The exact hyperbola formula gives

\[
 \Delta(y)=2y\epsilon_r+F-2\sum_{m=1}^r\{y/m\},
\qquad F=r^2(u^2-1-2u^2\log u).
 \tag{2}
\]

First, \(F\le-2t^2\). Indeed,
\(2u^2\log u-u^2+1-2(u-1)^2\) vanishes at one and has derivative
\(4(u\log u-u+1)\ge0\). Using the upper bound in (1) and the
nonnegative fractional parts in (2) therefore yields

\[
 \Delta(y)\le r+2t-(2-1/r)t^2\le\frac65(r+t).
\]

For the last inequality, the maximum over all real \(t\) of
\((4/5)t-(2-1/r)t^2\) is
\(4/[25(2-1/r)]\le r/5\), since \(r\ge1\).

For the other direction,
\(\log u\le(u-u^{-1})/2\) for \(u\ge1\): the difference vanishes at
one and has derivative \((u-1)^2/(2u^2)\). Consequently

\[
 -F\le r^2(u-1)(u^2-1)=rt(u^2-1)\le r(u^2-1).
\]

The lower bound in (1), together with
\(\sum_{m=1}^r\{y/m\}\le r\), now gives

\[
 \Delta(y)\ge-r-\frac{u^2}{6}\ge-\frac76ru
                  \ge-\frac65\sqrt y.
\]

Here \(u^2-7ru+6r\le u^2-7u+6=(u-1)(u-6)\le0\) because
\(r\ge1\) and \(1\le u<2\).

For completeness, (1) follows without an unspecified remainder estimate.
Let \(f_r=H_r-\log r-1/(2r)\) and
\(g_r=f_r+1/(12r^2)\). Both tend to \(\gamma\). For
\(z=1/(2r+1)\), the absolutely convergent logarithm series gives

\[
 f_{r+1}-f_r
 =\frac12\left(\frac1r+\frac1{r+1}\right)-\log(1+1/r)
 =\sum_{j\ge1}\frac{4j}{2j+1}z^{2j+1}>0,
\]

whereas

\[
 \frac1{12}\left(\frac1{r^2}-\frac1{(r+1)^2}\right)
 =\sum_{j\ge1}\frac{4j}{3}z^{2j+1}
 \ge f_{r+1}-f_r.
\]

Thus \(f_r\le\gamma\le g_r\), proving (1). In particular,
\(1/2<\gamma<7/12\), so \(0<c<1/6\).

### Convolution and the maximum, rather than a sum

The multiplicative coefficients

\[
 h(1)=1,\quad h(p)=0,\quad
 h(p^e)=2(-1)^{e-1}(e-1)\quad(e\ge2)
\]

satisfy \(A=d*h\), as follows from the local Euler factors. Absolute
convergence for \(\sigma>1/2\) gives

\[
 B_\sigma=\sum_n\frac{|h(n)|}{n^\sigma}<\infty,
\quad \sum_n\frac{h(n)}n=C,
\quad \sum_n\frac{h(n)\log n}n=-CD.
\]

It follows exactly that

\[
 S(X)-M(X)
 =\sum_{n\le X}h(n)\Delta(X/n)
  -X\sum_{n>X}\frac{h(n)}n\bigl[c-\log(n/X)\bigr].
 \tag{3}
\]

Normalize each summand by \(X^\sigma|h(n)|n^{-\sigma}\). In the first
range the absolute normalized kernel is at most

\[
 \frac65(n/X)^{\sigma-1/2}\le\frac65.
\]

In the second range let \(v=\log(n/X)>0\) and \(a=1-\sigma>0\).
The normalized absolute kernel is \(e^{-av}|c-v|\). Its supremum over
\(v\ge0\) is

\[
 \max\left\{c,\frac{e^{-1-ac}}a\right\}:
\]

on \([0,c]\) the function decreases from \(c\), and on
\([c,\infty)\) its maximum occurs at \(v=c+1/a\). Since
\(c<1/6<6/5\), every normalized kernel in (3) is at most
\(k_\sigma\). The two ranges together contain each coefficient exactly
once. Summing their absolute weights gives the displayed theorem.

This also independently proves the proposed conservative inequality: using
the weaker \(11\sqrt y\) divisor bound and bounding the two tail terms
separately yields \(11+|c|+1/[e(1-\sigma)]\le
12+1/[e(1-\sigma)]\).

## Rigorous finite Euler-product bounds

The absolute local factor has the exact identity

\[
 \left(1+\frac{2x^2}{(1-x)^2}\right)(1-x^2)^2
   =1+4x^3+3x^4.
\]

Consequently, for every \(\sigma>1/2\),

\[
 B_\sigma=\zeta(2\sigma)^2
             \prod_p(1+4p^{-3\sigma}+3p^{-4\sigma}).
\]

Extracting \(\zeta(2\sigma)^2\) is useful computationally: the remaining
prime tail starts at \(p^{-3\sigma}\), rather than \(p^{-2\sigma}\).
The zeta factor is evaluated by an elementary interval calculation, not a
floating-point special function. For \(a=2\sigma>1\), let
\(Z_{a,N}=\sum_{n=1}^N n^{-a}\). Convexity of \(f(t)=t^{-a}\) gives

\[
 Z_{a,N}+\frac{N^{1-a}}{a-1}-\frac{N^{-a}}2
 \le\zeta(a)\le
 Z_{a,N}+\frac{(N+1/2)^{1-a}}{a-1}.
\]

The lower inequality follows by integrating below the trapezoids between
successive integer arguments; the upper inequality integrates over unit
intervals centered at the omitted integers. The width is
\(O_a(N^{-a-1})\), but the displayed endpoints themselves contain no
unspecified remainder. The executable default uses \(N=64\).

For integer \(P\ge7\), let \(r\) run over the 48 reduced residue
classes modulo 210, and let \(n_r\) be the first integer above \(P\)
in that class. Every missing prime lies in one of these progressions. For
\(a>1\), monotonicity therefore gives the explicit bound

\[
 \sum_{p>P}p^{-a}\le W_a(P):=
 \sum_{\substack{1\le r<210\\\gcd(r,210)=1}}
 \left(n_r^{-a}+\frac{n_r^{1-a}}{210(a-1)}\right).
\]

Indeed, the progression sum is bounded by its first term plus the integral
of \((n_r+210t)^{-a}\) for \(t\ge0\). This removes multiples of
2, 3, 5 and 7 from the tail without assuming any theorem about prime
density. Requests with \(P<7\) evaluate those small prime factors
explicitly and report an effective cutoff of seven.

Let \(R_{\sigma,P}=\prod_{p\le P}
(1+4p^{-3\sigma}+3p^{-4\sigma})\). Since
\(\log(1+w)\le w\) for \(w\ge0\), the implemented majorant is

\[
 \boxed{\zeta(2\sigma)^2R_{\sigma,P}
 \le B_\sigma\le
 \zeta(2\sigma)^2R_{\sigma,P}
 \exp\!\left(4W_{3\sigma}(P)+3W_{4\sigma}(P)\right).}
 \tag{4}
\]

Every operation in (4), including the zeta enclosure, is evaluated with
outward rational intervals. The ordinary finite product is also retained
as an independent lower bound. At \(\sigma=3/5\), cutoff 1000 and
80-bit arithmetic, this gives \(284.96<B_\sigma<286.37\). At
\(\sigma=3/4\) the enclosure is \(27.9588<B_\sigma<27.9631\).
These are certified norms used in the theorem, not fitted error constants.

For comparison, a simpler all-integer tail applied directly to the
unextracted product gives

\[
 B_\sigma\le B_{\sigma,P}
 \exp\!\left(\frac{2P^{1-2\sigma}}
 {(2\sigma-1)[1-(P+1)^{-\sigma}]^2}\right),
\]

where \(B_{\sigma,P}\) is the ordinary finite prime product. This is
valid, but its tail can be much larger near \(\sigma=1/2\). The
extraction in (4) preserves the correct divergence of \(B_\sigma\)
through \(\zeta(2\sigma)^2\), while making the residual prime tail
rapidly computable.

The leading constant has the rational product enclosure already proved in
the original note,

\[
 C_P\left(1-\frac2{P+1}\right)\le C\le C_P.
\]

The derivative sum has positive terms and the elementary tail

\[
 D_P\le D\le D_P+\frac{4(\log P+1)}P.
\]

Both endpoints for \(D\), including each finite \(\log p\), must be
evaluated outwards. Euler's constant is likewise enclosed independently;
an unqualified floating-point library constant is not an endpoint proof.
The interval implementation uses the following explicit calculations.

### Rational interval arithmetic

All endpoints are fractions rounded outwards to multiples of \(2^{-b}\),
with \(32\le b\le256\). After binary range reduction, logarithms use
\(\log u=2\sum_{j\ge0}z^{2j+1}/(2j+1)\), where
\(z=(u-1)/(u+1)\) and \(1\le u\le2\). The omitted tail after the
last retained term is at most its next numerator divided by
\(1-z^2\), retaining the next denominator. Exponentials use a positive
Taylor series at an argument at most one half; a geometric bound encloses
its factorial tail. Interval squaring reverses the range reduction.
Negative arguments use reciprocals, and rational powers use
\(x^q=\exp(q\log x)\). Every rounding step preserves inclusion.

For Euler's constant, the exact Binet remainder identity is

\[
 \gamma=H_n-\log n-\frac1{2n}
 +2\int_0^\infty\frac{t}{(n^2+t^2)(e^{2\pi t}-1)}\,dt.
\]

Insert the finite geometric expansion of \((n^2+t^2)^{-1}\).
The integrated terms are \(B_{2j}/(2j n^{2j})\), and the remainder
has the sign of the next term and smaller absolute magnitude. The nine-term
and ten-term truncations therefore give upper and lower bounds. This uses
a finite expansion with a signed integral remainder, rather than convergence
of an infinite Bernoulli series. The harmonic sum is enclosed term by term
on a finer dyadic grid. The implementation chooses
\(n=2^{\max(5,\lceil b/18\rceil)}\).

The implementation improves the displayed integer tails for \(C,D\) by
also applying the modulo-210 progressions above to the decreasing functions
\(2/(t+1)^2\) and \(4\log(t)/t^2\). It takes the smaller of the
two proven tail bounds. Each progression is bounded by its first term plus
one 210th of its integral; the latter derivative integral is
\(4(\log n_r+1)/n_r\). These improvements concern the omitted primes;
they preserve every finite Euler factor.

## Certificate interface and interpretation

```python
from perfectjet.collision_asymptotic import counting_certificate, certificate_receipt

certificate = counting_certificate(10**8, sigma="auto", prime_cutoff=1000)
json_record = certificate_receipt("1000000", include_exact=True)
```

The same calculation is available in Math Lab and through the CLI:

```bash
python -m perfectjet collision-research approximate --x 1000000000000 --prime-cutoff 10000 --include-exact
python -m perfectjet collision-research approximate --x 1000000000000000000000000 --sigma 11/20
```

The input budget is 1024 bits for rational \(X\), 128 bits for rational
\(\sigma\), and an inclusive prime cutoff from 2 through 10,000.
Parameters too close to the sigma boundaries for the selected dyadic
precision reject before numerical work. Exact replay supports integer
inputs through \(10^{12}\) using the powerful-number convolution;
an independent coefficient sieve supports inputs through \(10^7\).
The approximation itself does not enumerate integers through \(X\).

The result includes rational enclosures for \(C,D,\gamma,K\), the
two-term main term, an upper bound for the theorem's remainder, the chosen
\(\sigma\), every parameter candidate, and integer endpoints enclosing
\(S(X)\). The point `prediction` is the midpoint of the main-term
interval; `prediction_error_upper` includes both the analytic remainder
and the main-term interval's half-width. `remainder_upper` alone bounds
the error relative to the mathematical main term \(M(X)\).

The automatic choice compares the finite rational grid
\(\sigma\in\{0.51,0.525,0.55,0.575,0.60,0.65,0.70,0.75,0.80,0.85,0.90\}\); it selects the
smallest certified radius on this grid, rather than asserting a global
optimum. Taking \(\sigma\) too close to \(1/2\) makes the absolute-coefficient
norm large; taking it too close to one raises \(X^\sigma\)
and the tail-kernel coefficient. Increasing the prime cutoff reduces the
Euler-product uncertainty and tightens the constant intervals. These
effects are included in the executable comparison, not inferred from a
floating-point minimizer.

The final count enclosure also uses \(1\le A(n)\le d(n)\), whence, for
\(N=\lfloor X\rfloor\),

\[
 N\le S(X)\le\sum_{n\le N}d(n)\le NH_N\le N(1+\log N).
\]

Intersecting independently valid bounds and rounding the lower endpoint up
and the upper endpoint down preserves an enclosure for the integer count.
The raw analytic enclosure is retained separately.

An exact replay, when requested within the supported counting budget, is
an additional comparison against the enclosure. Its observed difference
from the prediction measures numerical accuracy on that input; the proof
of the interval guarantee is (1)--(4), not the replay agreement.

## Numerical comparison and reproduction

The source-bound replay compares both coefficient constructions at every
integer through 100,000, the independent prime-power sieve and sparse
convolution at all decade endpoints through \(10^7\), and 204 additional
cumulative inputs. It records 27 exact comparisons through \(10^{12}\),
including square and prime-power neighbors and rational inputs. A separate
replay checks 211 count enclosures against the pre-existing coefficient
implementation through \(10^6\), 128 coefficients against original signed
factor pairs, and 1,000 divisor-remainder inputs.

The following results use **prime cutoff 10,000, 80-bit outward intervals,
and the eleven-candidate automatic sigma grid**. The prediction is the
midpoint of the certified main-term interval. Observed errors are rounded
to the nearest 0.01; guaranteed absolute errors and main-term widths are
rounded upward to integers, and guaranteed percentages are rounded upward
to six decimal places. Percentages divide the guaranteed error by the
independently computed exact cumulative count.

| X | Exact S(X) | Observed absolute prediction error | Guaranteed prediction error | Guaranteed relative error | Main-term interval width | sigma |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000,000 | 8,875,548 | 120.03 | 929,978 | 10.477970% | 966 | 0.70 |
| 100,000,000 | 1,158,932,442 | 1,091.83 | 19,393,256 | 1.673373% | 109,066 | 0.65 |
| 10,000,000,000 | 143,030,090,968 | 64,479.04 | 349,033,655 | 0.244029% | 12,160,077 | 0.60 |
| 1,000,000,000,000 | 17,016,685,657,676 | 15,698,140.32 | 6,106,127,342 | 0.035884% | 1,341,357,667 | 0.60 |

The exact errors are substantially smaller than the guaranteed bounds on
these inputs. The guarantee continues to use the proved majorant and
constant intervals; no empirical reduction factor is applied. The
machine-readable receipt retains exact rational endpoints, each candidate
radius, and the final integer enclosure.

The parameter study compares cutoffs 100, 1,000, and 10,000 at seven values
of X through \(10^{24}\). Cutoff 1,000 provides a convenient default;
cutoff 10,000 gives the narrowest reported certificates. At \(10^{12}\),
the latter gives the integer enclosure

\[
 17{,}010{,}563{,}832{,}195
 \le S(10^{12})\le
 17{,}022{,}776{,}086{,}877.
\]

At \(10^{24}\), the grid selects \(\sigma=0.55\). With cutoff 10,000,
the main-term interval half-width exceeds the analytic remainder by a
factor of 34,000. The limiting uncertainty there comes from the omitted
prime contributions to C and D. Increasing the dyadic precision alone
cannot remove it; a larger prime computation or a sharper proven tail
estimate is the appropriate next improvement.

Regenerate the deterministic records and verify their source hashes with:

```bash
python scripts/verify_collision_finite_x.py
python scripts/verify_collision_finite_x.py --check
python independent_checks/collision_finite_x/verify.py
PYTHONPATH=src python -m unittest discover -s tests -p 'test_collision*.py'
```

The full evidence is in
[validation.json](../results/collision-finite-x/validation.json), with its
source binding in
[manifest.json](../results/collision-finite-x/manifest.json). No timings or
run dates enter the reproducibility record.
