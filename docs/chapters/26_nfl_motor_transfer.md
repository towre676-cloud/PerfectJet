# Combine motor transfer and the scouting test

PerfectJet 0.11.0 preserves the complete previous NFL research package and implements a new experiment aimed at the actual scouting outcome. **No new real-data predictive gain is reported.** The recovered package excludes the nine raw competition CSVs; the official API requires authentication and the browser remains signed out. Analytic examples and fixture tests establish code behavior, not football advantage.

The official Kaggle dictionary defines `player_get_off` as seconds from the snap until the defensive rusher moves forward across the line of scrimmage. It is not pure reaction time. The source is https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/data, inspected October 14, 2026. The latest recovered canonical research commit is `2d2fc62af6502618821de23ddaf15e68cdb16a3e`; its original monograph, nine notebooks, aggregate receipts, vendor licenses and history bundle are preserved in `research/nfl_bdb_2027`.

## Evidence carried forward

The canonical audit reports 74 defensive-front rookies, 14,665 eligible NFL records and 582 angular-progress turns. A 34.1% sensitivity reduction is measurement stability. About 93.2% of individual player/drill panels cannot identify the four-coefficient bilinear response. Twelve overlapping duration-model partitions give four gains, two fallbacks, six losses and mean relative gain −0.13%. Pooled get-off's exploratory 2025 gain 2.72% is unstable; 11 of 64 fixed-configuration training-subset refits improve. These are recovered receipts, not new raw-data reproductions. Failed and adaptive stages remain intact.

The new adapter defines its prospective cohort by Combine position, which may differ from the historical NFL-position cohort. It must report counts rather than automatically claim reproduction of 74 players. All 15 conventional measurements enter the stronger baseline. NGS grades use an explicit pre-draft interpretation; exact chronology remains unverified. Physical availability dates are proxied by observed Combine tracking dates. A no-NGS comparison is a sensitivity, not a substitute headline.

## Target-relative mathematics

Let total LOS time be $t=\tau+u$, onset plus travel. Its observation row is $X=(1,1)$, with hidden witness $n=(-1,1)$. Then $Xn=0$ but$(1,0)n=-1$: total time cannot identify either component. This is PerfectJet's exact linear readout theorem, not a physiological claim. Under the separate local model$d=vu+au^2/2$, the stable root is

$$u(d,v,a)=\frac{2d}{v+\sqrt{v^2+2ad}},\qquad d,v\ge0,\quad a>0.$$

At distance 1 yard, initial speed 0 and total time 1 second, onset$1/5$ with acceleration$25/8$ and onset$3/10$ with acceleration$200/49$ give the same total. The receipt replays both rational identities. This nonlinear nonuniqueness counterexample stays separate from the linear nullspace theorem. Travel increases with distance and decreases with speed/acceleration. `crossing.travel_time_bounds` uses these corner extrema over a declared box, checking outward endpoint polynomial signs exactly. It bounds the specified model, not sensor error or physiology.

The new source readout is

$$A_T=\frac{2}{T^2}\int_0^T[v(t_0+t)-v(t_0)]dt
=\frac{2}{T^2}[x_\parallel(t_0+T)-x_\parallel(t_0)-Tv_\parallel(t_0)],\quad T=0.5\mathrm{s}.$$

It equals acceleration for quadratic motion and otherwise weights acceleration by$2(T-t)/T^2$. It requires no second numerical differentiation. A causal trailing three-frame derivative avoids forward-difference acceleration bias. Extraction requires recorded launch history and sustained onset; it rejects a curved first start rather than searching for a favorable later window. Rotation,translation,irregular-time analytic motion and missing-history rejection are tested. The operational onset has no known Combine start cue.

Primary extraction uses forty-yard starts. A separately declared secondary family uses the same functional on the four front-drill starts, with training-only drill and conventional nuisance adjustment. Smoothing variants remain sensitivity scenarios; they never count as independent attempts.

For source-reference residuals$x_{ij}=z_i+\epsilon_{ij}$, the scalar Gaussian model assumes$z_i\sim N(0,\tau^2)$ and drill variance$\sigma_d^2$ learned from actual training-player repeats. Its posterior is

