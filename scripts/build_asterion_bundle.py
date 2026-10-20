"""Create the focused, runnable mathematics package with all exact receipts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = re.search(r'__version__ = "([^"]+)"', (ROOT / "src/perfectjet/__init__.py").read_text()).group(1)

README = """# Asterion research source

This focused package contains the exact Python engines, unit tests, equation
registry, Asterion monographs, complete research programme and source-bound
numerical certificates. Python 3.10 or newer is sufficient; no third-party
runtime package is required. The full PerfectJet repository remains at
https://github.com/towre676-cloud/PerfectJet.

Open a terminal in this extracted folder and run `python run_asterion.py
currents --max-degree 12`, `python run_asterion.py periods`, or `python
run_asterion.py discoveries`. The complete declared replay is `python
run_asterion.py extension --exhaustive --max-degree 30 --output new-run.json`.
It includes the full 14,441-row affine null test and the literal Jacobi rank
certificates, so allow several minutes. The result records exactly what was
checked and which higher-weight or global questions remain open.

The next mathematical push is `python run_asterion.py frontiers --exhaustive
--max-degree 4 --output frontier-run.json`. It independently replays the
higher-weight kernel, classical elliptic compatibility, specialized level-four
monodromy group closure and rank-eight Jacobi charge/moment certificates.

Read docs/ASTERION_FRONTIERS.md first, then docs/ASTERION_EXTENSION.md for the
earlier foundation. The new work preserves every earlier research gate and
states the remaining all-weight kernel and quantum elliptic boundaries.
The mathematical modules retain historical attribution. New-to-program
results do not assert worldwide priority or an infinite-kernel classification.

The inner BUNDLE_MANIFEST.json binds every included byte. The adjacent outer
SHA-256 file binds the ZIP. The complete earlier PerfectJet source remains
available through the repository; this package omits unrelated research data.
"""

RUNNER = """from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from perfectjet.asterion import main
if __name__ == '__main__':
    raise SystemExit(main())
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT.parent / f"Asterion-v{VERSION}-research.zip")
    args = parser.parse_args()
    selected = set()
    for folder in (ROOT / "src/perfectjet", ROOT / "data", ROOT / "results/asterion", ROOT / "results/asterion-extension", ROOT / "results/asterion-frontiers"):
        selected.update(p for p in folder.rglob("*") if p.is_file()
                        and "__pycache__" not in p.parts and p.suffix != ".pyc")
    for pattern in ("tests/test_asterion*.py", "docs/ASTERION*", "docs/asterion_*sources.json",
                    "docs/chapters/34_asterion_basis.md", "docs/chapters/35_asterion_extension.md", "docs/chapters/36_asterion_frontiers.md"):
        selected.update(p for p in ROOT.glob(pattern) if p.is_file())
    for name in ("pyproject.toml", "LICENSE", "LICENSE.md", "docs/MONOGRAPH.md", "docs/EQUATION_ATLAS.md",
                 "scripts/verify_asterion.py", "scripts/verify_asterion_extension.py", "scripts/verify_asterion_frontiers.py"):
        if (ROOT / name).is_file():
            selected.add(ROOT / name)
    contents = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in selected}
    contents.update({"README.md": README.encode(), "run_asterion.py": RUNNER.encode()})
    manifest = {"schema": "perfectjet/asterion-bundle/1", "version": VERSION,
                "files": {name: {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                          for name, raw in sorted(contents.items())}}
    contents["BUNDLE_MANIFEST.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, raw in sorted(contents.items()):
            info = zipfile.ZipInfo("Asterion/" + name, (2026, 10, 20, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, raw)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_suffix(args.output.suffix + ".sha256").write_text(digest + "  " + args.output.name + "\n")
    with zipfile.ZipFile(args.output) as archive:
        if archive.testzip() is not None:
            raise ArithmeticError("focused archive CRC validation failed")
        for name, metadata in manifest["files"].items():
            if hashlib.sha256(archive.read("Asterion/" + name)).hexdigest() != metadata["sha256"]:
                raise ArithmeticError(f"focused archive hash mismatch: {name}")
    print(json.dumps({"archive": str(args.output), "bytes": args.output.stat().st_size,
                      "files": len(contents), "sha256": digest}))


if __name__ == "__main__":
    main()
