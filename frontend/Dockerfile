ARG PYTHON_VERSION=3.11-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install uv (fast dependency manager)
RUN pip install uv

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock /code/

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy full project
COPY . /code

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI (IMPORTANT: adjust if your entrypoint differs)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
