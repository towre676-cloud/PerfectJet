# Kaggle writeup scaffold

Constraints as stated for this project (verify on the competition page): a public notebook attached to the submission, a writeup of at most 2,000 words, fewer than ten tables or figures, deadline January 6, 2027, 23:59 UTC. Judging weights reported as football relevance 30%, data science 30%, writeup 20%, visualization 20%.

Numbers below are placeholders filled from `results/nfl/results.json`. Never fill them from the synthetic run.

## 1. The football question (about 250 words)
What a defensive-front evaluator wants to know before the draft, and why get-off is the outcome: its stability, and what the variable measures (confirmed definition).

## 2. The measurement (about 350 words) — Figure 1, Figure 2
- Figure 1: one detected turn with its recovery window (`fig_event_trace.svg`), plus the reviewer agreement rate from `review_sheet.csv`.
- Definition of eta in words; what it is not.
- Figure 2: observed demand support (`fig_demand_support.svg`) and the reference demand distribution.
- Repeatability: split-half {{repeatability}}; extraction-branch spread {{sensitivity}}.

## 3. What each player's attempts can and cannot tell us (about 300 words) — Table 1
- Identifiability share {{identified_share}}; the two-fit witness explained in one sentence.
- Why one or two supported readouts replace four unstable coefficients.

## 4. Does it add anything to what scouts already know? (about 450 words) — Figure 3, Table 2
- Baseline contents; same availability indicators and tuning for both models.
- Table 2: G by test class, pooled G {{G}}, fixed-prediction and full-refit intervals.
- Figure 3: held-out target against prediction (`fig_predictive_comparison.svg`).
- Diagnostics: by position, without low-play athletes, single-athlete influence.
- Which evaluations are development evidence and which are untouched.

## 5. Decisions that change (about 300 words) — Figure 4
- Frozen shortlist rule; hits baseline {{hits_b}} against movement {{hits_m}}; promoted and demoted players and their outcomes.
- Two scouting cards.

## 6. What to measure next (about 200 words)
- Value of information: repeat versus new condition; one proposed protocol to review with practitioners.

## 7. Limits (about 150 words)
- Observed NFL participants only; sample of about {{n}} athletes; what would be needed to claim an advantage.
