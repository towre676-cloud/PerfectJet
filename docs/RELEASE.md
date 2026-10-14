# PerfectJet 0.9.0

This release turns the partner evidence into certified statements and finds an explicit degree-12 partner.

- **Slice certificates** (`invariants.grid_certificate`): an identity between covariants of the same degree d, order and weight holds for every binary sextic once it holds on xy(x-y)(x^3+px^2y+qxy^2+ry^3) for (p,q,r) in {0..d}^3. The slice's GL2-orbit is dense, and a polynomial of degree at most d in each variable that vanishes on that grid is zero. The following identities are certified this way:
  - cubic partner: det L_3 = (A^2-B/6)/16, with 125 points;
  - quartic covariant partner: (f,(f,f)_4)_3 = (f,(f,f)_4)_5 = 0, with 64 points;
  - degree-12 identities, with 512 points, below.
- **Degree-12 partner on A^2 = 25B/96**: the drop curves of a second, non-symmetric family satisfy the same relation. Random sextics placed on the hypersurface all gain a degree-12 partner. The partner is the covariant G = 144A^2 f^2 + 216/5 A iH + 24A f(f,i)_2 - 9/4 i^3 - 9 Delta H + (f,i)_2^2, with H = (f,f)_2. For every sextic, (f,G)_3 = -432 (A^2-25B/96)(f,H)_1 and (f,G)_5 = 25920 (A^2-25B/96)(f,i)_1. The converse is open.

The registry has 339 entries. Chapters 15, 23 and 24 were updated, and `perfectjet invariants` reports the certificates.

# PerfectJet 0.8.0

This release adds a solution-carrying arithmetic compiler (`quadratic.py`) for k y^2 = a n^2 + b n + c over the integers.

- **Transport with the way back**: X = 2an+b, Y = y gives X^2 - 4ak Y^2 = b^2 - 4ac. The reconstruction is n = (X-b)/(2a), with the congruence X = b mod 2a as an explicit condition.
- **Branches with completeness status**:
  - a = 0 gives residue classes of y;
  - definite forms, square D and N0 = 0 have finitely many norm solutions;
  - the indefinite nonsquare case is a generalized Pell equation. Nagell's bounds give a seed in every class, so seeds times unit powers are all solutions.
- **Navigable population**: admissible positions are periodic along each orbit. The compiler answers hits below any bound and the j-th hit at remote indices with exact integers, replaying each returned n in the original equation.
- **Engine adapter** `arithmetic_problem` returns the unified report.

Tests compare 158 equations with brute force, across every branch. Pell7, n^2+7 = 2y^2, has hits 1, 5, 11, 31, 65, 181, and so on. Its 1000th orbit hit has 766 digits. The square-triangular equation gives 0, 2, 14, 84, 492, 2870, and so on. The registry has 336 entries. The CLI has a new command, `perfectjet quadratic`. Higher-degree equations (Thue, elliptic) remain outside the compiler.

# PerfectJet 0.7.0

This release explains the partner strata by invariant theory (`invariants.py`).

- **Clebsch invariants** A, B, C, D of degrees 2, 4, 6, 10, computed from unnormalized transvectants. They scale by det^(3k) under GL2, which the tests check. Equality in weighted projective space P(1,2,3,5) decides GL2-equivalence over the algebraic closure for squarefree sextics.
- **Cayley-Sylvester counts** of covariants by degree and order. They give the dimension facts the proofs below use.
- **Cubic partner theorem**: det L_3(f) = (A^2 - B/6)/16 for every binary sextic. A sextic has a cubic correction-free partner exactly when B = 6A^2.
- **Quartic covariant partner**: (f,(f,f)_4)_3 = (f,(f,f)_4)_5 = 0 for every binary sextic, because there are no covariants of degree 3 and order 4 or 0. This explains the generic degree-4 partner. It is active unless the Poisson bracket vanishes, as at the perfect cube.
- **Drop curves as invariant loci** on the two-parameter surface. Reducing weighted monomials in A, B, C, D modulo each curve ideal gives the lowest-weight relation:
  - degree 3: A^2 = B/6;
  - degree 12: A^2 = 25B/96;
  - degree 8: AB^2 + BC/6 - 9D/2 = 0.
