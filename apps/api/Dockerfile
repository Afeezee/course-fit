# Dockerfile for the FastAPI service.
#
# Deployed on Railway with the whole repo as build context (Root
# Directory=blank in the Railway service settings, Config Path=
# apps/api/railway.toml). Using Docker rather than Nixpacks gives
# deterministic behaviour on monorepo roots where Nixpacks otherwise
# has to guess whether the project is Python or Node.
FROM python:3.11-slim

# --- OS setup ---
# psycopg[binary] ships its own libpq, so no libpq-dev needed.
# curl is handy for the Railway healthcheck if not using HTTP probe.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- Python deps ---
# Install first (leverages layer caching so code edits don't re-install
# the ~280MB of ML wheels every push).
COPY apps/api/requirements.txt /app/apps/api/requirements.txt
RUN pip install --no-cache-dir -r apps/api/requirements.txt

# --- Application code ---
# ml/ is included because apps/api/main.py imports directly from it via
# sys.path (see main.py's API_DIR/ML_DIR block).
COPY ml/ /app/ml/
COPY apps/api/ /app/apps/api/

WORKDIR /app/apps/api

# Railway injects $PORT. Local: docker run -e PORT=8000 -p 8000:8000
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
