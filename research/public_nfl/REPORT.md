# Public Combine-to-rookie NFL observations: first real temporal benchmark

This is a real-data external benchmark of mathematical feature engineering. The primary population is Combine-listed defensive line prospects (DE, DT, DL, EDGE, NT). The front-seven and all-position populations are declared exploratory sensitivity screens. The mechanical transformations use exactly the same pre-draft measurements as conventional comparators. They do not introduce tracking or sensor information and do not validate the Combine-to-get-off bridge.

## Source corpus and identity audit

The ingested snapshot contains 88 source files, 80,173,908 bytes and 1,084,747 CSV rows. These include 8,968 Combine observations from 2000–2026, 12,927 draft records from 1980–2026, 24,854 player identities, regular-season NFL outcomes from 1999–2026, weekly outcomes and snaps from 2013–2026, PFR defense pressure summaries, eleven completed NGS assets, and the NFL's explicitly published 2017 single-game tracking sample of 316,025 rows. The incomplete 2026 season is retained as an ingestion record and excluded from all outcomes and evaluation. Every retained source URL, source timestamp where provided, byte count, schema, row count and SHA256 appears in SOURCE_MANIFEST.json. Later NGS asset requests encountered transport denial and the bulk network process was cancelled before approval returned; eight attempted failures are retained in the manifest. No participant reposts of gated Kaggle competition data were ingested.

The strict cohort retains 7,138 unique linked-or-linkable PFR identities through 2025. It excludes 1,531 Combine rows lacking PFR identity and every occurrence of 17 repeated or ambiguous PFR identities; 341 remaining PFR identities lack a GSIS crosswalk. The source actually attaches the same PFR ID to different humans/positions in several cases, so selecting one row would be unsafe. The pressure summary likewise contains identical name/team/stat lines attached to multiple PFR IDs; 22 ambiguous player-seasons are excluded. Team splits are never added to an already supplied 2TM total.

The join uses unique PFR and GSIS IDs and never fuzzy names. Outcome eligibility uses Combine position. Updated NFL position, roster status, career AV and career totals are absent from predictors. Draft pick is excluded from the main benchmark; a separately named sensitivity mode can add it, explicitly as post-Combine information. Unknown outcomes remain missing. An explicit NFL count of zero remains zero. Consequently these results are conditional on prospects with an explicitly observed rookie-season outcome, and do not estimate the probability that a Combine participant never reaches the NFL.

## Mathematical comparison and temporal protocol

The baseline observes Combine height, weight, forty, bench, vertical, broad jump, three-cone, shuttle, measured-trait count and Combine position. Fixed mechanical features add the following deterministic functions of these same measurements:

\[
 a_{40}^{\rm proxy}=\frac{80}{t_{40}^{2}},\quad
 \bar v_{40}=\frac{40}{t_{40}},\quad
 \frac{t_{\rm shuttle}}{t_{40}},\quad
 \frac{t_{\rm cone}}{t_{40}},\quad
 v_{\rm jump}^{\rm proxy}=\sqrt{2gH},\quad
 \frac{L_{\rm broad}}{H_{\rm body}},\quad
 \frac{W}{H_{\rm body}},\quad
 \frac{t_{\rm shuttle}}{t_{\rm cone}}.
\]

The acceleration and jump formulas are proxies, not measured effective acceleration or literal takeoff speed. Start rules, technique, friction, flight and nonconstant acceleration violate their idealized derivations. The conventional comparison includes raw ridge and a full degree-two conventional model across numeric features, missingness indicators and Combine-position indicators. In particular, it includes numeric-by-position interactions; omitting these overstated the exploratory front-seven pressure result in an initial run. Only the stronger rerun is reported here. For each held draft class, the baseline family and each model's ridge penalty are chosen using the latest three eligible earlier classes. Outer outcomes never select the model. Missing-value imputation, indicators, scaling and position encoding are fitted again on each training fold. Counts are predicted on their original scale and clipped at zero. Each athlete contributes one paired squared error. The shortlist uses the upper quartile of the training outcome as its fixed threshold and selects the top quarter of held-class predictions.

The final three-scope program executes 125 held scope/target/class folds and 5,310 ridge model fits, including all earlier-class tuning fits. It produces 12,342 held target/player predictions; these reuse players across endpoints and scopes and must not be read as a unique-athlete count. Ten held classes (2016–2025) support the main snaps, sacks and QB-hit evaluations. Pressure outcomes have a shorter available history. The rate outcome is pressures per 100 total defensive snaps, not pressures per pass-rush snap. It therefore remains an exposure/role proxy. The 2025 class has been inspected in this research and is development evidence, not a pristine future validation set.

## Primary defensive-line findings

A positive MSE gain means lower error than the baseline selected inside the training classes. The interval is a 1,000-draw paired class-plus-player resample of already fitted predictions. It does not include full-pipeline refitting uncertainty, does not correct for fifteen exploratory endpoint/scope comparisons, and is not evidence of a scouting edge.