- **Named exceptional points**:
  - (0,15) is equivalent to x^6+y^6, the family origin, and has the same partner profile;
  - (0,-5) is equivalent to the octahedral sextic xy(x^4-y^4);
  - (4,6) and (24,-9) both lie on B = 6A^2 but are not equivalent to each other.

Chapters 15, 23 and 24 were updated; the registry has 333 entries. The CLI has a new command, `perfectjet invariants`. Whether the degree-8 and degree-12 relations hold beyond this family is open.

# PerfectJet 0.6.0

This release adds the Combine scouting adapter, `src/perfectjet/applications/nfl_scouting`, and fixes its analysis in docs/nfl/PROTOCOL.md.

- **Events with lineage** (`events.py`): turns detected as a speed minimum followed by a direction change; eta = normalized travel in the outgoing direction over 0.5 s, with all six smoothing/alignment branches kept as a sensitivity range; an outcome-blinded, stratified review sheet with difficult examples.
- **Identifiability and readouts** (`readouts.py`): a training-fitted demand frame and reference distribution; the exact test h_q in row(X_i) for each athlete; a linear mixed model fitted by EM on training athletes; a random-intercept primary readout, a pooled secondary readout with pooling reliance, split-half repeatability, and the next condition that most reduces readout variance, marked repeat or new direction.
- **Targets** (`outcomes.py`): cross-fitted context residuals for training athletes, training-only models for test athletes, training-only shrinkage, and a leakage check on every run.
- **Validation** (`validate.py`): athlete-grouped temporal folds; identical availability indicators, imputation and tuning for baseline and movement models; G=1-MSE_movement/MSE_baseline; fixed-prediction and full-refit intervals (event extraction included); diagnostics by position, class, play count and single-athlete influence; a frozen shortlist rule.
- **One command** (`perfectjet nfl` or `python -m perfectjet.applications.nfl_scouting`): results.json with source hashes, code revision, configuration hash and folds; report.md; cards.json; review_sheet.csv; three SVG figures.
- **Data contract** (docs/nfl/DATA_CONTRACT.md): CSV layout through a column mapping, availability dates enforced, a join and chronology audit.

On synthetic data the pipeline recovers a planted signal and reports none under a null signal; a retained synthetic run is in results/nfl-synthetic. Synthetic results are never evidence about football. No real-data scouting advantage is claimed: the data are not in this repository, and the get-off definition must be confirmed before use.

# PerfectJet 0.5.0

This release turns the partner surface into active strata and adds the first pieces of the adaptive engine.

- **Active strata** (`strata.py`): each correction cell is refined by the joint cells of [L_N;P_N], so every stratum carries kernel, active and commuting dimensions. At rational points the module builds a basis of the active quotient and of the commuting part and replays each partner with exact transvectants. A Bareiss determinant of the Sylvester matrix gives the sextic discriminant on the surface (total degree 8), and each stratum is labelled repeated-root, squarefree or generically squarefree. Findings:
  - the perfect cube (0,3) adds no active capacity in degrees 4 to 10; its extra kernel is powers of x^2+y^2, and in degree 4 the generic active partner becomes commuting;
  - (+/-16,-9) gains one active partner in every degree 3 to 12; in degree 6 it is xy(x-y)^4;
  - new rational exceptional points on drop curves, found by a bounded-height scan: (+/-4,6), (+/-24,6), (+/-24,-9) in degree 3; (+/-11,6) in degree 8; (+/-4,-3) and (+/-32/25,-9/5) in degree 12. All are squarefree except (+/-4,-3), which has one double root.
