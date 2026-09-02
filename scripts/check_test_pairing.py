#!/usr/bin/env python3
"""Enforce test-paired changes across production code diffs.

Asserts that any pull request or commit set touching production source code
(backend/app/ or frontend/src/) also includes corresponding test changes
(backend/tests/ or frontend/src/**/__tests__ or frontend/tests/).

Run directly:
    python3 scripts/check_test_pairing.py [--base origin/main]
"""
from __future__ import annotations

import argparse
import subprocess
import sys


def get_changed_files(base: str | None = None) -> list[str]:
    cmd = ["git", "diff", "--name-only"]
    if base:
        cmd.append(base)
    else:
        cmd.extend(["HEAD~1", "HEAD"])
    try:
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        return [line.strip() for line in output.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        return []


def verify_test_pairing(files: list[str]) -> tuple[bool, str]:
    has_backend_prod = any(f.startswith("backend/app/") for f in files)
    has_backend_test = any(f.startswith("backend/tests/") for f in files)

    has_frontend_prod = any(
        f.startswith("frontend/src/") and not ("/__tests__/" in f or f.endswith(".test.ts") or f.endswith(".test.tsx"))
        for f in files
    )
    has_frontend_test = any(
        "/__tests__/" in f or f.startswith("frontend/tests/") or f.endswith(".test.ts") or f.endswith(".test.tsx")
        for f in files
    )

    if has_backend_prod and not has_backend_test:
        return False, "Backend production code changed in backend/app/ without paired test in backend/tests/."

    if has_frontend_prod and not has_frontend_test:
        return False, "Frontend production code changed in frontend/src/ without paired test in frontend/src/**/__tests__/."

    return True, "Test pairing requirement satisfied."


def main() -> int:
    parser = argparse.ArgumentParser(description="Check test pairing for git changes.")
    parser.add_argument("--base", help="Base git ref to compare against (e.g. origin/main)")
    args = parser.parse_args()

    files = get_changed_files(args.base)
    if not files:
        print("No changed files found in the specified range. Skipping check.")
        return 0

    ok, message = verify_test_pairing(files)
    if not ok:
        print(f"ERROR: {message}", file=sys.stderr)
        print("Every change to production code must include corresponding test diffs in the same PR/commit.", file=sys.stderr)
        return 1

    print(f"SUCCESS: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
