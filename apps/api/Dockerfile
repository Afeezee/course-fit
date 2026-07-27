# Dockerfile for the FastAPI service, deployed on Railway.
#
# Railway settings for this service:
#   Root Directory: (blank — whole repo is the build context)
#   Config Path:    apps/api/railway.toml
#
# One-shot COPY is used deliberately: earlier attempts with a
# split "COPY requirements first for cache, then rest" pattern
# hit a BuildKit checksum error on Railway's builder. Trading
# per-deploy layer cache for a build that reliably completes.

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# .dockerignore filters out node_modules, .git, and every .env file.
COPY . .

RUN pip install --no-cache-dir -r apps/api/requirements.txt

WORKDIR /app/apps/api

# JSON form so uvicorn receives SIGTERM directly on redeploy.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
