# A classified boundary for particlewise ellipticization

This result classifies one deliberately restrictive construction attempt.
It is new to this programme; worldwide priority has not been established.
It does not exclude double-elliptic systems, the Koroteev–Shakirov current,
position-dependent momentum moduli, changed coordinate weights, spin
variables, or non-particlewise couplings. Its purpose is to prove exactly
why replacing each Ruijsenaars momentum by one common elliptic profile is
insufficient when the old coordinate coefficients are retained.

The theorem concerns the full three-particle phase space. It is not asserted
as a theorem about a separately constrained or Dirac-reduced phase space.

## Setup and conventions

Use multiplicative canonical coordinates with

\[
 \{x_i,y_j\}=\delta_{ij}x_i y_j,\qquad
 \{x_i,x_j\}=\{y_i,y_j\}=0.
\]

For three distinct nonzero positions and coupling \(T\), put

\[
 a_I(x;T)=\prod_{i\in I,\,j\notin I}
                 \frac{Tx_i-x_j}{x_i-x_j}.
\]

The standard trigonometric RS Hamiltonians are
\(H_a=\sum_{|I|=a}a_I\prod_{i\in I}y_i\), for \(a=1,2\).
Their classical involutivity is the imported, attributed RS construction;
this project does not claim that classical result. Replace the momenta by
one scalar meromorphic profile \(f\):

\[
 H_1[f]=\sum_i a_{\{i\}}f(y_i),\qquad
 H_2[f]=\sum_{i<j}a_{\{i,j\}}f(y_i)f(y_j).
\]

Here and below, involutivity means an identity for all permitted positions
and independent momenta, rather than an equality on a finite point panel.
No momentum-dependent correction to \(a_I\) is allowed in this ansatz.

## Theorem: the complete coupling/profile boundary

Let \(f\) be meromorphic on a connected cover of \(\mathbb C^*\).
Suppose the above Hamiltonians Poisson commute identically.

If \(T=1\), all \(a_I=1\), so every profile works: the Hamiltonians depend
only on the mutually commuting momenta.

If \(T\ne1\), then either \(f\) is constant, or on every suitable local
logarithm chart

\[
 \boxed{f(y)=C y^\lambda.}
\]

The same \(\lambda\) continues throughout the connected cover. Conversely,
such a power profile multiplies the standard RS Poisson bracket by
\(\lambda\), so the imported RS involutivity supplies sufficiency.
If \(f\) is globally single-valued and meromorphic on \(\mathbb C^*\), then
\(\lambda\in\mathbb Z\). A nonconstant meromorphic function on a genuine
momentum elliptic curve \(\mathbb C^*/P^{\mathbb Z}\), \(0<|P|<1\), is
therefore impossible in this ansatz for every \(T\ne1\).

This is a sharp boundary of the declared ansatz. It is not a classification
of DELL systems.

## Exact two-witness proof

