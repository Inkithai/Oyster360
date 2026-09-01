# Oyster360 Architecture

## System Overview

Oyster360 follows a modern three-tier architecture:

1. **Presentation Layer** — Next.js 16 App Router, React 19, and TanStack Query
2. **Application Layer** — FastAPI modular monolith with domain services and Celery workers
3. **Data Layer** — PostgreSQL 16 + pgvector, with Redis for caching and task transport

## Frontend Architecture

- **Framework**: Next.js 16 (App Router)
- **State Management**: TanStack Query (server state) + Zustand (client state)
- **Forms**: React Hook Form + Zod
- **Styling**: Tailwind CSS + shadcn/ui
- **Charts**: Recharts

## Backend Architecture

- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Authentication**: JWT
- **AI Layer**: Abstract Provider Pattern

### AI Architecture

```
AIProvider (Abstract)
    ├── OpenAIProvider
    ├── GeminiProvider
    └── RuleBasedProvider (Fallback)
```

## Database Schema

### Core Entities
- `organizations` (future multi-tenant)
- `users`
- `farms`
- `rooms`
- `strains`
- `recipes` + `recipe_versions`
- `batches`
- `growth_logs`
- `environment_logs`
- `harvests`
- `inventory_items`
- `suppliers`
- `purchase_orders`

### AI Entities
- `image_inspections`
- `inspection_findings`
- `yield_predictions`
- `ai_conversations`
- `knowledge_documents`
- `document_chunks`

## Key Design Patterns

- **Repository Pattern** (services)
- **Dependency Injection** (FastAPI Depends)
- **Abstract Factory** (AI Providers)
- **DTO Pattern** (Pydantic schemas)

## Security

- JWT Authentication
- Role-Based Access Control (RBAC)
- Input validation on all endpoints
- CORS configuration

## Deployment Architecture

```
Vercel (Frontend)
    ↓
Railway / Cloud Run (Backend)
    ↓
Neon / Supabase (Database)
```

---

*Last Updated: July 2026*