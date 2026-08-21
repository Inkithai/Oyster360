# Changelog

All notable changes to Oyster360 are documented here. This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses Semantic Versioning.

## [Unreleased]

### Added
- Root PEP 621 `pyproject.toml` and `requirements.txt` so dependency tooling resolves runtime deps from the repository root.
- `uv.lock` alongside `backend/requirements.lock` for reproducible Python installs.
- `pre-commit` config that runs the same flake8 exclude set as CI (`backend/alembic/versions/*`).
- Security, support, code of conduct, and authors documents.
- Issue and pull-request templates that require source changes to ship with tests.

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

[Unreleased]: https://github.com/Inkithai/Oyster360/compare/v1.0.0...HEAD
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
