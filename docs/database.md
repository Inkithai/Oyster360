# Oyster360 - Database Documentation

## Overview

MycoFarm AI uses PostgreSQL with SQLAlchemy 2.0 and Alembic for migrations.

## Entity Relationships

```
User
  └── Farm (owner)
       ├── Room
       │    └── EnvironmentLog
       │
       ├── Recipe
       │    └── RecipeVersion
       │
       └── Batch
            ├── GrowBag
            ├── GrowthLog
            ├── Harvest
            └── AIInsight
```

## Key Tables

### Core Production Tables

- **users** — Authentication and roles
- **farms** — Farm information
- **rooms** — Growing rooms with environmental targets
- **strains** — Oyster mushroom strains
- **recipes** + **recipe_versions** — Substrate formulations
- **batches** — Production batches with lifecycle stages

### Logging Tables

- **growth_logs** — Daily observations and health scores
- **environment_logs** — Temperature, humidity, CO2 readings
- **harvests** — Harvest records with quality and revenue

### Future Tables

- **ai_insights** — AI recommendations
- **sensors** — IoT device support

## Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one revision
alembic downgrade -1
```

## Seed Data

Run the seed script to populate demo data:

```bash
cd backend
python -m app.database.seed
```

## Reset Database

```bash
docker compose down -v
docker compose up --build
alembic upgrade head
python -m app.database.seed
```