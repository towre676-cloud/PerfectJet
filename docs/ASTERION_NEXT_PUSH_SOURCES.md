# Asterion next-push primary sources

Reviewed on 20 October 2026. This note separates published theorems, the existing exact Asterion certificates, and the new acceptance criteria in [ASTERION_CLOSURE_AUDIT.md](ASTERION_CLOSURE_AUDIT.md). Source identifiers resolve in [asterion_frontier_sources.json](asterion_frontier_sources.json). They supplement the earlier source manifest. No worldwide priority claim is made.

## 1. Higher-weight arc relations

Song–Zeng's June 2026 paper remains at v1 on the reviewed arXiv page. Theorems 1.2 and 1.4 establish its freeness obstruction; Section 6.3 specifies the old E8 mixed quotient and gives its contradictory dimension bounds. The paper does not classify the infinite differential kernel. The project's explicit null lift and complete conformal-weight-four calculation should be attributed as concrete certificate work alongside that published non-freeness theorem. [AST-S007](https://arxiv.org/html/2606.14407v1)

A genuine contemporary follow-up is Kanade's 17 June 2026 type-A paper. Its introduction explicitly cites the E8 counterexample. Lemma 12 and Theorem 39 complete a leading-term computation using an all-degree combinatorial Hilbert comparison; finite Buchberger experiments alone are not the termination proof. The transferable idea is to apply an analogous proof to the **augmented** E8 arc quotient, because the unaugmented E8 algebra is already known to fail freeness. [AST-S034](https://arxiv.org/html/2606.19234v1)

Gaberdiel–Gannon had already computed the E8 C2 space of dimension 4,125 and its finite-module content, while Zhu's algebra has dimension one. That earlier anomaly must be distinguished from the later kernel of the differential arc map. [AST-S035](https://arxiv.org/pdf/0811.3892)

Laurie's published 2025 construction supplies a concrete E8 affine crystal target. Sections 3.2 and 3.3.2 give energy and column data; Theorem 4.10 identifies reduced Young walls with the level-one basic crystal. A weight-preserving map from proposed normal monomials to these walls could support an all-degree character proof. Neither the existence of the crystal nor agreement of its first coefficients proves that map. [AST-S036](https://arxiv.org/pdf/2311.03905)

The search used exact arXiv identifiers, the phrases “E8 classically free”, “arc kernel”, and related higher-weight and Gröbner queries, including recent-source filters. It located the type-A follow-up and the older E8 combinatorics, but no primary source in that search establishing a complete higher-weight E8 arc-kernel presentation. This is a bounded retrieval result, not proof that no such work exists. Full generation remains a project gate until an actual theorem or counterexample is supplied.

The finite character engine uses the classical Freudenthal recursion and Weyl-chamber uniqueness, explicitly reviewed in Cavallin's introduction and Section 2.1. His conditional improved formula is a different algorithm; the implementation does not claim to use it. [AST-S053](https://arxiv.org/html/1603.07196v2)

The affine-VOA construction of the 3,876-dimensional Chayet–Garibaldi algebra is also established prior work, with a January 2026 revision. Its symmetrized mode-one product on symmetric weight-two states is useful comparison data; it is neither the C2 multiplication nor the Li differential relation ideal. [AST-S048](https://arxiv.org/pdf/2503.24103)

## 2. Level-four five-dimensional monodromy

Feingold's Theorems 6.1–6.2 imply equality of tensor and fusion coefficients when the level is at least the highest-root pairing of the sum of the two highest weights. For two adjoint E8 weights this threshold is four. Thus the five multiplicity-free channels are available at level four. This application concerns the four-adjoint conformal-block fiber, not the holomorphic level-one vacuum VOA. [AST-S012](https://arxiv.org/pdf/math/0212387)

Belkale's Theorem 1.1 gives a preserved positive metric on genus-zero configuration-space conformal blocks for every simple Lie algebra at integral level. Section 8.1 gives the split-Casimir KZ equation. Section 10 explains projective descent to the moduli space. An exact identification of our five-dimensional fiber is required. For the selected linear lift, unit-modulus determinants then remove any positive scalar ambiguity in metric preservation. [AST-S037](https://arxiv.org/html/1101.5846v3)

Two low-dimensional primary results have different scopes. Tuba–Wenzl's Theorem 2.9 classifies irreducible B3 representations through degree five using spectral and determinant-root data; its input must include actual half-braids. Rowell–Tuba's Lemma 5.1(d) is more directly applicable to the pure-loop pair: finite primitive degree-five complex linear groups have no projective element of order 17. That lemma is independent of a braid-group extension. Their Theorem 2.1(d)(iv) also gives an infinite-image test for primitive five-dimensional B3 images of sufficiently large projective generator order. [AST-S039](https://arxiv.org/pdf/math/9912013), [AST-S038](https://arxiv.org/pdf/0806.0168)

The compact closure requires another argument. Zeier–Schulte-Herbrüggen's reviewed degree-five rows list only the fundamental or dual representation of su5, the vector representation of so5, and the highest-weight-four representation of su2. Both proper cases preserve a symmetric form. The completed project proof handles finite components and imprimitivity explicitly, after certifying the actual level-four projector graph; the source table alone would not establish density. Their separate 2014 erratum concerns an alternating-square table; it does not change the reviewed degree-five list. [AST-S041](https://arxiv.org/pdf/1012.5256)

Larsen–Rowell–Wang's Propositions 2.3–2.4 give a useful compact-closure template under a generating-conjugacy-class/no-cycle hypothesis. That hypothesis should not be silently transferred to two pure loops conjugate only by an external crossing matrix. The audit instead states the prime-dimensional Clifford argument directly. [AST-S040](https://arxiv.org/pdf/math/0506025)

The separate residue-algebra argument uses the classical regular-singular Schlesinger density theorem, reviewed in Mitschi–Singer's introduction. Its parameterized Kolchin theorem has a different statement; the implementation does not substitute it for a pointwise closure theorem. [AST-S052](https://arxiv.org/html/1106.2664v2)

## 3. E8 elliptic and dynamical constructions

There are three existing constructions to distinguish.

1. Etingof–Varchenko's equation (4.7) and Theorem 4.2 give the all-type classical dynamical elliptic r-matrix with spectral parameter, including E8. Its coefficients include the rank-eight Cartan parameter and theta quotients; its equation contains dynamical derivatives. [AST-S042](https://arxiv.org/pdf/q-alg/9703040)
2. Toledano Laredo–Yang's Theorem 2.5 constructs a universal root-system KZB connection. A realization must satisfy the rank-two root relations, commuting x and y relations, their mixed bracket, and root-orthogonality relations. The completed connection is not automatically a finite adjoint matrix. Their Theorem 5.15 also records nonquadratic elliptic braid Lie structure. [AST-S043](https://arxiv.org/pdf/1801.10259)
3. Their elliptic Casimir paper realizes this universal algebra in a completed deformed double current algebra; Theorem 3.6 gives the map, while Theorems B–C extend it in the modular direction. The reviewed version labels its quantum-toroidal monodromy identification as Conjecture 1.4. Its proved flatness and degeneration results must be kept separate from that conjecture. [AST-S044](https://arxiv.org/pdf/1805.12261)

Gautam–Toledano Laredo provide the all-type elliptic quantum-group representation framework through half-currents and a quantum-loop functor. Their spectral-domain and coefficient-field restrictions are part of the construction. A finite E8 specialization therefore needs an explicit representation and its shifts; assigning E8 labels to a type-A nondynamical elliptic matrix does not meet this requirement. [AST-S020](https://arxiv.org/pdf/1707.06469)

These references supply strong established starting points. The current push completes a classical E8 dynamical realization and an exhaustive root/Fay reduction, with exact finite nome coefficients. Felder's Section 2 gives the original dynamical compatibility equation; Etingof's Section 2.7, Example 3 fixes the plus-theta convention used in the implementation and explicitly permits every reductive algebra. [AST-S050](https://arxiv.org/pdf/hep-th/9407154), [AST-S051](https://arxiv.org/pdf/math/0207008)

A quantum exchange realization, explicit KZB connection and analytic numerical evaluation bounds remain separate contributions. A finite scalar period calculation is a useful normalization seed but does not construct the rank-eight KZB system.

## 4. Charged theta functions and the arithmetic boundary

Sakai's older equations (2.8)–(2.11) identify the E8 root-lattice theta function as the weight-four index-one Jacobi form and specify the rank-eight elliptic-variable transformation laws. These are the appropriate conventions for the charged character and its heat equation. [AST-S045](https://arxiv.org/pdf/1706.04619)

The current ring result is much stronger than the older paper's historical discussion: Sakai's published 2026 revision proves an isomorphism with joint covariants of a binary quartic and sextic. Theorems 4.17–4.18 give the map, and the paper obtains 194 minimal generators. Finite generation of this weak Jacobi ring is therefore established literature. It should not be listed as an unresolved Asterion discovery target. [AST-S046](https://arxiv.org/pdf/2410.12907)

De la Harpe–Pache–Venkov explicitly relate the strength-eight E8 shell condition to a Ramanujan tau zero. Their harmonic theta argument explains why every shell has strength seven while the next even moment is governed by a weight-twelve cusp form. A computed finite moment defect is an exact instance of that known relation. Universal tau nonvanishing would meet Lehmer's conjecture and cannot follow from a finite shell range. [AST-S047](https://www.unige.ch/math/folks/delaharpe/articles/10HaPaVe2006.pdf)

## Review boundaries

All theorem applications above cite primary texts with reviewed passages in the JSON manifest. The historical Dynkin reference is retained only as classification provenance; its full Russian proof was not reviewed here. Unimplemented comparisons, finite-range certificates and theorem-dependent deductions retain separate statuses in the closure audit. The existing 64 stable programme identifiers are preserved there without silently rewriting their original acceptance criteria.