$$V_i=(\tau^{-2}+\sum_j\sigma_{d_j}^{-2})^{-1},\qquad m_i=V_i\sum_jx_{ij}\sigma_{d_j}^{-2}.$$

No repeat evidence produces an unavailable readout, not perfect reliability. Sparse drills may use explicitly labeled pooled repeat variance. Common player deviation across drills, independent attempt errors and transferable variance are assumptions. Branch width is never substituted for Gaussian noise.

The NFL correction integrates source uncertainty:

$$r_i\mid D_i\sim N(\lambda m_i,\sigma_{NFL}^2+\nu_i^2+\lambda^2V_i).$$

Here$r_i$ is an out-of-player baseline residual. The descriptive$\nu_i^2$ uses game-cluster sums for the same play-weighted residual mean: with$G_i>1$ games and$n_i$plays, it is$G_i/(G_i-1)\sum_g[\sum_{p\in g}(r_{ip}-\bar r_i)/n_i]^2$. It omits context-reference uncertainty. Full pipeline refits address additional fitting variability. The scalar loading sees training outcomes only. Missing source information gives zero athlete-specific correction. This is materially different from estimating four unsupported coefficients.

## Validation and decisions

Both models receive all 15 conventional measurements,training-imputed missingness,Combine position,and identical raw drill flags/counts. NFL geometry defines labels only. Context adjustment includes depth,width,speed,formation,alignment and situation,with square-root/log depth terms motivated by travel. Training labels are cross-fitted by player; evaluated labels use the training reference. Every inner split rebuilds targets,source nuisance,repeat variance,imputation,scaling and models. Loading-residual folds also rebuild their context targets. Training NFL seasons precede the evaluated class; labels are rookie REG observations.

The fixed ridge grid is 10, 100, 1000 with three inner player folds and identical selection budgets. The primary metric is equal-athlete$G=1-MSE_{movement}/MSE_{baseline}$,with paired losses,source coverage,class results and player influence. Bootstrap draws preserve class sizes and group every copy by the original player. The default requests 64 complete source/context/selection refits. Their percentile intervals remain exploratory; they do not undo prior adaptive data use. Inspected 2025 cannot become a fresh holdout.

The separate NFL crossing extractor reconstructs thresholded onset,onset-to-LOS travel and half-second movement,flagging missing intervals,recrossing and anticipation. These are mechanism diagnostics. They must not replace a failed get-off result with a new headline. A fixed-budget shortlist comparison is needed before declaring improved scouting decisions. No betting advantage or causal development effect follows.

## Execute on official inputs

Use Python 3.12 and a private raw-input directory outside the checkout:

```bash
python -m pip install -e '.[scouting]'
perfectjet nfl-burst --data /path/to/official-nine-files --out /path/to/private-nfl-run --verify-known-hashes --refits 64
perfectjet nfl-burst --data /path/to/official-nine-files --out /path/to/private-nfl-no-ngs --verify-known-hashes --without-ngs --refits 64
```

Private results retain individual predictions and tuning choices. Aggregate output removes predictions and influence identities. Missing files cause a named-file error; the command has no synthetic fallback. `notebooks/PerfectJet_Motor_Transfer.ipynb` embeds the source and expects attached official data; it remains unexecuted until raw inputs exist. Fixture success is never a new NFL result.

## Corrections from the release audit

Independent rational approximations of standardized float coordinates broke bilinear dependencies: same-speed designs could have rank 3 instead of 2,and empirical demand averages sometimes failed identification from their own complete rows. The fixed gate forms raw rational$[1,s,a,sa]$ and exact cell-count averages. Bootstrap copies now share original-player folds; late events cannot alter predictors or availability; real drill indicators replace synthetic names; inner fitting is fully rebuilt; future NFL seasons cannot train historical folds; higher-is-better shortlists use the correct quartile. The inherited synthetic-first detector remains distinct from the older angular-progress detector,so 34.1% is not silently credited to this new code.

The empirical conclusion remains unresolved: does the supported motor readout improve get-off and player decisions? The release makes that test executable and preserves honest failures. Exact algebra and synthetic recovery cannot answer it without running the actual NFL inputs.
