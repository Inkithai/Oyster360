# Contributing to Oyster360

Thank you for improving Oyster360. Keep changes focused, reviewable, and proven by tests.

## Development setup

1. Fork and clone the repository.
2. Copy `.env.example` to `.env` for Docker development. Never commit environment files.
3. Follow the fresh-clone instructions in [README.md](README.md).
4. Create a short-lived branch from `main`.

## Change discipline

- Use Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`).
- Keep one concern per commit. Put the behavior change and the tests proving it in the same commit.
- Do not combine mass formatting, generated files, and feature work.
- Add a changelog entry under `Unreleased` for user-visible changes.
- Update API and environment documentation when contracts change.

## Required checks

Run these before opening a pull request. `make verify` from the repository root runs the same backend and frontend gates in one command:

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.lock
flake8 app tests --count --select=E9,F63,F7,F82 --show-source --statistics
pytest -m "not integration"      # seconds-long fast lane
pytest --cov=app --cov-fail-under=60

cd ../frontend
npm ci
npm run lint
npm run typecheck
npm test -- --coverage
npm run build
```

For infrastructure changes, also run:

```bash
docker compose config --quiet
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test-runner
docker compose -f docker-compose.test.yml down --volumes
```

## Tests

- Backend tests use an in-memory SQLite database and block Stripe/OpenAI network access.
- Frontend behavior tests use Vitest and Testing Library; browser journeys use Playwright.
- Assert externally visible behavior rather than implementation details.
- Every bug fix should include a regression test.
- Do not lower a coverage threshold to make a change pass.

## Pull requests

Include a concise problem statement, solution summary, risk notes, screenshots for UI changes, and the exact checks run. Keep PRs small enough to review independently. CI must pass before merge.

## Security

Do not open public issues containing vulnerabilities, customer data, tokens, or credentials. Report sensitive findings privately to the repository maintainers. Use fake values in tests and examples.
