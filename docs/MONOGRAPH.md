# PerfectJet — Representations, Arithmetic, and Closure

Version 0.12.0 · 14 October 2026

A master synthesis of the two archival passes and both enhancement programs. The repository distinguishes mathematical identities, executable exact checks, numerical evidence, historical reports, and proposals. It imports neither a complete upstream solver nor new Lean proofs.

## Contents

- [01_purpose_and_historical_audit](chapters/01_purpose_and_historical_audit.md)
- [02_arithmetic_geometry](chapters/02_arithmetic_geometry.md)
- [03_pell_orbits_and_transport](chapters/03_pell_orbits_and_transport.md)
- [04_descent_saturation_and_integer_lattices](chapters/04_descent_saturation_and_integer_lattices.md)
- [05_exact_populations_and_navigation](chapters/05_exact_populations_and_navigation.md)
- [06_series_hankel_and_weighted_quotients](chapters/06_series_hankel_and_weighted_quotients.md)
- [07_semantics_and_observability](chapters/07_semantics_and_observability.md)
- [08_feature_closure_error_and_decisions](chapters/08_feature_closure_error_and_decisions.md)
- [09_energy_IMP_and_numerical_structure](chapters/09_energy_IMP_and_numerical_structure.md)
- [10_PSG_scalar_and_coefficient_geometry](chapters/10_PSG_scalar_and_coefficient_geometry.md)
- [11_jets_Schroeder_and_obstruction](chapters/11_jets_Schroeder_and_obstruction.md)
- [12_collision_zeta_and_finite_parts](chapters/12_collision_zeta_and_finite_parts.md)
- [13_conductors_representation_and_fault_graphs](chapters/13_conductors_representation_and_fault_graphs.md)
- [14_shadow_core_and_regulators](chapters/14_shadow_core_and_regulators.md)
- [15_Weyl_exactness_and_partner_geometry](chapters/15_Weyl_exactness_and_partner_geometry.md)
- [16_deformation_moduli_and_codes](chapters/16_deformation_moduli_and_codes.md)
- [17_prefix_arithmetic_and_machine_semantics](chapters/17_prefix_arithmetic_and_machine_semantics.md)
- [18_mathematical_physics_and_protection](chapters/18_mathematical_physics_and_protection.md)
- [19_WIND_and_environmental_observability](chapters/19_WIND_and_environmental_observability.md)
- [20_Finsler_thermal_and_empirical_decisions](chapters/20_Finsler_thermal_and_empirical_decisions.md)
- [21_closure_stress_geometry_games_and_integrations](chapters/21_closure_stress_geometry_games_and_integrations.md)
- [22_master_enhancement_architecture](chapters/22_master_enhancement_architecture.md)
- [23_status_corrections_and_frontiers](chapters/23_status_corrections_and_frontiers.md)
- [24_mathematical_proofs](chapters/24_mathematical_proofs.md)
- [25_historical_results_and_extended_leads](chapters/25_historical_results_and_extended_leads.md)
- [26_nfl_motor_transfer](chapters/26_nfl_motor_transfer.md)
- [27_nfl_math_bridges](chapters/27_nfl_math_bridges.md)

---

# Purpose and historical audit

PerfectJet is the master repository for the mathematical program assembled in the October 14, 2026 conversation. It preserves the first categorized audit, equation-mining pass, first enhancement program, second archival pass, and second enhancement program. It supplies executable exact kernels where the present evidence supports them, and records the remaining work without silently converting proposals into theorems.

The strongest historical pattern is arithmetic and operator structure at the boundary between a sufficient representation and a failed representation. Computational arithmetic geometry is the strongest traditional subject. Spectral structure, effective dimension, exact populations, observability, and closure make the broader program. This assessment is an interpretation of the recovered requests and discussions, not an objective numerical ranking of interests.

The chronology reaches SYMMETRON in February 2025; MMHW in May; Harsh-Lattice, crystalline receipts, and master-program discussions in August; tau-Crystal in September; IMP, MEF, Arithmetic Shadow, subdivision and Pisot work in November; Finsler escape and transformer studies in December; thermal spectra in January 2026; prefix arithmetic in February; PSG jets and walls in March-April; PhaseNet, conductors, collision zeta, fault graphs, closure stress, and Weyl exactness in June; Shadow-Core and Morphonic in July; flux population work in August; WIND and PerfectPower in September; and DynaComp, allocation, games, BLAST, physics, and NFL in October. Dates identify recovered activity, not project inception.

The complete equation registry is machine-readable in `data/equations.json`. The topic census is in `data/topics.json`. Every archival extract has a source entry and byte hash in `archive/SOURCES.json`. Hashes identify these extracted/reconstructed bytes; they do not pretend to hash inaccessible original DOCX/PDF packages.

The repository intentionally preserves negative findings. A plausible reduction can fail on invariance; a norm-square condition can fall short of Selmer membership; an operator block can fail contraction; a finite-part equality can fail scaling; a movement feature can fail held-out prediction. A failure is retained as a mathematical object that directs the next step.


---

# Arithmetic geometry and perfect-power populations

The arithmetic entrance is $S(n)+k=m^d$, with integer polynomial $S$, integer inputs, and $d\ge2$. Define $A_{F,d}(N)=\#\{1\le n\le N:\exists m\in\mathbb Z,F(n)=m^d\}$. The existential definition counts inputs once even when signed square roots give two witnesses. The historical density uses $\limsup A(N)/N$. A polynomial identity $S+k=G^d$ with $G\in\mathbb Z[x]$ produces a hit at every input. Historical sparse classifications and multiplicity-based exponents are retained with their hypothesis gaps, rather than advertised for arbitrary sequences.

Exact transformations include $y^2+y=F(n)\iff(2y+1)^2=4F(n)+1$ and $y(y+1)/2=F(n)\iff(2y+1)^2=8F(n)+1$. For $ay^2+by+c=F(n)$, $a\ne0$, the square discriminant $b^2-4a(c-F(n))$ must be accompanied by the divisibility of $-b\pm\sqrt\Delta$ by $2a$. The integer chart for $x^2=y^3$ is $(t^3,t^2)$; for $2x^2=3y^3$ it is $(\pm18t^3,6t^2)$.

Morphonic expanded the arithmetic setting through localizations, real and p-adic completions, finite extensions, Galois actions, and adelic viewpoints. PerfectPower added concrete Mordell and Thue reductions, unit representatives, subgroup lattices, saturation, quartic coverings, source-bound lists, and polynomial pullbacks. Root splitting fields, Pell unit fields, polynomial discriminants, field discriminants, and nonmaximal orders must remain distinct.

The historical frontier moved from 316 Thue branches to 79 GL2 classes, later to a 457-curve census, with changing constructive witness counts. Those counts are dated historical snapshots, not current PerfectJet statistics. Global rank justification, saturation bounds, effective unit exponents, elliptic-logarithm enumeration, and integral-point completeness remain separate obligations. A finite list found by a backend is not automatically a kernel-checked complete solution set.

OEIS work was intended as a discovery/comparison layer using definitions, offsets, recurrences, references, and transformations. Prefix matches, transformed matches, proved identities, and rejected matches require different labels. Abelian heat/Dirichlet transforms, Bilu-Tichy, Runge, signed rank-two sieving, quartic covariants, and optimization over infinite families belong to the preserved frontier; their complete implementations are not imported into this repository.


---

# Pell dynamics and solution-carrying transport

A quadratic norm equation $x^2-Dy^2=N$ becomes a multiplicative orbit $x_j+y_j\sqrt D=\alpha\varepsilon^j$. If $\varepsilon=a+b\sqrt D$, the step is the integer matrix $\begin{pmatrix}a&Db\\b&a\end{pmatrix}$. For $m^2-2n^2=1$, $(n,m)\mapsto(3n+2m,4n+3m)$. The shifted problem $(x^2+7)/2=y^2$ is $x^2-2y^2=-7$. A complete family requires all seeds, signs, admissibility restrictions, and index ranges.

An admissibility automaton on an orbit can turn infinitude into a reachable-cycle question. A cycle of period $\pi$ with $g$ good positions contributes $g\log N/(\pi\log\varepsilon)+O(1)$ under the retained orbit-growth hypotheses. Thus arithmetic counting combines a growing eigenmode with a finite residue state. The exact identity $(1+\sqrt2)^6=99+70\sqrt2$ is a small illustration.

For $F(n)=(rn+s)^3+k$, $r\ne0$, a complete source list $L_k$ transports to $W=\{((t-s)/r,y):(t,y)\in L_k,r\mid t-s\}$. Integral-image restrictions are essential; omitting them turns the transported population into a different problem. The completeness contract is $m^2=F(n)\iff(n,m)\in W$, conditional on source completeness and preserved domains.

The recovered -23 leaves are $-u^3-3u^2v+6uv^2+4v^3=1$ and $-u^3-6u^2v+69uv^2+46v^3=1$, with $\theta^3-6\theta-3=0$. The D=72 leaf is $H=-3u^3+9uv^2-2v^3=\pm1$, with $\beta^3-27\beta-18=0$ and $\gamma=-3u-\beta v$, $N(\gamma)=9H$. Its reconstructed coordinates require $C=0$, $3\mid A$, $u=-A/3$, $v=-B$. Unit representations $\gamma=\zeta\alpha_j\varepsilon_1^{e_1}\varepsilon_2^{e_2}$ still need a complete representative inventory and an effective global exponent bound.

Question-dependent height $h_q(x)=h(q(x))$ can organize queries on residues or invariants, but cannot replace a completeness theorem for original objects. Adaptive local sieving changes the order of valid exclusions according to elimination-per-cost; it does not change the truth of any exclusion. Since 0.3.0, `sieve.py` implements this for $F(n)=m^d$. It keeps the residues n mod q for which F(n) is a d-th power residue mod q, combines moduli by CRT, and greedily chooses the modulus with the largest density drop per unit modulus. For the Pell7 input $2y^2-7=x^2$, moduli 4,3,5,11,17,25 leave density 224/4675. Integer roots are then tested on only93 of the first2000 inputs, and all nine hits are recovered. The tests confirm that every true hit survives every modulus and that a fixed modulus set excludes the same inputs in every order. A polynomial identity such as $(n+1)^2$ excludes nothing. The core transport principle is to carry the inverse map, the exceptional branches, and multiplicities with every reduction.

Since0.8.0 `quadratic.py` compiles k y2=a n2+b n+c over the integers and keeps the route back at every step. The transport X=2an+b, Y=y gives X2-4akY2=b2-4ac, with reconstruction n=(X-b)/2a when X=b mod2a. Each branch carries its own completeness status:
- a=0 is a congruence on y, so the hits are residue classes.
- Definite forms, square D and N0=0 have finitely many norm solutions, from a bounded box or divisor pairs.
- For the indefinite nonsquare case, Nagell's bounds give a representative of every class: N0>0 gives 0<=y<=y1 sqrt(N0/(2(x1+1))), and N0<0 gives 0<y<=y1 sqrt(-N0/(2(x1-1))). Seeds times powers of the fundamental unit are then all solutions.

Admissibility X=b mod2a is periodic along each orbit, so the compiled population counts hits below any bound and returns the j-th hit at remote indices with exact integers. Every returned n is replayed in the original equation. The tests compare 158 equations with brute force, including definite, linear and finite branches. Pell7, n2+7=2y2, has hits 1,5,11,31,65,181,...; its 1000th hit on an orbit has 766 digits and is replayed exactly. The square-triangular equation y2=8n2+8n+1 gives 0,2,14,84,492,....


---

# Descent, saturation, and integral lattices

For $y^2+a_1xy+a_3y=x^3+a_2x^2+a_4x+a_6$, define $b_2=a_1^2+4a_2$, $b_4=2a_4+a_1a_3$, $b_6=a_3^2+4a_6$. Completing the square gives $(2y+a_1x+a_3)^2=4x^3+b_2x^2+2b_4x+b_6$. The cubic $\psi_2$ has discriminant $16\Delta_E$. With the monic cubic normalization and its root $\theta$, $N(x-\theta)=((2y+a_1x+a_3)/2)^2$.

This norm-square bridge only supplies a necessary squareclass condition. Genuine 2-descent needs the S-unit and class-group spaces, norm restrictions, complete local Kummer images, and their global intersection. Sampled local signatures are not complete local images. The standard exact sequence $0\to E(\mathbb Q)/2E(\mathbb Q)\to\mathrm{Sel}_2\to\Sha[2]\to0$ explains why Selmer dimension is not automatically rational rank.

The historical anonymous model $y^2=x^3+2x^2-12x+16$ used $u^3+8u^2-192u+1024$, reported field discriminant -107, S={2,107}, six S-unit squareclass generators, a three-dimensional norm kernel, Selmer dimension two, and trivial Sha[2]. These are recorded upstream reports, not a descent engine implemented here.

The denominator-free kernel expression $K=\det(BB^T)I-B^T\operatorname{adj}(BB^T)B$ satisfies $BK=0$ and acts as multiplication by $\det(BB^T)$ on $\ker B$. This is rational-span information. Integral structure needs a lattice stage. In Smith form $UBV=D$ with unimodular transforms, $Bx=b$ requires $d_i\mid(Ub)_i$ and vanishing remaining coordinates. Integer nullspaces come from the free columns of V. Since 0.2.0 this stage is executable in `lattice.py`: Smith form with explicit unimodular transforms, integer solvability, an integer kernel basis, and the saturation index of a generated lattice.

Each failure carries a witness. If coordinate i fails, the rational row $y=U_i/d_i$ has $yB=V^{-1}_i$ integral and $yb=(Ub)_i/d_i$ non-integral, so no integer x can satisfy Bx=b. When $d_i=0$ the row $y=U_i$ gives $yB=0$ and $yb\ne0$, a failure already over Q. For a generator matrix G with invariant factors $d_1|\cdots|d_r$, the lattice has index $d_1\cdots d_r$ in its saturation; a row of $V^{-1}$ at the first $d_i>1$ lies in the rational span, is integral, and is not generated. Release0.3.0 adds row Hermite form $H=UB$, with an echelon shape, positive pivots and reduced entries above pivots. Two row lattices are equal exactly when their nonzero Hermite rows agree. The tests compare this with mutual membership decided by integer solvability. The example $\mathrm{diag}(2,3)x=(1,3)$ is solvable over Q and not over Z: the Smith form is diag(1,6) and the failing coordinate has residue3 modulo6.

Historical prime-specific saturation, bounded division, subgroup preimages, torsion-aware relation lattices, and isogeny witnesses must retain their scope. A proof for one finite box or one prime is not a global saturation bound. The master repo preserves these distinctions and pins upstream repositories for future integration without importing their formal proofs by implication.


---

# Exact populations and navigation

The selection polynomial $P(\mathbf z)=\prod_j(1+\prod_kz_k^{c_{jk}})$ encodes resource-use multiplicities. Summing coefficients with exponent vector bounded by capacities gives the feasible count when costs are nonnegative integers. Additional incompatibilities require additional factors or compatibility state. Adding a profit variable gives a distribution by objective, with Laurent exponents if profits may be negative.

The runnable residual-capacity engine preserves original project order. At prefix q, $C(q)=C(q0)+C(q1)$; terminal feasible assignments contribute one, infeasible ones zero. Lexicographic rank is $\sum_{i:x_i=1}C(x_{<i}0)$. Inverse rank follows the zero-branch population; uniform sampling draws an integer rank uniformly and reconstructs its original object. Optimization reports both value and tie count, including zero-cost and zero-profit multiplicities.

For general finite factors, $Z=\sum_x\prod_jf_j(x_{\mathrm{scope}_j})$. Independent components multiply; disjoint branches add. Auxiliary encodings preserve counts only when each original assignment has exactly one legal auxiliary extension. Weighted symmetry compression must preserve original multiplicity, not merely representatives.

The Petersen 50-project historical result is 702,508,860,122,761 feasible selections, objective16,537, one maximizer. The retained report used176 terminal partitions,437,533,492 visits and189,856,527 setup cells, with construction around362 seconds. Later retrieval reports independent decision-diagram reproduction, including all176 leaves and conditional counts16,777,216,512,16,095,745; a separate historical report gives5.3seconds and about518MiB. These workload/version-dependent figures are not new PerfectJet benchmarks. Original costs and the full retained DAG are not in this release, so this repo does not claim to replay that instance.

Exact counting also includes distinct outputs versus inputs, collision populations, CRT intervals, restricted-digit sums, monomial degrees, nonlinear sequence residues, generating functions, and integer calibration. The generic completion engine is implemented; these broader upstream adapters are indexed rather than falsely presented as already integrated.

Since0.10.0 the selection population explains itself. `attribution` counts, for each capacity constraint, the selections that it alone eliminates. That is the population with the constraint dropped, minus the feasible population; the unconstrained population is 2^n. `inclusion_profile` gives, for each project, the exact share of feasible selections and of optimal selections that contain it. It fixes the project and counts the residual population, so ties are counted in the original objects. Both are compared with exhaustive enumeration in the tests.


---

# Series, predictive state, and weighted quotients

Let $A_c$ encode finite transitions of positive integer cost c. With initial vector s and accepting map H, $\mathcal G(z)=H(I-\sum_cz^cA_c)^{-1}s$ sums all histories by cost. The formal inverse expands in operator powers because the transition series has zero constant term. Unit costs give $H(I-zA)^{-1}s$. The linear-system response series $C(I-zA)^{-1}B$ has coefficients $CA^kB$. The algebra is shared; coefficient meaning and admissible weights differ.

Initialization matters. $1/(1-z-z^2)$ gives Fibonacci-type populations, while $z/(1-z)$ starts0,1,1,... . A zero initial sample can increase realization size. Word-indexed Hankel data $\mathcal H_{u,v}=f(uv)$ encode predictive distinctions. Over a field, finite rank corresponds to a finite linear representation $f(w)=\alpha^TA_{a_1}\cdots A_{a_\ell}\beta$, with minimal dimension equal to Hankel rank. A field-minimal model can have signed coordinates; it need not be a probabilistic model or quotient of actual states.

For column-state transitions, an aggregation R must satisfy $RA=\bar AR$. Its block condition says each source in a block has the same total outgoing weight into each destination block. Initial weights aggregate as $\bar s=Rs$; accepting outputs require $H=\bar HR$. Then $HA^ts=\bar H\bar A^t\bar s$. Coefficientwise identities $RA_c=\bar A_cR$ preserve the cost series. Python exact matrix replay is supplied. Since 0.2.0, `coarsest_lumping` discovers the aggregation: starting from the partition by output columns, it splits blocks by their vectors of block-totals until stable. Every valid exact lumping refines the result, which is therefore the coarsest; the tests confirm this by enumerating all set partitions of small state spaces.

The first enhancement program proposed deriving state from Hankel distinctions, refining it when a new question adds an independent row/column, preserving event order with separate action matrices, and stacking multiple output Hankel blocks. Numerical Hankel rank requires held-out continuation tests and tolerance sensitivity. Since 0.2.0 the exact single-output case is executable in `realization.py`. With prefixes and suffixes up to length k, choose prefixes $P_0$ and suffixes $S_0$ whose Hankel block M is invertible. The state after prefix p is the row $x_p=H[p,S_0]$; then $A_a=M^{-1}H_a[P_0,S_0]$, $\beta=M^{-1}f(P_0)$, and $\alpha=f(S_0)$. The construction reproduces f on every word $ps$ and $pas$ in the block. It cannot see beyond the block: $f(w)=[|w|=5]$ looks like zero through length3. Agreement on longer words is therefore a held-out check that returns the first disagreeing word. Since 0.3.0, multiple outputs use the stacked block $H_{u,(v,j)}=f_j(uv)$ with a matrix-valued $\beta$. The shared state can be larger than either output alone needs: for $(|w|,2^{|w|})$ on one letter, the separate ranks are2 and1 while the stacked rank is3. Numerical Hankel rank with tolerances remains a proposal.


---

# Semantics and target-relative observability

SOE starts with $\pi:I\to S$ and legal fibres $\pi^{-1}(s)\cap L$. An implementation may be selected afterward by cost. Future equivalence identifies states that yield identical behavior under every finite permitted action word. For partial actions, whether a word is defined is part of behavior. The executable finite Moore-machine quotient supplies shortest distinguishing words via pair BFS, checks observation and transition preservation, and returns the exact equivalence blocks. It is Python mathematics, not a newly imported Lean theorem.

The historical Lean result `SOESemantics.quotient_complete` and324 two-state examples are documented upstream. The specialized generator used Fin2 and saved witnesses; general Python refinement was tested rather than universally formally verified. Historical adaptive diagnosis required two probes versus three in every fixed schedule for a retained example. The game bridge reported14->7 and68->34 phase/symbolic models; those are declared abstractions, not complete original games.

For linear dynamics, the observable row space is $\mathrm{span}\{\mathrm{rows}(CA^k):k\ge0\}$. Its annihilator is $\bigcap_k\ker(CA^k)$. Exact target recovery is $\ker\mathcal O\subseteq\ker G\iff G=L\mathcal O$. The rational implementation returns a hidden vector with nonzero target response on failure. Delay observations add rows C,CA,...; nonlinear delay sufficiency needs separate assumptions.

For quadratic target $T=g^Tx+\tfrac12x^TQx$ on fibre $x_0+\mathrm{im}N$, symmetric Q, constancy is equivalent to $N^T(g+Qx_0)=0$ and $N^TQN=0$. Linear sensitivity and hidden curvature are different obstructions. New sensors repair exactly when $\ker(H_{new}N)\subseteq\ker(GN)$. Repeated copies of the same row may reduce noise without repairing the nullspace.

A representation is relative to its question family. Enlarging Q refines equivalence. Joint coordinates $(q_1,q_2)$ preserve both question families, after which redundancy can be removed. The proposed preservation profile records exact questions, bounded questions, error, domain, and cost. This is a mathematical interface, not a universal scalar compression score.


---

# Feature closure, quantified defects, and decisions

Exact polynomial-feature closure means each $p_i\circ F$ belongs to the rational span of retained features. Then $p(F(x))=Gp(x)$ and $p(F^t(x))=G^tp(x)$. Outputs must lie in the feature span to be reconstructed. The implementation solves rational coefficient systems and replays the identities. It reports an unclosed pullback instead of silently fitting it.

When $\psi\circ F=G\psi+r$, residual structure can supply missing features. If $r=B\chi$ and $\chi\circ F=C\psi+D\chi$, the block state $[\psi;\chi]$ evolves by $[[G,B],[C,D]]$. Missing monomials, lags, order interactions, and parameter terms suggest different repairs. Finite closure may not exist. This release does not promise that augmentation terminates.

For full $x'=Ax+Bu$ and reduced $z'=Gz+Hu$, set $e=x-Vz$, $R=AV-VG$, $S=B-VH$. Then $e'=Ae+Rz+Su$ and $e_t=A^te_0+\sum_{j<t}A^{t-1-j}(Rz_j+Su_j)$. Continuous-time Lyapunov uses $A^TP+PA\preceq-2\alpha P$; discrete time uses $A^TPA\preceq\gamma^2P$. Mixing these forms is rejected. In a contracting norm, error is bounded by a geometric convolution; a uniform defect delta gives $\gamma^t\|e_0\|+\delta(1-\gamma^t)/(1-\gamma)$.

For staged reconstructions, total error is at most $\epsilon_1+\|V_1\|\epsilon_2$, or $\epsilon_1+L_1\epsilon_2$ for a Lipschitz first map. Model error and roundoff should remain separate. Parameter sensitivity evolves as $S_{t+1}=D_xF S_t+D_\theta F$; trajectory accuracy does not imply correct parameter response.

An action is certified best when its lower objective bound exceeds all competing upper bounds. With common error epsilon, a gap above2epsilon suffices. Computation can concentrate on candidates whose intervals overlap the best lower bound. This turns model-error machinery into decision machinery; deterministic approximation bounds do not replace empirical uncertainty about sports or markets.

Historical DynaComp reports include256-state compile time37.6s->1.3s,58 tests at one stage, later210/229 tests,200-state heat->7 states with0.01 ceiling and5.89x runtime gain, break-even about222 batches of256 scenarios, and descriptor200->9 with0.003483 bound and4.50x gain. Other models were slower or uncertifiable. These are upstream dated workloads, not universal or freshly reproduced PerfectJet results.

Since0.5.0 `engine.py` runs the augmentation loop rather than describing it. `adaptive_closure` starts from the monomials of the requested outputs, pulls every feature back through F, and adds exactly the monomials of the residual support. On closure it replays $m(F(x))=\sum_jK_{mj}m_j(x)$ for every retained monomial and extracts the smallest pullback-closed space containing the outputs, span$\{C,CK,CK^2,\dots\}$, which can be smaller than the monomial space (y+12x2 is a one-dimensional eigenfunction of $(x,y)\mapsto(x/2,y/3+x^2)$). When a missing monomial has higher degree than every retained one, the failure is classified as degree growth and the loop stops instead of inflating the model; the residual support is returned.

