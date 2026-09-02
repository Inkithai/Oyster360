# Oyster360 developer shortcuts. The same commands live in README.md; run
# `make help` to list targets.
.PHONY: help ci-local deps-check deps-sync sync-deps setup bootstrap fresh-start up down logs ps migrate seed verify quality test test-unit test-backend test-frontend test-integration test-e2e lint

setup: ## Prepare a fresh clone (creates .env and starts the Docker stack)
	./scripts/bootstrap.sh

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

bootstrap: ## Fresh clone -> running app (env, build, migrate, start; --seed supported)
	./scripts/bootstrap.sh

fresh-start: ## Never-seen-the-repo path: .env, databases, migrations, API + web
	@test -f .env || cp .env.example .env
	docker compose up -d postgres redis
	docker compose up -d --wait postgres redis || sleep 10
	docker compose build backend
	docker compose run --rm --no-deps backend alembic upgrade head
	docker compose up -d backend frontend
	@echo
	@echo "Databases migrated; backend and frontend are starting."
	@echo "Expected backend log line:  Uvicorn running on 0.0.0.0:8000"
	@echo "Frontend:  http://localhost:3000"
	@echo "Health:    http://localhost:8000/health"
	@echo "Follow logs: docker compose logs -f backend frontend"

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

ci-local: ## Reproduce every CI gate from a fresh clone (installs deps, no Docker needed)
	./scripts/ci-local.sh

deps-check: ## Verify dependency manifests and lockfiles agree
	python3 scripts/check_dependency_sync.py

deps-sync: ## Synchronize dependency manifests and regenerate lockfiles
	python3 scripts/sync_dependencies.py

sync-deps: deps-sync ## Alias for deps-sync

verify: ## Run the local checks CI enforces (assumes deps are already installed)
	python3 scripts/check_dependency_sync.py
	cd backend && flake8 app tests --count --show-source --statistics --exclude=.venv,__pycache__,alembic/versions
	cd backend && mypy app
	cd backend && pytest -m "not integration" --cov=app --cov-report=term-missing --cov-fail-under=80
	cd frontend && npm run lint && npm run typecheck
	cd frontend && npm run test:coverage

quality: verify ## Alias for the complete offline quality gate

test: test-unit ## Run deterministic unit tests (no network, database, or API keys)

test-unit: ## Fast offline lane: backend unit tests + frontend tests, zero external services
	cd backend && pytest -m "not integration" -q
	cd frontend && npm test

test-backend: ## Run deterministic backend tests only
	cd backend && pytest -m "not integration" -q

test-integration: ## Run integration tests (requires Docker test services)
	trap 'docker compose -f docker-compose.test.yml down --volumes --remove-orphans' EXIT; docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test-runner

test-frontend: ## Run frontend unit tests
	cd frontend && npm test

test-e2e: ## Run Playwright browser tests (installs Chromium on first use)
	cd frontend && npx playwright install chromium
	cd frontend && npm run test:e2e

lint: ## Lint backend and frontend
	cd backend && flake8 app tests --count --select=E9,F63,F7,F82 --show-source --statistics
	cd frontend && npm run lint
