"""Panel analysis at scale for the PerfectJet Observatory interferometers.

Shared engine + the 169-state relative interferometer + the branching
laboratory verification.  The 2,197-state absolute system is handled by
observatory_absolute.py, which imports this module.

Semantics (the repository's own, src/perfectjet/observatory/experiments.py):
- The initial observation is free.  The initially-possible states (the
  belief) are the states sharing the initial state's observation; the
  panel problem is over the unordered pairs of belief states, for every
  observation class at once (a fixed panel must serve whichever class
  the free initial observation reveals).
- A word's outcome on a state is its sequence of observations; an
  undefined transition gives a terminal observation distinct from every
  live one and the same for every terminal state.  A word separates a
  pair iff the two outcome sequences differ at any step.  Separation is
  monotone under extension: a word separating a pair at some step keeps
  separating it under every extension.
- A panel is 2-robust (two-witness) iff every pair is separated by at
  least two distinct words of the panel.  Word cost = sum of action
  costs (all unit here, so cost = length).

Pair-set quotient (proved from the fixture data in the engine): the
negation symmetry (u,v) -> (-u,-v) of the relative system (resp.
(x,y,z) -> (2z-x, 2z-y, z) for the absolute system) preserves every
observation and commutes with every transition, so orbit-mates produce
identical outcomes under EVERY word and can never be separated.  The
panel problem is therefore posed on inter-orbit pairs inside each
observation class; intra-orbit pairs are reported as provably
inseparable, matching the fixtures' own mathematics
("simultaneous sign reversal is invisible", 85 sign orbits).
"""

import heapq
import itertools
import json
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # repository root, from independent_checks/optimal_panel/
TERMINAL = ("undefined",)


def load_system(name):
    path = ROOT / "examples" / "observatory" / name
    return json.loads(path.read_text())


def okey(system, pos):
    """Observation key of a position (state index or -1 = terminal)."""
    return TERMINAL if pos == -1 else ("live", system["observations"][pos])


def step(system, pos, action):
    if pos == -1:
        return -1
    nxt = system["transitions"][pos][action]
    return -1 if nxt is None else nxt


# ---------------------------------------------------------------- orbits

def negation_map(system, kind):
    """Index map of the sign-reversal symmetry, from state coordinates."""
    prime = system["mathematics"]["prime"]
    index = {s: i for i, s in enumerate(system["states"])}
    neg = []
    for name in system["states"]:
        coords = [int(t) for t in name.split(",")]
        if kind == "relative":
            u, v = coords
            neg.append(index[f"{(-u) % prime},{(-v) % prime}"])
        elif kind == "absolute":
            x, y, z = coords
            neg.append(index[f"{(2 * z - x) % prime},{(2 * z - y) % prime},{z}"])
        else:
            raise ValueError(kind)
    return neg


def check_symmetry(system, neg):
    """Verify from the data that negation preserves observations and
    commutes with every transition.  Returns the number of violations;
    0 means orbit-mates are inseparable by every word (induction on
    word length: equal observations at every step)."""
    bad = 0
    for i in range(len(system["states"])):
        if system["observations"][neg[i]] != system["observations"][i]:
            bad += 1
        for a in range(len(system["actions"])):
            t = system["transitions"][i][a]
            tn = system["transitions"][neg[i]][a]
            if (t is None) != (tn is None):
                bad += 1
            elif t is not None and tn != neg[t]:
                bad += 1
    return bad


def orbit_ids(neg):
    return [min(i, neg[i]) for i in range(len(neg))]


def build_pairs(system, orbits):
    """Inter-orbit pairs inside each observation class, plus counts."""
    classes = defaultdict(list)
    for i, o in enumerate(system["observations"]):
        classes[o].append(i)
    pairs = []
    intra = 0
    for mem in classes.values():
        for x in range(len(mem)):
            for y in range(x + 1, len(mem)):
                i, j = mem[x], mem[y]
                if orbits[i] == orbits[j]:
                    intra += 1
                else:
                    pairs.append((i, j))
    return pairs, intra, {k: len(v) for k, v in classes.items()}