`decisions.py` implements the stopping rule above. `certified_choice` returns the settled action or the overlapping contenders; `refine_until_settled` refines only the widest contender, and its receipt records the evaluations spent against uniform refinement. `defect_split` replays $e_{t+1}=Ae_t+(AV-VG)z_t+(B-VH)u_t$ exactly at every step and reports the evolution and input defects separately, together with the geometric bound in the infinity norm.

Every adapter of `engine.py` returns one report shape: question, representation, preserved questions, replayed identities, answer, obstruction, obligations, and the next calculation implicated by the obstruction. Adapters exist for polynomial dynamics, linear sensing, readouts of linear responses, integer systems, and transvectant partners.


---

# Energy diagnostics, IMP, and numerical structure

For $\dot u=Au+f$ and constant SPD mass matrix M, $E=\tfrac12u^TMu$, $S_M=(A^TM+MA)/2$, and $\dot E=u^TS_Mu+u^TMf$. Define $\lambda=-2u^TS_Mu/(u^TMu)$ and $\zeta=2u^TMf/(u^TMu)$. Then $d\log E/dt=-\lambda+\zeta$ and $\rho=1-\zeta/\lambda$ when lambda is nonzero. Positive source reduces net decay for positive lambda. This corrects the historical plus sign and missing factor2. Python exact checks validate dimensions, positive definiteness, and the identity; rho is None at zero dial.

CRO/crystalline work estimated $\hat\alpha=-(\log E_k-\log E_{k-1})/\Delta t$, compared $|\hat\alpha-\alpha|$, and proposed compact128-byte manifests and40-byte receipts. Historical constants alpha=.0333996828 and beta=.6732050807568877 are retained as selected model constants, not proven universal values. The rank-one matrix $I+t11^T$ has determinant1+nt. Receipt hashes identify records, not the truth of physical claims.

IMP explicitly means Inertial Manifold Projector. Its SVD projector $P=QQ^T$ does not establish $M^k\to P$. An orthogonal rotation has all singular values1 and nonconvergent powers. A sufficient fixed-mode split is $M=P+T$, $P^2=P$, $PT=TP=0$, $\rho(T)<1$, which gives $M^k=P+T^k$. General retained dynamics requires $MQ=QG$, not fixed vectors. Invariant-space leakage $(I-P)AP$ indicates closure failure.

Historical Catmull-Clark11->2, transformer ranks6-7, diffusion65536->1024, errors around1e-14, and10-100x reductions were claims requiring source computation. The local valence6 block [[-7/48,3(1+i sqrt3)/32],[5(1-i sqrt3)/16,-9/8]] has characteristic $x^2+61x/48+3/64$. One root magnitude exceeds1; the block cannot supply a contraction claim without the true operator interpretation. The plastic/Pisot interpretation was removed from that specific block. More extensive motivic, holographic, fan-law, and global-refinement-period claims remain proposals or unsupported reports.


---

# PSG scalar balance and coefficient geometry

On0<x<pi/2, $L=-\log\cos x$, $U=x^2+L^2$, $K_\alpha=U^{-\alpha/2}$, $T=\tan x$, $H=x+LT$, $A=xH/(2U)$. Since $U'=2H$, $K_\alpha'=-\alpha HK_\alpha/U$. At a fixed point the multiplier is -2alpha A, so flip parameter is1/(2A). In L coordinates, $x=\arccos(e^{-L})$, $T=\sqrt{e^{2L}-1}$, and the scalar balance is $F=\log U+4A\log x=0$. Root replay gives L=.5319166892432992,x=.9428576799823384,A=.6740320257295228,alpha=.7418045150878947. It checks fixed residual and multiplier, but supplies no interval uniqueness or transcendence proof.

For v=2L, $a(v)=x(x+(v/2)T)/(2(x^2+v^2/4))$, $x=\arccos(e^{-v/2})$, $T=\sqrt{e^v-1}$. The archived differential-algebraic equation is $EF_1+F_0=0$, with E=e^v-1, $F_0=a(2a-1)(v+4-8a)^2$, and $F_1=(av-2a-2pv+1)(2av+4a-4pv-v-2)$, p=a'. This extracts E=-F0/F1 away from the exceptional branch.

The cleared field is $\widetilde X=D\partial_v+Dp\partial_a+N\partial_p$, $D=2av^2(2a-1)(v+4-8a)^2$. Its six listed factors are v,a,2a-1,v+4-8a and the two F1 factors. Darboux means $\widetilde X(H)=KH$. Listing and checking factors does not establish all-degree completeness. The source lacks full N and has a cofactor inconsistency: X(v)=D implies cofactor D/v, not D. Complete classification and algebraic-point exclusion need the missing global arguments.

The original26-term PSG source was reported to eliminate T using $T^2=Y^2-1$ into a100-term polynomial with even exponents U=x^2,Z=Y^2. Reconstruction T=-A/B needs the B=0 branch and integer-image conditions. Those actual26/100 coefficients were not recovered here; they remain explicitly missing rather than fabricated.

The sources mix numerical certification language with exact proofs, and one passage says A<1/2 while reporting A*=.674.... These contradictions are preserved in the archival extract and corrected in the canonical text. Neither a high-precision numerical root nor dense-intersection rhetoric establishes transcendence of alpha*.


---

# Jets, reflection, and model-specific obstruction

PSG's recovered normalized jets include A/A*=1+.3282804759delta+.0800766090delta^2+.0108819139delta^3+... and F/(L*F')=delta-.3793897467delta^2+.3008496421delta^3-.2807207864delta^4+... . They are root-centered normalized data, not an origin germ. Six coefficients cannot determine the actual seventh without a defining law. The quadratic-ODE prediction22.2074398750 was not an actual origin coefficient. Later reports of23.240 use a different stated context and do not erase the provenance issue.

The archive reports eighth-order jets,40 coefficients,Padé[20/20],a14-step preimage chain, and a fifth-order b5 effect on a seventh-order normalization. Reported b5 values .5604 versus .7771, normalized b7=-19.3142007715725, and offset -2.49298145474 with sensitivity11.5037 are historical claims. Full source and interval replay are needed. A negative squared Puiseux amplitude followed by a real-branch claim is rejected.

An invertible analytic coordinate satisfying Psi(f)=-Psi requires f^2=id. Conversely a centered involution with f'(0)=-1 has Psi=(x-f(x))/2 and Psi'(0)=1. Thus generic flip bifurcations cannot be advertised as exactly reflection-linearized. For f=-x+ax^2+bx^3+..., $f^2-x=-2(b+a^2)x^3+...$. The implementation computes finite composition defects exactly. Vanishing at a finite order does not establish an involution.

After recentering the parameter-dependent fixed point, a normal form $f_\nu=-(1+\nu)x+\kappa x^3+...$ has second-iterate leading equation $2\nu x-2\kappa x^3=0$, requiring x^2~nu/kappa>0 for a small real cycle. Signs follow the actual parameter convention.

For a specified Riccati model I'=a+bI+cI^2, Taylor coefficients obey $(n+1)i_{n+1}=a1_{n=0}+bi_n+c\sum_{j=0}^ni_ji_{n-j}$. The residual supplies a precise rejection test. Nonzero exact residual rejects this model; an interval residual excluding0 does the same. It is not a test of all algebraic germs or transcendence. MTB/GTT classifications and Feigenbaum depth profiles are archived exploratory classifications, not promoted to established mathematical universality in this release.


---

# Collision arithmetic, root-of-unity closure, and finite parts

The valuation kernel $\kappa(m,n)=\sum_pv_p(m)v_p(n)$ is symmetric and additive under multiplication. It vanishes exactly for coprime positive integers. kappa(72,108)=12. The divisor rank polynomial $R_n(q)=\prod_p(1+...+q^{v_p(n)})$ yields $F_{m,n}=R_mR_n-R_{mn}$ and at1 gives tau(m)tau(n)-tau(mn). For12,18 the36 divisor pairs map to16 product divisors; the surplus is20. The p3,p2 fibre profile is1,2,3,3,2,1.

The collision zeta $Z_t(s)=\sum_{m,n}e^{t\kappa(m,n)}(mn)^{-s}$ has Euler factors $\sum_{a,b}e^{tab}p^{-s(a+b)}$. For real t>0, the a=b=N terms fail to vanish, so it diverges. For t<=0 and Re(s)>1 it converges absolutely. At t->-infinity only coprime pairs survive, giving zeta(s)^2/zeta(2s) and H(1)->6/pi2. Reported H_t(1) at0,-.25,-.5,-1,-2,-4,-8 is1,.814101,.738157,.670474,.626911,.610278,.607970. Count asymptotics require original analytic hypotheses.

At zeta_L, exact residue splitting gives $L_L(x)=N_L(x)/(1-x^L)^2$, $N_L=\sum_{r,s<L}\zeta_L^{rs}x^{r+s}$. N(0)=1,N(1)=L,top coefficient zeta_L. For n=dL+r, a_n=dG_r+B_r, with complete and partial quadratic sums G,B. Hence a_{n+2L}-2a_{n+L}+a_n=0. The implementation checks direct coefficients and numerator convolution in exact cyclotomic quotient rings; it answers an index10^100 without iteration through prior indices. The archived blanket complete-Gauss coefficient claim is repaired by retaining partial blocks.

The higher-rank archive uses log Z=r log zeta(Ls)+sum a_m P(ms), a1=r zeta_L, and branch-stripped FP=zeta(L)^r product_p[N(1/p)e^{-a1/p}]. If the tail logarithm satisfies abs(r_p)<=C/p2 beyond a cutoff, omitted log tail<=C/P and multiplicative error<=exp(C/P)-1. Explicit C, finite zero factors, and logarithm branches are needed; no generic tail certificate is manufactured.

Negative collision suppression e^{-beta kappa} is not PSD: on{1,2} the determinant is e^{-beta}-1<0. A positive geometric kernel is exp(-beta norm(v(m)-v(n))2), factorizing into two norm weights times e^{2beta kappa}. The two serve different roles. Prime-product FP versus quantum D2 failed the retained low-height projection sweep; the separate conductor volume carries growth. Keep this negative finding.


---

# Conductors, representation structure, and weighted fault graphs

PhaseNet/Deformation-Conductor Networks organized UV=e^{2pi i theta}VU. With Ue_j=e_{j+1}, Ve_j=omega^j e_j, the actual relation is VU=omega UV. Sign/order conventions must be fixed. Rational theta=p/L supports finite conductor representations; irrational theta leads to A_theta and trace range Z+theta Z. Continued-fraction denominators form approximation levels, but are not automatically an inverse system without bonding maps. Bounded partial quotients imply q_{n+1}<=(A+1)q_n and chi=limsup log(q_{n+1})/log(q_n)=1. For j<=q_n, phase-coordinate error<=1/q_{n+1}.

Finite quadratic modules define b(x,y)=q(x+y)-q(x)-q(y), Sxy=|A|^-1/2 exp(-2pi i b), Txx=exp(2pi i q), with S2=C,(ST)3=xi C under the correct hypotheses. Weil commutant dimensions depend on the exact pair. Odd prime law a+1 and CRT multiplicativity were reported; dyadic2a-1 belongs to a different specified model than the cyclic pair with1,3,8,19,... . The model definition must precede any all-exponent statement.

For su2 level k, L=k+2, d_a=sin((a+1)pi/L)/sin(pi/L), D2=sum d_a2=L/(2sin2(pi/L))~L3/(2pi2). The simply-laced Weyl formula gives exponent rank+2positive-root-count=dim(g), reported3,8,15,28 for A1,A2,A3,D4. Nonsimply-laced finite-level normalizations remain distinct. A fusion wall should use monic integer polynomial U_{L-1}(X/2) in X=2cos(theta), not silently treat nonmonic U_m(x) as a monic integral relation.

DAT/DAU required both C_cond<C_Pauli and p_eff<p_th. Historical437 tests/74certificates and8x structural->about3.19x nominal net saving were model-level; device fidelity, heralding, feedforward, reset and noise gates remained essential. DBD solved a pointed sector with residuals2.9e-16/7.9e-16, while a672-target coupled component had residual about1.1 and0/48 recognitions: full spinor closure was open.

Weighted walks use Z_N(u)=sum_n c_n exp(n.u), gradient=E[n], Hessian=Cov(n)>=0 and abs(Z_N(u+i phi))<=Z_N(u). The archive reports4,133,166 length10 walks represented by66 type vectors. Histograms preserve type-dependent questions, not order-sensitive ones. Fault tails require justified native-graph counts and mu eta<1; the geometric tail is C(mu eta)^d/(1-mu eta). Square bounds cannot be transferred silently to triangular/hook graphs. Native extraction, assumptions and weights remain part of the result.


---

# Shadow-Core Lift and exact coefficient fields

The5_2 program distinguishes a conductor7 abelian shadow from a discriminant-23 nonabelian core. Recovered polynomials include alpha3-alpha2+1, the plastic beta3-beta-1, visible z3-2z2+3z-1, critical u3-4u2+5u-1 (each discriminant-23), and cyclic z3-2z2-z+1 (discriminant49). Equal discriminants do not establish field identity. Explicit transports do: u=1+alpha,beta=-1/alpha, with inverse alpha=u-1=-1/beta.

The canonical exact quotient ring is Q[u]/(u3-4u2+5u-1). This release computes h=(-2u2+3u-2)/(-u2+u), v=(6u-8)/(3u2-8u+5), proves denominators invertible in the ring, and replays h3+4h2-23h+23=0 and23v3+4v+200=0. These are preserved as field coordinates. Polynomial discriminants -1127=-23*72 and -571325888 are not automatically field discriminants.

The archive reports critical factorization (z-1)2(z3-4z2+5z-1), isolating a boundary branch from the cubic. It reports D(alpha)=.9427073627769277209... and3D=2.8281220883307831628..., with another embedding/avatar giving half the D value. These are selected-embedding regulator numbers; identification with geometric volume requires the actual oriented geometric data.

Corner P_ab=(1-z)^a-z^b scans reportedly found the visible cubic only at coprime(3,2) and hidden avatar at(5,1) through a<=300 under the specified search range, with smaller exact factors through a<=20. This is bounded evidence, not global isolation. The28-row9-field Theta atlas, Theta(5_2)=4/9, p-adic valuations3 and4, and ramified local Q23(sqrt(-23)) descriptions are retained reports requiring original source/certificates for promotion.

Bloch-Wigner conjugation D(conj z)=-D(z) means the unweighted sum over all embeddings cancels. Store one representative per conjugate pair as a regulator vector, then distinguish its squared norm from an oriented scalar c^T R. The first is conjugation-choice independent; the second needs coefficients from geometry. Zero at one embedding is not a zero regulator class. This repairs the archived positive all-embedding defect formula.

The proposed CoreLift pipeline is shadow->obstruction->legal receiving space->field-valued output. Abelian data are useful routing information but cannot be treated as a complete identity of nonabelian targets. Exact transports and embedding provenance are the enhancement, not a claim that every core extraction is implemented.


---

# Weyl exactness and partner-spectrum geometry

For monomials q^ap^b,q^cp^d, Poisson bracket is(ad-bc)q^{a+c-1}p^{b+d-1}. The normalized Moyal bracket is a finite sum over odd k<=min(a,d)+min(b,c), with coefficient (-1)^((k-1)/2)hbar^(k-1)S_k/(2^(k-1)k!), S_k=sum_r(-1)^r binomial(k,r)(a)_{k-r}(b)_r(c)_r(d)_{k-r}. Falling factorials make the arithmetic exact. It can be expressed as a terminating Hahn-type3F2 with careful denominator interpretation. Cubic q3,p3 yields9q2p2-3hbar2/2; quadratic q2,p2 is exact4qp.

Binary forms use unnormalized transvectants(f,g)_k=sum_i(-1)^i binomial(k,i)partial_x^{k-i}partial_y^i f times partial_x^i partial_y^{k-i}g. For sextic f only odd correction gates3 and5 remain. Exact partners need both gates zero; active partners additionally require nonzero first transvectant. Individual exact pairs do not overturn the full quantization no-go theorem.

For f_lambda=x6+lambda x3y3+y6, g8=xy(x6+y6-7lambda x3y3/20) has both correction gates zero for all lambda. Exact polynomial arithmetic checks it at four parameters; degree<=2 in lambda plus three distinct roots establishes the identities. Its Poisson bracket has leading6x12 and is nonzero. For h=xy(x3-y3), (f_lambda,h)_3=72(7lambda-40)(x4y+xy4), (f_lambda,h)_5=0. At lambda40/7, g8=(x3-y3)h. This is a precise ansatz obstruction and factorization, not an all-degree classification.

Define L_N:g->((f,g)_3,(f,g)_5), K_N=ker L_N, P_N:g->(f,g)_1. Active quotient A_N=K_N/(K_N intersect ker P_N) has dimension rank([L_N;P_N])-rank(L_N). The finite census for lambdas0,1,40/7,20,-20 and degrees3..12 separates trivial self-partners from nontrivial channels. At degree6 every retained family point has kernel1 but active0. At lambda40/7 degree5 has active1, absent at lambda1. Lambda0 has active2 in degree3 and1 in degree10; +/-20 has active1 in degree3. This finite result is recorded, not extrapolated to degree11 globally.

The archived squarefree quintic g=-xy(x-y)(x2-xy+y2), sextic f=(2x6-6x5y+5x4y2+5x2y4-6xy5+2y6)/2 passes exact gate replay with nonzero Poisson bracket. Normalized quintic elimination yields b6(b-1)6 times four quadratics(b2-3b+3)(b2-b+1)(b2+b+1)(3b2-3b+1). Archive orbit count was corrected3->1, but its supplied verifier uses numerical Mobius matching; exact orbit certificates are still preferable. R7/R9 modular patch evidence remains conjectural over Q. Incidence varieties I_N={(f,g):gates0} and symbolic minors are the correct next objects.

Since0.3.0 the one-parameter case is executable. `loci.py` computes the generic rank of a matrix over Q(lambda) and its exact drop locus, and `partner_loci` applies it to the gate matrices of f_lambda. The correction locus is lambda(lambda2-400) in degree3, lambda2-1600/49 in degree5, and lambda in degree10. It is lambda2+50 in degree4 and lambda2+5 in degree12, which have no rational points, and trivial in degrees6-9 and11. The joint matrix [L_N;P_N] has no drop locus in degrees3..12. The active dimension therefore jumps exactly at correction-locus points. The 7lambda-40 obstruction is rediscovered without being supplied, together with its mirror -40/7 under y->-y. The census parameters0,+/-20 and40/7 are the complete rational exceptional set in degrees3..12. Over Q, this replaces the finite census with a certificate for every lambda.

Since0.4.0 `parametric.py` handles several parameters. Comprehensive Gaussian elimination branches on each pivot, either nonzero or zero, and keeps each branch as V(S) minus V(N), with S saturated by every inequation. An exact Groebner basis decides whether the branch is empty and gives its Zariski closure. The leaves partition parameter space, over the algebraic closure, into cells of constant rank. Bareiss division by the previous pivot, when exact, keeps degrees small.

Applied to the two-parameter family x6+y6+a x3y3+b(x4y2+x2y4), whose slice b=0 is the C3 family, the method reproduces every one-parameter point on b=0. It also finds new rational exceptional points:
- (+/-16,-9), where f=(x-y)4(x2+4xy+y2) has a fourfold root, drops the correction rank in degrees5,6,7,9,10 and11.
- (0,3), where f=(x2+y2)3, drops the rank in degrees8,10 and12.
- (0,15)=(x2+y2)(x4+14x2y2+y4) and (0,-5)=(x2+y2)(x4-6x2y2+y4) are squarefree and still exceptional, at (0,15) in degrees3,8,10 and at (0,-5) in degrees4,8.

Degree3 has a whole drop curve of rank3: a4-16a2b2/3+256b4/81-2560b3/27-400a2+6400b2/9=0. In degree8 the drop locus contains the line b=0, which is why the C3 family has its degree-eight partner g8 for every lambda. The full incidence variety in all seven sextic coefficients remains open.

Since0.5.0 `strata.py` stratifies both dimensions. Each correction cell is refined by the joint cells of $[L_N;P_N]$, started from the correction cell itself, so every stratum carries the kernel dimension, the active dimension $\operatorname{rank}[L_N;P_N]-\operatorname{rank}L_N$, and the commuting dimension. At rational points of each stratum the module constructs actual partners: a basis of the active quotient and of $\ker L_N\cap\ker P_N$, each replayed with exact transvectants. A Bareiss determinant of the Sylvester matrix gives the sextic discriminant on the surface, of total degree8, and each stratum is labelled repeated-root, squarefree, or generically squarefree.

The refinement changes the reading of the surface:
- (0,3), f=(x2+y2)3, is not an active exception in degrees4..10. Its extra kernel directions are powers of x2+y2, which commute with f. In degree4 the generic active partner becomes the commuting form (x2+y2)2, so the active dimension drops from1 to0. Only degree12 gains active capacity there (kernel3, active2).
- (+/-16,-9), f=(x-y)4(x2+4xy+y2), gains one active partner in every degree3..12. In degree6 the partner is xy(x-y)4.
- New rational exceptional points lie on drop curves found by the cells. The degree3 curve passes through (+/-4,6) and (+/-24,6) and (+/-24,-9). The degree8 cubic a2b-4b3+6a2-28b2+20b+300=0 passes through (+/-11,6) and through (0,-5). The degree12 quartic b4+24b3+81a2-126b2+405=0 passes through (+/-4,-3) and (+/-32/25,-9/5). All of these are squarefree except (+/-4,-3), which has one double root. Each carries a replayed active partner in the jump degree.

The curve points come from a bounded-height scan (slices b=b0 with height at most12); they are not a complete list of rational points on those curves, which can be of positive genus. The strata are cells over the algebraic closure, and partners are constructed only at rational samples.

Since0.7.0 `invariants.py` explains the strata by invariant theory. With unnormalized transvectants, i=(f,f)4, Delta=(i,i)2, y1=(f,i)4, y2=(i,y1)2, y3=(i,y2)2 give the Clebsch invariants A=(f,f)6, B=(i,i)4, C=(i,Delta)4, D=(y3,y1)2 of degrees2,4,6,10. Because kernel and active dimensions are GL2-invariant, every stratum of the surface is the pullback of an invariant condition. Two universal statements follow, for every binary sextic:
- **Cubic partners.** det L3(f)=(A2-B/6)/16. A sextic has a cubic correction-free partner exactly when B=6A2. L3 is an equivariant map between copies of the cubic representation, so its determinant is a degree-4 invariant, and the Cayley-Sylvester count gives exactly two such invariants, A2 and B. Exact evaluation fixes the constants, and twenty random sextics confirm them.
- **Quartic partner.** The covariant i=(f,f)4 always satisfies (f,i)3=(f,i)5=0, because a binary sextic has no covariants of degree3 and order4 or0 (Cayley-Sylvester). This is the generic degree-4 partner seen on the surface. It is active unless (f,i)1=0, as at the perfect cube.

On the two-parameter surface, the drop curves are invariant loci. A2-B/6 is a constant times the degree-3 curve, and A2-25B/96 is a constant times the degree-12 curve. The degree-8 curve satisfies AB2+BC/6-9D/2=0. Each relation is found by reducing weighted monomials in A,B,C,D modulo the curve ideal. Orbit comparison in weighted projective space also identifies two exceptional points. (0,15) is GL2-equivalent over the algebraic closure to x6+y6, the origin of the family, and has the same partner profile. (0,-5) is equivalent to the octahedral sextic xy(x4-y4), which explains its three-dimensional quartic kernel. (4,6) and (24,-9) lie on B=6A2 but are not equivalent to each other. Whether the degree-8 relation holds beyond this family is open.

Since0.9.0 the degree-12 relation is understood beyond the family. On a second, non-symmetric family, x6+y6+a x5y+b xy5+2x3y3, the degree-12 drop curves ab=81/20 and ab=-9 again satisfy A2=25B/96. Random sextics placed on that hypersurface all acquire a degree-12 partner. A search over the seven-dimensional space of covariants of degree6 and order12 finds the partner explicitly: G=144A2f2+(216/5)A iH+24A f(f,i)2-(9/4)i3-9Delta H+(f,i)22, with H=(f,f)2. For every sextic, (f,G)3=-432(A2-25B/96)(f,H)1 and (f,G)5=25920(A2-25B/96)(f,i)1. So G is a correction-free degree-12 partner on the whole hypersurface wherever it is nonzero. These identities, the cubic theorem and the quartic partner are certified rather than sampled. Each side is a covariant, so checking a three-parameter slice whose GL2-orbit is dense suffices, and an exact grid of (d+1)^3 points on that slice proves an identity of degree d. The converse for degree12 remains open.


---

# Deformation, moduli, and arithmetic codes

For hypersurface f=0, a square-zero deformation f+epsilon g and marked point p+epsilon v require df_p(v)+g(p)=0. At cusp y2-x3 and origin, df=0: constant g=1 obstructs a point lift while g=x permits it. The local cotangent complex is[I/I2 -> Omega], and its dual records tangent/obstruction dimensions. Tjurina algebra for the cusp is Q[x,y]/(f,fx,fy)=span{1,x}; node/cusp historical dimensions were(2,1,1)/(2,1,2) in the indicated tangent/obstruction/T1 conventions. These local objects are not interchangeable with a complete global moduli theory.

