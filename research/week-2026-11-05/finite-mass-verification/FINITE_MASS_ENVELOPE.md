# Finite unequal-mass control and the second mass jet

## A sharp anchor theorem for the crossed box

**Conventions.** Let \(I(\rho)\) be the complete seven-propagator scalar crossed-box integral (not a maximal cut) in the retained DPS conventions, with \(D=4\), squared masses \(m_1^2=\dots=m_6^2=M>0\), \(m_7^2=M\rho\), and fixed kinematics \((s,t)=(3M,-M)\). Fix the positive subthreshold projective branch, \(\rho>0\). The loop normalization is the one used in `physics/kinematics/physical_dictionary.md`; at \(\epsilon=0\), its projective prefactor is \(-\Gamma(3)=-2\). The physical first-derivative master is \(I'(1)=MJ_{64}\), as already established in the first-response theorem. Put \(I_*=I(1)\), \(D_*=I'(1)\), \(W_*=-I_*>0\).

**Theorem.** The positive-mass function admits a generalized Stieltjes representation of order three,

\[
\boxed{ I(\rho)=-\int_0^1\frac{d\nu(b)}{[1+(\rho-1)b]^3},\qquad
\nu\ge0,\quad \nu([0,1])=W_*,\quad\int b\,d\nu(b)=D_*/3. }
\]

The support is contained in \([0,1]\), and the endpoint bound \(1\) is sharp for the underlying projective rational map. Consequently the optimal bounds determined **only** by the two already observable scalars \(I_*\), \(D_*\), and the support bound are, for every real \(\rho>0\),

\[
\boxed{
I_*+\frac{1-\rho^{-3}}{3}D_*
\ \le\ I(\rho)\ \le\
I_*\left[1+\frac{(\rho-1)D_*}{3W_*}\right]^{-3}
\ \le\ I_*+(\rho-1)D_* .}
\]

The first inequality is the endpoint-chord bound; the middle is the nonlinear Jensen bound. The two endpoint extremes are optimal among all positive measures on \([0,1]\) with the same total mass and first moment, although the specific crossed-box measure is more restrictive. Both inequalities are strict for \(\rho\neq1\) on the actual physical integral.

The **second mass jet** is nonzero and has a certified sign and quantitative bounds:

\[
\boxed{
I''(1)=2M^2J_{7^3}<0,\quad
\frac{4D_*^2}{3W_*}\ \le\ -I''(1)\ \le\ 4D_* .}
\]

Here \(J_{7^3}\) denotes the same normalized seven-line integral with its seventh propagator cubed; it is not asserted to be a new IBP-basis element. The estimates do not determine its exact value or its separate observable-minimal rank.

The entire positive-mass family is completely monotone after changing its sign:

\[
(-1)^k\frac{d^k}{d\rho^k}[-I(\rho)]>0,\qquad \rho>0,\ k=0,1,2,\ldots,
\]

and is holomorphic for \(\operatorname{Re}\rho>0\). In particular its Taylor series about \(\rho=1\) converges absolutely for \(|\rho-1|<1\), with coefficients given by the moments of \(\nu\):

\[
\boxed{ I^{(k)}(1)=(-1)^{k+1}(3)_k\int_0^1 b^k\,d\nu(b). }
\]

## Exact positivity identity

Use homogeneous projective parameters \(a_i\ge0\), \(S=\sum_i a_i\), and the retained polynomials

\[
\begin{aligned}
 X&=a_1+a_2+a_3,\qquad Y=a_4+a_5,\qquad Z=a_6,\qquad W=a_7,\\
 \mathcal U&=XY+(X+Y)(Z+W),\\
 P_s&=a_1a_3(Y+Z+W)+a_1a_5W+a_3a_4Z,\\
 P_t&=a_2a_5Z,\qquad P_u=a_2a_4W,\\
 \mathcal F_1/M&=S\mathcal U-3P_s+P_t+2P_u.
\end{aligned}
\]

The decisive strict improvement on the inherited \(\mathcal F_1\ge M\mathcal U/4\) is

\[
\boxed{\mathcal F_1/M-a_7\mathcal U=Y B_Y+ZB_Z+WB_W,}
\]

where

\[
\begin{aligned}
 B_Y&=X(X+Y+Z)-3a_1a_3,\\
 B_Z&=(X+Y+Z)(X+Y)-3a_3(a_1+a_4)+a_2a_5,\\
 B_W&=(X+Y+Z)(X+Y)-3a_1(a_3+a_5)+2a_2a_4.
\end{aligned}
\]

Each bracket is visibly nonnegative using the following explicit sum-of-squares and nonnegative-monomial decompositions. Put \(A_Z=a_1+a_3+a_4\), \(D_Z=a_2+a_5\), \(A_W=a_1+a_3+a_5\), \(D_W=a_2+a_4\). Then

\[
\begin{aligned}
 B_Y={}&(a_1-a_3)^2+a_1a_3+a_2(2a_1+2a_3+a_2)+X(Y+Z),\\
 B_Z={}&[a_3-(a_1+a_4)]^2+a_3(a_1+a_4)+2A_ZD_Z+D_Z^2+Z(A_Z+D_Z)+a_2a_5,\\
 B_W={}&[a_1-(a_3+a_5)]^2+a_1(a_3+a_5)+2A_WD_W+D_W^2+Z(A_W+D_W)+2a_2a_4.
\end{aligned}
\]