- **Rational roots for large coefficients** (`loci.py`): when the rational-root-theorem candidate set is too large, Sturm bisection isolates real roots below the 1/D^2 separation and the simplest rational in each interval is tested exactly.
- **Readout identifiability** (`readout.py`): h in row(X) with estimator weights, or a two-fit witness; demand-supported readouts; the smallest identifying set of candidate conditions; exact Gaussian value of information with each candidate marked repeat or new direction.
- **Certified decisions** (`decisions.py`): settled choice, refinement of overlapping contenders only, and an exact replay of e_{t+1}=A e_t+(AV-VG)z_t+(B-VH)u_t with an infinity-norm bound.
- **Adaptive engine** (`engine.py`): monomial closure that adds only residual-implicated monomials and extracts the minimal pullback-closed space, or stops on degree growth; adapters for sensing, readouts, integer systems and partners; every adapter returns the same representation-and-obstruction report.

Chapters 08, 15, 20, 22, 23 and 24 were updated; the registry has 321 entries. The CLI has four new commands: `strata`, `readout`, `decisions` and `engine`. No new Lean verification is claimed. The curve point lists are bounded-height scans, not complete rational point sets.

# PerfectJet 0.4.0

This release extends rank loci from one parameter to several.

- **Exact Groebner engine** (`parametric.py`): Buchberger with the product and chain criteria. It returns reduced bases in graded reverse lexicographic or elimination order. It also provides Rabinowitsch saturation, Krull dimension from leading monomials, and rational points of zero-dimensional ideals by lexicographic elimination.
- **Comprehensive rank cells** (`parametric.py`): Gaussian elimination over Q[t1..tk] that branches on whether each pivot is zero. Each cell is stored as V(S) minus V(N) with S already saturated, so the cell is nonempty exactly when S is not 1. Bareiss division keeps degrees low. The leaves partition parameter space, over the algebraic closure, into cells of constant rank. On a grid, every point lies in exactly one cell, and the cell's rank equals direct evaluation.
- **Two-parameter partner surface**: f=x^6+y^6+a x^3y^3+b(x^4y^2+x^2y^4), degrees 3 to 12, about 1.4 seconds in total. The b=0 slice reproduces every one-parameter point. New rational exceptional points:
  - (+/-16,-9), where f=(x-y)^4(x^2+4xy+y^2), in degrees 5, 6, 7, 9, 10 and 11;
  - (0,3), where f=(x^2+y^2)^3, in degrees 8, 10 and 12;
  - (0,15) and (0,-5), which are squarefree and still exceptional.

  Degree 3 has a whole drop curve. Degree 8 contains the line b=0, which explains the C3 degree-eight partner. These factorizations are checked with the package's own polynomial arithmetic.

The registry has 309 entries. Chapters 15, 22, 23 and 24 were updated, and chapter 24 proves the cell decomposition. The CLI has a new command, `perfectjet surface`, and the report includes the surface receipt. Local validation ran 78 unittest methods, all passing. No new Lean verification is claimed. The full seven-coefficient incidence variety remains open.

# PerfectJet 0.3.0

This release adds four executable kernels.

- **Hermite normal form** (`lattice.py`). `hermite_form` returns H=UB with U unimodular. `same_lattice` decides row-lattice equality by comparing Hermite forms. The tests check shape and reduction, invariance under random unimodular mixing, and agreement with mutual membership decided by integer solvability.
- **Multi-output word-Hankel realization** (`realization.py`). `realize(..., outputs=k)` stacks output coordinates into the Hankel columns and returns one shared state with a matrix-valued beta. A stacked rank can exceed every single-output rank, and a test shows this.
- **One-parameter rank loci** (`loci.py`). For a matrix over Q[t], `rank_locus` returns the generic rank over Q(t), the exact drop locus, and the rank on each locus factor. It never enumerates minors: one nonzero minor bounds the locus, and elimination over Q[t]/(squarefree minor) splits at zero divisors. The tests compare it with the gcd of all minors, with planted loci, and with direct evaluation. `partner_loci` applies it to the C3 sextic family. It rediscovers lambda=40/7 in degree 5, together with its mirror -40/7, and certifies that 0, +/-20 and +/-40/7 are the only rational exceptional parameters for degrees 3 to 12.
- **Adaptive local sieve** (`sieve.py`). The sieve keeps the residues n mod q for which F(n) is a d-th power residue mod q, combines them by CRT, and chooses moduli greedily by density drop per unit cost. It returns exclusion witnesses. The tests check soundness against brute-force hits, independence of test order, that a polynomial identity excludes nothing, and that density decreases strictly at each step.