E37 short model Y2=X3-16X+16 has Delta151552,c4=768,j110592/37. The differential dj=(559872/1369,373248/1369), gauge direction(64,-96) gives0, moduli direction(96,64) gives77635584/1369. The coordinate direction changes Delta while preserving j, so Delta preservation is not the correct gauge test. Canonical coefficient-space motion should be decomposed into presentation change and genuine moduli change.

The Z[sqrt(-5)] weight-one comparison has(2)=p2^2,(3)=p3+ p3-,(1+/-sqrt(-5))=p2 p3+/-. A nonprincipal ideal class has order2. Rank plus determinant class gives a K0 description Z plus Z/2, and the divisor/Picard/motivic weight-one comparisons agree in the saved artifact. No arbitrary higher-weight comparison is inferred.

Artin-Schreier-Witt0->Z/p^n->W_n --F-1-->W_n->0 belongs to characteristic-p etale sheaves, not the mixed-characteristic cubic Selmer pipeline. Historical Hermitian y^p+y=x^{p+1} over F_{p2} code reports were[8,4,4]_4,[27,6,19]_9,[125,3,119]_25. The p5 nonzero weight enumerator12000z119+600z120+3000z124+24z125 needs constant1 for all words. Another curve y^q+y=x2 had reported n=2q2-q and q7[91,37,52]_49, subject to evaluation conventions. The MK-VII claim was reported refuted; the monograph preserves that boundary.

These strands strengthen the master interpretation: equivalence can hide coordinate change, while an obstruction can survive every legal change. Actual comparison maps and tests are needed; derived/cohomological terminology alone supplies neither.


---

# Prefix arithmetic and machine semantics

For normal finite binary64 values, x=(-1)^s(2^52+F)2^{E-1075}. Subnormals, zeros, infinities and NaNs require separate semantics. The frozen MIE mapping flips the sign bit for nonnegative encodings and complements all bits for negative encodings. Prefix lcp(a,b)=clz(MIE(a) xor MIE(b)); k(x)=lcp(x,+0), D=64-k. Signed zeros remain distinct in the historical golden model; NaNs used k0/COLLAPSED. A prefix ultrametric2^-lcp on distinct encodings is not ordinary numerical distance.

Restricted transfer predictions included ADD=min(kA,kB),MUL=max(0,kA+kB-53),DIV=max(0,kA-kB),SQRT=max(0,kA-1),FMA=min(MUL,kC). They are retained explicitly as heuristics/restricted-semantic claims, not universal floating-point guarantees. Binade changes, carry, cancellation, exponent alignment, normalization, jamming, rounding, exception handling and extended precision can alter leading bits independently of mantissa precision.

The candidate prefix-Fermat condition k(f(x+delta),f(x))>=k(delta)-kappa_f connects the bit geometry to divided differences, Lawvere/Fermat theories, jets and Kahler differentials. A concrete operation/domain is needed before it becomes a theorem. The original PADD/PSC definitions, segmented-adder semantics, and complete corner-case model were not recovered sufficiently to implement them. A Chisel ordinary addition expression is not proof of those semantics.

The exact dyadic power test is different and sound: write nonzero finite rational dyadic x=+/-u2^e with u odd. It is a rational dth power iff u is an integer dth power and d divides e, with a negative sign only when d odd. Zero is separate. This is arithmetic of the value, not a heuristic prefix-depth prediction.

The historical corrected experiment found lambda_min16 inactive because mean k~1; collision1/escalation0 null; an LCP margin due to initialization; and H2 due to trivial weight shrinkage. Training had not established induced prefix geometry. The December modular-addition Transformer run had training~.99 but validation~.3333 through epoch1000, with ranks about13,76,78 across encoders. These negative results remain in the corpus.


---

# Mathematical physics and deformation protection

SYMMETRON explored Weyl/crossed-product algebras, ADE/non-ADE deformation, Berry curvature, modular/Monster/Umbral/Mathieu moonshine, VOAs, derived geometry, graphene/Kagome models, spectral dimension and quantum-gravity proposals. Historical constants alpha=.0333996828,beta=.6732050807568877,kappa=1.923606797749979,C~7042.25 and activation .0712 do not become derived physical constants merely by being retained. The proposed Hamiltonian L0-c/24+sum gamma_g T_g+kappa log L0 requires a positive spectral domain. L-value formulas lacked recovered underlying objects. The model tests recorded zero Berry curvature for both compared cases, not an observed topological distinction.

MMHW used psi=(1-alpha x2)e^-x2/2(1+beta sin(pi x2)e^-abs(x)3), with noncommutative-torus Chern/index/soliton applications. Claimed index error+.01,Hall response2.00+-.02 e2/h,nu1/3 and soliton.50+-.02 are model reports, not experimental validation. Admissibility of a wavelet family requires its own conditions.

The six-term phase potential is cos2theta+(2/3)cos3theta+(2/5)cos5theta+(1/4)cos8theta-(2/9)cos9theta-(1/6)cos12theta. At11pi/30 the derivative cancels numerically and second derivative~12.2092 is positive. The exact identity1-2cos12theta=(3-sqrt5)/2=phi^-2 also holds at other phase points. This does not establish global selection or the physical CKM phase.

Ceff=c(1-c2)/(ab), a=|Uus|,b=|Ucb|,c=|Uub|. If a model enforces Ceff=phi^-2, then c2(1-c2)2-3abc(1-c2)+a2b2=0. A different archived coefficient7 polynomial and N,K,t,J phase relations remain unresolved because their definitions were missing. Do not merge them. The allowed CP-even deformation V0+epsilon x changed the relation historically. A stationary point sensitivity -(Hessian V0)^-1 grad W and relation tangent -grad R^T(Hessian V0)^-1 grad W identify which permitted operators break protection; symmetry zero modes require quotienting.

Domain-wall work reported whole-line sign/barrier enclosures,1,080vacua,Goldstone/gauge derivative/cubic channels,Goldstone width~3.8e-8GeV,WW+ZZ~1.8e-9GeV atg.4,threshold(M-2m)3,frame window6.56<t<9.52,one-loop radial correction/counterterm,thermal wall-only window~8.63MeV,and late-network gravitational-wave simulations. These are model-specific reports. Running,thresholds,higher operators,higher loops,global vacuum selection,Sommerfeld/physical66degree prediction remain explicit frontiers. No physics source is modified by this repository.

Since0.10.0 `deformation.py` tests relations among stationary states against a declared perturbation space. At a nondegenerate stationary point, the implicit function theorem gives dx*/dtheta=-H^{-1}M exactly. A relation R among several stationary points then has first-order response dR/dtheta=sum_s grad_sR.dx*_s/dtheta. The module returns the breaking directions and the preserving subspace. Given a symmetry's action on the perturbations, it decides whether every symmetric perturbation preserves R. In the double well x4/4-x2/2+t1x+t2x3+t3x2, the mirror relation x*_++x*_-=0 is broken by the odd perturbations t1 and t2 and is protected by x->-x. The location x*_+=1 is accidental, broken even by the symmetric t3. First order only: a protected first-order relation can still break at higher order unless the symmetry argument is exact.


---

# WIND and environmental observability

WIND connects measurements to target questions rather than treating a reconstructed field as uniquely observed. Radar support, beam geometry, averaging windows, noise, staleness and target functionals are explicit. The historical corpus had272 NEXRAD volumes, and a lower velocity split in54/54 NewEngland volumes with mean absolute difference .74->1.556m/s. These are saved empirical reports; original radar bytes are not in PerfectJet and have not been replayed here.

The signed vorticity ledger is zeta=v_x-u_y,S=(zeta+f)w_z,T=-v_z w_x+u_z w_y,D=-(zeta+f)div(u),B=(rho_x p_y-rho_y p_x)/rho2,F=(curl forcing)_z,P_beta=-beta v, total=S+T+D+B+F+P_beta. A complete budget needs compatible signs, supports and fields. Surface geostrophic inference,3D Lorenz energy budgets,and storm impact targets are different quantities.

Information J=H^T R^-1H,hidden-target optimization over ker H intersect ker M,exact linear SDE F=e^{A dt},Qd=int e^{As}LL^T e^{A^Ts}ds,innovation I=sum K_i nu_i^T S_i^-1 nu_i,constraint injection C=delta_xC^T Q delta_xC,and residual R=norm(W[partial_t x+N(x)-F(x)])2 were recovered. K_i can mean a spatial support kernel; do not silently read every K as a Kalman gain.

Expiry criteria compare structural ambiguity or propagated uncertainty to positive baselines. The exterior law v=c r^-p,p=1+2h used quadrant threshold radii; pooled earlier p~.5123/.5445 and continuation .593829/.459171 are different fits/windows, not a universal exponent. A simultaneous quadratic pressure fit needs rank6 and at least7 stations for residual capacity, plus time alignment and conditioning. Repeated radial rows cannot repair a hidden crosswind; an independent crossbeam can in the declared linear model.

The source archive distinguishes frozen target truth from changed reporting windows, sustained winds from gusts,one-minute from ten-minute means,height/datum from other quantities,and missing from zero. Chemistry/aerosols were described as reduced HOx-NOx-VOC-ozone,two-moment microphysics,and4D transport, but individual rate equations and source states remain unrecovered. We preserve their integration plan without inventing reaction constants or claiming complete atmospheric chemistry.


---

# Finsler action, thermal spectra, and empirical decisions

For c>=0,D>0,phi(v)=0 for abs(v)<=c and(abs(v)-c)2/(4D) outside. Its convex conjugate is c abs(p)+D p2. With drift b, H=b.p+sum(c_i abs(p_i)+D_i p_i2). This fixes the normalization; another archived D/4 Hamiltonian belongs to a different convention and cannot be combined silently. Quasipotential H(x,grad W)=0 uses viscosity/subgradient treatment at facets. Historical finite optimizations .4,.5568,1.6 were model reports; the reversible .4 kink was later not robust. LC impedance Z0=sqrt(L/C),f0=1/(2pi sqrt(LC)) is a concrete physical mapping; its broader Finsler metric interpretation requires the actual circuit reduction.

Thermal spectra use H_i=E_i+cE_i^a,Z=sum exp(-beta H_i),F=log Z(2beta)-2log Z(beta)=log Tr rho_beta2. Variance over a declared log-beta grid is a particular objective, not every historical q-KMS criterion. Recovered fits included nonCMa.263053,c1.005524,V.006647506;CMa.25,c~2e-6,V7.650634e-7;Gopela.274014,c1.050564,V.08105414;dilationa.297677,c1.128171,V.2077005;Sp8a.285513,c1.059989,V.1003861. Sizes reached5000,12reps,400bootstrap,another1728draws/object/clip. Rankings were clip-dependent; c near0 weakly identifies a. Claims of universal2/3-versus1/4 splitting are not inferred.

Harsh Audit/tau-Crystal sought to prevent Texas-Sharpshooter post-hoc mass fitting through fixed prior lattices, transformation chains, perturbation/null tests,MDL/Bayes comparisons,and discovery ledgers. Historical implementations and executions varied. The math goal is distinguish explanatory restriction from added fit flexibility.

NFL Combine scouting seeks hidden talent,bust risk,and position-specific development. Early movement is a sequence: approach,braking,turn,recovery,acceleration. Pauli products separate dot-product alignment from cross-product order information; nested commutators propose higher interactions. A commutative ablation and held-out continuation tests are required. Reported future-speed MSE reductions33.36%/26.59% do not establish scouting success or betting profitability. An earlier betting baseline trailed market; live odds and bookmaker access were separate integration tasks. Exact representation machinery structures the candidate features; outcomes still require empirical validation.

Industrial portfolio570solved versus baseline584 with42.1% extra summed time and zero conflicts is a retained negative comparison. Family-held-out512tasks/128tests,graph504samples,sequence52families and calibration/experiment examples are workload-specific historical reports. Customer economics require setup,runtime,break-even,and supported-model conditions.

Since0.5.0 the identifiability question has an exact kernel. For the response $\eta=\beta_0+\beta_1s+\beta_2a+\beta_3sa$, a player's attempts form a design X. A readout $h^\top\beta$ is determined by those attempts exactly when $h\in\operatorname{row}(X)$. `readout.identify` returns estimator weights, or a vector n with Xn=0 and $h^\top n\ne0$: two coefficient vectors that fit every attempt and disagree on the readout. `demand_readout` forms $h_q=\sum_kq_k\phi(d_k)$ for a declared demand distribution. `repair` finds the smallest set of candidate conditions making the readout identifiable, and `value_of_information` gives the exact Gaussian posterior-variance reduction of each candidate, marked as a repeat or a new direction. In the receipt, repeats reduce variance by about0.16 while two new conditions are needed to identify the readout at all.

Since0.6.0 the scouting question has its own adapter, `applications/nfl_scouting`, with a protocol in docs/nfl. It asks whether a repeatable, demand-adjusted recovery readout from the Combine predicts NFL get-off beyond position, body measurements, timed tests and drill availability known before the draft. The pipeline detects turns and records every smoothing and alignment branch of eta with full lineage. It fits the demand frame and a linear mixed model by EM on training athletes only, and gates each athlete's readout with the exact identifiability test. Targets are cross-fitted context residuals with training-only shrinkage, and a leakage check runs every time. Validation uses athlete-grouped temporal folds with identical availability indicators and tuning for both models, the paired metric G=1-MSE_movement/MSE_baseline, fixed-prediction and full-refit intervals, diagnostics, a frozen shortlist rule, and scouting cards that show pooling reliance and the most informative next condition. A synthetic generator with a planted or null signal tests the pipeline: it recovers a planted signal and reports none under the null. Synthetic results are never evidence about football, and no real-data scouting advantage is claimed.


---

# Closure stress, geometry, games, and integrations

Finite closure cl(A)=intersection of stable supersets and debt mu(cl(A))-mu(A) describe information missing from an admitted state. Historical13-atom8192-world and16-atom65536-state programs tracked Omega_miss,Omega_ung,Omega_rule and sought minimal admitted closure cost. The proposed invariant I_tau=(K_tau*,Lambda_tau,B_tau) combined cost,cheaper-route obstruction,and fake-work spectrum. Closure means entailment under the rules; grounding/replay relates it to actual truth. Equivalent Horn bases,atom renaming,cost rescaling,refinement and reencoding were proposed invariance tests.

Comparison cochains gamma_ij=C_i-C_j and eta_i(f)=Psi(f)C_i-C_i Phi(f) require an additive linear setting. A true double complex has D=delta_Cech+(-1)^p d_I,D2=0. Then an unclosed defect is incoherent,a coboundary removable,and a closed nonexact class an obstruction. Arbitrary nonlinear constraint sheaves cannot be assigned ordinary H1 without constructing the complex. Null-labor efficiency1-K(residue)/K(expansion) needs an explicit cost model and preserved answer.

Geometry includes compatible charts,shared-factor intersections,unordered determinant identities,Jacobian transport,polygon triangulations,separating halfplanes,boundary cancellation,area identities,and visibility-graph shortest paths. Generic graph optimality from potentials does not prove the graph contains exactly all valid geometric edges. Exact mesh arithmetic does not replace full coverage/topology. Riemannian source mining,genus2 periods/marking,Richelot singular/stable reduction,signed quartic lifts,and smooth-curve comparisons remain separate integrations.

STRING/Pokepolis used finite phase abstractions,exact route populations,battle replay,and feedback studies. Historical reports include68->34 symbolic reduction,8->4 forecast statistic,6912route cases,232battle replays,and48battle studies. FF7 architectural reuse involves saved script positions,waits,request/ack boundaries,future-equivalence,and distinguishing experiments; original opcode archive was not recovered.151procedural rigs and1812property combinations are art reports,not proof of semantic completeness. Desired interactive worlds,clear gameplay,live research updates,and user-facing Explorers are application requirements.

BLAST work requested full-source adapters,recurrence proof,annotation,whole-database recall,and dedicated branch publication. Exact equations and complete original source/corpus were not recovered sufficiently to claim implementation here. The master repository keeps these destinations and obligations visible. PerfectPower and DynaComp are pinned upstream references,not vendored or silently merged. No existing site,mobile app,or external physics session is changed by this release.


---

# Master enhancement architecture

The preserved enhancement stack is question->candidate representation->closure test->exact executable model,bounded approximate model,or repair witness. It is a design organizing several precise mathematical mechanisms,not a single universal theorem. Its five central equations are qF_a=Fbar_a q,RA=Abar R,psi composed F=Gpsi+r,e_next=Ae+Rz+Su,and H_{u,v}=f(uv).

Question-specific equivalence and preservation profiles separate dimensions,outputs,multiplicity,reconstruction,valid domain,time horizon,and cost. Hankel structure discovers predictive state. Weighted quotients preserve populations only under an aggregation identity. Residual features repair nonlinear closure where possible; delays distinguish missing memory from missing sensors. Sensitivity states test response to parameter changes. Composed bounds permit multistage reduction,and decision margins stop refinement when a choice is settled.

Arithmetic height relative to a question organizes fibres but cannot bypass completeness. Adaptive local tests prioritize exact exclusions. Integral Smith/Hermite transport repairs rational-span gaps. Commutators isolate order effects. Deformation tangents test protection before expensive global physical work. Failed representations should return distinguishing words,unclosed polynomial coefficients,duplicate auxiliary extensions,divisibility failures,hidden target vectors,failed metric conditions,or allowed perturbations breaking a relation.

The second enhancement sharpens this into active transvectant spectra,exact ansatz obstruction7lambda-40,affine-periodic cyclotomic coefficients,positive valuation kernels distinct from penalties,finite-part tail enclosures,explicit cubic field transports,oriented regulator vectors,flip involution tests,Riccati residuals,target-first sensor repair,and reusable type histograms. These changes are implemented where supported by the current exact kernel; exact Smith-form lattice repair,single-output Hankel word realization,and coarsest exact lumping became executable in0.2.0; Hermite form,multi-output realization,one-parameter rank loci,and the adaptive power-residue sieve followed in0.3.0; multi-parameter comprehensive rank cells in0.4.0. The full sextic incidence variety,sieving beyond perfect-power hits,general nonlinear reduction and unrestricted empirical feature learning remain explicitly proposed. Release0.12.0 implements a finite-horizon numerical delay-state adapter for movement with player-held selection and physical-coordinate forecasts; this is distinct from exact all-future Hankel realization.

The master interface should record a domain,questions,state representation,legal operations,weights,exact identities,error bounds,source maps,obstructions,costs,and evidence. A new application adds an adapter and its preserved questions. It must not acquire correctness from its similarity to an older application. The decisive reuse is an executable identity with matching assumptions.

Release0.5.0 makes the master interface executable as `engine.py`: one report shape for every adapter, an adaptive closure loop that adds only residual-implicated structure, and decisions that stop once settled. The partner program now stratifies active capacity, not only correction rank, and readout identifiability gives the empirical program an exact gate before any fitting.


---

# Corrections, missing sources, and remaining frontiers

This repository preserves content by recording corrections rather than deleting awkward history. Exact checked means rational/cyclotomic replay in the supplied Python tests; numerical checked means floating evidence; derived means a stated mathematical argument; historical report means a prior claim not freshly reproduced; proposal/open/conditional/rejected retain their plain meanings. No status means new Lean verification.

Key corrections are the HLR source sign/factor2; singular vectors versus invariant modes; PSG multiplier factor2,A<1/2 contradiction,cofactor D versus D/v,finite-degree versus global Darboux classification,root jets versus origin germ,Puiseux sign,flip versus involution; dyadic Weil model mismatch; complete Gauss sum versus full/partial blocks; penalty versus PSD kernel; finite part versus quantum volume; all-embedding regulator cancellation; discriminant versus field identity; numerical orbit matching versus an exact orbit proof; integer saturation versus rational span; and deterministic error versus empirical predictive uncertainty.

Missing originals remain explicit: the separately named arithmetic GCD-kernel construction; complete master.txt; full SOE original archives; FF7 opcode archive; original PSG26/100-term coefficients and full prolonged numerator; complete PADD/PSC corner-case semantics; chemical/aerosol reaction-rate tables; full BLAST recurrence/adapters/corpus; original definitions for the coefficient7 CKM polynomial and N,K,t,J; radar bytes; original Petersen50 resource data and DAG. A filename or workflow title is not mathematical evidence for these items.

Release0.2.0 closes three implementation gaps rather than any formal frontier: integer lattices (Smith form, infeasibility certificates, integer kernels, saturation index), exact word-Hankel realization with held-out witnesses, and coarsest exact weighted lumping. The correction integer saturation versus rational span now has an executable witness.

The strongest finite executable contributions in0.1.0 are observable-space closure and hidden witnesses,partial-machine equivalence,polynomial-feature span replay,residual selection counts/rank/unrank/ties,weighted aggregation checks,energy balance,jet composition/Riccati residuals,corrected PSG root replay,cyclotomic coefficient recurrence,transvectant active census,and exact cubic coefficient-field identities. Archive algorithms are preserved as upstream source text and are not automatically included in the runnable trusted core.

Release0.3.0 adds Hermite form, multi-output Hankel realization, exact one-parameter rank loci (which rediscover the 7lambda-40 obstruction and certify the rational exceptional set of the C3 partner family for degrees3..12), and the adaptive local sieve for perfect-power hits.

Release0.4.0 adds comprehensive rank cells for several parameters, with an exact Groebner engine and saturation. On a two-parameter sextic surface it finds the exceptional points (+/-16,-9), (0,3), (0,15) and (0,-5) beyond the C3 slice.

Release0.5.0 adds active strata with replayed partners and the sextic discriminant on the two-parameter surface; it shows that the perfect-cube point (0,3) is mostly commuting structure and finds new squarefree exceptional points such as (+/-11,6), (+/-24,-9) and (+/-32/25,-9/5). It also adds exact readout identifiability with repair and value of information, certified decisions with targeted refinement, the evolution-defect split, and the adaptive representation engine with a unified report.

Release0.10.0 adds constraint attribution and inclusion profiles for selection populations, and first-order deformation protection of relations among stationary states.

Release0.9.0 proves a degree-12 partner on the hypersurface A2=25B/96, with an explicit covariant formula. It also certifies the cubic, quartic and degree-12 identities by exact slice grids.

Release0.8.0 adds a solution-carrying compiler for k y2=an2+bn+c. Every branch has a reconstruction map and a completeness status, Nagell seeds make the Pell branch complete, and exact remote-index queries are supported.

Release0.7.0 proves two universal partner statements for binary sextics: det L3=(A2-B/6)/16, and the covariant (f,f)4 is always correction-free. It identifies the surface's drop curves as invariant loci, and identifies (0,15) with x6+y6 and (0,-5) with the octahedral sextic.

Release0.6.0 adds the Combine scouting adapter and its protocol; it implements the empirical test but does not report a real-data result.

Release0.12.0 connects operational NFL movement targets, finite-horizon numerical delay states, player-cross-fitted Combine-to-movement-to-get-off transfer, fitted physical loadings, and exact joint measurement allocation. It adds a reproducible Gaussian package counterexample and a rational-snapshot allocation regret bound. The official nine-file experiment remains unexecuted; no new empirical NFL advantage is claimed.

Formal frontiers include the full seven-coefficient incidence variety,all-degree Darboux classification,elliptic rank/saturation/global bounds,geometry coverage/visibility completeness,and concrete large-DAG formal attachment. Empirical frontiers include scouting outcome advantage,market superiority,native device rates,chemical state ingestion,and sensor coverage. Closing one frontier does not close the others.


---

# Mathematical proofs for the shared exact core

These arguments state the mathematical reasons behind the executable identities. They are conventional written proofs, not Lean kernel proofs. The independent finite checks attack implementation errors; they do not replace the arguments' hypotheses.

## Cyclotomic closure and affine-periodic coefficients

Let L be a positive integer and zeta a primitive Lth root of unity. Work in formal power series over Q(zeta). Every pair a,b>=0 has unique decompositions a=r+Li,b=s+Lj with0<=r,s<L. Since zeta^(ab)=zeta^(rs), summing i,j gives the denominator(1-x^L)^2 and numerator sum_{r,s<L}zeta^(rs)x^(r+s). Uniqueness of decomposition prevents any missing or duplicated summand.

The coefficient of x^n in the original series is a_n=sum_{j=0}^n zeta^(j(n-j)). Write n=dL+r. The summand is periodic in j modulo L because replacing j by j+L changes j(n-j) by a multiple of L. The n+1 indices comprise d complete blocks and the partial block0..r. Thus a_n=dG_r+B_r. Replacing n by n+L increases d by1 and leaves r fixed, proving a_{n+2L}-2a_{n+L}+a_n=0. The numerator at1 is sum_r sum_s zeta^(rs)=L: r0 contributes L, every other inner geometric sum is0. For L>=2 its highest coefficient is zeta^((L-1)^2)=zeta.

## Active partner dimension

