# CourseFit — Complete Build Prompt for Claude Code

## What this is

CourseFit recommends the best-fit JAMB/UTME course to a Nigerian
secondary-school leaver, across all nine JAMB faculties, based on
their WAEC grades, subject strengths, career interest, and aptitude —
checking real JAMB eligibility rules first, then ranking what they
qualify for using a trained ML model, with a plain-language
explanation for every recommendation.

This is a final-year Computer Science project (Uche Samuel Ifeanyi,
U/23/CS/433, Oduduwa University, supervised by Miss Sadare), so it
needs to be genuinely production-quality — this is the artifact that
gets defended in front of an academic panel and used as a live demo,
not a throwaway prototype.

**Read every file in `ml/` before writing any application code.**
That folder is the real, already-working ML pipeline — 46 courses
compiled from actual JAMB brochure PDFs, a rule-based label generator,
a trained Gradient Boosting classifier at 94.1% accuracy / 0.901 macro
F1 (picked from an 8-model comparison), and a `recommend.py` that
already implements the eligibility-filter-then-rank logic. Your job is
to **serve and present** that pipeline, not redesign it. Do not
fabricate course data, invent subject requirements, or approximate the
model with mock logic anywhere in the app — every recommendation the
UI shows must come from a real call to the real model.

---

## Tech stack

| Layer | Choice |
|---|---|
| Frontend framework | Next.js 14, App Router, TypeScript |
| Styling | Tailwind CSS + shadcn/ui |
| Animation | Framer Motion |
| Backend | FastAPI (Python), wrapping `ml/recommend.py` and `ml/eligibility.py` directly |
| Model serving | `ml/best_model.joblib` loaded once at API startup, not per-request |
| Deployment | Railway, two services in one project (`apps/web`, `apps/api`) |
| Package managers | npm (web), pip (api) |

No database and no auth are required for the MVP — a prospective UTME
candidate should be able to get a recommendation with zero friction,
no account. (If you want a "save/share my result" feature later,
that's a legitimate Phase 2 addition — see the note at the end — but
don't let it block or complicate the MVP.)

---

## Design direction

Before writing any frontend code, do a real design pass — brainstorm
a token system (palette as 4–6 named hex values, a type pairing, a
layout concept, one signature element), critique it against the
guidance below, then build. Don't default to generic SaaS-template
looks (a cream-and-terracotta hero, a dark-mode-with-neon-accent
dashboard, a hairline-rule broadsheet layout) — this has a specific
subject and audience, design from that.

**The actual subject**: this app sits at one of the highest-stakes,
most emotionally loaded moments in a Nigerian teenager's life — the
choice that determines their university course, and by extension a
huge amount of their next decade. It should feel credible, calm, and a
little ceremonial (like a well-designed exam slip or admission letter
— official, but warm, not bureaucratic or cold), never like a generic
quiz app or a corporate SaaS dashboard.

**Interaction quality bar**: match the polish and motion craft of
Sculptform (sculptform.live) — a live-preview feel where the interface
visibly responds as the person provides input, confident
micro-interactions, a considered page-load/reveal sequence, not
scattered decorative animation. Concretely:

- As the student fills in grades, keep a live, ambient counter/preview
  visible (e.g. "14 of 46 courses still possible") that visibly
  shrinks or grows as they add grades, strengths, and preferences —
  this is the single most important "alive" moment in the app; get it
  right before polishing anything else.
- The results reveal should feel like a moment, not an instant dump —
  a staggered/sequenced reveal of the top 3 cards, not everything
  popping in at once.
- Respect `prefers-reduced-motion` throughout.
- Visible keyboard focus states on every interactive element — this
  is a public-facing tool for 16–18 year-olds on all kinds of devices
  and connections, treat accessibility as a real requirement, not a
  nice-to-have.

**Avoid literally cloning Sculptform's visual identity** (different
product, different audience) — match its *execution quality and
interaction craft*, not its palette or copy.

---

## Information architecture

Three real screens, no more for the MVP:

1. **Landing** — states what the tool does and why it's trustworthy
   (grounds itself in real JAMB data, not vibes), one clear CTA into
   the wizard. Include real, specific numbers (9 faculties, 46
   courses currently modelled, honestly framed as "growing" rather
   than implying total coverage — see `docs/BENCHMARK.md` and the
   `ml/jamb_data.py` docstring for the actual current scope and its
   limitations, and represent them honestly in the copy).
