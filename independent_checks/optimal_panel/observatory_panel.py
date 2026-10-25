"""Two-witness optimal panels on a real PerfectJet Observatory system.

This runs the panel problem of optimal_panel_transfer.py on data from
this repository instead of on a synthetic instance: the branching
laboratory fixture, examples/observatory/branching-lab.json.

Definitions, following the repository's own Observatory semantics
(src/perfectjet/observatory/experiments.py):

- The system has 12 states and 3 unit-cost actions (route,
  inspect alpha, inspect beta). Its initial belief is the four hidden
  states, so the pairs to distinguish are the 6 unordered pairs of
  hidden states; all four share the initial observation "unread",
  which is free.
- An experiment is a fixed (non-adaptive) action word of length 1 to
  3; its cost is the sum of its action costs. Applying a word to a
  state produces a sequence of observations. An undefined transition
  produces a terminal observation, distinct from every live
  observation and the same for every terminal state, exactly as in
  pair_experiment. A word separates a pair if the two observation
  sequences differ at any step.
- A panel is two-witness (2-robust) if every pair is separated by at
  least two distinct words in the panel, so any single result can be
  lost without losing the distinction.

The optimum is computed exactly by branch-and-bound search over SETS
of distinct words (each word used at most once — running the same word
twice is one witness, not two), with an admissible lower bound, and is
certified by the same exact search proving every cheaper cost limit
infeasible. There is also a one-line human check of the lower bound
for this instance: the alpha pair and the beta pair have disjoint
witness sets, the two cheapest witnesses of each cost 2 + 3 = 5, so
every robust panel costs at least 10. The greedy panel uses the
witnesses-per-cost rule of optimal_panel_transfer.py.

Scope: this is one small real system, with words bounded at length 3.
It does not solve the panel problem for the larger Observatory
systems (169 or 2197 states), and an adaptive experiment, which the
repository's adaptive_experiment computes, is a different object from
the fixed panels considered here.
"""

import heapq
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE = ROOT / "examples" / "observatory" / "branching-lab.json"
TERMINAL = "<terminal>"
MAX_WORD_LEN = 3
DEMAND = 2


def observation_sequence(system, state, word):
    obs = []
    current = state
    for action in word:
        if current is None:
            obs.append(TERMINAL)
            continue
        nxt = system["transitions"][current][action]
        if nxt is None:
            current = None
            obs.append(TERMINAL)
        else:
            current = nxt
            obs.append(system["observations"][current])
    return tuple(obs)


def build_instance():
    system = json.loads(FIXTURE.read_text())
    belief = system["initial_belief"]
    pairs = [(belief[i], belief[j])
             for i in range(len(belief)) for j in range(i + 1, len(belief))]
    actions = list(range(len(system["actions"])))
    costs = {a: system["actions"][a]["cost"] for a in actions}
    words = []
    for length in range(1, MAX_WORD_LEN + 1):
        for word in itertools.product(actions, repeat=length):
            words.append(word)
    experiments = []
    for word in words:
        covers = []
        for k, (x, y) in enumerate(pairs):
            if observation_sequence(system, x, word) != observation_sequence(system, y, word):
                covers.append(k)
        experiments.append({
            "word": [system["actions"][a]["name"] for a in word],
            "cost": sum(costs[a] for a in word),
            "covers": covers,
        })
    return system, pairs, experiments


def is_robust(panel, experiments, npairs):
    counts = [0] * npairs
    for idx in panel:
        for k in experiments[idx]["covers"]:
            counts[k] += 1
    return all(c >= DEMAND for c in counts)


def _lower_bound_add(counts, used, experiments, npairs):
    """Admissible remaining-cost bound: for each pair still needing
    witnesses, the cheapest distinct unused experiments covering it;
    take the maximum over pairs."""
    bound = 0
    for k in range(npairs):
        need = DEMAND - counts[k]
        if need <= 0:
            continue
        costs = sorted(exp["cost"] for i, exp in enumerate(experiments)
                       if i not in used and k in exp["covers"])
        if len(costs) < need:
            return None  # infeasible from here
        bound = max(bound, sum(costs[:need]))
    return bound


