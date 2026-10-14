# Transvectant Rank-Loci: Exact Status, R5 Settled and Corrected

## The framework is sound

The molecular program rests on one correct identification: for binary forms
$f,g$, the order-$k$ term of the Moyal bracket is the $k$-th transvectant
$(f,g)_k$ (the classical Überschiebung), so Weyl-exactness
$\tfrac1{i\hbar}[f,g]_\star=\{f,g\}$ is exactly the vanishing of all odd
transvectants $(f,g)_k=0$ for $3\le k\le\min(\deg f,\deg g)$. For a sextic $f$
the active gates are $(f,g)_3$ and $(f,g)_5$. This is equivalent to the earlier
$S_k$ coefficient criterion and is correct.

Independently re-verified over $\mathbb Q$ (exact, not finite-field):

- $(f,f)_3=(f,f)_5=0$ for every sextic (self-pairs, by transvectant antisymmetry).
- $(f,(f,f)_4)_3\equiv 0$: every sextic has the universal quartic partner $(f,f)_4$.
- The $C_3$ family $f_\lambda=x^6+\lambda x^3y^3+y^6$ has the eighth-degree partner
  $g_8=xy(x^6+y^6-\tfrac{7\lambda}{20}x^3y^3)$, with $(f_\lambda,g_8)_3=(f_\lambda,g_8)_5=0$.
- The catalecticant $\det(f,\cdot)_3$ restricted to the $C_3$ family is
  $15116544\,\lambda^2(\lambda-20)(\lambda+20)$.
- The reported squarefree $R_5$ pair $g=-xy(x-y)(x^2-xy+y^2)$,
  $f=\tfrac12(2x^6-6x^5y+5x^4y^2+5x^2y^4-6xy^5+2y^6)$ is genuine: $g$ is squarefree,
  the Poisson bracket $(f,g)_1$ is a nonzero degree-9 form, yet $(f,g)_3=(f,g)_5=0$.

So the established loci $R_3=V(\Delta_3)$ (catalecticant hypersurface),
$R_4=R_6=\mathbb P(V_6)$ (universal partners), and
$R_8=C_4^{-1}(\nu_2(\mathbb P V_2))$ (quartic covariant is a quadratic square) hold,
and the $R_5$ squarefree phenomenon is real, not a collision artifact.

## R5 is now an exact theorem (and the orbit count was wrong)

Take the normalized quintic partner $g=xy(x-y)(x-ay)(x-by)$, two free roots.
The rank-drop map $L_g:V_6\to V_5\oplus V_1$, $f\mapsto((f,g)_3,(f,g)_5)$, is an
$8\times7$ matrix over $\mathbb Q[a,b]$. Its eight maximal minors generate an ideal
whose elimination in $b$ factors, **over $\mathbb Q$**, as

$$
b^6(b-1)^6\,(b^2-3b+3)(b^2-b+1)(b^2+b+1)(3b^2-3b+1).
$$

The collision factor $b^6(b-1)^6$ is the high-root boundary $H_4=\{f=\ell^4 h_2\}$.
The four quadratics give $12$ squarefree solutions.

**Correction.** The transcript classified these into "three projective orbits."
A rigorous test — constructing explicit Möbius maps between configurations rather
than comparing invariants — shows all twelve squarefree points form a **single**
$\mathrm{PGL}_2$ orbit. The exceptional configuration is
$\{0,1,\infty,\omega,e^{i\pi/3}\}$ with $\omega$ a primitive cube root of unity; its
projective automorphism group has order $4$.

This is the clean statement:

> **Theorem (R5, exact, char 0).** Outside the safe zone, a sextic $f$ admits a
> *squarefree* quintic partner $g$ with $(f,g)_3=(f,g)_5=0$ and $\{f,g\}\ne0$ iff the
> root configuration of $g$ lies on the high-root boundary $H_4$ or on the single
> exceptional $\mathrm{PGL}_2$ orbit above. The $b$-locus factorization is exact over
> $\mathbb Q$.

The full set $R_5 = H_4 \cup O_{\mathrm{exc}}$ — one boundary stratum and one
exceptional orbit, not a family.

## R7, R9: still modular, not characteristic-zero

The transcript's $R_7$ and $R_9$ emptiness claims rest on finite-field Rabinowitsch
certificates $(\langle\text{minors}\rangle:\Delta^\infty)=\langle1\rangle$ over
$\mathrm{GF}(p)$, on individual root-patches ($d=2$, fixed triples). Those are real
evidence — the same selected minors certifying many patches and primes is a strong
sign — but they are not a proof. Two honest gaps remain, both acknowledged in the
transcript:

- A finite set of patches over finite fields is not the whole squarefree moduli
  space over $\mathbb Q$. A generic-parameter certificate, or a covering argument,
  is required.
- The exact $\mathbb Q$ Gröbner/saturation that would settle even one patch is
  heavy. It is confirmed infeasible in sympy (the $R_7$ $d{=}2$ certificate over
  $\mathbb Q[a,b,c,t]$ does not terminate), and the transcript's own environment had
  no Singular/Macaulay2/Sage. So "$R_7^{\text{sqfree}}=\varnothing$,
  $R_9^{\text{sqfree}}=\varnothing$" should be stated as **conjectural, modularly
  supported**, not proved.

The natural finish is a real CAS: compute $(I:\Delta^\infty)$ over $\mathbb Q$ in
Macaulay2/Singular for the generic squarefree chart, or prove the selected-minor
certificate lifts to $\mathbb Q(d)$.

## Framing, calibrated

The machinery here — transvectants, catalecticants, apolarity, the Veronese of
quadratic squares, $\mathrm{PGL}_2$-equivariant covariants — is classical 19th-century
invariant theory of binary forms. What is genuinely contributed is the *application*:
reading Moyal/Weyl exactness as the vanishing of odd transvectants, and the explicit
rank-loci dictionary $R_3,R_4,R_5,R_6,R_8$ for sextics. The "no-go theorem has hidden
corridors / hits the newspapers" framing overstates it: Groenewold–van Hove is about
the nonexistence of a *full* quantization homomorphism, and "specific observable pairs
whose bracket is reproduced exactly" is a real but much more modest refinement — closer
to a structure theorem for transvectant kernels than to a reversal of the no-go result.
Stated plainly and correctly it is still a nice piece of mathematics.

## Where it continues

1. **R5 is done** — write it as the exact theorem above; it is the first
   characteristic-zero result of the molecular layer and corrects the orbit count.
2. **R7/R9** need a genuine CAS certificate over $\mathbb Q$ before any emptiness
   claim is publishable; until then they are conjectures with modular support.
3. The cleaner mathematical object is the **incidence variety**
   $I_N=\{([f],[g]):(f,g)_3=(f,g)_5=0\}\subset\mathbb P(V_6)\times\mathbb P(V_N)$ and
   the geometry of its projection to $\mathbb P(V_6)$ — that is where the catalecticant,
   the Veronese, and the exceptional $R_5$ orbit all sit, and where a real theorem
   (rather than a patch table) would live.

All numerics regenerated from `verify_transvectant_rank_loci.py`.
