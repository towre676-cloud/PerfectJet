# From predictive movement to scouting decisions

PerfectJet 0.12.0 connects the representation program to a concrete pre-draft question: can measured Combine movement improve the prediction of rookie NFL snap-to-line-of-scrimmage get-off, beyond the full conventional information available for the same prospects? The implementation connects operational movement targets, finite-horizon predictive states, player-cross-fitted transfer, and exact target-directed measurement packages. It preserves the original atlas, every preceding release, and the recovered NFL work. This is an implemented research bridge; a new empirical scouting advantage remains unestablished until the official inputs are executed and independently validated.

The prior study matters because it prevents a false restart. Its launch/turn extraction became more stable, while several downstream models failed to deliver stable scouting lift. A representation can improve its own numerical behavior without improving a football decision. The present bridge therefore has separate movement, transfer, prediction, and decision receipts. A positive result in one cannot substitute for another.

## The mathematical chain and what each link preserves

Let $B_i$ be the fifteen conventional measurements, Combine position, and observed drill availability for prospect $i$. Let $X_i$ be a causal history of that prospect's Combine movement. Let $q_i$ contain declared NFL movement readouts, and let $y_i$ be context-adjusted rookie snap-to-LOS get-off. The proposed connection is

$$X_i \longmapsto \widehat q_i=f_{\mathcal T}(B_i,X_i)
\longmapsto \widehat y_i=g_{\mathcal T}(B_i,\widehat q_i).$$

The training set $\mathcal T$ includes only eligible past players. NFL context and tracked NFL movement define the training targets; prospect prediction uses Combine information. All physical readouts keep declared units. No raw SVD coordinate is treated as an invariant athlete trait.

| Research family | Executable connection | Preserved quantity | Limit of the connection |
|---|---|---|---|
| Observability and hidden witnesses | LOS decomposition and exact linear readout tests | Whether a specified question is determined by available measurements | An exact rank test is conditional on the declared linear response model |
| Finite jets and calculus | Causal position derivatives and the post-onset burst functional | A finite time and directional movement readout | Operational onset is a tracking proxy; no physiological reaction time is inferred |
| Hankel and predictive state | Supervised delay-block continuation with player-held rank/history selection | Physical movement outputs over a fixed finite horizon | Numerical reduced-rank prediction does not prove an exact all-future realization |
| Transport and reconstruction | Fixed-unit Combine-to-NFL target maps | An explicit movement target and its reconstruction into get-off prediction | A shared coordinate system does not prove cross-domain transport |
| Closure and obstruction | Continuation residuals, unsupported histories, unavailable movement targets | A failure witness and its scope | A suggested residual repair must be fitted and validated again |
| Compositional error | The actual fitted two-stage decoder's error decomposition | Where prediction error enters the chain | A deterministic scenario bound is separate from empirical uncertainty |
| Gaussian information | Exact scalar and correlated-block posterior updates | Conditional uncertainty in a frozen scouting readout | Prior, noise and fitted loading uncertainty are assumptions, not established physiology |
| Finite populations | Exact counting, ranking and joint package optimization | Original feasible measurement packages and ties | Exhaustive global optimality is for the declared finite candidate universe |
| Certified decisions | Bound-separated winner and overlapping contenders | A decision under supplied valid bounds | NFL sampling uncertainty is retained separately |
| Arithmetic geometry, lattice and invariant theory | Retained core and atlas; no forced athlete analogy | Exact arithmetic claims in their original domains | No evidence currently justifies inserting Pell or sextic features into scouting |

This is a stronger reuse of the existing mathematics than an indiscriminate feature expansion. Arithmetic geometry remains a central part of the broader research program. In this application, the useful bridges are those whose inputs, outputs and assumptions match the scouting question.

## Get-off is a sum with a hidden direction

The official get-off variable measures the elapsed time from snap to crossing the line of scrimmage. For an observed post-snap operational onset $t_o$, crossing $t_c$ and snap $t_s$,

$$y_{\rm tracked}=t_c-t_s=(t_o-t_s)+(t_c-t_o)=\tau+T_{\rm travel}.$$

This identity explains the original underidentification. An observation row $X=(1,1)$ cannot determine the onset component $h=(1,0)$: the hidden direction $n=(-1,1)$ satisfies $Xn=0$ while $hn\ne0$. Two athletes can have identical get-off and different onset/travel decompositions. Additional rows resolve that ambiguity only if they measure the target-affecting hidden direction. More repetitions of $(1,1)$ increase precision but leave this structural gap.

