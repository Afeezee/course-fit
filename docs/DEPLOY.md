# Deploying CourseFit to Railway

> Looking for the Vercel deploy guide instead? See [VERCEL.md](VERCEL.md).
> The two are alternatives — pick one. Railway runs the API as a
> persistent process (no cold starts, connection pooling actually
> works). Vercel is serverless (cold starts, but zero-config for the
> web side and simpler for a demo).



Both services live in one Railway project. The API imports directly
from the sibling `ml/` folder (`jamb_data.py`, `eligibility.py`,
`recommend.py`, `best_model.joblib`), so the whole repo must be
present in each service's container. That rules out the "per-service
root directory" pattern; use the monorepo pattern below.

## One-time project setup

1. Push this repo to GitHub.
2. Create a new Railway project. Add two services from the same repo:
   `api` and `web`. For **each** service:
   - **Root Directory**: leave EMPTY (the whole repo is the build
     context — the config files reference the subdirectories they need).
   - **Config Path**: point to the service's `railway.toml`
     (`apps/api/railway.toml` for `api`, `apps/web/railway.toml` for
     `web`).

## Service variables

On the `api` service:

| Variable | Value |
|---|---|
| `ALLOWED_ORIGINS` | `https://${{web.RAILWAY_PUBLIC_DOMAIN}}` |
| `MODEL_PATH` | leave unset (defaults to `../../ml/best_model.joblib`, correct after `cd apps/api`) |

On the `web` service:

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://${{api.RAILWAY_PUBLIC_DOMAIN}}` |

`NEXT_PUBLIC_API_URL` is baked into the client bundle at build time —
if you change it, redeploy the `web` service.

Deploy order the first time: `api` first, then set
`NEXT_PUBLIC_API_URL` on `web` to the api's now-known Railway domain,
then deploy `web`. From then on, cross-service `${{…}}` references
resolve automatically.

## End-to-end smoke test on the deployed URL

1. `curl https://<api-domain>/api/health` → should return
   `{"status":"ok","model_loaded":true,"model_name":"XGBoost","course_count":50}`.
2. Open `https://<web-domain>`, complete the wizard with a strong
   science profile (English B2, Maths B3, Physics B3, Chemistry A1,
   Biology A1; strengths: Chemistry, Biology; interest: Health & Life
   Sciences; aptitude 4).
3. Confirm the results page shows a genuine model response — a real
   percentage (not a hardcoded value), a real explanation naming your
   strength subjects, and the "XGBoost" model badge.

## Local dev (for reference)

```bash
# In one terminal — API
cd apps/api
pip install -r requirements.txt
uvicorn main:app --port 8000

# In another — web
cd apps/web
npm install
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local
npm run dev
```

Open http://localhost:3000.
