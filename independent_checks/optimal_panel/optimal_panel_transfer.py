"""Optimal-panel transfer prototype: Singularity's robust panel
method applied to a finite-system distinguishing problem of the
kind PerfectJet's Observatory handles.

Problem, stated exactly:
- There are behaviour pairs to distinguish (here, pairs of
  behaviour classes in a finite system).
- Each experiment separates a subset of those pairs, at a cost.
- A panel is robust if every pair is separated by at least
  TWO experiments in the panel, so one missing result cannot
  hide a distinction. This is Singularity's two-witness rule.
- The optimal panel is a minimum-total-cost robust panel.
- The greedy panel is built by repeatedly picking the experiment
  with the highest new-witnesses-per-cost ratio, breaking ties
  by lower cost, then by earlier index.

What this file does:
- Searches random small instances (fixed seed) for one where
  greedy is strictly more expensive than optimal, to show
  that greedy is not optimal in general and that exact
  optimisation matters even at small scale.
- Verifies the optimal panel by exhaustive subset search, and
  verifies that both panels satisfy the two-witness rule.
- Reports the found instance, both panels, and their costs.

What this is NOT:
- Not a result about PerfectJet's actual Observatory systems,
  and not a claim that greedy is worse by a specific ratio
  on those systems. It is a transferable prototype: the same
  exact solver can be run on a real Observatory pair-coverage
  table, once that table is supplied, and its output will be
  a minimum-cost robust panel for that table, or a proof that
  no robust panel exists in the supplied experiments.
- Not a scalable solver for large instances: exhaustive search
  is exponential in the number of experiments, so for large
  tables it must be replaced by an exact set-cover solver
  (branch and bound / ILP) with the same two-witness constraints.
  That scaling step is explicitly left open.
"""

import itertools
import json
import pathlib
import random


def witnesses(panel, coverage):
    """coverage: experiment -> set of pairs it separates.
    Return pair -> number of separating experiments in panel."""
    count = {}
    for e in panel:
        for p in coverage[e]:
            count[p] = count.get(p, 0) + 1
    return count


def is_robust(panel, coverage, pairs, k=2):
    count = witnesses(panel, coverage)
    return all(count.get(p, 0) >= k for p in pairs)


def greedy_panel(coverage, costs, pairs, k=2):
    panel = []
    remaining = list(coverage.keys())
    while not is_robust(panel, coverage, pairs, k):
        count = witnesses(panel, coverage)
        best = None
        best_key = None
        for e in remaining:
            new = sum(1 for p in coverage[e] if count.get(p, 0) < k)
            # new witnesses per cost; tie: lower cost, then earlier name
            key = (new / costs[e], -costs[e])
            if best_key is None or key > best_key:
                best_key = key
                best = e
        if best is None or best_key[0] == 0:
            return None  # no robust panel in these experiments
        panel.append(best)
        remaining.remove(best)
    return panel


def optimal_panel(coverage, costs, pairs, k=2):
    exps = list(coverage.keys())
    # Search by increasing total cost, then by size, for exactness
    # on small instances. This is exhaustive and therefore a proof
    # of optimality for the instance, within the supplied experiments.
    subsets = []
    for r in range(len(exps) + 1):
        for combo in itertools.combinations(exps, r):
            if is_robust(list(combo), coverage, pairs, k):
                subsets.append(combo)
    if not subsets:
        return None
    subsets.sort(key=lambda c: (sum(costs[e] for e in c), len(c)))
    return list(subsets[0])


def find_instance(seed=20261024, max_tries=5000):
    rng = random.Random(seed)
    pairs = [f"P{i}" for i in range(1, 9)]
    for trial in range(max_tries):
        exps = [f"E{i}" for i in range(1, 11)]
        coverage = {}
        costs = {}
        for e in exps:
            costs[e] = rng.randint(1, 5)
            # each experiment separates 3-5 pairs
            coverage[e] = set(rng.sample(pairs, rng.randint(3, 5)))
        if not is_robust(exps, coverage, pairs, 2):
            continue
        greedy = greedy_panel(coverage, costs, pairs, 2)
        optimal = optimal_panel(coverage, costs, pairs, 2)
        if greedy is None or optimal is None:
            continue
        gc = sum(costs[e] for e in greedy)
        oc = sum(costs[e] for e in optimal)
        if gc > oc and gc >= oc + 3:
            return {
                "trial": trial,
                "pairs": pairs,
                "experiments": exps,
                "costs": costs,
                "coverage": {e: sorted(coverage[e]) for e in exps},
                "greedy_panel": greedy,
                "greedy_cost": gc,
                "optimal_panel": optimal,
                "optimal_cost": oc,
                "all_experiments_cost": sum(costs.values()),
            }
    return None


def main():
    result = find_instance()
    if result is None:
        print("No greedy-suboptimal instance found in the search bound.")
        return
    print(f"Found at trial {result['trial']}")
    print(f"Pairs: {result['pairs']}")
    print(f"Costs: {result['costs']}")
    print(f"Coverage: {result['coverage']}")
    print(f"Greedy panel: {result['greedy_panel']} cost={result['greedy_cost']}")
    print(f"Optimal panel: {result['optimal_panel']} cost={result['optimal_cost']}")
    print(f"All experiments (fixed protocol) cost={result['all_experiments_cost']}")
    # Verify both panels independently
    cov = {e: set(v) for e, v in result["coverage"].items()}
    assert is_robust(result["greedy_panel"], cov, result["pairs"], 2)
    assert is_robust(result["optimal_panel"], cov, result["pairs"], 2)
    assert result["optimal_cost"] < result["greedy_cost"]
    print("Verification: both panels are 2-robust, optimal is strictly cheaper.")
    with open(pathlib.Path(__file__).resolve().parent / "optimal_panel_transfer.json", "w") as f:
        json.dump(result, f, indent=2)
    print("wrote optimal_panel_transfer.json")


if __name__ == "__main__":
    main()
