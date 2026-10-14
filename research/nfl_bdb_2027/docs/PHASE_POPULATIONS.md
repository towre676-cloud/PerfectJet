# Movement phase populations: an exact calculation and an exploratory transfer test

October 14, 2026. This extends the PerfectPower finite-language adaptation documented in `ORDERED_MOTION.md`. It sums weighted constrained movement histories instead of selecting a single segmentation. Arithmetic primes, Pauli phases and Lean arithmetic theorems supply no physiological or predictive guarantee. The contribution is a reproducible real-valued sum-product calculation and a fair numerical test of its football value.

## Population and measurement

The fixed defensive-front NFL cohort contains 74 DE/DT/NT/OLB rookies, 45 from 2023/2024 and 29 from 2025, with 14,665 eligible charted regular-season rush records. Eligibility, snap reconstruction and outcome limitations are retained from `SCOUTING_FRONT.md`. The pressure target is the indicator of a supplied finite pressure timestamp among finite get-off-charted records. Missing pressure times do not become a separately estimated censored survival outcome. The source filter yields 361 skill attempts from those same 74 athletes: 143 pass-rush, 76 hoop, 71 four-bag and 71 lateral-reaction. Sprint profiles already measured in the prior study remain available.

For each attempt, retain the first up-to-five seconds after three consecutive speeds above each of 0.5, 1, 1.5 and 2 yards/s. Reject irregular sampling or nonfinite channels. The median span of these onsets is 0.5 seconds, the 90th percentile 1.7 seconds and the maximum 3.8 seconds. This is substantial compared with a 0.1-second sampling interval. Seven-frame cubic position smoothing supplies velocity direction; supplied speed supplies tangential acceleration by differentiation. Suppress angular rates below geometric speed 1 yard/s and cap absolute rotation at 4π radians/s. These operational decisions do not identify the official starting cue or plant frame.

Use normalized channels z=(s/10, (ds/dt)/10, min(|dθ/dt|,4π)/π). Rotation/reflection/translation of the coordinates preserves these channels. Acceleration here is tangential speed change, not the magnitude of the supplied acceleration field, and no physical force or energy is inferred from the geometric proxies.

## Weighted constrained histories

Let q_t be one of four phases: approach, brake, redirect and recover. Allow only q_t−q_(t−1) in {0,1}, require q_0=0 and q_(n−1)=3, and give every permitted path equal base weight. There are C(n−1,3) paths, up to 19,600 in a 51-frame window. The base path measure induces a duration prior; it is not a uniform prior over physical athletes or an empirically identified duration distribution.

For normalized acceleration a and rotation w, use costs

\[
c_t(k)=\frac{1}{2T}\{a_t^2+w_t^2,\;(a_t+0.5)^2+w_t^2,\;a_t^2+(w_t-0.5)^2,\;(a_t-0.5)^2+w_t^2\}_k.
\]

A path's weight is exp(−Σ_t c_t(q_t)). The forward recurrence F_t(k)=exp(−c_t(k))[F_(t−1)(k)+F_(t−1)(k−1)], with forbidden transitions set to zero, computes the partition Z=F_(n−1)(3). The matching backward recurrence gives frame marginals p_t(k)=F_t(k)B_t(k)/Z. Implement both in log space. Complexity is linear in frames and states; exact enumeration on a small trace independently verifies the result.

Features include four expected occupancy fractions, three phase-conditioned channel means per phase, and mean frame-occupancy entropy. This entropy measures ambiguity of individual frame assignments, not the entropy of complete paths. Three signed channel areas, one for each pair of speed, acceleration and rotation, measure chronology:

\[
A_{ij}=\frac12\sum_t\bigl[\bar z_{t,i}\Delta z_{t,j}-\bar z_{t,j}\Delta z_{t,i}\bigr].
\]

Evaluate T=0.5,1,2 for each valid onset and aggregate means and standard deviations with equal scenario weights. Phase weights and onset/temperature weights are explicit sensitivity assumptions, **not calibrated probabilities of semantic phase truth**. Multiple turns and setup movement can violate this single-transition language. Source profiles are attempt medians per player/drill. The full panel has 432 coordinates: 112 summary, 160 sequence and 160 shuffled-control coordinates. With 26 sprint coordinates, predictive families contain 138 summary coordinates or 298 summary-plus-sequence/control coordinates before fold-local compression.

Common summaries already contain timed speeds, geometry and one speed/acceleration signed area. Thus this is a strong temporal baseline. A joint frame permutation changes the added phase and multichannel-area features while preserving each window's channel multiset and leaving the common summaries untouched. This tests incremental sequence information, not whether all movement chronology matters. Permutations change local smoothness and there is only one fixed permutation per window; no exchangeability-certified significance test is claimed.

## Matched tests and adaptive corrections

Retain the prior conventional-selected outer-fold configurations and 2024-selected forward configuration. Each of four families gets the same 16 class-stratified athlete bootstrap samples per outer fold and forward fit. Original train/test player IDs are checked before negative replica IDs preserve bootstrap multiplicity. Fit imputers, scalers, physical residualization and PCA only on training replicas. Every family receives the same original five source-availability flags, physical/timed/NGS measures, NFL role, snap geometry and game situation controls.

