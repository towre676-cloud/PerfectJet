# Beyond degree twenty: local resonance and all-degree partner strata

**Research extension, 20 October 2026 UTC.** Work in characteristic zero; interpret projective root statements after algebraic closure. For a nonzero binary sextic \(f\), let \(S_N\) denote the degree-\(N\) binary forms and define

\[
K_N(f)=\{g\in S_N:(f,g)_3=(f,g)_5=0\},\qquad N\ge3.
\tag{PS1}
\]

The unnormalized transvectants agree with `transvectants.py`. Correction-free membership is different from activity, which additionally requires \((f,g)_1\ne0\). The [previous full-space investigation](PARTNER_INCIDENCE.md) classifies through degree twenty with its stated external-solver dependency. This chapter proves all-degree local obstructions, complete high-multiplicity kernels in explicit ranges, and complete dimension generating series on the monomial strata. The global classification of squarefree sextics in degrees twenty-one and above remains open. No historical priority or new Lean theorem is claimed.

## The affine equations and their indicial polynomials

Write \(t=x/y\), \(f=y^6F(t)\), \(g=y^NG(t)\), and \((u)_j=u(u-1)\cdots(u-j+1)\), with \((u)_0=1\). Dehomogenizing the \(r\)-th transvectant gives

\[
y^{-(N+6-2r)}(f,g)_r
=\sum_{i=0}^r(-1)^i\binom ri
(6-r+i)_i(N-i)_{r-i}F^{(r-i)}(t)G^{(i)}(t).
\tag{PS2}
\]

This is an identity of homogeneous expressions, with the right side understood at \(y=1\). To prove it, first use \(F=(t+a)^6\) and \(G=(t+b)^N\). When \(N\ge r\), the falling factorials combine to the common factor \((6)_r(N)_r\), and the remaining binomial sum is \(((t+b)-(t+a))^r=(b-a)^r\). Pure powers span each space of forms in characteristic zero, so bilinearity proves the identity. When \(N<r\), each term vanishes: either \(i>N\) and \(G^{(i)}=0\), or \(i\le N\) and \((N-i)_{r-i}=0\). The homogeneous transvectant vanishes as well.

For the third gate, (PS2) is the short differential equation

\[
-120FG'''+60(N-2)F'G''
-12(N-1)(N-2)F''G'
+N(N-1)(N-2)F'''G=0.
\tag{PS3}
\]

At a point where \(f\) has multiplicity \(k\in\{0,\ldots,6\}\), choose a local coordinate with \(F(t)=a t^k+O(t^{k+1})\), \(a\ne0\). For a nonzero partner, write \(G(t)=b t^s+O(t^{s+1})\), \(b\ne0\). The coefficient at \(t^{k+s-r}\) in the gate is \(ab I_{r,k}(N,s)\), where

\[
I_{r,k}(N,s)=\sum_{i=0}^r(-1)^i\binom ri
(6-r+i)_i(N-i)_{r-i}(k)_{r-i}(s)_i.
\tag{PS4}
\]

Thus every nonzero partner satisfies \(I_{3,k}=I_{5,k}=0\). If the displayed exponent is negative, every contributing falling factorial vanishes; interpret this as a zero Laurent coefficient. Projective coordinate changes preserve vanishing of both gates, so the same obstruction applies at infinity. At \(k=0\), the third gate is \(-120s(s-1)(s-2)\), giving valuations at most two in every degree.

## A finite certificate for the infinite-degree statement

Factor \(I_{3,k}=c_{3,k}H_kJ_{3,k}\) and \(I_{5,k}=c_{5,k}H_kJ_{5,k}\). All these are identities in \(\mathbb Q[N,s]\), rather than sampled numerical equalities.

| \(k\) | \(H_k\) | \(J_{3,k}\) | \(J_{5,k}\) | \((c_{3,k},c_{5,k})\) |
|---|---|---|---|---|
| 0 | \(s(s-1)(s-2)\) | \(1\) | \((s-3)(s-4)\) | \((-120,-720)\) |
| 1 | \(s(s-1)\) | \(2s-N-2\) | \((s-2)(s-3)(6s-5N-4)\) | \((-60,-120)\) |
| 2 | \(s\) | \(N^2-5Ns+2N+5s^2-5s+2\) | \((s-N)(s-2)(s-1)(3s-2N-1)\) | \((-24,-240)\) |
| 3 | \(2s-N\) | \(N^2-10Ns-3N+10s^2+2\) | \(s(s-N)(s-1)(s-N+1)\) | \((-6,-360)\) |
| 4 | \(s-N\) | \(N^2-5Ns-3N+5s^2+5s+2\) | \(s(s-N+1)(s-N+2)(3s-N+1)\) | \((-24,-240)\) |
| 5 | \((s-N)(s-N+1)\) | \(2s-N+2\) | \((s-N+2)(s-N+3)(6s-N+4)\) | \((-60,-120)\) |
| 6 | \((s-N)(s-N+1)(s-N+2)\) | \(1\) | \((s-N+3)(s-N+4)\) | \((-120,-720)\) |