Let L:V->W and P:V->Y be linear maps over a field. Put K=ker L and J=K intersect ker P. The active quotient is K/J. Rank-nullity gives dim K=dim V-rank L and dim J=dim V-rank([L;P]). Subtraction yields dim(K/J)=rank([L;P])-rank L. This counts independent nonzero P outputs available inside the correction-free kernel. It does not count every individual nonzero partner, which is an infinite set over an infinite field.

For a fixed sextic, the third/fifth transvectants are linear in the partner g, so this theorem applies to the supplied gate matrices. Odd self-transvectants vanish by antisymmetry, but their first transvectant also vanishes; self-pairs therefore contribute to K without contributing to the active quotient.

## Parametric molecular identity

The sextic f_lambda and eighth-degree g_lambda are affine in lambda. Every fixed-order transvectant is bilinear in its two inputs, so each resulting monomial coefficient has degree at most2 in lambda. Exact vanishing at three distinct rational parameters implies every coefficient polynomial is identically zero. The implementation retains four parameters and independently computes all polynomial coefficients. The first transvectant has x12 coefficient6, independent of lambda, so its nonvanishing is not merely a sampled observation.

The quintic h is independent of lambda. Its third transvectant is affine in lambda; exact coefficient calculation yields72(7lambda-40)(x4y+xy4). Fifth transvectant vanishes. This proves exactness of this partner at40/7 and failure for other lambda. It does not prove absence of other quintic partners elsewhere.

## Target recovery

For finite-dimensional vector spaces, ker O subset ker G iff every row functional of G vanishes on ker O. The annihilator of ker O is the row space of O, so this is equivalent to G=LO for a linear map L. Equivalently, choose a basis N for ker O: recovery holds iff GN=0. A nonzero column response supplies a witness with unchanged observations and changed target. Rational row reduction computes this exactly for rational input matrices.

For T(x)=g^Tx+1/2 x^TQx with symmetric Q, substitute x=x0+Nz. The difference T(x0+Nz)-T(x0) equals z^T N^T(g+Qx0)+1/2 z^T N^TQN z. A polynomial of degree at most2 vanishes for every z over Q or R iff its linear and symmetric quadratic coefficients vanish. Hence the two fibre-constancy conditions. On a restricted/nonlinear feasible fibre they are sufficient but may not be necessary; the chapter's equivalence is for the full affine fibre.

## Weighted quotient series

Assume RA=Abar R. Induction gives RA^t=Abar^tR. If H=Hbar R, then HA^ts=Hbar Abar^t Rs. Apply the same multiplication argument coefficientwise to A(z)=sum_c z^c A_c. Positive costs imply A(0)=0 and ensure the formal inverse exists as a geometric series, yielding H(I-A(z))^-1s=Hbar(I-Abar(z))^-1Rs. Matching state labels alone is insufficient: aggregation must preserve total outgoing weights and the output must factor through R.

## Exact feature closure

Assume p(F(x))=Gp(x) as a polynomial identity. Base time0 is immediate. If p(F^t(x))=G^tp(x), substitution gives p(F^(t+1)(x))=G p(F^t(x))=G^(t+1)p(x). If O=Hp, then all outputs O(F^t(x))=HG^tp(x) follow. Exact span solving and coefficient replay establish the one-step identity; no regression residual is silently discarded. Existence of a finite closed feature span is not asserted for arbitrary polynomial F.

## Completion-count navigation

A feasible population in original binary order partitions disjointly by the next bit. Therefore C(q)=C(q0)+C(q1). In lexicographic order, every zero-branch completion precedes every one-branch completion. A word with bit1 skips exactly C(q0) predecessors at that level. Summing the skipped populations gives rank. Conversely, an address r either lies in the zero branch or in the one branch after subtracting C(q0). Induction on remaining length proves rank/unrank are inverse bijections. Drawing r uniformly thus samples original objects uniformly. Prefix count zero means no feasible completions and must not be sampled.

## Energy balance and defect propagation

For constant symmetric M, differentiating E=1/2 u^TMu gives E'=u^TM(Au+f). The scalar u^TMAu equals u^T(A^TM+MA)u/2. Divide by E to obtain the declared lambda/zeta identity and rho=1-zeta/lambda. M positive definite and u nonzero ensure E>0; lambda0 makes the ratio undefined.

Subtract V times reduced dynamics from full dynamics to get e_next=Ae+(AV-VG)z+(B-VH)u. Iterating yields the exact finite convolution. If norm(Ax)<=gamma norm(x), gamma<1, apply the triangle inequality at each step. A uniform defect bound delta yields the geometric series. This assumes the same valid norm throughout; eigenvalue bounds alone do not establish that norm contraction.

## Reflection coordinate and flip obstruction

If an injective local Psi satisfies Psi composed f=-Psi, applying it twice gives Psi composed f2=Psi and hence f2=id. Conversely, for a centered analytic involution f with f'(0)=-1, Psi=(x-f(x))/2 has derivative1 at0, so the analytic inverse function theorem makes it locally invertible. Direct substitution gives Psi composed f=-Psi. This proves the local equivalence.

For f(x)=-x+ax2+bx3+O(x4), expand -f+a f2+b f3 to cubic order. Quadratic terms cancel and the cubic coefficient is-2(b+a2). This is an obstruction to involution at that order; its vanishing does not settle higher orders. The finite-jet implementation composes the polynomial series directly rather than inferring reflection from multiplier-1.

## Quotient-ring field identity

In the monic quotient Q[u]/(u3-4u2+5u-1), reduction produces unique degree<3 coordinates. A nonzero polynomial element is invertible when its multiplication matrix is nonsingular; solving for its inverse and replaying the product checks the denominator. Substituting alpha=u-1 reduces alpha3-alpha2+1 to0. Since alpha is invertible, beta=-1/alpha satisfies beta3-beta-1=0 after multiplication by alpha3. The Hessian and vertex identities are established by the same exact quotient operations. This proves algebraic identities of the displayed field elements, not the geometric interpretation of the original state integral.

## Decision margin

If abs(J(a)-Jhat(a))<=epsilon_a, then J(a)>=Jhat(a)-epsilon_a and J(a)<=Jhat(a)+epsilon_a. A candidate whose lower bound exceeds every competitor's upper bound is strictly best. A shared epsilon therefore needs estimated margin>2epsilon. Equality only provides a non-strict comparison; the implementation returns unresolved for overlapping intervals. Empirical uncertainty needs its own justified intervals.

## Smith form and integer certificates

Row and column operations by integer elementary matrices keep U and V unimodular. Each pass either strictly lowers the absolute value of the pivot or clears its row and column. Positive integers cannot decrease forever, so the pass terminates. If the pivot fails to divide some later entry, adding that row to the pivot row and reducing again gives a smaller pivot. Thus the final diagonal satisfies $d_1|d_2|\cdots$. Unimodular transforms preserve the gcd $\Delta_k$ of all k-by-k minors, by Cauchy-Binet in both directions. For a divisibility-ordered diagonal, $\Delta_k=d_1\cdots d_k$. The tests compare these two routes.

Put y=V^{-1}x, so Bx=b becomes Dy=Ub. Because V is unimodular, x is integral exactly when y is integral. Coordinatewise, $d_iy_i=(Ub)_i$; rows past the rank require $(Ub)_i=0$. If coordinate i fails, the row $U_i/d_i$ times B equals row i of $V^{-1}$, which is integral, while its product with b is not an integer. Any integer solution x would make the same product an integer, a contradiction. The integer kernel is $\{Vy:Dy=0\}$, so it is spanned by the last n-r columns of V. Those columns extend to the unimodular basis V, so the kernel lattice is saturated.

For a generator matrix G, $UG=DV^{-1}$, and the rows of UG generate the same lattice as the rows of G. Hence the lattice is $\bigoplus_i d_i\mathbb Z w_i$, where $w_i$ are the rows of $V^{-1}$. Its rational span meets $\mathbb Z^n$ in $\bigoplus_{i\le r}\mathbb Z w_i$, because the $w_i$ form a basis of $\mathbb Z^n$. The quotient is $\bigoplus\mathbb Z/d_i$, with order $d_1\cdots d_r$. When $d_i>1$, $w_i$ is in the saturation and not in the lattice.

## Hankel realization from a finite block

Let M be the invertible Hankel block on prefixes $P_0$ and suffixes $S_0$, with r equal to the rank of the full finite block H on prefixes and suffixes of length at most k. Then every row $H[p,\cdot]$ is a combination $c_pH[P_0,\cdot]$, and restriction to $S_0$ gives $c_p=x_pM^{-1}$. Applied to the columns $as$ and to the empty suffix, $f(pas)=c_pH[P_0,as]$ and $f(p)=c_pH[P_0,\varepsilon]$. For prefixes p in the block, this gives $x_{pa}=x_pM^{-1}H_a[P_0,S_0]$ and $f(p)=x_pM^{-1}f(P_0)$. Induction on word length from $x_\varepsilon=f(S_0)$ shows the model agrees with f on the block. When f has a finite representation of dimension $n\le$ the block rank, the block rank equals the global Hankel rank, which is the minimal dimension. Without such a hypothesis the block cannot certify agreement on longer words. A held-out disagreement is then a witness that the block is too small.

## Coarsest exact lumping

Call a partition valid when every action matrix has constant block-column sums within each source block and the output is constant on blocks. The refinement step splits blocks by the vector of block-totals computed under the current partition. Suppose a valid partition $\pi$ refines the current partition. Two states in one $\pi$-block have equal totals into each $\pi$-block, so they also have equal totals into the unions that form current blocks. They are therefore never separated. The initial output partition is refined by every valid partition. By induction, every valid partition refines every iterate. The iteration stops only when the partition is valid, so its fixed point is the unique coarsest valid partition. With R the block indicator, the constant sums give $RA_c=\bar A_cR$ and $H=\bar HR$, which preserves the weighted cost series.

## Hermite form and lattice equality

Integer row operations keep U unimodular. In each column, Euclidean reduction among the remaining rows terminates with one nonzero entry, because the minimum absolute value strictly decreases. Rows above that pivot are then reduced modulo it. Uniqueness: let H and H' be Hermite forms of the same row lattice. Their pivot columns agree, because the pivot columns record the first nonzero coordinate across the lattice's echelon filtration. The first pivots are equal and positive, since each generates the projection of the lattice onto that coordinate. Inductively, row i of H minus row i of H' is a lattice vector whose first possible nonzero coordinate is pivot i, and that entry lies strictly between minus the pivot and the pivot. It must therefore vanish. The difference then has no nonzero pivot coordinate and is zero. Hence two row lattices are equal exactly when their nonzero Hermite rows agree.

## Multi-output realization

Replace columns indexed by suffixes with columns indexed by suffix-output pairs. The argument for single-output realization applies unchanged: each row $H[p,\cdot]$ is $x_pM^{-1}H[P_0,\cdot]$, so one state vector serves all outputs. A stacked rank can exceed every single-output rank, because the outputs may read independent parts of the state.

## One-parameter rank loci

Let r be the rank of A(t) over Q(t). Some r-minor is a nonzero polynomial of degree at most rd, where d bounds the entry degrees. It cannot vanish at all rd+1 evaluation nodes, so the maximum sampled rank is r. At any t, rank A(t)<r exactly when every r-minor vanishes there. Every drop point is therefore a root of the chosen nonzero minor $M_0$, and multiplicities do not matter, so the squarefree part s suffices. Over $R=Q[t]/(s)$, an element that is zero vanishes at every root of s. An element coprime to s vanishes at none of them, and an element sharing a factor g with s splits $R\cong Q[t]/(g)\times Q[t]/(s/g)$ by the Chinese remainder theorem. Elimination whose pivots are units of R is valid simultaneously at every root of the current modulus, so the rank is constant across those roots. Splitting at zero divisors terminates because degrees decrease. The drop locus is the product of the factors whose rank is less than r. Rational drop points come from the rational root theorem, and their ranks are replayed by direct evaluation.

## Local power exclusions

If $F(n)=m^d$, then $F(n)\equiv m^d \pmod q$ for every q. A residue that is not a d-th power modulo q therefore excludes n. Survivors for a set of moduli are residues modulo their least common multiple whose reductions survive each modulus. By the Chinese remainder theorem this set depends only on the set of moduli, not on their order. The greedy choice changes cost, never correctness. The sieved count equals the brute-force count, because integer roots are checked on every survivor.

## Comprehensive rank cells

Work over the algebraic closure. Rabinowitsch: a point t lies in V(I) minus V(q) exactly when some z satisfies $I(t)=0$ and $1-zq(t)=0$. Projecting away z, the ideal $(I+\langle1-zq\rangle)\cap Q[t]$ is $I:q^\infty$, and V of it is the Zariski closure of V(I) minus V(q). An elimination order with z largest computes this intersection as the z-free part of a Groebner basis. Saturating by inequations one at a time gives $S=I:(q_1\cdots q_s)^\infty$.

Each branch keeps a pair (S,N) with S saturated by every member of N. Its cell V(S) minus V(prod N) is dense in V(S), so the cell is empty exactly when S is the unit ideal. A pivot p is zero on the whole cell exactly when $S:p^\infty$ is the unit ideal. Otherwise the pivot branch $(S:p^\infty,N+p)$ and the zero branch $((S+p):N^\infty,N)$ split the cell into two disjoint constructible pieces whose union is the cell. Matrix entries may be reduced modulo S, because they are unchanged on V(S). In the pivot branch, the row operation $\mathrm{row}_k\to p\,\mathrm{row}_k-a_{kj}\mathrm{row}_i$ multiplies a row by p, which is nonzero on the cell. An exact division by the previous pivot, also nonzero on the cell, likewise preserves the pointwise rank. Each branch removes a row and column or adds a polynomial that is not already in the radical. Noetherianity and finite matrix size give termination. The leaves therefore partition parameter space, and the rank is constant on each leaf. Rational points of a zero-dimensional closure come from a lexicographic Groebner basis, the rational root theorem on its last eliminant, and back substitution. Tests compare each leaf's rank with direct evaluation on a grid.

## Active strata

On a correction cell C the rank of $L_N$ is constant. Running comprehensive elimination of $[L_N;P_N]$ from the starting pair (S,N) of C only ever adds equations or inequations, so its leaves partition C and the joint rank is constant on each leaf. Both ranks are then constant on every stratum, and so are $\dim\ker L_N=N+1-\operatorname{rank}L_N$ and $\dim A_N=\operatorname{rank}[L_N;P_N]-\operatorname{rank}L_N$, because $\ker[L_N;P_N]=\ker L_N\cap\ker P_N$. At a rational point, choosing kernel vectors whose $P_N$-images are independent gives a basis of the active quotient, and the nullspace of $P_N$ restricted to $\ker L_N$ gives the commuting part; each vector is replayed as a form with exact transvectants. The sextic has a repeated root exactly when the resultant of $f(x,1)$ and its derivative vanishes, since the leading coefficient is1.

## Identifiable readouts

If $h=X^\top c$, then $h^\top\beta=c^\top X\beta$ is a function of the noiseless observations. If $h\notin\operatorname{row}(X)=\ker(X)^\perp$, some $n\in\ker X$ has $h^\top n\ne0$; then $X\beta=X(\beta+n)$ while the readouts differ by $h^\top n$. Adding a row already in row(X) leaves row(X) unchanged, so a repeat can never make a non-identified readout identified. For $y=X\beta+e$ with Gaussian prior and noise, the posterior covariance $(\Sigma_0^{-1}+X^\top X/\sigma^2)^{-1}$ does not depend on y, so the expected variance reduction of a new row equals its realized reduction. Adding a row adds a positive semidefinite term to the precision, so no candidate increases the variance.

## Settled decisions and targeted refinement

If every reported interval contains its true value and the leader's lower bound exceeds every competitor's upper bound, the leader is strictly best whatever the true values are inside the intervals. Refinement of an action whose interval is already below the leader's lower bound cannot change the comparison, so only overlapping contenders need refinement.

## Evolution-defect split

From $x_{t+1}=Ax_t+Bu_t$ and $z_{t+1}=Gz_t+Hu_t$, $e_{t+1}=Ax_t+Bu_t-VGz_t-VHu_t=A(e_t+Vz_t)-VGz_t+(B-VH)u_t=Ae_t+(AV-VG)z_t+(B-VH)u_t$. Taking norms, $\|e_{t+1}\|\le\|A\|\|e_t\|+\|(AV-VG)z_t\|+\|(B-VH)u_t\|$, which is the recursion the implementation reports.

## Adaptive monomial closure

Pullback by a polynomial map sends a monomial to a polynomial, and the loop adds exactly the monomials of the pullbacks that are missing. If the loop stops with nothing missing, every retained monomial pulls back into their span, which is the closure identity. The span of $C,CK,CK^2,\dots$ inside it is the smallest pullback-closed space containing the outputs, by the observable-space argument of chapter07.

## Cubic and quartic partners of every sextic

Transvectants are SL2-equivariant. For a cubic g, (f,g)_5 has negative order and vanishes, so L_3(f) is the map g -> (f,g)_3 from cubics to cubics. It is linear in f and equivariant, so det L_3(f) is an SL2-invariant of f of degree 4. By the Cayley-Sylvester formula, the binary sextic has exactly two linearly independent invariants of degree 4 (`covariant_count(6,4,0)=2`), namely A^2 and B. Hence det L_3 = alpha A^2 + beta B. Two sextics with independent (A^2,B) determine alpha and beta. The identity det L_3=(A^2-B/6)/16 is then certified by the slice argument below. A cubic partner exists exactly when L_3(f) is singular, that is, when B=6A^2.

Let i=(f,f)_4, a covariant of degree 2 and order 4. Then (f,i)_5 is an invariant of degree 3, and (f,i)_3 is a covariant of degree 3 and order 4. The Cayley-Sylvester counts `covariant_count(6,3,0)` and `covariant_count(6,3,4)` are both 0, so both vanish identically. Thus i lies in ker L_4(f) for every sextic. It is active exactly when (f,i)_1 is nonzero.

## Strata as invariant loci

For g in GL2, transvectants satisfy (f∘g, h∘g)_k = det(g)^k (f,h)_k ∘ g. Hence ker L_N(f∘g) = (ker L_N(f))∘g, and the same holds for ker P_N. So kernel and active dimensions are functions on GL2-orbits. On a family, every stratum is therefore a union of fibres of the invariant map. If a weighted-homogeneous polynomial R(A,B,C,D), written as a polynomial in the family parameters, reduces to zero modulo a Groebner basis of a curve's ideal, then R lies in that ideal and vanishes at every point of the curve. Relations that vanish on the whole family are discarded, so a returned relation is specific to the curve. For squarefree sextics, two forms with equal points (A:B:C:D) in weighted projective space P(1,2,3,5) lie in one GL2(Qbar)-orbit, by the classical theory of genus-two curves. The test I_i^{w_j}J_j^{w_i}=J_i^{w_j}I_j^{w_i} is that equality, written without roots.

## Slice certificates for covariant identities

Let P(f)=Q(f) be an identity between covariants of the same degree d, order and weight, built from transvectants and invariants. The set of sextics where it holds is Zariski closed and GL2-stable. Every sextic with three distinct roots can be moved by GL2 over the algebraic closure to c·xy(x-y)(x^3+px^2y+qxy^2+ry^3). Scaling absorbs c, because both sides have the same degree. These slice forms therefore have a dense GL2-orbit, and the identity holds everywhere once it holds on the slice. On the slice, the coefficients of f are affine in (p,q,r), so P-Q is a polynomial of degree at most d in each of p, q and r. A polynomial with that bound that vanishes on {0,...,d}^3 is zero. `grid_certificate` evaluates the identity at those (d+1)^3 points in exact arithmetic. It certifies:
- the cubic partner theorem, with d=4 and 125 points;
- the quartic covariant partner, with d=3 and 64 points;
- the degree-12 identities, with d=7 and 512 points. Here s=A^2-25B/96, and (f,G)_3=-432 s (f,(f,f)_2)_1 and (f,G)_5=25920 s (f,(f,f)_4)_1, for G=144A^2f^2+(216/5)A iH+24A f(f,i)_2-(9/4)i^3-9 Delta H+(f,i)_2^2.

The degree-12 identities show that on the hypersurface A^2=25B/96, G(f) lies in ker L_12(f) whenever it is nonzero. The converse, that a degree-12 partner forces A^2=25B/96, is supported by random sextics and by two independent families, but is not proved.


---

# Historical results and extended recovered leads

This appendix preserves quantitative reports and older leads that would otherwise disappear behind a thematic synthesis. They are not freshly validated release results. Conflicting figures are version/window-dependent records, not values to average together.

| Program | Retained report | Interpretation and boundary |
|---|---|---|
| Flux V11.4 | Raw1<=F^T Sigma H<=28 space countably infinite | A charge bound alone did not make the search finite |
| Flux V11.5 | Positive Hodge/ISD candidate superset2,161,623,747,116,044 | A bounded candidate population, not a count of accepted physical vacua |
| Flux V11.8 | Negative D_tau34,669,605,175,703; positive34,328,024,267,279; ambiguous132,547,207,891,982 | Exact reported partition of the declared Hodge-core domain |
| Flux D_x | Excluded27,087,102,294,311; positive remainder7,240,921,972,968 | Successive arithmetic/analytic exclusions with original conventions |
| Flux exclusion floor |93.53318864804987% | Reported global floor for that defined population |
| Early PerfectPower |19complete hit certificates;138audited declarations | Early snapshot, not total release0.1.0 proofs |
| OEIS |399,744index entries;5,617full sequence files | Historical ingestion scope |
| D89 Mordell | Integral points(5,+/-6) on y2=x3-89 | Reported complete case with its retained premises |
| D89 unit enumeration |2,548,975box triples;33,217slab points | Computational cost data |
| D45 |229seconds->75seconds | Same historical optimization context |
| Unit-order pricing |88needed equations,32orders,27priced | Incomplete cost atlas;D39~1900,D60~4000 |
| Early release |1355audited declarations;0lint errors in2232 | Historical checking snapshot |
| Geometry |8emitted Lean examples | Source verification boundary distinct from generic graph proof |
| SOE |324models;384declarations in a reported build | Upstream formal history, not newly checked Lean |
| Saturation census |457backend ranks;365matching witnesses,then452/457 | Changing dated snapshots;full integral completeness separate |
| Later census |Computational closure of former457frontier reported | Rank upper bound/saturation/enumeration trust obligations remained |
| DynaComp heat earlier |200->8, bound.000308,~43x repeated execution | Different earlier benchmark context than later5.89x report |
| DynaComp PDE |84->4,bound.002705,~15x | Construction/replay cost and model conditions retained |
| DynaComp stability search |73seconds->1.21seconds | Particular certification search |
| Heat rod |64modes->3states,<.01over20samples,roundoff~1.2e-15 | Finite horizon and execution assumptions |
| Descriptor extension |Version0.12.0,229tests,200->9,bound.003483,4.50x | Sample range beyond supported region uncertified |
| Wall profile |Uniform field error<8.05e-7 | Specific whole-line model enclosure |
| Thermal wall |Bulk140.26646GeV;wall140.27509GeV;window~8.63MeV | Model thermal ordering, not an empirical phase measurement |
| Thermal example |At140.27146GeV,wall-center Higgs~2.48GeV,bulk0 | Model result |
| Wall formation |84ensembles;density exponent-.218,bootstrap[-.290,-.151] | Finite reduced2D experiment |
| GW network |Late exponent~.25,K~1.95,collapse~1.5xenergy,efficiency~.7 | Finite-box/network assumptions |
| GW peak |Omega h2~1.6e-12 at~2.7nHz | Model extrapolation with unresolved physical scope |
| DAT |437tests,74certificates,14saved seams~16.6repeats | Model-level cost accounting |
| DBD coupled block |672targets;local residual~1.1;recognition0/48 | Open spinor component, not solved coherence |
| Shadow-Core |28atlas rows,9fields,22branch-robust/5shape-transform/1embedding | Historical atlas classification |
| Shadow-Core p-adic |v(Reg)=3,v(Cblock)=4 | Original prime/uniformizer choices essential |
| Morphonic cubic front end |349irreducible-cubic curves,383x-theta classes,128sampled images | Samples were not complete local Kummer images |
| Morphonic integrity |1370/1370,64clean-room checks,9attacks,9causal kills reported | Historical integrity suite;not a new formal theorem |
| Graph sampling |Orders2..64,504samples | Retained workload |
| Sequence library |52families,residues at index10^100 | Supported family library, not all sequences |
| Experiment design |100->2 in a retained task | Exact task-specific optimality |
| Public-prompt benchmark |512tasks;128/128held-out tests reported | Family split/workload qualification |
| Industrial portfolio |570versus584solved;42.1%more summed time;0conflicts | Explicit negative performance result |
| NFL movement |Future-speed MSE improvements33.36%/26.59% | Not established Combine-outcome or betting edge |
| STRING/Pokepolis |68->34,8->4,6912routes,232battle replays | Declared symbolic/phase models |
| Art scope |151procedural rigs,1812property combinations | Visual implementation report, not complete original game content |

