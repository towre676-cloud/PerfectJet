# Movement languages: exact populations, uncertain phases and scouting transfer

Research engine release, October 14, 2026. This session supplies reusable infrastructure to the concurrent NFL scouting study. It does not replace that study's defensive-front notebook, receiver work, data or model outputs. The implementation and retained public receipts live in PerfectPower main. Restricted tracking rows, athlete-level features and predictions remain private. The public Movement Observatory uses synthetic trajectories and displays the current aggregate account.

## Why the arithmetic machinery transfers

PerfectPower's arithmetic modes describe finite words subject to state-dependent constraints. A height ceiling removes some transitions; accepted words are counted, ranked and sampled through a directed acyclic graph. The new movement language uses the same structural idea with different states: a state records how many ordered phases have been completed and the current frame boundary. An edge assigns one contiguous interval to the next phase. Minimum and maximum durations and optional boundary windows determine whether that edge exists. Every complete path is an allowed segmentation of the entire observation window.

There is no assertion that athlete motion is prime arithmetic or quantum mechanics. The arithmetic recurrence's Pauli lift motivates preserving order; the actual observation adapter uses classical tensor signatures and explicit-duration weighted inference. Both are established mathematical methods. The engineering contribution is their combination with exact finite populations, rank access, a rational reference calculation, phase-feature uncertainty, explicit budgets and a private-data transfer adapter compatible with the existing research.

## The weighted language

Let an edge e have log weight ell_e and vector reward r_e. A complete path pi has W(pi)=exp(sum_e ell_e) and R(pi)=sum_e r_e. The root partition is Z=sum_pi W(pi). The backward recurrence beta(v)=logsumexp_e[ell_e+beta(target(e))] computes log Z without enumerating paths; terminal beta is zero. A forward recurrence alpha gives edge marginal exp(alpha(source)+ell_e+beta(target)−log Z). For the unweighted observation, a separate integer recurrence C(v)=sum_e C(target(e)) gives the exact number of accepted paths. C at a terminal equals one. Parallel edges are labeled alternatives, even when they share endpoints.

Suffix counts implement lexicographic rank, inverse rank and uniform word sampling. Weighted sampling instead descends by normalized suffix mass. MAP decoding uses the maximum-sum recurrence. Additive reward means and variances are evaluated over the complete weighted language. The variance recurrence uses the law of total variance, avoiding subtraction of large nearly equal raw moments. Tests include a reward offset of 10^12 with a true variance of one. Each reward coordinate also has an all-path minimum and maximum. These support bounds are deterministic bounds over the specified language, not statistical confidence intervals.

Summing edge marginals across a phase interval gives framewise phase occupancy; summing by interval end gives the boundary distribution. The public summary supplies 5%, 50% and 95% model boundary quantiles, entropy and MAP mass. These are conditional on operational emission costs and duration constraints. They are not calibrated physiological probabilities. A separate Fraction-based API evaluates rational partition mass and rational raw moments on a supplied graph. It refuses floating weights and rewards rather than labeling approximate likelihoods exact.

The default compiler allows 1–16 ordered phases and 1–4096 frames, with 200,000 edges unless explicitly raised. Every phase has positive duration, every frame belongs to exactly one phase, and empty languages are reported explicitly. The generic DAG rejects non-topological edges, nonfinite weights, inconsistent reward dimensions and outgoing edges from accepting terminals. It supports up to 128 reward coordinates and 100,000 nodes. These are implementation budgets, not mathematical limitations of the recurrence.

## Retaining order in observations

The adapter first validates contiguous 10 Hz samples, finite coordinates, finite nonnegative reported speed and sufficient movement. It smooths coordinates, estimates geometric speed, acceleration and heading change, and interpolates heading rate from moving frames because heading is undefined at rest. It reports the fraction of frames with reliable moving heading and disagreement between reported and geometric speed. Gaps and duplicate timestamps are rejected; the implementation does not invent missing frames.