# ---------------------------------------------------------------- words

def compute_words(system, max_len, pair_index=None, npairs=0):
    """Enumerate all words of length 1..max_len level by level.

    Returns a list of word records: word (tuple of action indices),
    cost, parent index, and (if pair_index given) the bitset over the
    pair list of pairs this word separates.  Outcome labels are the
    canonical encoding of the full observation sequence per state, so
    two states share a label under a word iff the word does not
    separate them.
    """
    n = len(system["states"])
    nact = len(system["actions"])
    costs = [a["cost"] for a in system["actions"]]
    words = []
    # level entries: (word, cur positions list, labels list)
    level = [((), list(range(n)), [0] * n)]
    allmask = (1 << npairs) - 1 if npairs else 0
    for length in range(1, max_len + 1):
        next_level = []
        for word, cur, labels in level:
            for a in range(nact):
                ncur = [step(system, cur[s], a) for s in range(n)]
                mapping = {}
                nlabels = [0] * n
                for s in range(n):
                    key = (labels[s], okey(system, ncur[s]))
                    lab = mapping.get(key)
                    if lab is None:
                        lab = len(mapping)
                        mapping[key] = lab
                    nlabels[s] = lab
                nword = word + (a,)
                rec = {"word": nword,
                       "cost": sum(costs[x] for x in nword),
                       "parent": None}
                if pair_index is not None:
                    groups = defaultdict(list)
                    for s in range(n):
                        groups[nlabels[s]].append(s)
                    notsep = 0
                    for mem in groups.values():
                        for x in range(len(mem)):
                            base = mem[x] * n
                            for y in range(x + 1, len(mem)):
                                k = pair_index.get(base + mem[y])
                                if k is not None:
                                    notsep |= 1 << k
                    rec["bits"] = allmask ^ notsep
                words.append(rec)
                next_level.append((nword, ncur, nlabels))
        level = next_level
    # parent indices: word minus last action
    index_of = {w["word"]: i for i, w in enumerate(words)}
    for w in words:
        if len(w["word"]) > 1:
            w["parent"] = index_of[w["word"][:-1]]
    return words


def witness_stats(words, npairs, max_len):
    """Per-pair witness counts by exact word length and the two
    cheapest witness costs within the enumerated word set."""
    counts_by_len = [[0] * (max_len + 1) for _ in range(npairs)]
    cheapest = [[] for _ in range(npairs)]
    for w in words:
        bits = w["bits"]
        L = len(w["word"])
        b = bits
        while b:
            lsb = b & -b
            k = lsb.bit_length() - 1
            counts_by_len[k][L] += 1
            if len(cheapest[k]) < 4:
                cheapest[k].append(w["cost"])
            b ^= lsb
    for k in range(npairs):
        cheapest[k].sort()
    return counts_by_len, cheapest


def panel_counts_mask(panel_bits_list):
    """(covered>=1 mask, covered>=2 mask) for a list of word bitsets."""
    s1 = 0
    s2 = 0
    for b in panel_bits_list:
        s2 |= s1 & b
        s1 |= b
    return s1, s2


def is_robust_bits(panel_bits_list, allmask):
    return panel_counts_mask(panel_bits_list)[1] == allmask


def greedy_panel(words, npairs):
    """Wave-one greedy rule: maximise (gain/cost, gain, -cost), where
    gain = number of pairs still needing a witness that the word
    separates.  Deterministic tie-break by word order."""
    allmask = (1 << npairs) - 1
    zero = allmask
    one = 0
    chosen = []
    used = [False] * len(words)
    while zero | one:
        need = zero | one
        best, best_key = -1, None
        for i, w in enumerate(words):
            if used[i]:
                continue
            gain = (w["bits"] & need).bit_count()
            if gain == 0:
                continue
            key = (gain / w["cost"], gain, -w["cost"])
            if best_key is None or key > best_key:
                best, best_key = i, key
        if best < 0:
            return None, []
        b = words[best]["bits"]
        one = (one & ~b) | (b & zero)
        zero &= ~b
        used[best] = True
        chosen.append(best)
    return sum(words[i]["cost"] for i in chosen), sorted(chosen)


