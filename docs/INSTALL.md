# PerfectJet v0.22.0rc1 installation

Download **PerfectJet-v0.22.0rc1.zip** and **PerfectJet-v0.22.0rc1.zip.sha256** from the [versioned release](https://github.com/towre676-cloud/PerfectJet/releases/tag/v0.22.0rc1). This complete source distribution includes the graphical Math Lab, 744 equation records, 27 families, 30 computed tools, tests, proofs and retained research. Install Python 3.10 or newer first; the core needs no third-party runtime packages. The ZIP runs through Python and includes Windows launchers.

The release also provides `SOURCE_COMMIT.txt`, the complete `MANIFEST.json`, release notes and verification logs. The tag and source receipt identify the same tested revision. Development `main.zip` is a moving source snapshot; use the versioned asset for a reproducible installation.

On Windows, extract the ZIP, open the `PerfectJet` folder and double-click `Start_Math_Lab.bat`. If Windows does not recognize `python`, open PowerShell in that folder and run `py -3 run_observatory.py`. Keep the terminal open while using the Math Lab. Your browser opens the local interface at http://127.0.0.1:8765. If it does not open automatically, visit that address. Press Ctrl+C in the terminal to stop. If the port is busy, use `py -3 run_observatory.py --port 8766`.

On macOS or Linux, extract the ZIP, open a terminal in its `PerfectJet` folder and run `python3 run_observatory.py`. Open http://127.0.0.1:8765 if needed. The same `--port` option and Ctrl+C apply.

For an installed command-line package, run `python -m venv .venv`, then on Windows `.venv\Scripts\python -m pip install .` and `.venv\Scripts\perfectjet lab --open`. On macOS/Linux run `.venv/bin/python -m pip install .` and `.venv/bin/perfectjet lab --open`. This installs the core only. Optional historical numerical research uses `.[scouting]` and pinned dependencies; Python 3.12 is recommended for those extras.

To check the downloaded ZIP in PowerShell, run `Get-FileHash .\PerfectJet-v0.22.0rc1.zip -Algorithm SHA256` and compare its hash with the first field in the `.sha256` file. On Linux run `sha256sum -c PerfectJet-v0.22.0rc1.zip.sha256` from the download folder; on macOS use `shasum -a 256 -c PerfectJet-v0.22.0rc1.zip.sha256`. A matching checksum establishes byte integrity relative to the published receipt, not an additional mathematical proof.

For the developer release replay, install setuptools and wheel, then run `python scripts/verify_release.py /path/to/PerfectJet-v0.22.0rc1.zip` with the checksum beside the ZIP. It verifies archive hashes and equation identities, builds and installs a wheel in a temporary environment, computes all 30 tools, and launches the supplied interface to exercise all 30 tools over HTTP. This does not check desktop visual rendering. Full historical research tests additionally need the optional research dependencies.

The atlas includes definitions, rejected claims, historical statements and open problems as well as executable mathematics. Each computed tool reports its scope. Its examples are not universal solvers for every equation linked to the tool.


To rebuild the source ZIP from the tagged checkout, run `python scripts/build_release.py` twice; the SHA-256 must remain identical. Keep developer logs outside the checkout while rebuilding. Historical checksums do not verify this release candidate.

After installing, replay the certified research example with:

```sh
python -m perfectjet collision-research approximate --x 1000000000000 --prime-cutoff 10000 --include-exact
```

For the pinned historical numerical research suite, create a separate Python 3.12 environment and run `python -m pip install '.[scouting]'` followed by `python -m unittest discover -s tests -v`. The optional dependency pins require a newer Python than the dependency-free core.

## Completed Asterion cubic theorem

After installing this release candidate, run this from any directory:

```sh
python -m perfectjet.weight_seven
```

This checks the installed source and certificate bindings and reports the complete
weight-seven **length-three** kernel, of dimension 181,753, with no new cubic
primitive. It reads retained replay evidence; it does not rerun the lattice
calculation. The source checkout includes
[the proof and full replay commands](ASTERION_WEIGHT_SEVEN_LENGTH_THREE.md).
The older `asterion primitives` and frontier reports retain their explicitly
bounded weight-five/six and selected-sector scopes. Weight-seven quartic,
longer-length and full primitive classification remain open.

This prerelease preserves the published v0.21.0 tag and assets. Quartic and
longer-length research is excluded from the completed-theorem claim.

The source ZIP includes the proof documentation, independent checker scripts
and exact rank matrices under `results/asterion-primitives/`. A wheel installs
the executable modules and JSON certificate resources; retain the source ZIP
for documentation and the independent full replay infrastructure.

Run `python scripts/verify_release.py /path/to/PerfectJet-v0.22.0rc1.zip`
to verify the isolated installed theorem and independent stored-matrix checks.
Add `--e8-lattice` to regenerate both completed-sector lattice images and the
original full source null lift using the installed package. The inherited seven
sectors have a separate full replay command in the theorem documentation.
