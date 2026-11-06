# First seventh-mass-response minimum

## Theorem

Let `I` be the normalized threshold-nine three-particle ordinary scalar after the definite angular endpoints and outer integration, over `C(s,t)` at fixed nonzero mass scale `M`. Deform only the seventh squared mass by

\[
m_7^2=M\rho,
\qquad
\left.\partial_\rho I\right|_{\rho=1}=M J_{64}.
\]

On the distinguished physical threshold branch and all of its ordered analytic continuations,

\[
\boxed{r_{\rm phys}(I,MJ_{64})
      =r_{\rm phys}\!\left(I,\left.\partial_\rho I\right|_{\rho=1}\right)
      =16.}
\]

The universal joint observable module has rank 18. The physical Gram relation lowers it to rank 17. A second rational invariant hyperplane, selected to zero by the physical threshold germ, lowers the distinguished physical system to rank 16. Thus first sensitivity to the seventh mass requires no additional physical state beyond the already minimal ordinary scalar representation.

## Universal joint module

The proven scalar observable frame has rank 17. Reducing the pure `J64` coordinate row against that frame leaves a nonzero residual `r`, normalized at restricted source pivot 30. Its support is exactly the six restricted coordinates `{3,8,9,15,27,30}`. Exact covariant reduction gives

\[
\nabla_s r\equiv \frac{t}{2s(s+t)}r,
\qquad
\nabla_t r\equiv-\frac{s+2t}{2t(s+t)}r
\pmod{\mathcal O_{17}}.
\]

Hence the new quotient line has character

\[
\chi=\frac12d\log\frac{s}{t(s+t)},
\]

and the joint universal module has exact rank 18.

## Physical restrictions

The existing Gram-character relation omits the new residual row, so it lowers the joint system from 18 to 17. Its closed lower projection has rank 13: the old twelve-dimensional physical lower projection plus the new line.

Write the lower rank-13 connection as

\[
d\binom zw=
\begin{pmatrix}A&0\\u&\chi\end{pmatrix}\binom zw,
\qquad z\in\mathbb C^{12}.
\]

There is an explicit rational row `g=(g_0,...,g_11)` satisfying, for `a=s,t`,

\[
\partial_a g+gA_a+u_a-\chi_a g=0.
\]

All 24 component identities are checked exactly over `Q(s,t)`. Therefore

\[
\mathcal H_{\rm mass}=w+\sum_{i=0}^{11}g_i z_i
\]

obeys

\[
\boxed{d\mathcal H_{\rm mass}
=\frac12d\log\frac{s}{t(s+t)}\,\mathcal H_{\rm mass}.}
\]

After exact cancellation, the source support of this hyperplane is

\[
\{9,10,12,23,24,25,26,33,34,35,36,51,52,54,55,57\}.
\]

Every one of these is an undotted lower master. The rational coefficients are regular at `(s,t)=(9,-3)`, while the certified physical threshold theorem makes every undotted entry `O((s-9)^2)`. Since

\[
\frac{s}{t(s+t)}\bigg|_{(9,-3)}=-\frac12\ne0,
\]

the quotient

\[
\frac{\mathcal H_{\rm mass}}{\sqrt{s/[t(s+t)]}}
\]

is locally constant with zero threshold limit. Hence `H_mass=0` on the distinguished physical germ and on every analytic continuation of that germ.

## Explicit reconstruction

The verifier reconstructs a rational 16-coordinate readout `d_phys` satisfying the exact source-row identity

\[
e_{64}-d_{\rm phys}R_{\rm phys}
=\lambda\,H_{\rm mass}+\mu\,H_{\rm Gram}.
\]

Both invariant hyperplanes vanish on the selected physical solution. Therefore `J64` is recovered from the same 16-state physical frame already sufficient for `I`. This gives a rank-16 upper bound for the pair. The scalar `I` alone already has certified minimum 16, so the pair cannot have smaller rank.

## Scope

This theorem concerns only the first derivative at `rho=1`. It does not assert that the finite unequal-mass family for `rho != 1` remains rank 16, and it does not transfer equal-mass differential-field minimality to that full family. It proves that the infinitesimal seventh-mass response is exactly observable from the existing minimal physical scalar system.

## Replay

Run:

```bash
python first_mass_response_minimum.py
```

The principal machine-readable receipts are:

- `first_mass_response_minimum_certificate.json`
- `joint_mass_response_certificate.json`
- `physical_mass_response_hyperplane_certificate.json`
- `physical_J64_readout_certificate.json`

The consolidated verifier replays the exact rank-18 closure, all 24 rational hyperplane identities, the exact 16-state `J64` readout, the threshold regularity checks, and the inherited rank-16 scalar minimum dependency.
