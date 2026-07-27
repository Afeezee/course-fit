# Deploying CourseFit to Railway

> Prefer Vercel? See [VERCEL.md](VERCEL.md). Note that the API bundle
> (~900 MB with xgboost + scikit-learn + pandas) exceeds Vercel's
> 500 MB Python function limit, so Railway is the recommended path
> for the API. Vercel is still fine for the web-only side if you
> want split hosting.

Two Railway services in ONE Railway project — both pointing at the
same GitHub repo. The API runs as a Docker container (deterministic,
no serverless bundle limits, connection pooling actually works). The
Web runs as a Node.js service via Nixpacks.

## Prerequisites

- The repo pushed to GitHub (this project is at
  https://github.com/Afeezee/course-fit).
- Free Railway account at https://railway.com/.
- These accounts + keys already set up locally:
  - Neon Postgres — `DATABASE_URL`
  - Groq — `GROQ_API_KEY` (optional; template explanations if absent)
  - Clerk — `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`,
    and the Frontend API URL for `CLERK_ISSUER` (optional; anonymous
    flow works if absent)

## Create the Railway project

1. https://railway.com/new → **Deploy from GitHub repo** → select
   `Afeezee/course-fit`. Railway auto-creates the first service.
2. **DON'T let it deploy yet.** In the service's **Settings** tab:
   - **Source Repo**: `Afeezee/course-fit`
   - **Root Directory**: leave EMPTY (whole repo is the build context)
   - **Config Path**: `apps/api/railway.toml`
   - Rename this service to **`api`** (top of Settings).
3. Add a second service in the same project: **New → GitHub Repo →
   Afeezee/course-fit** again.
4. In the second service's Settings:
   - **Root Directory**: `apps/web`  ← different from the api!
   - **Config Path**: leave EMPTY (no config file — Nixpacks
     auto-detects Next.js from `apps/web/package.json`).
   - Rename to **`web`**.

The two services now use different deploy patterns intentionally:
the api uses `Root Directory=/` + `Config Path=apps/api/railway.toml`
because its Dockerfile needs to see both `apps/api/` and the sibling
`ml/` folder as build context. The web has no cross-directory
imports, so it uses the simpler `Root Directory=apps/web` pattern
with no config file.

You should now see two services (`api` and `web`) in one project, both
tracking the same repo but with different config paths.

## Set environment variables

### On the `api` service (Settings → Variables)

| Variable | Value |
|---|---|
| `ALLOWED_ORIGINS` | fill in AFTER web deploys — see step below |
| `DATABASE_URL` | your Neon connection string, e.g. `postgresql://user:pw@ep-xxx.neon.tech/db?sslmode=require` (do NOT include `channel_binding=require`) |
| `GROQ_API_KEY` | `gsk_…` (optional — omit to fall back to template explanations) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` (optional; this is the default) |
| `CLERK_ISSUER` | `https://<slug>.clerk.accounts.dev` (optional — required only if you want /api/history) |

### On the `web` service (Settings → Variables)

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://${{api.RAILWAY_PUBLIC_DOMAIN}}` — Railway's cross-service reference, resolves to the api service's public URL automatically |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_test_…` (optional) |
| `CLERK_SECRET_KEY` | `sk_test_…` (optional) |

## Deploy sequence

5. **Deploy the `api` service first**. Settings → Deployments tab →
   trigger a redeploy (or wait for auto-deploy). Watch the build
   logs. First build takes ~4–6 min because the Docker image installs
   xgboost + scikit-learn + pandas wheels; subsequent deploys reuse
   layers and take ~1 min.
6. When the api build shows **Deployed**, click the service → the
   generated URL is shown at the top (e.g.
   `https://api-production-xxxx.up.railway.app`). Note it.
7. **Deploy the `web` service** next. Watch build; ~2 min.
8. When web shows **Deployed**, its URL will be similar. Note it.
9. **Close the CORS loop**: back on the `api` service → Variables →
   set `ALLOWED_ORIGINS` to the web URL (no trailing slash), e.g.
   `https://web-production-yyyy.up.railway.app`. Save — Railway
   redeploys the api automatically.

## Sanity check

- `curl https://<api-url>/api/health` → JSON with
  `"model_loaded":true`, `"persistence_enabled":true`,
  `"auth_enabled":true` (or `false` if you skipped optional keys).
- Open `<web-url>` in a browser → landing loads, activity feed
  populates.
- Click **Sign in** (if Clerk is configured) → modal appears.
- Run the wizard end-to-end → results page shows adviser-voice
  explanations from Groq (or template if you skipped Groq).

## Local dev is unchanged

```bash
# One terminal — API
cd apps/api
pip install -r requirements.txt
uvicorn main:app --port 8000

# Another — web
cd apps/web
npm install
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local
npm run dev
```

Open http://localhost:3000. See the top-level `apps/api/.env.example`
and `apps/web/.env.example` for the full env-var reference for
local runs.

## If a deploy fails

- **Docker build fails with pip error**: check `apps/api/requirements.txt`
  for a version conflict.
- **API deploys but /api/health 500**: check the api service's
  **Logs** tab. Usually a missing env var or an unreachable
  DATABASE_URL.
- **Web loads but the wizard fails to fetch**: check CORS — the
  `ALLOWED_ORIGINS` env var on the api service must be *exactly* the
  web service's URL, no trailing slash.
- **Clerk /api/history returns 401 "invalid token"**: the
  `CLERK_ISSUER` on the api doesn't match the token's `iss` claim.
  Copy the Frontend API URL from your Clerk dashboard exactly.