Additional recovered mathematical leads include the January thermal curvature diagnostic f(t)=F(e^t),V=Var_t f,K=sup abs(f''),and proposed limit invariant[(a_N*,c_N*,V_N*,K_N*,R_N*)]. Distinct versions used log residual variance instead of purity variance; their objectives must remain separate. The historical spectrum claims favoring a~2/3 versus1/4 are not supported as universal by the clipping-sensitive numerical tables.

The April graph-cycle construction proposed T_C(F_G)=sum_e partial_{xi_e}J_{C,e},P_C=T_C(F_G)/F_G,E[P_C]=0,G_CD=E[P_CP_D],with claimed Gram-rank reconstruction. The cycle polynomials and distributions were not recovered completely. It is a lead,not an implemented result.

A July shifted-Xi program proposed Theta_alpha(z)=Xi(z-i alpha)/Xi(z+i alpha) and kernel K_alpha(z,w)=(1-Theta_alpha(z)conj(Theta_alpha(w)))/(i(conj(w)-z)),with a negative-square invariant and an RH equivalence claim. The original analytic hypotheses,normalization,and proofs were not recovered sufficiently to promote that claim. Its prime-phase derivative proposal was -2sum_{k>=1}(log p)p^{-k(1/2+alpha)}cos(kE log p),and it explicitly distinguished an unconditional alpha>1/2 starting region from the hard boundary. This is preserved as an unresolved spectral-number-theory direction;PerfectJet claims no RH proof.

SYMMETRON's archived L-value proposals included alpha=L(E,1)/(2pi),beta=L(f,3/2)/pi^(3/2),kappa=L'(g,1)/L(g,1),C=int_[X_M]^vir ch(E_6A)Td(T_XM),and an asserted alpha beta kappa2 Delta(i)/(2pi)^12=1. The underlying E,f,g,X_M were not recovered with enough specification. These are historical assertions,not determined constants or proved identities. The Moonshine decomposition/umbral Hamiltonian and higher-genus corrections likewise remain proposals without complete construction.

The early MEF fan-law log10 N_h~4.33h-.28,Padovan dimensions d7=3,d12=12,and waste estimates3.57e29/3.98e50 were assistant-authored historical claims. Some records instead used N_h~4^h,an incompatible scale. They are not reconciled into one theorem. The subdivision weight display alpha_n=1-7/(4n),beta_n=3/(2n),gamma_n=1/(4n) needs the full stencil and aggregation convention. Six-Kernel Covenant examples were mock kernels;51,584-dimensional residue/projection claims andmaster.txtdescriptions were not backed by recovered full source.

The Finsler LC examples used L=.2H,C=1.5nF,impedance about11.5kOhm,resonance about9.2kHz;one other fit used7.5e-10F anddrive5.8kHz. These are different circuit descriptions. Noise conventions,escaperate prefactors,and mappings to a Finsler metric need explicit derivation.

This appendix is a preservation layer. New work should select a precise source object, recover its missing definitions, and then implement or prove the claim. The master does not make an unsupported historical number reliable merely by cataloguing it.


---

# Combine motor transfer and the scouting test

PerfectJet 0.11.0 preserves the complete previous NFL research package and implements a new experiment aimed at the actual scouting outcome. **No new real-data predictive gain is reported.** The recovered package excludes the nine raw competition CSVs; the official API requires authentication and the browser remains signed out. Analytic examples and fixture tests establish code behavior, not football advantage.

The official Kaggle dictionary defines `player_get_off` as seconds from the snap until the defensive rusher moves forward across the line of scrimmage. It is not pure reaction time. The source is https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/data, inspected October 14, 2026. The latest recovered canonical research commit is `2d2fc62af6502618821de23ddaf15e68cdb16a3e`; its original monograph, nine notebooks, aggregate receipts, vendor licenses and history bundle are preserved in `research/nfl_bdb_2027`.

## Evidence carried forward

The canonical audit reports 74 defensive-front rookies, 14,665 eligible NFL records and 582 angular-progress turns. A 34.1% sensitivity reduction is measurement stability. About 93.2% of individual player/drill panels cannot identify the four-coefficient bilinear response. Twelve overlapping duration-model partitions give four gains, two fallbacks, six losses and mean relative gain −0.13%. Pooled get-off's exploratory 2025 gain 2.72% is unstable; 11 of 64 fixed-configuration training-subset refits improve. These are recovered receipts, not new raw-data reproductions. Failed and adaptive stages remain intact.

The new adapter defines its prospective cohort by Combine position, which may differ from the historical NFL-position cohort. It must report counts rather than automatically claim reproduction of 74 players. All 15 conventional measurements enter the stronger baseline. NGS grades use an explicit pre-draft interpretation; exact chronology remains unverified. Physical availability dates are proxied by observed Combine tracking dates. A no-NGS comparison is a sensitivity, not a substitute headline.

## Target-relative mathematics

Let total LOS time be $t=\tau+u$, onset plus travel. Its observation row is $X=(1,1)$, with hidden witness $n=(-1,1)$. Then $Xn=0$ but$(1,0)n=-1$: total time cannot identify either component. This is PerfectJet's exact linear readout theorem, not a physiological claim. Under the separate local model$d=vu+au^2/2$, the stable root is

$$u(d,v,a)=\frac{2d}{v+\sqrt{v^2+2ad}},\qquad d,v\ge0,\quad a>0.$$

At distance 1 yard, initial speed 0 and total time 1 second, onset$1/5$ with acceleration$25/8$ and onset$3/10$ with acceleration$200/49$ give the same total. The receipt replays both rational identities. This nonlinear nonuniqueness counterexample stays separate from the linear nullspace theorem. Travel increases with distance and decreases with speed/acceleration. `crossing.travel_time_bounds` uses these corner extrema over a declared box, checking outward endpoint polynomial signs exactly. It bounds the specified model, not sensor error or physiology.

The new source readout is

$$A_T=\frac{2}{T^2}\int_0^T[v(t_0+t)-v(t_0)]dt
=\frac{2}{T^2}[x_\parallel(t_0+T)-x_\parallel(t_0)-Tv_\parallel(t_0)],\quad T=0.5\mathrm{s}.$$

It equals acceleration for quadratic motion and otherwise weights acceleration by$2(T-t)/T^2$. It requires no second numerical differentiation. A causal trailing three-frame derivative avoids forward-difference acceleration bias. Extraction requires recorded launch history and sustained onset; it rejects a curved first start rather than searching for a favorable later window. Rotation,translation,irregular-time analytic motion and missing-history rejection are tested. The operational onset has no known Combine start cue.

Primary extraction uses forty-yard starts. A separately declared secondary family uses the same functional on the four front-drill starts, with training-only drill and conventional nuisance adjustment. Smoothing variants remain sensitivity scenarios; they never count as independent attempts.

For source-reference residuals$x_{ij}=z_i+\epsilon_{ij}$, the scalar Gaussian model assumes$z_i\sim N(0,\tau^2)$ and drill variance$\sigma_d^2$ learned from actual training-player repeats. Its posterior is

$$V_i=(\tau^{-2}+\sum_j\sigma_{d_j}^{-2})^{-1},\qquad m_i=V_i\sum_jx_{ij}\sigma_{d_j}^{-2}.$$

No repeat evidence produces an unavailable readout, not perfect reliability. Sparse drills may use explicitly labeled pooled repeat variance. Common player deviation across drills, independent attempt errors and transferable variance are assumptions. Branch width is never substituted for Gaussian noise.

The NFL correction integrates source uncertainty:

$$r_i\mid D_i\sim N(\lambda m_i,\sigma_{NFL}^2+\nu_i^2+\lambda^2V_i).$$

Here$r_i$ is an out-of-player baseline residual. The descriptive$\nu_i^2$ uses game-cluster sums for the same play-weighted residual mean: with$G_i>1$ games and$n_i$plays, it is$G_i/(G_i-1)\sum_g[\sum_{p\in g}(r_{ip}-\bar r_i)/n_i]^2$. It omits context-reference uncertainty. Full pipeline refits address additional fitting variability. The scalar loading sees training outcomes only. Missing source information gives zero athlete-specific correction. This is materially different from estimating four unsupported coefficients.

## Validation and decisions

Both models receive all 15 conventional measurements,training-imputed missingness,Combine position,and identical raw drill flags/counts. NFL geometry defines labels only. Context adjustment includes depth,width,speed,formation,alignment and situation,with square-root/log depth terms motivated by travel. Training labels are cross-fitted by player; evaluated labels use the training reference. Every inner split rebuilds targets,source nuisance,repeat variance,imputation,scaling and models. Loading-residual folds also rebuild their context targets. Training NFL seasons precede the evaluated class; labels are rookie REG observations.

The fixed ridge grid is 10, 100, 1000 with three inner player folds and identical selection budgets. The primary metric is equal-athlete$G=1-MSE_{movement}/MSE_{baseline}$,with paired losses,source coverage,class results and player influence. Bootstrap draws preserve class sizes and group every copy by the original player. The default requests 64 complete source/context/selection refits. Their percentile intervals remain exploratory; they do not undo prior adaptive data use. Inspected 2025 cannot become a fresh holdout.

The separate NFL crossing extractor reconstructs thresholded onset,onset-to-LOS travel and half-second movement,flagging missing intervals,recrossing and anticipation. These are mechanism diagnostics. They must not replace a failed get-off result with a new headline. A fixed-budget shortlist comparison is needed before declaring improved scouting decisions. No betting advantage or causal development effect follows.

## Execute on official inputs

Use Python 3.12 and a private raw-input directory outside the checkout:

```bash
python -m pip install -e '.[scouting]'
perfectjet nfl-burst --data /path/to/official-nine-files --out /path/to/private-nfl-run --verify-known-hashes --refits 64
perfectjet nfl-burst --data /path/to/official-nine-files --out /path/to/private-nfl-no-ngs --verify-known-hashes --without-ngs --refits 64
```

Private results retain individual predictions and tuning choices. Aggregate output removes predictions and influence identities. Missing files cause a named-file error; the command has no synthetic fallback. `notebooks/PerfectJet_Motor_Transfer.ipynb` embeds the source and expects attached official data; it remains unexecuted until raw inputs exist. Fixture success is never a new NFL result.

## Corrections from the release audit

Independent rational approximations of standardized float coordinates broke bilinear dependencies: same-speed designs could have rank 3 instead of 2,and empirical demand averages sometimes failed identification from their own complete rows. The fixed gate forms raw rational$[1,s,a,sa]$ and exact cell-count averages. Bootstrap copies now share original-player folds; late events cannot alter predictors or availability; real drill indicators replace synthetic names; inner fitting is fully rebuilt; future NFL seasons cannot train historical folds; higher-is-better shortlists use the correct quartile. The inherited synthetic-first detector remains distinct from the older angular-progress detector,so 34.1% is not silently credited to this new code.

The empirical conclusion remains unresolved: does the supported motor readout improve get-off and player decisions? The release makes that test executable and preserves honest failures. Exact algebra and synthetic recovery cannot answer it without running the actual NFL inputs.


---

# From predictive movement to scouting decisions

PerfectJet 0.12.0 connects the representation program to a concrete pre-draft question: can measured Combine movement improve the prediction of rookie NFL snap-to-line-of-scrimmage get-off, beyond the full conventional information available for the same prospects? The implementation connects operational movement targets, finite-horizon predictive states, player-cross-fitted transfer, and exact target-directed measurement packages. It preserves the original atlas, every preceding release, and the recovered NFL work. This is an implemented research bridge; a new empirical scouting advantage remains unestablished until the official inputs are executed and independently validated.

The prior study matters because it prevents a false restart. Its launch/turn extraction became more stable, while several downstream models failed to deliver stable scouting lift. A representation can improve its own numerical behavior without improving a football decision. The present bridge therefore has separate movement, transfer, prediction, and decision receipts. A positive result in one cannot substitute for another.

## The mathematical chain and what each link preserves

Let $B_i$ be the fifteen conventional measurements, Combine position, and observed drill availability for prospect $i$. Let $X_i$ be a causal history of that prospect's Combine movement. Let $q_i$ contain declared NFL movement readouts, and let $y_i$ be context-adjusted rookie snap-to-LOS get-off. The proposed connection is

$$X_i \longmapsto \widehat q_i=f_{\mathcal T}(B_i,X_i)
\longmapsto \widehat y_i=g_{\mathcal T}(B_i,\widehat q_i).$$

The training set $\mathcal T$ includes only eligible past players. NFL context and tracked NFL movement define the training targets; prospect prediction uses Combine information. All physical readouts keep declared units. No raw SVD coordinate is treated as an invariant athlete trait.

| Research family | Executable connection | Preserved quantity | Limit of the connection |
|---|---|---|---|
| Observability and hidden witnesses | LOS decomposition and exact linear readout tests | Whether a specified question is determined by available measurements | An exact rank test is conditional on the declared linear response model |
| Finite jets and calculus | Causal position derivatives and the post-onset burst functional | A finite time and directional movement readout | Operational onset is a tracking proxy; no physiological reaction time is inferred |
| Hankel and predictive state | Supervised delay-block continuation with player-held rank/history selection | Physical movement outputs over a fixed finite horizon | Numerical reduced-rank prediction does not prove an exact all-future realization |
| Transport and reconstruction | Fixed-unit Combine-to-NFL target maps | An explicit movement target and its reconstruction into get-off prediction | A shared coordinate system does not prove cross-domain transport |
| Closure and obstruction | Continuation residuals, unsupported histories, unavailable movement targets | A failure witness and its scope | A suggested residual repair must be fitted and validated again |
| Compositional error | The actual fitted two-stage decoder's error decomposition | Where prediction error enters the chain | A deterministic scenario bound is separate from empirical uncertainty |
| Gaussian information | Exact scalar and correlated-block posterior updates | Conditional uncertainty in a frozen scouting readout | Prior, noise and fitted loading uncertainty are assumptions, not established physiology |
| Finite populations | Exact counting, ranking and joint package optimization | Original feasible measurement packages and ties | Exhaustive global optimality is for the declared finite candidate universe |
| Certified decisions | Bound-separated winner and overlapping contenders | A decision under supplied valid bounds | NFL sampling uncertainty is retained separately |
| Arithmetic geometry, lattice and invariant theory | Retained core and atlas; no forced athlete analogy | Exact arithmetic claims in their original domains | No evidence currently justifies inserting Pell or sextic features into scouting |

This is a stronger reuse of the existing mathematics than an indiscriminate feature expansion. Arithmetic geometry remains a central part of the broader research program. In this application, the useful bridges are those whose inputs, outputs and assumptions match the scouting question.

## Get-off is a sum with a hidden direction

The official get-off variable measures the elapsed time from snap to crossing the line of scrimmage. For an observed post-snap operational onset $t_o$, crossing $t_c$ and snap $t_s$,

$$y_{\rm tracked}=t_c-t_s=(t_o-t_s)+(t_c-t_o)=\tau+T_{\rm travel}.$$

This identity explains the original underidentification. An observation row $X=(1,1)$ cannot determine the onset component $h=(1,0)$: the hidden direction $n=(-1,1)$ satisfies $Xn=0$ while $hn\ne0$. Two athletes can have identical get-off and different onset/travel decompositions. Additional rows resolve that ambiguity only if they measure the target-affecting hidden direction. More repetitions of $(1,1)$ increase precision but leave this structural gap.

`movement_targets.py` reconstructs the geometry with official game/play/player identities. It finds the snap in a first tracking pass, then retains bounded selected-player windows in a second pass. A canonical forward axis points from the defensive start side toward LOS. The implementation rejects nonpositive starting depth; it does not silently take an absolute value and invent a different task. Translation, reflection and rotation tests check the geometry. Gaps, missing snap observations and invalid crossing paths retain failure records and counts.

The supplied official get-off remains the primary outcome even when tracked decomposition fails. The tracked-minus-supplied discrepancy is a diagnostic. The two initial movement readouts are forward displacement over the first operational post-onset half-second, in yards, and motion-onset-to-LOS travel time, in seconds. Onset delay remains a diagnostic rather than a claim about reaction time. Anticipation and pre-snap motion must retain their own flags; an onset already outside the observed window cannot be manufactured from the first available frame.

Player targets use a common set of usable plays for their channel vector. Context adjustment is fitted on training players and cross-fitted for training targets. Neither starting depth nor NFL contextual covariates become prospect predictors. For $G$ observed games and play weights $w_p$ defining the reported player mean, game-cluster uncertainty is

$$S_g=\sum_{p\in g}w_p(z_p-\bar z),\qquad
\widehat{\operatorname{Cov}}(\bar z)=\frac{G}{G-1}\sum_{g=1}^{G}S_gS_g^\top.$$

One game does not estimate this cluster covariance: it produces unknown uncertainty, rather than a falsely precise zero. A thousand frames from one play do not constitute a thousand independent players or a thousand independent measurement attempts.

## A physical source functional before a latent model

The original post-onset Combine source is

$$A_T=\frac{2}{T^2}\left[x_\parallel(t_o+T)-x_\parallel(t_o)-T v_\parallel(t_o)\right],\qquad T=0.5\,\mathrm{s}.$$

For twice differentiable motion this is

$$A_T=\frac{2}{T^2}\int_0^T(T-u)a_\parallel(t_o+u)\,du.$$

It equals constant acceleration for quadratic motion. In general it is a weighted acceleration readout, with no force, power, efficiency or developmental interpretation. Initial velocity is estimated with a trailing causal derivative, and adequate pre-onset history is required. Straightness is tested over the declared source window. Smoothing alternatives represent extraction scenarios; they are never independent repetitions of the athlete.

The new state bridge uses forward and lateral movement channels derived from observed history. Its source feature vector contains half-second forward displacement, terminal forward speed, endpoint directional retention, and physical-coordinate continuation forecasts; the preceding burst functional remains executable in the separate motor-transfer experiment. A forecast origin has a declared time. Frames beyond that origin cannot enter input derivatives, history blocks or source features. The physical forecast itself can extend over the fitted short horizon, but its input stays within the available prefix.

## Predictive state without arbitrary cross-fold coordinates

For channel vector $u_t$, form a history block $p_t=[u_{t-L+1},\ldots,u_t]$ and a future block $f_t=[u_{t+1},\ldots,u_{t+H}]$. Training-only scaling gives matrices $P,F$. The numerical continuation estimator is

$$\widehat K_\lambda=(P^\top W P+\lambda I)^{-1}P^\top W F.$$

The fitted future matrix $P\widehat K_\lambda$ is compressed through its right singular vectors. If $V_r$ contains the retained output directions, the state and physical forecast use

$$z_t=p_t\widehat K_\lambda V_r,\qquad
\widehat f_t=z_tV_r^\top,$$

with the fitted centering and inverse scaling restored in code. History length, rank and ridge penalty are selected by whole-player inner validation on common forecast origins. The instantaneous comparison receives those same origins, data weights and declared horizon. Each sampled athlete has equal total weight; bootstrap multiplicity is preserved, while copies remain in their original athlete's fold.

This implements a target-directed delay model inspired by the Hankel program. It does not assert that a noisy finite sample has discovered an exact weighted automaton, a nonlinear sufficient statistic, or an all-time physiological state. The forecast outputs are physical coordinates. A latent basis may rotate across separate SVD fits without changing those coordinates, so the transfer stage consumes physical forecasts rather than concatenating incompatible latent states.

NFL movement histories train the continuation map within each training fold. Applying that map to a Combine history is a declared cross-domain hypothesis. Train-history Mahalanobis and orthogonal-design distances flag unsupported inputs. These distances are descriptive; their training 95th percentile does not become a calibrated prediction interval. An unsupported athlete remains visible in coverage and sensitivity reports. The bridge cannot call an unusual history familiar by refitting on the held-out NFL player.

The analytic receipt uses an explicitly synthetic second-order recurrence to demonstrate why history can matter. Two histories with the same current sample can have different continuations. A history model can distinguish them, while an instantaneous model cannot. This establishes the implemented mechanism on the fixture; it establishes no NFL performance improvement.

## Train the decoder on the predictions it will actually receive

A frequent two-stage error is to train a football decoder on true NFL movement and then deploy it on noisy Combine-derived movement estimates. That changes its input distribution. The implemented bridge instead trains its decoder with player-out-of-fold movement predictions:

$$\widehat q_i^{\rm OOF}=f_{\mathcal T\setminus\mathcal F(i)}(B_i,X_i),\qquad
\widehat g=\arg\min_g\sum_{i\in\mathcal T}
\left[y_i-g(B_i,\widehat q_i^{\rm OOF})\right]^2+\alpha\|g\|^2.$$

Each stacking fold rebuilds the movement representation, context targets, source reference, preprocessing and transfer map using its training players. The final first-stage map is refitted on the outer training set and then feeds the frozen decoder for outer held-out prospects. Tuning occurs inside the outer training population. Athlete labels and NFL trajectories from the outer evaluation class enter scoring and post-prediction diagnostics only.

The comparator receives all fifteen conventional measurements, position and identical drill availability. Any derived source coverage/support flags are shared with it, so a comparison cannot attribute missingness or attendance information to movement values. Missing trajectories remain missing. Eligibility dates, rookie seasons and training outcome cutoffs are enforced. Held-player perturbation tests change NFL labels and trajectories and check that fitted prospect predictions remain fixed.

Temporal comparisons on previously inspected classes are development evidence. In particular, a newly packaged model cannot restore untouched status to 2025 merely by renaming an analysis. The primary headline remains supplied snap-to-LOS get-off. A useful onset or displacement result can be reported as a mechanism diagnostic without replacing a failed primary result.

## Locate transfer error and ask for the measurement that matters

After predictions are frozen, held-out NFL movement can locate the two-stage error:

$$\widehat y-y=
\underbrace{g(B,\widehat q)-g(B,q)}_{\text{movement transfer error}}+
\underbrace{g(B,q)-y}_{\text{decoder residual}}.$$

This is an algebraic decomposition for the actual fitted decoder. It does not establish causation or identifiability of a biological mechanism. For an affine decoder with loading $w$ and a supplied box $|\widehat q_j-q_j|\le r_j$,

$$|g(B,\widehat q)-g(B,q)|\le\sum_j|w_j|r_j.$$

Those radii must be supplied or validated. A fixed-fit box bound cannot be substituted for uncertain extrapolation, model selection variability, unknown loading uncertainty or NFL sampling error.

For a fixed affine source-to-movement map $q=F x+c$ and decoder $g=w^\top q+b$, the scouting loading on physical source coordinates is $h=F^\top w$. The implementation exposes the fitted finite-difference Jacobian in physical units. Pipeline imputation and missingness make this a local conditional loading: it is not a universal derivative across missing-value boundaries or new support regions.

The allocation bridge takes that frozen loading and a caller-declared prior covariance, measurement noise, candidate constraints and budget. It records training IDs, held-out IDs, cutoff and the loading's declared source. These receipts expose provenance; they do not independently prove that an external caller trained honestly. A floating fitted coefficient can be rationalized within a declared tolerance so the package algebra is reproducible. Exact arithmetic proves calculations for that rational snapshot, rather than proving that an estimated loading is exactly correct. The allocation wrapper also bounds the effect of coefficient rationalization over every feasible package, so a reproducible approximation comes with an optimization-error receipt.

With prior covariance $\Sigma$, loading $h$, measurement row $e$ and independent noise variance $s^2$, the update is

