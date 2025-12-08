# Build dependencies into a prefix that can be copied to the non-root runtime.
FROM python:3.12-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-runtime.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements-runtime.txt

FROM python:3.12-slim AS runtime

WORKDIR /app
RUN groupadd -r oyster360 && useradd -r -g oyster360 oyster360

COPY --from=builder /install /usr/local
COPY --chown=oyster360:oyster360 . .

USER oyster360
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)"]

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
