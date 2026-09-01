# Changelog

All notable changes to Oyster360 are documented here. This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses Semantic Versioning.

## [Unreleased]

### Added
- `make ci-local` (`scripts/ci-local.sh`): reproduces every CI gate from a completely fresh clone — dependency install, dependency-sync check, backend lint/typecheck/tests with coverage, and frontend lint/typecheck/tests — with no Docker, no PostgreSQL/Redis and no API keys required. Verified end to end against a clean checkout.
- `make deps-check` (`scripts/check_dependency_sync.py`): deterministic verification that the root and backend `pyproject.toml`, `requirements-runtime.txt`, `requirements-dev.txt`, `requirements.lock`, `package.json` and `package-lock.json` all agree. Replaces the recompile-and-diff CI step, which failed spuriously whenever an unpinned transitive dependency published a new release.
- Autouse `block_outbound_sockets` test fixture: any non-`integration` test that opens a non-loopback socket now fails loudly, making the suite's offline guarantee enforced rather than conventional. `tests/test_offline_isolation.py` asserts the guarantee directly.
- Test coverage for previously untested business-critical paths: Stripe webhook verification/idempotency/failure handling, subscription lifecycle, `require_subscription` plan enforcement, organization membership and tenant switching, and the AI, RAG, vision and assistant services. Backend coverage rose from ~77% to ~87%.
- `backend/mypy.ini` with a documented, shrinking per-module baseline for files awaiting the SQLAlchemy `Mapped[...]` migration.
- README sections for reproducing CI locally, the test-isolation guarantees, a layered architecture diagram, and the dependency-management policy.
- `make fresh-start` one-command path for a machine that has never seen the repo: copies `.env.example` to `.env`, starts PostgreSQL and Redis, applies `alembic upgrade head`, and brings up the backend and frontend.
- Quick Start documentation for `make fresh-start` and the expected backend log line `Uvicorn running on 0.0.0.0:8000`.

### Fixed
- RAG retrieval matched only whitespace-delimited tokens, so a question such as "what humidity?" never matched a chunk containing the bare word `humidity`; tokenization now strips punctuation.
- `RAGService.chunk_text` looped forever when `overlap >= chunk_size` and emitted a spurious empty chunk for blank documents; both cases are now validated.
- The CI lockfile job recompiled `requirements.lock` without the `dev` extra, so the committed lockfile could never match and the check was effectively dead.
- README referenced a `backend/requirements.txt` that does not exist.

### Changed
- `mypy` is now a **blocking** CI gate (`mypy app`) instead of an advisory step, and is pinned in `pyproject.toml`, `backend/pyproject.toml`, `requirements-dev.txt` and `requirements.lock`.
- Backend coverage gate raised from 70% to 80% across CI, `make verify`, `make ci-local` and the coverage configuration.
- `make verify` now runs flake8 and mypy in addition to the test lanes, matching CI exactly.
- Maintainer roster lists ten people so each feature or fix can land as its own pull request with a named reviewer (see `AUTHORS.md` and `CONTRIBUTING.md`).

## [1.1.0] - 2026-08-24

### Added
- Deployment automation: every green run on `main` and every `v*` tag builds and publishes `oyster360-api` and `oyster360-web` images to GitHub Container Registry (`ghcr.io/inkithai/oyster360`).
- `pip-audit` dependency gate for the backend tree alongside `npm audit` and the Trivy filesystem scan (SARIF results published to the GitHub Security tab).
- Advisory `mypy` type-check step for the backend (pinned 2.3.1) as the first step toward a hard type gate.
- Coverage reports uploaded as workflow artifacts for backend (XML) and frontend (lcov) test jobs.
- CI now regenerates `uv.lock` and `requirements.lock` on Dependabot pull requests and pushes the result back to the PR branch, so dependency updates are installable, fully tested, and mergeable.
- Manual `workflow_dispatch` trigger and a `develop` pull-request target; least-privilege per-job permissions.
- Root PEP 621 `pyproject.toml` and `requirements.txt` so dependency tooling resolves runtime deps from the repository root.
- `uv.lock` alongside `backend/requirements.lock` for reproducible Python installs.
- `pre-commit` config that runs the same flake8 exclude set as CI (`backend/alembic/versions/*`).
- Security, support, code of conduct, and authors documents.
- Issue and pull-request templates that require source changes to ship with tests.
- Testing guide (`docs/testing.md`) covering local test lanes, coverage gates, and the CI pipeline.

### Changed
- Backend pytest coverage gate raised from 60% to 70% (suite currently measures ~77%).
- Frontend typecheck step runs `tsc --noEmit` explicitly; both production Docker images are now built on every pull request.
- Pinned `trivy-action` to the upstream `v0.36.0` tag (the unprefixed tag Dependabot referenced no longer resolves).
- Frontend lockfile verification normalizes `package-lock.json` to the CI npm format on Dependabot branches.

### Dependencies
- stripe 15.5.0 → 15.5.1
- SQLAlchemy 2.0.41 → 2.0.52
- python-json-logger 2.0.7 → 4.2.0
- pre-commit 4.3.0 → 4.6.2
- @tailwindcss/postcss 4.3.2 → 4.3.3
- autoprefixer 10.4.21 → 10.5.4
- @radix-ui/react-dialog 1.1.14 → 1.1.23

## [1.0.0] - 2026-08-21

### Added
- Frontend `test:coverage` script with Vitest thresholds (lines/statements/functions >= 70%, branches >= 60%).
- Isolated Docker Compose test stack with ephemeral PostgreSQL and Redis.
- Structured JSON request/error logging and optional Sentry error tracking.
- One-command bootstrap script and Makefile shortcuts for fresh clones.

### Changed
- Dashboard renders API values exactly and displays honest error/empty states.
- Yield prediction aggregates real Harvest and EnvironmentLog records.

## [0.9.0] - 2026-07-18

### Added
- Playwright end-to-end specs for login and dashboard (network-level API mocks).
- Login, register, and reset-password page specs.

## [0.8.0] - 2026-06-20

### Added
- Trivy filesystem scanning and Dependabot for npm, pip, and GitHub Actions.
- Coverage-gated backend pytest (`--cov-fail-under=60`).

## [0.7.0] - 2026-05-23

### Added
- Stripe billing, signed webhooks, and subscription lifecycle.
- GDPR export/delete compliance endpoints.

## [0.6.0] - 2026-04-25

### Added
- Next.js App Router frontend with role-aware navigation.
- Reusable UI components, TanStack Query client, and Zod forms.

## [0.5.0] - 2026-03-28

### Added
- FastAPI routers for batches, recipes, inventory, purchases, analytics, and AI.

## [0.4.0] - 2026-02-21

### Added
- Domain services for inventory movements, harvest grading, MFA, and onboarding.

## [0.3.0] - 2026-01-24

### Added
- SQLAlchemy models for organizations, farms, batches, harvests, and inventory.

## [0.2.0] - 2025-11-15

### Added
- Multi-tenant middleware, rate limiting, and JWT authentication utilities.

## [0.1.0] - 2025-08-16

### Added
- Initial repository, Docker Compose topology, backend configuration, and product docs.

[Unreleased]: https://github.com/Inkithai/Oyster360/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Inkithai/Oyster360/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Inkithai/Oyster360/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/Inkithai/Oyster360/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/Inkithai/Oyster360/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/Inkithai/Oyster360/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/Inkithai/Oyster360/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/Inkithai/Oyster360/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Inkithai/Oyster360/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Inkithai/Oyster360/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Inkithai/Oyster360/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Inkithai/Oyster360/releases/tag/v0.1.0
