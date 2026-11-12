#!/usr/bin/env python3
"""Build a self-contained mathematical synthesis; no network assets required."""
from pathlib import Path
from html import escape
import re
from latex2mathml.converter import convert

ROOT = Path(__file__).resolve().parent
PIN = 'https://github.com/towre676-cloud/PerfectJet/blob/9b69eab9beff3011bc6216b30a460c2c6d0e97be/'

def lib(identity):
    return 'https://chatgpt.com/library?file_id='+identity+'&account_id=personal'

SOURCES = [
 ('pj', 'PerfectJet v0.21.0', 'Published 31 October 2026; current source pinned to 9b69eab9beff3011bc6216b30a460c2c6d0e97be. Release scope and assets were checked; the full upstream regression suite was not rerun here.', 'https://github.com/towre676-cloud/PerfectJet/releases/tag/v0.21.0'),
 ('obs', 'Semantics and target-relative observability', 'Current PerfectJet chapter 7; exact recovery criterion and target-dependent representations.', PIN+'docs/chapters/07_semantics_and_observability.md'),
 ('closure', 'Feature closure, quantified defects, and decisions', 'Current PerfectJet chapter 8; closure identities, residual augmentation, separate input defects, and sensitivity equations.', PIN+'docs/chapters/08_feature_closure_error_and_decisions.md'),
 ('scalar', 'PSG scalar balance and coefficient geometry', 'Current PerfectJet chapter 10 explicitly limits its root computation to numerical replay. The interval-assisted proof in this synthesis strengthens that result.', PIN+'docs/chapters/10_PSG_scalar_and_coefficient_geometry.md'),
 ('jets', 'Jets, Schröder equations, and obstruction', 'Current PerfectJet chapter 11; reflection requires an involution, and a finite jet alone does not determine an additional coefficient.', PIN+'docs/chapters/11_jets_Schroeder_and_obstruction.md'),
 ('univ', 'univpisot.txt', 'Recovered original scalar family, parameter sweeps, and integral identity. Source windows include lines 6499–6514 and 10000–10349.', lib('libfile_301564ae518c8191acc221fd35c8adf6')),
 ('galois', 'galois2.txt', 'Later threshold and cubic data at lines 43–109; the branch-sign statement is corrected here. A separate passage retracts the exact integral; the analytic proof below resolves that conflict.', lib('libfile_bb8badeb1a3c8191939b03da174dc9d2')),
 ('psg', 'Programmable_Stability_Geometry.docx', 'Multiplier-profile synthesis at lines 52–61. The sign of its multiplier-ratio identity is corrected here.', lib('libfile_9fac0df6cf4481919573e032fd30a48c')),
 ('tri', 'triskelion_writeup.md', 'Displayed six-state graph and directed-edge construction, lines 123–198. Only the finite displayed matrices are certified here; archive extraction and global tiling interpretations are separate claims.', lib('libfile_3117ef75ff4c8191baa3ca37ae0e609d')),
 ('delzant', 'Pisot Embeddings, Delzant Polytop', 'Displayed weighted-translation matrix, lines 115–127. Its claimed rank two is disproved by the exact determinant in the supplied checker.', lib('libfile_014e5b3db7648191afabba9bffaaaca4')),
 ('periodic', 'PSG field theory complete', 'Four-channel centered periodic-table model and closure diagnostics. Its rank-three centering is imposed by its projection.', lib('libfile_035d9e6f38d48191bbd716edf806c54f')),
 ('b5', 'Flavor interactions, physical CP and exact constraint geometry', 'PerfectPower monograph, 8 October 2026, version 29. The scalar counterterm on pages 2–4 is independently checked here; the larger coupled theory is described from its source, not freshly replayed.', lib('libfile_e75de44ca4388191b6b20434c7cd86bc')),
 ('gim', 'Mixed-mass GIM benchmark', 'Previously supplied reproducible fixed-input leading electroweak coefficient, with 80/100-digit checks. No interval or phenomenological-fit claim.', lib('libfile_41eefcc4f594819192fa9b189146d3e9')),
 ('annulus', 'Annular periods publication', 'Current completed publication, HTML version 9. Equal-mass field and rank statements retain their stated hypotheses. Positive-anchor and mass-derivative passages: lines 6278–6283 and 10759–10765.', lib('libfile_7dfdc6fce5d8819187ee71332baff605')),
 ('half', 'Asterion half-braid account', 'Separate exact KZ descent and half-braid results. Their method is relevant to continuation; no identification with the annulus period field is asserted.', PIN+'docs/ASTERION_HALF_BRAID.md'),
]

