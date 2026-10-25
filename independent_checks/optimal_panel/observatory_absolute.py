"""Panel analysis for the 2,197-state absolute interferometer.

Uses the shared engine in observatory_large.py (same semantics).

Pair-set subtlety, resolved from the fixture data: the absolute
system has TWO exact symmetries, both verified from the data with
zero violations -- sign reversal (x,y,z) -> (2z-x, 2z-y, z) and
global translation (x,y,z) -> (x+t, y+t, z+t), which fixes the
relative coordinates u = x-z, v = y-z that the sensor reads.  The
group they generate has exactly 85 orbits (84 of size 26, one of
size 13: the diagonal x=y=z), matching the fixture's own
expected_sign_orbit_count.  States in one orbit are inseparable by
every word.  A sign-only pair set (196,638 pairs) is therefore WRONG
for this system: it contains 26,286 translation-equivalent pairs
whose pair-automaton configurations can never separate (verified
below), which makes any two-witness panel infeasible for a spurious
reason.  The correct pair set is the inter-orbit pairs of the full
group inside each observation class: 170,352 pairs.  (The relative
fixture is exactly this quotient: its states are the (u,v), with the
same 85 sign orbits.)  On the corrected pair set the panel problem
is then solved exactly, as for the relative system.
"""

import json
import sys
import time
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from observatory_large import (build_automaton, check_symmetry, compute_words,
                               enumerate_sets_upto, greedy_panel,
                               is_robust_bits, load_system, negation_map,
                               two_cheapest)


def group_orbits(system):
    """Orbits under <translation by 1, negation>, by BFS on the two
    generators (both verified symmetries of the fixture data)."""
    n = len(system["states"])
    index = {s: i for i, s in enumerate(system["states"])}
    prime = system["mathematics"]["prime"]
    neg = negation_map(system, "absolute")

    def shift1(i):
        x, y, z = (int(t) for t in system["states"][i].split(","))
        return index[f"{(x + 1) % prime},{(y + 1) % prime},{(z + 1) % prime}"]

    orbit_of = [-1] * n
    sizes = []
    for i in range(n):
        if orbit_of[i] >= 0:
            continue
        oid = len(sizes)
        stack = [i]
        orbit_of[i] = oid
        size = 0
        while stack:
            s = stack.pop()
            size += 1
            for t in (shift1(s), neg[s]):
                if orbit_of[t] < 0:
                    orbit_of[t] = oid
                    stack.append(t)
        sizes.append(size)
    return orbit_of, sizes, neg


def pairs_for_orbits(system, orbit_of):
    classes = defaultdict(list)
    for i, o in enumerate(system["observations"]):
        classes[o].append(i)
    pairs, intra = [], 0
    for mem in classes.values():
        for x in range(len(mem)):
            for y in range(x + 1, len(mem)):
                i, j = mem[x], mem[y]
                if orbit_of[i] == orbit_of[j]:
                    intra += 1
                else:
                    pairs.append((i, j))
    return pairs, intra


