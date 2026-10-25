# The PerfectJet quadratic-completion interval 493–496 (AST-P036)

Scope of this report. The question is the one recorded in the PerfectJet
repository as discovery AST-D013 and programme item AST-P036
(`docs/ASTERION_EXTENSION.md` §6, `docs/ASTERION_BOUNDARY.md`,
`docs/ASTERION_CLOSURE_AUDIT.md` AST-P036, and
`src/perfectjet/resources/asterion_discoveries.json`). Everything below is
over **Q**, the repo's ground field. The bottom line is stated first:
**dimensions 493, 494 and 495 are not closed by this work.** What is
delivered is an exact verification of both bounds from the repo's own data,
a sharper structural description of what any completion in 493–495 would
have to look like, two rigorous exclusions of natural construction routes,
and a verified reformulation of the remaining question as one explicit
finite linear-then-quadratic system whose exact size is computed. No
completion in dimension 493, 494 or 495 is constructed, and none is
excluded in general.

## 1. The reconstructed question

The boundary algebra is the $t=0$ fibre of the principal Rees family of
$E_8$. Under the principal $\mathfrak{sl}_2$ it decomposes into eight
pairwise nonisomorphic irreducible blocks $V_m$ for the $E_8$ exponents
$m \in \{1, 7, 11, 13, 17, 19, 23, 29\}$, with $\dim V_m = 2m+1$. The block
$V_1$ is the principal $\mathfrak{sl}_2$ itself (dimension 3), and the
remaining seven blocks span a nilpotent ideal
$\mathfrak{n} = \bigoplus_{m>1} V_m$ of dimension
$15+23+27+35+39+47+59 = 245$. The boundary algebra is
$\mathfrak{g}_0 = \mathfrak{sl}_2 \ltimes \mathfrak{n}$, of dimension
$248$, with $\mathfrak{n}$ nilpotent of class 4 (lower central dimensions
$245, 207, 145, 59, 0$), centre of $\mathfrak{n}$ equal to the
59-dimensional block $V_{29}$, $\mathfrak{g}_0$ perfect
($[\mathfrak{g}_0,\mathfrak{g}_0]=\mathfrak{g}_0$) and centreless. Only 16
of the 170 principal coupling channels survive at $t=0$: the eight
principal $\mathfrak{sl}_2$ actions and eight nonprincipal channels, all
with output exponent $a+b-1$ and coefficient $\pm\tfrac12$.

A **quadratic Lie algebra** is a finite-dimensional Lie algebra $D$ with a
nondegenerate symmetric bilinear form $B$ that is invariant,
$B([x,y],z)=B(x,[y,z])$. A **quadratic completion** of $\mathfrak{g}_0$ is
an injective Lie homomorphism $\mathfrak{g}_0 \hookrightarrow D$ into a
quadratic Lie algebra; identifying $\mathfrak{g}_0$ with its image, the
question is the minimum possible $\dim D$. The **restricted form** is
$B|_{\mathfrak{g}_0}$, and its **radical** is
$R = \{r \in \mathfrak{g}_0 : B(r, \mathfrak{g}_0) = 0\}$. Because
$B|_{\mathfrak{g}_0}$ is a $\mathfrak{g}_0$-invariant symmetric form, and
the repo proves the space of such forms on $\mathfrak{g}_0$ is
one-dimensional — spanned by the form $B_0$ that is the Killing form on
$V_1$ and zero on $\mathfrak{n}$ — every restricted form is $cB_0$ for a
single scalar $c$. Hence $\operatorname{rank} B|_{\mathfrak{g}_0} \le 3$
and $\dim R \ge 245$ in *every* completion, with equality cases analysed
in §3. The canonical **cotangent double**
$T^*\mathfrak{g}_0 = \mathfrak{g}_0 \ltimes \mathfrak{g}_0^*$ with pairing
$\langle x+\alpha, y+\beta\rangle = \alpha(y)+\beta(x)$ is a completion of
dimension $496$ in which $\mathfrak{g}_0$ is isotropic. The problem
AST-P036 is to decide the minimum in $\{493, 494, 495, 496\}$.

Concretely, an embedding in dimension $493+e$ ($e = 0, 1, 2$) must satisfy:
$\dim D = 248 + k$ with $k = \dim D/\mathfrak{g}_0 = 245+e$; the map
$\varphi: R \to (D/\mathfrak{g}_0)^*$, $r \mapsto B(r, -)$, must be
injective; and the bracket and form must satisfy invariance and Jacobi on
all of $D$, not merely on $\mathfrak{g}_0$. Section 4 turns these into
explicit necessary conditions and §5 into an explicit algebraic system.