The test uses four whole-player outer folds on the earlier classes and exploratory forward evaluation on 2025. Configurations were selected on conventional models, so this constrained experiment can favor that family; it is not an exhaustive source-model search. Added coordinates change compressed source modes, so a sequence-family difference cannot be attributed to a single isolated physiological parameter. Design receipts precede the respective trial scores, but repeated prior inspection of the cohorts prevents any fresh confirmatory claim.

After concatenation performed poorly in development, a second trial preserves the exact conventional predictions and fits a source-only correction to whole-player residuals. For every outer training set, three player-separated 16-model conventional ensembles supply training residuals. Average them by athlete, fit training-only physical residualization and rank-four PCA, and use components, their squares and body-mass interactions. A zero-intercept Ridge100 predicts a constant correction per held-out athlete; final probabilities are clipped to [0,1]. This adaptation is disclosed as occurring after the concatenation results, including 2025, were inspected.

The first correction's nonlinear coordinates were unscaled. Unequal variances make a common ridge penalty unequal across squared components and interactions. A third, explicitly adaptive trial clips each final correction coordinate to training 1st/99th percentiles and fits a training StandardScaler before the same Ridge100. It reuses the exact residuals and baseline. Both corrections are retained; no family is selected based on 2025. Zero residuals reproduce zero correction in software tests. Conditioning and support restriction are not an empirically calibrated measurement-error model.

## Complete prediction results

Player-rate MSE is the mean squared error between each athlete's recorded pressure frequency and their mean predicted probability over the same actual NFL workload. A percentage reduction changes this error, not pressures produced. The target remains conditional on NFL participation and context; it is not a standalone pre-draft production forecast.

| Method | Split | Conventional | Summaries | Sequence | Shuffled |
|---|---|---:|---:|---:|---:|
| Concatenate | Earlier 45 | 0.000997646 | 0.001685494 | 0.001637191 | 0.001937758 |
| Concatenate | 2025, 29 | 0.000575076 | 0.000564309 | 0.000576280 | 0.000596303 |
| Unscaled correction | Earlier 45 | 0.000997646 | 0.001813997 | 0.001558035 | 0.001604815 |
| Unscaled correction | 2025, 29 | 0.000575076 | 0.000911197 | 0.000959406 | 0.001118428 |
| Scaled/support-limited correction | Earlier 45 | 0.000997646 | 0.001045350 | 0.000992449 | 0.000997650 |
| Scaled/support-limited correction | 2025, 29 | 0.000575076 | 0.000516863 | 0.000572177 | 0.000581963 |

For the final correction, ordinary summaries reduce 2025 error by 10.12%; the absolute paired difference is 0.0000582127 with prediction-conditional player-bootstrap 95% interval [0.0000189020,0.000106907]. **The same summary correction worsens earlier-player error by 4.78%**, with interval crossing zero. This is a cohort-specific exploratory lead, not established transport. Sequence correction improves conventional error by only 0.52% earlier and 0.50% forward, both intervals crossing zero. It improves on summaries earlier by 5.06% but is 10.70% worse than summaries forward. The sequence-versus-shuffle differences remain uncertain in both splits. These results do not establish a new order-specific scouting advantage.

All intervals condition on fitted predictions and this selected cohort. They omit model refits, source-weight ambiguity, configuration-selection uncertainty, repeated adaptive testing and selection of the athlete-level metric in earlier work. The prior 80 training refits demonstrated that broader uncertainty can be much larger than prediction-conditional intervals; their intervals cannot simply be transferred to this new estimator. No multiplicity correction or fresh held-out class is manufactured by trying a new model.

## Measurement diagnostics and actionable next experiment

The median coordinate-level onset/temperature sensitivity SD, relative to between-player profile SD, is approximately 0.45–0.89 for sequence coordinates across these drills. That scale cautions against treating a phase estimate as an established athlete trait. Among 68 pass-rush repeat pairs, median rank correlation is 0.418 for summary coordinates and 0.368 for sequence coordinates. Seven hoop pairs are too few for reliable generalization; four-bag and lateral-reaction have no repeats per eligible athlete. Different attempts may reflect different drill conditions, so repeatability is descriptive rather than a physiological reliability estimate.

A useful next study should validate phase semantics and narrow the source representation: labeled complete cuts, matched entry speed and turn angle, repeated attempts, and reliable recovery channels. Empirical weights require phase labels or independently validated sensor-error models. Measure whether the channel predicts a prospectively reserved athlete's future game movement before asserting hidden-talent identification. Coaching benefits require intervention evidence; this analysis alone does not establish that changing recovery mechanics causes more pressures. Extra parameter sweeps against 2025 would not resolve those gaps.

## Reproducibility and output limits

`Movement_Phase_Populations.ipynb` embeds nine source modules, verifies hashes of all nine official CSVs, reconstructs the cohort and source features, and runs all three trials. Six executed code cells and four aggregate figures preserve successful and unsuccessful fits. Fresh execution defaults to a private temporary directory; optional `BDB_WORK_ROOT` permits controlled checkpoint resumption. The initial family experiment runs 320 predictive fits, cross-fitted baselines add 240 fits, and the two correction variants add 30 player regressions. This excludes source nuisance fits and repeated numerical replay.

Raw tracking, individual predictions, credentials and restricted inputs remain excluded from the source archive. The full archive retains the previous defensive-front study and all earlier experiments. No competition model is integrated into the betting app, published to Kaggle, or formally submitted by this work.