2. **Wizard** (multi-step, one concern per step):
   1. WAEC/SSCE grades — every subject in `ml/jamb_data.py`'s
      `SUBJECT_NAMES`, one grade selector each (A1–F9, or "didn't
      sit"). Design this as something better than a giant table if
      you can — a searchable/filterable subject list, or grouped by
      subject area, so a student isn't scanning 14+ rows on mobile.
   2. Strongest subjects — up to 3, chosen only from subjects with a
      credit grade (C6 or better). Reuse the credit-grade set exactly
      as defined in `ml/eligibility.py`'s `CREDIT_GRADES` — don't
      redefine it in the frontend or backend separately from that
      source of truth.
   3. Weakest subjects — up to 2, same credit-only constraint, and a
      subject picked as a strength can't also be picked as a weakness
      (enforce this in the UI, not just by trusting the API).
   4. Career interest + preferred work environment — pick from the
      `career_cluster` values that actually appear in
      `ml/jamb_data.py`'s `COURSES` (derive the list from that file
      programmatically at build/generation time, don't hardcode a
      separate copy that can drift out of sync).
   5. Quantitative aptitude — a single 1–5 scale.
3. **Results** — top 3 ranked, eligible-only recommendations, each
   with: course name, a fit indicator (use the model's actual
   predicted probability from `recommend.py`, not a fabricated
   percentage), and the plain-language explanation `recommend.py`
   already generates. Include a "Start over" action and a way to go
   back and adjust an earlier step without losing later answers.

No login, no dashboard, no admin panel for the MVP.

---

## Backend (`apps/api`)

Build a FastAPI service that:

1. Loads `../../ml/best_model.joblib` once at startup (not per
   request — this matters for response time).
2. Exposes:
   - `GET /api/courses` — returns the course list and metadata Claude
     Code needs the frontend to render (course names, career
     clusters, subject codes/names) — derived directly from
     `ml/jamb_data.py`'s `COURSES` and `SUBJECT_NAMES`, imported as a
     Python module, not duplicated as a static JSON the frontend
     maintains separately. If `jamb_data.py` changes, this endpoint's
     output should change with it automatically.
   - `POST /api/recommend` — accepts a student profile (grades,
     strengths, weaknesses, career interest, work environment,
     aptitude) matching the shape `ml/recommend.py`'s
     `top_n_recommendations()` expects, and returns its output
     directly. Validate the request body with a Pydantic model that
     mirrors what `eligibility.py` and `recommend.py` actually need —
     read those two files closely before writing the schema.
3. Handles the "no eligible course" case explicitly — return a clear,
   distinguishable response (not an empty 200, not a 500) so the
   frontend can show a real empty-state, not a spinner that silently
   stops.
4. CORS: allow only the origin(s) in `ALLOWED_ORIGINS` (see
   `.env.example`) — no wildcard `*` in production.
5. Import `eligibility.py`, `label_engine.py`, `jamb_data.py`, and
   `recommend.py` directly from `../../ml/` (adjust `sys.path` or use
   a relative import setup — don't copy-paste their contents into
   `apps/api`, since that creates two copies of the same logic that
   will drift apart).