def enumerate_sets_upto(words, npairs, cap):
    """Exhaustively enumerate word SETS with total cost <= cap.
    Returns (best_cost_or_None, best_panel, sets_examined).  A set is
    2-robust iff the covered>=2 mask is full.  Complete: every panel
    cheaper than the incumbent is enumerated, which certifies the
    optimum when combined with a feasible panel of that cost."""
    allmask = (1 << npairs) - 1
    order = sorted(range(len(words)), key=lambda i: (words[i]["cost"], i))
    best = [None, None]
    examined = [0]

    def dfs(start, cost, s1, s2, chosen):
        examined[0] += 1
        if s2 == allmask:
            if best[0] is None or cost < best[0]:
                best[0] = cost
                best[1] = list(chosen)
            return
        if cost >= cap:
            return
        for pos in range(start, len(order)):
            i = order[pos]
            c = words[i]["cost"]
            if cost + c > cap:
                break  # order sorted by cost
            b = words[i]["bits"]
            dfs(pos + 1, cost + c, s1 | b, s2 | (s1 & b), chosen + [i])

    dfs(0, 0, 0, 0, [])
    return best[0], best[1], examined[0]


# ---------------------------------------------------------------- automaton

def build_automaton(system):
    """Pair automaton over non-exit configurations: unordered pairs of
    positions (state or -1) whose observation keys agree.  Returns
    (config_id dict, transitions, exit_actions) where transitions[c]
    maps action -> next config id or None (that action separates).
    Reverse BFS gives dist[c] = length of the shortest separating word
    from c (the pair-automaton ground truth, independent of any word
    length cap), and membership in dist = 'can ever separate'."""
    n = len(system["states"])
    positions = list(range(-1, n))
    cid = {}
    configs = []
    for x in range(len(positions)):
        for y in range(x + 1, len(positions)):
            px, py = positions[x], positions[y]
            if okey(system, px) == okey(system, py):
                cid[(px, py)] = len(configs)
                configs.append((px, py))
    # Diagonal configurations (px, px): reachable when a deterministic
    # action merges the two trajectories (or both terminate).  They
    # never separate again, but they must exist as automaton nodes.
    for p in positions:
        cid[(p, p)] = len(configs)
        configs.append((p, p))
    trans = []
    exits = []
    for (px, py) in configs:
        row = []
        ex = []
        for a in range(len(system["actions"])):
            nx, ny = step(system, px, a), step(system, py, a)
            if okey(system, nx) != okey(system, ny):
                row.append(None)
                ex.append(a)
            else:
                row.append(cid[(min(nx, ny), max(nx, ny))])
        trans.append(row)
        exits.append(ex)
    rev = defaultdict(list)
    for c, row in enumerate(trans):
        for nxt in row:
            if nxt is not None:
                rev[nxt].append(c)
    dist = {}
    dq = deque()
    for c, ex in enumerate(exits):
        if ex:
            dist[c] = 1
            dq.append(c)
    while dq:
        c = dq.popleft()
        for p in rev.get(c, ()):
            if p not in dist:
                dist[p] = dist[c] + 1
                dq.append(p)
    return cid, configs, trans, exits, dist


