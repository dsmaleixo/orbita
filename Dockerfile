# syntax=docker/dockerfile:1
# Multi-stage Dockerfile for Órbita — uses uv for fast dependency installation

# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy dependency manifest first (layer cache)
COPY pyproject.toml .
COPY README.md .

# Install dependencies into /build/.venv
RUN uv sync --no-dev --no-install-project

# Copy source and install the project itself
COPY src/ src/
COPY ingest/ ingest/
COPY app/ app/
COPY eval/ eval/
RUN uv sync --no-dev

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy uv binary and the pre-built virtualenv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY --from=builder /build/.venv /app/.venv

# Copy application code
COPY src/ src/
COPY app/ app/
COPY ingest/ ingest/
COPY eval/ eval/
COPY mcp_allowlist.yaml .
COPY .env.example .env

# Create necessary directories
RUN mkdir -p data/raw data/processed data/faiss_index logs eval/results

# Always use the virtualenv
ENV PATH="/app/.venv/bin:$PATH"

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Entry point
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
