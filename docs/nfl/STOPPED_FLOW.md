# Stopped-flow scouting: what survives a missing launch?

PerfectJet 0.14.0 continues the recovered official-data program rather than replacing it. It adds an exact launch-ambiguity witness, a speed-landmark extractor, position-signature and minimum-variance acceleration readouts, independent-attempt covariance reduction, strong repeat-prediction controls, and fully rebuilt temporal NFL experiments. The complete earlier atlas, archives, failed experiments and 0.13 receipts remain available. The new conclusion is specific: useful rolling motion can be recovered without seeing a launch, and repeated measurement can be improved, but this release does not establish incremental NFL scouting accuracy.

The most important numerical distinctions are these. The forty-yard source now supports all 177 available attempts and 57 eligible NFL players, compared with 18 attempts and ten eligible players under the earlier observed-launch protocol. Noise-aware three-coordinate acceleration estimates reduce independent-attempt prediction MSE by 22.87% against taking the first attempt literally; the full-refit development interval remains positive against that raw comparator. They do not beat a properly tuned ordinary multivariate ridge. Simple rolling kinematics show a 24.49% fixed-prediction gain on a physically matched NFL movement target, but its full-refit interval crosses zero. The primary get-off result is negative. These are different questions, not interchangeable performance claims.

## An exact obstruction, not a detector failure

Suppose recording begins at time zero and all subsequent positions are known perfectly. Even a known starting position, twice-continuously differentiable motion, forward-only velocity and nonnegative acceleration do not identify when movement began. The following pair proves this within a declared piecewise-polynomial model. Both athletes remain at the same position, −5/12, until their respective launches. Both follow the common recorded tail

\[
x(t)=t+\tfrac12t^2,\qquad t\ge0.
\]

One launches at −1. On its unobserved moving interval, put \(z=t+1\) and use

\[
x_L(t)=\tfrac23z^3-\tfrac14z^4-\tfrac5{12}.
\]

The other launches at −2. With \(z=(t+2)/2\), use

\[
x_E(t)=z^7-\tfrac14z^8-\tfrac13z^9-\tfrac5{12}.
\]

At each launch the position, velocity and acceleration are \((-5/12,0,0)\). At zero both position jets are \((0,1,1)\), matching the recorded tail. Their velocities are respectively \(z^2(2-z)\) and \(z^6(7-2z-3z^2)/2\). Their accelerations are \(z(4-3z)\) and \(z^5(21-7z-12z^2)/2\). Every displayed factor has the required nonnegative sign on \([0,1]\). Thus both histories are C², have the same starting point and every future observation, and have launch times a full second apart.

`launch_ambiguity.py` replays the boundary identities in rational arithmetic. The factor inequalities give the interval argument, rather than relying on sampled positivity. Stronger global assumptions, such as one acceleration law holding throughout the unseen interval, can exclude these histories; those assumptions would have to be justified separately. The witness does not prove that every practical launch estimator fails under every model. It shows why the original missing-launch bottleneck cannot be solved merely by applying a more elaborate transform to the same observed tail.

## Change the identifiable readout

The new gate is the first observed point at which two consecutive trailing 0.2-second displacement speeds exceed 2, 3 or 4 yards per second. These two speeds overlap and are not independent observations. A valid gate requires the declared 0.1-second sampling throughout its observed prefix. The extractor then uses precisely the next half second. The gate is chosen from its past; the readout becomes available at the half-second endpoint, not at the gate itself. Later frames cannot alter it. This is a separately declared rolling-motion experiment, not a relaxation of the older launch experiment after seeing its outcomes.

The source axis is the local observed velocity direction. Translation, rotation, reflection and clock-shift checks accompany the extractor. Its features include entry speed, forward displacement, terminal speed, path length and absolute lateral displacement. A full-history control retains every selected forward position and absolute lateral position. The exact jet features are deterministic transforms of these positions; they do not create additional measured information. Conventional measurements and every source-support flag are shared with the baseline.

The gate protocol was frozen before the first new outcome evaluation in `ROLLING_PROTOCOL.json`. Floating threshold ties have a documented 10⁻⁹ arithmetic tolerance; this is not a fitted tolerance. The later covariance refinement and repeat-control comparison are explicitly marked exploratory follow-ups after that initial run.

## The order-sensitive readout has a physical meaning

For a one-dimensional position history on a fixed window of duration \(T\), define the antisymmetric time-position area

\[
A_{tx}=\frac12\int_0^T\left[t\,dx-(x(t)-x(0))\,dt\right]
      =\frac{T}{2}(x(T)-x(0))-\int_0^T(x(t)-x(0))\,dt.
\]