def second_minimal_length(system, cid, trans, exits, start_config, cap_len=14):
    """Second-smallest minimal-separator length d2 for one start
    config, by enumerating words in increasing length order (BFS over
    the word tree, tracking configs).  Minimal words are exactly the
    words whose first exit step is their last step.  Returns None if
    fewer than two minimal separators exist within cap_len."""
    found = []
    # heap entries: (length, config); expand level by level, counting
    # distinct words.  Keep per-config arrival counts per length to
    # avoid exponential blowup: at most 2 distinct shortest arrivals
    # matter for the first two exits overall.
    from collections import Counter
    frontier = Counter({start_config: 1})
    length = 0
    while frontier and length < cap_len:
        length += 1
        nxt = Counter()
        for c, cnt in frontier.items():
            for a in range(len(trans[c])):
                if trans[c][a] is None:
                    found.extend([length] * cnt)
                else:
                    nxt[trans[c][a]] += cnt
        # cap counts at 2: more arrivals cannot change the first two
        frontier = Counter({c: min(v, 2) for c, v in nxt.items()})
        if len(found) >= 2:
            break
    found.sort()
    if len(found) >= 2:
        return found[1]
    return None


def two_cheapest(d1, d2):
    """Exact cost of the two cheapest distinct witnesses of a pair in
    the UNRESTRICTED word universe, given the two smallest minimal
    separator lengths d1 <= d2 (d2 may be None = infinity): the two
    cheapest witnesses are either two distinct minimal separators
    (costs d1, d2) or a minimal separator and its cheapest extension
    (costs d1, d1+1); every other witness is an extension of some
    minimal separator and costs no less than the corresponding case."""
    second = d1 + 1 if d2 is None else min(d2, d1 + 1)
    return d1 + second


# ---------------------------------------------------------------- lab check

def lab_check():
    sys.path.insert(0, str(HERE))
    system = load_system("branching-lab.json")
    belief = system["initial_belief"]
    pairs = [(belief[i], belief[j]) for i in range(len(belief))
             for j in range(i + 1, len(belief))]
    npairs = len(pairs)
    n = len(system["states"])
    pair_index = {min(x, y) * n + max(x, y): k for k, (x, y) in enumerate(pairs)}
    words = compute_words(system, 3, pair_index, npairs)
    counts = [0] * npairs
    for w in words:
        b = w["bits"]
        while b:
            lsb = b & -b
            counts[lsb.bit_length() - 1] += 1
            b ^= lsb
    gcost, gpanel = greedy_panel(words, npairs)
    # exact optimum via the wave-one DFS decision search, run on THIS
    # engine's coverage data (independent second implementation).
    wave_dir = HERE  # wave one's observatory_panel.py lives in this directory
    sys.path.insert(0, str(wave_dir))
    import observatory_panel as wave1
    experiments = [{"word": [system["actions"][a]["name"] for a in w["word"]],
                    "cost": w["cost"],
                    "covers": [k for k in range(npairs) if w["bits"] >> k & 1]}
                   for w in words]
    opt_cost, opt_panel, cert = wave1.optimal_panel(experiments, npairs)
    wave_json = json.loads((wave_dir / "observatory_panel.json").read_text())
    covers_match = all(
        set(e["covers"]) == set(wave_json["coverage_table"][i]["covers"])
        for i, e in enumerate(experiments))
    result = {
        "system": system["name"],
        "pairs": [[system["states"][x], system["states"][y]] for x, y in pairs],
        "experiments_considered": len(words),
        "witness_counts_per_pair": counts,
        "expected_witness_counts": wave_json["witness_counts_per_pair"],
        "witness_counts_match_wave1": counts == wave_json["witness_counts_per_pair"],
        "coverage_table_matches_wave1": covers_match,
        "greedy_cost": gcost,
        "greedy_words": [[system["actions"][a]["name"] for a in words[i]["word"]]
                         for i in gpanel],
        "expected_greedy_cost": wave_json["greedy_panel"]["cost"],
        "optimal_cost": opt_cost,
        "optimal_words": [experiments[i]["word"] for i in opt_panel],
        "expected_optimal_cost": wave_json["optimal_panel"]["cost"],
        "optimal_verified_2_robust": is_robust_bits(
            [words[i]["bits"] for i in opt_panel], (1 << npairs) - 1),
    }
    result["all_expectations_met"] = (
        result["witness_counts_match_wave1"] and covers_match
        and gcost == result["expected_greedy_cost"]
        and opt_cost == result["expected_optimal_cost"]
        and result["optimal_verified_2_robust"])
    return result


