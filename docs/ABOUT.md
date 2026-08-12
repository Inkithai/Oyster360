# Oyster360 - About the Application

## Overview

**Oyster360** is a production-grade, AI-powered SaaS platform designed specifically for commercial oyster mushroom cultivation. It combines traditional farm operations management with intelligent AI capabilities to help farms increase yield, reduce contamination, and optimize growing conditions.

## Core Value Proposition

Oyster360 solves the three biggest challenges in commercial oyster mushroom farming:

1. **Lack of visibility** into batch performance and environmental conditions
2. **Inconsistent decision-making** based on experience rather than data
3. **Late detection** of contamination and growth issues

## Key Features

### Production Management
- Full cultivation lifecycle tracking (Preparation → Harvest)
- Substrate recipe versioning and performance comparison
- Environmental monitoring and logging
- Growth log and timeline tracking

### AI-Powered Intelligence
- **Cultivation Assistant**: RAG-based chatbot that answers farm-specific questions
- **Image Analysis**: AI-powered quality inspection for mushroom health and contamination detection
- **Yield Prediction**: Data-driven harvest forecasting

### Operations
- Inventory management
- Supplier and purchase order tracking
- Harvest grading and quality control
- Worker task management

## Technology Stack

### Frontend
- **Next.js 15** (App Router) + TypeScript
- **Tailwind CSS** + **shadcn/ui**
- **TanStack Query** for data fetching
- **React Hook Form** + **Zod** for forms
- **Recharts** for visualizations

### Backend
- **FastAPI** (Python)
- **SQLAlchemy 2.0** + **Alembic**
- **PostgreSQL** + **pgvector**
- **Pydantic v2**

### AI
- Abstract AI Provider architecture
- Support for OpenAI, Gemini, Ollama
- Rule-based fallback system
- RAG (Retrieval-Augmented Generation) for cultivation knowledge

### Infrastructure
- Docker + Docker Compose
- GitHub Actions CI/CD
- Multi-stage Docker builds

## Architecture Diagram

```
┌─────────────────────┐
│   Next.js Frontend  │
│   (Oyster360 UI)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   FastAPI Backend   │
│   - Auth            │
│   - Business Logic  │
│   - AI Services     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   PostgreSQL        │
│   + pgvector        │
└─────────────────────┘
```

## Target Users

- **Farm Owners**: Overview, analytics, decision support
- **Production Managers**: Batch management, recipes, quality control
- **Farm Workers**: Daily tasks, growth logs, inspections

## Competitive Advantage

Unlike generic farm management tools, Oyster360 is purpose-built for oyster mushrooms with:

- Deep domain knowledge of *Pleurotus* cultivation
- AI specifically trained on mushroom farming data
- Mobile-first design for field workers
- Multi-tenant architecture for farming companies

---

**Oyster360** — *Monitor. Predict. Optimize.*