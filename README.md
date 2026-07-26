# CourseFit

A machine-learning course recommendation system for Nigerian UTME
candidates, covering all nine JAMB faculties. Built for Uche Samuel
Ifeanyi's final-year project (U/23/CS/433, supervised by Miss Sadare).

This repo is meant to be handed to **Claude Code**, which builds
`apps/web` and `apps/api` from scratch following `BUILD_PROMPT.md`.
Everything under `ml/` already exists and works — it is not
something Claude Code should regenerate, only import from and serve.

## Layout

```
course-fit/
├── BUILD_PROMPT.md      ← give this to Claude Code first, in full
├── apps/
│   ├── web/               ← Next.js 14 frontend (Claude Code builds this)
│   │   ├── railway.toml
│   │   └── .env.example
│   └── api/                ← FastAPI backend (Claude Code builds this)
│       ├── railway.toml
│       └── .env.example
├── ml/                      ← the ML pipeline — already built, already working
│   ├── jamb_data.py          (50 courses, 9 faculties, real JAMB requirements)
│   ├── eligibility.py         (hard eligibility filter)
│   ├── label_engine.py         (rule-based ground-truth label generator)
│   ├── generate_dataset.py      (synthetic labelled training set generator)
│   ├── train_model.py            (single Random Forest baseline)
│   ├── model_comparison.py        (8-model comparison → best_model.joblib)
│   ├── recommend.py                (eligibility + model → top-3 with explanations)
│   ├── best_model.joblib             (trained XGBoost model, 75.6% top-1 accuracy on 50 classes)
│   ├── course_dataset.csv             (5,000-row labelled training set)
│   ├── model_comparison_results.csv    (all 8 models' metrics)
│   ├── scrape_brochure.py               (template for adding more courses later)
│   └── requirements.txt
└── docs/
    └── BENCHMARK.md         ← how this system compares to the two prior works
                                 cited in the project proposal (Isma'il et al.
                                 2020 / Aliyu et al. 2021, and Uzoma et al. 2024)
```

## How to start the build

Open this folder in Claude Code and give it, as the first message:

> Read BUILD_PROMPT.md in full, then read every file in ml/ before
> writing any application code. Follow BUILD_PROMPT.md's build order
> exactly — do not skip ahead to frontend code before the backend
> API is working end-to-end and you've reported that back to me.

`BUILD_PROMPT.md` is self-contained and references `ml/` by relative
path throughout, so Claude Code can read the real pipeline directly
rather than working from a description of it.

## Deployment

Two supported paths — pick one:

- **Vercel** (recommended for a demo): both services on Vercel, using
  the `vercel.json` at the repo root. Zero-config for the web side,
  serverless Python for the API. See [`docs/VERCEL.md`](docs/VERCEL.md).
- **Railway**: persistent process for the API (no cold starts,
  connection pooling), separate service for the web. Uses the
  `railway.toml` files scaffolded in `apps/api` and `apps/web`. See
  [`docs/DEPLOY.md`](docs/DEPLOY.md).

Both are free-tier friendly for an academic demo.
