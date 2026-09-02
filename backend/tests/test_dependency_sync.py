"""Tests for dependency synchronisation and manifest consistency checks."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from check_dependency_sync import (  # noqa: E402
    canonical,
    check_node_manifests,
    check_python_manifests,
    errors as check_errors,
    parse_requirements,
)
from sync_dependencies import (  # noqa: E402
    format_toml_array,
    merge_dependency_lists,
    parse_dep,
    parse_version,
    update_setup_cfg,
    update_toml_dependencies,
)


def test_canonical_names():
    assert canonical("sentry-sdk") == "sentry-sdk"
    assert canonical("sentry_sdk") == "sentry-sdk"
    assert canonical("PyYAML") == "pyyaml"
    assert canonical("argon2-cffi-bindings") == "argon2-cffi-bindings"


def test_parse_version():
    assert parse_version("2.68.1") > parse_version("2.68.0")
    assert parse_version("1.0.0") > parse_version("0.9.9")
    assert parse_version("2.9.0.post0") > parse_version("2.9.0")
    assert parse_version("2.0.0b1") < parse_version("2.0.0")
    assert parse_version("==2.68.1") == parse_version("2.68.1")


def test_parse_dep():
    canon, raw, op, ver = parse_dep("sentry-sdk==2.68.1")
    assert canon == "sentry-sdk"
    assert raw == "sentry-sdk"
    assert op == "=="
    assert ver == "2.68.1"

    canon, raw, op, ver = parse_dep("qrcode[pil]==8.2")
    assert canon == "qrcode"
    assert raw == "qrcode[pil]"
    assert op == "=="
    assert ver == "8.2"

    canon, raw, op, ver = parse_dep("starlette>=1.0.1")
    assert canon == "starlette"
    assert raw == "starlette"
    assert op == ">="
    assert ver == "1.0.1"


def test_merge_dependency_lists():
    list_root = ["fastapi==0.141.1", "sentry-sdk==2.68.1", "qrcode[pil]==8.2"]
    list_backend = ["fastapi==0.141.1", "sentry-sdk==2.68.0", "qrcode==8.2"]

    merged = merge_dependency_lists(list_root, list_backend)
    assert "sentry-sdk==2.68.1" in merged
    assert "qrcode[pil]==8.2" in merged
    assert "fastapi==0.141.1" in merged

    # Test reverse precedence — higher version wins regardless of argument position
    merged_reverse = merge_dependency_lists(list_backend, list_root)
    assert "sentry-sdk==2.68.1" in merged_reverse
    assert "qrcode[pil]==8.2" in merged_reverse


def test_update_toml_dependencies():
    content = """[project]
name = "oyster360"
dependencies = [
    "fastapi==0.141.1",
    "sentry-sdk==2.68.0",
]

[project.optional-dependencies]
dev = [
    "flake8==7.3.0",
]
"""
    updated = update_toml_dependencies(
        content,
        ["fastapi==0.141.1", "sentry-sdk==2.68.1"],
        ["flake8==7.3.0", "pytest==9.1.1"],
    )
    assert '"sentry-sdk==2.68.1",' in updated
    assert '"pytest==9.1.1",' in updated


def test_update_setup_cfg():
    content = """[metadata]
name = oyster360

[options]
python_requires = >=3.11
install_requires =
    fastapi==0.141.1
    sentry-sdk==2.68.0

[flake8]
select = E9
"""
    updated = update_setup_cfg(
        content,
        ["fastapi==0.141.1", "sentry-sdk==2.68.1"],
    )
    assert "sentry-sdk==2.68.1" in updated
    assert "[flake8]" in updated


def test_parse_requirements():
    lines = [
        "# A comment",
        "fastapi==0.141.1",
        "qrcode[pil]==8.2",
        "-r requirements-runtime.txt",
        "",
    ]
    parsed = parse_requirements(lines)
    assert parsed["fastapi"] == "0.141.1"
    assert parsed["qrcode"] == "8.2"
    assert "requirements-runtime.txt" not in parsed


def test_current_manifests_pass_checks():
    check_errors.clear()
    check_python_manifests()
    check_node_manifests()
    assert check_errors == [], f"Unexpected dependency sync errors: {check_errors}"
