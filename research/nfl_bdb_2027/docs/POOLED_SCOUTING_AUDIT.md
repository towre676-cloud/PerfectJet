# Sparse movement profiles and the scouting-advantage test

Nine official CSVs were downloaded again through the enrolled account and checked against retained acquisition hashes. Reconstruction matches the previous 74 defensive-front rookies,14,665 eligible NFL records and 582 angular-progress turns. Shared source curves and regularized player deviations do not yet establish a scouting advantage. Every adaptive trial remains retained.

## Source-only partial pooling

The earlier finding that 93.17% of player/drill panels cannot identify four bilinear coefficients remains valid. Pooling is an assumption, not a cure for missing observations. Shared nuisance curves use physical/timed attributes, entry speed, angle, squared terms, interactions and drill identity. Training-player residuals use three whole-player source crossfits; evaluated players use the full training reference. No NFL labels enter source fitting. Geometry scaling and repeat noise use training players only.

With standardized demand rows $\phi=(1,s,a,sa)$ and shared-reference residual $r$, coefficients are

$$\widehat b=(\Phi^TW\Phi+\lambda I)^{-1}\Phi^TWr.$$

Penalties are 1,10,100. Turns within an attempt share at most unit total weight; sensitivity widths reduce weights relative to a training-estimated repeat variance with floor 0.0025. These descriptive coefficients are not identified biological thresholds or calibrated posteriors.

The primary target is equal-player mean recorded pressure indicator. Missing timestamps are absent indicators, not independently established no-pressure events. Predictors contain no NFL game/snap covariates. Conventional, capacity, duration, pooled and combined models share 15 body/timed/NGS traits, Combine position, availability and per-drill attempt counts. Four outer/three inner whole-player folds select transforms and penalties, allowing conventional fallback. Three partitions reuse 45 earlier athletes;2023→2024 tuning precedes 29 already-inspected 2025 players. All results are exploratory.

Pooled pressure changes earlier error by+0.65%,−18.61%,−0.40%, with−18.60% forward; positive means error reduction. Duration-plus-pooling selects conventional fallback forward. This does not establish incremental scouting value.

## Baseline-preserving corrections

A high-shrinkage follow-up changed conventional coefficients too; it remains a diagnostic. The corrected experiment fixes conventional penalty 100 and added-motion penalty 1000. Include a free intercept in$B$, conventional penalty matrix$P_B$, and $A=B^TB+P_B$. Then

$$\beta_0=A^{-1}B^Ty,\quad T=A^{-1}B^TZ,$$

$$\gamma=(Z^TZ-Z^TBT+1000 I)^{-1}Z^T(y-B\beta_0),$$

$$\widehat y_*=B_*\beta_0+(Z_*-B_*T)\gamma.$$

Schur elimination equals the full block-penalized solve. Zero motion returns the original prediction exactly; independent numerical tests check both facts. No runtime superiority claim follows from this small calculation.

Completely enumerate nonnegative correction triples from 0,0.1,0.25,0.5,1 with sum at most one. Training-only selectors use mean gain minus 1 SE, worst-class gain minus 1 SE, or worst-class mean gain. These are heuristics, not transport or confidence guarantees. The isolated pooled correction gives+0.26%,−0.67%,−0.52% earlier and−0.03% forward. The class/1 SEguard returns zero forward and in two earlier partitions; the third loses 1.92%.

## Expanded duration audit supersedes the initial stability assessment

Restore the original five-availability baseline separately from the new attempt-count baseline. Twelve seeds declared before scores produce+3.67%,+1.32%,+6.31%,+2.07%,−0.23%,−3.23%,−2.58%,0%,0%,−2.80%,−5.85%,−0.27%. The original three scores and 4.49% forward gain reproduce exactly. Four partitions improve, two select fallback and six lose; mean relative gain is−0.13%. This mean of ratios is not pooled error. The same 45 athletes recur, so this is not twelve independent studies. Earlier chapters retain historical summaries; this broader audit supersedes the current stability assessment.

## More repeatable response, still no validated edge

Across 200 random halves of recorded games, median pressure-rate rank correlation is 0.280(range 0.165–0.417); charted get-off is 0.775(range 0.715–0.830). These are split-sensitivity ranges, not confidence intervals or predictive ceilings. Role, context, annotation and field semantics remain relevant; supplied get-off is not assumed pure reaction time.

The identical pooled bank tests mean get-off as supporting. Time predictions are not clipped to[0,1]; existing pressure predictions retain clipping by default. Pooled get-off gains 2.72% forward, but earlier changes are−7.50%,−46.60% and fallback. This cannot replace the primary pressure result.

Sixty-four class-stratified 80% training subsets per outcome refit source and scouting transforms with selected configurations fixed. These without-replacement sensitivity runs are not ordinary bootstrap confidence intervals or full selection refits. None of 64 pressure refits improves forward error. Eleven of 64 get-off refits improve; its median change is−7.32%, with 2.5–97.5% range−26.05% to+4.39%. Evaluated-player resampling adds a sensitivity diagnostic without correcting adaptive search.

## Research decision and reproduction

Measurement stability has not converted into dependable scouting value. The useful next direction is a validated, position-specific game movement response: establish turn-completion semantics, collect repeats at independent demands, match relevant game situations and reserve independent outcomes before final model selection. More searches against inspected 2025 cannot create fresh confirmation. Development interventions need causal evidence. This result concerns this construction and cohort, not an impossibility theorem for all Combine signals.

`Pooled_Recovery_Scouting_Audit.ipynb` embeds 27 modules, verifies nine source hashes, reconstructs features and retains every adaptive stage. Four aggregate figures show demands, model stability, outcome repeatability and exploratory forward comparisons. The complete archive retains prior studies and Git history; raw restricted data, credentials, individual profiles and predictions are excluded. No betting integration or public Kaggle submission occurred.


Fresh-run verification: all four code cells completed from reconstructed official inputs;27embedded modules match source;997numeric scores/diagnostics across16aggregate receipts reproduce with maximum difference0.0. All128training-subset refits completed and85checks passed. The notebook has659words including stream output and four aggregate figures.