The Sylvester determinants eliminating \(s\), with \(J_3\) rows first and descending coefficients, are

\[
\begin{aligned}
\operatorname{Res}_s(J_{3,1},J_{5,1})&=-4(N-4)(N-2)(N-1),\\
\operatorname{Res}_s(J_{3,2},J_{5,2})&=-(N-6)(N-2)^3(N-1)^3(N+8),\\
\operatorname{Res}_s(J_{3,3},J_{5,3})&=(N-12)^2(N-2)^2(N-1)^4,\\
\operatorname{Res}_s(J_{3,4},J_{5,4})&=-(N-6)(N-2)^3(N-1)^3(N+8),\\
\operatorname{Res}_s(J_{3,5},J_{5,5})&=4(N-4)(N-2)(N-1).
\end{aligned}
\tag{PS5}
\]

The \(k=0,6\) resultants equal one. Their signs depend on the stated Sylvester convention, while nonvanishing is the mathematical obstruction. If both original indicial polynomials vanish and \(H_k\ne0\), both reduced factors must vanish, forcing the corresponding resultant to vanish. None of (PS5) vanishes for \(N\ge13\). We have therefore proved the complete necessary local table

| Multiplicity of \(f\) at the point | Possible partner valuation, \(N\ge13\) |
|---|---|
| 0 | \(0,1,2\) |
| 1 | \(0,1\) |
| 2 | \(0\) |
| 3 | \(N/2\), only for even \(N\) |
| 4 | \(N\) |
| 5 | \(N-1,N\) |
| 6 | \(N-2,N-1,N\) |

These are necessary conditions for a general sextic; the table does not assert global existence for every listed valuation. The uniform conclusion is an all-degree theorem because the determinant identities hold in a polynomial ring. The verifier recomputes the fourteen factor identities and all seven determinants by division-free polynomial arithmetic, without calling an external CAS or testing only finitely many values of \(N\).

## Complete high-root strata and the pure-power equivalence

Suppose \(f=\ell^k h\), with \(\ell\nmid h\), and \(k\in\{4,5,6\}\). Then

\[
\boxed{K_N(f)=\ell^{N-k+4}S_{k-4},\qquad\dim K_N(f)=k-3.}
\tag{PS6}
\]

The ranges are \(N\ge7\) for \(k=4\), \(N\ge5\) for \(k=5\), and \(N\ge3\) for \(k=6\). Necessity follows from (PS5) and the corresponding common factor: in each range there are no other allowed valuations. With \(\ell=x\), the allowed valuations force \(g\in x^{N-k+4}S_{k-4}\). Conversely \(f\) has \(y\)-degree at most \(6-k\), and each proposed \(g\) has \(y\)-degree at most \(k-4\). Their total available \(y\)-degree is at most two. Every summand of an order-three or order-five transvectant differentiates a total of respectively three or five times in \(y\), so every term vanishes. Coordinate change transports the entire kernel formula.

There is also a global equivalence in every degree \(N\ge3\), without an exact-multiplicity assumption:

\[
\boxed{\ell^N\in K_N(f)\quad\Longleftrightarrow\quad\ell^4\mid f.}
\tag{PS7}
\]

After \(\ell=x\), one has \((f,x^N)_3=-(N)_3 x^{N-3}\partial_y^3f\). In characteristic zero this vanishes exactly when the \(y\)-degree of \(f\) is at most two, or equivalently \(x^4\mid f\); the fifth gate then vanishes as well. The first gate is \((f,x^N)_1=-Nx^{N-1}\partial_yf\). Consequently this pure-power partner is active precisely when \(f\) is not proportional to \(\ell^6\). This criterion applies to the particular pure-power partner, not to every vector in the larger kernel of a pure sextic.

## Triple roots, finite jets and complete two-root series

