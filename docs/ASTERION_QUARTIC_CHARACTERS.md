# Exact quartic E8 characters

`asterion_quartic_characters.py` proves a3876-dimensional lower bound for
the kernel of finite multiplication

    mu:Sym²(W)->Sym⁴(g),  W=1+3875 inside Sym²(g).

Its connection to the weight-six, factor-length-four arc component uses
the separate dual-polarization identification in `asterion_quartic`.
Character multiplicities alone do not prove every multiplication block
has maximal rank, determine the complete quartic kernel, or prove any
particular class vanishes in the simple affine VOA.

The complete exact finite characters are:

| Space | E8 character | Dimension |
| --- | --- | ---: |
|Sym²(3875)|1+3875+27000+147250+2450240+4881384|7509750|
|Sym²(W)|2·1+2·3875+27000+147250+2450240+4881384|7513626|
|Sym⁴(g)|1+3875+2·27000+147250+2450240+4096000+4881384+70680000+79143000|161455750|

Both the trivial and3875 representations have source multiplicity two
and target multiplicity one. An equivariant map can have rank at most
one on either multiplicity space. Therefore ker(mu) contains at least
one copy of each, giving1+3875 and dimension3876. The3875 lower bound
and the explicit invariant line are independent components of this
same3876-dimensional bound; the invariant must not be counted twice.

The program derives these tables from the241 distinct adjoint weights,
with the zero weight of multiplicity eight. Their square has9361
distinct weights. Its norm-at-most-four support contains precisely one
zero weight,240 roots and2160 norm-four lattice vectors; the last count
equals the full E8 theta-series coefficient240·sigma3(2). Thus every
weight needed for3875 is present. The degree-two lattice-VOA formula
and V2=1+g+3875 give multiplicities35,7,1 on squared norms0,2,4.
These2401 distinct weights have total multiplicity3875.

The Newton identities give all symmetric-power weight multiplicities:

    Sym²(chi)=(chi²+psi2(chi))/2,
    Sym⁴(chi)=(chi⁴+6chi²psi2(chi)+3psi2(chi)²+8chi psi3(chi)+6psi4(chi))/24.

Here psi_r sends each weight to r times that weight. Every numerator,
integer weight multiplicity and exact dominant-weight subtraction is
recorded. The norm bounds16 for Sym²(W) and32 for Sym⁴(g) follow
from Cauchy-Schwarz, so the enumerated dominant weights exhaust all
possible highest weights. Weyl-chamber-folded Freudenthal recursion then
reconstructs the irreducibles and their Weyl dimensions. The three
dimension totals independently equal the elementary symmetric-power
dimensions. The frozen tower module is reused without editing its public
degree bound; the new module has a private fixed-norm32 specialization
for this finite four-factor calculation. No large tensor-product table
or unbounded user-supplied character request is imported.

`quartic_characters_receipt(exhaustive=False)` returns a JSON-safe object
with `passed`, the three complete character certificates, the forced
kernel character and dimension, and explicit false fields for stronger
claims that are not proved. Its default run takes about1.3 seconds. The
exhaustive mode additionally records every nontrivial Freudenthal
recursion step; it has the same mathematical scope.
`verify_quartic_character_certificate(record)` recomputes the character
calculation and detects coefficient or dimension changes, independently
of any stored `passed` field. Boolean multiplicities, duplicate highest
weights, malformed labels and non-Boolean flags are rejected.

Run the focused verification with:

```sh
PYTHONPATH=src python -m unittest discover -s tests -p test_asterion_quartic_characters.py -v
```

Classical inputs and algorithm provenance are documented in
[ASTERION_KERNEL_TOWER.md](ASTERION_KERNEL_TOWER.md). The quartic
character deductions here are exact finite calculations. Their global
novelty is unverified; no infinite arc-kernel presentation is claimed.
