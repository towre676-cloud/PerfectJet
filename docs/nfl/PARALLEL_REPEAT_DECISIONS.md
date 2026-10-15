# Repeat decisions: uncertainty, partial rankings and exact testing budgets

## What this parallel contribution does

This study extends PerfectJet's v0.14.0 stopped-flow measurements without changing the simultaneous movement-capacity, launch-timing or rookie-tracking transfer experiments. It asks a narrower operational question: when one measured attempt is used to predict another, which player comparisons remain distinguishable after measurement uncertainty is included, and what additional testing would resolve an ambiguous comparison under an explicitly stated model? The delivered components are a joint-vector calibration wrapper, interval-based partial rankings, a repeat-variance calculator and an exact population compiler for two-player testing plans. The empirical study uses the recovered owner checkpoint, not a substitute dataset or newly obtained competition files. This is development research on already inspected classes, not a new prospective holdout and not an established NFL scouting advantage.

The mathematical contribution is the connection between prediction geometry and navigable populations of possible testing decisions. Standard conformal calibration and Gaussian conditioning are not inventions of this project. Exact support calculations translate a prediction region into intervals for physical readouts. Rank bounds retain unresolved comparisons instead of forcing an ordering. Rational inequalities then define a population of admissible repeat plans, and a finite frontier plus a floor-sum tail supports exact counting, ranking, inverse ranking and cost minimization. Statistical assumptions and arithmetic conclusions remain separate throughout.

The parallel files are `src/perfectjet/replication_geometry.py`, `src/perfectjet/repeat_allocation.py`, `src/perfectjet/applications/nfl_scouting/repeat_decisions.py`, the two corresponding scripts, three new unittest files and `results/parallel_repeat_decisions/`. Existing numbered monograph chapters, registry identifiers, transfer modules, package version and the unrelated sextic-partner PR are left unchanged. This supplement can therefore be merged alongside those efforts without choosing between competing versions of their work.

## Data boundary and declared evaluation

The preparation receipt identifies checkpoint SHA-256 `2ade4c164b540b124583ff630e7ace485b8147aefb6136471e5eec210f881957`. The checkpoint is 45,733,866 bytes and retains the previously prepared official dataset. This run verifies that digest and the retained official-adapter and movement-extractor hashes before loading it. The execution receipt additionally binds every Python module in `src`, the runner, the package configuration and the installed scientific-library versions. A hash is provenance, not a security sandbox: arbitrary untrusted pickle files must not be loaded.

The measurement vector contains the three area-acceleration readouts at speed gates 2, 3 and 4 yards per second. Their units are yards per second squared. They come from overlapping windows within one attempt, so they are never counted as independent attempts. Complete vectors are available for 93 source players; 84 have two distinct complete forty-yard attempts. The source attempt-ID ordering defines the first and second vectors. It is not represented as a verified chronological ordering. The source extraction retains 531 windows, corresponding to 177 complete attempts.

The primary split uses 29 players from 2023 for fitting, 26 from 2024 for calibration and 29 from 2025 for evaluation. No NFL play outcome, career outcome or draft-success label enters this experiment. The prediction target is the second measured acceleration vector, not an unobserved innate trait. Training uses both directions of each attempt pair, with all rows from an original athlete kept in the same inner fold. Scaling, penalty selection and residual geometry are fitted only within the 2023 partition. Calibration labels select radii but not model parameters; evaluation labels affect neither. Tests explicitly perturb these labels to check those boundaries.

The model families are the raw first attempt, the inherited joint signal/noise shrinkage model and tuned multivariate ridge. Three uncertainty shapes wrap the identical ridge predictions: full covariance, its diagonal and an isotropic matrix. Ridge penalties are selected from 0.1, 1, 10, 100 and 1,000 using three original-athlete inner folds. The selected full-fit penalty is 10. Five penalties across three folds plus the final fit require 16 ridge fits per complete run. Shape estimation uses fit-partition out-of-fold residuals and a five-percent diagonal regularizer. Its internal selection may be optimistic; the separate calibration partition supplies the later rescaling.

## A pooled number concealed a cohort-specific calibration problem

An audit of the inherited earlier-class Gaussian covariance finds nominal 90-percent joint coverage for 20 of 26 players in 2024, or 76.92 percent, and 29 of 29 players in 2025, or 100 percent. Pooled across these classes, 49 of 55 observations are covered, approximately 89.09 percent. The pooled number looks close to the nominal target while concealing very different class-specific behavior. This is an empirical diagnostic, not proof that the Gaussian model is invalid in every population. It is sufficient reason not to label its intervals automatically as reliable player-level confidence statements.

