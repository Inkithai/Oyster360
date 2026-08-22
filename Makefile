# Oyster360 developer shortcuts. The same commands live in README.md; run
# `make help` to list targets.
.PHONY: help bootstrap up down logs ps migrate seed verify test test-backend test-frontend test-e2e lint

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

bootstrap: ## Fresh clone -> running app (env, build, migrate, start; --seed supported)
	./scripts/bootstrap.sh

up: ## Start the full stack in the background
	docker compose up -d

down: ## Stop the stack (keep data)
	docker compose down

logs: ## Follow backend and frontend logs
	docker compose logs -f backend frontend

ps: ## Show compose service status
	docker compose ps

migrate: ## Apply all Alembic migrations inside the running backend
	docker compose exec -T backend alembic upgrade head

seed: ## Seed demo farm data inside the running backend
	docker compose exec -T backend python -c "from app.database.database import SessionLocal; from app.services.seed_data import seed_demo_data; seed_demo_data(SessionLocal())"

verify: ## Run the local checks CI enforces (no Docker or live services needed)
	cd backend && pytest --cov=app --cov-report=term-missing --cov-fail-under=60
	cd frontend && npm run lint && npm run typecheck
	cd frontend && npm run test:coverage

test: test-backend test-frontend ## Run backend and frontend test suites

test-unit: ## Fast offline lane: backend unit tests + frontend tests, zero external services
	cd backend && pytest -m "not integration" -q
	cd frontend && npm test

test-backend: ## Run the full backend suite (in-memory SQLite; no services needed)
	cd backend && pytest

test-frontend: ## Run frontend unit tests
	cd frontend && npm test

test-e2e: ## Run Playwright browser tests (installs Chromium on first use)
	cd frontend && npx playwright install chromium
	cd frontend && npm run test:e2e

lint: ## Lint backend and frontend
	cd backend && flake8 app tests --count --select=E9,F63,F7,F82 --show-source --statistics
	cd frontend && npm run lint
