# Oyster360 - Setup Guide

## Quick Start

```bash
git clone <repository>
cd oyster360
docker compose up --build
```

**Access**:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

**Demo Login**:
```
Email: admin@myco.farm
Password: admin123
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