The observation path has four fixed-scale coordinates: normalized elapsed time, speed divided by 10 yd/s, acceleration divided by 5 yd/s², and absolute angular rate divided by pi radians/s. Bounded acceleration and angular-rate coordinates limit extreme derivative artifacts. These scales are fixed before any outcome analysis. The truncated piecewise-linear signature is built from tensor exponentials of increments and Chen concatenation. It preserves first-order changes, second-order signed areas and third-order event order. The extractor retains six second-order areas and six permutations of the three motion-coordinate indices, rather than feeding a large unrestricted tensor into a tiny cohort. Translation of the coordinate origin does not change the signature, and splitting a straight segment leaves its signature unchanged. Tests verify these identities and order reversal examples.

Four operational phase templates correspond to approach, braking, redirect and recovery. Their centers are fixed, not fitted to NFL outcomes. The first active window has at most 61 contiguous frames, with at least two frames per phase. Three sustained-onset definitions, 0.5, 1 and 2 yd/s, are evaluated. Their feature means and ranges are sensitivity summaries with equal scenario weights, not learned probability weights. Per-phase duration uncertainty, boundary widths and integrated acceleration/turn rewards expose ambiguous interpretations. The acceleration rate reported for a phase is expected integrated acceleration divided by expected duration; it is not the expectation of each path's duration-normalized rate.

## First real-data experiment

The adapter read the other session's existing eligible defensive-front rookie cohort, without modifying it, and the original Combine tracking. It used four shared drill names: PASS_RUSH_DRILL, RUN_THE_HOOP_DRILL, FOUR_BAG_AGILITY_DRILL and FRONT_START_WAVE_DRILL_AND_LATERAL_REACTION. It accepted 361 attempts, covering 74 players and 1,083 onset scenarios. Player counts are 23 from 2023, 22 from 2024 and 29 from 2025. Allowed segmentation populations range from 3,276 to 27,720 per scenario. The target is each player's mean observed pressure indicator within the supplied charted rookie-rush cohort. It is conditional on that cohort and its playing opportunities, not an unconditional career-success measure.

The conventional baseline contains fifteen recorded body, timed-test and NGS-score fields, NFL position and identical drill-availability indicators in every model. The fields include height, weight, hand size, arm length, wingspan, ten-yard split, forty, vertical, broad jump, three-cone, short shuttle, bench repetitions and three NGS scores. Source attempt features are aggregated by player and drill using medians. No NFL movement features or pressure labels enter source feature extraction.

Entire athletes are held out. Imputation, scaling, residualization against conventional traits, PCA and ridge choices are trained within the relevant folds. Four outer folds of the 2023–2024 athlete population use inner selection. A separate forward analysis selects configurations on 2023→2024 and refits on both classes before predicting 2025. The final configuration bank includes a baseline-only fallback, so extra movement coordinates are optional. That selection option does not guarantee improvement on an unseen cohort. An earlier mandatory-feature diagnostic is retained separately: forcing all features worsened development error by 18.1%, motivating the optional baseline design.

| Feature family | Earlier-cohort nested MSE | Relative change versus baseline | Exploratory 2025 MSE | Relative change versus baseline |
| --- | ---: | ---: | ---: | ---: |
| Conventional baseline | 0.000962767 | — | 0.000708857 | — |
| Kinematic | 0.000983556 | -2.16% | 0.000715504 | -0.94% |
| Ordered | 0.000963700 | -0.10% | 0.000710973 | -0.30% |
| Uncertain | 0.001032709 | -7.26% | 0.000714832 | -0.84% |
| Combined | 0.001065648 | -10.69% | 0.000654407 | +7.68% |

Positive relative change means lower error. The combined 2025 model improves MSE by 7.68%, from 0.000708857 to 0.000654407, while the nested development comparison worsens by 10.69%. Its 2025 fixed-prediction athlete bootstrap interval for the absolute gain is about [0.000004166,0.000110012]. This interval omits model-refitting uncertainty and multiplicity from adaptive experiments; the 2025 draft class has already been inspected in the parallel program. Therefore it is exploratory evidence, not an untouched-test confirmation. Neither the order-only nor uncertainty-only family produces a supported general advantage here. All outcomes remain in the receipts rather than presenting only the favorable comparison.

