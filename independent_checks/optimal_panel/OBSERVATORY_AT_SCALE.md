# Observatory panels at scale: the 169-state and 2,197-state interferometers

## 0. Problem, semantics, and the pair set

Definitions follow the repository's own Observatory semantics
(`src/perfectjet/observatory/experiments.py`) and wave one's panel
programme (PR #6, `observatory_panel.py`):

- The initial observation is free. The initially-possible states (the
  belief) are the states sharing the initial observation; the panel
  problem is posed over the unordered pairs of belief states, for all
  observation classes simultaneously (a fixed panel must serve
  whichever class the free initial observation reveals).
- A word's outcome on a state is its sequence of observations. An
  undefined transition produces a terminal observation distinct from
  every live observation and identical for every terminal state. A
  word separates a pair iff the two outcome sequences differ at any
  step; separation is monotone under extension (a difference at step
  $k$ persists in every extension).
- A panel is **2-robust** (two-witness) iff every pair is separated by
  at least two distinct words of the panel. Word cost is the sum of
  action costs; all actions here cost 1, so cost = word length.
- What is being identified is the state **up to the system's intrinsic
  symmetry**, and this qualification is forced, not chosen: both
  interferometer fixtures carry a sign-reversal symmetry —
  $(u,v)\mapsto(-u,-v)$ for the relative system,
  $(x,y,z)\mapsto(2z-x,\,2z-y,\,z)$ for the absolute system (negating
  the relative coordinates $u=x-z$, $v=y-z$) — which the engine
  verifies directly from the fixture data (0 violations in both
  systems): it preserves every observation and commutes with every
  transition. By induction on word length, orbit-mates therefore
  produce identical outcome sequences under **every** word and can
  never be separated; the pair automaton confirms this independently
  (every intra-orbit configuration is outside the set of
  configurations that can ever separate). This matches the fixtures'
  own mathematics ("simultaneous sign reversal is invisible";
  `expected_sign_orbit_count` 85 for the relative system). The pair
  set $\mathcal P$ is thus the inter-orbit pairs inside each
  observation class, and intra-orbit pairs are reported as provably
  inseparable. Demanding witnesses for intra-orbit pairs would make
  the problem infeasible for a reason that has nothing to do with
  panels.

**Verification gate (branching laboratory).** Before any scale work,
the engine in `observatory_large.py` was run on
`examples/observatory/branching-lab.json` with the wave-one
definitions (belief from the fixture, words of length 1–3, 39 words,
6 pairs). It reproduces wave one exactly: witness counts per pair
$[4,13,13,13,13,4]$, the full coverage table identical to
`observatory_panel.json`, greedy cost 11, and — running wave one's own
exact DFS decision search on this engine's coverage data — optimal
cost 10, with the returned panel verified 2-robust. A second
independent cross-check used the repository's own
`pair_experiment` (Dijkstra) on the relative system: 12 sampled
inter-orbit pairs all returned a distinguishing word of cost 1, and 6
sampled intra-orbit pairs all returned status `infinite`
(`repo_crosscheck.log`).

## 1. The 169-state relative interferometer: optimal cost 2, certified

Fixture facts. 169 states, actions $A,B$ (unit cost), 13 observation
classes (the $q=0$ class has 25 states; the other twelve classes have
12 each), 85 sign orbits. $|\mathcal P| = 1008$ inter-orbit pairs;
84 intra-orbit pairs are provably inseparable (above).

The panel problem on this system collapses completely, for a reason
the computation makes exact:

- **Every pair has distinguishing depth $d_1 = 1$, via both actions.**
  The pair automaton (1,092 non-exit configurations plus diagonals;
  reverse BFS) gives $d_1 = 1$ for all 1,008 pairs, and the start
  configuration of every pair has **both** actions as separating
  steps: each of the words $A$ and $B$ alone separates every pair in
  $\mathcal P$. (Direct check from the data: length-1 split A-only 0,
  B-only 0, both 1008, neither 0.)
- By monotonicity under extension, **every word separates every
  pair**: all 126 words of length $\le 6$ are witnesses for all 1,008
  pairs (witness count per pair: min = max = mean = 126 at $L=6$).
  The two-cheapest witness cost of every pair is exactly $1+1 = 2$.

Certificates for the optimum (three independent arguments):
1. **Lower bound 2.** Any 2-robust panel contains at least two
   distinct words, each of cost $\ge 1$; the disjoint-witness-family
   machinery below evaluates to the same number here: every pair has
   two-cheapest cost 2, while the depth-1 commitment classes are
   *empty* (a pair committed to first action $A$ would need a
   separating-word set disjoint from $B$-first words, but $B$ itself
   separates every pair), so no two pairs have disjoint witness sets
   and the family bound is the single-pair bound, 2.
2. **Construction.** The panel $\{A, B\}$ (cost 2) is 2-robust:
   verified directly from the computed bitsets — every pair is
   separated by both words.
3. **Exhaustive enumeration.** All word sets of total cost $\le 5$
   over the 126 words were enumerated (158 sets examined); the
   cheapest 2-robust set found has cost 2, and no set of cost 1 is
   2-robust. (Any panel of cost $\le 5$ uses only words of length
   $\le 5$, all of which are in the enumerated universe, so this also
   covers panels using longer alphabets of words up to that cost.)

**Optimal panel cost for the 169-state system is exactly 2**,
attained by $\{A,B\}$; greedy (wave-one rule) also finds cost 2.
Word-length sensitivity: the optimum is 2 for every cap $L \ge 1$
(words of length $\le L$), certified by the same enumeration at each
$L$; at $L=0$ the problem is infeasible (no words, no witnesses). The
earlier guess $\{A,B,AA,BB\}$ of cost 6 is feasible but far from
optimal — it assumed each pair was separated by only one of the two
length-1 words, which the data refute.

Scope note. This is the fixed (non-adaptive) two-witness panel
problem, as in wave one. The repository's adaptive experiment is a
different object; nothing here speaks to it. Also, the result is a
statement about this fixture's arithmetic: with sensor $u^2+v^2 \bmod
13$ and the two shears, one step of *either* shear already moves every
two states from distinct sign orbits in the same sensor class to
distinct sensor values (or exactly one of them to the blocked,
terminal outcome). The collapse is a property of the system, not of
the method: the same engine leaves the branching laboratory at
optimal 10 vs greedy 11, and the absolute system below has real depth.

## 2. The 2,197-state absolute interferometer

## 2. The 2,197-state absolute interferometer: optimal cost 2, after a necessary correction

Fixture facts. 2,197 states $(x,y,z) \in \mathbb F_{13}^3$, actions
$A,B$ (unit cost), sensor $q = u^2+v^2 \bmod 13$ on the relative
coordinates $u=x-z$, $v=y-z$; 13 observation classes (the $q=0$ class
has 325 states; the other twelve have 156 each).

**The pair set needs the full symmetry group, and getting this wrong
is silently fatal.** This system has *two* exact symmetries, both
verified from the fixture data with 0 violations: sign reversal
$(x,y,z)\mapsto(2z-x,2z-y,z)$ and global translation
$(x,y,z)\mapsto(x{+}t,y{+}t,z{+}t)$, which fixes the relative
coordinates the sensor reads. The group they generate has exactly
**85 orbits** — 84 of size 26 (13 translations × 2 signs) and one of
size 13 (the diagonal $x=y=z$, where $u=v=0$ is sign-fixed) —
matching the fixture's `expected_sign_orbit_count: 85`. A first run
using sign orbits only (196,638 pairs) produced a greedy stall: some
pairs had no witness of any length. The automaton diagnosis is exact:
26,286 of those pairs are translation-equivalent, and **none of them
can ever separate** (their configurations lie outside the automaton's
separating set; 0 exceptions), so with the sign-only pair set the
panel problem is infeasible for a spurious reason — the same trap as
the intra-orbit pairs of §0, one symmetry larger. With the corrected
pair set (inter-orbit pairs of the full group), there are
$|\mathcal P| = 170{,}352$ pairs, and 27,378 intra-orbit
same-observation pairs are provably inseparable; the automaton also
confirms that no intra-orbit configuration of any kind can separate
(0 of all such configurations).

On the corrected pair set the system collapses exactly as the
relative one did — unsurprising in hindsight, since the relative
fixture *is* the quotient of this one by translation (its states are
the $(u,v)$, with the same 85 sign orbits):

- $d_1 = 1$ for all 170,352 pairs (pair automaton: 199,928
  configurations, reverse BFS), via **both** actions: every pair is
  separated by the word $A$ and by the word $B$. The 26,286 removed
  pairs were precisely those separated by neither length-1 word.
- Every word separates every pair (witness count per pair at $L=6$:
  min = max = mean = 126); two-cheapest cost is exactly 2 for every
  pair; depth-1 commitment classes are empty.
- **Optimal panel cost is exactly 2**, attained by $\{A,B\}$:
  certified by the same three arguments as §1 (single-pair lower
  bound 2 — the disjoint-family bound again evaluates to the
  single-pair bound because no two pairs have disjoint witness sets;
  direct bitset verification of the construction; exhaustive
  enumeration of all word sets of total cost $\le 5$, 158 sets,
  cheapest robust cost 2). Greedy also finds 2. Sensitivity: optimum
  2 at every word-length cap $L \ge 1$; infeasible at $L=0$.
- Independent cross-check with the repository's own
  `pair_experiment`: 8 sampled inter-orbit pairs all returned a
  distinguishing word of cost 1; 5 sampled same-full-orbit pairs all
  returned `infinite` (`repo_crosscheck_absolute.log`).

## 3. Summary: what is optimal, what is a bound, what is heuristic

| system | pairs $\mathcal P$ | result | status |
|---|---|---|---|
| branching laboratory (gate) | 6 | optimal 10, greedy 11 | exact (wave-one DFS on this engine's data; reproduces PR #6) |
| relative interferometer, 169 states | 1,008 | **optimal 2** = $\{A,B\}$ | **certified exact**: lower bound 2 (counting / single-pair / disjoint-family, all coincide), construction verified, exhaustive cost-$\le 5$ enumeration |
| absolute interferometer, 2,197 states | 170,352 | **optimal 2** = $\{A,B\}$ | **certified exact**: same three certificates, on the translation-corrected pair set |

Nothing in the interferometer results is heuristic: no local-search
incumbent or positive certified gap remains, because in both systems
every separable pair is separated by each of the two length-1 words,
which forces the optimum to the trivial counting bound. The
branch-and-bound / ILP machinery contemplated for a harder instance
was unnecessary; the exhaustive set enumeration at cost $\le 5$ is a
complete exact decision procedure here (any cheaper panel has total
cost $\le 5$ and hence only words of length $\le 5$, all enumerated).
The genuinely load-bearing work at this scale turned out to be the
pair set itself: quotienting by the full verified symmetry group
(sign reversal in both systems, plus translation in the absolute
one). With a too-fine pair set the problem is infeasible for spurious
reasons (26,286 + 84 witnessless pairs), and any "optimal panel"
computed against it would have been meaningless.

Reproduction. `observatory_large.py lab` (gate; writes
`lab_check.json`), `observatory_large.py relative`
(`relative_results.json`, ~0.3 s), `observatory_absolute.py`
(`absolute_results.json`, ~750 s — the cost is the witness tally and
the repeated exhaustive enumerations over 170,352-bit masks, not the
automaton, which takes ~4 s). Cross-check logs:
`repo_crosscheck.log`, `repo_crosscheck_absolute.log`. All scripts
read the repository read-only and write only into this directory.