The source-only primary split separately calibrates the radii on 2024. Every tested joint-region construction then contains all 29 measured 2025 targets. That observed coverage is not a demonstrated 100-percent future guarantee. A small evaluation set and a comparatively difficult calibration class can produce conservative regions. Crucially, none of the five projected joint regions resolves a player pair on the declared mean-acceleration readout. There are 406 dependent pairs among 29 evaluation players; there are not 406 independent evaluation subjects.

The raw-repeat mean squared error is 0.1439477549. Joint reliability shrinkage gives 0.1045583739, while ordinary multivariate ridge gives 0.1001589588. These squared errors average the three physical coordinates equally. On this single development class, ridge reduces error by approximately 30.42 percent relative to raw reuse of the first attempt, but that is repeated-measurement prediction, not an NFL performance gain. Reliability shrinkage does not beat the ordinary ridge control.

With the same ridge centers, calibrated region volumes are 14.6680552 for full covariance, 12.5671575 for diagonal covariance and 9.5028545 for the isotropic shape. All three cover the same 29 evaluation vectors. Full covariance therefore does not win this efficiency comparison: the isotropic region is about 35.21 percent smaller than the full-covariance region in this retained split. Volumes have cubed acceleration units and depend on the fixed physical coordinates. Comparing shapes is meaningful here because those coordinates, centers and coverage target are identical; it is not an argument that spheres are universally preferable to correlated regions.

The declared scalar readout is the equally weighted mean of the three acceleration coordinates. Directly calibrating this fixed scalar gives the ridge prediction a halfwidth of 0.5388842 yards per second squared, compared with 0.8980748 when the whole-vector ellipsoid is projected onto the same direction. Both contain all 29 observed scalar targets. The approximately 40-percent reduction is an expected benefit of protecting one prespecified question rather than every possible linear readout. It is not free protection for choosing a different question after viewing results. The scalar ridge intervals resolve only one of 406 pairs in this development sample. Their one observed correct comparison does not establish a reliable selective-ranking rate.

A complete original-player resampling sensitivity analysis runs 128 refits, with all 128 completing. Including the primary fit, that is 2,064 ridge fits, not 2,064 independent athletes. Copies retain their original group identifiers. Fitting retains resampled frequencies, but calibration takes one maximum score per distinct original identity. The resulting percentile envelopes are explicitly resampling sensitivities, not confidence intervals with asserted nominal coverage. In particular, deduplication changes the quantile resolution in each draw, so these outputs must not be advertised as an ordinary bootstrap confidence interval. Full per-draw aggregates are preserved, while individual predictions remain private.

## Exact calibration resolution and partial ranks

For a separately fitted center and positive-definite shape matrix C, the vector nonconformity score is the Mahalanobis distance

\[
s(y,\mu)=\sqrt{(y-\mu)^T C^{-1}(y-\mu)}.
\]

For m original calibration groups and miscoverage alpha, the noninterpolated split-conformal radius is the order statistic with index

\[
k=\left\lceil(m+1)(1-\alpha)\right\rceil.
\]

The implementation retains an infinite radius when k equals m+1. It does not interpolate, cap the index at m or treat duplicated athlete IDs as new information. If the calibration and future original-group scores are exchangeable conditional on the fitted model, the usual rank argument gives marginal coverage of at least 1-alpha. Different draft classes do not establish exchangeability automatically. No distribution-shift guarantee is added by relabeling the cohorts as calibration and evaluation.

For a linear physical readout h, the sharp interval over the entire ellipsoid is

\[
h^T\mu\;\pm\;q\sqrt{h^TCh}.
\]

Indeed, writing a point as mu plus C to the one-half times u, with norm of u at most q, reduces the extremum to Cauchy-Schwarz. The endpoint is attained in the direction C times h whenever the directional variance is positive. Containment of one vector simultaneously controls every linear loading on that vector, including loadings subsequently inspected. It does not give simultaneous coverage across an entire board of players.

For K players, a simple Bonferroni construction uses alpha/K per player. Its radius is finite only if

\[
m\geq\left\lceil K/\alpha\right\rceil-1.
\]