This is the level-two antisymmetric path-signature coordinate of time and position, not a newly invented signature theory. The established signature background is Chevyrev and Kormilitzin, *A Primer on the Signature Method in Machine Learning*, arXiv:1603.03788, version 2. Here the application-specific step is to choose this coordinate because its nuisance cancellation has a direct physical interpretation. It removes a constant position and a constant-velocity trend. For a C² trajectory, integration gives

\[
\frac{12A_{tx}}{T^3}=\int_0^T\frac{6t(T-t)}{T^3}\,a(t)\,dt.
\]

The weight is nonnegative and integrates to one. The readout is a weighted mean acceleration, not a mysterious oscillatory score. It is sensitive to temporal order: interchanging two increments preserves their total displacement but reverses their contribution to the antisymmetric area. Chen composition supplies an exact streaming update. This makes a concrete connection from the earlier ordered-motion/commutator program to a measured physical question.

For sampled positions, the code computes the exact piecewise-linear area rather than pretending that an unknown continuous curve has been observed. On times \(t_i\), its quadratic normalization is

\[
\widehat a_A=\frac{12A^{\rm PL}_{tx}}{T^3-\sum_i(t_{i+1}-t_i)^3}.
\]

The denominator is the exact trapezoid correction for a quadratic. On the six uniform points 0, 0.1, …, 0.5 seconds, this becomes

\[
\widehat a_A=20x_0-10x_1-10x_2-10x_3-10x_4+20x_5.
\]

Its units are yards per second squared when the positions are yards. The weights sum to zero and their time-weighted sum is zero. This fixed-window nuisance cancellation must not be confused with Galilean invariance of the complete speed-gated pipeline: adding a physical velocity changes which gate is selected.

## Exact minimum-noise jets and their limits

The second readout reuses the exact observability solver. Let \(X_{ik}=(t_i-T/2)^k/k!\), let \(h\) select the desired derivative and let \(C\) be a positive-definite position-error covariance. An unbiased polynomial readout satisfies \(X^Tw=h\). The minimum-variance solution is

\[
w=C^{-1}X(X^TC^{-1}X)^{-1}h.
\]

The implementation also handles redundant polynomial constraints and returns a null-polynomial witness when the target derivative is not identifiable from the samples. Covariance positivity is checked in exact arithmetic. This is a readout-specific calculation, not a demand to reconstruct every derivative or the complete trajectory.

For the six-point cubic-exact midpoint acceleration, independent equal-variance position errors give a variance multiplier of \(7500/7\). The area readout gives 1200. A standard 0.1-second three-point second difference gives 60000. Consequently the respective noise amplification ratios are exactly 1/56 and 1/50. These are conditional noise identities, not measured improvements in football prediction. They use a wider window and a specified polynomial target. Under constant acceleration the targets agree; for general changing motion, window location, smoothing and bias matter. A bounded higher derivative gives the explicit Taylor remainder bound \(M\sum_i|w_i||t_i-T/2|^{p+1}/(p+1)!\).

Gate selection uses noisy positions, real errors may be correlated, and the motion need not be cubic. The fixed-window covariance calculation does not account for these issues automatically. The full data experiment therefore tests both ordinary kinematics and the complete sampled history rather than giving the more elaborate jet a weak comparator.

## What was recovered from the real source

The experiment reuses the same nine official CSV inputs, totaling 2,306,804,135 bytes. The owned preparation checkpoint and its extractor digests are checked before use. No Kaggle login or substitute dataset is required. There are 118 tracked prospects, 74 players meeting the primary NFL outcome threshold, and 51 temporal test players across the 2024 and 2025 classes. The larger frame and play counts do not increase that number of independent scouting cases.

At each of the three gates, all 177 forty-yard attempts are usable, spanning 93 source players. Of these, 57 have eligible primary NFL outcomes, and 84 source players have distinct repeat attempts. Counting three gates as 531 independent attempts would be wrong. Other front-drill families are retained separately and their pooled outcome experiment is secondary. The complete coverage ledger is `results/stopped-flow/source-coverage.json`.

At the speed-2 forty gate, descriptive disjoint-attempt Spearman correlations across 84 players are 0.5348 for area acceleration, 0.5485 for minimum-variance acceleration, 0.2829 for forward displacement, 0.4276 for terminal speed and −0.2256 for the cubic jerk estimate. This supports investigating stable acceleration readouts and cautions against adding higher derivatives just because the algebra permits them. These are stability statistics under observed drill conditions, not proof of innate ability, causality or NFL transfer. The actual source-attempt identifier determines the split; it is not claimed to be chronological ordering within the Combine.