The observation engine is useful independently of this prediction result: it makes phase ambiguity measurable and supplies a common, testable interface for later drill-specific calibration. The experiment does not yet establish that a chosen movement trait causes improved pressure production, that the effect generalizes across classes, or that the Kaggle challenge has been solved. The other session retains responsibility for its notebook and scouting claims; this package supplies an additional engine and clearly scoped aggregate comparison.

## Population scale

The public synthetic benchmark compares segmentation counts against binomial coefficients and performs 1,000 rank round trips per case. Posterior computations use floating arithmetic; the count and rank identity remain integer-exact.

| Frames | Ordered phases | Exact segmentations | Graph edges | Build seconds | Moment seconds |
| --- | ---: | --- | ---: | ---: | ---: |
| 61 | 4 | 34220 | 3,719 | 0.0122 | 0.0086 |
| 120 | 6 | 182637273 | 28,085 | 0.1102 | 0.0972 |
| 200 | 8 | 2203959847089 | 116,828 | 0.5291 | 0.5436 |
| 300 | 12 | 35513096590299098589 | 435,754 | 2.6624 | 2.7661 |

These are synthetic workloads, not scouting-accuracy comparisons or universal speedup claims. Four thousand exact rank round trips passed. Eighteen focused tests cover exhaustive finite-path inference, rational weights, all-boundary normalization, duration constraints, empty languages, numerical stability, source validation, rotation/translation invariance, signature concatenation, baseline fallback and athlete-leakage checks. The new numerical feature compiler and regression are not Lean-verified. Existing ArithmeticModes finite-language and transport theorems provide a formal framework, but no generic refinement proof links this Python compiler to those theorems.

## Run and integrate

The standard-library core runs with PYTHONPATH=python python -m perfectpower.movement_language examples/movement_language/phase.json --rank 0 --samples 3 --seed 7. Its JSON output contains exact count strings, numerical phase uncertainty and complete sampled segment intervals. Windows PowerShell users can set $env:PYTHONPATH="python" before the same Python command. The optional observation adapter and transfer script require requirements-movement.txt. Make targets run tests and public benchmarks.

The private-data runner accepts --data, --cohort, --private-out and --aggregate. The cohort is the explicit existing eligible player-play table; the supplied input's hash appears in the aggregate receipt. Athlete-level features and predictions are written only to the separate private output directory. The reusable interface is attempt_features(time_seconds, coordinates_yards, speed_yards_per_second), or ensemble_features for onset sensitivity. A notebook can join returned features by its own player/event keys without changing this engine. Restricted raw or per-player files must not be added to the public repository or archive.

This session owns movement_language.py, movement_features.py, run_movement_transfer.py, the associated tests, public synthetic examples and the Movement Observatory. It leaves the other session's front-transfer, receiver, phase-channel and notebook modules untouched. Next work should calibrate phase templates against drill-specific source annotations, test a baseline-preserving residual correction inside nested folds, and evaluate stability across predeclared cohorts and target definitions. Synthetic order controls can verify that a feature reacts to chronology, but only held-out NFL comparisons can establish a scouting benefit.

## Mathematical sources

Chevyrev and Kormilitzin, A Primer on the Signature Method in Machine Learning, https://arxiv.org/abs/1603.03788, develops path signatures and their order-sensitive use in learning. State Duration and Interval Modeling in Hidden Semi-Markov Model for Sequential Data Analysis, https://arxiv.org/abs/1608.06954, supplies explicit-duration sequence-model context. The current phase graph is a finite ordered explicit-duration specialization. These established foundations are credited; no novelty claim is made for forward–backward inference or Chen signatures themselves. The application and implementation must earn their value through the retained tests and future independent scouting results.
