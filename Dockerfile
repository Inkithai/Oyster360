# syntax=docker/dockerfile:1
#
# Root build for the Oyster360 FastAPI API service.
#
# This is the single deployable used by docker-compose.yml for the `backend`
# service. The frontend (Next.js) is built and served via frontend/Dockerfile.
# Build from the repository root:
#     docker build -t oyster360-api .
FROM python:3.12-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements-runtime.txt ./requirements-runtime.txt
RUN pip install --prefix=/install --no-cache-dir -r requirements-runtime.txt

FROM python:3.12-slim AS runtime

WORKDIR /app
RUN groupadd -r oyster360 && useradd -r -g oyster360 oyster360

COPY --from=builder /install /usr/local
COPY --chown=oyster360:oyster360 backend/alembic.ini ./alembic.ini
COPY --chown=oyster360:oyster360 backend/alembic ./alembic
COPY --chown=oyster360:oyster360 backend/app ./app

USER oyster360
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)"]

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
