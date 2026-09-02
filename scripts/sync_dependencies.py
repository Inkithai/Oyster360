#!/usr/bin/env python3
"""Synchronize dependency manifests and lockfiles across the Oyster360 repo.

This script keeps all Python manifests and lockfiles consistent:
  - pyproject.toml (root PEP 621 manifest)
  - backend/pyproject.toml
  - setup.cfg
  - backend/setup.cfg
  - backend/requirements-runtime.txt
  - backend/requirements-dev.txt
  - backend/requirements.lock (via `uv pip compile`)
  - uv.lock (via `uv lock`)
  - backend/uv.lock (via `cd backend && uv lock`)
  - frontend/package-lock.json (via `npm install --package-lock-only` if needed)

When dependency versions differ across manifests (e.g. after Dependabot bumps a
package in root pyproject.toml or backend/pyproject.toml), this script resolves
the conflict by adopting the updated/higher version, updating all manifests,
and recompiling the lockfiles.

Usage:
  python scripts/sync_dependencies.py [--no-compile] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    print("Python 3.11+ is required to run the dependency synchronizer.", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent.parent
SPEC_RE = re.compile(r"^\s*([A-Za-z0-9._-]+(?:\[[^\]]+\])?)\s*([<>=~!^].*)?$")


def canonical(name: str) -> str:
    """PEP 503 normalised distribution name."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_dep(dep_str: str) -> tuple[str, str, str, str]:
    """Parse a requirement string into (canonical_base, raw_name, operator, version)."""
    dep_str = dep_str.strip()
    match = SPEC_RE.match(dep_str)
    if not match:
        return (canonical(dep_str), dep_str, "", "")
    raw_name = match.group(1)
    base_name = canonical(re.sub(r"\[.*\]", "", raw_name))
    spec = (match.group(2) or "").strip()
    op_match = re.match(r"^([<>=~!^]+)\s*(.*)$", spec)
    if op_match:
        return (base_name, raw_name, op_match.group(1), op_match.group(2).strip())
    return (base_name, raw_name, "", "")


def parse_version(v: str) -> tuple:
    """Parse a version string for comparison (supports PEP 440 basic & pre-release formats)."""
    v = re.sub(r"^[<>=~!^ ]+", "", v).strip()
    match = re.match(r"^(\d+(?:\.\d+)*)(?:[-._]?(a|b|rc|alpha|beta|dev|post|preview)(\d*))?", v)
    if not match:
        return (v,)
    base_nums = tuple(int(x) for x in match.group(1).split("."))
    tag = match.group(2)
    tag_num = int(match.group(3)) if match.group(3) else 0
    if not tag:
        return base_nums + (0,)  # final release
    if tag == "post":
        return base_nums + (1, tag_num)
    return base_nums + (-1, tag, tag_num)  # pre-release


