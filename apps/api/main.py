"""
CourseFit API
-------------
Thin FastAPI wrapper around the pipeline in ../../ml/. The pipeline
(eligibility filter + trained Gradient Boosting ranker + explanation
generator) is not re-implemented here — it is imported directly, so
this file is the only place the two must be kept in sync with.

Endpoints:
    GET  /api/health      liveness + model-loaded probe
    GET  /api/courses     course + subject + career-cluster metadata
                          derived from ml/jamb_data.py at request time
    POST /api/recommend   student profile in, top-3 eligible-and-ranked
                          courses out (or an explicit "no eligible
                          course" response — never a silent empty 200)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Literal, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

# Load apps/api/.env (if present) before anything reads os.environ, so
# ALLOWED_ORIGINS, GROQ_API_KEY, etc. picked up from a local .env file
# take effect. Also load .env.local — the Next.js convention — as a
# convenience for anyone who habitually names it that way. Neither
# file is committed. On Railway (or any real deployment) the service
# variables are already in the real environment; load_dotenv() is a
# no-op if the file doesn't exist.
_API_DIR = Path(__file__).resolve().parent
load_dotenv(_API_DIR / ".env")
load_dotenv(_API_DIR / ".env.local", override=False)

# ---------------------------------------------------------------------------
# Wire ml/ onto sys.path so we import the real modules, not a copy.
# ---------------------------------------------------------------------------
API_DIR = Path(__file__).resolve().parent
ML_DIR = (API_DIR / ".." / ".." / "ml").resolve()
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from eligibility import CREDIT_GRADES, eligible_courses  # noqa: E402
from jamb_data import COURSES, SUBJECT_NAMES  # noqa: E402
from recommend import load_best_model, top_n_recommendations  # noqa: E402

from explanation import enhance_explanations  # noqa: E402
import auth  # noqa: E402
import db  # noqa: E402


# ---------------------------------------------------------------------------
# App + model bootstrap. best_model.joblib is loaded ONCE at startup so
# /api/recommend is not paying deserialization cost per request.
# ---------------------------------------------------------------------------
MODEL_PATH = os.environ.get(
    "MODEL_PATH", str(ML_DIR / "best_model.joblib")
)

app = FastAPI(
    title="CourseFit API",
    version="1.0.0",
    description="JAMB course recommender for UTME candidates.",
)

allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class _ModelState:
    clf = None
    label_encoder = None
    feature_columns: Optional[List[str]] = None
    model_name: Optional[str] = None


@app.on_event("startup")
def _startup() -> None:
    _ModelState.clf, _ModelState.label_encoder, _ModelState.feature_columns = (
        load_best_model(MODEL_PATH)
    )
    import joblib
    bundle = joblib.load(MODEL_PATH)
    _ModelState.model_name = bundle.get("model_name")
    db.init_pool()


@app.on_event("shutdown")
def _shutdown() -> None:
    db.close_pool()


# ---------------------------------------------------------------------------
# Request / response schemas. These mirror what eligibility.py and
# recommend.py actually consume — do not add fields the pipeline ignores.
# ---------------------------------------------------------------------------
GRADE_LITERALS = ("A1", "B2", "B3", "C4", "C5", "C6", "D7", "E8", "F9")
GradeLiteral = Literal["A1", "B2", "B3", "C4", "C5", "C6", "D7", "E8", "F9"]

_VALID_SUBJECT_CODES = set(SUBJECT_NAMES.keys())
_VALID_CAREER_CLUSTERS = sorted({c["career_cluster"] for c in COURSES})


class StudentProfile(BaseModel):
    olevel_grades: Dict[str, GradeLiteral] = Field(
        ...,
        description=(
            "Map of subject code → WAEC grade. Only subjects the student "
            "sat should appear. Missing subjects are treated as 'not sat'."
        ),
    )
    utme_subjects: List[str] = Field(
        ...,
        min_length=1,
        max_length=6,
        description="UTME subject codes; must include ENG.",
    )
    strengths: List[str] = Field(default_factory=list, max_length=3)
    weaknesses: List[str] = Field(default_factory=list, max_length=2)
    career_interest: str
    work_environment: str
    aptitude: int = Field(..., ge=1, le=5)

    @field_validator("olevel_grades")
    @classmethod
    def _check_grade_subjects(cls, v: Dict[str, str]) -> Dict[str, str]:
        unknown = [s for s in v if s not in _VALID_SUBJECT_CODES]
        if unknown:
            raise ValueError(f"unknown subject codes in olevel_grades: {unknown}")
        return v

    @field_validator("utme_subjects")
    @classmethod
    def _check_utme(cls, v: List[str]) -> List[str]:
        if "ENG" not in v:
            raise ValueError("utme_subjects must include ENG (English is compulsory)")
        unknown = [s for s in v if s not in _VALID_SUBJECT_CODES]
        if unknown:
            raise ValueError(f"unknown subject codes in utme_subjects: {unknown}")
        return v

    @field_validator("strengths", "weaknesses")
    @classmethod
    def _check_subject_list(cls, v: List[str]) -> List[str]:
        unknown = [s for s in v if s not in _VALID_SUBJECT_CODES]
        if unknown:
            raise ValueError(f"unknown subject codes: {unknown}")
        return v

    @field_validator("career_interest", "work_environment")
    @classmethod
    def _check_cluster(cls, v: str) -> str:
        if v not in _VALID_CAREER_CLUSTERS:
            raise ValueError(
                f"unknown career cluster {v!r}; must be one of {_VALID_CAREER_CLUSTERS}"
            )
        return v


class Recommendation(BaseModel):
    course: str
    faculty: str
    career_cluster: str
    probability: float
    explanation: str


class RecommendResponse(BaseModel):
    status: Literal["ok", "no_eligible_courses"]
    recommendations: List[Recommendation]
    eligible_count: int
    model_name: Optional[str] = None
    # "template" = deterministic recommend.py explanation; "llm" =
    # Groq-generated. Tells the UI whether it should render an
    # "AI-personalised" badge / disclaimer.
    explanation_source: Literal["template", "llm"] = "template"


class CourseMeta(BaseModel):
    course: str
    faculty: str
    career_cluster: str
    utme_subjects: List[str]
    utme_alt_subject: Optional[str] = None
    olevel_subjects: List[str]


class SubjectMeta(BaseModel):
    code: str
    name: str


class CoursesResponse(BaseModel):
    courses: List[CourseMeta]
    subjects: List[SubjectMeta]
    career_clusters: List[str]
    credit_grades: List[str]
    grade_scale: List[str]
    faculties: List[str]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "model_loaded": _ModelState.clf is not None,
        "model_name": _ModelState.model_name,
        "course_count": len(COURSES),
        "persistence_enabled": db.is_enabled(),
        "auth_enabled": auth.is_enabled(),
    }


class RecentItem(BaseModel):
    id: int
    created_at: str
    career_interest: str
    eligible_count: int
    top_course: str
    top_faculty: str
    top_cluster: str
    top_probability: float


class RecentResponse(BaseModel):
    enabled: bool
    items: List[RecentItem]


@app.get("/api/recent", response_model=RecentResponse)
def recent(limit: int = 12) -> RecentResponse:
    return RecentResponse(
        enabled=db.is_enabled(),
        items=[RecentItem(**row) for row in db.fetch_recent(limit=limit)],
    )


@app.get("/api/courses", response_model=CoursesResponse)
def get_courses() -> CoursesResponse:
    return CoursesResponse(
        courses=[
            CourseMeta(
                course=c["course"],
                faculty=c["faculty"],
                career_cluster=c["career_cluster"],
                utme_subjects=c["utme_subjects"],
                utme_alt_subject=c.get("utme_alt_subject"),
                olevel_subjects=c["olevel_subjects"],
            )
            for c in COURSES
        ],
        subjects=[SubjectMeta(code=k, name=v) for k, v in SUBJECT_NAMES.items()],
        career_clusters=_VALID_CAREER_CLUSTERS,
        credit_grades=sorted(CREDIT_GRADES),
        grade_scale=list(GRADE_LITERALS),
        faculties=sorted({c["faculty"] for c in COURSES}),
    )


class HistoryItem(BaseModel):
    id: int
    created_at: str
    career_interest: str
    eligible_count: int
    top_course: str
    top_faculty: str
    top_cluster: str
    top_probability: float
    explanation_source: str
    snapshot: Optional[dict] = None


class HistoryResponse(BaseModel):
    items: List[HistoryItem]


@app.get("/api/history", response_model=HistoryResponse)
def history(
    limit: int = 25,
    user_id: str = Depends(auth.required_user_id),
) -> HistoryResponse:
    return HistoryResponse(
        items=[HistoryItem(**row) for row in db.fetch_user_history(user_id, limit=limit)],
    )


@app.post("/api/recommend", response_model=RecommendResponse)
def recommend(
    profile: StudentProfile,
    user_id: Optional[str] = Depends(auth.optional_user_id),
) -> RecommendResponse:
    if _ModelState.clf is None:
        raise HTTPException(status_code=503, detail="model not loaded")

    student = {
        "olevel_grades": profile.olevel_grades,
        "utme_subjects": set(profile.utme_subjects),
        "strengths": list(profile.strengths),
        "weaknesses": list(profile.weaknesses),
        "career_interest": profile.career_interest,
        "work_environment": profile.work_environment,
        "aptitude": profile.aptitude,
    }

    eligible = eligible_courses(student)
    if not eligible:
        return RecommendResponse(
            status="no_eligible_courses",
            recommendations=[],
            eligible_count=0,
            model_name=_ModelState.model_name,
        )

    raw = top_n_recommendations(
        student,
        _ModelState.clf,
        _ModelState.label_encoder,
        _ModelState.feature_columns,
        n=3,
    )
    course_lookup = {c["course"]: c for c in COURSES}

    # Assemble what we need to pass to the LLM (faculty + cluster
    # already present in `raw` via the template layer? no — recompute)
    llm_input_recs = [
        {
            "course": r["course"],
            "faculty": course_lookup[r["course"]]["faculty"],
            "career_cluster": course_lookup[r["course"]]["career_cluster"],
            "probability": r["probability"],
        }
        for r in raw
    ]
    llm_explanations = enhance_explanations(
        student, llm_input_recs, course_by_name=course_lookup
    )
    source: Literal["template", "llm"] = "llm" if llm_explanations else "template"
    final_explanations = llm_explanations or [r["explanation"] for r in raw]

    # Persist the outcome. Silent no-op if the DB is off.
    # If the caller is signed in, ALSO save the full snapshot linked
    # to the user_id so they can revisit their past recommendations
    # via /api/history. Anonymous callers save only the summary row
    # that feeds the public activity feed.
    top = raw[0]
    snapshot = None
    if user_id:
        snapshot = {
            "profile": {
                "olevel_grades": profile.olevel_grades,
                "utme_subjects": list(profile.utme_subjects),
                "strengths": list(profile.strengths),
                "weaknesses": list(profile.weaknesses),
                "career_interest": profile.career_interest,
                "work_environment": profile.work_environment,
                "aptitude": profile.aptitude,
            },
            "recommendations": [
                {
                    "course": r["course"],
                    "faculty": course_lookup[r["course"]]["faculty"],
                    "career_cluster": course_lookup[r["course"]]["career_cluster"],
                    "probability": float(r["probability"]),
                    "explanation": final_explanations[i],
                }
                for i, r in enumerate(raw)
            ],
        }
    db.insert_recommendation(
        career_interest=profile.career_interest,
        eligible_count=len(eligible),
        top_course=top["course"],
        top_faculty=course_lookup[top["course"]]["faculty"],
        top_cluster=course_lookup[top["course"]]["career_cluster"],
        top_probability=float(top["probability"]),
        explanation_source=source,
        clerk_user_id=user_id,
        snapshot=snapshot,
    )

    return RecommendResponse(
        status="ok",
        recommendations=[
            Recommendation(
                course=r["course"],
                faculty=course_lookup[r["course"]]["faculty"],
                career_cluster=course_lookup[r["course"]]["career_cluster"],
                probability=float(r["probability"]),
                explanation=final_explanations[i],
            )
            for i, r in enumerate(raw)
        ],
        eligible_count=len(eligible),
        model_name=_ModelState.model_name,
        explanation_source=source,
    )


# ---------------------------------------------------------------------------
# Static frontend mount (single-container deploy).
#
# In the single-service Railway setup, this container also serves the
# Next.js static export at "/", so the frontend and API share the same
# origin (no CORS, no cross-service URL wiring). The Docker build's web
# stage produces the export at apps/web/out/ and copies it here.
#
# Local dev (two servers) doesn't need this — the Next.js dev server
# handles the frontend itself. When the directory is absent, we just
# skip the mount and the API runs headless.
# ---------------------------------------------------------------------------
_WEB_DIR = (_API_DIR / ".." / "web" / "out").resolve()
_WEB_DIR_ALT = Path("/app/web-static")  # what the Dockerfile copies to

_web_root: Optional[Path] = None
for _candidate in (_WEB_DIR, _WEB_DIR_ALT):
    if _candidate.is_dir():
        _web_root = _candidate
        break

if _web_root is not None:
    @app.get("/", include_in_schema=False)
    def _index() -> FileResponse:
        return FileResponse(_web_root / "index.html")

    # StaticFiles(html=True) resolves /foo/ -> /foo/index.html, so the
    # combination of trailingSlash:true in next.config.mjs + html=True
    # here gives correct routing for /wizard/, /history/, etc.
    app.mount(
        "/",
        StaticFiles(directory=str(_web_root), html=True),
        name="web",
    )
