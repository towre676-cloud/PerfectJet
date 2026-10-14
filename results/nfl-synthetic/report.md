# Combine recovery readout: validation report

**SYNTHETIC DATA: tests the pipeline only; not evidence about football.**

Question: Does a demand-adjusted Combine recovery readout predict NFL get-off beyond pre-draft information?

## Measurement

588 turn events from 588 attempts. Median extraction-branch spread 0.013 (a sensitivity range, not a calibrated interval). Split-half reliability of the demand-adjusted readout: 0.897 (Spearman-Brown).

## Identifiability

Own attempts identify the demand-supported readout for 84.2% of athletes (exact test on the design rounded to the demand resolution). Median distinct demands 5.0; median share of the reference demand mass observed 0.21.

## Prediction

Pooled G = 1 - MSE_movement/MSE_baseline = **0.275**.

| Test class | G | MSE baseline | MSE movement |
|---|---|---|---|
| 2022 | 0.254 | 0.00028 | 0.00021 |
| 2023 | 0.223 | 0.00026 | 0.00021 |
| 2024 | 0.336 | 0.00033 | 0.00022 |

90% interval with predictions fixed: [0.168, 0.376].
90% interval refitting the full pipeline (20 athlete resamples): [0.110, 0.397].
Temporal folds share training classes, so they are robustness checks, not independent replications.

## Diagnostics

G by position: DE 0.312 (n=30), DT 0.274 (n=30), OLB 0.250 (n=30).
G excluding athletes with fewer than 20 plays: 0.328.
Largest single-athlete influence on G: A0034 0.032, A0115 0.026, A0031 0.022.

## Decisions

Rule: top 25% by predicted target within each class; hit means training best-quartile.
Shortlist hits: baseline 19, movement 19.

## Leakage

{"training_targets_unchanged": true, "context_model_unchanged": true}

## Historical reports (not reproduced here)

- angular-progress alignment reduced measurement sensitivity by about 34.1% — measurement improvement only; not a scouting advantage.
- about 93.2% of player/drill panels cannot identify all four response coefficients — motivates supported readouts instead of full response surfaces.
- get-off split-half stability about 0.77 versus pressure about 0.28 — get-off is the primary outcome; confirm what the supplied variable measures.
- duration-model 2025 gain did not persist across earlier partitions — 2025 is development evidence, not a pristine holdout.
- pooled turn-response get-off gain was inconsistent across partitions — pooling is a controlled candidate here, not the expected breakthrough.
- future-speed MSE reductions 33.36% / 26.59% — short-horizon prediction; does not establish scouting success.

## Example scouting cards

### A0003 (DE, class 2024)
- Baseline prediction 0.025; movement-adjusted 0.026 (change 0.001).
- Evidence: 6 turn events at 6 distinct demands covering 16% of the reference demand mass; own attempts identify the readout.
- Measurement sensitivity across extraction branches 0.007; pooling reliance 0.10 (share of prior variance retained).
- Most informative next condition: speed 5.0 yd/s, angle 90 deg (variance reduction 4.16e-05, within current design span).

### A0007 (DT, class 2024)
- Baseline prediction 0.048; movement-adjusted 0.043 (change -0.005).
- Evidence: 4 turn events at 4 distinct demands covering 12% of the reference demand mass; own attempts identify the readout.
- Measurement sensitivity across extraction branches 0.015; pooling reliance 0.15 (share of prior variance retained).
- Most informative next condition: speed 6.0 yd/s, angle 45 deg (variance reduction 1.10e-04, within current design span).

### A0011 (OLB, class 2024)
- Baseline prediction -0.005; movement-adjusted -0.004 (change 0.001).
- Evidence: 2 turn events at 2 distinct demands covering 11% of the reference demand mass; readout relies on pooled assumptions.
- Measurement sensitivity across extraction branches 0.009; pooling reliance 0.29 (share of prior variance retained).
- Most informative next condition: speed 6.0 yd/s, angle 170 deg (variance reduction 3.35e-04, new direction).

### A0015 (DE, class 2024)
- Baseline prediction 0.023; movement-adjusted 0.018 (change -0.005).
- Evidence: 4 turn events at 3 distinct demands covering 18% of the reference demand mass; readout relies on pooled assumptions.
- Measurement sensitivity across extraction branches 0.009; pooling reliance 0.16 (share of prior variance retained).
- Most informative next condition: speed 4.0 yd/s, angle 45 deg (variance reduction 1.15e-04, new direction).

### A0019 (DT, class 2024)
- Baseline prediction 0.024; movement-adjusted 0.023 (change -0.001).
- Evidence: 4 turn events at 4 distinct demands covering 9% of the reference demand mass; own attempts identify the readout.
- Measurement sensitivity across extraction branches 0.017; pooling reliance 0.15 (share of prior variance retained).
- Most informative next condition: speed 5.0 yd/s, angle 45 deg (variance reduction 9.47e-05, within current design span).

### A0023 (OLB, class 2024)
- Baseline prediction 0.007; movement-adjusted 0.003 (change -0.003).
- Evidence: 6 turn events at 6 distinct demands covering 28% of the reference demand mass; own attempts identify the readout.
- Measurement sensitivity across extraction branches 0.010; pooling reliance 0.10 (share of prior variance retained).
- Most informative next condition: speed 7.0 yd/s, angle 135 deg (variance reduction 5.79e-05, within current design span).