The registry has 305 entries, and the adaptive-sieve row changed status to exact checked. Chapters 03, 04, 06, 15, 22, 23 and 24 were updated. The CLI has two new commands, `perfectjet loci` and `perfectjet sieve`, and the report includes both receipts. Local validation ran 65 unittest methods, all passing. No new Lean verification is claimed.

# PerfectJet 0.2.0

This release adds three exact kernels that 0.1.0 described as missing.

- `lattice.py` adds Smith normal form with explicit unimodular transforms, integer solvability of Bx=b, integer kernel bases, and the saturation index of a generated lattice. A failed integer system returns a certificate row y. When yB is integral and yb is not, the system fails over Z; when yB=0 and yb is nonzero, it already fails over Q. An unsaturated lattice returns an integral witness in its rational span that it does not generate.
- `realization.py` builds a minimal linear representation from a finite word-Hankel block. The model is exact on that block. Agreement on longer words is a held-out check, and a disagreement is returned as a witness word.
- `realization.py` also adds coarsest exact lumping. It discovers the aggregation R satisfying RA_c=Abar_c R and H=Hbar R for every cost matrix, starting from the output partition. Every valid lumping refines it.

The registry has 300 entries. The Smith form, integral solvability, and word-Hankel rows changed status to exact checked. Five entries were added: the infeasibility certificate, saturation index, integer kernel, Hankel realization, and coarsest lumping. Existing equation and topic IDs are unchanged. Chapters 04, 06, 22, and 23 describe the new kernels. Chapter 24 gives written proofs for the Smith form, the integer certificates, the Hankel construction, and coarsest-lumping uniqueness. The CLI has two new commands, `perfectjet lattice` and `perfectjet realization`, and the report includes both receipts.

Local validation ran 49 unittest methods, 34 retained and 15 new. Each new kernel is compared with an independent route:

- invariant factors against gcds of all k-by-k minors;
- integer infeasibility against exhaustive box search, with the certificate checked separately;
- integer kernel bases against brute-force kernel vectors;
- saturation index against maximal-minor gcds;
- recovered Hankel dimension against generic random representations of dimensions 1 to 3, a redundant three-state model, and an independent sequence Hankel rank;
- coarsest lumping against enumeration of every set partition of up to five states.

These are exact finite checks and written arguments. No new Lean verification is claimed. Hermite form, multi-output or numerical Hankel discovery, and the formal frontiers listed in chapter 23 remain open.

The v0.2.0 ZIP and its manifest are rebuilt by `scripts/build_release.py`, which now reads the version from the package. The v0.1.0 ZIP is retained unchanged. GitHub Actions status must be read from GitHub.

# PerfectJet 0.1.0 (retained)

The first master release preserves the categorized historical audit, both equation/archival passes, and both enhancement programs. It contains a25-chapter monograph,295equation entries,416topic entries, eight archived source extracts, a dependency-free Python library, examples, and reproducible exact receipts.

Local validation:34unittest methods passed, including exhaustive small selection populations and rank/unrank/tie comparisons; rational feature closure; partial-machine behavior; hidden-target witnesses; corrected energy source signs; finite-jet rejection; exact transvectant families and active dimensions; cyclotomic coefficients/convolution/recurrence; cubic-ring inverses and coefficient identities. The corrected PSG root is floating numerical evidence. Counts of methods are not counts of all looped cases.

Written mathematical arguments accompany the kernels. No new Lean verification is claimed. Original archives can contain stronger unsupported claims and remain separated from corrected canonical content. External numerical reports,large upstream data,chemical models,BLAST adapters,scouting/betting claims,and live applications are documented with boundaries rather than advertised as reproduced implementations.

The ZIP includes all eligible repository files and a manifest with per-file hashes. It excludes git internals,caches,and prior ZIPs. GitHub Actions status must be read from GitHub; local success does not assert a remote run passed. The original PerfectJet repository was empty and the release is published to main.
