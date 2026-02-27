# Changelog

All notable changes to Oyster360 are documented here. This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and uses Semantic Versioning.

## [Unreleased]

### Added
- Isolated Docker Compose test stack with ephemeral PostgreSQL and Redis.
- Frontend dashboard and data-table interaction tests with a 60% coverage gate.
- Explicit TypeScript typecheck in local scripts and CI.
- Structured JSON request/error logging and optional Sentry error tracking.
- Deterministic test fixtures that prevent Stripe and AI provider network calls.
- Contributor workflow and maintenance documentation.

### Changed
- Dashboard now renders API values exactly and displays honest error/empty states instead of demo fallbacks.
- CI now validates linting, typechecking, coverage, clean-clone Docker tests, and high/critical dependency findings.

### Fixed
- CI workflow is valid YAML rather than a Markdown-fenced document.
- CSV export now quotes headers, handles null values, and releases generated object URLs.

## [0.1.0] - 2026-08-22

### Added
- Initial Oyster360 SaaS application with tenant-aware farm management APIs, dashboards, billing foundations, Docker deployment, and automated tests.

[Unreleased]: https://github.com/Inkithai/Oyster360/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Inkithai/Oyster360/releases/tag/v0.1.0