The matched NFL target uses the same speed-2, half-second forward-displacement functional on observed post-snap movement. It retains 12,682 plays from 74 players with at least twenty qualifying plays. NFL entry speed, gate time, depth and heading are used to define a contextualized target, never as pre-draft prospect features. The conventional comparison is therefore not being handed less geometry for target normalization than the tracking model.

## The temporal scouting experiment

For evaluation on 2024, training uses 2023; for evaluation on 2025, training uses 2023–2024. Inner original-player folds rebuild context normalization, imputation, scaling and model selection. Original players remain together when bootstrapped copies are present. A conventional-only comparison chooses between linear and quadratic/position-interaction ridge models, with penalties 10, 100 and 1000. Tracking models receive the identical conventional and support information. The jet, simple-kinematic and full-history families each have the same inner penalty grid. All previously inspected classes remain development data.

Positive percentages below mean lower MSE for the candidate. Intervals in this first table resample fixed predictions by player within class and do not rebuild fitted models.

| Target and comparison | MSE gain | Fixed-prediction 90% interval |
|---|---:|---:|
| Get-off: selected tracking versus conventional | −13.43% | −29.20% to +1.15% |
| Get-off: jet family versus conventional | −4.85% | −19.42% to +7.88% |
| Get-off: simple kinematics versus conventional | −4.75% | −19.84% to +8.34% |
| Get-off: jet family versus full history | +3.43% | −12.16% to +16.52% |
| Matched movement: simple kinematics versus conventional | +24.49% | +10.98% to +34.78% |
| Matched movement: jet family versus conventional | +3.83% | −9.46% to +14.33% |
| Matched movement: jet family versus full history | −22.06% | −52.58% to −0.41% |

The primary jet model increases get-off MSE from 0.0025729 to 0.0026977 seconds squared. Its shortlist changes, but the small number of hits cannot overturn the unfavorable primary error result. Removing NGS measurements produces a −5.90% jet result and a −5.17% simple-kinematic result. The five-front-drill selected-tracking experiment gives +4.34%, with an interval crossing zero. No scouting edge is established by any of these variants.

The matched-movement result is an interesting lead, not the main claim. Simple kinematics improve this target by 1.63% in 2024 and 40.28% in 2025; the pooled gain is heavily concentrated in the latter class. Removing NGS gives a similar pooled point gain of 24.31%. However, 32 complete original-player refits expand the simple-kinematic interval to −23.97% through +34.80%. The primary jet get-off refits give −50.57% through +24.30%. All 32 requested draws succeeded in each study. These small empirical percentile studies measure procedure instability; they are neither prospective confidence guarantees nor correction for the entire history of adaptive research.

There is also a model-selection lesson. The inner-selected movement family is not necessarily the best family on the small outer class. Publishing the best outer family as though it had been selected prospectively would turn an exploratory lead into a misleading headline. The release keeps both the fixed family contrasts and the actual inner-selected procedure.

## A measured low-noise representation across repeated attempts

The follow-up uses one three-coordinate area-acceleration vector per distinct forty attempt. The coordinates are the three overlapping speed gates, so their covariance is estimated jointly. For a working model \(z_{ij}=\mu+u_i+\epsilon_{ij}\), pooled within-player differences estimate \(N=\operatorname{Cov}(\epsilon)\). Player-mean covariance, after subtracting the average \(N/n_i\) contribution, estimates the between-player signal \(S\). A fixed 5% trace-scaled ridge stabilizes the noise covariance.

The generalized eigenproblem \(Sq=\lambda Nq\) distinguishes repeatable directions from noise-dominated directions. Negative empirical signal eigenvalues are reported and clipped for this estimator; they are not asserted to prove that a biological direction is absent. The two earlier-class calibrations have spectra approximately \((-0.0235,0.3424,5.5431)\) and \((-0.0474,0.2131,3.2461)\). Both concentrate their positive noise-whitened signal strongly in one direction, with a weaker second direction. That is a reason to shrink uncertain coordinates, not to claim an exact two-dimensional physiological state.

The posterior mean is returned in the original physical coordinates:

\[
\widehat z_i=\mu+S(S+N/n_i)^{-1}(\bar z_i-\mu).
\]

This matters because eigenvectors can rotate or change sign across training folds. Feeding differently oriented latent coordinates into one shared decoder would silently change the meaning of a feature. The implementation rebuilds the covariance model inside each fold but maps every output back to the same three physical acceleration coordinates. Its covariance is conditional on the working model and estimated parameters; it is not a calibrated uncertainty interval for NFL ability.

## Strong independent-attempt controls

