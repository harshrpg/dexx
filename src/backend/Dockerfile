# syntax=docker/dockerfile:1

# -------- Builder stage --------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	POETRY_VERSION=1.8.3

WORKDIR /app

# System build dependencies (removed in final image since multi-stage)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		build-essential \
		git \
		curl \
		pkg-config \
	&& rm -rf /var/lib/apt/lists/*

# Create virtual environment and install Poetry
RUN python -m venv /venv \
	&& /venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel \
	&& /venv/bin/pip install --no-cache-dir poetry==${POETRY_VERSION}

# Leverage layer caching: copy only dependency manifests first
COPY pyproject.toml poetry.lock ./

# Install only main (non-dev) dependencies into the venv
ENV PATH="/venv/bin:$PATH" \
	VIRTUAL_ENV="/venv"
RUN poetry config virtualenvs.create false \
	&& poetry install --no-interaction --no-ansi --only main

# Copy application code
COPY app ./app


# -------- Runtime stage --------
FROM python:3.12-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	VIRTUAL_ENV="/venv" \
	PATH="/venv/bin:$PATH" \
	PORT=8000 \
	WORKERS=4

WORKDIR /app

# Minimal runtime dependencies (common for scientific stacks and TLS)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		ca-certificates \
		libgomp1 \
	&& rm -rf /var/lib/apt/lists/*

# Copy the virtual environment and application
COPY --from=builder /venv /venv
COPY --from=builder /app/app ./app

# Create a non-root user for security and switch to it
RUN useradd -m appuser
USER appuser

EXPOSE 8000

# Start the server with Gunicorn + Uvicorn worker (honors PORT/WORKERS)
CMD ["sh", "-c", "exec gunicorn -k uvicorn.workers.UvicornWorker app.main:app --workers ${WORKERS} --bind 0.0.0.0:${PORT}"] 