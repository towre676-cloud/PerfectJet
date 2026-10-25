# Two-witness panels on a real Observatory system: the branching laboratory

## The instance

This is the panel problem of `optimal_panel_transfer.py` run on real
data from this repository instead of on a synthetic instance: the
branching laboratory, `examples/observatory/branching-lab.json`. The
system has 12 states and three unit-cost actions (route, inspect
alpha, inspect beta). Its initial belief is the four hidden states
`hidden:alpha:0`, `hidden:alpha:1`, `hidden:beta:0`, `hidden:beta:1`,
so there are 6 state pairs to distinguish, all sharing the free
initial observation "unread".

An experiment is a fixed, non-adaptive action word of length 1 to 3
(39 words), costing the sum of its action costs. Separation follows
this repository's own semantics in
`src/perfectjet/observatory/experiments.py`: a word separates a pair
if the two observation sequences differ at any step, where an
undefined transition produces a terminal observation distinct from
every live observation and identical for every terminal state. A
panel is two-witness (2-robust) if every pair is separated by at
least two **distinct** words in the panel — running the same word
twice is one witness, not two.

## Results

Every pair has enough witnesses (the two same-family pairs have 4
witnesses each; the four cross-family pairs have 13 each), so the
problem is feasible. The exact results are:

- **Optimal panel, cost 10:** route→inspect alpha,
  route→inspect beta, route→inspect alpha→route,
  route→inspect beta→route.
- **Greedy panel, cost 11:** route, route→inspect alpha,
  route→inspect beta, route→inspect alpha→route,
  route→inspect beta→route — the witnesses-per-cost rule of the
  synthetic prototype spends one extra unit here, because it buys
  the cheap word "route" first, which separates only cross-family
  pairs.
- Running all 39 words would cost 102.

Optimality is certified two ways. The solver
(`observatory_panel.py`) is an exact branch-and-bound over sets of
distinct words, and it proves every cost limit from 5 to 9
infeasible (5 to 17 search nodes per limit; the full certificate is
in `observatory_panel.json`). There is also a one-line human proof
of the lower bound for this instance: the alpha pair
(`hidden:alpha:0` versus `hidden:alpha:1`) can only be separated by
words that route and then inspect alpha, and the beta pair only by
words that route and then inspect beta — two **disjoint** witness
sets — and the two cheapest witnesses in each set cost $2 + 3 = 5$,
so every two-witness panel costs at least $5 + 5 = 10$.

## What this is and is not

This is a complete, exact panel analysis of one small real
Observatory system, using the repository's own fixture and
separation semantics, and it shows the greedy rule is already
suboptimal (by one unit) on real data, not only on the synthetic
instance in `optimal_panel_transfer.py`. It is not a solution for
the larger Observatory systems in this repository (the
interferometers have 169 and 2,197 states), where both the word
space and the pair space are far larger; a scalable exact panel
solver at that scale remains open. It also does not compete with
the repository's `adaptive_experiment`, which computes optimal
*adaptive* decision trees — a different and generally stronger
object than the fixed panels costed here. The fixed-panel question
is the one Singularity's robust-panel method asks, which is why it
is the right transfer target, but the two should not be conflated.
