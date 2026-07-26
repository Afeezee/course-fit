"""
db.py
------
Optional Neon (Postgres) persistence for anonymous recommendation
outcomes. Powers the recent-activity feed on the landing page.

What is stored per recommendation (deliberate minimum):
  - server timestamp
  - career_interest the student stated
  - eligible_count (how many courses matched)
  - top match: course name, faculty, career_cluster, fit probability
  - explanation_source: 'template' | 'llm'

What is NOT stored (deliberate):
  - grades, strengths, weaknesses, work_environment, aptitude
  - IP address, user-agent, session, or any identifier
Rationale: the wizard advertises that grades stay in the browser, and
we want to keep that promise while still surfacing a live "system in
use" signal on the homepage. The stored fields cannot be used to
re-identify or reconstruct any individual student's profile.

Fail-safe: every function here returns quietly / harmlessly if
DATABASE_URL is missing or the connection is unhealthy. /api/recommend
must never break because the DB is down.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional

log = logging.getLogger("courselab.db")

_pool = None  # psycopg_pool.ConnectionPool or None


def init_pool() -> None:
    """Open the connection pool and ensure the schema exists. Safe to
    call multiple times. No-op if DATABASE_URL is not set."""
    global _pool
    if _pool is not None:
        return
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        log.info("DATABASE_URL not set — persistence disabled")
        return
    try:
        from psycopg_pool import ConnectionPool
    except ImportError:
        log.warning("psycopg[pool] not installed — persistence disabled")
        return
    try:
        # min_size=0 means the pool does NOT open a connection eagerly
        # at import time — Neon's serverless compute may take several
        # seconds to wake from sleep, and blocking startup on that is a
        # bad tradeoff. The first real /api/recommend call opens the
        # first connection lazily. timeout=30 covers cold-start
        # comfortably.
        _pool = ConnectionPool(
            conninfo=url,
            min_size=0,
            max_size=4,
            timeout=30,
            kwargs={"application_name": "coursefit-api"},
            open=True,
        )
        # Try the schema ensure once, but tolerate a wake-up failure —
        # the write path retries on next request and psycopg_pool will
        # cold-open a connection then.
        try:
            _ensure_schema()
        except Exception as e:
            log.info("initial schema-ensure deferred (%s) — will retry on first write", e)
        log.info("DB pool ready")
    except Exception as e:
        log.warning("DB pool init failed (%s) — persistence disabled", e)
        _pool = None


def _ensure_schema() -> None:
    assert _pool is not None
    with _pool.connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id                  BIGSERIAL PRIMARY KEY,
                created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                career_interest     TEXT        NOT NULL,
                eligible_count      INTEGER     NOT NULL,
                top_course          TEXT        NOT NULL,
                top_faculty         TEXT        NOT NULL,
                top_cluster         TEXT        NOT NULL,
                top_probability     REAL        NOT NULL,
                explanation_source  TEXT        NOT NULL
            );
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS recommendations_created_at_desc
                ON recommendations (created_at DESC);
        """)
        # Additive migration for the sign-in-linked history feature.
        # ADD COLUMN IF NOT EXISTS is idempotent so this is safe on
        # both fresh and existing databases.
        conn.execute("""
            ALTER TABLE recommendations
                ADD COLUMN IF NOT EXISTS clerk_user_id TEXT NULL,
                ADD COLUMN IF NOT EXISTS snapshot      JSONB NULL;
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS recommendations_user_created
                ON recommendations (clerk_user_id, created_at DESC)
                WHERE clerk_user_id IS NOT NULL;
        """)


def insert_recommendation(
    *,
    career_interest: str,
    eligible_count: int,
    top_course: str,
    top_faculty: str,
    top_cluster: str,
    top_probability: float,
    explanation_source: str,
    clerk_user_id: Optional[str] = None,
    snapshot: Optional[dict] = None,
) -> None:
    """Persist one outcome row. Silent no-op if persistence is off or
    the write fails. When clerk_user_id + snapshot are provided (i.e.
    a signed-in submission), the full snapshot is also stored for the
    /api/history endpoint; anonymous rows leave both NULL and only
    appear in the public activity feed."""
    if _pool is None:
        return
    try:
        import json
        with _pool.connection() as conn:
            conn.execute(
                """
                INSERT INTO recommendations
                    (career_interest, eligible_count, top_course, top_faculty,
                     top_cluster, top_probability, explanation_source,
                     clerk_user_id, snapshot)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (career_interest, eligible_count, top_course, top_faculty,
                 top_cluster, float(top_probability), explanation_source,
                 clerk_user_id,
                 json.dumps(snapshot) if snapshot is not None else None),
            )
    except Exception as e:
        log.warning("insert_recommendation failed: %s", e)


def fetch_user_history(clerk_user_id: str, limit: int = 25) -> list[dict]:
    """Return the signed-in user's own past recommendations, most
    recent first. Returns [] if persistence is off or the read fails."""
    if _pool is None or not clerk_user_id:
        return []
    limit = max(1, min(limit, 100))
    try:
        with _pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, created_at, career_interest, eligible_count,
                       top_course, top_faculty, top_cluster,
                       top_probability, explanation_source, snapshot
                FROM recommendations
                WHERE clerk_user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (clerk_user_id, limit),
            )
            rows = cur.fetchall()
        out = []
        for r in rows:
            created: datetime = r[1]
            out.append({
                "id": r[0],
                "created_at": created.isoformat(),
                "career_interest": r[2],
                "eligible_count": r[3],
                "top_course": r[4],
                "top_faculty": r[5],
                "top_cluster": r[6],
                "top_probability": float(r[7]),
                "explanation_source": r[8],
                "snapshot": r[9],  # psycopg3 returns JSONB as dict
            })
        return out
    except Exception as e:
        log.warning("fetch_user_history failed: %s", e)
        return []


def fetch_recent(limit: int = 12) -> list[dict]:
    """Return the N most recent outcomes as dicts. Returns [] if
    persistence is off or the read fails."""
    if _pool is None:
        return []
    limit = max(1, min(limit, 50))
    try:
        with _pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, created_at, career_interest, eligible_count,
                       top_course, top_faculty, top_cluster, top_probability
                FROM recommendations
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
        out = []
        for r in rows:
            created: datetime = r[1]
            out.append({
                "id": r[0],
                "created_at": created.isoformat(),
                "career_interest": r[2],
                "eligible_count": r[3],
                "top_course": r[4],
                "top_faculty": r[5],
                "top_cluster": r[6],
                "top_probability": float(r[7]),
            })
        return out
    except Exception as e:
        log.warning("fetch_recent failed: %s", e)
        return []


def is_enabled() -> bool:
    return _pool is not None


def close_pool() -> None:
    global _pool
    if _pool is not None:
        try:
            _pool.close()
        except Exception:
            pass
        _pool = None
