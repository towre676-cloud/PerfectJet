# 38. P-521 provenance: source contracts and exact exclusions

The P-521 investigation concerns the historical construction of public curve parameters. Its strongest results are exact exclusions for declared generator models and sharp state-recovery theorems. The October follow-up adds authenticated-source execution and a recorded search for missing NTL revisions. **The published base-point origin remains unresolved.** No private key or discrete logarithm is recovered.

## The observation problem

The historical FreeLIP model fixes

\[
M=2^{107}-1,\qquad A=3^{121}\bmod M,
\qquad F(s)=As\bmod M.
\]

For a positive bound b, the recovered NTL 1.5 integer sampler advances F until its state is below \(T_b=M-(M\bmod b)\), then returns the low residue modulo b. The complete seed integer is reduced modulo M; zero residue is replaced by one. Its lazy default seed is 7157891. These are contracts read from a pinned historical distribution, not guessed from a modern generator.

The point-generation recipe includes more than this recurrence. Write

\[
H=(v,\mathrm{ABI},w,\mathrm{seed},F,\mathrm{emit},
\mathrm{reject},\mathrm{assemble},\mathrm{convert},\mathrm{select}).
\]

Here v identifies the source version; w is the limb width; the remaining maps retain seeding, output extraction, rejected states, integer assembly, field conversion and elliptic-curve candidate selection. Once these are specified, \(X_H(s),Y_H(s)\) denote the complete coordinate computation. An origin reconstruction requires a historically supported H and a witness s producing both complete published coordinates, together with every intervening rejection and sign decision. Finding a short matching bit window does not meet this requirement.

The archived 1.5 wrappers demonstrate why the contract must be explicit. Big-integer `RandomBnd` concatenates the first accepted radix output at the most significant end, adds an extra limb, and reduces modulo the requested bound. Big-integer `RandomLen` places the first output at the least significant end, masks the final limb and forces the highest requested bit. For a length L>1 it consumes \(\lceil L/w\rceil\) accepted words even when the final word is only partially retained. Scalar `RandomBnd(1)` consumes a draw; the big-integer overload with bound one consumes none. The same visible result can therefore leave different future streams.

The source-generated native configuration on the replay host has 64-bit longs, 53-bit doubles and w=50. The historical configuration formula also justifies w=30 on a 32-bit-long machine and the supported `SINGLE_MUL` option gives w=26. Radix emulation on a 64-bit host is useful for integer semantics but is not a native 32-bit ABI or a test of the original single-multiply path.

## What is proved over every state

For low-word observations \(y_i\), write emitting states as \(x_i=2^wu_i+y_i\). A declared raw-gap pattern gives linear congruences for u and an exact finite box. The retained lattice certificates supply an integer functional that takes values in \(D\mathbb Z\) on the affine lattice, while its minimum and maximum over the box contain no multiple of D. Exact arithmetic checks the contradiction and complete branch coverage. Lattice reduction discovers a witness; it is not trusted as the proof checker.

The initial standalone release covers all six specified 26-bit assemblies of the P-521 x coordinate with the original rejection sampler. The later portable receipt covers 92 declared profiles, including the recovered exact-length wrapper and additional historically supported widths, with 1,617 exact dual certificates. These existing results are retained unchanged. They establish

\[
\forall s\in D_H,\quad X_H(s)\ne G_x
\quad\Longrightarrow\quad
\nexists s\in D_H:\ (X_H(s),Y_H(s))=(G_x,G_y).
\]

Thus complete x-coordinate exclusion already excludes the full point under the same contract. It does not prove impossibility for all historical generators. A successor source inherits this conclusion only after its relevant semantics are shown to satisfy the certified model, including integer and field conversions.

The separate low26 observer results are also preserved. Five consecutive raw outputs determine the state; six accepted outputs determine the first emitting state with rejection included; explicit collisions prove five accepted outputs insufficient. The raw error-correction thresholds through nine observations belong to the fixed raw-time interface. They must not be applied to an unknown output slice, arbitrary interleaved draws or a successor RNG without a new proof.

## Authentic source replay

The follow-up executes the recovered NTL 1.5 C code through a new independent driver. The program checks the compressed archive size and SHA-256 before decompression and checks every selected source-member digest before compilation. The historical source is not vendored. Compiler flags, driver digest, generated machine description, numerical outputs and final internal states are retained in a numeric receipt.

The fixed replay comprises **867 C observations** across widths 26, 30 and 50. Width 50 uses the generated native configuration; the other widths are explicitly labeled radix emulations. Outputs and post-call states agree with the separately written model for all retained cases. Coverage includes full signed large seeds, normalization, lazy initialization, scalar-versus-big-integer draw consumption, limb-count boundaries, top-bit masking and forced rejection at the exact threshold. These are finite conformance checks, not a universal theorem about C execution.

The offline checker recomputes expected observations and requires every fixed case. It detects modified source pins, driver pins, configurations, missing cases, changed outputs and changed final states. It does not re-execute historical C. Supplying the authentic archive to the replay command performs that experiment again; original bytes, a compiler and gzip are required only for this optional source-execution path. The existing exact arithmetic certificates continue to verify without any of them.

## Missing revisions remain explicit

No authentic NTL 2.0 or 3.0-era source distribution was recovered in this bounded follow-up. The audit records 16 author/archive endpoint attempts, 22 author-focused search queries and 47 distribution/source-record endpoint attempts. Responses, failed access and guessed paths have separate labels; available response hashes and preserved commit references identify the inspected records. These counts describe executed searches, not exhaustive coverage of the Internet.

The checked author download list and package histories start too late. The author's changelog identifies distinct `RandomBits` fixes in 3.0e and 3.0f and a PRNG replacement in 3.5a. It does not specify those implementations. Consequently the pre-fix 3.0d, first-fix 3.0e, second-fix 3.0f and successor 3.1 streams remain separate unresolved source questions, as do actual 1.7/2.0 wrappers and the replacement's chronology. The August 1997 coefficient-seed timestamp does not date base-point selection and cannot by itself eliminate a later recipe.

The [detailed historical audit](https://github.com/towre676-cloud/PerfectJet/blob/main/research/p521_math/HISTORICAL_SEARCH.md) links the per-endpoint records, authenticated source pins, version boundary table and execution commands. The [research verifier](https://github.com/towre676-cloud/PerfectJet/blob/main/research/p521_math/verify_all.py) replays retained conformance and the prior mathematical certificates. The earlier published research release is preserved independently. The next admissible advance is authentic successor source or a historically supported complete-point reconstruction; neither is replaced by an inferred `RandomBits` routine.
