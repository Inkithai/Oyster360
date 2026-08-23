# Changelog

All notable changes to Oyster360 are documented here. This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses Semantic Versioning.

## [Unreleased]

### Added
- Structured frontend logging (`src/lib/logger.ts`) with levels and `X-Request-ID` correlation, optional Sentry-compatible client error reporting via `NEXT_PUBLIC_SENTRY_DSN`, and a reporting `ErrorBoundary` mounted in providers.
- GDPR compliance API tests (export + deletion) and verified Stripe webhook API tests, including signature verification, metadata validation, and every handled event type.
- Unit tests for the pure analytics math in `analytics_calculations`, plus page specs for forgot-password, strains, and settings/subscription; the vitest coverage gate now tracks all eight covered surfaces at 60%.
- `make test-all` target documented in the README: offline unit lanes followed by the full integration suite on `docker-compose.test.yml`.
- Shared HTTP middleware tests (security headers, request IDs) and app-wide rate-limiter middleware tests.

### Changed
- `app.main` no longer defines middleware inline: security headers and request IDs live in `app/core/middleware.py`, and the app-wide rate limiter shares the sliding-window store in `app/core/rate_limit.py`.
- `AnalyticsService` delegates its agronomy math to database-free helpers in `app/services/analytics_calculations.py`.
- CI now fails when `backend/requirements.lock` drifts from `requirements.txt` (pip-compile reproducibility check) and documents the lockfile policy in the README.

### Fixed
- Stripe webhook router no longer mutates `stripe.api_key` at import time; the key is resolved per request.
- Deprecated `datetime.utcfromtimestamp`/naive `utcnow` usage replaced in webhook timestamps and GDPR export payloads.
- Forgot-password email label is programmatically associated with its input (screen-reader/a11y fix).
- Isolated Docker Compose test stack with ephemeral PostgreSQL and Redis.
- Frontend dashboard and data-table interaction tests with a 60% coverage gate.
- Explicit TypeScript typecheck in local scripts and CI.
- Structured JSON request/error logging and optional Sentry error tracking.
- Deterministic test fixtures that prevent Stripe and AI provider network calls.
- Contributor workflow and maintenance documentation.
- One-command bootstrap script and Makefile shortcuts for fresh clones, plus backend flake8 config and a native `backend/.env.example`.
- Analytics service tests pinning deterministic, fixture-derived predictions, plus admin and notifications API test suites.
- Login, register, and reset-password page specs, and route-level API mocks for the dashboard e2e test.

### Changed
- Dashboard now renders API values exactly and displays honest error/empty states instead of demo fallbacks.
- CI now validates linting, typechecking, coverage, clean-clone Docker tests, and high/critical dependency findings.
- Yield prediction now aggregates real Harvest and EnvironmentLog records instead of random factors, and strain/recipe performance metrics are computed from recorded batches instead of hash-based placeholders.
- The end-to-end lifecycle suite is marked `integration` so `pytest -m "not integration"` provides a fast, service-free unit lane.

### Fixed
- CI workflow is valid YAML rather than a Markdown-fenced document.
- CSV export now quotes headers, handles null values, and releases generated object URLs.

## [0.1.0] - 2026-08-22

### Added
- Initial Oyster360 SaaS application with tenant-aware farm management APIs, dashboards, billing foundations, Docker deployment, and automated tests.

[Unreleased]: https://github.com/Inkithai/Oyster360/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Inkithai/Oyster360/releases/tag/v0.1.0