`movement_targets.py` reconstructs the geometry with official game/play/player identities. It finds the snap in a first tracking pass, then retains bounded selected-player windows in a second pass. A canonical forward axis points from the defensive start side toward LOS. The implementation rejects nonpositive starting depth; it does not silently take an absolute value and invent a different task. Translation, reflection and rotation tests check the geometry. Gaps, missing snap observations and invalid crossing paths retain failure records and counts.

The supplied official get-off remains the primary outcome even when tracked decomposition fails. The tracked-minus-supplied discrepancy is a diagnostic. The two initial movement readouts are forward displacement over the first operational post-onset half-second, in yards, and motion-onset-to-LOS travel time, in seconds. Onset delay remains a diagnostic rather than a claim about reaction time. Anticipation and pre-snap motion must retain their own flags; an onset already outside the observed window cannot be manufactured from the first available frame.

Player targets use a common set of usable plays for their channel vector. Context adjustment is fitted on training players and cross-fitted for training targets. Neither starting depth nor NFL contextual covariates become prospect predictors. For $G$ observed games and play weights $w_p$ defining the reported player mean, game-cluster uncertainty is

$$S_g=\sum_{p\in g}w_p(z_p-\bar z),\qquad
\widehat{\operatorname{Cov}}(\bar z)=\frac{G}{G-1}\sum_{g=1}^{G}S_gS_g^\top.$$

One game does not estimate this cluster covariance: it produces unknown uncertainty, rather than a falsely precise zero. A thousand frames from one play do not constitute a thousand independent players or a thousand independent measurement attempts.

## A physical source functional before a latent model

The original post-onset Combine source is

$$A_T=\frac{2}{T^2}\left[x_\parallel(t_o+T)-x_\parallel(t_o)-T v_\parallel(t_o)\right],\qquad T=0.5\,\mathrm{s}.$$

For twice differentiable motion this is

$$A_T=\frac{2}{T^2}\int_0^T(T-u)a_\parallel(t_o+u)\,du.$$

It equals constant acceleration for quadratic motion. In general it is a weighted acceleration readout, with no force, power, efficiency or developmental interpretation. Initial velocity is estimated with a trailing causal derivative, and adequate pre-onset history is required. Straightness is tested over the declared source window. Smoothing alternatives represent extraction scenarios; they are never independent repetitions of the athlete.

The new state bridge uses forward and lateral movement channels derived from observed history. Its source feature vector contains half-second forward displacement, terminal forward speed, endpoint directional retention, and physical-coordinate continuation forecasts; the preceding burst functional remains executable in the separate motor-transfer experiment. A forecast origin has a declared time. Frames beyond that origin cannot enter input derivatives, history blocks or source features. The physical forecast itself can extend over the fitted short horizon, but its input stays within the available prefix.

## Predictive state without arbitrary cross-fold coordinates

For channel vector $u_t$, form a history block $p_t=[u_{t-L+1},\ldots,u_t]$ and a future block $f_t=[u_{t+1},\ldots,u_{t+H}]$. Training-only scaling gives matrices $P,F$. The numerical continuation estimator is

$$\widehat K_\lambda=(P^\top W P+\lambda I)^{-1}P^\top W F.$$

The fitted future matrix $P\widehat K_\lambda$ is compressed through its right singular vectors. If $V_r$ contains the retained output directions, the state and physical forecast use

$$z_t=p_t\widehat K_\lambda V_r,\qquad
\widehat f_t=z_tV_r^\top,$$

with the fitted centering and inverse scaling restored in code. History length, rank and ridge penalty are selected by whole-player inner validation on common forecast origins. The instantaneous comparison receives those same origins, data weights and declared horizon. Each sampled athlete has equal total weight; bootstrap multiplicity is preserved, while copies remain in their original athlete's fold.

This implements a target-directed delay model inspired by the Hankel program. It does not assert that a noisy finite sample has discovered an exact weighted automaton, a nonlinear sufficient statistic, or an all-time physiological state. The forecast outputs are physical coordinates. A latent basis may rotate across separate SVD fits without changing those coordinates, so the transfer stage consumes physical forecasts rather than concatenating incompatible latent states.

NFL movement histories train the continuation map within each training fold. Applying that map to a Combine history is a declared cross-domain hypothesis. Train-history Mahalanobis and orthogonal-design distances flag unsupported inputs. These distances are descriptive; their training 95th percentile does not become a calibrated prediction interval. An unsupported athlete remains visible in coverage and sensitivity reports. The bridge cannot call an unusual history familiar by refitting on the held-out NFL player.

The analytic receipt uses an explicitly synthetic second-order recurrence to demonstrate why history can matter. Two histories with the same current sample can have different continuations. A history model can distinguish them, while an instantaneous model cannot. This establishes the implemented mechanism on the fixture; it establishes no NFL performance improvement.

