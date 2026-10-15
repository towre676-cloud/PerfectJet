# Real public NFL tracking: useful progress and finite movement history

The October 14, 2026 run ingested every file in the publicly posted regional-event dataset at [ThompsonJamesBliss/nfl-big-data-bowl-regional-event-data](https://github.com/ThompsonJamesBliss/nfl-big-data-bowl-regional-event-data), pinned to commit `85da22eeff2f1d5be106faa9dfe06a1205f2defd`. The publisher's documentation attributes tracking to NFL Next Gen Stats and scouting annotations to PFF. The complete download contains 122 games from the first eight weeks of the 2021 season, 8,314,178 tracking observations, 8,557 plays, 188,254 player-play scouting records and 1,679 player metadata rows. The source files total 865,324,685 bytes and occupy 179,216,034 bytes in the compressed analysis cache. The manifest records source URLs, git blob IDs, byte counts and SHA-256 hashes. Raw inputs remain outside the repository and are not relicensed or included in the research ZIP. A separate original NFL-owned 2017 one-game sample, containing 316,025 tracking observations, was downloaded and hashed as an additional source, but was not pooled into the reported 2021 tests.

This is an independent physical-mechanism test using real NFL trajectories. It does not contain the 2023–2025 Combine sensor trajectories and does not, by itself, establish a scouting advantage. The source README identifies `gameId` and `playId` as the join to nflverse's `old_game_id` and `play_id`. The PFF Pass Rush annotation selects the historical analysis cohort; it is not represented as information available about an undrafted prospect. PFF hit, hurry and sack values are retained as outcome metadata and never enter the movement representation, tuning or timing predictors.

## Geometry and clocks

The adapter uses the play's `absoluteYardlineNumber` as the LOS in field coordinates. The defensive forward axis is negative x when the offense moves right and positive x when it moves left. A player's snap depth is `(LOS - snap_x) * defensive_axis`. A nonpositive value is rejected rather than repaired with an absolute value. Positions are then translated to the player's snap origin, with forward progress toward the LOS kept distinct from the path's arc length.

The real source exposed two adapter traps that unit tests now cover: its CSV says `Pass Rush` while its prose says `Pass rush`, and its timestamp strings retain only whole seconds even though distinct tracking frames continue between them. The adapter uses declared 0.1-second frame spacing only after checking that one common phase makes those frame times consistent with the supplied one-second clock quantization. This accepted 8,526 plays, rejected six clock-inconsistent plays and rejected 25 plays with absent or inconsistent snap-frame annotations. Missing/nonuniform player frame intervals are not interpolated into the velocity sequences. Velocities use backwards position differences only, so future frames cannot alter an earlier input velocity.

There were 36,235 available Pass Rush player-play records on the accepted plays. Of these, 1,455 had invalid defensive-side LOS depth. The remaining 34,780 records covered 697 players; 32,936 had a usable onset/crossing decomposition and 21,406 had a usable strictly post-snap onset. The onset is an operational sustained-forward-motion threshold, including tactical timing and frame-resolution effects, not a neurological reaction-time measurement. Onsets at or before the tagged snap are retained and flagged, then excluded from the primary post-snap-onset comparisons. The extraction also reports missing onsets, absent crossings and significant LOS recrossings. Timing analyses condition on an observed usable crossing; slow or noncrossing plays are not filled with an invented arrival time.

## Finite-horizon continuation on unseen players

Player/play hashes fixed a source-label-independent cap of four sequences per player and 320 eligible players. After geometry and frame checks, 1,117 sequences from 319 players remained. A fixed seed assigned 255 players to training and 64 to the outer test. There were 5,331 common test forecast origins. Every method predicted the same next three frames, a 0.3-second horizon, from the same physical forward/lateral velocity channels. Player-level mean squared error was averaged with equal total weight per player. History length, rank and ridge penalty were selected using three whole-player folds confined to the outer training players; scalers were fitted inside those folds.

| Method | Outer equal-player RMSE, yards/second |
|---|---:|
| Four-state learned history, five frames | 0.280226 |
| Matched uncompressed five-frame ridge | 0.280228 |
| Last-difference constant-acceleration extrapolation | 0.390579 |
| Five-frame linear time trend | 0.411815 |
| Five-frame quadratic time trend | 0.466836 |
| Learned instantaneous comparator | 0.499747 |
| Velocity persistence | 0.529634 |

The selected representation used five velocity frames, four numerical states and ridge penalty 0.0001. It reduced outer MSE by 68.56% relative to the instantaneous learned comparator, 48.52% relative to last-difference acceleration and 53.70% relative to the linear trend. The paired fixed-prediction bootstrap over the 64 test players gave an instantaneous-minus-history MSE interval of [0.15009, 0.19237] in squared velocity units. This interval resamples players and does not repeat representation fitting or estimate all training uncertainty.

The strongest control is the matched ordinary uncompressed ridge, which used the identical five-frame past, physical outputs, training-only scalers, inner folds and penalty candidates. Its RMSE is essentially identical. The four-state map therefore preserves this ordinary linear continuation forecast very closely on the retained test; it does not establish predictive superiority over an uncompressed linear autoregression. The benefit demonstrated here is finite memory and a compact response representation. It is neither an all-future equivalence theorem nor a physiological state identification. Trend and full-rank controls were added after the first inspection; the predictive-state candidate protocol and held-player assignment remained unchanged. This is development evidence on one NFL season, not an untouched competition test.

## Which movement target repeats?

Each player was divided chronologically into two game halves, requiring at least two games and ten usable plays in each half. Every readout used the same accepted player-play support. The common sample comprised 254 players.

| Readout | Game-half Spearman correlation |
|---|---:|
| Forward displacement in 0.5 seconds after onset | 0.801862 |
| Motion-onset-to-LOS travel time | 0.727243 |
| Path arc in the same 0.5 seconds | 0.722090 |
| Forward progress divided by path arc | 0.472728 |
| Operational onset delay | 0.396612 |

Useful forward displacement is more repeatable than path arc in this same-support comparison. This supports testing directional progress as a transfer readout. It does not establish that the difference between correlations is statistically significant, that it measures demand-standardized intrinsic ability, or that Combine data can predict it. Stable tactical deployment and depth can also induce player-level repeatability. The weak repeatability of onset cautions against calling a single arrival-time statistic a pure acceleration or reaction phenotype.

## Arrival laws and role-conditioned effects

The simple starting law is `arrival = onset + beta * sqrt(remaining distance)`. A strict zero-intercept travel fit corresponds to common effective constant acceleration with negligible initial forward speed. An affine version adds a travel intercept and therefore relaxes that strict physical model. The observed-onset diagnostic uses NFL onset to assess the law and is expressly not a deployable pre-snap or pre-draft predictor. Conventional context models use snap depth, width, down, yards to go, play action, aligned position and formation; no pressure result or future trajectory enters them. The ridge penalty was fixed at 10 rather than selected using the reported test sets.

| Test and model | Train/test plays | Equal-player RMSE, seconds |
|---|---:|---:|
| Unseen players: constant | 17,428 / 3,906 | 0.389192 |
| Unseen players: square-root snap depth | 17,428 / 3,906 | 0.222161 |
| Unseen players: conventional context | 17,428 / 3,906 | 0.198367 |
| Unseen players: observed onset plus affine square-root remaining depth, diagnostic | 17,428 / 3,906 | 0.134152 |
| Unseen players: observed onset plus strict square-root travel, diagnostic | 17,428 / 3,906 | 0.135965 |
| Weeks 7–8 known players: conventional context | 16,412 / 4,751 | 0.199188 |
| Weeks 7–8 known players: context plus player intercept | 16,412 / 4,751 | 0.205436 |
| Weeks 7–8 known players: context plus player intercept/depth slope | 16,412 / 4,751 | 0.204587 |

The outer unseen-player timing split trained on 503 players and tested on 126. The temporal split trained on Weeks 1–6 from 579 players and tested on 383 previously observed players in Weeks 7–8. Every training player received equal total regression weight. The random player-specific depth slope was ridge pooled using training-only player categories and depth scaling. It did not improve on the simpler context model in this test, so a role-response curve is not yet a demonstrated advantage. Conditional timing itself depends strongly on starting depth. The observed-onset diagnostic narrows error, but its onset is measured in the NFL target domain and cannot be inserted into a prospect's source feature vector.

## Reproduction and retained files

Run `python scripts/ingest_public_tracking.py --output /absolute/path/outside/git/regional_2021`, then `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/run_external_tracking.py --data /absolute/path/outside/git/regional_2021 --output /absolute/path/outside/git/regional_analysis`. The scouting optional dependencies are required. The runner writes a private derived-record/sequence checkpoint before fitting and refuses to silently reuse an existing checkpoint directory. The published aggregate is `results/external-tracking/summary.json`; the source manifest is `results/external-tracking/public-source-manifest.json`. The derived checkpoint hash in the aggregate binds the exact capped physical sequences and full geometry records used for the retained comparisons. Raw and derived caches remain outside git; the downloader and source hashes make them reproducible.

This real-data pass establishes a useful movement target and confirms that short physical history can support substantially better finite-horizon NFL forecasts than instantaneous or simple extrapolation baselines. The uncompressed control shows where the mathematical compression helps and where it supplies no predictive gain. The role-specific arrival test also returns a substantive negative result. Whether any of this creates a Combine-to-NFL scouting advantage is a separate paired temporal transfer experiment using the official Combine source data.