## 2. What was verified from the repo, exactly

The script `perfectjet_interval_analysis.py` (Part A) imports the repo's
own modules read-only and rechecks every numerical input of both bounds.
The block dimensions sum to $248$ with $\dim\mathfrak{n} = 245$; the
coupling table has exactly 170 nonzero channels, of which exactly 16 are
leading (valuation zero) at $t=0$, listed in the JSON output; no leading
channel has the form $(m, m, 1)$ with $m>1$, and indeed the $E_8$ channel
$(m,m,1)$ has Rees valuation $2(m-1) > 0$ for every $m>1$, which is exactly
the input that forces $[\,V_m, V_m\,]$ to have no $V_1$ component at the
boundary and hence forces every $V_m$ ($m>1$) into the radical of every
invariant form; the only nonprincipal self-bracket at the boundary is
$(7,7,13)$; the nonprincipal bracket outputs are $\{13,17,19,23,29\}$, so
$\mathfrak{n}/[\mathfrak{n},\mathfrak{n}]$ has spins $\{7,11\}$ and
dimension $38$, matching the repo's structure receipt; and the repo's own
`quadratic_completion_bound(248, 3)` returns lower bound $493$, cotangent
upper bound $496$, isotropic minimum $496$. Separately, the repo's full
`boundary_receipt(exhaustive=False)` was replayed end-to-end and passed
(see `boundary_receipt_replay.log`): this includes the cotangent double's
complete finite check — all $61{,}504$ ordered base pairs, $10{,}488$
coadjoint transpose entries, Gram matrix $\bigl(\begin{smallmatrix} 0 & I
\\ I & 0 \end{smallmatrix}\bigr)$, pairing rank $496$ — and the boundary
structure certificate (lower central series $245, 207, 145, 59, 0$;
centre of $\mathfrak{n}$ of dimension $59$; $\mathfrak{g}_0$ perfect;
centre of $\mathfrak{g}_0$ zero). The lower-bound argument itself is the
pure linear-algebra statement that $\varphi$ above is well defined
($B(R, \mathfrak{g}_0)=0$) and injective (if $B(r, D)=0$ then $r=0$ by
nondegeneracy), so $k \ge \dim R \ge 245$; Part C of the script exercises
exactly this mechanism over $\mathbf{F}_{101}$ on a small analogue
($\mathfrak{sl}_2 \ltimes \mathrm{Sym}^6$, dimension $10$, radical
dimension $7$, bound $17$ attained at the level of forms), which validates
the mechanism only and is **not** evidence about $\mathfrak{g}_0$.

## 3. A sharper case split: any completion in 493–495 has restricted radical exactly $\mathfrak{n}$

Since $B|_{\mathfrak{g}_0} = cB_0$, there are only two cases. If $c = 0$
the restricted form vanishes, $R = \mathfrak{g}_0$, injectivity of
$\varphi$ gives $k \ge 248$, and $\dim D \ge 496$; this is the isotropic
case, where the cotangent double is already known to be optimal. If
$c \ne 0$ then $\operatorname{rank} B|_{\mathfrak{g}_0} = 3$ and
$R = \mathfrak{n}$ exactly. Consequently **every completion of dimension
$493$, $494$ or $495$ has $c \ne 0$, restricted radical exactly
$\mathfrak{n}$, and $\varphi: \mathfrak{n} \to (D/\mathfrak{g}_0)^*$
injective with cokernel of dimension $e = 0, 1, 2$ respectively.** The
interval problem is therefore entirely a question about non-isotropic
embeddings whose restricted form is a nonzero multiple of the boundary
form $B_0$; no isotropic or partially degenerate variant can slip into
the gap.