## Train the decoder on the predictions it will actually receive

A frequent two-stage error is to train a football decoder on true NFL movement and then deploy it on noisy Combine-derived movement estimates. That changes its input distribution. The implemented bridge instead trains its decoder with player-out-of-fold movement predictions:

$$\widehat q_i^{\rm OOF}=f_{\mathcal T\setminus\mathcal F(i)}(B_i,X_i),\qquad
\widehat g=\arg\min_g\sum_{i\in\mathcal T}
\left[y_i-g(B_i,\widehat q_i^{\rm OOF})\right]^2+\alpha\|g\|^2.$$

Each stacking fold rebuilds the movement representation, context targets, source reference, preprocessing and transfer map using its training players. The final first-stage map is refitted on the outer training set and then feeds the frozen decoder for outer held-out prospects. Tuning occurs inside the outer training population. Athlete labels and NFL trajectories from the outer evaluation class enter scoring and post-prediction diagnostics only.

The comparator receives all fifteen conventional measurements, position and identical drill availability. Any derived source coverage/support flags are shared with it, so a comparison cannot attribute missingness or attendance information to movement values. Missing trajectories remain missing. Eligibility dates, rookie seasons and training outcome cutoffs are enforced. Held-player perturbation tests change NFL labels and trajectories and check that fitted prospect predictions remain fixed.

Temporal comparisons on previously inspected classes are development evidence. In particular, a newly packaged model cannot restore untouched status to 2025 merely by renaming an analysis. The primary headline remains supplied snap-to-LOS get-off. A useful onset or displacement result can be reported as a mechanism diagnostic without replacing a failed primary result.

## Locate transfer error and ask for the measurement that matters

After predictions are frozen, held-out NFL movement can locate the two-stage error:

$$\widehat y-y=
\underbrace{g(B,\widehat q)-g(B,q)}_{\text{movement transfer error}}+
\underbrace{g(B,q)-y}_{\text{decoder residual}}.$$

This is an algebraic decomposition for the actual fitted decoder. It does not establish causation or identifiability of a biological mechanism. For an affine decoder with loading $w$ and a supplied box $|\widehat q_j-q_j|\le r_j$,

$$|g(B,\widehat q)-g(B,q)|\le\sum_j|w_j|r_j.$$

Those radii must be supplied or validated. A fixed-fit box bound cannot be substituted for uncertain extrapolation, model selection variability, unknown loading uncertainty or NFL sampling error.

For a fixed affine source-to-movement map $q=F x+c$ and decoder $g=w^\top q+b$, the scouting loading on physical source coordinates is $h=F^\top w$. The implementation exposes the fitted finite-difference Jacobian in physical units. Pipeline imputation and missingness make this a local conditional loading: it is not a universal derivative across missing-value boundaries or new support regions.

The allocation bridge takes that frozen loading and a caller-declared prior covariance, measurement noise, candidate constraints and budget. It records training IDs, held-out IDs, cutoff and the loading's declared source. These receipts expose provenance; they do not independently prove that an external caller trained honestly. A floating fitted coefficient can be rationalized within a declared tolerance so the package algebra is reproducible. Exact arithmetic proves calculations for that rational snapshot, rather than proving that an estimated loading is exactly correct. The allocation wrapper also bounds the effect of coefficient rationalization over every feasible package, so a reproducible approximation comes with an optimization-error receipt.

With prior covariance $\Sigma$, loading $h$, measurement row $e$ and independent noise variance $s^2$, the update is