At a nominal 90-percent level, the requirements are 9 calibration groups for one player, 19 for a prespecified two-player pair and 289 for a 29-player board. Only 26 are available in the primary calibration class. Consequently this particular distribution-free board construction returns unbounded regions and no certified top-five selection. The number 289 is a resolution limit of this construction, not a universal lower bound on all possible ranking methods. Stronger assumptions, alternative joint constructions or a different decision target can change the requirement. Repeated attempts by the same calibration players cannot turn 26 identities into 289 new independent players.

Conditional on every score interval containing its target, the best attainable rank of player i is one plus the number of other lower endpoints strictly above i's upper endpoint. Its worst attainable rank is one plus the number of other upper endpoints at least as large as i's lower endpoint. Ties may be broken in either direction. These bounds are exact over the product of intervals; explicit choices of endpoint values attain them. They support possible versus guaranteed top-k membership without a forced total ordering. Their deterministic correctness must not be confused with a probabilistic guarantee that all input intervals contain their targets.

## What repeated testing can and cannot remove

Under a fitted independent-attempt Gaussian model, let S denote repeatable variation and N attempt noise. After m independent attempts, the latent-state conditional covariance is

\[
V_m=S-S(S+N/m)^{-1}S.
\]

For a new measured attempt, the predictive covariance is N plus V_m. The latent covariance tends to zero as m grows, including positive-semidefinite singular S, while next-attempt uncertainty tends to N. Thus unlimited repetitions need not make the next physical execution arbitrarily predictable. This distinguishes uncertainty about a repeatable latent mean from variability in a future observed performance.

In the 2023 fitted working model, the equally weighted readout has next-attempt variance 0.0873986 after one known attempt and 0.0695539 after two. The irreducible fitted floor is 0.0481775. Additional known repeats could reduce that variance by at most 44.88 percent relative to its one-repeat value under this model. The high-minus-low speed-gate contrast has a much higher fitted noise fraction: its one-repeat next-attempt variance is 0.6015540 and its floor is 0.4965114, leaving at most 17.46 percent reducible. These are model-based ceilings, not measured improvements from collecting third or later attempts. The covariance model was calibrated to distinct attempts, not independent speed windows.

A radius calibrated for one known attempt is not automatically calibrated for two, five or ten. The budget calculations therefore freeze the radius and centers explicitly and report a conditional planning result. A deployed adaptive retesting policy would require new data under its own sampling rule, an appropriate sequential or simultaneous guarantee, and a decision target whose value has been validated for scouting. This study does not silently transfer a one-attempt coverage statement to an adaptively selected repeat count.

## Counting the complete population of repeat plans

For a scalar repeatable variance s and attempt noise n, the conditional latent variance is sn/(n+ms). Next-attempt variance adds n. Consider two players with frozen positive mean gap g, common region radius q and respective variances v_a and v_b. Nonoverlap requires

\[
g>q(\sqrt{v_a}+\sqrt{v_b}).
\]

The engine avoids rounded square-root comparisons. For q positive, define D=(g/q)^2-v_a-v_b. The condition is exactly D positive and D squared greater than 4v_av_b. All coefficients and comparisons use rational arithmetic. Zero gaps, zero radii, zero signal, zero noise, unequal costs and strict boundary equality have explicit handling. No appeal to floating-point tolerance is needed for plan membership.

At each count for player A, feasible counts for B form an integer interval because predictive variance is nonincreasing with repeats. As A's count tends to infinity, its variance approaches the fitted floor. When the limiting minimum count for B is strictly feasible, it becomes the exact minimum beyond a finite A threshold. The compiler enumerates a bounded frontier and represents the remaining tail by a fixed lower count together with the budget's linear upper bound. Euclidean floor sums count the tail without listing its plans. If the frontier exceeds the explicit compilation limit, the implementation raises an error rather than returning an incomplete population.

The resulting object follows the existing population interface: `count()`, `rank(plan)`, `unrank(index)`, `sample(rng)` and `minimum()`. Rank and inverse rank use lexicographic order of the total attempt counts. Prefix counts and binary search navigate a huge tail. Sampling is uniform over the encoded population when its supplied integer random sampler is uniform. Positive costs ensure that all minimum-cost plans can be recovered from the frontier lower endpoints and the start of the tail. This is a concrete reuse of PerfectJet's exact-population approach for a measurement-planning problem rather than a separate arbitrary recommendation score.

A constructed example uses both signal variances and both noise variances equal to one, gap 23/10, radius one, one already known attempt per player and unit costs. The globally cheapest plans collect total counts (2,3) or (3,2), costing three additional attempts. Repeating each player to the same count requires (3,3), costing four additional attempts. The asymmetric optimum therefore saves one of four extra attempts, or 25 percent, in this specified mathematical example. This is not an observed 25-percent saving in NFL scouting operations.