A triple root forces valuation \(N/2\), so no nonzero partner exists in any odd degree \(N\ge13\) when \(f\) has a triple root. If \(f=(\ell m)^3\), with \(\ell,m\) independent, divisibility at both roots gives

\[
K_N((\ell m)^3)=
\begin{cases}
\mathbb F(\ell m)^{N/2},&N\ge14\text{ even},\\
0,&N\ge13\text{ odd}.
\end{cases}
\tag{PS8}
\]

Sufficiency follows after \(\ell=x,m=y\): in every odd transvectant of \(x^3y^3\) and \(x^{N/2}y^{N/2}\), the \(i\) and \(r-i\) terms cancel. Their first transvectant vanishes too, so these partners are correction-free but inactive.

The local restrictions also give exact finite-jet dimension bounds. At a point outside \(f=0\), the map \(g\mapsto(G,G',G'')\) evaluated at that point is injective, because any nonzero kernel vector would have valuation at least three. Thus \(\dim K_N(f)\le3\) for every \(N\ge3\). At a simple root, evaluation of \((G,G')\) is injective for \(N\ge5\), so the dimension is at most two. At a double root, evaluation of \(G\) is injective for \(N\ge7\), giving dimension at most one. At a triple root, the coefficient at order \(N/2\) is injective in the even-degree range above; in the odd-degree range the space is zero. These facts follow from linear combinations and the allowed valuations, without an assumption about existence of analytic solutions to the differential equation.

For a monomial sextic \(f=x^k y^{6-k}\), each input \(g=x^s y^{N-s}\) produces the single monomial

\[
(f,g)_r=I_{r,k}(N,s)x^{k+s-r}y^{N+6-k-s-r}.
\]

Different input monomials have different output exponents. Therefore the common indicial roots give a complete basis of the joint kernel, for every \(N\ge3\). The only additional integer roots beyond the ordinary common factors are \((k,N,s)=(1,4,3),(2,6,2),(3,12,1),(3,12,11)\), and their reflected \(k\leftrightarrow6-k,\ s\leftrightarrow N-s\) cases. This is a finite exhaustive list: (PS5) restricts exceptional positive degrees \(N\ge3\) to four, six and twelve, and substitution into the two explicit indicial polynomials finishes those cases.

Define \(H_f(t)=\sum_{N\ge3}\dim K_N(f)t^N\). Up to exchanging \(x,y\), all one-root and two-root strata have

\[
\boxed{
\begin{aligned}
H_{x^6}(t)&=\frac{3t^3}{1-t},\\
H_{x^5y}(t)&=\frac{2t^3}{1-t}+t^4,\\
H_{x^4y^2}(t)&=\frac{t^3}{1-t}+t^6,\\
H_{x^3y^3}(t)&=\frac{t^4}{1-t^2}+2t^{12}.
\end{aligned}}
\tag{PS9}
\]

These are dimension generating series; no graded-module closure under multiplication is assumed. The exceptional dimensions in degrees four, six and twelve are explicit local resonances. They do not by themselves derive the entire invariant hypersurfaces in the seven-dimensional space of sextics.

## Reproduction and the next global frontier

Run `PYTHONPATH=src python -m unittest discover -s tests -p test_partner_structure.py -v`, then `python scripts/verify_partner_structure.py`. The second command emits `results/partner_structure.json`, including deterministic source hashes. The implementation uses the existing exact rational polynomial type and a division-free subset determinant for the Sylvester matrices. There is no msolve, Singular, SymPy or numerical-rank dependency.

The ten focused tests replay all symbolic factorizations and resultants, compare affine gates against independent mixed homogeneous derivatives, compare indicial coefficients with actual monomial transvectants, verify rational gate-matrix kernel dimensions beyond degree twenty, test coordinate-transported high-root bases and activity, check the complete dimension formulas at all degrees through forty-four and at one hundred and one hundred one, and reject malformed declarations. These finite tests supplement the proofs; the all-degree conclusions rest on polynomial identities and valuation arguments. Earlier external-solver classifications keep their original evidence status, and no new formal-kernel claim is made.

The remaining global question is narrower: which of these low-dimensional local solution spaces extend to global polynomial partners for squarefree or other low-multiplicity sextics in unbounded degree? A rational differential-operator gcd with explicit Bezout identities, or a theorem bounding the degrees of squarefree exceptions, would be a substantial next step. Checking degrees twenty-one through a larger finite cutoff would remain finite evidence. Any proposed global result must agree with the exact boundary strata and local resonance constraints proved here.