Write \(z_i=f(y_i)\), \(g_i=y_i f'(y_i)\), and
\(D_i=x_i\partial_{x_i}\). Direct differentiation gives

\[
 \{H_1[f],H_2[f]\}=\sum_i g_i P_i(z),\qquad
 P_i=(D_iH_1)\partial_{z_i}H_2-a_{\{i\}}D_iH_2.
\]

Every \(P_i\) is quadratic in \(z\) and of coupling degree at most four:
each \(a_I\) and \(D_i a_I\) has coupling degree at most two.

At \(x=(1,3,7)\), set \(z=(z,s,s)\). The exact identities are

\[
 P_1=K_1(T)s(s-z),\qquad
 P_2+P_3=-K_1(T)z(s-z),
\]

where indices in this document start at one, and

\[
 K_1(T)=\frac{5T^4-26T^3+126T-105}{72}.
\]

At \(x=(1,2,5)\), the same identities hold with

\[
 K_2(T)=\frac{7T^4-27T^3+90T-70}{16}.
\]

These are not numerical fits. The derivative compiler constructs every
quadratic monomial coefficient with rational arithmetic. For each witness,
the identities are replayed at the five distinct couplings \(0,1,2,3,4\).
The proved degree bound of four makes those five exact evaluations a
polynomial identity certificate valid for every complex coupling.

Let \(A=72K_1\) and \(B=16K_2\). Exact integer polynomial multiplication
certifies the Bezout identity

\[
\begin{aligned}
 &A(-529875-72145T+142128T^2)\\
 &\quad+B(835114+187859T-101520T^2)
       =2821105(T-1).
\end{aligned}
\]

Thus \(K_1\) and \(K_2\) have no common zero except \(T=1\). For every
other coupling, at least one coordinate witness gives, on substituting
\(y=(u,v,v)\),

\[
\boxed{
 \{H_1[f],H_2[f]\}
 =K(T)(f(v)-f(u))
       \bigl(f(v)u f'(u)-f(u)v f'(v)\bigr).
}
\]

If \(f\) is nonconstant, on a patch away from its zeros and poles the first
factor is nonzero for generic \(u,v\). Hence

\[
 \frac{u f'(u)}{f(u)}=\frac{v f'(v)}{f(v)}=\lambda.
\]

The identity theorem extends this relation across the connected domain.
Solving \(y f'=\lambda f\) gives the claimed local powers. Single-valued
continuation around zero requires \(e^{2\pi i\lambda}=1\), so \(\lambda\)
is integral on \(\mathbb C^*\). Momentum ellipticity would require
\(f(Py)=f(y)\), hence \(P^\lambda=1\). Since \(0<|P|<1\), the only integral
possibility is \(\lambda=0\), giving a constant profile. This completes the
analytic proof; the finite code certificate verifies its exact algebraic
premises, not the identity theorem itself.

## Abstract multiaffine lemma and persistence into the elliptic regime

The scalar-profile obstruction does not require the special form of the
trigonometric coefficients once one nonzero witness has been found.
Let

\[
 h_1(z)=\sum_i a_i(x)z_i,\qquad
 h_2(z)=\sum_{i<j}a_{ij}(x)z_i z_j
\]

be any multiaffine Hamiltonian pair on the same multiplicative canonical
phase space. Assume \(\{h_1(y),h_2(y)\}=0\) identically. The same derivative
formula defines quadratic polynomials \(P_i\), and base involutivity says

\[
 z_1P_1+z_2P_2+z_3P_3=0.
\]

At \(z=(z,s,s)\), therefore,

\[
 P_2+P_3=-\frac zs P_1,
\qquad
 \{h_1[f],h_2[f]\}
 =P_1(f(u),f(v),f(v))
       \left(uf'(u)-\frac{f(u)}{f(v)}vf'(v)\right).
\]

**Lemma.** If, at some permitted coordinate point, the polynomial
\(P_1(z,s,s)\) is not identically zero, any nonconstant common meromorphic
profile preserving commutativity must satisfy \(yf'/f=\lambda\).

To prove the lemma, restrict away from zeros and poles of \(f\). A
nonconstant meromorphic function has open image there. Consequently the
substitution of two independent values \(f(u),f(v)\) into a nonzero
polynomial cannot vanish identically. On the resulting nonempty open set
the second factor must vanish; the meromorphic identity theorem extends
that equality. This reproduces the scalar ODE and the power classification.
The lemma is conditional on base involutivity and on a nonzero witness.
It does not assert either premise for an arbitrary proposed model.

Now suppose the coefficients are holomorphic in the coordinate elliptic
nome \(P\) near zero, remain multiaffine in the momenta, commute before
substitution, and specialize to the above standard RS coefficients at
\(P=0\). Standard elliptic RS, in a consistently normalized momentum
chart, supplies the motivating example. For every fixed nonzero
\(T\ne1\), choose
one of our two coordinate witnesses with \(K_r(T)\ne0\). At \(z=2,s=3\),

\[
 P_1(2,3,3;P)=3K_r(T)+O(P).
\]

The constant term is nonzero. Thus there exists \(\delta(T)>0\) such that
the abstract lemma applies for every \(|P|<\delta(T)\), including genuinely
elliptic \(P\ne0\). This is an analytic neighborhood theorem, not an
extrapolation from finitely many nome coefficients. No explicit radius is
computed. On any connected domain on which this same witness is
holomorphic and extends from zero, its zero set is discrete. The lemma
therefore also applies away from that discrete set. No assertion is made
at the exceptional zeros, at poles of the chosen chart, or uniformly for
all elliptic moduli.

There is a parallel formal statement. If the coefficients are formal power
series in \(P\), and \(f(y;P)\) has nonconstant leading profile, the nonzero
constant witness makes \(P_1(f(u;P),f(v;P),f(v;P))\) a nonzero formal
series of meromorphic functions. Cancellation in that integral domain
again forces

\[
 y\partial_y f(y;P)=\lambda(P)f(y;P),\qquad
 f(y;P)=C(P)y^{\lambda(P)}
\]

on a logarithm cover. If every coefficient is globally single-valued and
meromorphic on \(\mathbb C^*\), the leading exponent is integral and every
higher coefficient of \(\lambda(P)\) must vanish: its first nonzero term
would introduce a forbidden \(\log y\). Thus only \(C(P)y^m\), with a fixed
integer \(m\), survives. This formal assertion assumes a nonconstant
leading profile and does not classify singular expansions whose leading
profile degenerates to a constant.

## First-order obstruction and exact negative control

For a formal scalar substitution
\(f_\epsilon(y)=y+\epsilon h(y)+O(\epsilon^2)\), the same witness gives

\[
\begin{aligned}
 [\epsilon]\{H_1,H_2\}
  =K(T)(v-u)\bigl[&v(uh'(u)-h(u))\\
                 &-u(vh'(v)-h(v))\bigr].
\end{aligned}
\]

Thus a first-order correction in this ansatz satisfies
\(y h'(y)-h(y)=\kappa y\), and therefore

\[
 h(y)=y(c+\kappa\log y).
\]

The logarithmic term changes the local exponential slope; it is excluded
for single-valued meromorphic corrections on \(\mathbb C^*\). Only the
overall scaling \(h=cy\) survives there. Any nontrivial positive or negative
Laurent mode is obstructed in this unchanged-weight scalar ansatz.

For a completely explicit negative control, take \(T=2\), \(x=(1,3,7)\),
\(y=(2,3,3)\), and \(f_\epsilon(y)=y+\epsilon/y\). Exact expansion gives

\[
 \boxed{\{H_1,H_2\}=-\frac{95}{216}\epsilon
                         +\frac{95}{1296}\epsilon^2.}
\]

The constant and cubic coefficients are exactly zero. This one example is
not the classification proof; it is a replayable sign-sensitive control.
The implementation also checks multiple power profiles as positive controls
and verifies that \(T=1\) has zero coordinate derivatives for every profile.

## Relation to published DELL constructions

Koroteev and Shakirov, *The Quantum DELL System*,
[arXiv:1906.10354](https://arxiv.org/abs/1906.10354), equations (1.10)–(1.11),
define Hamiltonians by normalized Fourier modes of an infinite current.
That current introduces mixed momentum shifts and changes the interaction
coefficients together with the shifts. It lies outside the ansatz classified
here, so the theorem neither contradicts nor proves their conjecture.

The standard RS involutivity used for sufficiency is classical: see
S. N. M. Ruijsenaars, *Complete integrability of relativistic Calogero–Moser
systems and elliptic function identities*, Communications in Mathematical
Physics **110** (1987), 191–213,
[doi:10.1007/BF01207363](https://doi.org/10.1007/BF01207363).
Our elementary obstruction proof fixes the nonsymmetric multiplicative
coefficient convention explicitly and does not identify its momentum chart
with an unadjusted oriented-theta current convention.

The theorem motivates testing coupled corrections, altered coordinate
coefficients, or position-dependent momentum geometry. It does not establish
that any one of those enlargements is sufficient, nor does it select a unique
new interaction or prove a quantum double-elliptic identity.

## A forced mixed harmonic in the normalized current

The normalization itself produces mixed momentum harmonics. To make signs
unambiguous, write the sign-stripped classical current modes as

\[
 A_a=\sum_{\sum n_i=a}
 W^{\sum_i n_i(n_i-1)/2}
 \prod_{i<j}\frac{\theta(T^{n_i-n_j}x_i/x_j;P)}
                       {\theta(x_i/x_j;P)}\,y^n.
\]

The actual Fourier mode of the KS current with \((-z)^{\sum n_i}\) is
\(O_a=(-1)^a A_a\). At order \(W^0\), \(A_0=1\). At order \(W^1\), the
charge-one numerator \(A_1\) has precisely the three permutations of
\((-1,1,1)\); the charge-zero denominator has precisely the six permutations
of \((-1,1,0)\). This enumeration is exhaustive because each cost
\(n_i(n_i-1)/2\) is nonnegative and cost at most one forces
\(n_i\in\{-1,0,1,2\}\).

For the positive-sign Hamiltonian \(\widetilde H_1=A_0^{-1}A_1\), the first
nome correction is \(A_1^{[1]}-A_0^{[1]}A_1^{[0]}\). Its momentum harmonic
\((-1,2,0)\) receives no contribution from \(A_1^{[1]}\), and exactly one
contribution from the normalization product:

\[
 [W y_1^{-1}y_2^2]\widetilde H_1
 =-c_{(-1,1,0)}c_{(0,1,0)},\qquad
 c_n=\prod_{i<j}\frac{\theta(T^{n_i-n_j}x_i/x_j;P)}
                              {\theta(x_i/x_j;P)}.
\]

At \(P=0,T=2,x=(1,3,7)\), these factors are exactly
\(143/384\) and \(5/16\), giving \(-715/6144\). For the actual KS
Hamiltonian \(H_1=O_0^{-1}O_1=-\widetilde H_1\), the coefficient is
\(+715/6144\). The sign is a Hamiltonian convention; nonvanishing is not.
The theta-product expression establishes generic nonvanishing, and the
exact rational value supplies an independent replay.

This mode is forced within the specified normalized current; it cannot be
represented by its original finite positive subset momentum support.
It is not by itself evidence of a novel interaction: even at \(T=1\), where
all coefficients become position-independent and commutativity is trivial,
the same normalization creates mixed harmonics. Nor does this support
calculation prove full classical or quantum DELL commutativity.

## Reproduction

`src/perfectjet/dell_obstructions.py` contains the exact differentiation
compiler, the two coupling-polynomial certificates, the integer Bezout
identity, the negative control and JSON-safe receipt.
`tests/test_dell_obstructions.py` independently checks diagonal identities
outside the interpolation panel, alternative position witnesses, power
profiles, the complete inverse-mode counterexample and input rejection.

Run `PYTHONPATH=src python -m unittest discover -s tests -p test_dell_obstructions.py -v`.
