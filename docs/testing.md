# Testing guide

How to run and extend the Oyster360 test suites locally, and what CI enforces
on every pull request. For the same commands as Make targets run `make help`
from the repository root.

## Test lanes

| Lane | What it covers | Command |
| --- | --- | --- |
| Backend fast unit | All tests not marked `integration` (no external services) | `cd backend && pytest -m "not integration" -q` |
| Backend full suite | Everything, including `integration`-marked tests (in-memory SQLite) | `cd backend && pytest` |
| Backend + coverage gate | Full suite with `pytest-cov`, fails under 80% | `cd backend && pytest --cov=app --cov-report=term-missing --cov-fail-under=80` |
| Backend typecheck | `mypy` against `backend/mypy.ini` (blocking in CI) | `cd backend && mypy app` |
| Dependency sync | Manifests vs. lockfiles, both ecosystems | `make deps-check` |
| Frontend unit + coverage | Vitest with jsdom + React Testing Library, thresholds enforced | `cd frontend && npm run test:coverage` |
| Frontend typecheck | TypeScript, no emit | `cd frontend && npx tsc --noEmit` |
| Frontend lint | ESLint, zero warnings allowed | `cd frontend && npm run lint` |
| End-to-end | Playwright browser specs (installs Chromium on first use) | `cd frontend && npm run test:e2e` |
| Compose integration | Full suite against ephemeral PostgreSQL (pgvector) + Redis in Docker | `docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test-runner` |

The one-command local equivalent of the CI gates is **`make ci-local`**, which
also installs dependencies and therefore works on a completely fresh clone:

```bash
git clone https://github.com/Inkithai/Oyster360.git
cd Oyster360
make ci-local
```

Use `SKIP_INSTALL=1 make ci-local` (or `make verify`) when dependencies are
already installed.

## Offline isolation guarantee

The default lane must run with no credentials, no infrastructure and no
internet. Two autouse fixtures in `backend/tests/conftest.py` enforce this
rather than leaving it to convention:

- `block_outbound_sockets` raises `AssertionError` if a non-`integration` test
  connects to anything other than loopback.
- `block_external_services` stubs every `requests` HTTP verb and every Stripe
  client call, including webhook signature verification.

```text
pytest -m "not integration"
   ├── PostgreSQL ──── in-memory SQLite, fresh schema per test
   ├── Redis ───────── in-process fake client
   ├── Stripe ──────── stubbed client and webhook verification
   ├── AI providers ── stubbed; services fall back to rule-based output
   └── outbound TCP ── blocked
```

`tests/test_offline_isolation.py` asserts these properties, and the lane is
verified to pass inside a network-disabled namespace (`unshare -rn`). If a new
test genuinely needs infrastructure, mark it `@pytest.mark.integration`.

## Backend conventions

- Tests live in `backend/tests/` as `test_*.py`; markers are `unit`,
  `integration`, `security`, and `slow` (declared in `backend/pytest.ini`).
- Anything needing PostgreSQL- or Redis-specific behaviour should be marked
  `@pytest.mark.integration` so the fast lane stays offline.
- Coverage is measured across `backend/app` with branch coverage on
  (`[tool.coverage.run]` in `backend/pyproject.toml`). The suite currently
  measures ~87%; CI fails below 80%.
- Lint policy (`flake8`) intentionally excludes generated Alembic migrations
  under `backend/alembic/versions/`.
- Type checking is a hard gate: `mypy app` must pass. `backend/mypy.ini` holds
  a shrinking per-module baseline for files awaiting the SQLAlchemy
  `Mapped[...]` migration; new modules are checked from day one.

## Frontend conventions

- Component and page tests live next to the source in `__tests__/`
  directories; end-to-end specs live in `frontend/tests/e2e/`.
- `vitest.config.ts` scopes coverage reporting to the interactive surface that
  has behavior tests; add a source file to the `include` list together with
  its test. Thresholds: lines/statements/functions ≥ 70%, branches ≥ 60%.
- API access is mocked at the network layer (see `src/lib/__tests__/api.test.ts`)
  so tests do not require a running backend.

## What CI runs on every pull request

`.github/workflows/ci.yml` executes seven jobs:

1. **Lockfile reproducibility** — `uv lock --check` (root and backend),
   `scripts/check_dependency_sync.py`, `pip install --dry-run -r
   requirements.lock`, and `npm ci --dry-run`. On Dependabot PRs the uv
   lockfiles are regenerated and pushed back to the branch instead of failing.
2. **Lint** — flake8 (backend) and `eslint --max-warnings=0` (frontend).
3. **Typecheck** — `mypy app` and `tsc --noEmit`. Both are blocking.
4. **Test** — fast offline lane, full suite with the 80% coverage gate, Vitest
   with coverage; coverage XML and lcov uploaded as artifacts.
5. **Docker build and integration tests** — `docker compose config`
   validation, builds of both production images, and the isolated Compose
   test stack.
6. **Security audit** — blocks committed `.env` files, `pip-audit` on
   `requirements.lock`, `npm audit --audit-level=high`, and a Trivy
   filesystem scan whose SARIF lands in the GitHub Security tab.
7. **Deploy (main and v\* tags only)** — builds and publishes
   `oyster360-api` and `oyster360-web` images to GitHub Container Registry.

## Writing good tests

Prefer behavior over line-count: assert on outcomes a user or caller would
observe (returned values, persisted state, HTTP status codes, rendered text)
rather than implementation details. Every behavior change should ship with a
test that fails before the change and passes after it — the pull request
template asks for exactly that.
