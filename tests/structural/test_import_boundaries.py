"""Import boundaries are a layer contract, enforced by reading the AST.

Two assertions, per PHASE-0-DECISIONS E5 and ruling 1:

  (a) no module imports outside its layer's allowance
  (b) every top-level package under avise/ is classified into exactly one layer

Requirement (b) is the one that keeps this honest. Without it, a package added in
a later phase is silently unchecked; with it, adding one forces a deliberate
decision about where it sits.

"processing" is a layer name, not a directory. The processing packages live flat
under avise/.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import avise

AVISE_ROOT = Path(avise.__file__).resolve().parent

#: layer -> the layers it may import from. A layer may always import itself.
LAYERS: dict[str, set[str]] = {
    "domain": set(),
    "core": {"domain"},
    "db": {"domain", "core"},
    "processing": {"domain", "core", "db"},
    "worker": {"domain", "core", "db", "processing"},
    "api": {"domain", "core", "db", "processing"},
}

#: The packages that make up the processing layer.
PROCESSING = {
    "ingest",
    "extract",
    "identity",
    "graph",
    "patterns",
    "query",
    "report",
    "storage",
}


def layer_of(package: str) -> str | None:
    """The layer a top-level avise package belongs to, or None if unclassified."""
    if package in PROCESSING:
        return "processing"
    if package in LAYERS:
        return package
    return None


def top_level_packages() -> set[str]:
    return {
        path.name
        for path in AVISE_ROOT.iterdir()
        if path.is_dir() and (path / "__init__.py").exists() and path.name != "__pycache__"
    }


def module_files() -> list[Path]:
    return sorted(AVISE_ROOT.rglob("*.py"))


def package_of(path: Path) -> str | None:
    """The top-level avise package a file belongs to; None for avise/__init__.py."""
    relative = path.relative_to(AVISE_ROOT)
    return relative.parts[0] if len(relative.parts) > 1 else None


def imported_avise_packages(path: Path) -> set[str]:
    """Every top-level avise package this file imports."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    packages: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[0] == "avise" and len(parts) > 1:
                    packages.add(parts[1])
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import, same package by definition
                continue
            if node.module:
                parts = node.module.split(".")
                if parts[0] == "avise" and len(parts) > 1:
                    packages.add(parts[1])
    return packages


def test_every_package_is_classified() -> None:
    """(b) An unclassified package fails the suite rather than going unchecked."""
    unclassified = {
        package for package in top_level_packages() if layer_of(package) is None
    }
    assert not unclassified, (
        f"unclassified package(s): {sorted(unclassified)}. Add each to LAYERS or to "
        "PROCESSING in this test, and to the layer rule in CLAUDE.md, deliberately."
    )


def test_layer_map_is_self_consistent() -> None:
    known = set(LAYERS) | {"processing"}
    for layer, allowed in LAYERS.items():
        unknown = allowed - known
        assert not unknown, f"layer {layer} allows unknown layer(s) {sorted(unknown)}"
    assert not (PROCESSING & set(LAYERS)), "a package cannot be both a layer and processing"


@pytest.mark.parametrize("path", module_files(), ids=lambda p: str(p.name))
def test_module_imports_stay_within_its_layer(path: Path) -> None:
    """(a) No module imports outside its layer's allowance."""
    package = package_of(path)
    if package is None:
        return  # avise/__init__.py itself
    layer = layer_of(package)
    assert layer is not None, f"{package} is unclassified"
    allowed = LAYERS[layer]

    for imported in imported_avise_packages(path):
        if imported == package:
            continue  # a package may import itself
        imported_layer = layer_of(imported)
        assert imported_layer is not None, (
            f"{path.name} imports unclassified package avise.{imported}"
        )
        assert imported_layer in allowed, (
            f"avise/{package}/{path.name} ({layer}) imports avise.{imported} "
            f"({imported_layer}), which {layer} may not import. Allowed: "
            f"{sorted(allowed) or 'nothing internal'}."
        )


def test_nothing_imports_api() -> None:
    """The api layer is a leaf. Only api may import api."""
    offenders = [
        str(path.relative_to(AVISE_ROOT))
        for path in module_files()
        if package_of(path) not in (None, "api") and "api" in imported_avise_packages(path)
    ]
    assert not offenders, f"these modules import avise.api: {offenders}"


def test_processing_packages_do_not_import_each_other() -> None:
    offenders: list[str] = []
    for path in module_files():
        package = package_of(path)
        if package not in PROCESSING:
            continue
        for imported in imported_avise_packages(path):
            if imported != package and imported in PROCESSING:
                offenders.append(f"avise/{package}/{path.name} -> avise.{imported}")
    assert not offenders, f"processing packages may not import each other: {offenders}"
