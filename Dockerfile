# syntax=docker/dockerfile:1
# Multi-stage Dockerfile for Órbita — FastAPI API + Next.js frontend

# ── Python build stage ───────────────────────────────────────────────────────
FROM python:3.11-slim AS py-builder

WORKDIR /build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY pyproject.toml .
COPY README.md .

RUN uv sync --no-dev --no-install-project

COPY src/ src/
COPY ingest/ ingest/
COPY api/ api/
COPY eval/ eval/
RUN uv sync --no-dev

# ── Node build stage ────────────────────────────────────────────────────────
FROM node:22-slim AS node-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# ── Runtime stage ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl nodejs npm && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY --from=py-builder /build/.venv /app/.venv

COPY src/ src/
COPY api/ api/
COPY ingest/ ingest/
COPY eval/ eval/
COPY config/ config/
COPY .env.example .env

COPY --from=node-builder /frontend/.next frontend/.next
COPY --from=node-builder /frontend/node_modules frontend/node_modules
COPY --from=node-builder /frontend/package.json frontend/package.json
COPY --from=node-builder /frontend/next.config.ts frontend/next.config.ts

RUN mkdir -p data/raw data/processed data/faiss_index logs eval/results

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8001 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port 8001 & cd frontend && npx next start --port 3000 --hostname 0.0.0.0"]