All polynomial identities are exact over \(\mathbb Z[a_1,\ldots,a_7]\), replayed in `finite_mass_envelope.py`. Thus \(\mathcal F_1\ge Ma_7\mathcal U\), and

\[
 b=\frac{Ma_7\mathcal U}{\mathcal F_1}\in[0,1].
\]

For \(a_1=\eta\), \(a_7=1-\eta\), other parameters zero, the limit is \(b=1-\eta\to1\), establishing the sharp endpoint (the limiting projective vertex itself has \(\mathcal U=0\) and is not taken as an interior point).

Since \(\mathcal F_\rho=\mathcal F_1+M(\rho-1)a_7\mathcal U\), the normalized density is exactly

\[
 I(\rho)=-2\int_{\Delta_6}\frac{\mathcal U}{\mathcal F_1^3}\,[1+(\rho-1)b]^{-3}\,d^6a,
\]

where \(\Delta_6\) has the standard projective Lebesgue measure. The measure \(d\nu\) is the positive pushforward of \(2\mathcal U/\mathcal F_1^3\,d^6a\) along \(a\mapsto b(a)\). The existing subthreshold convergence theorem makes it finite; for any \(\rho>0\), the ratio is bounded away from zero by \(\min(1,\rho)\), hence the deformed integral remains finite on the chosen branch.

## Proof of the optimal two-observable envelope

Put \(m=D_*/(3W_*)\in(0,1)\). Normalize \(d\pi=d\nu/W_*\). The function \(f_\rho(b)=[1+(\rho-1)b]^{-3}\) is convex on \([0,1]\), and its second derivative is \(12(\rho-1)^2[1+(\rho-1)b]^{-5}\). Jensen's inequality and the endpoint chord give

\[
 f_\rho(m)\le\int f_\rho(b)\,d\pi(b)\le (1-m)f_\rho(0)+mf_\rho(1)
 =1-m+m\rho^{-3}.
\]

Multiplication by \(-W_*\) reverses the inequalities and yields the theorem. The tangent bound uses \(1-\rho^{-3}\le3(\rho-1)\), which follows from the convexity of \(x^{-3}\) (or \(3\rho+\rho^{-3}\ge4\)). Jensen equality for a one-point measure at \(b=m\), and endpoint-chord equality for the Bernoulli measure \((1-m)\delta_0+m\delta_1\), prove optimality among measures with the same \((W_*,m)\). The actual measure has interior support and is not concentrated at these extremes.

Differentiating under the positive integral gives \(D_*=3\int b\,d\nu\), \(-I''(1)=12\int b^2\,d\nu\). The support inequality \(b^2\le b\) yields the upper second-jet bound; Cauchy–Schwarz gives \((\int b\,d\nu)^2\le W_*\int b^2\,d\nu\), yielding the lower bound. The same argument proves all alternating-sign derivatives, the holomorphic half-plane, and the moment expansion.

## Exact finite displacement coefficients

At \(\rho=7/8\),

\[
\boxed{
I_*-\frac{169}{1029}D_*\ \le I(7/8) \le\
I_*\left(1-\frac{D_*}{24W_*}\right)^{-3}
\ \le I_*-\frac18D_* .}
\]

At \(\rho=9/8\),

\[
\boxed{
I_*+\frac{217}{2187}D_*\ \le I(9/8) \le\
I_*\left(1+\frac{D_*}{24W_*}\right)^{-3}
\ \le I_*+\frac18D_* .}
\]

The signed first-order Taylor remainder is always nonpositive. Its **absolute** certified bounds at these points are

\[
\begin{aligned}
0&\le -[I(7/8)-I_*+D_*/8]\le\frac{323}{8232}D_*,\\
0&\le -[I(9/8)-I_*-D_*/8]\le\frac{451}{17496}D_*.
\end{aligned}
\]

These numerical coefficients are exact rational numbers. They give a finite-mass interval in terms of two exact equal-mass physical observables, both in the minimal rank-16 frame. An **absolute numerical enclosure** for \(I(7/8)\) or \(I(9/8)\) would additionally require rigorous enclosures for \(I_*\) and \(D_*\); the separately supplied Sobol estimates are crosschecks, not such enclosures.

## Physical and mathematical scope

The statement is for the full uncut seven-propagator scalar at the fixed regular subthreshold anchor and \(D=4\), without analytic continuation across a moving singular divisor. It supplies a nonzero second jet, its sign, quantitative moment bounds, and certified finite-mass *relative brackets*, not an exact evaluation of the triple-dotted integral. It neither asserts rank 16 for the second jet nor for the finite unequal-mass family. The rank-16 first-response theorem at \(\rho=1\) is a separate, previously certified statement with specified threshold-nine physical continuation; the present bound is at a different kinematic point on the same equal-mass analytic branch.

## Reproduction

The independently constructed exact proof is in `finite_mass_envelope.py`, with emitted `finite_mass_envelope_certificate.json`. It recomputes the Symanzik polynomial, proves the full sum-of-squares decomposition over integers, checks the exact \(\rho\)-derivatives and the rational endpoints, and certifies the sharp projective endpoint. The source polynomial dictionary is preserved as `crossed_box.py`. The optional script `mass_qmc_diagnostic.py` runs independently scrambled simplex integration and records its sampling errors in `mass_qmc_diagnostic.json`; its outputs are deliberately excluded from the proof premises.
