# A sharp observer for the actual FreeLIP rejection interface

**Six consecutive accepted low-26-bit outputs uniquely determine the first
emitting state. Five do not.** This is an exact, all-state statement for the
specified recurrence and rejection loop. The retained proof covers different
rejection patterns as well as matching patterns, with every source rejection
guard enforced. A constructive decoder is included.

The recurrence is

\[
M=2^{107}-1,\qquad A=3^{121}\bmod M,\qquad B=2^{26},\qquad
F(x)=Ax\bmod M.
\]

The source first advances the state, repeats while the state is at least
\(T=M-(M\bmod B)=M-(B-1)\), and returns its residue modulo \(B\). This
note observes an accepted emitting state itself, then its successive accepted
returns. Its target is that first emitting state. In the notation below
\(S=\{0,\ldots,T-1\}\), including the fixed state zero.

The executable proof is [accepted_observer.py](accepted_observer.py), the
retained integer receipt is
[results/accepted-observer.json](results/accepted-observer.json), and the
regressions are [tests/test_accepted_observer.py](tests/test_accepted_observer.py).
All verification and decoding use the Python standard library. Lattice
reduction is used only to discover the retained bases.

## The sharpness witness

These two different first emitting states have the same first five accepted
outputs:

| Quantity | First trajectory | Second trajectory |
|---|---:|---:|
| First emitting state | 126295752713511514371453877552714 | 81692446156502146450273842038346 |
| First five outputs | 53806666, 63148225, 39235656, 43695102, 27978396 | 53806666, 63148225, 39235656, 43695102, 27978396 |
| Raw gaps between those outputs | 1, 1, 1, 2 | 1, 1, 1, 1 |
| Sixth output | 37823841 | 63084375 |

The first trajectory's skipped raw state is exactly \(M-32041695\). It is in
the source rejection interval. Thus this is a real accepted-output collision,
with a forced rejection, rather than a collision obtained by allowing arbitrary
missing raw draws. It also explains why the sharp five-output theorem for the
unwrapped raw recurrence cannot simply be reused for this interface.

## Why only raw gaps one and two occur

Suppose two rejected states were consecutive. Write them as \(M-u\) and
\(M-v\), where \(1\leq u,v\leq B-1\). Then \(v\equiv Au\pmod M\).
The fixed integers

\[
q_0=9944586160332543,\qquad q_1=21699637613853658
\]

satisfy \(q_0+Aq_1\equiv0\pmod M\). Therefore \(q_0u+q_1v\) is a multiple
of \(M\), but exact arithmetic verifies

\[
0<q_0+q_1\leq q_0u+q_1v\leq(B-1)(q_0+q_1)<M.
\]

This contradiction proves that a source call skips at most one raw state. Each
six-output trace consequently has one of the 32 gap words in \(\{1,2\}^5\).

## The complete six-output proof

Let \(U=\lfloor(M-1)/B\rfloor\). If two emitting states have equal outputs
at a position, their state difference is \(Bz_i\) with \(|z_i|\leq U\).

For **matching gap words**, let \(e_0=0,e_1,\ldots,e_5\) be cumulative raw
times. The difference vector \(z\) lies in the six-dimensional integer lattice

\[
z_i\equiv A^{e_i}z_0\pmod M.
\]

Its standard basis has first row \((1,A^{e_1},\ldots,A^{e_5})\) and modulus
rows on the other coordinates; its determinant has magnitude \(M^5\). For each
of the 32 patterns, the receipt gives an integer basis \(R\). The verifier
checks every row's congruences and \(|\det R|=M^5\), establishing equality
with the full stated lattice. With row-vector convention \(z=cR\), the exact
inverse gives

\[
|c_j|\leq U\sum_i |(R^{-1})_{ij}|<1.
\]

All integer coefficients are zero. Hence the states are equal. The largest
retained coefficient bound across all these certificates is exactly

\[
\frac{2659994645194790114589299127948}
     {162259276829213363391578010288127}<0.017.
\]

For **different gap words**, at least one trajectory has a rejection. Orient
that trajectory to the left. There are \(31\cdot31=961\) oriented pairs to
check: the left word has a two, and the right word is any different word.
Pairs with rejections on both sides may be checked twice; a pair whose only
rejection is on the right is covered after swapping sides.

Anchor the left path at its first rejected raw state, \(M-u\), with
\(1\leq u\leq B-1\). If that rejection is at raw time \(j\), and the two
cumulative observation schedules are \(e_i\) and \(f_i\), put

\[
\alpha_i=-A^{e_i-j}\bmod M,\qquad \beta_i=A^{f_i}\bmod M.
\]

Negative exponents use the modular inverse, which exists. The left and right
emitting states at position \(i\) are respectively
\(s_i=\alpha_i u\bmod M\) and \(t_i=\beta_i t_0\bmod M\). Equal outputs
require \(s_i-t_i=Bz_i\). Eliminating \(t_0\) gives

