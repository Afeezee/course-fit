# Single-service CourseFit container.
#
# One image, one Railway service, one URL. FastAPI serves:
#   /api/*   → the recommender API (this file's WORKDIR is apps/api)
#   /...     → the Next.js static export copied in from stage 1
#
# Railway settings for this service:
#   Root Directory:  (blank — whole repo is the build context)
#   Config Path:     apps/api/railway.toml
#   Builder:         Dockerfile (auto-detected)

# ============================================================
# Stage 1: build the Next.js static export
# ============================================================
FROM node:20-alpine AS web-builder

WORKDIR /web

# NEXT_PUBLIC_* values must be present at build time so Next.js inlines
# them into the client bundle. Railway auto-passes service variables as
# build args when they're declared as ARG here.
ARG NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=""
ARG NEXT_PUBLIC_API_URL=""
ENV NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Deps first for cache
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci

# Now the rest of the web source
COPY apps/web/ ./

# next.config.mjs sets output:"export", so `npm run build` produces
# ./out as a directory of static HTML/JS/CSS ready to be served by
# any HTTP server.
RUN npm run build


# ============================================================
# Stage 2: Python API + copy in the built web assets
# ============================================================
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# .dockerignore excludes .git, node_modules, and every .env* file.
COPY . .

RUN pip install --no-cache-dir -r apps/api/requirements.txt

# The static web export goes to the location main.py checks for.
COPY --from=web-builder /web/out /app/web-static

WORKDIR /app/apps/api

# JSON form so uvicorn receives SIGTERM directly on redeploy.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
