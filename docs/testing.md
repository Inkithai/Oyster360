# Testing guide

How to run and extend the Oyster360 test suites locally, and what CI enforces
on every pull request. For the same commands as Make targets run `make help`
from the repository root.

## Test lanes

| Lane | What it covers | Command |
| --- | --- | --- |
| Backend fast unit | All tests not marked `integration` (no external services) | `cd backend && pytest -m "not integration" -q` |
| Backend full suite | Everything, including `integration`-marked tests (in-memory SQLite) | `cd backend && pytest` |
| Backend + coverage gate | Full suite with `pytest-cov`, fails under 70% | `cd backend && pytest --cov=app --cov-report=term-missing --cov-fail-under=70` |
| Frontend unit + coverage | Vitest with jsdom + React Testing Library, thresholds enforced | `cd frontend && npm run test:coverage` |
| Frontend typecheck | TypeScript, no emit | `cd frontend && npx tsc --noEmit` |
| Frontend lint | ESLint, zero warnings allowed | `cd frontend && npm run lint` |
| End-to-end | Playwright browser specs (installs Chromium on first use) | `cd frontend && npm run test:e2e` |
| Compose integration | Full suite against ephemeral PostgreSQL (pgvector) + Redis in Docker | `docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test-runner` |

The one-command local equivalent of the CI gates is `make verify`.

## Backend conventions

- Tests live in `backend/tests/` as `test_*.py`; markers are `unit`,
  `integration`, `security`, and `slow` (declared in `backend/pytest.ini`).
- Anything needing PostgreSQL- or Redis-specific behaviour should be marked
  `@pytest.mark.integration` so the fast lane stays offline.
- Coverage is measured across `backend/app` with branch coverage on
  (`[tool.coverage.run]` in `backend/pyproject.toml`). The suite currently
  measures ~77%; CI fails below 70%.
- Lint policy (`flake8`, select `E9,F63,F7,F82`) intentionally excludes
  generated Alembic migrations under `backend/alembic/versions/`.

## Frontend conventions

- Component and page tests live next to the source in `__tests__/`
  directories; end-to-end specs live in `frontend/tests/e2e/`.
- `vitest.config.ts` scopes coverage reporting to the interactive surface that
  has behavior tests; add a source file to the `include` list together with
  its test. Thresholds: lines/statements/functions ≥ 70%, branches ≥ 60%.
- API access is mocked at the network layer (see `src/lib/__tests__/api.test.ts`)
  so tests do not require a running backend.

## What CI runs on every pull request

`.github/workflows/ci.yml` executes six jobs:

1. **Lockfile reproducibility** — `uv lock --check` (root and backend),
   re-compiled `requirements.lock`, and `package-lock.json` must all match
   their manifests. On Dependabot PRs the lockfiles are regenerated and pushed
   back to the branch instead of failing.
2. **Backend** — flake8, advisory mypy, fast unit lane, full suite with the
   70% coverage gate; coverage XML uploaded as an artifact.
3. **Frontend** — `npm ci`, ESLint, `tsc --noEmit`, Vitest with coverage
   thresholds, `next build`; lcov uploaded as an artifact.
4. **Docker build and integration tests** — `docker compose config`
   validation, builds of both production images, and the isolated Compose
   test stack.
5. **Security audit** — blocks committed `.env` files, `pip-audit` on
   `requirements.lock`, `npm audit --audit-level=high`, and a Trivy
   filesystem scan whose SARIF lands in the GitHub Security tab.
6. **Deploy (main and v\* tags only)** — builds and publishes
   `oyster360-api` and `oyster360-web` images to GitHub Container Registry.

## Writing good tests

Prefer behavior over line-count: assert on outcomes a user or caller would
observe (returned values, persisted state, HTTP status codes, rendered text)
rather than implementation details. Every behavior change should ship with a
test that fails before the change and passes after it — the pull request
template asks for exactly that.