def find_panel_within(experiments, npairs, limit):
    """Exact decision search: is there a SET of distinct experiments
    (each used at most once) with total cost <= limit that is
    2-robust? Branch on the under-covered pair with the fewest
    candidate experiments; returns (panel_or_None, nodes_explored)."""
    nodes = [0]

    def dfs(counts, used, cost):
        nodes[0] += 1
        if all(c >= DEMAND for c in counts):
            return sorted(used)
        add = _lower_bound_add(counts, used, experiments, npairs)
        if add is None or cost + add > limit:
            return None
        # choose under-covered pair with fewest candidates
        best_pair, best_cands = None, None
        for k in range(npairs):
            if counts[k] >= DEMAND:
                continue
            cands = [i for i, exp in enumerate(experiments)
                     if i not in used and k in exp["covers"]]
            if best_cands is None or len(cands) < len(best_cands):
                best_pair, best_cands = k, cands
        for idx in best_cands:
            exp = experiments[idx]
            new_counts = list(counts)
            for k in exp["covers"]:
                new_counts[k] = min(DEMAND, new_counts[k] + 1)
            used.add(idx)
            found = dfs(new_counts, used, cost + exp["cost"])
            if found is not None:
                return found
            used.remove(idx)
        return None

    panel = dfs([0] * npairs, set(), 0)
    return panel, nodes[0]


def optimal_panel(experiments, npairs):
    """Minimum-cost robust SET panel, certified by proving every
    cheaper limit infeasible with the same exact search."""
    witness = [0] * npairs
    for exp in experiments:
        for k in exp["covers"]:
            witness[k] += 1
    if any(w < DEMAND for w in witness):
        return None, [], {}
    start_counts = [0] * npairs
    lb = _lower_bound_add(start_counts, set(), experiments, npairs) or 0
    total = sum(e["cost"] for e in experiments)
    certificate = {"lower_bound_start": lb, "infeasible_limits": {}}
    limit = lb
    while limit <= total:
        panel, nodes = find_panel_within(experiments, npairs, limit)
        if panel is not None:
            certificate["feasible_limit_nodes"] = nodes
            return sum(experiments[i]["cost"] for i in panel), panel, certificate
        certificate["infeasible_limits"][str(limit)] = nodes
        limit += 1
    return None, [], certificate


def greedy_panel(experiments, npairs):
    counts = [0] * npairs
    chosen = []
    remaining = set(range(len(experiments)))
    while any(c < DEMAND for c in counts):
        best, best_key = None, None
        for idx in remaining:
            exp = experiments[idx]
            gain = sum(1 for k in exp["covers"] if counts[k] < DEMAND)
            if gain == 0:
                continue
            key = (gain / exp["cost"], gain, -exp["cost"])
            if best_key is None or key > best_key:
                best, best_key = idx, key
        if best is None:
            return None, []
        chosen.append(best)
        remaining.remove(best)
        for k in experiments[best]["covers"]:
            counts[k] += 1
    return sum(experiments[i]["cost"] for i in chosen), sorted(chosen)


def main():
    system, pairs, experiments = build_instance()
    npairs = len(pairs)
    witness_counts = [0] * npairs
    for exp in experiments:
        for k in exp["covers"]:
            witness_counts[k] += 1
    feasible = all(c >= DEMAND for c in witness_counts)
    opt_cost, opt_panel, certificate = optimal_panel(experiments, npairs)
    greedy_cost, greedy = greedy_panel(experiments, npairs)
    pair_names = [[system["states"][x], system["states"][y]] for x, y in pairs]
    result = {
        "system": system["name"],
        "fixture": "examples/observatory/branching-lab.json",
        "initial_belief": [system["states"][i] for i in system["initial_belief"]],
        "pairs": pair_names,
        "word_lengths": [1, MAX_WORD_LEN],
        "experiments_considered": len(experiments),
        "witness_counts_per_pair": witness_counts,
        "feasible": feasible,
        "optimal_panel": {
            "cost": opt_cost,
            "words": [experiments[i]["word"] for i in opt_panel],
            "verified_2_robust": is_robust(opt_panel, experiments, npairs),
            "certified_no_cheaper_panel": opt_cost is not None,
            "exact_search_certificate": certificate,
        },
        "greedy_panel": {
            "cost": greedy_cost,
            "words": [experiments[i]["word"] for i in greedy],
            "verified_2_robust": is_robust(greedy, experiments, npairs),
        },
        "all_experiments_cost": sum(e["cost"] for e in experiments),
        "coverage_table": experiments,
    }
    out = HERE / "observatory_panel.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"system: {system['name']}")
    print(f"pairs: {npairs}; experiments (words len 1..{MAX_WORD_LEN}): {len(experiments)}")
    print(f"witness counts per pair: {witness_counts}; feasible: {feasible}")
    print(f"optimal panel cost {opt_cost}: {[experiments[i]['word'] for i in opt_panel]}")
    print(f"optimal verified 2-robust: {result['optimal_panel']['verified_2_robust']}; "
          f"cheaper limits proved infeasible by exact search: "
          f"{certificate['infeasible_limits']}")
    print(f"greedy panel cost {greedy_cost}: {[experiments[i]['word'] for i in greedy]}")
    print(f"all experiments cost: {result['all_experiments_cost']}")
    print("wrote observatory_panel.json")


if __name__ == "__main__":
    main()
