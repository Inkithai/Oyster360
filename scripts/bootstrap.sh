#!/usr/bin/env bash
#
# One-command bootstrap for a fresh clone of Oyster360.
#
#   ./scripts/bootstrap.sh           build, migrate, start, wait for health
#   ./scripts/bootstrap.sh --seed    ... and seed demo farm data afterward
#
# Every step is idempotent, so the script is also safe to re-run.
set -euo pipefail

cd "$(dirname "$0")/.."

command -v docker >/dev/null 2>&1 || {
  echo "docker is required. Install Docker Engine 24+ with Compose v2." >&2
  exit 1
}

# 1. Environment file --------------------------------------------------------
if [ ! -f .env ]; then
  cp .env.example .env
  echo "[1/4] Created .env from .env.example"
else
  echo "[1/4] Reusing existing .env"
fi

# 2. Random JWT secret if the placeholder is still in place ------------------
if grep -q "^JWT_SECRET=replace-this-with-a-random-secret" .env; then
  if command -v openssl >/dev/null 2>&1; then
    secret="$(openssl rand -hex 32)"
    sed -i.bak "s|^JWT_SECRET=.*|JWT_SECRET=${secret}|" .env && rm -f .env.bak
    echo "[2/4] Generated a random JWT_SECRET"
  else
    echo "[2/4] WARNING: openssl not found; set JWT_SECRET in .env manually." >&2
  fi
else
  echo "[2/4] JWT_SECRET already configured"
fi

# 3. Build and start (the backend container runs alembic upgrade head first) -
echo "[3/4] Building and starting the stack (first build takes a few minutes)..."
docker compose up --build -d

# 4. Wait for the API health check ------------------------------------------
echo "[4/4] Waiting for http://localhost:8000/health ..."
healthy=0
for _ in $(seq 1 90); do
  if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    healthy=1
    break
  fi
  sleep 2
done
if [ "$healthy" -ne 1 ]; then
  echo "API did not become healthy in time. Inspect logs with:" >&2
  echo "  docker compose logs -f backend" >&2
  exit 1
fi

# Optional: demo data --------------------------------------------------------
if [ "${1:-}" = "--seed" ]; then
  echo "Seeding demo farm data..."
  docker compose exec -T backend python - <<'PY'
from app.database.database import SessionLocal
from app.services.seed_data import seed_demo_data

seed_demo_data(SessionLocal())
PY
  echo "Demo login: admin@myco.farm / admin123"
fi

echo
echo "Oyster360 is up:"
echo "  Frontend      http://localhost:3000"
echo "  API docs      http://localhost:8000/docs"
echo "  Health check  http://localhost:8000/health"
echo
echo "Stop with:            docker compose down"
echo "Reset databases too:  docker compose down -v"
