#!/usr/bin/env bash
#
# Reproduce the CI quality gates locally, from a completely fresh clone.
#
#   git clone https://github.com/Inkithai/Oyster360.git
#   cd Oyster360
#   cp .env.example .env      # optional: ci-local.sh creates it if missing
#   make ci-local
#
# What it runs (identical to .github/workflows/ci.yml, jobs: lint / typecheck /
# test / lockfiles):
#
#   1. environment file
#   2. backend dependency install into .venv from backend/requirements.lock
#   3. frontend dependency install with `npm ci` from package-lock.json
#   4. dependency synchronisation (pyproject.toml <-> requirements.lock <->
#      requirements-*.txt, package.json <-> package-lock.json, uv.lock)
#   5. backend lint (flake8)
#   6. backend typecheck (mypy)
#   7. backend tests + coverage gate (pytest -m "not integration")
#   8. frontend lint (eslint)
#   9. frontend typecheck (tsc --noEmit)
#  10. frontend tests + coverage (vitest)
#
# Requirements: Python 3.11+, Node 20+, and network access for the first
# dependency install only. No Docker, no PostgreSQL, no Redis, and no API keys:
# the default test lane runs against in-memory SQLite with every external
# provider (Stripe, OpenAI, Redis, outbound HTTP) stubbed in
# backend/tests/conftest.py.
#
# Exits non-zero on the first failing check.
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$PWD"
VENV="$ROOT/.venv"
PY_BIN="${PYTHON:-python3}"
SKIP_INSTALL="${SKIP_INSTALL:-0}"
step=0

log() {
  step=$((step + 1))
  printf '\n\033[1;36m[ci-local %2d]\033[0m %s\n' "$step" "$1"
}

fail() {
  printf '\n\033[1;31mci-local failed:\033[0m %s\n' "$1" >&2
  exit 1
}

command -v "$PY_BIN" >/dev/null 2>&1 || fail "python3 not found (need Python 3.11+)"
command -v node >/dev/null 2>&1 || fail "node not found (need Node 20+)"
command -v npm >/dev/null 2>&1 || fail "npm not found (need Node 20+)"

"$PY_BIN" - <<'PYVER' || fail "Python 3.11+ is required"
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
PYVER

log "Environment file"
if [ -f .env ]; then
  echo "reusing existing .env"
else
  cp .env.example .env
  echo "created .env from .env.example"
fi

log "Backend dependencies (.venv from backend/requirements.lock)"
if [ "$SKIP_INSTALL" = "1" ]; then
  echo "SKIP_INSTALL=1, reusing $VENV"
  [ -x "$VENV/bin/python" ] || fail "SKIP_INSTALL=1 but $VENV does not exist"
else
  [ -x "$VENV/bin/python" ] || "$PY_BIN" -m venv "$VENV"
  "$VENV/bin/python" -m pip install --quiet --upgrade pip
  "$VENV/bin/python" -m pip install --quiet -r backend/requirements.lock
fi
PY="$VENV/bin/python"

log "Frontend dependencies (npm ci)"
if [ "$SKIP_INSTALL" = "1" ] && [ -d frontend/node_modules ]; then
  echo "SKIP_INSTALL=1, reusing frontend/node_modules"
else
  (cd frontend && npm ci --no-audit --no-fund)
fi

log "Dependency manifest / lockfile synchronisation"
"$PY" scripts/check_dependency_sync.py
"$PY" -m pip install --quiet uv
"$PY" -m uv lock --check || fail "root uv.lock is out of sync. Regenerate with: uv lock"
(cd backend && "$PY" -m uv lock --check) ||
  fail "backend/uv.lock is out of sync. Regenerate with: cd backend && uv lock"

log "Backend lint (flake8)"
(cd backend && "$PY" -m flake8 app tests --count --show-source --statistics \
  --exclude=.venv,__pycache__,alembic/versions)

log "Backend typecheck (mypy)"
(cd backend && "$PY" -m mypy app)

log "Backend tests + coverage (offline lane)"
(cd backend && "$PY" -m pytest -m "not integration" \
  --cov=app --cov-report=term-missing --cov-fail-under=70)

log "Frontend lint (eslint)"
(cd frontend && npm run lint)

log "Frontend typecheck (tsc --noEmit)"
(cd frontend && npm run typecheck)

log "Frontend tests + coverage (vitest)"
(cd frontend && npm run test:coverage)

printf '\n\033[1;32mci-local passed:\033[0m all %d checks succeeded.\n' "$step"
echo "Integration tests that need PostgreSQL/Redis are not part of this lane."
echo "Run them with: make test-integration"
