# Combine recovery readout: analysis protocol

This protocol fixes the analysis before the next untouched evaluation is opened. Code: `src/perfectjet/applications/nfl_scouting/`. One command rebuilds everything:

```bash
PYTHONPATH=src python -m perfectjet.applications.nfl_scouting --data DIR --mapping mapping.json --out results/nfl
PYTHONPATH=src python -m perfectjet.applications.nfl_scouting --synthetic --seed 1 --out results/nfl-synthetic
```

## Question

Primary: does a repeatable, demand-adjusted recovery readout measured at the Combine predict NFL get-off for defensive-front players beyond position, body measurements, timed tests and drill availability known before the draft?

Secondary, downstream: pressure. Its reported split-half stability (about 0.28, against about 0.77 for get-off) makes it a weak primary target.

**Before any claim, confirm what the supplied get-off variable measures** (snap-to-first-movement time, distance threshold, frame rate, which snaps). Do not call it reaction time until that is confirmed. The current definition is recorded in `outcome_definition` and printed in every result.

## Status of earlier evidence

| Reported result | Status | Use here |
|---|---|---|
| Angular-progress alignment cut measurement sensitivity about 34.1% | historical report | measurement improvement, not scouting advantage |
| About 93.2% of player/drill panels cannot identify all four response coefficients | historical report | motivates supported readouts |
| Get-off split-half about 0.77, pressure about 0.28 | historical report | get-off is primary |
| Duration-model 2025 gain did not persist | historical report | 2025 is development evidence |
| Pooled turn-response get-off gain inconsistent | historical report | pooling is a controlled candidate only |
| Future-speed MSE reductions 33.36% / 26.59% | historical report | short-horizon prediction only |

Reproduce these once on the original data and keep the receipts next to the new results. The 2025 class has been inspected and is **development evidence**; it cannot become a holdout again.

## Fixed definitions

- **Event.** Speed minimum below 0.6 of the preceding one-second maximum, followed within 0.8 s by a direction change of at least 30 degrees. This is a detected direction change, not a verified plant. `review_sheet.csv` is an outcome-blinded sample stratified by drill, speed tercile and angle band, with the most branch-sensitive event of each stratum added as a difficult example. Reviewers fill the three `reviewer_*` columns. Systematic detector errors are fixed before any predictive comparison.
- **Measurement.** eta = sum_k w_k v_k / (0.5 s_entry): normalized travel in the outgoing direction over the half second after the plant, trapezoidal weights. Not force, energy efficiency or physiological capacity. Primary branch: 3-frame smoothing, chord alignment. All six smoothing/alignment branches are kept; their spread is a sensitivity range, not a probability interval.
- **Demand frame.** phi(s,a) = (1, s', a', s'a') on training-standardized entry speed and turn angle. The reference demand distribution q is the training-fold histogram on a 0.5 yd/s by 15 degree grid. h_q = sum q_k phi(d_k).
- **Identifiability gate.** For each athlete, the exact test h_q in row(X_i) on the design rounded to that grid. A witness n with X_i n = 0 and h_q.n != 0 means two coefficient vectors fit the athlete's attempts and disagree on the readout. The share of athletes identified and the share of q-mass they observed are reported with every run.
- **Primary readout.** Random-intercept readout: theta_i = h_q.beta + sum_j (eta_ij - phi_ij.beta)/(n_i + sigma^2/T_0), with beta, sigma^2, T fitted by EM on training athletes only.
- **Secondary readout (exploratory).** Full pooled readout h_q.(beta + u_i) with u_i ~ N(0, T). Reported with its pooling reliance, the share of prior variance it retains.
- **Outcome.** r_i = mean over eligible plays of (y - m(context)); m is a ridge context model on alignment and play type. Training athletes get residuals cross-fitted over 5 player folds; test athletes get residuals from m fitted on training athletes only. Shrinkage n_i/(n_i + k) with k = sigma_play^2/tau^2 from training athletes. The leakage check (perturbing held-out outcomes leaves training targets and m unchanged) runs every time.
- **Models.** Ridge regression. Baseline: position, admissible measurements (training-mean imputation plus missing indicators), drill-completion flags, attempt count. Movement: baseline plus the readout. Same availability indicators, missing-data rule and penalty grid {0.1, 1, 10, 100} chosen by 5-fold athlete-grouped CV inside each training set.
- **Folds.** Train on draft classes before Y, test on class Y, for every Y after the first. Folds share training classes; they are robustness checks, not independent replications.
- **Primary metric.** G = 1 - MSE_movement / MSE_baseline pooled over folds. Reported with a fixed-prediction 90% interval (athletes resampled, predictions fixed) and a full-refit 90% interval (athletes resampled, entire pipeline refit including event extraction).
- **Diagnostics.** G by position and by class, G without athletes below 20 eligible plays, mean error (calibration in the large), and the five largest single-athlete influences on G.
- **Decision rule (frozen).** Within each class, shortlist the top 25% by predicted target. A hit is a target in the training best quartile. Report hits for both systems, and the promoted and demoted athletes with their outcomes.

## What would count as an advantage

Proposed, to be confirmed by the project owner before the untouched class is opened: on the untouched class, G at least 0.03 **and** the fixed-prediction 90% lower bound above zero **and** no single athlete moving G by more than half its value. Anything less is reported as "no established advantage", together with the measurement and identifiability findings, which stand on their own.

## Scouting cards

Each card shows baseline and movement-adjusted predictions, events and distinct demands, whether the athlete's own attempts identify the readout, the share of reference demand mass observed, measurement sensitivity, pooling reliance, and the condition whose next attempt most reduces the readout's posterior variance, marked as a repeat or a new design direction. A card's usefulness is not evidence of prediction lift.

## Next measurements

Value of information for a new condition e is Var(theta | D) - Var(theta | D, e) under the fitted Gaussian model, conditional on its assumptions. A repeat improves precision; only a new design direction can resolve non-identification (`perfectjet.readout.repair`). Any proposed condition must be translated into a safe, repeatable drill with practitioners before it is used.