def main():
    t0 = time.time()
    system = load_system("interferometer.json")
    n = len(system["states"])
    neg = negation_map(system, "absolute")
    neg_violations = check_symmetry(system, neg)
    _prime = system["mathematics"]["prime"]
    _index = {s: i for i, s in enumerate(system["states"])}
    shift_map = []
    for nm in system["states"]:
        x, y, z = (int(t) for t in nm.split(","))
        shift_map.append(_index[f"{(x + 1) % _prime},{(y + 1) % _prime},"
                                f"{(z + 1) % _prime}"])
    shift_violations = check_symmetry(system, shift_map)
    orbit_of, sizes, _ = group_orbits(system)
    pairs, intra = pairs_for_orbits(system, orbit_of)
    npairs = len(pairs)
    # sign-only pair set (the wrong one) for the diagnostic
    sign_orbits = [min(i, neg[i]) for i in range(n)]
    sign_pairs, sign_intra = pairs_for_orbits(system, sign_orbits)
    print(f"full-group orbits: {len(sizes)}; corrected pairs: {npairs}; "
          f"sign-only pairs: {len(sign_pairs)}; t={time.time()-t0:.1f}s",
          flush=True)

    # automaton first: exact d1, and the inseparability diagnostic
    cid, configs, trans, exits, dist = build_automaton(system)
    print(f"automaton: {len(configs)} configs; t={time.time()-t0:.1f}s",
          flush=True)
    d1 = []
    never = 0
    for (x, y) in pairs:
        c = cid[(min(x, y), max(x, y))]
        if c in dist:
            d1.append(dist[c])
        else:
            d1.append(None)
            never += 1
    # diagnostic: sign-only pairs NOT in the corrected set are exactly
    # the translation-equivalent ones; check none of them can ever
    # separate.
    corrected = {min(x, y) * n + max(x, y) for (x, y) in pairs}
    removed = [(x, y) for (x, y) in sign_pairs
               if min(x, y) * n + max(x, y) not in corrected]
    removed_can_separate = sum(
        1 for (x, y) in removed if cid[(min(x, y), max(x, y))] in dist)
    intra_can_separate = sum(
        1 for (px, py) in configs
        if px >= 0 and py >= 0 and orbit_of[px] == orbit_of[py]
        and cid[(px, py)] in dist)

    pair_index = {min(x, y) * n + max(x, y): k for k, (x, y) in enumerate(pairs)}
    words = compute_words(system, 6, pair_index, npairs)
    print(f"words <= 6: {len(words)}; t={time.time()-t0:.1f}s", flush=True)
    wit_total = [0] * npairs
    for w in words:
        b = w["bits"]
        while b:
            lsb = b & -b
            wit_total[lsb.bit_length() - 1] += 1
            b ^= lsb
    allmask = (1 << npairs) - 1
    gcost, gpanel = greedy_panel(words, npairs)
    best5, panel5, examined = enumerate_sets_upto(words, npairs, 5)
    # two-cheapest per pair: d1 = 1 for all (checked); d2 = 1 iff both
    # actions separate at step 1 of the start config.
    tc = []
    committed = {0: 0, 1: 0}
    for k, (x, y) in enumerate(pairs):
        c = cid[(min(x, y), max(x, y))]
        d2 = 1 if len(exits[c]) == 2 else None
        tc.append(two_cheapest(1, d2) if d1[k] == 1 else None)
        for a in (0, 1):
            other = 1 - a
            if other in exits[c]:
                continue
            nxt = trans[c][other]
            if nxt is not None and nxt not in dist:
                committed[a] += 1
    sensitivity = {}
    for L in range(0, 7):
        sub = [w for w in words if len(w["word"]) <= L]
        if L == 0:
            sensitivity[str(L)] = {"words": 0, "optimal_cost": None}
            continue
        b, p, _ = enumerate_sets_upto(sub, npairs, 5)
        g, gp = greedy_panel(sub, npairs)
        sensitivity[str(L)] = {"words": len(sub), "optimal_cost": b,
                               "greedy_cost": g}
    name = lambda i: [system["actions"][a]["name"] for a in words[i]["word"]]
    result = {
        "system": system["name"],
        "fixture": "examples/observatory/interferometer.json",
        "states": n,
        "actions": [a["name"] for a in system["actions"]],
        "negation_symmetry_violations": neg_violations,
        "translation_symmetry_violations": shift_violations,
        "full_group_orbits": len(sizes),
        "orbit_size_distribution": {str(k): v for k, v in
                                    Counter(sizes).items()},
        "pairs_inter_orbit_corrected": npairs,
        "pairs_intra_orbit_inseparable": intra,
        "sign_only_pair_set_diagnostic": {
            "sign_only_pairs": len(sign_pairs),
            "removed_translation_equivalent_pairs": len(removed),
            "removed_pairs_that_can_ever_separate": removed_can_separate,
        },
        "intra_orbit_configs_that_can_separate": intra_can_separate,
        "d1_from_automaton_distribution": {str(k): v for k, v in
                                           Counter(d1).items()},
        "pairs_never_separable_inter_orbit": never,
        "max_word_len": 6,
        "words_enumerated": len(words),
        "witness_count_per_pair_min": min(wit_total),
        "witness_count_per_pair_max": max(wit_total),
        "witness_count_per_pair_mean": sum(wit_total) / npairs,
        "every_word_separates_every_pair": all(v == len(words)
                                               for v in wit_total),
        "two_cheapest_per_pair_distribution": {str(k): v for k, v in
                                               Counter(tc).items()},
        "committed_pairs_depth1": {system["actions"][a]["name"]: committed[a]
                                   for a in (0, 1)},
        "lower_bound_disjoint_family": 0,
        "lower_bound_single_pair": max(v for v in tc if v is not None),
        "greedy": {"cost": gcost, "words": [name(i) for i in gpanel],
                   "verified_2_robust": is_robust_bits(
                       [words[i]["bits"] for i in gpanel], allmask)},
        "exhaustive_search_cost_upto_5": {"best_cost": best5,
                                          "sets_examined": examined},
        "optimal_cost": best5,
        "optimal_certified": best5 == 2,
        "sensitivity_by_word_length_cap": sensitivity,
        "seconds": round(time.time() - t0, 1),
    }
    (HERE / "absolute_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print("absolute: OPTIMAL", result["optimal_cost"],
          "| every word separates every pair:",
          result["every_word_separates_every_pair"],
          "| removed pairs that can separate:", removed_can_separate,
          "| d1 dist:", result["d1_from_automaton_distribution"])


if __name__ == "__main__":
    main()
