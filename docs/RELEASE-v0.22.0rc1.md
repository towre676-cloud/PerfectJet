# PerfectJet v0.22.0rc1 — completed E8 cubic theorem release candidate

This prerelease packages the weight-seven, length-three E8 arc-kernel theorem
merged in PR #13 after v0.21.0:

K₇ = V₂₄₈ ⊕ V₃₈₇₅ ⊕ V₃₀₃₈₀ ⊕ V₁₄₇₂₅₀, dimension 181,753.

Every surviving cubic relation is a derivative of a lower-weight relation.
There is no new cubic primitive at weight seven. **Quartic, longer-length and
full weight-seven primitive classification remain open.**

The complete source ZIP includes the mathematical account, exact matrices,
independent fraction-free rank checker, lattice replay machinery and strict
source provenance. The installed wheel provides `python -m perfectjet.weight_seven`
and the mathematical JSON resources. This command checks source and certificate
bindings and reports retained evidence; it is not a fresh lattice calculation.

## Reproduction

Use Python 3.10+ for the dependency-free core, Python 3.12 and the pinned
`scouting` extras for the complete historical regression suite.

```sh
python scripts/build_release.py
python scripts/build_release.py
python scripts/check_release_source.py releases/PerfectJet-v0.22.0rc1.zip
python scripts/verify_release.py releases/PerfectJet-v0.22.0rc1.zip --e8-lattice
```

The verifier installs a wheel in a fresh environment outside the source tree,
checks all 30 Math Lab tools and both HTTP launchers, executes the installed E8
report and independent exact certificate checks, and optionally regenerates
lattice images and the full source null lift. All archived evidence hashes and
all 744 equation identities are checked. Linux and Windows publication checks
must produce identical source archives. The workflow retains logs, source commit
and SHA256SUMS; verification claims are limited to the recorded successful runs.

## Publication operation

Create the new tag `v0.22.0rc1` at the tested candidate commit, create a draft
GitHub Release with the source ZIP, checksum, manifest, source commit, installation
guide, these notes and platform/regression logs, download and verify the draft,
then set `draft=false, prerelease=true, latest=false`. Re-download and verify the
public assets. Existing tags and assets are never retargeted or replaced.

Version 0.22.0 is the next minor release because the installed theorem interface
is new; rc1 marks the requested candidate rather than claiming a final release.
Historical mathematical certificates and their source bindings are preserved.
The combined integration inventory is refreshed only for the changed installation
guide; its preceding bytes are retained in `releases/asterion-w7-integration-v021.json`.
The mathematical implementation and certificate payloads are unchanged.