Write a `requirements.txt` for `apps/api` covering `fastapi`,
`uvicorn`, plus whatever `../../ml/requirements.txt` already pins
(read that file — don't guess versions).

---

## Frontend (`apps/web`)

- Fetch `NEXT_PUBLIC_API_URL` (see `.env.example`) for all API calls;
  never hardcode `localhost` in a component.
- Keep wizard state in React state (Context or a simple reducer) —
  no `localStorage`/`sessionStorage` dependency for core flow state;
  it's fine to lose progress on a hard refresh for an MVP this short.
- Build the "live eligible-course counter" by calling a lightweight
  client-side eligibility check as the student fills in each step —
  either replicate `eligibility.py`'s logic in a small, well-tested
  TypeScript module (kept in `apps/web/lib/eligibility.ts`, generated
  from or kept in lockstep with `ml/eligibility.py` — comment clearly
  where the logic must be kept in sync) for instant feedback without a
  network round-trip per keystroke, or debounce calls to
  `POST /api/recommend` if you'd rather have one source of truth and
  accept the latency. Either is defensible — pick one, document the
  tradeoff in a code comment, don't leave it unstated.
- Handle loading and error states for every API call — a slow or
  failed `/api/recommend` call should never leave the student looking
  at a blank screen.

---

## Deployment (Railway)

Two services in one Railway project, each with its own root
directory (`apps/api` and `apps/web` respectively) — `railway.toml`
is already scaffolded in both folders with the right build/start
commands; verify they still match what you actually build (e.g. if
you add a build step for the API, update its `railway.toml`).

Steps once the app works locally:
1. Push the repo to GitHub.
2. Create a Railway project, add two services, set each one's root
   directory (`/apps/api`, `/apps/web`) in its service settings.
3. Set watch paths per service (`apps/api/**` for the API,
   `apps/web/**` for the web app) so a change to one doesn't trigger a
   rebuild of the other.
4. Set environment variables per service:
   - `apps/api`: `ALLOWED_ORIGINS` = the web service's public Railway
     domain (get this after the web service has deployed once).
   - `apps/web`: `NEXT_PUBLIC_API_URL` = the api service's public
     Railway domain, using Railway's cross-service variable reference
     syntax where possible instead of hardcoding a URL.
5. Deploy both, then do a real end-to-end check: submit the full
   wizard against the live API and confirm the results page shows a
   genuine model response, not a cached/mock one.

---

## Build order — follow this sequence, report back after each step

**Step 0.** Read `README.md`, then every file in `ml/`, in full. Run
`ml/recommend.py`'s existing logic locally (you'll need
`pip install -r ml/requirements.txt`) against a hand-built sample
student profile, and confirm you get sensible output before writing
any new code. Report what you found — course count, model accuracy,
any assumptions in `eligibility.py` or `label_engine.py` worth
flagging — before moving on.

**Step 1.** Build `apps/api` — the FastAPI service, both endpoints,
tested locally with a few manual `curl`/httpie requests covering an
eligible case, an ineligible-for-everything case, and a partial-grade
case. Do not proceed to frontend work until this is solid.

**Step 2.** Do the design brainstorm/critique pass described above,
and share the resulting token system (palette, type, layout, signature
element) before building UI — a quick text summary is enough, this
doesn't need to block on approval, just make the reasoning visible.

**Step 3.** Build the wizard (steps in order: grades → strengths →
weaknesses → interests → aptitude), wired to the live eligibility
counter.

**Step 4.** Build the results page, wired to `POST /api/recommend`.

**Step 5.** Full local end-to-end pass: landing → wizard → results,
on both a desktop and a narrow mobile viewport, checking keyboard
navigation and focus states throughout.

**Step 6.** Prepare both `railway.toml` files and both `.env.example`
files for accuracy against what you actually built, then walk through
the Railway deployment steps above.

---

## Non-negotiables

- Every recommendation shown in the UI must come from a real call to
  the real trained model via `POST /api/recommend` — no mock data, no
  client-side approximation standing in as the "real" result anywhere
  in the shipped app (the client-side eligibility pre-check for the
  live counter is fine and expected; the actual ranked recommendation
  is not).
- Don't duplicate `jamb_data.py`'s course list, subject codes, or
  career clusters as a separately-maintained frontend copy — derive
  them from the real file via the API, so the two can never silently
  drift apart.
- Don't quietly drop the eligibility filter — a course the student
  isn't actually qualified for should never appear in results, full
  stop, regardless of what the ranking model would have scored it.
- Keep explanations in the plain, direct language `recommend.py`
  already generates ("you have credits in X, identified as a
  strength") — don't rephrase them into vaguer marketing copy.
- If something in `ml/` looks off, wrong, or worth questioning while
  you're reading it in Step 0 (for instance, check the data-quality
  caveat already documented in `jamb_data.py`'s docstring about the
  Social Sciences faculty extraction), say so before building around
  it silently.

## Optional Phase 2 (do not build unless explicitly asked)

- Account creation (Clerk) so a student can save/revisit a past
  result.
- A feedback/rating step after results, feeding the real-user
  relevance evaluation described in the project proposal's Objective
  (iv) — this would need its own small persistence layer (Postgres on
  Railway is the natural choice given the rest of the stack) and
  should be scoped as its own follow-up prompt once the MVP is live,
  not folded into this build.
