# Deploying CourseFit to Railway

**One Railway service, one deploy, one URL.** The Dockerfile is a two-
stage build that packages the Next.js frontend as a static export and
serves it from the same FastAPI process that owns the recommender API.
No CORS, no cross-service URL wiring, no coordinated deploy sequence.

## Prerequisites

- Repo on GitHub — this one is at https://github.com/Afeezee/course-fit.
- Free Railway account at https://railway.com/.
- Optional accounts + keys — the app runs anonymously without any of them:
  - **Neon Postgres** for the activity feed and per-user history
  - **Groq** for LLM-personalised explanations
  - **Clerk** for sign-in

## Create the service

1. https://railway.com/new → **Deploy from GitHub repo** → select
   `Afeezee/course-fit`. Railway auto-creates one service.
2. Open the service → **Settings**:
   - **Source Repo**: `Afeezee/course-fit`
   - **Root Directory**: leave EMPTY
   - **Config Path**: `apps/api/railway.toml`
   - Rename the service to whatever you like (`coursefit`, `web`, etc.).

That's it — no second service to add.

## Set environment variables

**Settings → Variables**. All of these are optional; the app degrades
gracefully when any are absent.

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Neon connection string. Use the pooled endpoint. Include `?sslmode=require` but NOT `channel_binding=require` (breaks psycopg on Windows / some Linux builds). |
| `GROQ_API_KEY` | `gsk_…` — enables LLM explanations. Omit for template. |
| `GROQ_MODEL` | Defaults to `llama-3.3-70b-versatile`. |
| `CLERK_ISSUER` | `https://<slug>.clerk.accounts.dev` — enables `/api/history`. |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_test_…` — enables the sign-in button. Baked into the client bundle at **build** time, so if you change it you have to redeploy. |
| `NEXT_PUBLIC_API_URL` | Leave EMPTY — same-origin means the frontend calls `/api/...` on itself. |
| `ALLOWED_ORIGINS` | Only needed if you also want the API reachable cross-origin. For single-container deploy, leave unset — the built-in same-origin path doesn't need CORS. |

Railway automatically passes any variable with an `ARG` declaration in
the Dockerfile as a build arg, so `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
and `NEXT_PUBLIC_API_URL` reach the web build stage without further
configuration.

## Deploy

Railway auto-deploys on every push to `main`. The first build takes
6–9 minutes (Node installs, xgboost + sklearn wheels install, image
push). Later builds reuse layers and take 2–3 minutes.

## Sanity check the live URL

- `curl https://<your-service>.up.railway.app/api/health` → JSON with
  `model_loaded: true` and whichever optional subsystems you enabled.
- Open the same URL in a browser → landing page loads.
- Click **Start** → run the wizard → results page renders.
- (If Clerk is configured) click **Sign in** → modal → complete → click
  **History** → your submission is listed.

## Local dev is unchanged

You can still run frontend + API separately for a fast dev loop:

```bash
# Terminal 1 — API
cd apps/api
pip install -r requirements.txt
uvicorn main:app --port 8000

# Terminal 2 — web
cd apps/web
npm install
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local
npm run dev
```

Open http://localhost:3000. In local dev the two are on different
origins, so `ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`
in `apps/api/.env.local` is important. In production single-container
deploy that CORS setting is irrelevant.

## Testing the production build locally

```bash
cd apps/web && npm run build      # produces apps/web/out/
cd ../api && uvicorn main:app --port 8000
open http://localhost:8000
```

FastAPI will detect `apps/web/out/` on the sibling path and serve both
the API and the static frontend from port 8000.

## If a deploy fails

- **Web build fails with "Missing publishableKey"**: you set the Clerk
  publishable key on the wrong side, or forgot to set it. It needs to
  be `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` on this service's Variables
  page.
- **API up but landing 404**: the web stage didn't produce `out/`.
  Check the build logs for a Next.js error — usually a type error or
  a client-side env var missing that the build validates.
- **`invalid token` on `/api/history`**: `CLERK_ISSUER` doesn't match
  the token's `iss` claim. Copy the Frontend API URL from your Clerk
  dashboard verbatim (include `https://`, exclude trailing slash).
- **`persistence_enabled: false`** in `/api/health` after configuring
  Neon: check that `DATABASE_URL` doesn't include
  `&channel_binding=require`. Strip that param and redeploy.
