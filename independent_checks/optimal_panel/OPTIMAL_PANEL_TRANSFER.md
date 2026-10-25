# Optimal-panel transfer prototype (synthetic instance)

## What was built

A small, exact optimal-panel solver in `optimal_panel_transfer.py`,
transferring Singularity's two-witness robust panel rule to a
finite-system distinguishing problem of the kind PerfectJet's
Observatory handles.

Problem: given behaviour pairs to distinguish, experiments that each
separate a subset of those pairs, and a cost per experiment, find a
minimum-total-cost panel in which every pair is separated by at least
two experiments, so one missing result cannot hide a distinction. The
greedy panel is built by repeatedly picking the experiment with the
highest new-witnesses-per-cost ratio.

## Result on the found instance

The script searched random small instances (seed 20261024) and found
one at trial 11 where greedy is strictly worse than optimal. The
instance has 8 pairs and 10 experiments, with verified costs:

- Greedy panel: E7, E3, E5, E1, E10, total cost 13.
- Optimal panel: E1, E5, E7, E10, total cost 10.
- All experiments (fixed protocol): total cost 35.

Both panels were verified in the script to satisfy the two-witness
rule for every pair, and the optimal panel was found by exhaustive
subset search, so its optimality is proved for this instance, within
the supplied experiments. The full coverage table is in
`optimal_panel_transfer.json`.

## What this is NOT

- Not a result about PerfectJet's actual Observatory systems, and not
  a claim that greedy is worse by 13 versus 10 on those systems. The
  numbers above belong to the synthetic instance found by the search.
- Not a scalable solver: exhaustive search is exponential in the
  number of experiments.

## The real-system step, in this same directory

`observatory_panel.py` runs the same two-witness panel problem on a
real system from this repository — the branching laboratory fixture
`examples/observatory/branching-lab.json` — with an exact
branch-and-bound solver over sets of distinct words, which also
proves every cheaper cost limit infeasible. See
`OBSERVATORY_PANEL.md` for its results and its limits. That still does not settle the panel problem for the
larger Observatory systems (169 or 2,197 states); a run at that scale
remains open.