Write $E = \mathfrak{g}_0^\perp \subseteq D$. A dimension count that is
easy to get wrong is worth recording: the map $D \to \mathfrak{g}_0^*$,
$d \mapsto B(d, -)|_{\mathfrak{g}_0}$, is surjective (extend a functional
on $\mathfrak{g}_0$ to $D$ and use that $B$ identifies $D \cong D^*$), so
$\dim E = k$, not $k + 245$. One has $R = \mathfrak{g}_0 \cap E$,
$E^\perp = \mathfrak{g}_0$, $[ \mathfrak{g}_0, E ] \subseteq E$ (adjoint
invariance of $B$), and $B$ induces a nondegenerate form on the quotient
$E/R$, because the radical of $B|_E$ is $E \cap E^\perp = R$. The form $B$
also gives $\mathfrak{g}_0$-module isomorphisms $D/\mathfrak{g}_0 \cong E^*$
and the equivariant injection $\varphi$ identifies $\mathfrak{n}$ with a
submodule of $(D/\mathfrak{g}_0)^* \cong E$; precisely, there are exact
sequences of $\mathfrak{g}_0$-modules
$0 \to \mathfrak{n} \to E \to E/R \to 0$ and
$0 \to E/R \to D/\mathfrak{g}_0 \to \mathfrak{n}^* \to 0$, where the second
comes from dualising and from $\mathfrak{n}^\perp = \mathfrak{g}_0 + E$.

The new structural restriction is that **$\mathfrak{g}_0$ acts trivially
on $E/R$ whenever $e \le 2$**. Indeed $E/R$ carries the nondegenerate
$\mathfrak{g}_0$-invariant symmetric form just described, so the action is
a homomorphism $\rho: \mathfrak{g}_0 \to \mathfrak{so}(E/R)$. For $e = 1$
invariance alone gives $2\rho(x) = 0$, hence $\rho = 0$; for $e = 2$,
$\mathfrak{so}$ of a nondegenerate symmetric form in dimension 2 is
one-dimensional, hence abelian, and $\mathfrak{g}_0$ is perfect, so
$\rho$ factors through the abelianisation of $\mathfrak{g}_0$, which is
zero. (The argument genuinely stops at $e = 2$: in dimension 3,
$\mathfrak{so}(3)$ is simple and a perfect algebra can act nontrivially.)
Equivalently, $[\mathfrak{g}_0, E] \subseteq \mathfrak{n}$ in any
completion of dimension $493$–$495$, and the subspace
$\mathfrak{g}_0 + E$ (dimension $248 + e$) is normalised by
$\mathfrak{g}_0$ with trivial induced action on the quotient
$(\mathfrak{g}_0 + E)/\mathfrak{g}_0$. In the extremal case $e = 0$
(dimension $493$) the statement sharpens to a clean characterisation:
$E = \mathfrak{n}$, i.e. $\mathfrak{g}_0^\perp = \mathfrak{n}$ and
$\mathfrak{n}^\perp = \mathfrak{g}_0$ — the two algebras are mutual
orthogonal complements — and $D/\mathfrak{g}_0 \cong \mathfrak{n}^*$ as
$\mathfrak{g}_0$-modules. These are necessary conditions only; nothing in
this section produces a contradiction, and §5 explains exactly where the
remaining freedom lives.

## 4. Two natural routes to 493–495 are excluded

First, no completion in the gap is hiding inside the cotangent double. If
$\mathfrak{g}_0 \subseteq D' \subseteq T^*\mathfrak{g}_0$ and the
restricted cotangent form on $D'$ were nondegenerate, writing
$D' = \mathfrak{g}_0 \oplus V$ with $V \subseteq \mathfrak{g}_0^*$ of
dimension $j$, the Gram matrix has the form
$\bigl(\begin{smallmatrix} 0 & A \\ A^{T} & 0 \end{smallmatrix}\bigr)$
because both halves of the cotangent double are isotropic, so its rank is
at most $2j$ while $\dim D' = 248 + j$; nondegeneracy forces $j \ge 248$,
i.e. $D' = T^*\mathfrak{g}_0$. Every proper intermediate subspace — in
particular every proper subalgebra between $\mathfrak{g}_0$ and its double
— carries a degenerate restricted form. This excludes subspaces of the
cotangent double only; a general completion need not embed there.