$$\Sigma' = \Sigma-
\frac{\Sigma e e^\top\Sigma}{s^2+e^\top\Sigma e},\qquad
\operatorname{VOI}(e)=h^\top(\Sigma-\Sigma')h.$$

Several correlated channels from one attempt use the block update

$$\Sigma' = \Sigma-\Sigma E^\top(R+E\Sigma E^\top)^{-1}E\Sigma.$$

The channel block is one candidate with one cost and its full noise covariance. Duplicate original attempt IDs are rejected. Repeating an independent attempt may improve precision; splitting its frames into fictitious independent observations may not. Irreducible NFL outcome noise and uncertainty in the fitted loading are outside this conditional source-covariance reduction and must remain visible.

If $D_S=\Sigma-\Sigma_S$ is the covariance reduction for a package, then $0\preceq D_S\preceq\Sigma$ and $|(D_S)_{ij}|\le(\Sigma_{ii}+\Sigma_{jj})/2$. A raw decimal loading $h$ and rational snapshot $\widetilde h$ therefore satisfy

$$|h^\top D_Sh-\widetilde h^\top D_S\widetilde h|\le
\sum_{i,j}|h_i h_j-\widetilde h_i\widetilde h_j|
\frac{\Sigma_{ii}+\Sigma_{jj}}{2}=\epsilon.$$

The bound is uniform over the declared candidate packages. The package optimized for the rational snapshot has raw-snapshot regret at most $2\epsilon$, including for the minimum over a declared loading family. This controls arithmetic approximation in the optimizer; it does not control errors in the fitted hypothesis, prior or noise model.

## A concrete new exact result: isolated-value greedy allocation can fail

The allocation receipt gives a small exact counterexample. Take $\Sigma=I_2$, $h=(1,0)$, budget two and unit candidate costs. Let A measure $(1,0)$ with noise variance one, B measure $(1,1)$ with noise variance $1/10$, and C measure $(0,1)$ with noise variance $1/10$.

| Candidate or package | Conditional variance reduction in the target |
|---|---:|
| A alone | $1/2$ |
| B alone | $10/21$ |
| C alone | $0$ |
| Greedy package A+B | $21/32$ |
| Globally best package B+C | $110/131$ |

The zero-isolated-value measurement C estimates the nuisance coordinate contaminating B. Together B and C recover the target far more precisely than the isolated-value ordering suggests. The difference is $769/4192$. Target-specific variance reduction is monotone but need not be submodular: the marginal value of C is zero at the empty package and $110/131-10/21=1000/2751$ after B. This violates diminishing returns, so additive-profit models and the usual submodular greedy guarantees do not apply. This is an exact linear-Gaussian counterexample, not a newly observed NFL benefit. It directly justifies optimizing packages jointly instead of sorting candidates by standalone value.

The existing finite-population core counts and ranks the original feasible subsets; the allocation layer evaluates each joint posterior. For at most eighteen candidate packages the implementation provides a global optimum, tie count and feasible population receipt. Larger candidate universes require a separately declared search procedure; the bounded exhaustive routine does not silently claim scalable global optimality.

Multiple plausible frozen loadings can be supplied. A robust objective maximizes the minimum variance reduction over that declared hypothesis family. If the family contains a zero source loading, its worst-case reduction is zero: a source-only measurement cannot guarantee value when an admissible fitted hypothesis gives the source no scouting effect. Weighted-mean optimization is a separate declared alternative, with explicit weights rather than an implicit uniform biological prior.

## Decide which comparisons are still worth resolving

For a higher-is-better score with valid fixed-fit bounds $[L_a,U_a]$, candidate $a$ is certified ahead when $L_a>\max_{b\ne a}U_b$. The get-off target is lower-is-better, so the direction must be transformed consistently before using that comparison. A fixed budget or roster constraint remains explicit.

When the winner is unsettled, measurement can target score differences $H_a-H_b$ for overlapping contenders. Resolving an irrelevant athlete's complete parameter vector can consume budget without changing the decision. The contender allocator targets those score differences. When source uncertainties are correlated, a measurement on another athlete can still resolve a contender comparison; the exact joint search retains such candidates, including measurements with zero isolated benefit. Empirical uncertainty can be attached to the decision report, but is not silently reclassified as a proved scenario bound.

The full scouting assessment still needs equal-player paired prediction loss, calibration, coverage, class-by-class behavior and the fixed-budget shortlist. A representation should earn its place by improving these outcomes against the comparably informed baseline. Selection must be frozen before evaluating the class. Repeated refits test instability; they do not erase adaptive use of an already inspected class.

## Execution and evidence

Install the scouting extras. Run `perfectjet math-bridges --output results/math-bridges.json` for the analytic and exact receipts without raw football data. Run `perfectjet nfl-bridges --data OFFICIAL_DIR --output private_results/bridges.json --verify-known-hashes --refits 64` for the official-data experiment and full original-player pipeline refits. The primary comparison uses the stronger of direct conventional and conventional two-stage decoding, selected within training-player validation. Both individual comparisons remain available. The bridge notebook embeds and hashes the actual repository modules and refuses a synthetic fallback when official inputs are absent.

The official experiment needs `players.csv`, `combine_results.csv`, `combine_tracking.csv`, `player_play.csv`, `games.csv`, `player_career_successes.csv` and game-tracking files for 2023, 2024 and 2025. Their absence blocks empirical execution, rather than implementation, analytic verification or package publication. The released notebook is explicitly unexecuted on those raw inputs.

The strongest completed result is a connected, falsifiable computation: physical targets, causal finite-history predictions, out-of-player transfer, a decoder trained on those actual predictions, an exposed physical loading, and exact measurement packages directed at that loading. The next empirical question is whether this chain improves football predictions and decisions. A negative result should identify whether the loss occurred in source coverage, finite-history forecasting, Combine-to-NFL transport or decoding, and remain in the permanent research record.


---

# Complete equation registry

Status describes the evidence available in this repository. Exact checking is not Lean verification.

| ID | Domain | Title | Equation | Status | Assumptions and limits |
|---|---|---|---|---|---|
| PJ-E001 | arithmetic | perfect-power equation | S(n)+k=m^d | definition | Integer polynomial S; integer n,k,m; d>=2. |
| PJ-E002 | arithmetic | hit count | A_{F,d}(N)=#{n in N:n<=N, exists m in Z:F(n)=m^d} | definition | Positive inputs; existential m avoids double-counting signed witnesses. |
| PJ-E003 | arithmetic | hit density | H_d^S(k)=limsup_{N->infinity} A_{S+k,d}(N)/N | definition | Density claim depends on the sequence class. |
| PJ-E004 | arithmetic | polynomial identity case | S(x)+k=G(x)^d | derived | G in Z[x] supplies a hit at each positive input. |
| PJ-E005 | arithmetic | historical geometric exponent | e=gcd(d,m_i); A(N)=O(N^(e/d+epsilon)) | historical_report | Multiplicity notation and hypotheses must be restored before using this bound. |
| PJ-E006 | arithmetic | growth taxonomy | bounded; c log N+O(1); c sqrt(N)+O(1); N | historical_report | Retained square-hit classification; not a universal classification of every sequence. |
| PJ-E007 | arithmetic | Mordell curve | y^2=x^3+k | definition | Rational group structure and integral completeness are separate questions. |
| PJ-E008 | arithmetic | generalized Pell | y^2-Dx^2=N_0 | definition | Nonsquare D>0 for standard unit-orbit analysis. |
| PJ-E009 | arithmetic | triangular reduction | (2y+1)^2=8F(n)+1 | derived | Equivalent to y(y+1)/2=F(n) with odd-square reconstruction. |
| PJ-E010 | arithmetic | completed square | (2y+1)^2=4F(n)+1 | derived | Equivalent to y^2+y=F(n). |
| PJ-E011 | arithmetic | quadratic discriminant | Delta(n)=b^2-4a(c-F(n)); y=(-b +/- sqrt(Delta))/(2a) | derived | a nonzero; discriminant square AND numerator divisible by 2a. |
| PJ-E012 | arithmetic | coefficient power chart | 2x^2=3y^3; x=+/-18t^3,y=6t^2 | derived | Integer parametrization; retain signs and t=0. |
| PJ-E013 | arithmetic | cusp power chart | x^2=y^3; x=t^3,y=t^2 | derived | Integer t carries the sign of x. |
| PJ-E014 | pell | quadratic norm | N(x+y sqrt(D))=x^2-Dy^2 | derived | Quadratic extension convention. |
| PJ-E015 | pell | unit orbit | x_j+y_j sqrt(D)=alpha epsilon^j | historical_report | Seed inventory and index domain must be complete. |
| PJ-E016 | pell | unit matrix | [x';y']=[[a,Db],[b,a]][x;y] | derived | epsilon=a+b sqrt(D); multiplication identity. |
| PJ-E017 | pell | sqrt2 hit recurrence | n'=3n+2m; m'=4n+3m; m^2-2n^2=1 | derived | A single orbit step; seeds/domain still matter. |
| PJ-E018 | pell | Pell7 | x^2-2y^2=-7 | derived | Equivalent to (x^2+7)/2=y^2. |
| PJ-E019 | pell | orbit coordinate | X_j=(eta epsilon^j+(Delta/eta)epsilon^(-j))/2 | historical_report | Original seed/norm convention required. |
| PJ-E020 | pell | input asymptotic | n_j=eta epsilon^j/(4A)-B/(2A)+O(epsilon^(-j)) | historical_report | Original quadratic pullback coefficients required. |
| PJ-E021 | pell | filtered orbit population | A_orbit(N)=g log(N)/(pi_period log(epsilon))+O(1) | historical_report | Reachable cycle with period pi_period and g admissible positions. |
| PJ-E022 | pell | filtered infinitude | reachable admissible cycle iff infinitely many admissible orbit hits | historical_report | For retained finite-state orbit encoding, not arbitrary automata. |
| PJ-E023 | pell | unit identity | (1+sqrt(2))^6=99+70sqrt(2) | derived | Exact binomial expansion. |
| PJ-E024 | descent | general Weierstrass | y^2+a1xy+a3y=x^3+a2x^2+a4x+a6 | definition | Nonsingular elliptic model when discriminant nonzero. |
| PJ-E025 | descent | Weierstrass coefficients | b2=a1^2+4a2; b4=2a4+a1a3; b6=a3^2+4a6 | definition | Standard model coefficients. |
| PJ-E026 | descent | square completion | (2y+a1x+a3)^2=4x^3+b2x^2+2b4x+b6 | derived | Direct polynomial identity. |
| PJ-E027 | descent | two-torsion cubic | psi2(x)=4x^3+b2x^2+2b4x+b6 | definition | Leading coefficient 4; use monic normalization for the norm. |
| PJ-E028 | descent | cubic discriminant | disc(psi2)=16Delta_E | derived | Standard discriminant normalization. |
| PJ-E029 | descent | cubic etale norm | N(x-theta)=((2y+a1x+a3)/2)^2 | derived | theta is root of monic psi2/4; norm-square is necessary, not sufficient for Selmer membership. |
| PJ-E030 | descent | squareclasses | L^*/L^(*2) | definition | Product algebra when cubic splits; do not silently assume a field. |
| PJ-E031 | descent | local Kummer condition | loc_v(alpha) in image(delta_v) | definition | Actual complete local images, not sampled signatures. |
| PJ-E032 | descent | Selmer intersection | Sel2={alpha in appropriate global squareclasses:loc_v(alpha) in image(delta_v) for all v} | definition | S-unit/class-group/norm conditions must also be supplied. |
| PJ-E033 | descent | unit-class sequence | O_{L,S}^*/O_{L,S}^{*2}->L(S,2)->Cl(O_{L,S})[2] | historical_report | Recover exact sequence conventions before downstream proof. |
| PJ-E034 | descent | Selmer exact sequence | 0->E(Q)/2E(Q)->Sel2(E/Q)->Sha(E/Q)[2]->0 | derived | Standard 2-Selmer interpretation. |
| PJ-E035 | descent | anonymous model | y^2=x^3+2x^2-12x+16 | historical_report | v1.67 report; not imported as a complete descent implementation. |
| PJ-E036 | descent | anonymous field | u^3+8u^2-192u+1024=0 | historical_report | Field discriminant reported -107; polynomial and field discriminants differ. |
| PJ-E037 | transport | affine pullback | F(n)=(rn+s)^3+k | definition | r nonzero for inverse transport. |
| PJ-E038 | transport | transported list | W={((t-s)/r,y):(t,y) in L_k, r divides t-s} | derived | L_k must be complete to conclude complete pullback. |
| PJ-E039 | transport | list contract | m^2=F(n) iff (n,m) in W | conditional | Requires complete source list and preserved domains. |
| PJ-E040 | transport | Thue23 first | -u^3-3u^2v+6uv^2+4v^3=1 | historical_report | Retained descent leaf; all branches/reconstruction needed. |
| PJ-E041 | transport | Thue23 second | -u^3-6u^2v+69uv^2+46v^3=1 | historical_report | Retained descent leaf. |
| PJ-E042 | transport | field621 | theta^3-6theta-3=0 | historical_report | Associated field representation in archive. |
| PJ-E043 | transport | D72 leaf | H(u,v)=-3u^3+9uv^2-2v^3=+/-1 | historical_report | Residual branch, not a closure claim. |
| PJ-E044 | transport | D72 field | beta^3-27beta-18=0 | historical_report | Coordinates and order matter. |
| PJ-E045 | transport | D72 norm | gamma=-3u-beta v; N(gamma)=9H(u,v)=+/-9 | historical_report | Exact identity attached to the selected field/order. |
| PJ-E046 | transport | D72 units | gamma=zeta alpha_j epsilon1^e1 epsilon2^e2 | historical_report | Need representatives and effective global exponent bounds. |
| PJ-E047 | transport | D72 reconstruction | C=0; 3 divides A; u=-A/3; v=-B | historical_report | Coordinate restrictions are part of completeness. |
| PJ-E048 | transport | scaled rational kernel | K=det(BB^T)I-B^T adj(BB^T)B | derived | Full row rank for nondegenerate projector interpretation. |
| PJ-E049 | transport | kernel identities | BK=0; Bx=0 implies Kx=det(BB^T)x | derived | Rational-span statement does not prove integral saturation. |
| PJ-E050 | transport | Smith form | UBV=D | exact_checked | Unimodular U,V; d_1\|d_2\|...; replayed in lattice.py against gcd-of-minors divisors. |
| PJ-E051 | transport | integral solvability | d_i divides (Ub)_i; remaining coordinates (Ub)_i=0 | exact_checked | For Smith form of Bx=b; failure returns a certificate row. |
| PJ-E052 | counting | resource polynomial | P(z)=product_j(1+product_k z_k^{c_jk}) | derived | Nonnegative integral costs; extra compatibility requires extra factors/state. |
| PJ-E053 | counting | capacity population | #F=sum_{a<=b}[z^a]P(z) | derived | Componentwise capacity bound. |
| PJ-E054 | counting | profit polynomial | P(z,t)=product_j(1+t^{p_j}product_k z_k^{c_jk}) | proposal | Laurent t exponents if profits negative. |
| PJ-E055 | counting | completion recurrence | C(q)=C(q0)+C(q1) | exact_checked | Disjoint binary prefixes; populations.py and exhaustive comparisons. |
| PJ-E056 | counting | terminal count | C(q)=1 if complete and feasible else 0 | exact_checked | Original objects counted once. |
| PJ-E057 | counting | ranking | rank(x)=sum_{i:x_i=1} C(x_<i 0) | exact_checked | Lexicographic original project order. |
| PJ-E058 | counting | unranking | r<C(q0):choose0; else choose1 and r<-r-C(q0) | exact_checked | 0<=r<C(q). |
| PJ-E059 | counting | uniform sampling | Pr(0\|q)=C(q0)/C(q) | derived | Exact uniformity over original objects, not quotient representatives. |
| PJ-E060 | counting | factor population | Z=sum_x product_j f_j(x_scope_j) | definition | Finite domains and specified weight algebra. |
| PJ-E061 | counting | variable elimination | g(x_rest)=sum_{x_i}product_{j containing i}f_j | derived | No duplicated auxiliary witnesses. |
| PJ-E062 | counting | auxiliary uniqueness | for every original legal x, #{y:encoding(x,y)}=1 | definition | Needed to preserve population under functional encodings. |
| PJ-E063 | counting | Petersen historical total | 702508860122761; optimum=16537; tie_count=1 | historical_report | Upstream retained result; original 50-project data not included here. |
| PJ-E064 | counting | population aggregation | Z_{A disjoint-union B}=Z_A+Z_B; Z_{A times B}=Z_A Z_B | derived | Disjointness / independence essential. |
| PJ-E065 | counting | exponent-pattern polynomial | product_i(1+q+...+q^{a_i}) | definition | Prime-exponent populations. |
| PJ-E066 | counting | power-exponent criterion | d divides gcd(a_1,...,a_s) | derived | Positive integer prime factorization; handle 1 separately. |
| PJ-E067 | series | weighted transfer series | G(z)=H(I-sum_c z^c A_c)^(-1)s | derived | Positive integral costs; finite-dimensional formal series. |
| PJ-E068 | series | resolvent expansion | (I-M(z))^(-1)=sum_{ell>=0}M(z)^ell | derived | M has zero constant term, or other convergence hypotheses. |
| PJ-E069 | series | Fibonacci series | 1/(1-z-z^2) | definition | Initialization determines sequence offset. |
| PJ-E070 | series | zero-series initialization | z/(1-z)=0+z+z^2+... | historical_report | Zero initial sample can change minimal realization size. |
| PJ-E071 | series | linear response | G(z)=C(I-zA)^(-1)B; coefficients=CA^kB | derived | Linear input/output convention. |
| PJ-E072 | series | Hankel matrix | H_{u,v}=f(uv) | exact_checked | Word-indexed predictive state; finite rank over a field; exact on the supplied block only. |
| PJ-E073 | series | linear word realization | f(w)=alpha^T A_{a1}...A_{aell} beta | derived | Minimal field realization dimension equals finite Hankel rank; positivity is separate. |
| PJ-E074 | semantics | semantic fibre | pi:I->S; I_s=pi^(-1)(s) intersect L | definition | Legal implementations of a meaning. |
| PJ-E075 | semantics | cost realization | i*=argmin_{i in I_s}cost(i) | proposal | Minimum must exist or infimum used. |
| PJ-E076 | semantics | future equivalence | x~y iff all finite permitted words have equal behavior | exact_checked | Partial definedness included; finite machine replay. |
| PJ-E077 | semantics | quotient dynamics | qF_a=Fbar_a q | exact_checked | Observation and definedness preserved. |
| PJ-E078 | semantics | quotient observation | O=Obar q | exact_checked | Chosen output family only. |
| PJ-E079 | semantics | completeness | q(x)=q(y) iff x~y | exact_checked | Finite Python quotient, not new Lean theorem. |
| PJ-E080 | semantics | distinguishing word | exists w:behavior(x,w)!=behavior(y,w) | exact_checked | Shortest witness via pair BFS. |
| PJ-E081 | semantics | question refinement | Q subset Q' implies equivalence(Q') subset equivalence(Q) | derived | More questions can only refine the state partition. |
| PJ-E082 | semantics | joint representation | q=(q1,q2) | proposal | Then remove redundant distinctions relative to joint questions. |
| PJ-E083 | observability | row closure | O=span{rows(CA^k):k>=0} | exact_checked | Finite rational matrices; exact observable-space compiler. |
| PJ-E084 | observability | hidden space | N=intersection_{k>=0}ker(CA^k) | derived | Linear all-future output equivalence. |
| PJ-E085 | observability | target recovery | ker(O) subset ker(G) iff G=L O | exact_checked | Finite dimensions; hidden-vector failure witness. |
| PJ-E086 | observability | hidden target amplitude | max_{delta in ker(H) intersect ker(M),norm(delta)<=1}\|g^T delta\| | derived | Norm must be declared; Euclidean formula uses orthonormal hidden basis. |
| PJ-E087 | observability | quadratic fibre constancy | N^T(g+Qx0)=0 and N^T QN=0 | derived | T=g^Tx+1/2 x^TQx, symmetric Q, full affine fibre x0+image(N). |
| PJ-E088 | observability | sensor repair | ker(Hnew N) subset ker(GN) | derived | Repairs target-affecting hidden directions. |
| PJ-E089 | observability | information matrix | J=H^T R^(-1)H | definition | Positive noise covariance; prior added separately. |
| PJ-E090 | observability | sensor sensitivity | d(g^T P g)/dw=-(h^T P g)^2 | derived | P=(J0+w hh^T)^(-1), nonsingular. |
| PJ-E091 | observability | stable recovery | G^*G <= lambda O^*O | historical_report | Bounded-operator assumptions; exact recovery and stable recovery differ. |
| PJ-E092 | observability | delay coordinates | Psi_L=[O;O F;...;O F^(L-1)] | proposal | Linear observability rows become [C;CA;...]; nonlinear sufficiency needs hypotheses. |
| PJ-E093 | features | finite feature closure | p_i composed F in span_Q{p_j} | exact_checked | Exact coefficient replay, not fitted regression. |
| PJ-E094 | features | feature evolution | p(F(x))=G p(x) | exact_checked | Output must belong to retained feature span. |
| PJ-E095 | features | all-time feature evolution | p(F^t(x))=G^t p(x) | derived | Induction from exact closure. |
| PJ-E096 | features | closure defect | psi(F(x))=G psi(x)+r(x) | definition | Explicit residual rather than silent truncation. |
| PJ-E097 | features | defect state augmentation | [psi';chi']=[[G,B],[C,D]][psi;chi] | proposal | r=Bchi and chi'=Cpsi+Dchi; closure may never terminate. |
| PJ-E098 | features | parameter sensitivity | S_{t+1}=D_xF S_t+D_theta F | derived | Differentiable parameterized dynamics. |
| PJ-E099 | features | linear sensitivity | S'=A S+A_theta x+B_theta u | derived | Discrete-time prime notation means next state; input fixed relative to parameter. |
| PJ-E100 | dynamics | reconstruction error | e=x-Vz | definition | State error versus output error distinguished. |
| PJ-E101 | dynamics | evolution defects | R=AV-VG; S=B-VH | exact_checked | Compatible linear model/reconstruction matrices. |
| PJ-E102 | dynamics | error recurrence | e_next=Ae+Rz+Su | derived | Direct substitution into full and reduced dynamics. |
| PJ-E103 | dynamics | error convolution | e_t=A^t e0+sum_{j<t}A^(t-1-j)(Rz_j+Su_j) | derived | Exact finite-time identity. |
| PJ-E104 | dynamics | continuous Lyapunov | A^T P+PA<=-2alpha P; P>0 | derived | Continuous time; alpha positive for decay. |
| PJ-E105 | dynamics | discrete Lyapunov | A^T PA<=gamma^2 P; 0<=gamma<1 | derived | Discrete time; fixed metric. |
| PJ-E106 | dynamics | contractive error | norm(e_t)<=gamma^t norm(e0)+sum gamma^(t-1-j)delta_j | exact_checked | Defects nonnegative bounds in the same contracting norm. |
| PJ-E107 | dynamics | uniform defect bound | norm(e_t)<=gamma^t norm(e0)+delta(1-gamma^t)/(1-gamma) | derived | Supremum defect delta and gamma<1. |
| PJ-E108 | dynamics | composed error | epsilon_total<=epsilon1+norm(V1)epsilon2 | derived | Compatible reconstruction stages. |
| PJ-E109 | dynamics | nonlinear composed error | epsilon_total<=epsilon1+L1 epsilon2 | derived | First reconstruction Lipschitz with constant L1. |
| PJ-E110 | dynamics | decision certificate | Jhat(a*)-epsilon_a*>max_{b!=a*}(Jhat(b)+epsilon_b) | exact_checked | Deterministic interval bounds; empirical uncertainty separate. |
| PJ-E111 | energy | mass energy | E=1/2 u^T M u | definition | Constant symmetric positive-definite M. |
| PJ-E112 | energy | symmetric energy operator | S_M=(A^T M+MA)/2 | exact_checked | u'=Au+f. |
| PJ-E113 | energy | energy derivative | E'=u^T S_M u+u^T M f | exact_checked | Direct identity; boundaries/sources in A or f. |
| PJ-E114 | energy | corrected decay dial | lambda=-2u^T S_Mu/(u^TMu) | exact_checked | Nonzero state; sign chosen for predicted decay. |
| PJ-E115 | energy | corrected source term | zeta=2u^T Mf/(u^TMu) | exact_checked | Positive source reduces net decay when lambda>0. |
| PJ-E116 | energy | corrected residue | d log(E)/dt=-lambda+zeta; rho=1-zeta/lambda | exact_checked | rho undefined at lambda=0; historical plus-sign formula rejected. |
| PJ-E117 | energy | CRO measured rate | alpha_hat=-(log E_k-log E_{k-1})/Delta_t | definition | Positive energies; window and integration scheme retained. |
| PJ-E118 | energy | CRO residual | R1=\|alpha_hat-alpha\| | definition | Diagnostic, not proof of physical universality. |
| PJ-E119 | energy | rank-one crystalline matrix | S(t)=I+t11^T; det(S)=1+nt | derived | n-dimensional all-ones vector. |
| PJ-E120 | energy | invariant-space leakage | (I-P)AP | definition | Zero iff range(P) invariant when P is a projection. |
| PJ-E121 | imp | SVD projector | M=U Sigma V^T; P=QQ^T | historical_report | Unit singular vectors do not establish invariant fixed modes. |
| PJ-E122 | imp | rejected SVD limit | all selected singular values=1 implies M^k->P | rejected | Orthogonal rotation counterexample. |
| PJ-E123 | imp | sufficient fixed-mode split | M=P+T; P^2=P; PT=TP=0; rho(T)<1 | derived | Then M^k=P+T^k and M^k x->Px. |
| PJ-E124 | imp | general invariant reduction | MQ=QG | derived | Retained dynamics may evolve instead of remaining fixed. |
| PJ-E125 | imp | exact retained evolution | M^k Q=QG^k | derived | Induction from intertwining. |
| PJ-E126 | psg | potential | L=-log cos(x); U=x^2+L^2; K_alpha=U^(-alpha/2) | definition | 0<x<pi/2; global contraction is not assumed. |
| PJ-E127 | psg | support functions | T=tan(x); H=x+LT; A=xH/(2U) | definition | Archive A<1/2 claim contradicts retained root A*=0.674... . |
| PJ-E128 | psg | corrected derivative | K_alpha'=-alpha H K_alpha/U | derived | U'=2H; factor-of-two repaired. |
| PJ-E129 | psg | flip parameter | alpha=1/(2A) | numerical_checked | At a fixed point with multiplier -1. |
| PJ-E130 | psg | scalar balance | F(L)=log U(L)+4A(L)log x(L)=0 | numerical_checked | x=acos(exp(-L)); bracket replay only, not uniqueness/transcendence proof. |
| PJ-E131 | psg | coordinate derivatives | x'=1/sqrt(exp(2L)-1); L_x'=tan x; T_x'=1+T^2 | derived | Positive L and admissible angle. |
| PJ-E132 | psg | root receipt | L*=0.531916689243299; x*=0.942857679982338; alpha*=0.741804515087895 | numerical_checked | Floating root reproduction, historical higher precision not re-certified. |
| PJ-E133 | psg | coefficient curve | a(v)=x(x+(v/2)T)/(2(x^2+v^2/4)); x=acos(exp(-v/2)); T=sqrt(exp(v)-1) | historical_report | Correct v=2L convention; archive typography inconsistent in places. |
| PJ-E134 | psg | exponential extraction | E F1+F0=0; E=exp(v)-1=-F0/F1 | historical_report | p=a'; F1 nonzero; original numerator and certificates needed. |
| PJ-E135 | psg | F0 | a(2a-1)(v+4-8a)^2 | historical_report | Factor structure preserved. |
| PJ-E136 | psg | F1 | (av-2a-2pv+1)(2av+4a-4pv-v-2) | historical_report | Factor structure preserved. |
| PJ-E137 | psg | cleared jet field | Xtilde=D partial_v+Dp partial_a+N partial_p | historical_report | D=2av^2(2a-1)(v+4-8a)^2; full N absent from read document. |
| PJ-E138 | psg | Darboux equation | Xtilde(H)=KH | definition | Listed identities do not by themselves establish unrestricted classification. |
| PJ-E139 | psg | PSG source elimination | P(x,L,T)=0; T^2=Y^2-1; T=-A/B | historical_report | 26-term source/100-term elimination reported; B=0 and integer-image branches must remain. |
| PJ-E140 | psg | normalized amplitude jet | A/A*=1+.3282804759delta+.0800766090delta^2+.0108819139delta^3+... | historical_report | Root-centered finite jet; not an origin-germ coefficient table. |
| PJ-E141 | psg | normalized balance jet | F/(L*F')=delta-.3793897467delta^2+.3008496421delta^3-.2807207864delta^4+... | historical_report | Declared normalization required. |
| PJ-E142 | psg | logarithmic derivative | I=F''/F' | definition | Derivative ratio; archive sometimes conflates Taylor factorial conventions. |
| PJ-E143 | jets | Schroeder equation | Psi(f(x))=-Psi(x) | conditional | Locally invertible exact solution requires f^2=id. |
| PJ-E144 | jets | reflection criterion | Psi=(x-f(x))/2; f^2=id implies Psi composed f=-Psi | derived | Centered analytic f with f'(0)=-1 gives Psi'(0)=1. |
| PJ-E145 | jets | flip obstruction | f=-x+ax^2+bx^3+...; f^2-x=-2(b+a^2)x^3+... | exact_checked | Centered coordinates; coefficient convention without factorials. |
| PJ-E146 | jets | two-cycle leading sign | f_nu=-(1+nu)x+kappa x^3+...; x^2~nu/kappa | derived | Real small cycle requires positive ratio; parameter-dependent fixed point recentered. |
| PJ-E147 | jets | Riccati coefficient law | (n+1)i_{n+1}=a 1_{n=0}+b i_n+c sum_{j=0}^n i_j i_{n-j} | exact_checked | Specific ODE I'=a+bI+cI^2; not a transcendence test. |
| PJ-E148 | jets | Riccati rejection residual | r_n=(n+1)i_{n+1}-a1_{n=0}-b i_n-c sum i_j i_{n-j} | exact_checked | Nonzero exact residual rejects this fixed model. |
| PJ-E149 | jets | Puiseux series | xi=a1 sqrt(epsilon)+a2 epsilon+a3 epsilon^(3/2)+... | proposal | Check second-iterate signs before claiming a real branch. |
| PJ-E150 | jets | seventh-order freedom | b7 leaves orders0..6 unchanged; order7 coefficient=1/128 | historical_report | Specific archived wall normalization; not recomputed here. |
| PJ-E151 | recurrences | Padovan | P_n=P_{n-2}+P_{n-3}; characteristic=x^3-x-1 | definition | Initial conditions fixed separately. |
| PJ-E152 | recurrences | Padovan modes | P_n=A psi^n+B q^n+conjugate(B q^n) | derived | Distinct characteristic roots and real initial data. |
| PJ-E153 | recurrences | Fibonacci kernel | F_{n+1}=sum_{k=0}^{floor(n/2)} binomial(n-k,k) | derived | Standard finite combinatorial identity. |
| PJ-E154 | recurrences | Tribonacci | T_n=T_{n-1}+T_{n-2}+T_{n-3}; x^3-x^2-x-1=0 | definition | Separate family from Catmull-Clark operator spectra. |
| PJ-E155 | recurrences | Escher-Pisot proposal | F_{n+1}(z)=lambda F_n(exp(2pi i alpha)conj(z))+sum_k(-1)^k theta^(-2k-1)binomial(n-k,k)q^(k(k+1)/2)+Phi(F_n(z)) | proposal | Finite k range for given n; no global contraction from lambda>1. |
| PJ-E156 | recurrences | mode stability | abs(lambda exp(-im alpha)+a)<1 | conditional | Specified linearized mode only. |
| PJ-E157 | topology | MMHW wavelet | psi_{alpha,beta}(x)=(1-alpha x^2)exp(-x^2/2)(1+beta sin(pi x^2)exp(-abs(x)^3)) | proposal | Wavelet admissibility and topological accuracy need separate analysis. |
| PJ-E158 | topology | subdivision block | M=[[-7/48,3(1+i sqrt3)/32],[5(1-i sqrt3)/16,-9/8]] | historical_report | Particular local block, not established full refinement operator. |
| PJ-E159 | topology | block characteristic | chi=x^2+61x/48+3/64 | derived | Trace/determinant checked in session; one root magnitude>1 prevents naive contraction claim. |
| PJ-E160 | topology | finite quadratic phases | b(x,y)=q(x+y)-q(x)-q(y) | definition | Finite nondegenerate quadratic module conventions. |
| PJ-E161 | topology | finite S,T | S_xy=\|A\|^(-1/2)exp(-2pi i b(x,y)); T_xx=exp(2pi i q(x)) | definition | Choice of sign fixes relations. |
| PJ-E162 | topology | modular relations | S^2=C; (ST)^3=xi C; xi=\|A\|^(-1/2)sum_x exp(2pi i q(x)) | conditional | Correct quadratic-module hypotheses and convention. |
| PJ-E163 | conductor | rotation algebra | UV=exp(2pi i theta)VU | definition | Generator conventions explicit. |
| PJ-E164 | conductor | clock shift convention | Ue_j=e_{j+1}; Ve_j=omega^j e_j; VU=omega UV | derived | Corrects sign/order mismatch with alternate UV convention. |
| PJ-E165 | conductor | irrational trace range | Z+theta Z | historical_report | K-theory/trace conventions for A_theta. |
| PJ-E166 | conductor | Weil commutant | c=dim{X:XS=SX,XT=TX} | definition | Operator pair must be specified, particularly dyadic case. |
| PJ-E167 | conductor | odd prime law | c(p^a)=a+1 | historical_report | Specific Weil core; not imported formal theorem. |
| PJ-E168 | conductor | multiplicativity | c(mn)=c(m)c(n), gcd(m,n)=1 | conditional | Requires product representation compatibility. |
| PJ-E169 | conductor | model-specific dyadic | c(2^a)=2a-1 | historical_report | Different archive cyclic dyadic pair gives 1,3,8,19,...; do not conflate models. |
| PJ-E170 | conductor | DAT hardware gates | C_cond<C_Pauli and p_eff<p_th | proposal | Illustrative rates are not measured native hardware. |
| PJ-E171 | conductor | continued-fraction tower | chi(theta)=limsup log(q_{n+1})/log(q_n) | definition | Growth diagnostic, not an inverse system without supplied bonding maps. |
| PJ-E172 | conductor | bounded type tower | a_n<=A implies q_{n+1}<=(A+1)q_n and chi=1 | derived | Irrational continued fractions. |
| PJ-E173 | conductor | finite phase approximation | abs(j theta-j p_n/q_n)<=1/q_{n+1}, j<=q_n | derived | From convergent error bound; trace claims require output continuity. |
| PJ-E174 | conductor | su2 quantum dimension | D^2=L/(2sin^2(pi/L)) | derived | L=k+2>=3; direct sine-sum identity. |
| PJ-E175 | conductor | Weyl volume | D^2=\|P/Q\| L^r/product_{alpha>0}(2sin(pi<rho,alpha^vee>/L))^2 | historical_report | Archived simply-laced scope; nonsimply-laced normalization separate. |
| PJ-E176 | conductor | volume asymptotic | D^2~C_g L^(r+2\|Phi+\|)=C_g L^dim(g) | derived | For fixed valid root-data formula. |
| PJ-E177 | conductor | fusion wall corrected variable | U_{L-1}(X/2)=0; X=2cos(theta) | derived | Use monic integer polynomial, rather than silently treating nonmonic U_m(x) as a monic Z[x] quotient. |
| PJ-E178 | collision | valuation kernel | kappa(m,n)=sum_p v_p(m)v_p(n) | exact_checked | Positive integers; arithmetic dot product. |
| PJ-E179 | collision | coprime orthogonality | kappa(m,n)=0 iff gcd(m,n)=1 | exact_checked | Nonnegative valuations. |
| PJ-E180 | collision | multiplicative bilinearity | kappa(mn,r)=kappa(m,r)+kappa(n,r) | exact_checked | Valuation additivity. |
| PJ-E181 | collision | divisor collision defect | F_{m,n}(q)=R_m(q)R_n(q)-R_mn(q) | derived | R_n product over prime-exponent intervals. |
| PJ-E182 | collision | collision zeta | Z_t(s)=sum_{m,n} exp(t kappa(m,n))/(mn)^s | definition | t real<=0 and Re(s)>1 ensures absolute convergence. |
| PJ-E183 | collision | Euler factor | product_p sum_{a,b>=0} exp(tab)p^(-s(a+b)) | derived | Absolute convergence or appropriate formal interpretation. |
| PJ-E184 | collision | positive-temperature divergence | exp(tN^2)p^(-2sN) does not tend to zero for real t>0 | derived | Single-prime diagonal suffices. |
| PJ-E185 | collision | coprime endpoint | Z_{-infinity}(s)=zeta(s)^2/zeta(2s) | derived | Re(s)>1; monotone/dominated limit for real parameters. |
| PJ-E186 | collision | historical thermal factor | Z_t(s)=zeta(s)^2 H_t(s) | historical_report | t<0; analytic continuation/remainders require original hypotheses. |
| PJ-E187 | collision | historical count asymptotic | A_t(X)=H_t(1)Xlog X+((2gamma-1)H_t(1)+H_t'(1))X+... | historical_report | Original Tauberian/analytic bounds not imported. |
| PJ-E188 | collision | finite numerator | N_L(x)=sum_{r,s=0}^{L-1}zeta_L^(rs)x^(r+s) | exact_checked | Exact ring implementation and series convolution comparisons. |
| PJ-E189 | collision | rational closure | L_L(x)=N_L(x)/(1-x^L)^2 | exact_checked | Formal series or abs(x)<1. |
| PJ-E190 | collision | direct coefficient | a_n=sum_{j=0}^n zeta_L^(j(n-j)) | exact_checked | Retains full and partial residue blocks. |
| PJ-E191 | collision | affine-periodic coefficient | a_{dL+r}=dG_r+B_r | exact_checked | G complete sum, B partial sum, 0<=r<L. |
| PJ-E192 | collision | stride recurrence | a_{n+2L}-2a_{n+L}+a_n=0 | exact_checked | All n>=0; finite exact state. |
| PJ-E193 | collision | numerator checkpoints | N_L(0)=1; N_L(1)=L; leading coefficient=zeta_L | exact_checked | For L>=2; L=1 special but implemented. |
| PJ-E194 | collision | rejected penalty PSD | exp(-beta kappa(m,n)) is always PSD | rejected | On {1,2}, determinant exp(-beta)-1<0 for beta>0. |
| PJ-E195 | collision | positive valuation kernel | K_beta(m,n)=exp(-beta norm(v(m)-v(n))^2) | derived | beta>=0, finite valuation supports; Gaussian PSD. |
| PJ-E196 | collision | Gaussian factorization | K=e^(-beta norm(v(m))^2)e^(-beta norm(v(n))^2)e^(2beta kappa(m,n)) | derived | Similarity role differs from collision suppression. |
| PJ-E197 | collision | prime-zeta decomposition | log Z_Gamma,L=r log zeta(Ls)+sum_m a_m P(ms) | historical_report | Original numerator/branch conventions; P prime zeta. |
| PJ-E198 | collision | branch-stripped product | FPbr= zeta(L)^r product_p[N(1/p)exp(-a1/p)] | historical_report | Finite factors, zeros, and branch conventions explicit. |
| PJ-E199 | collision | finite-part tail | abs(log tail)<=C/P; abs(tail-1)<=exp(C/P)-1 | derived | Requires proved local remainder bound abs(r_p)<=C/p^2 beyond cutoff. |
| PJ-E200 | collision | failed dimension weld | FPbr != D^2 under retained projection/normalization sweep | historical_report | Bounded tested family, not exclusion of every possible relationship. |
| PJ-E201 | core | core cubic | alpha^3-alpha^2+1=0 | exact_checked | Transported from cubic quotient ring. |
| PJ-E202 | core | critical cubic | u^3-4u^2+5u-1=0 | exact_checked | Canonical ring modulus in rings.py. |
| PJ-E203 | core | plastic transport | u=1+alpha; beta=-1/alpha; beta^3-beta-1=0 | exact_checked | Explicit inverse maps; not discriminant-only identification. |
| PJ-E204 | core | critical factorization | (z-1)^2(z^3-4z^2+5z-1) | historical_report | Critical ideal elimination source retained; not recomputed full ideal. |
| PJ-E205 | core | abelian shadow cubic | z^3-2z^2-z+1; disc=49 | historical_report | Conductor7 cyclic shadow versus nonabelian core. |
| PJ-E206 | core | Hessian element | h=(-2u^2+3u-2)/(-u^2+u); h^3+4h^2-23h+23=0 | exact_checked | Denominators invertible; field coordinates retained. |
| PJ-E207 | core | vertex element | v=(6u-8)/(3u^2-8u+5); 23v^3+4v+200=0 | exact_checked | Archived quantity, no new physical loop prediction. |
| PJ-E208 | core | corner family | P_{a,b}(z)=(1-z)^a-z^b | definition | Bounded divisibility census not global isolation. |
| PJ-E209 | core | regulator volume report | 3D(alpha)=2.8281220883307831628... | historical_report | Selected complex embedding/orientation; volume identification requires geometric input. |
| PJ-E210 | core | Bloch conjugation | D(conjugate(z))=-D(z) | derived | All-conjugate unweighted sum cancels. |
| PJ-E211 | core | oriented regulator | R(xi)=(D(sigma1 xi),...,D(sigmar xi)); scalar=c^T R | proposal | One embedding per conjugate pair; c from geometry. |
| PJ-E212 | core | regulator magnitude | norm(R(xi))^2 | proposal | Conjugation-choice independent magnitude, not automatically volume. |
| PJ-E213 | deformation | cotangent fibre | L_{B/Q} tensor k(p)=[I/I^2 tensor k(p) -> Omega tensor k(p)] | historical_report | Local complete-intersection convention; differential df_p. |
| PJ-E214 | deformation | point lift | df_p(v)+g(p)=0 | derived | Square-zero deformation f+epsilon g and marked point p+epsilon v. |
| PJ-E215 | deformation | cusp | f=y^2-x^3; Tjurina=Q[x,y]/(f,f_x,f_y)=span{1,x} | historical_report | Characteristic0 or suitable good characteristic. |
| PJ-E216 | deformation | E37 model | Y^2=X^3-16X+16; Delta=151552; j=110592/37 | derived | Standard short-Weierstrass invariants. |
| PJ-E217 | deformation | E37 tangent | dj=(559872/1369,373248/1369); gauge=(64,-96); moduli=(96,64) | historical_report | dj(gauge)=0; dj(moduli)=77635584/1369. |
| PJ-E218 | deformation | discriminant formula | Delta=-16(4a^3+27b^2); j=1728(4a^3)/(4a^3+27b^2) | derived | Nonsingular short model; coordinate scaling can alter Delta while preserving j. |
| PJ-E219 | deformation | Zsqrt-5 divisors | (2)=p2^2; (3)=p3+ p3-; (1+/-sqrt(-5))=p2 p3+/- | historical_report | Archive weight-one Picard/K0 comparison; not arbitrary higher weights. |
| PJ-E220 | deformation | stationary sensitivity | dx*/d epsilon=-(Hessian V0)^(-1)gradient W | derived | Nonsingular Hessian; symmetry zero modes require quotient/gauge fixing. |
| PJ-E221 | deformation | relation response | dR/d epsilon=-gradient R^T(Hessian V0)^(-1)gradient W | derived | Allowed perturbation space must be specified. |
| PJ-E222 | codes | Artin-Schreier-Witt | 0->Z/p^n->W_n --F-1-->W_n->0 | historical_report | Characteristic p etale sheaf setting; not mixed-characteristic elliptic descent. |
| PJ-E223 | codes | Hermitian curve | y^p+y=x^(p+1) | definition | Over F_{p^2}; code divisor/evaluation set needed. |
| PJ-E224 | codes | Hermitian code reports | [8,4,4]_4; [27,6,19]_9; [125,3,119]_25 | historical_report | Retained numerical/exact reports, implementation not imported. |
| PJ-E225 | codes | p5 weight enumerator | 12000z^119+600z^120+3000z^124+24z^125 | historical_report | Nonzero words; add constant1 for full enumerator. |
| PJ-E226 | codes | alternate curve | X_q:y^q+y=x^2; n_q=2q^2-q | historical_report | Point-count convention and q conditions must be supplied. |
| PJ-E227 | prefix | normal binary64 | x=(-1)^s(2^52+F)2^(E-1075) | derived | Normal finite values only; subnormals special. |
| PJ-E228 | prefix | monotone integer encoding | MIE(raw)=raw xor 2^63 if nonnegative; raw xor(2^64-1) if negative | historical_report | Frozen bit convention; NaNs/signed zeros explicitly handled in original model. |
| PJ-E229 | prefix | prefix depth | lcp(a,b)=clz(MIE(a) xor MIE(b)); k(x)=lcp(x,+0); D=64-k | definition | Same bit depth can mean different numerical precision across binades. |
| PJ-E230 | prefix | prefix distance | d(a,b)=2^(-lcp(a,b)) for a!=b; d(a,a)=0 | derived | Ultrametric on finite bit encodings, not ordinary real distance. |
| PJ-E231 | prefix | dyadic power test | x=+/-u2^e, u odd; u=v^d and d divides e | derived | Rational dth powers; negative sign allowed only odd d; zero separate. |
| PJ-E232 | prefix | restricted transfer heuristics | ADD=min(kA,kB); MUL=max(0,kA+kB-53); DIV=max(0,kA-kB); SQRT=max(0,kA-1) | historical_report | Not universal IEEE754 guarantee; binade/cancellation cases matter. |
| PJ-E233 | prefix | prefix bookkeeping | Delta_pflux=k_result-k_in; Ksys_new=Ksys_old-k_old+k_result | definition | Register selection and meanings explicit. |
| PJ-E234 | prefix | prefix Fermat proposal | k(f(x+delta),f(x))>=k(delta)-kappa_f | proposal | Restricted operation/domain hypotheses and exact bit semantics needed. |
| PJ-E235 | physics | SYMMETRON Hamiltonian | H=L0-c/24+sum_g gamma_g T_g+kappa log L0 | proposal | Positive spectral domain for logarithm; not a validated gravity theory. |
| PJ-E236 | physics | log-periodic coupling | g(E)~E^alpha[1+A cos(2pi log(E/E0)/log C)] | proposal | Parameters and units specified before physical interpretation. |
| PJ-E237 | physics | L-value constant proposals | alpha=L(E,1)/(2pi); beta=L(f,3/2)/pi^(3/2); kappa=L'(g,1)/L(g,1) | proposal | Underlying objects not recovered; cannot use as determined constants. |
| PJ-E238 | physics | activation model | F(x)=1/(1+exp(-x/.0712)); H*=H+alpha abs(H)^beta F(H/Ep) | proposal | Functional calculus, units, and physical fit not established. |
| PJ-E239 | physics | spectral dimension model | d_s(E)=4-alpha(E/Ep)^beta F(E/Ep) | proposal | Model ansatz, not observed dimension law. |
| PJ-E240 | physics | six-term potential | U(theta)=cos2theta+(2/3)cos3theta+(2/5)cos5theta+(1/4)cos8theta-(2/9)cos9theta-(1/6)cos12theta | historical_report | Local phase check distinct from physical CKM prediction/global proof. |
| PJ-E241 | physics | phase derivative | U'=-2sin2theta-2sin3theta-2sin5theta-2sin8theta+2sin9theta+2sin12theta | derived | Direct derivative. |
| PJ-E242 | physics | golden phase identity | theta*=11pi/30; 1-2cos(12theta*)=(3-sqrt5)/2=phi^(-2) | derived | Shared by other phase points; does not alone select66degrees. |
| PJ-E243 | physics | observable ratio | Ceff=\|Uub\|(1-\|Uub\|^2)/(\|Uus\|\|Ucb\|) | definition | Nonzero denominator; model must enforce value. |
| PJ-E244 | physics | conditional observable polynomial | c^2(1-c^2)^2-3abc(1-c^2)+a^2b^2=0 | conditional | a=\|Uus\|,b=\|Ucb\|,c=\|Uub\|, if Ceff=phi^-2. |
| PJ-E245 | physics | unresolved archived polynomial | c^2 t^4-7abc t^2+a^2b^2=0 | open | Original a,b,c,t definitions unrecovered; do not equate with coefficient3 relation. |
| PJ-E246 | physics | unresolved phase polynomials | 4t^2 J^2=4K-N^2; N^8-7N^6K+14N^4K^2-8N^2K^3+K^4=0 | open | Original N,K,t,J definitions missing. |
| PJ-E247 | physics | allowed perturbation | V_epsilon=V0+epsilon x | historical_report | A CP-even deformation changed the golden relation; protection unresolved. |
| PJ-E248 | physics | coercivity certificate | f-L=sigma0+sum_i sigma_i g_i+sum_j q_j h_j | proposal | SOS positivity and constraint conventions needed; no universal optimizer guarantee. |
| PJ-E249 | physics | wall threshold law | Gamma proportional (M-2m)^3 near threshold | historical_report | Specific channels/model, not universal decay law. |
| PJ-E250 | wind | vorticity | zeta=v_x-u_y | definition | Coordinates and velocity components explicit. |
| PJ-E251 | wind | stretch tilt divergence | S=(zeta+f)w_z; T=-v_z w_x+u_z w_y; D=-(zeta+f)div(u) | historical_report | Saved signed-source ledger; governing equation convention must match. |
| PJ-E252 | wind | baroclinicity | B=(rho_x p_y-rho_y p_x)/rho^2 | historical_report | Density positive; coordinate signs fixed. |
| PJ-E253 | wind | forcing beta source | F=(curl forcing)_z; P_beta=-beta v; S_zeta=S+T+D+B+F+P_beta | historical_report | Budget term ledger, not full unobserved atmosphere reconstruction. |
| PJ-E254 | wind | exact SDE | F=exp(A Delta_t); Qd=int_0^Delta_t exp(As)LL^T exp(A^Ts) ds | derived | Linear constant-coefficient SDE. |
| PJ-E255 | wind | innovation support | I=sum_i K_i nu_i^T S_i^(-1)nu_i | historical_report | K_i spatial support kernel, not necessarily Kalman gain. |
| PJ-E256 | wind | constraint injection | C=delta_xC^T Q delta_xC | definition | Declared metric; mechanism and causality separate. |
| PJ-E257 | wind | dynamic residual | R=norm(W[partial_t x+N(x)-F(x)])^2 | definition | Units, supports, operators required. |
| PJ-E258 | wind | expiry rule | t_exp=inf{t:A_struct^2/V0>=eta_s or Vplus/V0>=eta_p} | historical_report | Baseline positive; model expiry criterion. |
| PJ-E259 | wind | exterior law | v=c r^(-p); p=1+2h | historical_report | Quadrant envelopes are not pointwise wind samples. |
| PJ-E260 | wind | pressure adequacy | Delta_t<=L/(2U); quadratic fit needs at least7 stations | historical_report | Six coefficients plus residual degree of freedom, rank/conditioning separately checked. |
| PJ-E261 | wind | assimilation commutator | [A,F]x | proposal | Order effects between assimilation and dynamics. |
| PJ-E262 | sequence | Pauli product | (a.sigma)(b.sigma)=(a.b)I+i(a cross b).sigma | derived | Standard Pauli convention. |
| PJ-E263 | sequence | commutator | [a.sigma,b.sigma]=2i(a cross b).sigma | derived | Order-sensitive interaction, not automatically empirical predictive feature. |
| PJ-E264 | sequence | symmetric-order split | AB=1/2{A,B}+1/2[A,B] | derived | Algebraic identity. |
| PJ-E265 | sequence | nested interaction | [A,[B,C]] | proposal | Higher-order feature; test against commutative ablation. |
| PJ-E266 | graphs | weighted histogram | Z_N(u)=sum_n c_n exp(n.u) | exact_checked | Histogram partition exact for rational multiplicative weights; log derivatives mathematical. |
| PJ-E267 | graphs | gradient covariance | grad log Z=E[n]; Hessian log Z=Cov(n)>=0 | derived | Finite positive partition function. |
| PJ-E268 | graphs | phase domination | abs(Z_N(u+i phi))<=Z_N(u) | derived | Positive multiplicities; triangle inequality. |
| PJ-E269 | graphs | subcritical tail | sum_{ell>=d}C(mu eta)^ell=C(mu eta)^d/(1-mu eta) | derived | mu eta<1 and justified graph-count domination. |
| PJ-E270 | graphs | finite histogram compression | 4133166 walks ->66 type vectors | historical_report | Specific retained length10 graph; order-specific observables require richer state. |
| PJ-E271 | finsler | dead-zone action | phi(v)=0 if abs(v)<=c; (abs(v)-c)^2/(4D) otherwise | definition | D>0,c>=0. |
| PJ-E272 | finsler | convex conjugate | phi*(p)=c abs(p)+D p^2 | derived | Exact Legendre transform of declared dead-zone action. |
| PJ-E273 | finsler | Hamiltonian | H=b.p+sum_i(c_i abs(p_i)+D_i p_i^2) | derived | Normalization tied to the displayed Lagrangian. |
| PJ-E274 | finsler | Hamilton-Jacobi | H(x,grad W)=0 | proposal | Viscosity/subgradient treatment at nonsmooth facets. |
| PJ-E275 | finsler | FW action | S=1/4 int (xdot-b)^T D^(-1)(xdot-b) dt | definition | Noise normalization fixes epsilon and diffusion factors. |
| PJ-E276 | finsler | escape proxy | lambda_FW=exp(-Wmin/epsilon); P_T=1-exp(-T lambda) | historical_report | Asymptotic exponential rate/prefactors and Poisson assumptions separate. |
| PJ-E277 | thermal | energy deformation | H_i=E_i+cE_i^a | definition | Energy domain for fractional powers and units required. |
| PJ-E278 | thermal | partition and purity | Z(beta)=sum_i exp(-beta H_i); F(beta)=log Z(2beta)-2log Z(beta) | derived | Finite Gibbs spectrum. |
| PJ-E279 | thermal | purity identity | exp(F)=Tr(rho_beta^2) | derived | Normalized Gibbs density matrix. |
| PJ-E280 | thermal | variance objective | V=Var_{t uniform}[F(exp(t))] | definition | Grid/range/clipping specified; different historical objectives not conflated. |
| PJ-E281 | thermal | finite-size intercept | spread(N)=A+B/N | proposal | Model fit, not automatically an asymptotic theorem. |
| PJ-E282 | thermal | weak exponent identification | c=0 implies H_i independent of a | derived | Near-zero c undermines preferred-exponent inference. |
| PJ-E283 | closure | finite closure | cl(A)=intersection{B superset A:B stable} | definition | Finite closure-system implementation proposal. |
| PJ-E284 | closure | closure debt | D(A)=mu(cl(A))-mu(A) | definition | Monotone nonnegative measure mu. |
| PJ-E285 | closure | admitted state | adm=c_{R_sound(w)}(X) intersect(S intersect w) | historical_report | Original finite atom/rule semantics required. |
| PJ-E286 | closure | obstruction partition | Omega=Omega_miss disjoint-union Omega_ung disjoint-union Omega_rule | historical_report | Missing support, ungrounded claims, rule gaps. |
| PJ-E287 | closure | closure-cost invariant | I_tau=(K_tau*,Lambda_tau,B_tau) | proposal | Minimal admitted closure cost, cheaper-route witnesses, fake-work spectrum; invariance tests needed. |
| PJ-E288 | closure | comparison cochains | gamma_ij=C_i-C_j; eta_i(f)=Psi(f)C_i-C_i Phi(f) | proposal | Linear/additive setting required for subtraction/cohomology. |
| PJ-E289 | closure | total differential | D=delta_Cech+(-1)^p d_I; D^2=0 | conditional | Compatible double-complex structure, not arbitrary nonlinear constraint sheaves. |
| PJ-E290 | closure | cohomological trichotomy | DDelta!=0 incoherent; Delta=Dh removable; closed nonexact obstruction | derived | For an actual declared cochain complex. |
| PJ-E291 | closure | null-labor efficiency | eta(E)=1-K(residue)/K(expansion) | definition | Cost model and correctness preservation must be explicit. |
| PJ-E292 | closure | representation profile | P(q)=(Q_exact,Q_bounded,E,D,C) | proposal | Preserved questions, bounds, domain, and cost. |
| PJ-E293 | closure | question-dependent height | h_q(x)=h(q(x)) | proposal | Organizes search, does not replace a global completeness bound. |
| PJ-E294 | closure | adaptive local sieve | R_m={e mod m:retained constraints hold}; next test by eliminated_population/cost | exact_checked | Implemented for F(n)=m^d in sieve.py; exclusions independent of test order; counts replayed against integer roots. |
| PJ-E295 | closure | repair pipeline | question->candidate->closure test->exact model / bounded model / repair witness | proposal | Master architecture; not one universal theorem. |
| PJ-E296 | transport | integer infeasibility certificate | y in Q^m, yB in Z^n, yb not in Z => Bx=b has no integer solution | exact_checked | y=U_i/d_i from a failing Smith coordinate; yB=0, yb!=0 when the system already fails over Q. |
| PJ-E297 | transport | saturation index | [(Q-span(G) intersect Z^n):Z-span(G)]=d_1 d_2...d_r | exact_checked | Rows of G independent or not; witness row of V^{-1} at the first d_i>1. |
| PJ-E298 | transport | integer kernel | ker_Z B=Z-span(V e_{r+1},...,V e_n) | exact_checked | UBV=D with rank r; the basis is saturated. |
| PJ-E299 | series | Hankel realization | x_{pa}=x_p M^{-1}H_a; f(p)=x_p M^{-1}h; alpha=x_empty | exact_checked | M invertible Hankel block on chosen prefixes/suffixes; agreement beyond the block is a held-out check with a witness word. |
| PJ-E300 | series | coarsest exact lumping | sum_{i in B}A_c[i][j] constant over j in C for all blocks B,C and all costs c; H constant on blocks | exact_checked | Partition refinement from output labels; every valid lumping refines the result. |
| PJ-E301 | transport | Hermite normal form | H=UB; echelon, pivots positive, entries above pivots in [0,pivot) | exact_checked | U unimodular; equal row lattices iff equal nonzero Hermite rows. |
| PJ-E302 | series | multi-output Hankel realization | H_{u,(v,j)}=f_j(uv); f(w)=alpha A_w Beta with Beta n-by-k | exact_checked | Stacked block; shared state can exceed each single-output rank. |
| PJ-E303 | invariants | parametric rank locus | {t:rank A(t)<r}=Z(gcd of r-minors) subset Z(M_0) | exact_checked | One variable over Q; elimination over Q[t]/(squarefree M_0) with zero-divisor splitting. |
| PJ-E304 | invariants | C3 family exceptional parameters | degree5 correction locus lambda^2-1600/49; degree3 lambda(lambda^2-400); degree10 lambda | exact_checked | Degrees3..12 over Q; degree4 lambda^2+50 and degree12 lambda^2+5 have no rational points. |
| PJ-E305 | arithmetic | local power exclusion | F(n) mod q not a d-th power residue mod q => F(n) is not a d-th power | derived | Exact for every modulus q>=2; the sieve only orders these tests. |
| PJ-E306 | invariants | comprehensive rank cells | parameter space = disjoint union of V(S_i) minus V(prod N_i), rank constant on each | exact_checked | Several parameters over the algebraic closure; S_i saturated by N_i; branch on pivot zero/nonzero. |
| PJ-E307 | invariants | Rabinowitsch saturation | I:q^infinity = (I+<1-zq>) intersect Q[t] | derived | Elimination order on z; cell nonempty iff saturated ideal is not 1. |
| PJ-E308 | invariants | two-parameter partner surface | f=x^6+y^6+a x^3y^3+b(x^4y^2+x^2y^4); rational exceptional points (+/-16,-9),(0,3),(0,15),(0,-5),(0,0),(+/-20,0),(+/-40/7,0) | exact_checked | Degrees3..12 of the correction gates; degree3 has a drop curve, degree8 has drop curves including b=0. |
| PJ-E309 | invariants | fourfold-root exceptional sextic | x^6+y^6+16x^3y^3-9(x^4y^2+x^2y^4)=(x-y)^4(x^2+4xy+y^2) | exact_checked | Correction rank drops at this point in degrees5,6,7,9,10,11. |
| PJ-E310 | invariants | active strata | dim A_N=rank[L_N;P_N]-rank L_N constant on refined cells; commuting=dim ker L_N-dim A_N | exact_checked | Two-parameter sextic surface, degrees3..12; partners replayed at rational samples only. |
| PJ-E311 | invariants | surface discriminant | Res_x(f(x,1),f_x(x,1)) in Q[a,b], total degree8 | exact_checked | Bareiss determinant of the Sylvester matrix; vanishes exactly at repeated roots since f is monic in x. |
| PJ-E312 | invariants | perfect-cube commuting exceptions | f=(x^2+y^2)^3: ker L_N=span{(x^2+y^2)^(N/2)} with A_N=0 for N=4,6,8,10 | exact_checked | Correction-rank exception that adds no active capacity; degree12 kernel3 active2. |
| PJ-E313 | invariants | degree8 partner curve | a^2b-4b^3+6a^2-28b^2+20b+300=0; rational points (+/-11,6),(+/-16,-9),(0,-5) | exact_checked | Bounded-height scan, height<=12; not a complete rational point list. |
| PJ-E314 | invariants | degree12 partner curve | b^4+24b^3+81a^2-126b^2+405=0; rational points (+/-4,-3),(+/-32/25,-9/5),(+/-16,-9) | exact_checked | (+/-4,-3) has a double root; (+/-32/25,-9/5) is squarefree. |
| PJ-E315 | observability | readout identifiability | h^T beta determined by X beta iff h in row(X); else Xn=0, h^T n!=0 | exact_checked | Noiseless linear response; witness gives two fits with different readouts. |
| PJ-E316 | observability | demand-supported readout | theta_i=sum_k q_k phi(d_k)^T beta_i=h_q^T beta_i | definition | q a declared training-derived demand distribution. |
| PJ-E317 | observability | repeat versus new condition | row in row(X) leaves identifiability unchanged | exact_checked | Repeats sharpen precision only; minimal identifying sets by exhaustive search up to a size bound. |
| PJ-E318 | observability | Gaussian value of information | VOI(e)=h^T Sigma h-h^T(Sigma^{-1}+e e^T/s^2)^{-1}h | exact_checked | Linear Gaussian model; reduction independent of the unseen outcome; conditional on prior and noise. |
| PJ-E319 | decisions | settled decision | Jhat(a*)-eps(a*)>max_{b!=a*}(Jhat(b)+eps(b)) | exact_checked | Valid intervals; refinement restricted to overlapping contenders. |
| PJ-E320 | decisions | evolution-defect split | e_{t+1}=A e_t+(AV-VG)z_t+(B-VH)u_t | exact_checked | Replayed at every step in rational arithmetic with an infinity-norm bound. |
| PJ-E321 | closure | adaptive monomial closure | add supp(psi o F) minus current features until empty; minimal space span{C,CK,CK^2,...} | exact_checked | Stops on degree growth or budget with the residual support. |
| PJ-E322 | counting | constraint attribution | removed_only_by_k = #F(constraints minus k) - #F | exact_checked | Selections violating constraint k and no other; compared with enumeration. |
| PJ-E323 | counting | inclusion profile | Pr(x_i=1 \| feasible) = #F(x_i=1)/#F; Pr(x_i=1 \| optimal) = ties(x_i=1)/ties | exact_checked | Counts original objects; compared with enumeration. |
| PJ-E324 | physics | stationary response | dx*/dtheta = -H^{-1} d2V/dx dtheta at (x*,0) | derived | Nondegenerate stationary point; first order only. |
| PJ-E325 | physics | symmetry protection | dR(v)=0 for every perturbation v fixed by the symmetry | exact_checked | First-order statement; higher orders need an exact symmetry argument. |
| PJ-E326 | transport | quadratic square transport | k y^2=an^2+bn+c <=> X^2-4ak Y^2=b^2-4ac, X=2an+b, Y=y; n=(X-b)/(2a) | exact_checked | Integers; X=b mod 2a required; branches a=0, definite, square D, N0=0 handled separately. |
| PJ-E327 | pell | Nagell class bound | N0>0: 0<=y<=y1 sqrt(N0/(2(x1+1))); N0<0: 0<y<=y1 sqrt(-N0/(2(x1-1))) | derived | x^2-Dy^2=N0, D>0 nonsquare, (x1,y1) fundamental unit; classical theorem, cited. |
| PJ-E328 | pell | compiled quadratic population | hits = {(X-b)/(2a): (X,Y) in seeds*eps^Z, X=b mod 2a} | exact_checked | Complete for the Pell branch; checked against brute force on 158 equations; remote indices replayed exactly. |
| PJ-E329 | invariants | Clebsch invariants of the sextic | i=(f,f)_4; A=(f,f)_6; B=(i,i)_4; C=(i,(i,i)_2)_4; D=(y3,y1)_2 with y1=(f,i)_4,y2=(i,y1)_2,y3=(i,y2)_2 | definition | Unnormalized transvectants; degrees2,4,6,10; scale by det^(3k) under GL2. |
| PJ-E330 | invariants | weighted orbit test | (A:B:C:D) equal in P(1,2,3,5) iff I_i^{w_j}J_j^{w_i}=J_i^{w_j}I_j^{w_i} | derived | Proves GL2(Qbar)-equivalence only for squarefree sextics. |
| PJ-E331 | invariants | Cayley-Sylvester count | dim Cov_{d,m}(n)=p(w;d,n)-p(w-1;d,n), w=(nd-m)/2 | derived | p counts partitions into at most d parts of size at most n. |
| PJ-E332 | invariants | cubic partner theorem | det L_3(f)=(A^2-B/6)/16 | exact_checked | Every binary sextic; certified on the dense slice by a 125-point exact grid. |
| PJ-E333 | invariants | quartic covariant partner | (f,(f,f)_4)_3=(f,(f,f)_4)_5=0 | exact_checked | Every binary sextic; no covariants of degree3 and order4 or0; slice certificate (64 points); active iff (f,(f,f)_4)_1!=0. |
| PJ-E334 | invariants | degree-12 covariant partner | G=144A^2f^2+(216/5)A iH+24A f(f,i)_2-(9/4)i^3-9Delta H+(f,i)_2^2; (f,G)_3=-432 s (f,H)_1; (f,G)_5=25920 s (f,i)_1; s=A^2-25B/96 | exact_checked | Every binary sextic; slice certificate (512 points); G is a partner on s=0 where G!=0. |
| PJ-E335 | invariants | degree-12 partner converse | ker L_12(f)!=0 => A^2=25B/96 | open | Supported by random sextics and two independent families; not proved. |
| PJ-E336 | invariants | slice certificate | covariant identity of degree d holds iff it holds on xy(x-y)(x^3+px^2y+qxy^2+ry^3) for (p,q,r) in {0..d}^3 | derived | Same degree, order and weight; dense GL2-orbit; grid vanishing lemma. |
| PJ-E337 | invariants | surface drop curves as invariant loci | deg3: A^2=B/6; deg12: A^2=25B/96; deg8: AB^2+BC/6-9D/2=0 | exact_checked | On the two-parameter family only; whether the deg8/deg12 relations hold in the full moduli is open. |
| PJ-E338 | invariants | named exceptional sextics | (0,15)~x^6+y^6; (0,-5)~xy(x^4-y^4) | exact_checked | Equal Clebsch points of squarefree sextics; GL2 over the algebraic closure. |
| PJ-E339 | empirical | normalized recovery travel | eta_ij=sum_k w_k v_ijk/(0.5 s_ij,entry) | definition | Velocity projected on the outgoing direction over 0.5s after a detected plant; trapezoid weights; not force or efficiency. |
| PJ-E340 | empirical | recovery response model | eta=phi(s,a)^T(beta+u_i)+e, phi=(1,s',a',s'a'), u_i~N(0,T) | proposal | Linear mixed model fitted by EM on training athletes; pooling assumptions reported as pooling reliance. |
| PJ-E341 | empirical | context-adjusted target | r_i=(1/n_i) sum_p [y_ip-m(x_ip)]; shrunk by n_i/(n_i+k) | definition | Cross-fitted for training athletes; training-only m and k for validation athletes; observed participants only. |
| PJ-E342 | empirical | paired predictive gain | G=1-MSE_movement/MSE_baseline | definition | Same availability indicators, missing-data rule and tuning grid in both models; athlete-grouped temporal folds. |
| PJ-E343 | empirical | scouting advantage | G>=0.03 with fixed-prediction 90% lower bound >0 on an untouched class | open | Proposed threshold awaiting owner confirmation; synthetic runs test the pipeline only. |
| PJ-E344 | observability | LOS onset-travel ambiguity | X=(1,1), n=(-1,1); Xn=0, (1,0)n=-1 | exact_checked | Total onset plus travel cannot identify either component; separate from acceleration models. |
| PJ-E345 | empirical | stable crossing travel | u=2d/(v+sqrt(v^2+2ad)) | derived | Local constant acceleration; d,v>=0 and a>0; not an athlete physiology law. |
| PJ-E346 | empirical | crossing travel box | u(d_lo,v_hi,a_hi)<=u(d,v,a)<=u(d_hi,v_lo,a_lo) | exact_checked | Monotone extrema of declared box; outward polynomial signs rationally checked. |
| PJ-E347 | empirical | half-second motor functional | A_T=2[x_parallel(t0+T)-x_parallel(t0)-T v_parallel(t0)]/T^2 | definition | T=.5s post operational onset; no known cue or reaction-time claim. |
| PJ-E348 | empirical | acceleration functional identity | A_T=(2/T^2) integral_0^T (T-t) a_parallel(t0+t) dt | derived | Integrable acceleration; analytic invariance tests; no second numerical differentiation. |
| PJ-E349 | empirical | scalar source precision | V_i=(tau^-2+sum sigma_d^-2)^-1; m_i=V_i sum x_ij sigma_d^-2 | derived | Gaussian player deviation; independent training repeats; branches are not repeats. |
| PJ-E350 | empirical | uncertainty-integrated NFL correction | r_i given D_i ~ Normal(lambda m_i, sigma_NFL^2+nu_i^2+lambda^2 V_i) | derived | Conditional error independence; target precision descriptive; empirical transfer unestablished. |
| PJ-E351 | empirical | paired loss noise cancellation | Delta_noisy=Delta_clean+2e(p_movement-p_baseline) | derived | Expected equality requires conditional mean-zero error; no automatic causal interpretation. |
| PJ-E352 | observability | operational get-off decomposition | t_cross-t_snap=(t_onset-t_snap)+(t_cross-t_onset) | derived | Observed geometry and operational tracking onset; supplied official get-off retained separately; no reaction-time claim. |
| PJ-E353 | observability | positive onset-travel hidden direction | X=(1,1), h=(1,0), n=(-1,1); Xn=0, hn=-1 | exact_checked | Linear sum cannot determine onset independently; physically admissible positive witnesses in bridge receipt. |
| PJ-E354 | empirical | game-cluster movement covariance | Cov(mean z)=G/(G-1) sum_g S_g S_g^T, S_g=sum_(p in g) w_p(z_p-mean z) | definition | Common usable plays and original play weights; fewer than two games yields unknown covariance. |
| PJ-E355 | dynamics | causal post-onset burst integral | A_T=(2/T^2) integral_0^T (T-u) a_parallel(t_onset+u) du | derived | Twice differentiable directional position, causal initial velocity, T=.5 s; not force or reaction time. |
| PJ-E356 | series | supervised delay continuation | K_lambda=(P^T W P+lambda I)^(-1)P^T W F | numerical_checked | Train-only standardized past/future movement blocks; equal sampled-player weight; player-held inner selection. |
| PJ-E357 | series | target-directed finite state | z=p K_lambda V_r; forecast=z V_r^T | numerical_checked | Right singular vectors of fitted future outputs; centering/inverse scaling in code; finite declared horizon only. |
| PJ-E358 | series | second-order predictive witness | u_(t+1)=3/2 u_t-3/4 u_(t-1) | numerical_checked | Explicitly synthetic recurrence; identical current samples need not imply equal continuations. |
| PJ-E359 | empirical | cross-fitted physical movement transfer | qhat_i^OOF=f_(training minus fold(i))(B_i,X_i) | definition | State discovery, targets and preprocessing rebuilt for each player fold; physical units across SVD rotations. |
| PJ-E360 | empirical | prediction-trained outcome decoder | g_hat=argmin_g sum_i (y_i-g(B_i,qhat_i^OOF))^2+alpha norm(g)^2 | definition | Training inputs are predicted movement; held-out NFL movement enters diagnostics only. |
| PJ-E361 | dynamics | fitted two-stage error identity | yhat-y=[g(B,qhat)-g(B,q)]+[g(B,q)-y] | derived | Frozen fitted decoder and observed held-out target; algebraic decomposition does not imply causation. |
| PJ-E362 | dynamics | fixed affine movement scenario bound | abs(g(B,qhat)-g(B,q))<=sum_j abs(w_j) r_j | derived | Affine fitted decoder and valid supplied box abs(qhat_j-q_j)<=r_j; separate from empirical intervals. |
| PJ-E363 | observability | physical scouting loading | q=F x+c, g=w^T q+b => h=F^T w | derived | Frozen affine fit and fixed preprocessing/missingness pattern; physical source units. |
| PJ-E364 | observability | exact scalar posterior update | Sigma'=Sigma-Sigma e e^T Sigma/(s^2+e^T Sigma e) | exact_checked | Positive-definite rational prior, positive independent noise; fixed loading and declared Gaussian model. |
| PJ-E365 | observability | correlated attempt block update | Sigma'=Sigma-Sigma E^T(R+E Sigma E^T)^(-1)E Sigma | exact_checked | Positive-definite joint within-attempt noise; duplicate original attempt IDs rejected. |
| PJ-E366 | counting | joint target measurement package | S*=argmax_(cost(S)<=budget) min_k h_k^T(Sigma-Sigma_S)h_k | exact_checked | Declared finite hypotheses and at most18 candidate packages; exact feasible counts, ranks and tie population. |
| PJ-E367 | observability | zero-isolated-value synergy | VOI(A)=1/2, VOI(B)=10/21, VOI(C)=0; VOI(A+B)=21/32, VOI(B+C)=110/131 | exact_checked | Sigma=I2, h=(1,0), A=(1,0) noise1, B=(1,1) noise1/10, C=(0,1) noise1/10, budget2. |
| PJ-E368 | observability | joint package advantage witness | 110/131-21/32=769/4192 | exact_checked | Synthetic exact Gaussian allocation example; no empirical NFL gain inferred. |
| PJ-E369 | observability | loading-family zero-effect limit | min_h VOI(S;h)=0 if 0 belongs to loading hypotheses | derived | Covariance reduction PSD; a zero target loading has zero conditional source benefit. |
| PJ-E370 | decisions | contender-difference loading | h_(a,b)=H_a-H_b | definition | Frozen common source coordinates; only overlapping possible leaders need sensing under valid scenario bounds. |
| PJ-E371 | observability | rationalized fitted loading | norm(h_decimal-h_rational)_infinity<=declared_tolerance | exact_checked | Exact calculation for rational snapshot; coefficient discrepancy recorded; estimated loading remains empirically uncertain. |
| PJ-E372 | observability | uniform loading rationalization bound | abs(h^T D h-htilde^T D htilde)<=sum_ij abs(h_i h_j-htilde_i htilde_j)(S_ii+S_jj)/2 | exact_checked | 0<=D<=S in PSD order; exact bound valid for every declared package; fitted-loading uncertainty remains separate. |
| PJ-E373 | counting | rationalized package regret | raw_objective(S_raw_opt)-raw_objective(S_rational_opt)<=2 epsilon | exact_checked | Uniform raw-versus-rational objective discrepancy<=epsilon; weighted mean or minimum over declared loading hypotheses. |
| PJ-E374 | observability | target-information non-submodularity witness | VOI(C given empty)=0 < VOI(C given B)=110/131-10/21=1000/2751 | exact_checked | The declared Gaussian target-specific variance reduction is monotone; this exact example violates diminishing returns, so no generic submodular greedy guarantee follows. |
