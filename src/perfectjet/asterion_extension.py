"""Executable Asterion extension programme and bounded exact replay.

The components expose their mathematical scope independently.  A successful
report means that the stated certificates replay; it does not close every
research question or establish worldwide priority for a result.
"""
from __future__ import annotations

import hashlib
from importlib import resources
import json
from pathlib import Path


COMPONENTS = ("boundary", "currents", "kz", "relations", "higher", "rigidity", "periods")


def _degree(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 80:
        raise ValueError("max_degree must be an integer in 0..80")
    return value


def component_report(component, *, exhaustive=False, max_degree=12):
    """Run one explicitly bounded component, preserving exact coefficients."""
    if component not in COMPONENTS:
        raise ValueError("unknown Asterion extension component")
    if not isinstance(exhaustive, bool):
        raise ValueError("exhaustive must be a Boolean")
    max_degree = _degree(max_degree)
    if component == "boundary":
        from .asterion_boundary import boundary_receipt
        result = boundary_receipt(exhaustive=exhaustive)
    elif component == "currents":
        from .asterion_currents import currents_receipt
        result = currents_receipt(max_degree=max_degree)
    elif component == "kz":
        from .asterion_kz import kz_receipt
        result = kz_receipt(exhaustive=exhaustive)
    elif component == "relations":
        from .asterion_relations import relations_receipt
        result = relations_receipt(exhaustive=exhaustive)
    elif component == "higher":
        from .asterion_higher import higher_receipt
        result = higher_receipt(exhaustive=exhaustive)
    elif component == "rigidity":
        from .asterion_rigidity import rigidity_receipt
        result = rigidity_receipt(exhaustive=exhaustive)
    else:
        from .asterion_periods import periods_receipt
        result = periods_receipt()
    from .asterion import json_ready
    return json_ready(result)


def research_ledger():
    """Read the installed discovery ledger without relying on a git checkout."""
    path = resources.files("perfectjet").joinpath("resources/asterion_discoveries.json")
    if not path.is_file():
        raise FileNotFoundError("the Asterion discovery ledger is missing from this installation")
    return json.loads(path.read_text(encoding="utf-8"))


def extension_report(*, exhaustive=False, max_degree=12):
    """Replay all implemented extensions, reporting unresolved questions too."""
    if not isinstance(exhaustive, bool):
        raise ValueError("exhaustive must be a Boolean")
    max_degree = _degree(max_degree)
    reports = {}
    for name in COMPONENTS:
        component = component_report(name, exhaustive=exhaustive, max_degree=max_degree)
        if component.get("passed") is not True:
            raise ArithmeticError(f"Asterion component failed its declared replay: {name}")
        reports[name] = component
    from .asterion import source_digests
    return {
        "schema": "perfectjet/asterion-extension/1",
        "name": "Asterion extension",
        "source_sha256": source_digests(),
        "exhaustive_requested": exhaustive,
        "max_degree": max_degree,
        "components": reports,
        "passed": all(row.get("passed") is True for row in reports.values()),
        "scope": "Exact certificates and declared finite computations; open research gates remain open.",
        "priority": "Implementation and derived consequences are identified separately from historical priority.",
    }


def file_manifest(folder):
    """Bind a collection of certificate bytes without trusting embedded flags."""
    folder = Path(folder)
    return {p.name: {"bytes": p.stat().st_size,
                     "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in sorted(folder.iterdir()) if p.is_file() and p.name != "manifest.json"}
