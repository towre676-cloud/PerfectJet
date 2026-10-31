# Collision arithmetic, Pell transport and analytic boundaries

This continuation develops the exact cyclotomic collision engine into a
research tool. It supplies two all-conductor classifications, an elementary
two-term counting asymptotic, certified rational Euler-product enclosures,
finite zeta-factor extraction, and positive divisor-pair populations with
count, rank, inverse rank, conditioning and uniform sampling. The core uses
only Python's standard library. Written proofs, executable exact checks,
illustrations and historical-priority questions retain their separate roles.

## The conductor-two mechanism

For positive integers define
\(\kappa(m,n)=\sum_pv_p(m)v_p(n)\). Initially for \(\Re s>1\), put

\[
Z_2(s)=\sum_{m,n\ge1}\frac{(-1)^{\kappa(m,n)}}{(mn)^s}
      =\prod_pL_2(p^{-s}).
\]

Absolute convergence justifies regrouping the signed pair series there.
Unique parity-residue decompositions give the exact identity

\[
\boxed{L_2(x)=\sum_{a,b\ge0}(-1)^{ab}x^{a+b}
 =\frac{1+2x-x^2}{(1-x^2)^2}
 =\frac{(1+(1+\sqrt2)x)(1+(1-\sqrt2)x)}{(1-x^2)^2}.}
\]

The coefficient at exponent \(k\) is 1 if \(k\) is even and \(k+1\)
if it is odd. For odd \(k\), every product \(a(k-a)\) is even; for
even \(k\), its parity is that of \(a\), and the alternating sum is 1.
Thus \(Z_2=\sum_{n\ge1}A(n)n^{-s}\) has positive multiplicative
coefficients

\[
A(p^k)=\begin{cases}1&2\mid k,\\k+1&2\nmid k,\end{cases}
\quad A(n)=\tau\!\left(\prod_{v_p(n)\text{ odd}}p^{v_p(n)}\right).
\]

This supplies an ordinary cardinality interpretation for \(A(n)\), but does
not turn the original signed factor-pair summands into probabilities.

Let \(P_n=(1+\sqrt2)^n+(1-\sqrt2)^n\). Then
\(P_0=P_1=2\), \(P_n=2P_{n-1}+P_{n-2}\), and