Second, the standard quadratic reduction of the cotangent double cannot
produce the gap either. For an isotropic ideal $I$ of a quadratic Lie
algebra, the inherited nondegenerate form lives on $I^\perp / I$, of
dimension $496 - 2\dim I$, which is even, so $493$ and $495$ are
impossible by this route. Dimension $494$ would require $\dim I = 1$, and
$T^*\mathfrak{g}_0$ has no one-dimensional ideals: it is perfect and
centreless, both consequences of the repo-verified facts
$[\mathfrak{g}_0,\mathfrak{g}_0] = \mathfrak{g}_0$ and
$Z(\mathfrak{g}_0) = 0$ (a central element $(x,\xi)$ of the double forces
$x \in Z(\mathfrak{g}_0)$ and $\xi$ vanishing on
$[\mathfrak{g}_0,\mathfrak{g}_0]$, hence $(x,\xi) = 0$; and
$[\mathfrak{g}_0, \mathfrak{g}_0^*] = \mathfrak{g}_0^*$ because its
annihilator in $\mathfrak{g}_0$ is $Z(\mathfrak{g}_0)$), while in any
perfect Lie algebra a one-dimensional ideal is central, since the action
gives a character vanishing on the derived algebra. The repo's own remark
that quotienting the double by the three dual principal directions does
not make the pairing descend is consistent with, and subsumed by, this
dimension-and-ideals argument. Again the exclusion is of this route, not
of $494$ in general.

## 5. Reformulation: an equivariant normal form and the exact remaining system

The remaining question is reduced here to a specific finite computation.
Let $D$ be a completion of dimension $493 + e$, $e \in \{0,1,2\}$, so
$c \ne 0$ by §3. The adjoint action makes $D$ a module over
$\mathfrak{s} = V_1 \cong \mathfrak{sl}_2$; by complete reducibility in
characteristic zero there is an $\mathfrak{s}$-stable complement $W$ of
$\mathfrak{g}_0$ in $D$. Since $B$ is $\mathfrak{s}$-invariant and
$\omega(x,y,z) := B([x,y],z)$ is a totally skew $\mathfrak{s}$-invariant
3-form (its invariance is part of Jacobi in $D$), all data can be taken
$\mathfrak{s}$-equivariant. The $\mathfrak{s}$-module structure is then
forced: $E \cong \mathfrak{n} \oplus \mathbf{1}^e$ as $\mathfrak{s}$-modules
(semisimplicity applied to $0 \to \mathfrak{n} \to E \to E/R \to 0$ with
$E/R$ trivial by §3), dualising gives $W \cong D/\mathfrak{g}_0 \cong
\mathfrak{n} \oplus \mathbf{1}^e$, and the form $B$ has the following
normal form, with all assertions being Schur's-lemma counts that the
script verifies dimensionally. After rescaling $B$, $c = 1$; the pairing
$B(\mathfrak{s}, W)$ vanishes identically, because $W$ contains no
$V_1$ summand; the pairing $A = B(\mathfrak{n}, W)$ is, block by block, a
scalar $a_m$ times the canonical identification $V_m \cong V_m^*$, and
every $a_m$ is nonzero by injectivity of $\varphi$ (the seven $a_m$ can
be gauged to $1$ by rescaling the blocks of $W$); and
$S = B(W, W)$ is a scalar $s_m$ times the unique invariant symmetric form
on each block $V_m$, plus an arbitrary symmetric form on the trivial
block $\mathbf{1}^e$ — $7 + e(e+1)/2$ parameters in all. Nondegeneracy of
the assembled $B$ is equivalent to $c \ne 0$ and $a_m \ne 0$ for all $m$,
for every value of $S$.

Given $B$, the bracket is equivalent to $\omega$: invariance is automatic
for a bracket defined by $B([x,y], -) = \omega(x,y,-)$ with $\omega$
totally skew, the condition $[\mathfrak{g}_0,\mathfrak{g}_0] =
[\ ,\ ]_{\mathfrak{g}_0}$ forces the components of $\omega$ on
$\Lambda^3\mathfrak{g}_0$ and on $\Lambda^2\mathfrak{g}_0 \wedge W$
completely (they are the values $B([\ ,\ ]_{\mathfrak{g}_0}, -)$), and
Jacobi is the only remaining condition. The free data are therefore
exactly the $\mathfrak{s}$-invariant components $\omega_2$ on
$\mathfrak{g}_0 \wedge \Lambda^2 W$ and $\omega_3$ on $\Lambda^3 W$,
together with $S$. Part B of the script computes their dimensions exactly
by Clebsch–Gordan and weight-multiset arithmetic (all dimension checks,
e.g. $\dim \Lambda^2\mathfrak{n} = \binom{245}{2}$ and
$\dim \Lambda^3\mathfrak{n} = \binom{245}{3}$, pass): $\omega_2$ has
$162$, $169$, $176$ free parameters for $e = 0, 1, 2$ (the increment of
$7$ per trivial line is the seven singlets of $\mathfrak{g}_0 \otimes
\mathfrak{n}$), $\omega_3$ has $68$ parameters for all three values of
$e$, and $S$ contributes $7$, $8$, $10$. **The total free parameter count
after gauge-fixing is $237$ ($e=0$), $245$ ($e=1$), $254$ ($e=2$), and a
completion in dimension $493+e$ exists if and only if the Jacobi system
in these parameters — quadratic, with coefficients built from
$\mathfrak{g}_0$'s bracket and Clebsch–Gordan data — has a rational
solution.** That is the verified reformulation.