def load_pyproject(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def merge_dependency_lists(*dep_lists: list[str]) -> list[str]:
    """Merge lists of dependency strings, picking the highest / most specific version."""
    merged: dict[str, tuple[str, str, str]] = {}
    order: list[str] = []

    for d_list in dep_lists:
        for dep in d_list:
            stripped = dep.strip()
            if not stripped or stripped.startswith(("#", "-")):
                continue
            canon, raw_name, op, ver = parse_dep(stripped)
            if canon not in merged:
                merged[canon] = (raw_name, op, ver)
                order.append(canon)
            else:
                curr_raw, curr_op, curr_ver = merged[canon]
                chosen_raw = raw_name if "[" in raw_name else curr_raw
                chosen_op = op or curr_op
                chosen_ver = curr_ver
                if ver and curr_ver:
                    if parse_version(ver) > parse_version(curr_ver):
                        chosen_ver = ver
                        chosen_op = op or curr_op
                        chosen_raw = raw_name
                elif ver and not curr_ver:
                    chosen_ver = ver
                    chosen_op = op or curr_op
                    chosen_raw = raw_name

                merged[canon] = (chosen_raw, chosen_op, chosen_ver)

    result = []
    for canon in order:
        raw_name, op, ver = merged[canon]
        if op and ver:
            result.append(f"{raw_name}{op}{ver}")
        elif ver:
            result.append(f"{raw_name}=={ver}")
        else:
            result.append(raw_name)
    return result


def format_toml_array(name: str, items: list[str], indent: str = "    ") -> str:
    lines = [f"{name} = ["]
    for item in items:
        lines.append(f'{indent}"{item}",')
    lines.append("]")
    return "\n".join(lines)


def update_toml_dependencies(
    content: str, runtime_deps: list[str], dev_deps: list[str] | None = None
) -> str:
    deps_block = format_toml_array("dependencies", runtime_deps)
    content = re.sub(r"dependencies\s*=\s*\[[\s\S]*?\n\]", deps_block, content)
    if dev_deps is not None:
        dev_block = format_toml_array("dev", dev_deps)
        content = re.sub(r"dev\s*=\s*\[[\s\S]*?\n\]", dev_block, content)
    return content


def update_setup_cfg(content: str, runtime_deps: list[str]) -> str:
    lines = ["install_requires ="]
    for dep in runtime_deps:
        lines.append(f"    {dep}")
    req_block = "\n".join(lines)
    return re.sub(r"install_requires\s*=(?:\n[ \t]+[^\n]+)+", req_block, content)


def sync_python_manifests(dry_run: bool = False) -> tuple[list[str], list[str]]:
    root_pyproject_path = ROOT / "pyproject.toml"
    backend_pyproject_path = ROOT / "backend" / "pyproject.toml"
    setup_cfg_path = ROOT / "setup.cfg"
    backend_setup_cfg_path = ROOT / "backend" / "setup.cfg"
    runtime_txt_path = ROOT / "backend" / "requirements-runtime.txt"
    dev_txt_path = ROOT / "backend" / "requirements-dev.txt"

    root_proj = load_pyproject(root_pyproject_path).get("project", {})
    backend_proj = load_pyproject(backend_pyproject_path).get("project", {})

    runtime_from_txt = [
        line.strip()
        for line in runtime_txt_path.read_text().splitlines()
        if line.strip() and not line.strip().startswith(("#", "-"))
    ]
    dev_from_txt = [
        line.strip()
        for line in dev_txt_path.read_text().splitlines()
        if line.strip() and not line.strip().startswith(("#", "-"))
    ]

    merged_runtime = merge_dependency_lists(
        root_proj.get("dependencies", []),
        backend_proj.get("dependencies", []),
        runtime_from_txt,
    )

    merged_dev = merge_dependency_lists(
        root_proj.get("optional-dependencies", {}).get("dev", []),
        backend_proj.get("optional-dependencies", {}).get("dev", []),
        dev_from_txt,
    )

    print(f"Synchronizing {len(merged_runtime)} runtime and {len(merged_dev)} dev dependencies...")

    # 1. Update root pyproject.toml
    root_content = root_pyproject_path.read_text()
    new_root_content = update_toml_dependencies(root_content, merged_runtime, merged_dev)
    if not dry_run and new_root_content != root_content:
        root_pyproject_path.write_text(new_root_content)
        print("  Updated pyproject.toml")

    # 2. Update backend/pyproject.toml
    backend_content = backend_pyproject_path.read_text()
    new_backend_content = update_toml_dependencies(backend_content, merged_runtime, merged_dev)
    if not dry_run and new_backend_content != backend_content:
        backend_pyproject_path.write_text(new_backend_content)
        print("  Updated backend/pyproject.toml")

    # 3. Update setup.cfg
    if setup_cfg_path.exists():
        setup_content = setup_cfg_path.read_text()
        new_setup_content = update_setup_cfg(setup_content, merged_runtime)
        if not dry_run and new_setup_content != setup_content:
            setup_cfg_path.write_text(new_setup_content)
            print("  Updated setup.cfg")

    # 4. Update backend/setup.cfg
    if backend_setup_cfg_path.exists():
        b_setup_content = backend_setup_cfg_path.read_text()
        new_b_setup_content = update_setup_cfg(b_setup_content, merged_runtime)
        if not dry_run and new_b_setup_content != b_setup_content:
            backend_setup_cfg_path.write_text(new_b_setup_content)
            print("  Updated backend/setup.cfg")

    # 5. Update backend/requirements-runtime.txt
    new_runtime_txt = "\n".join(merged_runtime) + "\n"
    if not dry_run and new_runtime_txt != runtime_txt_path.read_text():
        runtime_txt_path.write_text(new_runtime_txt)
        print("  Updated backend/requirements-runtime.txt")

    # 6. Update backend/requirements-dev.txt
    dev_header = (
        "# Development / CI-only dependencies. Install everything needed for local\n"
        "# development and tests with:\n"
        "#     pip install -r requirements.txt -r requirements-dev.txt\n"
        "# Runtime dependencies live in requirements-runtime.txt and the fully resolved,\n"
        "# reproducible set (including transitives) is pinned in requirements.lock.\n"
        "-r requirements-runtime.txt\n"
    )
    new_dev_txt = dev_header + "\n".join(merged_dev) + "\n"
    if not dry_run and new_dev_txt != dev_txt_path.read_text():
        dev_txt_path.write_text(new_dev_txt)
        print("  Updated backend/requirements-dev.txt")

    return merged_runtime, merged_dev


def find_uv_executable() -> str | None:
    # Check PATH
    uv_path = shutil.which("uv")
    if uv_path:
        return uv_path
    # Check .venv
    venv_uv = ROOT / ".venv" / "bin" / "uv"
    if venv_uv.exists() and venv_uv.is_file():
        return str(venv_uv)
    # Check if python -m uv works
    try:
        subprocess.run(
            [sys.executable, "-m", "uv", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return f"{sys.executable} -m uv"
    except Exception:
        pass
    return None


def run_command(cmd: list[str] | str, cwd: Path = ROOT, shell: bool = False) -> None:
    print(f"  Running: {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True, shell=shell)


def recompile_lockfiles(dry_run: bool = False) -> None:
    if dry_run:
        print("Dry run: skipping lockfile compilation.")
        return

    uv_cmd = find_uv_executable()
    if not uv_cmd:
        print(
            "Warning: `uv` not found. Skipping lockfile recompilation. "
            "Install uv (`pip install uv`) and run `make deps-sync`.",
            file=sys.stderr,
        )
        return

    is_module = uv_cmd.startswith(f"{sys.executable} -m uv")
    uv_base = [sys.executable, "-m", "uv"] if is_module else [uv_cmd]

    print("Recompiling backend/requirements.lock...")
    run_command(
        uv_base
        + [
            "pip",
            "compile",
            "pyproject.toml",
            "--extra",
            "dev",
            "--output-file",
            "backend/requirements.lock",
        ]
    )

    print("Regenerating root uv.lock...")
    run_command(uv_base + ["lock"])

    print("Regenerating backend/uv.lock...")
    run_command(uv_base + ["lock"], cwd=ROOT / "backend")


def sync_node_manifests(dry_run: bool = False) -> None:
    package_json = ROOT / "frontend" / "package.json"
    package_lock = ROOT / "frontend" / "package-lock.json"
    if not package_json.exists() or not package_lock.exists():
        return

    try:
        pkg = json.loads(package_json.read_text())
        lock = json.loads(package_lock.read_text())
    except Exception:
        return

    needs_sync = False
    if lock.get("name") != pkg.get("name") or lock.get("version") != pkg.get("version"):
        needs_sync = True

    root_entry = lock.get("packages", {}).get("", {})
    for section in ("dependencies", "devDependencies"):
        if pkg.get(section, {}) != root_entry.get(section, {}):
            needs_sync = True
            break

    if needs_sync and not dry_run:
        npm_bin = shutil.which("npm")
        if npm_bin:
            print("Syncing frontend/package-lock.json...")
            run_command([npm_bin, "install", "--package-lock-only"], cwd=ROOT / "frontend")


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize dependency manifests and lockfiles.")
    parser.add_argument(
        "--no-compile", action="store_true", help="Skip recompiling lockfiles with uv/npm"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Check and print actions without modifying files"
    )
    args = parser.parse_args()

    sync_python_manifests(dry_run=args.dry_run)

    if not args.no_compile:
        recompile_lockfiles(dry_run=args.dry_run)
        sync_node_manifests(dry_run=args.dry_run)

    print("\nDependency synchronization complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