BODY = r"""
<header>
<div class="eyebrow">Mathematical synthesis · 3 November 2026</div>
<h1>Quotients, closure,<br>and physical observables</h1>
<p class="subtitle">The strongest common structure in the Pisot, PSG, PerfectJet, flavor, and annular-period results</p>
<p class="lead">A reduced description earns its value by preserving a specified answer. Arithmetic structure, a small state space, and a dominant spectral mode each provide useful information; none alone determines which terms a physical calculation can safely discard. The recovered results become coherent when their preserved observables, closure conditions, and error bounds are stated together.</p>
<div class="summary-grid">
<div><b>Exact scalar reduction</b><span>The Pisot-labelled kernel depends only on its quotient exponent. Its logarithmic integral has an exact evaluation.</span></div>
<div><b>Certified local dynamics</b><span>A unique flip is enclosed by interval arithmetic. The corrected local two-cycle is subcritical.</span></div>
<div><b>Observable accuracy</b><span>Finite graph modes, flavor coefficients, and period systems require different sufficient representations.</span></div>
</div>
</header>
<nav aria-label="Contents"><a href="#current">1. Current mathematical position</a><a href="#integral">2. Exact integral</a><a href="#flip">3. Certified flip</a><a href="#psi">4. Stability equivalence</a><a href="#arithmetic">5. Genuine Pisot structure</a><a href="#physics">6. Flavor and period calculations</a><a href="#synthesis">7. One coherent contribution</a><a href="#verification">8. Verification</a><a href="#references">References</a></nav>

<section id="current">
<div class="section-label">1 / Current mathematical position</div>
<h2>The later recoveries supply the organizing principle</h2>
<p>The current PerfectJet release is <strong>v0.21.0</strong>, published on 31 October 2026. Its 744 equations, 27 families and 30 tools supersede the October v0.17 monograph as a release inventory. More useful than the inventory is the mathematical separation already present in its current source: target observability, exact closure, residual repair, and parameter sensitivity. These supply a precise language for bringing the other projects together. <a class="cite" href="#ref-pj">[1]</a> <a class="cite" href="#ref-obs">[2]</a> <a class="cite" href="#ref-closure">[3]</a></p>
<p>For linear measurements \(\mathcal O x\) and a requested target \(Gx\), exact recovery is equivalent to</p>
\[
\ker\mathcal O\subseteq\ker G
\quad\Longleftrightarrow\quad G=L\mathcal O.
\]
<p>The forward implication defines the map \(L\) on the image of \(\mathcal O\); the kernel inclusion makes that definition independent of the chosen preimage. Conversely, a factorization makes the inclusion immediate. A state component may be unobservable while the requested target remains exactly recoverable. Increasing the family of requested targets can require a larger representation.</p>
<p>For polynomial features \(p\) and an update \(F\), the separate question is whether</p>
\[
p\circ F=Gp.
\]
<p>If this identity holds, the feature evolution closes exactly. If it fails, the nonzero residual identifies information the representation loses. Exact output recovery at one point and exact dynamic closure are distinct requirements. The later source implements both checks, including the possibility that no finite augmentation closes the chosen class. <a class="cite" href="#ref-closure">[3]</a></p>
<div class="table-wrap"><table><thead><tr><th>Recovered component</th><th>Strongest retained value</th><th>Its precise scope</th></tr></thead><tbody>
<tr><td>Pisot scalar family</td><td>Exact parameter quotient and integral; certified unique flip</td><td>One specified logarithmic kernel</td></tr>
<tr><td>PSG multiplier synthesis</td><td>Corrected inverse construction and ratio-profile equivalence</td><td>Positive potentials in a fixed state coordinate</td></tr>
<tr><td>Finite triskelion graph</td><td>Exact symmetry decomposition and observable-error bound</td><td>The displayed six-state matrix</td></tr>
<tr><td>PerfectJet</td><td>Target recovery, closure defects, and quantified repair</td><td>Each declared algebraic model and question</td></tr>
<tr><td>Protected flavor</td><td>Exact counterterm obstruction; later coupled tensor calculations</td><td>Specified interactions and approximation orders</td></tr>
<tr><td>Annular periods</td><td>Certified continuation and minimal physical representations</td><td>The established equal-mass family and coefficient fields</td></tr>
</tbody></table></div>
<p>The October flavor monograph also supersedes an assessment based only on the early March flavor drafts. It contains actual canonical matching, scalar-loop tests, and a coupled running system. Its own account carefully distinguishes those achievements from a prediction of the nominated golden CKM coefficient or 66-degree phase. <a class="cite" href="#ref-b5">[12]</a></p>
</section>

<section id="integral">
<div class="section-label">2 / An exact recovered identity</div>
<h2>The logarithmic integral is exact</h2>
<p>Set</p>
\[
W(x)=-\log(\cos x)+ix,
\qquad J(\alpha)=\int_0^{\pi/2}\operatorname{Re}\bigl(W(x)^{-\alpha}\bigr)\,dx.
\]
<p>All logarithms and powers use their principal branches. The original transcripts alternate between an exact evaluation and a later assertion that the expression only approximates a residue contribution. The following proof resolves that disagreement. <a class="cite" href="#ref-univ">[6]</a> <a class="cite" href="#ref-galois">[7]</a></p>
<div class="theorem"><div class="theorem-label">Proposition 1 · exact evaluation</div>
\[
\boxed{J(\alpha)=\frac{\pi}{2(\log2)^\alpha},\qquad 0<\alpha<1.}
\]
</div>
<p><strong>Proof.</strong> Define on the open unit disk</p>
\[
H(z)=\log2-\operatorname{Log}(1+z),\qquad F_\alpha(z)=H(z)^{-\alpha}.
\]
<p>Since \(|1+z|<2\), the real part of \(H\) is positive. Thus \(F_\alpha\) is holomorphic. Its circular mean equals \(F_\alpha(0)=(\log2)^{-\alpha}\). Near \(z=1\),</p>
\[
H(z)=\frac{1-z}{2}+O((1-z)^2).
\]
<p>For radial approach, the resulting boundary singularity is bounded by a constant times \(|\theta|^{-\alpha}\), which is integrable when \(\alpha<1\). Near \(z=-1\), the real part of \(H\) tends to positive infinity and the power tends to zero. Dominated convergence therefore passes the circular mean to the boundary. On the lower semicircle parameterized by \(z=e^{-2ix}\),</p>
\[
H(e^{-2ix})=-\log(\cos x)+ix=W(x).
\]
<p>Conjugate symmetry identifies the real half-interval integral with one quarter of the full angular integral. The result follows. This argument also makes clear why the arithmetic type of a base parameter cannot alter the answer.</p>
<h3>The endpoint carries a real boundary correction</h3>
<p>The formula is stated on its proper open parameter range. At \(\alpha=1\), the integral of the real part exists, while the complex integral itself diverges at the origin. Subtract the boundary pole:</p>
\[
R(z)=\frac1{H(z)}-\frac2{1-z}.
\]
<p>The expansion \(1/H(z)=2/(1-z)-1/2+O(1-z)\) makes \(R\) continuous at \(z=1\). It is also continuous at \(z=-1\), with value \(-1\). Hence its boundary mean is \(R(0)=1/\log2-2\). Since \(\operatorname{Re}[2/(1-e^{-2ix})]=1\),</p>
\[
J(1)=\frac{\pi}{2\log2}-\frac\pi2
=0.69538374411870028558\ldots,
\qquad
\lim_{\alpha\uparrow1}J(\alpha)=\frac{\pi}{2\log2}.
\]
<p>The difference is \(\pi/2\). Endpoint concentration explains why unspecialized quadrature can suggest a false failure of the interior identity. The supplied numerical check subtracts the lower-end singular term and uses a logarithmic variable for the opposite endpoint. Six interior values, including \(\alpha=0.99\), agree with the analytic formula in independent 80- and 100-digit calculations. These quadratures support the proof; they are not interval certificates.</p>
<h3>The quotient has an immediate consequence</h3>
<p>When \(\alpha=\beta^{-t}\), with \(\beta>1\) and \(t>0\), both this integral and the scalar map below depend only on \(\alpha\). The normalized integral is identically</p>
\[
\frac2\pi(\log2)^{\beta^{-t}}
\int_0^{\pi/2}\operatorname{Re}\bigl(W(x)^{-\beta^{-t}}\bigr)\,dx=1.
\]
<p>Choosing a Pisot or Salem value for \(\beta\) labels a curve in the original parameter plane; the conjugates of that number do not enter this scalar identity. Genuine arithmetic information requires an object that actually retains those conjugates.</p>
</section>

<section id="flip">
<div class="section-label">3 / A certified stability boundary</div>
<h2>One flip, with the branch on the correct side</h2>
<p>Let</p>
\[
L(x)=-\log(\cos x),\quad U(x)=x^2+L(x)^2,\quad
K_\alpha(x)=U(x)^{-\alpha/2},\qquad 0<x<\pi/2.
\]
<p>This is the modulus of the complex power, not its real part. With \(H_1=x+L\tan x\), its derivative is \(K_\alpha'=-\alpha H_1K_\alpha/U<0\). The map decreases from positive infinity to zero and therefore has a unique fixed point for every \(\alpha>0\). The whole interval is not invariant under the map; the conclusions below concern local fixed-point and cycle geometry.</p>
<div class="theorem"><div class="theorem-label">Proposition 2 · interval-assisted uniqueness</div>
<p>There is exactly one positive parameter at which the fixed-point multiplier equals \(-1\). It lies in \((0,1)\), and</p>
\[
\begin{array}{rl}
\alpha_*&=0.74180451508789468891901626577308272417\ldots,\\
x_*&=0.94285767998233843967338162657360719637\ldots.
\end{array}
\]
<p>The fixed point is locally attracting below \(\alpha_*\) and repelling above it.</p>
</div>
<p><strong>Proof and certificate.</strong> Let \(x_0\) solve \(U(x_0)=1\). Every positive-parameter fixed point lies in \((x_0,1)\), where</p>
\[
\alpha(x)=-\frac{2\log x}{\log U(x)}
\]
<p>decreases strictly from infinity to zero. The flip equation reduces to</p>
\[
G(x)=U\log U+2xH_1\log x=0.
\]
<p>Both terms are negative on \((0,x_0]\), and \(G\) is positive on \([1,\pi/2)\). The certificate proves \(U(0.887)<1\), then covers \([0.887,1]\) by 1,130 exact rational cells of width \(10^{-4}\). Outward-rounded Arb arithmetic at 384 bits proves \(G'>4.66\) on every cell. Strict opposite signs at the two exact decimal bracket endpoints enclose the unique root. All endpoints and interval outputs are retained in <code>pisot-scalar-certificate.json</code>.</p>
<p>The later transcript already had the corrected root digits and a correct positive cubic coefficient of the second iterate. Its real branch formula nevertheless had the wrong sign. Current PerfectJet correctly limited its implementation to floating replay; the new certificate closes the uniqueness question for the declared kernel. <a class="cite" href="#ref-galois">[7]</a> <a class="cite" href="#ref-scalar">[4]</a></p>
<h3>The local two-cycle is subcritical</h3>
<p>At the critical point define</p>
\[
c_1=-\mu'(\alpha_*)=1.31627436766051292677\ldots,
\qquad
\sigma_2=\frac{(K_{\alpha_*}\circ K_{\alpha_*})'''(x_*)}{6}
=0.89327141474094919479\ldots.
\]
<p>The chain rule gives \(\sigma_2=-K'''/3-(K'')^2/2\). Both \(c_1\) and \(\sigma_2\) are enclosed strictly above zero. Centering at the moving fixed point and writing \(\delta=\alpha-\alpha_*\),</p>
\[
K_\alpha^{\circ2}(x_{\rm fp}+y)-x_{\rm fp}-y
=2c_1\delta y+\sigma_2y^3
+O(\delta^2|y|+|\delta|y^2+|y|^4).
\]
<p>The nonzero branches satisfy the leading balance</p>
\[
\boxed{y^2\sim-\frac{2c_1}{\sigma_2}(\alpha-\alpha_*).}
\]
<p>They are real below the threshold. In the declared state coordinate,</p>
\[
x_\pm-x_{\rm fp}
=\pm1.71670823984696389692\ldots\sqrt{\alpha_*-\alpha}
+O(\alpha_*-\alpha).
\]
<p>Their two-step multiplier is \(1-4c_1\delta+o(|\delta|)>1\), so the cycle is unstable. At \(\alpha=\alpha_*-10^{-8}\), a separate high-precision solve finds points approximately 0.9426860188997573 and 0.9430293605426657, with multiplier 1.0000000526509776. The interval signs establish the local type; that explicit cycle is a floating-point cross-check.</p>
<p>No transcendence claim is needed. The draft inference that every nonzero real \(z\) is algebraically independent of \(e^z\) fails already at \(z=\log2\). The exact identity \(e^z=2\) supplies a polynomial relation. Removing that inference leaves a strong and fully specified analytic result.</p>
</section>

<section id="psi">
<div class="section-label">4 / The precise content of stability equivalence</div>
<h2>A ratio profile determines a family up to parameter scale</h2>
<p>The PSG synthesis idea survives with a corrected sign and domain. On a connected interval \(I\subset(0,1)\), take a positive smooth potential \(\Phi\) with nonzero derivative, and define</p>
\[
K_\alpha(x)=e^{-\alpha\Phi(x)},\qquad
R_\Phi(x)=\frac{\Phi(x)}{x\Phi'(x)}.
\]
<p>At a fixed point, \(\alpha=-\log x/\Phi(x)\). Direct substitution gives</p>
\[
\boxed{\mu(x)=\frac{\log x}{R_\Phi(x)}.}
\]
<p>The minus sign in the recovered draft's numerator would reverse the orientation and must be corrected. <a class="cite" href="#ref-psg">[8]</a></p>
<div class="theorem"><div class="theorem-label">Proposition 3 · exact synthesis and equivalence</div>
<p>For a smooth prescribed profile \(\nu(x)<0\),</p>
\[
\Phi(x)=c\exp\left(\int_{x_{\rm ref}}^x
\frac{\nu(t)}{t\log t}\,dt\right),\qquad c>0,
\]
<p>realizes that fixed-point multiplier on the parameter image of \(I\). Moreover,</p>
\[
R_{\Phi_1}=R_{\Phi_2}
\quad\Longleftrightarrow\quad\Phi_2=c\Phi_1
\quad\Longrightarrow\quad K^{(2)}_\alpha=K^{(1)}_{c\alpha}.
\]
</div>
<p><strong>Proof.</strong> Differentiating the synthesis formula gives \(x\Phi'/\Phi=\nu/\log x\), hence \(\mu=\nu\). Along the fixed branch, \(\alpha'(x)=(\nu-1)/(x\Phi)<0\), so the parameterization is invertible on its image. Equality of the ratio functions gives equality of logarithmic derivatives of the two positive potentials; integration on the connected interval gives a positive constant ratio.</p>
<p>If a unique threshold exists, normalization by \(u=\alpha/\alpha_*\) removes that constant parameter scale. This is a precise equivalence result in a fixed state coordinate. Merely arranging equal threshold locations is weaker and does not identify two families.</p>
<h3>Equal thresholds can hide opposite bifurcations</h3>
<p>For \(\Phi=cx^r\), with \(c,r>0\), the principal Lambert function gives</p>
\[
\mu(\alpha)=-W_0(\alpha cr),\qquad
\alpha_* =\frac e{cr},\qquad
\mu(u)=-W_0(eu).
\]
<p>At \(x_*=e^{-1/r}\), write the centered map at the flip as \(-y+a_2y^2+a_3y^3+\cdots\). Its normal-form cubic coefficient is</p>
\[
a_3+a_2^2=\frac{r^2}{12x_*^2}>0.
\]
<p>For the logarithmic kernel the corresponding coefficient is \(-\sigma_2/2<0\). Choosing the amplitude \(c\) can align the threshold values while leaving these signs opposite. This gives an explicit reason to retain nonlinear local data when comparing stability laws.</p>
<p>The reserve \(\rho=1-|\mu|\) is a useful margin, but it is determined by \(\mu\). A numerical amplitude coefficient also depends on state normalization: under \(y_{\rm new}=s y\), its magnitude scales by \(|s|\), while the cubic coefficient scales by \(s^{-2}\). A defensible ψ description therefore specifies its permitted coordinate changes and the information it preserves.</p>
</section>

<section id="arithmetic">
<div class="section-label">5 / Arithmetic that genuinely remains</div>
<h2>Conjugate contraction belongs to a specified spectrum</h2>
<p>For a Pisot algebraic integer \(\beta=\beta_1>1\), with conjugates \(\beta_2,\ldots,\beta_d\), put \(r=\max_{j\ge2}|\beta_j|<1\). An integer companion matrix \(C\) gives the elementary exact mechanism</p>
\[
N_n=\operatorname{tr}(C^n)=\sum_{j=1}^d\beta_j^n\in\mathbb Z,
\qquad |\beta^n-N_n|\le(d-1)r^n.
\]
<p>The trace certifies exponentially close integer approximation. It concerns the conjugates in that irreducible polynomial. A different operator with the same leading eigenvalue can contain additional expanding modes.</p>
<h3>The recovered six-state graph makes this distinction explicit</h3>
<p>The displayed triskelion matrix is the adjacency matrix of a triangle with one leaf on each vertex. Reordering the three core vertices and their three leaves gives</p>
\[
A\sim\begin{pmatrix}J_3-I_3&I_3\\ I_3&0\end{pmatrix}.
\]
<p>Separate the constant vector of \(\mathbb R^3\) from its two-dimensional orthogonal complement. An orthogonal change of basis gives</p>
\[
A\cong
\begin{pmatrix}2&1\\1&0\end{pmatrix}
\oplus\begin{pmatrix}-1&1\\1&0\end{pmatrix}
\oplus\begin{pmatrix}-1&1\\1&0\end{pmatrix}.
\]
<p>Consequently,</p>
\[
\det(xI-A)=(x^2-2x-1)(x^2+x-1)^2.
\]
<p>The silver eigenvalue \(1+\sqrt2\) is exact. The omitted blocks also contain \(-\varphi\), twice, where \(\varphi=(1+\sqrt5)/2>1\). The source's displayed matrix and this complete factorization supply a useful finite example without requiring its proposed global tiling interpretation. <a class="cite" href="#ref-tri">[9]</a></p>
<p>Let \(P\) project onto vectors constant on the core and constant on the leaves. Since \(P\) commutes with \(A\), for any real initial vector \(b\) and observable \(c\),</p>
\[
\left|c^TA^nb-c^TPA^nPb\right|
\le\varphi^n\|(I-P)c\|_2\|(I-P)b\|_2.
\]
<p>If either vector lies in the retained subspace, the error is exactly zero. In general the omitted component grows absolutely, although it shrinks relative to the dominant scale at rate \((\varphi/(1+\sqrt2))^n\). Exact symmetry reduction and asymptotic dominance answer different questions.</p>
<p>The directed-edge nonbacktracking calculation also closes exactly:</p>
\[
\det(xI-B)=x^6(x^3-1)^2,\qquad
\det(I-zB)^{-1}=(1-z^3)^{-2},\qquad B^5=B^2.
\]
<p>For this matrix, \(\mathbf1^TB^n\mathbf1=24\) for every \(n\ge2\). Its fixed-length counts are bounded and eventually periodic. The corrected finite result replaces the draft's inconsistent zero multiplicity and linear-growth interpretation.</p>
<h3>The early rank example cannot support a flavor necessity</h3>
<p>The earlier Pisot–Delzant text's displayed weighted-translation matrix has determinant</p>
\[
\det\begin{pmatrix}1.17&0.24&0.11\\0.64&1.21&0.045\\0.018&0.015&0.96\end{pmatrix}
=\frac{24193617}{20000000}\ne0.
\]
<p>Its exact rank is three, rather than the claimed two. That calculation prevents the example from supporting the proposed rank-two flavor explanation. The finite graph reduction above supplies a valid and more useful comparison instead. <a class="cite" href="#ref-delzant">[10]</a></p>
</section>

<section id="physics">
<div class="section-label">6 / From reduced states to physical coefficients</div>
<h2>The later flavor work already tests closure under loops</h2>
<p>The periodic-table construction uses \(Q_4=I-\mathbf1\mathbf1^T/4\). Its zero-sum condition and rank at most three follow from that definition. The empirical question concerns response and residual structure after projection. The useful bridge to the other projects is therefore a closure test: does the retained state determine the response that the calculation actually needs? <a class="cite" href="#ref-periodic">[11]</a></p>
<p>The October protected-flavor monograph applies a much more concrete test. Define</p>
\[
P(x)=x^8-7x^6+14x^4-8x^2+1,\qquad
Q(x)=-1+3x-x^3,\qquad V'=PQ,
\]
\[
h(x)=(4-x^2)V''(x)-xV'(x).
\]
<p>The declared scalar-loop counterterm produces a torque proportional to \((h^2)'\). Preserving the stationary algebraic family requires its remainder modulo \(P\) to vanish. Exact rational recomputation gives</p>
\[
\begin{array}{rl}
R(x)={}&4800x^7-4400x^6-30080x^5+24160x^4\\
&+43600x^3-31360x^2-6880x+5040,
\end{array}
\]
\[
\gcd(P,R)=1.
\]
<p>The supplied checker constructs rational Bézout polynomials \(A,B\) with \(AP+BR=1\). Thus the counterterm torque is nonzero at every root of \(P\). This is an exact obstruction for that scalar-only construction. It does not rule out models with additional fields. <a class="cite" href="#ref-b5">[12]</a></p>
<p>The same monograph subsequently reports a 61-quartic algebra with 1,891 coefficientwise product identities and a specified coupled one-loop evolution system. It also records a lower CP-conserving competitor to the nominated CP-breaking branch. Those later results materially advance the model analysis while restricting its physical interpretation. This synthesis freshly checks the polynomial obstruction above; it does not relabel the entire later calculation as newly verified.</p>
<h3>The mixed-mass benchmark gives an observable error criterion</h3>
<p>In the retained leading electroweak test, the reduced coefficient is the complex bilinear form</p>
\[
C=\lambda^TS\lambda,\qquad
\lambda_i=V_{is}^*V_{id},\qquad\mathbf1^T\lambda=0.
\]
<p>Unitarity allows exact restriction to the GIM plane:</p>
\[
Q_3=I-\frac13\mathbf1\mathbf1^T,\qquad
C=\lambda^TQ_3SQ_3\lambda.
\]
<p>For the published illustrative inputs \(x=(0,1/4000,4)\), the leading eigenmode retains 99.9999993226% of the squared Frobenius norm of the restricted kernel, yet discarding the other mode changes the full complex coefficient by 95.92296721%. This is a fixed-input mathematical benchmark, with electroweak prefactors, QCD, hadronic and long-distance factors outside its scope. The exact error estimate that matters is</p>
\[
|C-\widetilde C|
\le\|\lambda\|_2^2\|S-\widetilde S\|_2.
\]
<p>The small spectral direction can carry a large share of a particular observable. The graph example establishes the same principle in elementary exact algebra; the flavor coefficient tests it in a mass-dependent kernel. <a class="cite" href="#ref-gim">[13]</a></p>
<h3>The annulus extension has a concrete mass response</h3>
<p>For the crossed-box family, the existing bounded extension varies only the seventh squared mass:</p>
\[
m_1^2=\cdots=m_6^2=M,\qquad m_7^2=M\rho,
\qquad \left.\partial_\rho I\right|_{\rho=1}=M J_{64}.
\]
<p>The physical kinematic variables \(s,t,M\) are held fixed. The derivative is a dotted-propagator master already present in the equal-mass basis. At the regular anchor \((s,t)=(3M,-M)\), the second Symanzik polynomial obeys</p>
\[
\mathcal F_\rho=\mathcal F_1+M(\rho-1)a_7\mathcal U,
\qquad
\mathcal F_\rho\ge\frac{M\mathcal U}{8}
\quad\left(\frac78\le\rho\le\frac98\right).
\]
<p>This gives a controlled domain for the mass deformation. It does not by itself evaluate the unequal-mass integral or transfer the equal-mass rank and field-minimality statements. The recovered observability framework improves the benchmark specification: preserve the requested integral and its mass response, and control their errors separately. <a class="cite" href="#ref-annulus">[14]</a></p>
<p>For a retained differential system \(z'=Bz+r\), the defect relative to a closed model satisfies an exact variation-of-constants identity. With constant \(B\),</p>
\[
e(t)=e^{Bt}e(0)+\int_0^t e^{B(t-s)}r(s)\,ds.
\]
<p>For a chosen readout \(c^Tz\), apply \(c^T\) before bounding the error. With a varying connection, replace the exponential by its propagator. The sensitivity equation must also be retained when masses vary. This is a mathematical framework for assessing a reduction; the actual source terms, branches, and interval bounds still belong to the specific integral family.</p>
</section>

<section id="synthesis">
<div class="section-label">7 / One coherent contribution</div>
<h2>Preserve the answer; measure the cost of discarded information</h2>
<p>The common contribution can be stated precisely: <strong>identify an exact quotient where one exists, expose the failure of closure where it does not, and bound the effect on the requested observable.</strong> This is a shared mathematical question with different answers in different models.</p>
<p>The scalar Pisot reduction is complete because the original parameters enter through one exponent. The ratio-profile theorem says exactly when two stability potentials differ only by parameter scale. The finite graph admits an exact symmetry quotient for symmetric observations. The GIM coefficient requires its physically weighted small mode. The flavor counterterm produces an explicit nonzero polynomial obstruction. The annulus publication establishes which continued functions and extension directions a difficult physical period problem must retain.</p>
<p>These statements should be presented as distinct theorems and examples under that common question. The dimensions 1, 2, 3, 37 and 114 refer to different objects and categories; there is no legitimate operation that equates them simply because each describes a form of reduction. Likewise, the Asterion half-braid work contributes methods for exact continuation and branch conventions, while its KZ system retains its own mathematical identity. <a class="cite" href="#ref-half">[15]</a></p>
<p>The current unequal-mass milestone remains the appropriate physical focus. Its two linked tests are a known mixed-mass flavor kernel with a coefficient-level error budget, and one certified nonzero mass deformation of the crossed box anchored by \(J_{64}\). The additional recoveries strengthen the acceptance criteria: include parameter response, verify the operative branch, and distinguish exact reductions from approximations. They do not require adding a separate GUT, tiling, or arithmetic-classification project.</p>
<blockquote>The practical value is a way to decide which parts of a complicated calculation are essential to its answer. Exact structure removes genuine redundancy. A closure defect identifies missing information. An observable bound states what an approximation costs.</blockquote>
</section>

<section id="verification">
<div class="section-label">8 / Reproducibility and scope</div>
<h2>What was established in this reconciliation</h2>
<div class="table-wrap"><table><thead><tr><th>Result</th><th>Verification</th><th>Delivered evidence</th></tr></thead><tbody>
<tr><td>Logarithmic integral and endpoint</td><td>Analytic Cauchy-mean proof; 80/100-digit independent quadratures</td><td><code>recheck_integral_and_flavor.py</code> and two JSON reports</td></tr>
<tr><td>Unique scalar flip and local signs</td><td>384-bit Arb certificate over 1,130 rational cells; 80/120-digit cross-checks</td><td><code>pisot_scalar_check.py</code> and interval certificate</td></tr>
<tr><td>Finite graph and early rank example</td><td>Ten exact symbolic matrix checks</td><td><code>arithmetic_matrix_audit.py</code> and JSON results</td></tr>
<tr><td>Scalar-loop obstruction</td><td>Exact remainder, gcd, and Bézout identity</td><td>Included in the integral/flavor checker</td></tr>
<tr><td>Ratio-profile equivalence and synthesis</td><td>Displayed analytic proof by logarithmic differentiation</td><td>Proposition 3</td></tr>
<tr><td>Later releases and model results</td><td>Current source and selected mathematical passages inspected</td><td>Version-pinned references below</td></tr>
</tbody></table></div>
<p>The downloadable package contains this complete article, the three checkers, their generated evidence and installation instructions in one directory. The earlier annulus publication remains the authority for its completed results. The two-cycle numerical coordinates, quadrature differences and previous GIM computation are not relabelled as interval enclosures. The interval-assisted scalar proof and exact polynomial identities have their own clearly stated certification routes.</p>
</section>

<section id="references"><div class="section-label">Sources</div><h2>Versioned mathematical references</h2><ol class="references">{{REFERENCES}}</ol></section>
<footer>Quotients, closure, and physical observables · Complete mathematical synthesis and independently replayable checks · 3 November 2026</footer>
"""

