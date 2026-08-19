# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 1.x     | Yes       |
| 0.x     | Best effort |

## Reporting a vulnerability

Do not open a public GitHub issue for security problems.

Email the maintainers listed in [AUTHORS.md](AUTHORS.md) or use GitHub's private vulnerability reporting on this repository. Include:

- A description of the issue and its impact
- Reproduction steps or a proof of concept
- Affected version / commit SHA
- Any suggested fix

You should receive an acknowledgement within 5 business days. Please give us a reasonable window to patch before any public disclosure.

## What we consider in-scope

- Authentication, session, and tenant-isolation bypasses
- Injection, SSRF, or privilege escalation in the API
- Secret leakage in logs, images, or committed files
- Dependency vulnerabilities with a working exploit path

## What we do already

- Passwords hashed with Argon2
- JWT access tokens with rotating, revocable refresh tokens
- Organization-scoped queries for tenant-owned resources
- Stripe webhook signature verification
- No committed `.env` files; templates live in `.env.example`
- CI dependency scanning (Trivy) and Dependabot
- Input validation with Pydantic (API) and Zod (forms)

## Secrets

Never commit API keys, JWT secrets, Stripe credentials, or production connection strings. Use a secrets manager in production. Local development uses `.env` copied from `.env.example`.