$$\Sigma' = \Sigma-
\frac{\Sigma e e^\top\Sigma}{s^2+e^\top\Sigma e},\qquad
\operatorname{VOI}(e)=h^\top(\Sigma-\Sigma')h.$$

Several correlated channels from one attempt use the block update

$$\Sigma' = \Sigma-\Sigma E^\top(R+E\Sigma E^\top)^{-1}E\Sigma.$$

The channel block is one candidate with one cost and its full noise covariance. Duplicate original attempt IDs are rejected. Repeating an independent attempt may improve precision; splitting its frames into fictitious independent observations may not. Irreducible NFL outcome noise and uncertainty in the fitted loading are outside this conditional source-covariance reduction and must remain visible.

If $D_S=\Sigma-\Sigma_S$ is the covariance reduction for a package, then $0\preceq D_S\preceq\Sigma$ and $|(D_S)_{ij}|\le(\Sigma_{ii}+\Sigma_{jj})/2$. A raw decimal loading $h$ and rational snapshot $\widetilde h$ therefore satisfy

$$|h^\top D_Sh-\widetilde h^\top D_S\widetilde h|\le
\sum_{i,j}|h_i h_j-\widetilde h_i\widetilde h_j|
\frac{\Sigma_{ii}+\Sigma_{jj}}{2}=\epsilon.$$

The bound is uniform over the declared candidate packages. The package optimized for the rational snapshot has raw-snapshot regret at most $2\epsilon$, including for the minimum over a declared loading family. This controls arithmetic approximation in the optimizer; it does not control errors in the fitted hypothesis, prior or noise model.

## A concrete new exact result: isolated-value greedy allocation can fail

The allocation receipt gives a small exact counterexample. Take $\Sigma=I_2$, $h=(1,0)$, budget two and unit candidate costs. Let A measure $(1,0)$ with noise variance one, B measure $(1,1)$ with noise variance $1/10$, and C measure $(0,1)$ with noise variance $1/10$.

| Candidate or package | Conditional variance reduction in the target |
|---|---:|
| A alone | $1/2$ |
| B alone | $10/21$ |
| C alone | $0$ |
| Greedy package A+B | $21/32$ |
| Globally best package B+C | $110/131$ |

The zero-isolated-value measurement C estimates the nuisance coordinate contaminating B. Together B and C recover the target far more precisely than the isolated-value ordering suggests. The difference is $769/4192$. Target-specific variance reduction is monotone but need not be submodular: the marginal value of C is zero at the empty package and $110/131-10/21=1000/2751$ after B. This violates diminishing returns, so additive-profit models and the usual submodular greedy guarantees do not apply. This is an exact linear-Gaussian counterexample, not a newly observed NFL benefit. It directly justifies optimizing packages jointly instead of sorting candidates by standalone value.

The existing finite-population core counts and ranks the original feasible subsets; the allocation layer evaluates each joint posterior. For at most eighteen candidate packages the implementation provides a global optimum, tie count and feasible population receipt. Larger candidate universes require a separately declared search procedure; the bounded exhaustive routine does not silently claim scalable global optimality.

Multiple plausible frozen loadings can be supplied. A robust objective maximizes the minimum variance reduction over that declared hypothesis family. If the family contains a zero source loading, its worst-case reduction is zero: a source-only measurement cannot guarantee value when an admissible fitted hypothesis gives the source no scouting effect. Weighted-mean optimization is a separate declared alternative, with explicit weights rather than an implicit uniform biological prior.

## Decide which comparisons are still worth resolving

For a higher-is-better score with valid fixed-fit bounds $[L_a,U_a]$, candidate $a$ is certified ahead when $L_a>\max_{b\ne a}U_b$. The get-off target is lower-is-better, so the direction must be transformed consistently before using that comparison. A fixed budget or roster constraint remains explicit.

When the winner is unsettled, measurement can target score differences $H_a-H_b$ for overlapping contenders. Resolving an irrelevant athlete's complete parameter vector can consume budget without changing the decision. The contender allocator targets those score differences. When source uncertainties are correlated, a measurement on another athlete can still resolve a contender comparison; the exact joint search retains such candidates, including measurements with zero isolated benefit. Empirical uncertainty can be attached to the decision report, but is not silently reclassified as a proved scenario bound.

The full scouting assessment still needs equal-player paired prediction loss, calibration, coverage, class-by-class behavior and the fixed-budget shortlist. A representation should earn its place by improving these outcomes against the comparably informed baseline. Selection must be frozen before evaluating the class. Repeated refits test instability; they do not erase adaptive use of an already inspected class.

## Execution and evidence

Install the scouting extras. Run `perfectjet math-bridges --output results/math-bridges.json` for the analytic and exact receipts without raw football data. Run `perfectjet nfl-bridges --data OFFICIAL_DIR --output private_results/bridges.json --verify-known-hashes --refits 64` for the official-data experiment and full original-player pipeline refits. The primary comparison uses the stronger of direct conventional and conventional two-stage decoding, selected within training-player validation. Both individual comparisons remain available. The bridge notebook embeds and hashes the actual repository modules and refuses a synthetic fallback when official inputs are absent.

The official experiment needs `players.csv`, `combine_results.csv`, `combine_tracking.csv`, `player_play.csv`, `games.csv`, `player_career_successes.csv` and game-tracking files for 2023, 2024 and 2025. Their absence blocks empirical execution, rather than implementation, analytic verification or package publication. The released notebook is explicitly unexecuted on those raw inputs.

The strongest completed result is a connected, falsifiable computation: physical targets, causal finite-history predictions, out-of-player transfer, a decoder trained on those actual predictions, an exposed physical loading, and exact measurement packages directed at that loading. The next empirical question is whether this chain improves football predictions and decisions. A negative result should identify whether the loss occurred in source coverage, finite-history forecasting, Combine-to-NFL transport or decoding, and remain in the permanent research record.