Using earlier classes to calibrate and the first distinct attempt to predict the second gives 55 evaluated source players: 26 from 2024 and 29 from 2025. The noise-aware estimator has MSE 0.17290, compared with 0.22417 for the raw first attempt. This is the 22.87% improvement. Sixty-four complete original-player source refits all succeed, with a development interval of +13.13% to +29.70% against raw observations.

That comparison alone is insufficient to credit sophisticated mathematics. The follow-up adds a pooled prior, a training-selected scalar shrinkage, diagonal reliability shrinkage and multivariate ridge with five training-selected penalties. Both orientations of a training repeat pair stay together in the same original-player fold; augmentation is not counted as extra independent people. Every control uses only source data from earlier classes.

| Noise-aware estimator compared with | MSE gain | Full-refit 90% development interval |
|---|---:|---:|
| Raw first attempt | +22.87% | +13.13% to +29.70% |
| Pooled prior | +34.20% | +20.46% to +50.94% |
| Scalar shrinkage | +8.39% | −8.15% to +15.19% |
| Diagonal reliability shrinkage | +4.15% | −4.74% to +14.00% |
| Multivariate ridge | −1.70% | −4.62% to +5.10% |

The properly tuned ordinary ridge is slightly better on this retained test. The defensible finding is that denoising helps repeated measurement, not that the covariance method beats strong conventional prediction. Its additional value is an interpretable noise decomposition, physical-coordinate transport and an explicit conditional uncertainty model. Transporting the reliable acceleration coordinates to NFL get-off gives −0.24% versus the conventional baseline; the raw three-coordinate acceleration variant gives −4.17%. The refinement mitigates overfitting, but still does not create an incremental scouting advantage. Without NGS the reliable get-off result is −4.08%.

## What the bridges now accomplish

The earlier mathematical programs enter as executable mechanisms rather than decorative vocabulary. Observability supplies the exact hidden-launch witness and asks for a recoverable target instead. Ordered-path algebra isolates weighted acceleration from constant position and velocity. Exact rational readout design supplies the derivative weights, minimum-noise solution and nullspace obstruction. Statistical state reduction learns which correlated attempt coordinates warrant shrinkage, while preserving physical coordinates across splits. The empirical comparison identifies where the chain still fails: usable source measurement and repeatability do not yet translate into a dependable get-off advantage.

This is not evidence that acceleration never matters in football. It is evidence against deploying these fitted scouting corrections on this sample. A plausible next physical hypothesis is that launch timing, assignment and the transfer from motion to a football task matter more than another high-order derivative. That interpretation remains a hypothesis; the current experiments do not identify its causal contribution. The next confirmatory study needs genuinely uninspected players, a declared motor endpoint and get-off endpoint kept separate, and a strong ordinary history/reliability control. A missing-launch clip should be valued for the rolling readouts it actually observes, not for a launch time the data cannot uniquely supply.

## Reproduction and retained evidence

Install `.[scouting]` from the repository. First reproduce the owned checkpoint with the existing nine-file preparation script, or reuse the already-owned hash-matching checkpoint. Do not deserialize a checkpoint from an untrusted source; a hash establishes equality, not the safety of arbitrary pickle bytes. The four new runners require both the checkpoint and its preparation receipt, and require restricted individual outputs outside the public repository.

```bash
python scripts/run_stopped_flow.py --checkpoint PRIVATE/official_bridge_data.pkl --preparation results/real-nfl/preparation.json --out results/stopped-flow --private PRIVATE/stopped-flow --refits 32
python scripts/run_motor_sensitivity.py --checkpoint PRIVATE/official_bridge_data.pkl --preparation results/real-nfl/preparation.json --out results/stopped-flow --private PRIVATE/stopped-flow --refits 32
python scripts/run_reliable_stopped_flow.py --checkpoint PRIVATE/official_bridge_data.pkl --preparation results/real-nfl/preparation.json --out results/stopped-flow --private PRIVATE/stopped-flow
python scripts/run_repeat_controls.py --checkpoint PRIVATE/official_bridge_data.pkl --preparation results/real-nfl/preparation.json --out results/stopped-flow --private PRIVATE/stopped-flow --refits 64
python -m unittest discover -s tests -v
```

The retained study contains 8,568 candidate outcome-regression fits: 600 across five initial/sensitivity experiments, 288 across three reliability experiments, and 7,680 across 64 complete NFL procedure refits. This count excludes additional context-normalization fits and does not treat repeated runs as new evidence. The strong source-repeat comparison adds 2,080 ridge fits across its initial run and 64 complete refits. The complete source archive includes exact kernels, all previous mathematical content, tests, this chapter, protocols, aggregate receipts and a source-complete notebook. Restricted input and individual derived predictions remain in the separate private checkpoint package. There is no new Lean formalization claim and no claimed live-site or upstream-application deployment.