| Rookie endpoint | Held players | Held classes | Mechanical MSE gain | Fixed-prediction 95% interval | Positive classes |
|---|---:|---:|---:|---:|---:|
| rookie_defense_snaps | 421 | 10 | -2.48% | [-11.00%, +3.39%] | 7/10 |
| rookie_sacks | 438 | 10 | -1.39% | [-5.80%, +2.23%] | 3/10 |
| rookie_qb_hits | 438 | 10 | -0.93% | [-6.10%, +3.64%] | 4/10 |
| rookie_pressures | 185 | 5 | +0.56% | [-9.05%, +11.49%] | 3/5 |
| rookie_pressures_per_100_defense_snaps | 185 | 5 | -0.83% | [-6.11%, +6.72%] | 2/5 |

The primary defensive-line results are null or negative. Stable algebraic transformations of standard Combine measurements do not establish an incremental NFL scouting advantage on this experiment. The source audit, matched temporal controls and honest negative results are useful constraints on the next physical-transfer experiment.

## Exploratory scope screens

| Scope | Rookie endpoint | Held players | Held classes | Mechanical MSE gain | Fixed-prediction 95% interval |
|---|---|---:|---:|---:|---:|
| FRONT7 | rookie_defense_snaps | 653 | 10 | -0.80% | [-3.07%, +1.27%] |
| FRONT7 | rookie_sacks | 687 | 10 | -2.04% | [-6.60%, +1.51%] |
| FRONT7 | rookie_qb_hits | 687 | 10 | -2.33% | [-7.57%, +3.10%] |
| FRONT7 | rookie_pressures | 326 | 6 | +2.09% | [-6.45%, +9.64%] |
| FRONT7 | rookie_pressures_per_100_defense_snaps | 324 | 6 | -3.91% | [-10.74%, +3.19%] |
| ALL | rookie_defense_snaps | 2213 | 10 | +0.49% | [-1.09%, +2.04%] |
| ALL | rookie_sacks | 2271 | 10 | -0.16% | [-2.89%, +2.18%] |
| ALL | rookie_qb_hits | 2271 | 10 | -0.67% | [-5.79%, +2.98%] |
| ALL | rookie_pressures | 680 | 7 | -9.70% | [-24.78%, -1.89%] |
| ALL | rookie_pressures_per_100_defense_snaps | 563 | 6 | -0.50% | [-7.12%, +7.76%] |

The front-seven pressure-count screen improves pooled MSE by 2.09% across 326 held prospects and 6 classes, with five of six class gains positive. Against raw ridge alone its gain is 2.91%, showing comparator sensitivity. The stronger position-interaction baseline makes its fixed-prediction interval cross zero (−6.45% to +9.64%); its latest 2025 class loses 12.92%, and pressure-per-defensive-snap performance declines by 3.91%. The public-cohort screen therefore does not establish an incremental scouting edge. The appropriate next experiment uses genuinely additional paired Combine tracking and independent NFL movement, rather than more transformations of these same timing summaries.


## Reproduction and what remains

The complete fold selections, metrics and player predictions are retained in public_cohort_dl.json, public_cohort_front7.json and public_cohort_all.json. SOURCE_MANIFEST.json permits exact source replay with `python scripts/ingest_public_nfl.py --output PATH`. Run the benchmark with `python scripts/run_public_cohort.py --data-root PATH --output RESULT.json --scope DL`. Install the pinned scouting extra first. A frozen source hash mismatch means the public URL has changed; the script refuses to silently substitute a newer snapshot.

The decisive remaining test requires actual Combine tracking joined to independent future NFL movement and outcomes. This public benchmark has measured Combine trait timing summaries and NFL outcomes, but lacks the paired pre-draft trajectories. It cannot determine whether finite-horizon predictive states, directional onset readouts or decision-focused additional sensing recover information absent from conventional traits. The real 2017 tracking sample supports physical geometry and continuation checks, but its one game does not provide broad draft-class validation or private Combine trajectories.

Attribution: nflverse public releases, with the nflverse-data CC-BY-4.0 source license; Combine and draft data are attributed by nflverse to Pro Football Reference. The 2017 sample is explicitly published by NFL Football Operations at nfl-football-ops/Big-Data-Bowl, whose ownership and source notices remain distinct. We do not assign the nflverse license to NFL tracking data. Primary documentation: https://nflreadr.nflverse.com/reference/load_combine.html , https://nflreadr.nflverse.com/reference/load_players.html , https://nflreadr.nflverse.com/reference/load_player_stats.html , https://nflreadr.nflverse.com/reference/load_snap_counts.html , https://github.com/nflverse/nflverse-data/blob/main/LICENSE.md , https://github.com/nfl-football-ops/Big-Data-Bowl .
