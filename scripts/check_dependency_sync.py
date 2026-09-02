#!/usr/bin/env python3
"""Verify that every dependency manifest and lockfile in the repo agrees.

Recompiling ``backend/requirements.lock`` and diffing it byte-for-byte is not a
usable CI gate: unpinned transitive dependencies resolve to whatever was
published most recently, so the check fails on days nobody touched the
manifests. This script instead asserts the properties that actually matter and
are deterministic:

1. The root ``pyproject.toml`` and ``backend/pyproject.toml`` declare exactly the
   same runtime and dev dependencies (one dependency story, two entry points).
2. Every direct dependency declared in ``pyproject.toml`` is present in
   ``backend/requirements.lock`` at exactly the declared version.
3. ``backend/requirements-runtime.txt`` and ``backend/requirements-dev.txt``
   match the corresponding ``pyproject.toml`` sections.
4. ``frontend/package-lock.json`` covers every dependency range declared in
   ``frontend/package.json`` and declares the same package name/lockfile
   version.

Run it directly, via ``make deps-check``, or as part of ``make ci-local``.
Exits non-zero with an actionable message on the first inconsistency.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    print("Python 3.11+ is required to run the dependency sync check.", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent.parent
REQUIREMENT_RE = re.compile(r"^\s*([A-Za-z0-9._-]+)\s*(\[[^\]]+\])?\s*==\s*([^\s;#]+)")
errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def canonical(name: str) -> str:
    """PEP 503 normalised distribution name."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_requirements(lines: list[str]) -> dict[str, str]:
    """Map canonical name -> pinned version for ``name==version`` lines."""
    pinned: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "-")):
            continue
        match = REQUIREMENT_RE.match(stripped)
        if match:
            pinned[canonical(match.group(1))] = match.group(3)
    return pinned