\[
c_n=[x^n]\frac{xL_2'(x)}{L_2(x)}
 =(-1)^{n+1}P_n+4\mathbf1_{2\mid n}.
\]

The formal integer zeta exponents are
\(b_n=n^{-1}\sum_{d\mid n}\mu(d)c_{n/d}\). Their first values are
\(2,-2,4,-7,16,-34,68,-140,308,-680,1476,-3248\).
`RationalEulerFactor` computes these from any supplied bounded integer
rational local factor, independently of the Pell formula. A finite extraction
returns the full residual \(R_M\):

\[
L(x)=\prod_{n\le M}(1-x^n)^{-b_n}R_M(x),\qquad
R_M(x)=1+O(x^{M+1}).
\]

Keeping this rational residual is essential. The infinite formal zeta product
is not evaluated as an analytic formula in the continuation region. Taylor
logarithms of the conductor-two numerator already have radius
\(\sqrt2-1\), so small primes cannot be silently included in that expansion.
Finite extraction and sufficiently large prime tails give the appropriate
continuation representation. `extract` reports the actual first residual
degree and explicitly retains the small-prime qualification.

## Two complete conductor classifications

For a primitive \(L\)-th root \(\zeta\), the existing exact engine has

\[
N_{L,\zeta}(x)=\sum_{0\le r,s<L}\zeta^{rs}x^{r+s},\qquad
L_{L,\zeta}(x)=N_{L,\zeta}(x)/(1-x^L)^2.
\]

**Norm theorem.** For every \(L>1\), every primitive numerator has roots
both inside and outside the unit circle. The prime-local full Galois norm
Euler product is meromorphic on \(\Re s>0\), with every point of
\(\Re s=0\) a natural boundary. At \(L=1\) it is \(\zeta(s)^2\).

The proof starts with just four coefficients. With \(D=2L-2\), they are
\(c_0=1,c_1=2,c_D=\zeta,c_{D-1}=2\zeta^2\). If all roots were of
modulus one, conjugate reciprocity would require
\(c_{D-1}=c_D\overline{c_1}=2\zeta\), which contradicts \(\zeta\ne1\).
The product of root moduli is one, so roots occur on both sides. Multiplying
primitive Galois conjugates gives an integer polynomial of constant one with
an off-circle root. Estermann's theorem applies to that integer numerator;
the denominator contributes only a global meromorphic zeta factor.
See [the complete norm proof](../COLLISION_NORM_CLASSIFICATION.md).

**Prime-local projection theorem.** Set

\[
C_L(x)=\sum_{\substack{0\le r,s<L\\L\mid rs}}x^{r+s}.
\]

Then the positive pair-counting Euler product
\(\mathcal P_L(s)=\prod_p C_L(p^{-s})/(1-p^{-Ls})^2\) is a finite
integer-power product of \(\zeta(ns)\) if and only if \(L=1\) or \(4\):

\[
\boxed{\mathcal P_1(s)=\zeta(s)^2,\qquad
\mathcal P_4(s)=\zeta(s)^2\zeta(4s)/\zeta(2s).}
\]

Every other conductor has \(\Re s=0\) as a natural boundary. This product
counts pairs satisfying \(L\mid v_p(m)v_p(n)\) **for each prime separately**.
It differs from imposing only \(L\mid\kappa(m,n)\). For example, \(m=n=6\)
passes the latter condition at \(L=2\) and fails the former.

The all-conductor proof does not extrapolate a finite scan. The exact degree
is \(2L-\min_{d\mid L}(d+L/d)\); a nonsquare conductor has leading
coefficient 2 and constant 1, ruling out all roots of modulus one. If
\(L=k^2\), reciprocity forces \(C_L(1)=k^3\). The gcd-sum formula
\(C_L(1)=k^2\prod_{p^a\parallel k}(1+2a(1-1/p))\), together with
\(1+2a(1-1/p)\le p^a\), gives equality only for \(k=1,2\).
See [the complete projection proof](../COLLISION_PROJECTION_CLASSIFICATION.md).

Both analytic arguments use the classical theorem stated in §1.2, p. 227 of
[Delabarre, BSMF 141 (2013)](https://numdam.org/item/10.24033/bsmf.2647.pdf).
No new version of Estermann's theorem, worldwide-priority claim, Lean proof,
or classification of each individual complex-phase Euler product is asserted.
In particular the norm, primitive trace and all-character projection are
different operations with different meanings.

## Counting, certified constants and navigable populations

Factoring off \(\zeta(s)^2\) gives

\[
Z_2(s)=\zeta(s)^2H(s),\quad
H(s)=\prod_p\left(1-\frac{2p^{-2s}}{(1+p^{-s})^2}\right).
\]

Writing \(C=H(1)\) and
\(D=\sum_p4p\log p/((p+1)(p^2+2p-1))\), elementary divisor convolution
proves

\[
\sum_{n\le X}A(n)=CX\log X+C(2\gamma-1+D)X
                  +O_\epsilon(X^{1/2+\epsilon}).
\]

For a finite prime cutoff \(P\), the exact leading-constant enclosure is
\(C_P(1-2/(P+1))\le C\le C_P\), with
\(C_P=\prod_{p\le P}(1-2/(p+1)^2)\). The library also supplies exact
rational enclosures for \(Z_2(s)\) at integer \(s\ge2\), and rounds JSON
endpoints outward. The [finite-input extension](../COLLISION_FINITE_X.md)
adds a guaranteed error bar, intervals for the secondary coefficient and
automatic rational-parameter selection. The [square-supported refinement](../COLLISION_SQRT_REMAINDER.md)
proves an explicit \(O(\sqrt X(1+\log X)^2)\) remainder, and a
[finite zeta extraction](../COLLISION_CONSTANT_EXTRACTION.md) sharply reduces
the constant uncertainties. The asymptotic proof is retained
in [the original account](../COLLISION_ASYMPTOTICS.md).

For actual populations retain phase residues:

\[
C_{L,c}(e)=\#\{a+b=e:ab\equiv c\pmod L\}.
\]

At \(e=dL+r\), this is \(dG_{r,c}+B_{r,c}\). `ExponentSplitPopulation`
therefore counts, ranks and selects at \(e=10^{100}\) after inspecting only
\(L\) residue classes. `FactorPairResiduePopulation` combines supplied prime
exponents by cyclic convolution and retains the original divisor pairs.
Counts conditioned on a left-exponent prefix and uniform rank sampling use
the same suffix tables. Primes are verified under a trial-division budget;
factorization is supplied, not guessed. Materializing the original integers
has a separate output-bit guard. These are conditional exact populations,
not empirical forecasts or a factoring algorithm.

## Use and reproduce

Run from an installed checkout, or prefix commands with `PYTHONPATH=src`:

```bash
python -m perfectjet collision-research report --order 24 --limit 10000
python -m perfectjet collision-research norm --conductor 3 --order 12
python -m perfectjet collision-research projection --conductor 4 --order 12
python -m perfectjet collision-research classify --max-conductor 32
python -m perfectjet collision-research extract --order 4
python -m perfectjet collision-research constants --prime-cutoff 10000 --s 2
python -m perfectjet collision-research population --conductor 6 --factorization '[[2,4],[3,3],[5,2]]' --residue 0 --rank 7
python scripts/verify_collision_pell.py --check
python independent_checks/collision_pell/verify.py
```

Every operation also accepts a JSON request and `--output`. The **Explore
arithmetic collisions** Math Lab card uses the same request router. The
offline [collision explorer](../../research/collision_pell/explorer.html)
visualizes residue populations and signed cancellations with exact BigInt
arithmetic; illustrative complex-plane graphics are labeled separately.

PJ-C001–PJ-C020 append the results to the equation catalogue without changing
the preceding 724 records. Replay receipts pin source hashes and mathematical
outputs; the independent verifier recomputes original divisor pairs, formal
series and determinant norms without trusting the main implementation's
discovery steps. Finite tests accompany the proofs; they do not replace their
unbounded arguments. The individual algebraic-coefficient Euler products,
broader asymptotic families and literature priority remain further research.