With an additional-cost budget of 12, there are exactly 81 feasible plans, independently checked by exhaustive rational enumeration. For any integer budget B at least four, the count in this example is (B+1)(B+2)/2 minus ten. The excluded cells are (1,1) through (1,5), (2,1), (2,2), (3,1), (4,1) and (5,1). At B=10^30 the exact population is

\[
500000000000000000000000000001499999999999999999999999999991.
\]

It is represented by five frontier rows and one tail. The retained replay uses 707 exact membership predicates for construction and checks 67 large-index rank/inverse-rank round trips. The large budget is an arithmetic stress example, not a plausible number of football tests. Its purpose is to show that the decision population is navigable without enumerating all candidate plans.

## Tests, replay and preserved limitations

The repository has 377 collected test cases after adding 30 tests for this contribution. All 377 completed successfully across resumed test invocations; two earlier invocations reached the execution environment's wall-time limit without reporting a test failure. The public test receipt records the unique test identities and the resumed coverage rather than presenting partial logs as a completed single invocation. The new tests include 3,000 independently brute-forced floor sums, 360 small exact plan populations, 1,200 scalar-budget cases, 80 interval-ranking boxes checked at all vertices, 30 affine-coordinate transports and 40 sharp-support endpoint checks. They also check calibration resolution, duplicate identities, strict inequalities, unbounded intervals and training/calibration/evaluation isolation. These are executable arithmetic and software tests, not Lean kernel proofs.

On Windows, macOS or Linux, first install the editable package from its root with `python -m pip install -e ".[scouting]"`; after installation, the following Python script commands also work without the Unix-specific `PYTHONPATH=src` prefix. Run the public mathematical replay from the repository root with `PYTHONPATH=src python scripts/replay_repeat_geometry.py --output results/parallel_repeat_decisions/exact-population.json`. Run the restricted-data experiment with `PYTHONPATH=src python scripts/run_repeat_decisions.py --checkpoint PATH_TO_TRUSTED_CHECKPOINT --preparation PATH_TO_PREPARATION_JSON --out results/parallel_repeat_decisions --private PATH_OUTSIDE_REPOSITORY --refits 128`. The private output directory is required to be outside the public repository. Full real-data reruns need the recovered owner checkpoint; the public notebook can replay the exact mathematics and read the retained aggregate experiment without private data. Public and private packages preserve these distinct capabilities rather than claiming that the notebook independently reruns restricted inputs.

The strongest empirical conclusion remains limited: denoising helps this repeated-measurement target, but more elaborate covariance geometry does not outperform the strong simple control in the retained split, and the calibrated board is not discriminating enough to justify a complete ranking. The exact planning engine is operational under its declared model; an NFL scouting or betting edge is not established. The capacity-versus-timing and rookie-tracking work can use this extension to distinguish a predictive improvement from an actionable comparison, to state when a ranking is unresolved and to ask what additional observation would matter.

## Sources and novelty boundary

The recovered v0.14.0 source, `docs/nfl/STOPPED_FLOW.md`, `reliable_modes.py` and the owner preparation receipt are the sources for the inherited data and measurement definitions. The complete companion ZIP retains `results/parallel_repeat_decisions/study.json`, `nominal-audit.json`, all 128 per-refit aggregate rows in `refits.json`, `exact-population.json`, complete test identities and the hash-bound execution receipts, also consolidated losslessly in `run.json.gz`. The GitHub source contribution includes the smaller `PUBLIC_EVIDENCE.json` aggregate summary, containing source hashes, all primary model comparisons, refit-sensitivity summaries, exact-population evidence and the digest of that complete aggregate bundle. The notebook supports both representations. Individual player outputs and the trusted checkpoint remain only in the private continuation package.

For standard conformal prediction and its exchangeability-based rank argument, see Anastasios N. Angelopoulos and Stephen Bates, *A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification*, arXiv:2107.07511. Ellipsoidal multivariate conformal regions also predate this study; see Chen Xu, Hanyang Jiang and Yao Xie, *Conformal prediction for multi-dimensional time series by ellipsoidal sets*, arXiv:2403.03850. The present study does not implement that paper's sequential method or inherit its time-series coverage results. Its own exact support, rank-box and repeat-population derivations are stated above, with their assumptions exposed and their software independently tested on finite examples.
