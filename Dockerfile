# 1. Base Image (Using 3.12 for stability)
FROM python:3.12-slim-bookworm AS base

# 2. Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Install System Dependencies (Required for psycopg2)
# Consolidate RUN commands for smaller image size
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Set Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Set default port to 8080 as a fallback, though Cloud Run injects the PORT env var
    PORT=8080

# 5. Set Work Directory and venv location
WORKDIR /app
# uv creates the venv here. Add it to PATH.
ENV PATH="/app/.venv/bin:$PATH"

# 6. Install Dependencies (Caching Layer)
COPY pyproject.toml uv.lock /app/

# Sync dependencies: installs the venv and dependencies first
RUN uv sync --frozen --no-dev --no-install-project

# 7. Copy Project Code
COPY . /app/

# 8. Install the Project Code
# This final uv sync step installs the project itself into the venv
RUN uv sync --frozen --no-dev

# 9. Security: Create non-root user
RUN useradd -m django_user
USER django_user

# 10. Run Gunicorn on the PORT variable
EXPOSE 8080
# The CMD uses the Gunicorn binary from the venv path and binds to the injected $PORT
# Use the correct Django project name!
CMD ["gunicorn", "User_Auth.wsgi:application", "--bind", "0.0.0.0:${PORT}"]