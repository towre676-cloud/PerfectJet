# PerfectJet v0.20.0 installation

Download the current source archive from https://github.com/towre676-cloud/PerfectJet/archive/refs/heads/main.zip. To make the deterministic versioned package, run `python scripts/build_release.py`; it writes **PerfectJet-v0.20.0.zip** and its **.sha256** receipt under `releases/`. This source update does not itself publish a GitHub Release. This is the complete source distribution, including the graphical Math Lab, tests, mathematical documentation and retained research. It is not a standalone Windows EXE. Install Python 3.10 or newer first; the core needs no third-party packages.

On Windows, extract the ZIP, open the `PerfectJet` folder and double-click `Start_Math_Lab.bat`. If Windows does not recognize `python`, open PowerShell in that folder and run `py -3 run_observatory.py`. Keep the terminal open while using the Math Lab. Your browser opens the local interface at http://127.0.0.1:8765. If it does not open automatically, visit that address. Press Ctrl+C in the terminal to stop. If the port is busy, use `py -3 run_observatory.py --port 8766`.

On macOS or Linux, extract the ZIP, open a terminal in its `PerfectJet` folder and run `python3 run_observatory.py`. Open http://127.0.0.1:8765 if needed. The same `--port` option and Ctrl+C apply.

For an installed command-line package, run `python -m venv .venv`, then on Windows `.venv\Scripts\python -m pip install .` and `.venv\Scripts\perfectjet lab --open`. On macOS/Linux run `.venv/bin/python -m pip install .` and `.venv/bin/perfectjet lab --open`. This installs the core only. Optional historical numerical research uses `.[scouting]` and pinned dependencies; Python 3.12 is recommended for those extras.

To check the downloaded ZIP in PowerShell, run `Get-FileHash .\PerfectJet-v0.20.0.zip -Algorithm SHA256` and compare its hash with the first field in the `.sha256` file. On Linux run `sha256sum -c PerfectJet-v0.20.0.zip.sha256` from the download folder; on macOS use `shasum -a 256 -c PerfectJet-v0.20.0.zip.sha256`. A matching checksum establishes byte integrity relative to the published receipt, not an additional mathematical proof.

For the developer release replay, install setuptools and wheel, then run `python scripts/verify_release.py /path/to/PerfectJet-v0.20.0.zip` with the checksum beside the ZIP. It verifies archive hashes and equation identities, builds and installs a wheel in a temporary environment, computes all 29 tools, and launches the supplied interface to exercise all 29 tools over HTTP. This does not check desktop visual rendering. Full historical research tests additionally need the optional research dependencies.

The atlas includes definitions, rejected claims, historical statements and open problems as well as executable mathematics. Each computed tool reports its scope. Its examples are not universal solvers for every equation linked to the tool.