\[
z_i\equiv\beta_i z_0+c_i u\pmod M,\qquad
c_i=(\alpha_i-\beta_i\alpha_0)B^{-1}\bmod M.
\]

Scale the rejection-distance coordinate by \(K=2^{55}\). A necessary
collision vector \((Ku,z_0,\ldots,z_5)\) lies in a seven-dimensional lattice
with generators

\[
(K,0,c_1,\ldots,c_5),\quad
(0,1,\beta_1,\ldots,\beta_5),\quad
Me_2,\ldots,Me_6,
\]

and lies in the box

\[
K\leq Ku\leq K(B-1),\qquad -U\leq z_i\leq U.
\]

The determinant is \(KM^5\). For every retained reduced basis the verifier
checks integer entries, divisibility of its first coordinate by \(K\), all
congruences, and determinant magnitude \(KM^5\). These checks certify the
complete lattice; no assumption about reduction quality is used.

For a box vector \(v=cR\), every coefficient is in the exact rational interval
obtained by minimizing and maximizing \(vR^{-1}\) over the coordinate box.
The verifier enumerates every integer tuple in those intervals, retains the
vectors actually in the box, and reconstructs

\[
s_0=\alpha_0u\bmod M,\qquad t_0=(s_0-Bz_0)\bmod M.
\]

It then executes the complete source return map on both states. Both first
states must be accepted and different; every emitting state must be accepted;
each skipped state must meet the actual rejection predicate; the two gap words
must be exactly the declared words; and all six outputs must match. This final
step is necessary because the congruence box is a relaxation.

Across all 961 pairs, the exact coefficient boxes contain only **1,556 integer
tuples**, with at most 15 for any pair. Of these, **304 vectors** lie in the
coordinate boxes. **Zero** give a valid collision after the source guards.
Together with the 32 same-pattern certificates, this exhausts every possible
pair of six-output trajectories. The five-output witness proves optimality.

## Constructive recovery

For each possible gap word, write an emitting state as \(y_i+Bh_i\), where
\(y_i\) is the observed output and
\(0\leq h_i\leq\lfloor(T-1-y_i)/B\rfloor\). The high parts lie in an affine
translate of the same-pattern lattice above. Its certified inverse bounds
allow at most one coefficient tuple for that word. Reconstruct it, then check
the true accepted trace. Six-output uniqueness ensures at most one candidate
over all 32 words.

```python
from research.p521_math.accepted_observer import recover_accepted

state = recover_accepted([53806666, 63148225, 39235656,
                          43695102, 27978396, 37823841])
assert state == 126295752713511514371453877552714
```

`recover_accepted` accepts six or more outputs and returns `None` for an
impossible sequence. Extra outputs are replayed in full. This decoder promises
exact observations; unknown symbol errors and erasures require further work.

## The state before the first call is a different target

Let \(H\) map a raw pre-call state to the next accepted emitting state. For
every rejected raw state \(r\), the two different inputs \(r\) and
\(F^{-1}r\) have the same image \(F(r)\). They produce identical future
accepted streams, regardless of how many outputs are supplied.

More precisely, for each \(e\in S\), one preimage is always \(F^{-1}e\).
A second preimage \(F^{-2}e\) exists exactly when \(F^{-1}e\) is rejected.
The no-consecutive-rejections lemma rules out any other preimages. Thus \(H\)
has exactly

\[
B-1=67108863\text{ double fibres},\qquad
M-2(B-1)=162259276829213363391577876070401\text{ singleton fibres}.
\]

The accepted return map itself is a bijection on \(S\). Its inverse at \(e\)
is \(F^{-1}e\) if that state is accepted, and \(F^{-2}e\) otherwise.
Consequently the coalescence is entirely in the pre-call-to-first-emission
map. Combined with the six-output theorem, the displayed fibres are exactly
the observational equivalence classes of raw pre-call states for infinite
accepted streams.

## Reproduction and scope

From the repository root:

```sh
python research/p521_math/accepted_observer.py --verify
python -m unittest research.p521_math.tests.test_accepted_observer -v
```

To rediscover all bases and rewrite the receipt:

```sh
python research/p521_math/accepted_observer.py
```

Discovery uses `fpylll` when installed, with the existing exact rational LLL
fallback otherwise. The receipt verifier and decoder do not require it.
An independent checker is described in [ACCEPTED_AUDIT.md](ACCEPTED_AUDIT.md).

The mathematical tools are classical truncated-congruential lattice methods
and exact integer enumeration, specialized here to this generator's actual
rejection return map. Worldwide priority has not been established. This theorem
does not identify the historical P-521 generation recipe, establish a seed for
P-521, recover a private key, or weaken the elliptic-curve discrete logarithm
problem. It establishes a sharp observability fact about a precisely specified
candidate generator interface.