Jacobi itself splits usefully, and one piece can be settled now. For
inputs $x, y \in \mathfrak{g}_0$ and $w \in W$, the components of the
Jacobiator $J(x,y,w)$ paired against $\mathfrak{g}_0$ vanish identically,
with no hypothesis on the unknowns: pairing against $z \in
\mathfrak{g}_0$ and using invariance gives
$B(J(x,y,w), z) = B(-[[x,y],z] - [y,[x,z]] + [x,[y,z]],\, w)$, and the
bracketed expression is zero by Jacobi inside $\mathfrak{g}_0$. The first
genuinely unknown-dependent piece is $J(x,y,w)$ paired against $W$,
which is **affine linear** in $(\omega_2, S)$ jointly (each bracket
$[\mathfrak{g}_0, W]$ has $\mathfrak{s}$- and $W$-components forced by
$\omega$ on $\Lambda^2\mathfrak{g}_0 \wedge W$, an $\mathfrak{n}$-component
affine in $(\omega_2, S)$ through $B^{-1}$, and the second bracket is then
linear in those components; $\omega_3$ does not occur). This linear
system is the first finite check: at $e = 0$ it has $162 + 7 = 169$
unknowns, and its target, the space
$\operatorname{Hom}_{\mathfrak{s}}(\Lambda^2\mathfrak{g}_0 \wedge W, W)$
of equivariant Jacobi components, has dimension $22{,}688$ (script,
Part B); the full ambient singlet counts for the remaining Jacobi types
are $45{,}789$ ($( \mathfrak{g}_0,\mathfrak{g}_0,W)$ against all of $D$),
$44{,}897$ ($( \mathfrak{g}_0,W,W)$) and $14{,}449$ ($(W,W,W)$) at $e=0$.
These are dimensions of the ambient equivariant component spaces — upper
bounds on the number of independent scalar equations — not assertions
that the equations are independent or inconsistent; the actual
coefficient matrices are explicit contractions of the repo's principal
basis data and have not been assembled here. Assembling the $e = 0$
linear system exactly over **Q** and computing its rank and consistency
is a finite, well-specified computation that would either exclude $493$
outright (if the affine system is inconsistent) or reduce $\omega_2$ to
an explicit affine subspace on which the remaining quadratic Jacobi
system in $(\omega_2, \omega_3, S)$ must then be solved or refuted. The
same programme applies verbatim at $e = 1, 2$.

## 6. What remains open

The unrestricted minimum is still in $\{493, 494, 495, 496\}$, exactly as
the repo states; this work narrows the *shape* of a possible example
(nonzero restricted form, radical exactly $\mathfrak{n}$, trivial
$\mathfrak{g}_0$-action on $E/R$, equivariant normal form with the
parameter counts above) and excludes the two most natural constructions
(subspaces and isotropic reductions of the cotangent double), but it does
not construct a completion in $493$–$495$ and does not exclude one. The
single most concrete next step is the assembly and exact solution of the
affine-linear $(\mathfrak{g}_0,\mathfrak{g}_0,W)$-against-$W$ Jacobi
system described in §5, starting at $e = 0$; beyond it, the quadratic
system in $237$ parameters is finite but large, and would likely need the
block-by-block Clebsch–Gordan sparsity of the repo's principal basis to
be tractable. Any future claim of closure should be required to exhibit
either an explicit $(\omega_2, \omega_3, S)$ solution with a Jacobi
certificate, or an inconsistency certificate for the linear system (or
for a named subsystem), in the same exact style as the repo's existing
receipts.

Files: `perfectjet_interval_analysis.py` (portable, standard library
only, reads the repo read-only; run from this directory it defaults to
the repository root, or pass `--repo`), `perfectjet_interval_results.json`
(machine-readable output of all three parts), `run_log.txt`,
`boundary_receipt_replay.log`. These files are committed on the branch
`muse/asterion-completion-partial`, as new files under
`independent_checks/asterion_completion/`, for review by pull request.
No existing repository file is changed.
