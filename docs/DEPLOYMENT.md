# Oyster360 - Deployment Guide

## Frontend Deployment (Vercel)

### Steps

1. Connect your GitHub repository to Vercel
2. Set environment variables:
   - `NEXT_PUBLIC_API_URL`
3. Deploy

### Recommended Settings
- Framework: Next.js
- Build Command: `npm run build`
- Output Directory: `.next`

---

## Backend Deployment (Railway / Render)

### Environment Variables Required

```env
DATABASE_URL=postgresql://...
JWT_SECRET=...
OPENAI_API_KEY=...
AI_PROVIDER=openai
```

### Health Check Endpoint

```
GET /health
```

---

## Database (Neon / Supabase)

1. Create PostgreSQL database with pgvector extension
2. Run migrations:
   ```bash
   alembic upgrade head
   ```
3. Seed demo data (optional):
   ```bash
   python -m app.database.seed
   ```

---

## Docker Production Deployment

```bash
docker compose -f docker-compose.prod.yml up -d
```

---

**Last Updated**: July 2026