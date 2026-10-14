# PerfectJet 0.3.0

This release adds four executable kernels.

- **Hermite normal form** (`lattice.py`). `hermite_form` returns H=UB with U unimodular. `same_lattice` decides row-lattice equality by comparing Hermite forms. The tests check shape and reduction, invariance under random unimodular mixing, and agreement with mutual membership decided by integer solvability.
- **Multi-output word-Hankel realization** (`realization.py`). `realize(..., outputs=k)` stacks output coordinates into the Hankel columns and returns one shared state with a matrix-valued beta. A stacked rank can exceed every single-output rank, and a test shows this.
- **One-parameter rank loci** (`loci.py`). For a matrix over Q[t], `rank_locus` returns the generic rank over Q(t), the exact drop locus, and the rank on each locus factor. It never enumerates minors: one nonzero minor bounds the locus, and elimination over Q[t]/(squarefree minor) splits at zero divisors. The tests compare it with the gcd of all minors, with planted loci, and with direct evaluation. `partner_loci` applies it to the C3 sextic family. It rediscovers lambda=40/7 in degree 5, together with its mirror -40/7, and certifies that 0, +/-20 and +/-40/7 are the only rational exceptional parameters for degrees 3 to 12.
- **Adaptive local sieve** (`sieve.py`). The sieve keeps the residues n mod q for which F(n) is a d-th power residue mod q, combines them by CRT, and chooses moduli greedily by density drop per unit cost. It returns exclusion witnesses. The tests check soundness against brute-force hits, independence of test order, that a polynomial identity excludes nothing, and that density decreases strictly at each step.

The registry has 305 entries, and the adaptive-sieve row changed status to exact checked. Chapters 03, 04, 06, 15, 22, 23 and 24 were updated. The CLI has two new commands, `perfectjet loci` and `perfectjet sieve`, and the report includes both receipts. Local validation ran 65 unittest methods, all passing. No new Lean verification is claimed.

# PerfectJet 0.2.0

This release adds three exact kernels that 0.1.0 described as missing.

- `lattice.py` adds Smith normal form with explicit unimodular transforms, integer solvability of Bx=b, integer kernel bases, and the saturation index of a generated lattice. A failed integer system returns a certificate row y. When yB is integral and yb is not, the system fails over Z; when yB=0 and yb is nonzero, it already fails over Q. An unsaturated lattice returns an integral witness in its rational span that it does not generate.
- `realization.py` builds a minimal linear representation from a finite word-Hankel block. The model is exact on that block. Agreement on longer words is a held-out check, and a disagreement is returned as a witness word.
- `realization.py` also adds coarsest exact lumping. It discovers the aggregation R satisfying RA_c=Abar_c R and H=Hbar R for every cost matrix, starting from the output partition. Every valid lumping refines it.

The registry has 300 entries. The Smith form, integral solvability, and word-Hankel rows changed status to exact checked. Five entries were added: the infeasibility certificate, saturation index, integer kernel, Hankel realization, and coarsest lumping. Existing equation and topic IDs are unchanged. Chapters 04, 06, 22, and 23 describe the new kernels. Chapter 24 gives written proofs for the Smith form, the integer certificates, the Hankel construction, and coarsest-lumping uniqueness. The CLI has two new commands, `perfectjet lattice` and `perfectjet realization`, and the report includes both receipts.

Local validation ran 49 unittest methods, 34 retained and 15 new. Each new kernel is compared with an independent route:

- invariant factors against gcds of all k-by-k minors;
- integer infeasibility against exhaustive box search, with the certificate checked separately;
- integer kernel bases against brute-force kernel vectors;
- saturation index against maximal-minor gcds;
- recovered Hankel dimension against generic random representations of dimensions 1 to 3, a redundant three-state model, and an independent sequence Hankel rank;
- coarsest lumping against enumeration of every set partition of up to five states.

These are exact finite checks and written arguments. No new Lean verification is claimed. Hermite form, multi-output or numerical Hankel discovery, and the formal frontiers listed in chapter 23 remain open.

The v0.2.0 ZIP and its manifest are rebuilt by `scripts/build_release.py`, which now reads the version from the package. The v0.1.0 ZIP is retained unchanged. GitHub Actions status must be read from GitHub.

# PerfectJet 0.1.0 (retained)

The first master release preserves the categorized historical audit, both equation/archival passes, and both enhancement programs. It contains a25-chapter monograph,295equation entries,416topic entries, eight archived source extracts, a dependency-free Python library, examples, and reproducible exact receipts.

Local validation:34unittest methods passed, including exhaustive small selection populations and rank/unrank/tie comparisons; rational feature closure; partial-machine behavior; hidden-target witnesses; corrected energy source signs; finite-jet rejection; exact transvectant families and active dimensions; cyclotomic coefficients/convolution/recurrence; cubic-ring inverses and coefficient identities. The corrected PSG root is floating numerical evidence. Counts of methods are not counts of all looped cases.

Written mathematical arguments accompany the kernels. No new Lean verification is claimed. Original archives can contain stronger unsupported claims and remain separated from corrected canonical content. External numerical reports,large upstream data,chemical models,BLAST adapters,scouting/betting claims,and live applications are documented with boundaries rather than advertised as reproduced implementations.

The ZIP includes all eligible repository files and a manifest with per-file hashes. It excludes git internals,caches,and prior ZIPs. GitHub Actions status must be read from GitHub; local success does not assert a remote run passed. The original PerfectJet repository was empty and the release is published to main.