def load_pyproject(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def check_python_manifests() -> None:
    root_project = load_pyproject(ROOT / "pyproject.toml")["project"]
    backend_project = load_pyproject(ROOT / "backend" / "pyproject.toml")["project"]

    root_runtime = parse_requirements(root_project["dependencies"])
    backend_runtime = parse_requirements(backend_project["dependencies"])
    if root_runtime != backend_runtime:
        only_root = sorted(set(root_runtime.items()) - set(backend_runtime.items()))
        only_backend = sorted(set(backend_runtime.items()) - set(root_runtime.items()))
        error(
            "pyproject.toml and backend/pyproject.toml declare different runtime "
            f"dependencies.\n  only in root:    {only_root}\n  only in backend: {only_backend}"
        )

    if not root_runtime:
        error("pyproject.toml declares no runtime dependencies; scanners need them pinned here.")

    root_dev = parse_requirements(root_project.get("optional-dependencies", {}).get("dev", []))
    backend_dev = parse_requirements(
        backend_project.get("optional-dependencies", {}).get("dev", [])
    )
    missing_dev = sorted(set(backend_dev) - set(root_dev))
    if missing_dev:
        error(
            "backend/pyproject.toml dev extras missing from the root pyproject.toml: "
            f"{missing_dev}"
        )
    for name, version in backend_dev.items():
        if name in root_dev and root_dev[name] != version:
            error(
                f"dev dependency '{name}' is pinned to {version} in backend/pyproject.toml "
                f"but {root_dev[name]} in pyproject.toml"
            )

    lock_path = ROOT / "backend" / "requirements.lock"
    locked = parse_requirements(lock_path.read_text().splitlines())
    if not locked:
        error("backend/requirements.lock contains no pinned requirements.")

    for label, declared in (("runtime", root_runtime), ("dev", root_dev)):
        for name, version in sorted(declared.items()):
            if name not in locked:
                error(
                    f"{label} dependency '{name}=={version}' is declared in pyproject.toml but "
                    "absent from backend/requirements.lock.\n  Regenerate with: uv pip compile "
                    "pyproject.toml --extra dev --output-file backend/requirements.lock"
                )
            elif locked[name] != version:
                error(
                    f"{label} dependency '{name}' is pinned to {version} in pyproject.toml but "
                    f"{locked[name]} in backend/requirements.lock.\n  Regenerate with: uv pip "
                    "compile pyproject.toml --extra dev --output-file backend/requirements.lock"
                )

    runtime_txt = parse_requirements(
        (ROOT / "backend" / "requirements-runtime.txt").read_text().splitlines()
    )
    if runtime_txt != root_runtime:
        missing = sorted(set(root_runtime.items()) - set(runtime_txt.items()))
        extra = sorted(set(runtime_txt.items()) - set(root_runtime.items()))
        error(
            "backend/requirements-runtime.txt does not match the pyproject.toml runtime "
            f"dependencies.\n  missing/mismatched: {missing}\n  unexpected: {extra}"
        )

    dev_txt = parse_requirements(
        (ROOT / "backend" / "requirements-dev.txt").read_text().splitlines()
    )
    for name, version in sorted(root_dev.items()):
        if dev_txt.get(name) not in (None, version):
            error(
                f"dev dependency '{name}' is pinned to {version} in pyproject.toml but "
                f"{dev_txt[name]} in backend/requirements-dev.txt"
            )


def check_node_manifests() -> None:
    package = json.loads((ROOT / "frontend" / "package.json").read_text())
    lock = json.loads((ROOT / "frontend" / "package-lock.json").read_text())

    if lock.get("name") != package.get("name"):
        error(
            f"frontend/package-lock.json name '{lock.get('name')}' does not match "
            f"package.json name '{package.get('name')}'"
        )
    if lock.get("version") != package.get("version"):
        error(
            f"frontend/package-lock.json version '{lock.get('version')}' does not match "
            f"package.json version '{package.get('version')}'"
        )
    if lock.get("lockfileVersion", 0) < 2:
        error("frontend/package-lock.json must use lockfileVersion 2 or newer for `npm ci`.")

    root_entry = lock.get("packages", {}).get("", {})
    for section in ("dependencies", "devDependencies"):
        declared = package.get(section, {})
        locked_declared = root_entry.get(section, {})
        if declared != locked_declared:
            differing = sorted(
                name
                for name in set(declared) | set(locked_declared)
                if declared.get(name) != locked_declared.get(name)
            )
            error(
                f"frontend/package-lock.json {section} do not match package.json for: "
                f"{differing}\n  Regenerate with: cd frontend && npm install "
                "--package-lock-only"
            )
        for name in declared:
            if f"node_modules/{name}" not in lock.get("packages", {}):
                error(
                    f"'{name}' is declared in package.json {section} but has no resolved entry "
                    "in package-lock.json.\n  Regenerate with: cd frontend && npm install"
                )


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Verify that dependency manifests and lockfiles agree.")
    parser.add_argument("--fix", action="store_true", help="Automatically synchronize manifests and lockfiles.")
    args = parser.parse_args()

    if args.fix:
        if str(ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(ROOT / "scripts"))
        from sync_dependencies import sync_python_manifests, recompile_lockfiles, sync_node_manifests
        sync_python_manifests()
        recompile_lockfiles()
        sync_node_manifests()
        errors.clear()

    check_python_manifests()
    check_node_manifests()

    if errors:
        print("Dependency manifests are out of sync:\n", file=sys.stderr)
        for item in errors:
            print(f"  - {item}", file=sys.stderr)
        print("\nFix automatically with: make deps-sync (or python scripts/sync_dependencies.py)", file=sys.stderr)
        return 1

    print("Dependency manifests and lockfiles are consistent:")
    print("  pyproject.toml <-> backend/pyproject.toml <-> backend/requirements.lock")
    print("  backend/requirements-runtime.txt, backend/requirements-dev.txt")
    print("  frontend/package.json <-> frontend/package-lock.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
