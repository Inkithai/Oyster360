# Oyster360

**AI-powered, multi-tenant farm management and intelligence for commercial oyster mushroom cultivation.**

Oyster360 combines cultivation operations, environmental records, inventory, purchasing, harvest quality, analytics, AI assistance, subscription billing, and platform administration in one SaaS application. Each farm operates inside an isolated organization, and API authorization is enforced by both role and tenant.

> **Project status:** Active development. Core workflows, tenant isolation, authentication, billing infrastructure, background jobs, dashboards, Docker deployment, and automated tests are implemented. See [Roadmap Status](docs/ROADMAP_STATUS.md) for the current completion breakdown.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Application Modules](#application-modules)
- [Technology Stack](#technology-stack)
- [Complexity and Scale](#complexity-and-scale)
- [Quick Start with Docker](#quick-start-with-docker)
- [Environment Configuration](#environment-configuration)
- [Native Development Setup](#native-development-setup)
- [Database Migrations](#database-migrations)
- [Testing and Quality Checks](#testing-and-quality-checks)
- [Project Structure](#project-structure)
- [API and Service URLs](#api-and-service-urls)
- [Deployment Notes](#deployment-notes)
- [Additional Documentation](#additional-documentation)

## Features

### Farm and Cultivation Operations

- Organization and farm onboarding during user registration
- Multi-stage batch lifecycle: preparation, inoculation, colonization, fruiting, harvest, and completion
- Room and grow-space management
- Strain catalogue and cultivation metadata
- Versioned substrate recipes and recipe performance data
- Growth logs, health scores, images, and batch timelines
- Environmental temperature, humidity, and CO2 records
- Harvest recording, grading, quality scores, and revenue calculations

### Inventory and Purchasing

- Tenant-isolated inventory items and stock levels
- IN, OUT, and ADJUSTMENT transactions
- Low-stock detection and reorder thresholds
- Tenant-isolated suppliers and purchase orders
- Purchase order line items, totals, expected dates, and status tracking

### AI and Analytics

- Rule-based cultivation assistant that works without an external AI key
- Optional external AI provider integration
- Retrieval-augmented generation over user-owned knowledge documents
- Image inspection and contamination findings
- Yield prediction and expected harvest estimates
- Farm dashboards for production, success rate, environment, strains, and recipes
- SaaS analytics for growth, revenue, retention, usage, and AI activity

### Authentication and Security

- JWT access tokens and rotating refresh tokens
- Refresh-token revocation on logout, password change, and password reset
- Separate email-verification and password-reset token flows
- Password hashing with Argon2
- Multi-factor authentication service using TOTP and QR codes
- Role-based access control: `ADMIN`, `FARM_MANAGER`, `WORKER`, and `VIEWER`
- Organization-level query enforcement across tenant-owned resources
- Rate limiting, request IDs, CORS configuration, and security headers
- Audit-log and feature-flag models for platform administration

### Billing and Platform Operations

- Stripe customer and checkout session creation
- Server-controlled Stripe price IDs, preventing client-side plan/price substitution
- Verified Stripe webhooks with idempotent subscription synchronization
- Subscription lifecycle states and cancellation-at-period-end support
- Admin and SaaS analytics endpoints
- GDPR data export and account-data deletion endpoints

### Background Work and Deployment

- Redis caching
- Celery workers and Celery Beat scheduled jobs
- Background email, AI-analysis, token-cleanup, and report tasks
- Alembic database migrations
- Multi-stage, non-root Docker images
- Docker Compose services for frontend, API, PostgreSQL, Redis, migration, worker, and scheduler
- GitHub Actions checks for backend, frontend, Docker, and security scanning

## Architecture

Oyster360 is a **modular monolith** with independently deployable frontend and backend containers. Business domains are separated into API, service, schema, and persistence modules, while sharing one PostgreSQL database and one Redis deployment.

```mermaid
flowchart LR
    U[Browser / Farm User]
    S[Stripe]
    AI[External AI Provider]

    subgraph FE[Frontend Container]
        N[Next.js 16 App Router]
        Q[TanStack Query]
        UI[React 19 + Tailwind UI]
        N --- Q
        N --- UI
    end

    subgraph BE[Backend Container]
        F[FastAPI Routers]
        AUTH[Auth + RBAC + Tenant Enforcement]
        SV[Domain Services]
        RAG[AI / RAG / Analytics]
        ORM[SQLAlchemy Models]
        F --> AUTH
        AUTH --> SV
        SV --> RAG
        SV --> ORM
    end

    subgraph JOBS[Background Processing]
        CW[Celery Worker]
        CB[Celery Beat]
    end

    DB[(PostgreSQL / pgvector)]
    REDIS[(Redis Cache + Broker)]

    U -->|HTTPS| N
    N -->|same-origin /api proxy| F
    S -->|signed webhooks| F
    RAG -. optional API calls .-> AI
    ORM --> DB
    SV --> REDIS
    CB --> REDIS
    REDIS --> CW
    CW --> DB
```

### Request Flow

1. The browser calls a relative `/api/...` URL.
2. Next.js proxies that request to `BACKEND_URL`; browser code never needs to contact an internal container hostname.
3. FastAPI validates the request body with Pydantic.
4. Authentication dependencies decode the JWT, load the user, enforce the role, and resolve the active organization.
5. Domain services execute tenant-scoped SQLAlchemy queries.
6. PostgreSQL persists operational data; Redis provides caching and Celery transport.
7. Long-running or scheduled work is processed by Celery outside the API request.

### Data and Security Boundaries

- `organization_id` is the primary tenant boundary for farm-owned data.
- Parent resources are verified before nested resources such as inspections, logs, grades, and AI operations are accessed.
- The frontend role guard improves navigation and presentation, but the backend remains the authoritative security boundary.
- Stripe webhook payloads are accepted only after signature verification.
- RAG retrieval is restricted to documents owned by the authenticated user.

## Application Modules

The backend currently contains **24 API router modules, 27 model modules, and 28 service modules**. The frontend exposes **28 App Router pages**.

| Domain | Main backend modules | Main frontend areas | Responsibility |
|---|---|---|---|
| Authentication | `api/auth.py`, `core/security.py`, `core/dependencies.py` | `/login`, `/register`, `/forgot-password`, `/reset-password` | Accounts, JWTs, refresh rotation, password and verification flows |
| Organizations | `api/organizations.py`, `core/tenant.py`, `core/tenant_enforcer.py` | Organization-aware navigation | Tenant membership, active organization, query isolation |
| Cultivation | `api/batches.py`, `api/rooms.py`, `api/strains.py`, batch services | `/batches`, `/strains` | Batch lifecycle, rooms, strains, stage transitions |
| Recipes | `api/recipes.py`, `services/recipe_service.py` | `/recipes` | Substrate recipes, versions, and performance |
| Farm records | `api/growth_logs.py`, `api/environment.py`, `api/harvests.py` | Growth, environment, and harvest forms | Observations, sensor-style records, harvest completion |
| Quality | `api/inspections.py`, `api/harvest_grades.py` | `/analysis`, `/grading` | Image inspections, findings, grades, quality control |
| Inventory | `api/inventory.py`, `services/inventory_service.py` | `/inventory` | Stock, transactions, and low-stock reporting |
| Purchasing | `api/purchases.py`, `services/purchase_service.py` | `/purchases` | Suppliers, orders, line items, and totals |
| AI and RAG | `api/ai.py`, `api/assistant.py`, `services/ai/`, `rag_service.py` | `/ai`, `/assistant`, `/analysis` | Cultivation advice, document retrieval, image and yield analysis |
| Analytics | `api/analytics.py`, `api/saas_analytics.py` | `/dashboard`, `/analytics`, `/admin/analytics` | Farm KPIs and SaaS business metrics |
| Billing | `api/billing.py`, `api/webhooks.py`, Stripe and billing services | `/settings/subscription` | Checkout, subscriptions, webhook synchronization, cancellation |
| Administration | `api/admin.py`, `services/admin_service.py` | `/admin/dashboard` | System statistics, users, organizations, flags, and audit logs |
| Compliance | `api/compliance.py`, retention services | API-driven | GDPR export, deletion, and retention support |
| Background jobs | `core/celery.py`, `tasks/` | Status endpoint | Async analysis, email tasks, cleanup, and reports |

## Technology Stack

### Frontend

| Technology | Use |
|---|---|
| Next.js 16 | App Router, server rendering, production server, API proxy |
| React 19 + TypeScript | UI and type-safe application code |
| Tailwind CSS 4 | Styling and responsive layouts |
| Radix UI primitives | Accessible dialog, label, and select behavior |
| TanStack Query | Server-state fetching, caching, and mutations |
| React Hook Form + Zod | Form state and client-side validation |
| Chart.js + react-chartjs-2 | Analytics visualization |
| Zustand | Lightweight client-state support |
| Vitest + Testing Library | Component tests and coverage |
| Playwright | Browser-level end-to-end tests |
| ESLint | Static frontend checks |

### Backend

| Technology | Use |
|---|---|
| FastAPI | HTTP API and dependency injection |
| Pydantic v2 | Request, response, and settings validation |
| SQLAlchemy 2 | ORM and query layer |
| Alembic | Versioned database schema migrations |
| PostgreSQL 16 + pgvector | Relational storage and future vector search |
| PyJWT | Access-token creation and verification |
| Argon2 | Password hashing |
| Stripe SDK | Billing and webhook verification |
| Redis | Cache, Celery broker, and result backend |
| Celery | Background and scheduled task execution |
| PyOTP + QRCode | TOTP multi-factor authentication |
| Pytest + pytest-cov | Backend tests and coverage |

### Infrastructure

- Docker multi-stage builds
- Docker Compose for local and production service topology
- GitHub Actions CI/CD
- Trivy filesystem security scanning
- Uvicorn ASGI server

## Complexity and Scale

Oyster360 is **medium-to-high complexity** for a web application. It is more involved than a CRUD dashboard but intentionally less operationally complex than a distributed microservice system.

### Why the complexity is higher

- Every tenant-owned query must enforce organization boundaries.
- Four roles require different authorization levels.
- Authentication includes access tokens, refresh rotation, revocation, reset, verification, and MFA foundations.
- Stripe state must remain synchronized despite duplicate or out-of-order webhook delivery.
- Celery introduces asynchronous execution, retries, scheduling, and Redis dependencies.
- AI features combine farm data, user documents, optional external providers, and deterministic fallbacks.
- Production startup requires database migration ordering before API and worker startup.

### Current size indicators

- 24 FastAPI router modules
- 27 SQLAlchemy model modules
- 28 backend service modules
- 28 frontend page routes
- 22 backend/frontend unit-test files, plus Playwright specifications
- Up to 7 Docker Compose service roles: frontend, backend, migration, PostgreSQL, Redis, Celery worker, and Celery Beat

### Architectural trade-off

The modular-monolith design keeps transactions, development, and deployment understandable while preserving clear domain boundaries. If usage grows substantially, Celery workers, analytics, AI processing, and webhook ingestion are the most natural candidates to scale or extract independently.

## Quick Start with Docker

Docker is the recommended setup because it starts the complete service topology and runs migrations automatically.

### One-command bootstrap

From a fresh clone, `scripts/bootstrap.sh` (or `make bootstrap`) performs every setup step below in one shot: it creates `.env` from `.env.example`, generates a random `JWT_SECRET` when the placeholder is still in place, builds and starts the stack (which applies `alembic upgrade head` before the API boots), and waits for the API health check before printing the URLs.

```bash
./scripts/bootstrap.sh          # or: make bootstrap
./scripts/bootstrap.sh --seed   # additionally seed demo farm data
```

The script is idempotent and safe to re-run. `make help` lists the other developer shortcuts (`make verify`, `make test`, `make seed`, `make logs`).

### Prerequisites

- Git
- Docker Engine 24+ with Docker Compose v2
- Approximately 4 GB of free memory for all services

### 1. Clone the repository

```bash
git clone https://github.com/Inkithai/Oyster360.git
cd Oyster360
```

### 2. Create the environment file

```bash
cp .env.example .env
```

Generate a local JWT secret and place it in `.env`:

```bash
openssl rand -hex 32
```

For basic farm-management development, the default `AI_PROVIDER=rule-based` works without an AI key, and all Stripe variables may remain empty.

### 3. Build and start the application

Start the core web stack:

```bash
docker compose up --build
```

Docker Compose will:

1. Start PostgreSQL and Redis.
2. Build the backend image.
3. Apply `alembic upgrade head` before FastAPI starts.
4. Build and start the Next.js frontend.

Enable the optional background worker and scheduler profile when developing Celery tasks:

```bash
docker compose --profile workers up --build
```

To run the core stack in the background:

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f backend frontend
```

### 4. Create the first account

Open [http://localhost:3000/register](http://localhost:3000/register). Registration creates:

- a farm-manager user;
- an organization owned by that user; and
- the user's first farm.

Then sign in at [http://localhost:3000/login](http://localhost:3000/login).

### 5. Stop or reset the stack

```bash
# Stop containers but retain PostgreSQL data
docker compose down

# Stop containers and delete local database/Redis volumes
docker compose down -v
```

## Environment Configuration

Oyster360 does **not** require real AI or Stripe credentials for basic local cultivation workflows. Production deployments must replace every placeholder and use a secrets manager.

### Environment-file locations

| Run mode | File/location | Notes |
|---|---|---|
| Docker Compose | repository-root `.env` | Compose loads this automatically |
| Native backend | `backend/.env` | Pydantic Settings loads it when the backend runs from `backend/` |
| Native frontend | `frontend/.env.local` | Next.js loads it for development |
| Production | platform secrets or an external secrets manager | Never commit `.env.production` or `.env.local` files, even with placeholder values; keep production configuration in your platform secrets manager |

### Variables

| Variable | Required | Example | Purpose |
|---|---:|---|---|
| `DB_USER` | Docker | `oyster360` | PostgreSQL container user |
| `DB_PASSWORD` | Docker | `oyster360_secure_pass` | PostgreSQL container password; replace outside local development |
| `DB_NAME` | Docker | `oyster360` | PostgreSQL database name |
| `DATABASE_URL` | Backend | `postgresql://oyster360:...@localhost:5432/oyster360` | SQLAlchemy/Alembic connection URL |
| `JWT_SECRET` | Yes | output of `openssl rand -hex 32` | JWT signing key; minimum 32 characters |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `10080` | Access-token lifetime |
| `CORS_ORIGINS` | Yes in production | `https://app.example.com` | Comma-separated browser origins allowed by FastAPI |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Cache and Celery connection |
| `AI_PROVIDER` | No | `rule-based` | `rule-based`, `openai`, or another implemented provider |
| `OPENAI_API_KEY` | Only for OpenAI | `sk-...` | External AI access |
| `STRIPE_SECRET_KEY` | Only for billing | `sk_test_...` | Stripe server SDK key |
| `STRIPE_WEBHOOK_SECRET` | Only for billing | `whsec_...` | Stripe webhook signature secret |
| `STRIPE_PRICE_STARTER` | Only for billing | `price_...` | Server-approved Starter recurring price |
| `STRIPE_PRICE_PRO` | Only for billing | `price_...` | Server-approved Pro recurring price |
| `STRIPE_PRICE_ENTERPRISE` | Only for billing | `price_...` | Server-approved Enterprise recurring price |
| `NEXT_PUBLIC_API_URL` | No | empty | Empty uses the recommended same-origin `/api` proxy |
| `BACKEND_URL` | Frontend server | `http://localhost:8000` | Backend target used by the Next.js server |

### Minimal native backend `.env`

```env
DATABASE_URL=postgresql://oyster360:oyster360_secure_pass@localhost:5432/oyster360
JWT_SECRET=replace-with-at-least-32-random-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=http://localhost:3000
REDIS_URL=redis://localhost:6379/0
AI_PROVIDER=rule-based
```

### Enabling Stripe locally

1. Create recurring Stripe prices for Starter, Pro, and Enterprise.
2. Put their `price_...` IDs and a Stripe test secret key in `.env`.
3. Forward Stripe CLI events to the backend:

```bash
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

4. Copy the CLI's `whsec_...` value to `STRIPE_WEBHOOK_SECRET` and restart the backend.

Client requests select a plan, but the backend resolves the actual Stripe price from these server-side variables.

## Native Development Setup

Use this mode when developing the frontend or backend outside containers.

### Prerequisites

- Node.js 20.9+
- npm 10+
- Python 3.11+ (Python 3.12 is used by CI and Docker)
- PostgreSQL 16 and Redis 7, or Docker for those dependencies

### 1. Start PostgreSQL and Redis

```bash
docker compose up -d postgres redis
```

### 2. Configure and run the backend

```bash
cp backend/.env.example backend/.env
cd backend

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.lock

alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

In separate terminals, background processing can be started with:

```bash
cd backend
source .venv/bin/activate
celery -A app.core.celery:celery_app worker --loglevel=info
```

```bash
cd backend
source .venv/bin/activate
celery -A app.core.celery:celery_app beat --loglevel=info
```

### 3. Configure and run the frontend

```bash
cd frontend
npm ci

cat > .env.local <<'EOF'
NEXT_PUBLIC_API_URL=
BACKEND_URL=http://localhost:8000
EOF

npm run dev -- --hostname 0.0.0.0
```

The frontend is now available at [http://localhost:3000](http://localhost:3000).

## Database Migrations

Alembic is the source of truth for production schema changes.

```bash
cd backend

# Apply all migrations
alembic upgrade head

# Show the current revision
alembic current

# Create a migration after changing SQLAlchemy models
alembic revision --autogenerate -m "describe the schema change"

# Review generated migration code before applying it
alembic upgrade head
```

The local backend container applies migrations before starting FastAPI. The production Compose topology uses a dedicated one-time `migrate` service before API and worker replicas start.

## Testing and Quality Checks

### Backend

```bash
cd backend
pip install -r requirements.lock
pytest -m "not integration"                     # fast unit lane, skips end-to-end flows
pytest --cov=app --cov-report=term-missing       # full suite with coverage
flake8 app tests --count --select=E9,F63,F7,F82 --show-source --statistics
```

The backend suite uses an isolated in-memory SQLite database for API, authentication, model-registry, integration, and tenant-security tests. `pytest` needs no running PostgreSQL, Redis, external account, or manually-created environment file: `conftest.py` blocks outbound HTTP, stubs every Stripe client call, and builds a fresh schema per test. The end-to-end lifecycle tests in `tests/test_integration.py` are marked `integration`, so `pytest -m "not integration"` gives a seconds-long feedback loop; CI runs that lane first and the compose stack still exercises the full suite.

### Frontend

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
npm test
npm run test:coverage    # Vitest with lines/statements/functions >= 70%, branches >= 60%
npm run build
```

### Browser tests

```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

Every browser spec fulfills its API routes at the network level with `page.route` (login, dashboard analytics), so the Playwright suite runs against the Next.js development server without a live backend or seeded database.

### Dependency security

```bash
cd frontend
npm audit --audit-level=high
```

## Project Structure

```text
Oyster360/
├── backend/
│   ├── alembic/                 # Migration environment and revisions
│   ├── app/
│   │   ├── api/                 # FastAPI route modules
│   │   ├── core/                # Settings, auth, tenancy, Celery, middleware
│   │   ├── database/            # Engine, sessions, optional seed helpers
│   │   ├── models/              # SQLAlchemy entities
│   │   ├── repositories/        # Tenant-aware repository helpers
│   │   ├── schemas/             # Pydantic request/response DTOs
│   │   ├── services/            # Domain, billing, AI, analytics logic
│   │   └── tasks/               # Celery tasks
│   ├── tests/                   # Pytest suite
│   ├── Dockerfile
│   ├── requirements-runtime.txt # Runtime-only container dependencies
│   └── requirements.txt         # Local/CI dependencies
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages and layouts
│   │   ├── components/          # Layout, guards, and reusable UI
│   │   └── lib/                 # API client, validation, utilities
│   ├── tests/e2e/               # Playwright specifications
│   ├── Dockerfile
│   ├── eslint.config.mjs
│   ├── playwright.config.ts
│   └── vitest.config.ts
├── docs/                        # Product, API, setup, architecture, deployment docs
├── scripts/                     # Bootstrap, deployment, and backup scripts
├── Makefile                     # Developer shortcuts (make help)
├── docker-compose.yml           # Local complete stack
├── docker-compose.prod.yml      # Production-oriented stack
└── .env.example                 # Safe configuration template
```

## API and Service URLs

After local startup:

| Service | URL |
|---|---|
| Web application | http://localhost:3000 |
| FastAPI root | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| OpenAPI JSON | http://localhost:8000/openapi.json |
| Health | http://localhost:8000/health |
| Readiness | http://localhost:8000/ready |
| Liveness | http://localhost:8000/live |
| Celery status | http://localhost:8000/celery-status |

Main API families are mounted under `/api/auth`, `/api/batches`, `/api/recipes`, `/api/inventory`, `/api/purchases`, `/api/analytics`, `/api/assistant`, `/api/billing`, `/api/admin`, and `/api/compliance`.

## Deployment Notes

- Use `docker-compose.prod.yml` as a reference, not as a substitute for environment-specific infrastructure review.
- Store database, JWT, Stripe, email, AI, and cloud credentials in a secrets manager.
- Terminate TLS at a trusted reverse proxy or managed load balancer.
- Run the Alembic migration job once before rolling out new API/worker replicas.
- Keep `NEXT_PUBLIC_API_URL` empty when the frontend proxies to an internal backend service.
- Set `BACKEND_URL` to the backend's private service URL, such as `http://backend:8000`.
- Configure Stripe to send signed events to `/api/webhooks/stripe`.
- Back up PostgreSQL and test restoration procedures before production use.

## Additional Documentation

- [Setup Guide](docs/SETUP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [Product Overview](docs/PRODUCT_OVERVIEW.md)
- [User Guide](docs/USER_GUIDE.md)
- [Roadmap Status](docs/ROADMAP_STATUS.md)

## Reproducible Dependencies

Both package ecosystems have committed lockfiles. Frontend installs must use `npm ci` with `frontend/package-lock.json`. Backend local development and CI install `backend/requirements.lock` (also published as `backend/uv.lock` and declared in the root `pyproject.toml`), which pins direct and transitive Python dependencies. The root `requirements.txt` and `pyproject.toml` exist so dependency scanners that only inspect the repository root still see the runtime manifest.

To intentionally refresh the backend lock in a clean virtual environment:

```bash
cd backend
python -m venv .lock-venv
. .lock-venv/bin/activate
python -m pip install --upgrade pip pip-tools
pip-compile --no-emit-index-url --strip-extras \
  --output-file=requirements.lock requirements.txt
pip install -r requirements.lock
pytest
```

Review the resulting dependency diff and security scan before committing it. Dependabot checks npm and pip dependencies weekly via `.github/dependabot.yml`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, test gates, commit conventions, and the pull-request checklist. User-visible changes are recorded in [CHANGELOG.md](CHANGELOG.md). Keep each feature or fix in a focused Conventional Commit together with the tests that prove it.

## License

All rights reserved.

---

**Built for commercial oyster mushroom farms.**
