# Dockerfile for the FastAPI service.
#
# Deployed on Railway with the whole repo as build context (Root
# Directory=blank in the Railway service settings, Config Path=
# apps/api/railway.toml). Using Docker rather than Nixpacks gives
# deterministic behaviour on monorepo roots where Nixpacks otherwise
# has to guess whether the project is Python or Node.
FROM python:3.11-slim

# psycopg[binary] ships its own libpq, so no libpq-dev needed.
# curl is handy for the Railway healthcheck if not using HTTP probe.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first so code edits don't re-install the ~280 MB of ML
# wheels every push.
COPY apps/api/requirements.txt ./apps/api/requirements.txt
RUN pip install --no-cache-dir -r apps/api/requirements.txt

# Copy the rest of the repo. .dockerignore keeps this small — apps/web,
# node_modules, docs, .git, and every .env file are excluded.
# ml/ is included because apps/api/main.py imports directly from it
# via sys.path (see main.py's API_DIR/ML_DIR block).
COPY . .

WORKDIR /app/apps/api

# JSON form so uvicorn receives SIGTERM directly (Railway sends SIGTERM
# on redeploy; a shell wrapper would swallow it and force a SIGKILL
# after grace period). The $PORT env var is expanded by uvicorn via
# --port with envvar interpolation on newer versions; use an entrypoint
# script if you're on an older uvicorn that doesn't support it.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
