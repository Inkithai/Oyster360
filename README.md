# Oyster360

**AI-Powered Oyster Mushroom Farm Management & Intelligence Platform**

Oyster360 is a production-ready B2B SaaS platform built for commercial oyster mushroom cultivation. It combines traditional farm operations with AI-powered insights to help farms increase yield, reduce contamination, and optimize growing conditions.

## Features

### Core Operations
- Full cultivation lifecycle management
- Substrate recipe versioning & performance tracking
- Inventory management
- Supplier & purchase order management
- Harvest grading & quality control

### AI & Analytics
- AI Cultivation Assistant (RAG-powered)
- AI Image Analysis for quality inspection
- Yield prediction
- Environmental monitoring & analytics
- Production dashboards

### Platform
- Role-based access control
- Mobile responsive design
- Professional SaaS interface

## Tech Stack

**Frontend**
- Next.js 15 (App Router) + TypeScript
- Tailwind CSS + shadcn/ui
- TanStack Query
- Recharts
- React Hook Form + Zod

**Backend**
- FastAPI
- SQLAlchemy 2.0 + Alembic
- PostgreSQL + pgvector
- Pydantic v2
- JWT Authentication

**Infrastructure**
- Docker + Docker Compose
- GitHub Actions CI/CD

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### Local Development

```bash
git clone <repository>
cd oyster360

# Start all services
docker compose up --build
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

### Demo Credentials
```
Email: admin@myco.farm
Password: admin123
```

## Project Structure

```
oyster360/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API routers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── core/           # Configuration
│   └── alembic/            # Database migrations
├── frontend/               # Next.js application
│   └── src/
│       ├── app/            # Pages & routes
│       ├── components/     # UI components
│       └── lib/            # Utilities
└── docker-compose.yml
```

## Environment Variables

Copy `.env.example` and configure:

```env
DATABASE_URL=postgresql://...
JWT_SECRET=your-secret-key
```

## Deployment

The application is containerized and ready for deployment.

**Recommended Stack:**
- Frontend → Vercel
- Backend → Railway / Render / Fly.io
- Database → Neon / Supabase

## Roadmap

- Mobile application for workers
- IoT sensor integration (ESP32/MQTT)
- Advanced machine learning models
- Multi-tenant support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

All rights reserved.

---

**Built for commercial oyster mushroom farms.**