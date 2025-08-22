# HyperAI Builder - Production Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Base Python image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

# Stage 2: Dependencies
FROM base as dependencies

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-dev

# Stage 3: Production image
FROM base as production

# Copy dependencies from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Set ownership
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "hyperai_builder.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 4: Development image
FROM base as development

# Install development dependencies
COPY pyproject.toml poetry.lock* ./
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install

# Copy application code
COPY . .

# Set ownership
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose ports
EXPOSE 8000 8501

# Default command for development
CMD ["streamlit", "run", "hyperai_builder/frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]