CSS = r'''
:root{color-scheme:light;--ink:#15263a;--muted:#536476;--blue:#1e5576;--rule:#d7e0e7;--paper:#fff;--light:#f3f7fa;--gold:#a46e35}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#eaf0f4;color:var(--ink);font-family:Georgia,'Times New Roman',serif;font-size:18px;line-height:1.7}main{max-width:1060px;margin:36px auto;background:var(--paper);padding:70px 88px 48px;box-shadow:0 12px 60px #1730480d}h1,h2,h3,.eyebrow,.section-label,nav,table,.theorem-label,.summary-grid,footer{font-family:Arial,Helvetica,sans-serif}h1{font-size:58px;line-height:1.09;letter-spacing:-2px;margin:22px 0;color:#122d46}h2{font-size:32px;line-height:1.23;letter-spacing:-.7px;margin:10px 0 25px}h3{font-size:22px;line-height:1.35;margin:35px 0 12px}.eyebrow,.section-label{font-size:12px;letter-spacing:1.6px;text-transform:uppercase;font-weight:bold;color:var(--blue)}.subtitle{font-size:22px;line-height:1.4;color:var(--muted);max-width:720px}.lead{font-size:20px;line-height:1.7;margin:28px 0}.summary-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;border-top:3px solid var(--blue);padding:25px 0;margin-top:30px;font-size:14px;line-height:1.55}.summary-grid b{display:block;color:var(--blue);font-size:16px;margin-bottom:8px}.summary-grid span{display:block}nav{border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);display:grid;grid-template-columns:1fr 1fr;column-gap:28px;row-gap:7px;padding:22px 0;font-size:13px;line-height:1.6;margin:8px 0 54px}a{color:var(--blue);text-decoration-thickness:1px;text-underline-offset:3px}nav a{text-decoration:none}a:hover{text-decoration:underline}section{margin:0 0 56px;scroll-margin-top:24px}p{margin:16px 0}.section-label{padding-top:4px}.theorem{border-left:3px solid var(--blue);padding:18px 25px;background:var(--light);margin:25px 0}.theorem-label{font-weight:bold;font-size:14px;color:var(--blue);margin-bottom:12px}.theorem p:first-of-type{margin-top:6px}.eq{position:relative;padding:13px 4px;margin:20px 0;overflow-x:auto;max-width:100%;font-size:1.03em}math[display="block"]{margin:0;display:block;max-width:max-content;min-width:0}math[display="inline"]{font-size:1.04em}.eq math{margin-inline:auto}code{font-size:13px;font-family:Consolas,monospace;overflow-wrap:anywhere}.table-wrap{overflow-x:auto;margin:25px 0}table{width:100%;border-collapse:collapse;font-size:13.5px;line-height:1.5;text-align:left}th{background:#eaf1f6;color:var(--blue);font-weight:bold}th,td{padding:13px 12px;border-bottom:1px solid var(--rule);vertical-align:top}td:first-child{font-weight:bold;width:25%}.cite{font-size:12px;white-space:nowrap}blockquote{font-size:24px;line-height:1.5;margin:35px 0;padding:24px 0 24px 28px;border-left:3px solid var(--gold);color:#224760}.references{padding-left:24px;font-size:14px;line-height:1.55}.references li{margin:16px 0;padding-left:4px}.references small{display:block;color:var(--muted);font-size:13px;margin-top:4px}footer{font-size:11px;line-height:1.5;color:var(--muted);border-top:1px solid var(--rule);padding-top:24px;margin-top:40px}
@media(max-width:760px){body{font-size:17px}main{margin:0;padding:38px 22px;box-shadow:none}h1{font-size:39px;letter-spacing:-1.3px}h2{font-size:27px}.lead{font-size:18px}.subtitle{font-size:20px}.summary-grid{grid-template-columns:1fr;gap:18px}.summary-grid b{margin-bottom:4px}nav{grid-template-columns:1fr;row-gap:8px;margin-bottom:38px}.theorem{padding:16px 15px}.eq{font-size:16px}blockquote{font-size:21px;padding-left:18px}table{min-width:620px}section{margin-bottom:42px}}
@media print{@page{size:A4;margin:18mm 18mm 19mm}html{scroll-behavior:auto}body{background:white;font-size:10.5pt;line-height:1.5}main{max-width:none;margin:0;padding:0;box-shadow:none}h1{font-size:35pt}h2{font-size:20pt;break-after:avoid}h3{font-size:14pt;break-after:avoid}.subtitle{font-size:15pt}.lead{font-size:12pt}.summary-grid{font-size:9pt;gap:18px}nav{font-size:9pt;margin-bottom:24px}.eq{font-size:10.5pt;overflow:visible;break-inside:avoid}.theorem{break-inside:avoid}section{margin-bottom:28px}table{font-size:8.5pt}tr{break-inside:avoid}blockquote{font-size:14pt}a{text-decoration:none}.references{font-size:9pt}.references small{font-size:8pt}}
'''

def render_math(text):
    def display(m):
        return '<div class="eq">'+convert(m.group(1).strip(),display='block')+'</div>'
    def inline(m):
        return convert(m.group(1),display='inline')
    text=re.sub(r'\\\[(.*?)\\\]',display,text,flags=re.S)
    return re.sub(r'\\\((.*?)\\\)',inline,text,flags=re.S)

def main():
    references='\n'.join(f'<li id="ref-{key}"><a href="{escape(url,quote=True)}">{escape(title)}</a><small>{escape(note)}</small></li>' for key,title,note,url in SOURCES)
    body=render_math(BODY.replace('{{REFERENCES}}',references))
    document='<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Exact scalar reduction, a certified subcritical flip, observable closure, and the reconciliation of Pisot, PSG and flavor research."><title>Quotients, closure, and physical observables</title><style>'+CSS+'</style></head><body><main>'+body+'</main></body></html>'
    out=ROOT/'research-reconciliation.html'
    out.write_text(document,encoding='utf-8')
    print(out)

if __name__=='__main__':
    main()
