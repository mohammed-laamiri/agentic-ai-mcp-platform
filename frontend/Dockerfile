ARG PYTHON_VERSION=3.11-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install system dependencies
RUN pip install --upgrade pip

# Copy dependency files first (better caching)
COPY pyproject.toml /code/

# Install dependencies safely (production-ready approach)
RUN pip install django gunicorn python-decouple

# Copy full project
COPY . /code

# Collect static files (FAIL LOUD if broken)
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run Django with Gunicorn (production)
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]