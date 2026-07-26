# Deploying CourseFit on Vercel

Two Vercel projects from the same GitHub repo — one for the FastAPI
backend (Python serverless), one for the Next.js frontend. Both are
free-tier friendly for a demo.

## One-time setup

1. **Push this repo to GitHub** if it isn't already.
2. **Sign in to https://vercel.com/** with your GitHub account.

## Create the API project

3. **Add New… → Project → Import** the CourseFit repo.
4. In the "Configure Project" screen:
   - **Framework Preset**: `Other`
   - **Root Directory**: leave blank (repo root)
   - **Build Command**: leave blank (Vercel reads `vercel.json`)
   - **Output Directory**: leave blank
5. **Environment Variables** (Add them here — same values you have in
   `apps/api/.env.local` locally):

   | Name | Value |
   |---|---|
   | `ALLOWED_ORIGINS` | (fill in after web deploys, see below) |
   | `DATABASE_URL` | your Neon connection string (with `?sslmode=require`, without `channel_binding=require`) |
   | `GROQ_API_KEY` | `gsk_…` |
   | `GROQ_MODEL` | `llama-3.3-70b-versatile` |
   | `CLERK_ISSUER` | `https://<slug>.clerk.accounts.dev` |

6. **Deploy.** Vercel builds the Python function using `vercel.json`
   at the repo root (bundles `apps/api/` + `ml/`, installs
   `apps/api/requirements.txt`). First deploy takes ~2–3 min because
   xgboost + scikit-learn are heavy wheels; subsequent deploys are
   cached and fast.
7. Note the deployed URL — something like
   `https://course-fit-api-<hash>.vercel.app`. Test it:
   ```
   curl https://your-api.vercel.app/api/health
   ```
   You should see `{"status":"ok","model_loaded":true,…}`.

## Create the web project

8. **Add New… → Project → Import** the SAME repo again.
9. Configure:
   - **Framework Preset**: `Next.js` (Vercel auto-detects it)
   - **Root Directory**: `apps/web`
10. **Environment Variables**:

    | Name | Value |
    |---|---|
    | `NEXT_PUBLIC_API_URL` | `https://your-api.vercel.app` (from step 7) |
    | `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_test_…` |
    | `CLERK_SECRET_KEY` | `sk_test_…` |

11. **Deploy.** Note the deployed URL — something like
    `https://course-fit.vercel.app`.

## Close the loop

12. Back on the **API project's** dashboard → Settings → Environment
    Variables → set `ALLOWED_ORIGINS` to the web URL from step 11
    (e.g. `https://course-fit.vercel.app`). No wildcard.
13. Redeploy the API for the CORS change to take effect (Deployments
    tab → three-dot menu → Redeploy).

## Sanity check

- `https://course-fit.vercel.app` — landing loads, activity feed shows recent items.
- Click **Sign in** → Clerk modal → sign up.
- Run the wizard end-to-end. Result explanations should read as adviser prose (LLM path).
- Click **History** — the run you just made appears.

## Notes / gotchas

- **Cold starts.** First request after ~5 min of inactivity spins up
  a new Python container and loads the joblib model. Expect ~2–4 s
  on the first request; subsequent requests within the container's
  life (≈ 15 min) are ~200–500 ms.
- **Vercel's Python function size limit is 500 MB** (2026 update).
  Current bundle is ~280 MB, well within limits.
- **Groq geo-blocking.** Vercel Python functions run in AWS US
  regions by default. Outbound calls to Groq come from US IPs, so
  the geo-block that hit you locally on a Romania VPN doesn't apply
  here.
- **Neon serverless wake.** Neon puts inactive computes to sleep;
  first DB call after ~5 min takes 1–2 s to wake. Only affects the
  first request of a cold cycle.
- **CORS.** `ALLOWED_ORIGINS` on the API must be the *exact*
  web URL — no trailing slash, and if you get a custom domain later,
  update this variable.
