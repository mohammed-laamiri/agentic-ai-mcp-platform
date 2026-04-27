# Build stage
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Copy dependency files first (better caching)
COPY pyproject.toml uv.lock ./

# Copy full backend + frontend (workspace needs it)
COPY app ./app
COPY frontend ./frontend

# Install dependencies into venv
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Ensure venv is used
ENV PATH="/app/.venv/bin:$PATH"

# Copy app code
COPY app ./app
COPY pyproject.toml ./

# IMPORTANT: expose Fly port (must match fly.toml internal_port)
EXPOSE 8000

# Start app (use uvicorn from venv)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]