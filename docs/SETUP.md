# Oyster360 - Setup Guide

## Quick Start

On a machine that has never cloned this repository:

```bash
git clone https://github.com/Inkithai/Oyster360.git
cd Oyster360
make fresh-start
```

That target copies `.env.example` to `.env`, starts PostgreSQL and Redis, runs `alembic upgrade head`, and starts the API and frontend. The backend is ready when its logs show:

```text
Uvicorn running on 0.0.0.0:8000
```

**Access**:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- Health: http://localhost:8000/health

**Demo Login** (after `make bootstrap --seed` or `./scripts/bootstrap.sh --seed`):
```
Email: admin@myco.farm
Password: admin123
```

Equivalent manual Compose flow (migrations still run automatically in the backend container):

```bash
cp .env.example .env
docker compose up --build
```

## Environment Variables

```env
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret
OPENAI_API_KEY=sk-...          # Optional
AI_PROVIDER=rule-based         # openai | gemini | rule-based
```

## Production Deployment

- **Frontend**: Vercel
- **Backend**: Railway / Render / Cloud Run
- **Database**: Neon / Supabase

---

**Last Updated**: July 2026