def relative_main(max_len=6):
    system = load_system("relative-interferometer.json")
    t0 = time.time()
    neg = negation_map(system, "relative")
    violations = check_symmetry(system, neg)
    orbits = orbit_ids(neg)
    pairs, intra, class_sizes = build_pairs(system, orbits)
    npairs = len(pairs)
    n = len(system["states"])
    pair_index = {min(x, y) * n + max(x, y): k for k, (x, y) in enumerate(pairs)}
    words = compute_words(system, max_len, pair_index, npairs)
    counts_by_len, cheapest = witness_stats(words, npairs, max_len)
    total_by_len = [sum(1 for w in words if len(w["word"]) == L)
                    for L in range(max_len + 1)]
    wit_total = [sum(counts_by_len[k]) for k in range(npairs)]
    # automaton ground truth
    cid, configs, trans, exits, dist = build_automaton(system)
    d1_auto = []
    never_sep_pairs = 0
    for (x, y) in pairs:
        c = cid[(min(x, y), max(x, y))]
        if c in dist:
            d1_auto.append(dist[c])
        else:
            d1_auto.append(None)
            never_sep_pairs += 1
    intra_configs_never = 0
    intra_configs = 0
    for (px, py) in configs:
        if px >= 0 and py >= 0 and orbits[px] == orbits[py]:
            intra_configs += 1
            if cid[(px, py)] not in dist:
                intra_configs_never += 1
    # commitment classes at depth 1 (automaton): pair committed to
    # action a iff the other action neither separates at step 1 nor
    # reaches a config that can ever separate.
    committed = {0: [], 1: []}
    tc = []
    for k, (x, y) in enumerate(pairs):
        c = cid[(min(x, y), max(x, y))]
        d1 = d1_auto[k]
        # d2 == 1 iff both actions already separate at step 1;
        # otherwise enumerate minimal separators in length order.
        d2 = 1 if len(exits[c]) == 2 else second_minimal_length(
            system, cid, trans, exits, c)
        tc.append(two_cheapest(d1, d2))
        for a in (0, 1):
            other = 1 - a
            if other in exits[c]:
                continue
            nxt = trans[c][other]
            if nxt is not None and nxt not in dist:
                committed[a].append(k)
    fam_lb = sum(max((tc[k] for k in committed[a]), default=0) for a in (0, 1))
    single_lb = max(tc)
    family_lb = max(fam_lb, single_lb)
    # greedy + exhaustive exact optimum (sets of total cost <= 5; the
    # optimum is <= 6 by the {A,B,AA,BB} construction whenever d1==1,
    # and in fact {A,B} is feasible here -- the enumeration decides).
    gcost, gpanel = greedy_panel(words, npairs)
    best5, panel5, examined = enumerate_sets_upto(words, npairs, 5)
    construction = {}
    name_of = {w["word"]: i for i, w in enumerate(words)}
    for cand in [("A",), ("B",), ("A", "B"), ("A", "B", "AA", "BB")]:
        # cand entries are words as strings over {A,B}
        idxs = []
        ok = True
        for wname in cand:
            wt = tuple({"A": 0, "B": 1}[ch] for ch in wname)
            if wt in name_of:
                idxs.append(name_of[wt])
            else:
                ok = False
        construction["+".join(cand)] = {
            "cost": sum(words[i]["cost"] for i in idxs) if ok else None,
            "robust": bool(ok and is_robust_bits(
                [words[i]["bits"] for i in idxs], (1 << npairs) - 1)),
        }
    # sensitivity of the optimum to the word-length cap L: optimum
    # over words of length <= L, by the same exhaustive enumeration
    # (cap 5) plus feasibility of the best panel found at that L.
    sensitivity = {}
    for L in range(0, max_len + 1):
        sub = [w for w in words if len(w["word"]) <= L]
        if L == 0:
            sensitivity[L] = {"words": 0, "optimal_cost": None,
                              "note": "no words: pairs have no witnesses"}
            continue
        b, p, _ = enumerate_sets_upto(sub, npairs, 5)
        # also greedy at this L as an upper bound certificate
        g, gp = greedy_panel(sub, npairs)
        sensitivity[L] = {"words": len(sub),
                          "optimal_cost": b if b is not None else g,
                          "certified_by_exhaustion_upto_5": b is not None,
                          "greedy_cost": g}
    result = {
        "system": system["name"],
        "fixture": "examples/observatory/relative-interferometer.json",
        "states": n,
        "actions": [a["name"] for a in system["actions"]],
        "observation_class_sizes": {str(k): v for k, v in class_sizes.items()},
        "negation_symmetry_violations": violations,
        "sign_orbits": len(set(orbits)),
        "pairs_inter_orbit": npairs,
        "pairs_intra_orbit_inseparable": intra,
        "max_word_len": max_len,
        "words_enumerated": len(words),
        "witness_count_per_pair_min": min(wit_total),
        "witness_count_per_pair_max": max(wit_total),
        "witness_count_per_pair_mean": sum(wit_total) / npairs,
        "every_word_separates_every_pair": all(
            v == len(words) for v in wit_total),
        "d1_from_automaton_distribution": {
            str(k): d1_auto.count(k) for k in sorted(set(d1_auto)) if k is not None},
        "pairs_never_separable_inter_orbit": never_sep_pairs,
        "intra_orbit_configs": intra_configs,
        "intra_orbit_configs_never_separate": intra_configs_never,
        "two_cheapest_per_pair_distribution": {
            str(k): tc.count(k) for k in sorted(set(tc))},
        "committed_pairs_depth1": {system["actions"][a]["name"]: len(committed[a])
                                   for a in (0, 1)},
        "lower_bound_disjoint_family": fam_lb,
        "lower_bound_single_pair": single_lb,
        "lower_bound_certified": family_lb,
        "greedy": {"cost": gcost,
                   "words": [[system["actions"][a]["name"] for a in words[i]["word"]]
                             for i in gpanel],
                   "verified_2_robust": is_robust_bits(
                       [words[i]["bits"] for i in gpanel], (1 << npairs) - 1)},
        "exhaustive_search_cost_upto_5": {"best_cost": best5,
                                          "sets_examined": examined},
        "constructions": construction,
        "optimal_cost": best5,
        "optimal_certified": best5 is not None and best5 == family_lb,
        "sensitivity_by_word_length_cap": {str(k): v for k, v in sensitivity.items()},
        "seconds": round(time.time() - t0, 2),
    }
    return result


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    if phase in ("lab", "all"):
        res = lab_check()
        (HERE / "lab_check.json").write_text(json.dumps(res, indent=2) + "\n")
        print("lab: witness counts", res["witness_counts_per_pair"],
              "match:", res["witness_counts_match_wave1"],
              "| coverage match:", res["coverage_table_matches_wave1"],
              "| greedy", res["greedy_cost"], "(expected", res["expected_greedy_cost"],
              ") | optimal", res["optimal_cost"], "(expected",
              res["expected_optimal_cost"], ") | ALL OK:", res["all_expectations_met"])
    if phase in ("relative", "all"):
        res = relative_main()
        (HERE / "relative_results.json").write_text(json.dumps(res, indent=2) + "\n")
        print("relative: pairs", res["pairs_inter_orbit"],
              "| every word separates every pair:", res["every_word_separates_every_pair"],
              "| LB", res["lower_bound_certified"], "| greedy", res["greedy"]["cost"],
              "| exhaustive best <=5:", res["exhaustive_search_cost_upto_5"]["best_cost"],
              "| OPTIMAL", res["optimal_cost"], "certified:", res["optimal_certified"])
