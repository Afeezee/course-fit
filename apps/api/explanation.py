"""
explanation.py
--------------
Optional Groq LLM upgrade for the /api/recommend explanation strings.

When GROQ_API_KEY is set in the environment, `enhance_explanations()`
sends the student's full profile plus the top-N course recommendations
to a Groq-hosted chat model in ONE batched call, and returns a list of
personalised, natural-language explanations — one per recommendation
in input order.

Deliberate design decisions:
  - Single batched call, not one call per recommendation. Cuts cost
    and latency to O(1) per user submission.
  - Structured JSON I/O via response_format={"type": "json_object"}
    so we get a parseable list back rather than free-form prose we'd
    have to parse. Groq's chat completions API supports this.
  - Fail-safe. If the key is missing, if the network is down, if the
    LLM returns malformed JSON, if any recommendation is missing from
    the response — return None. The caller keeps the deterministic
    template explanations from ml/recommend.py. /api/recommend must
    never fail because of an LLM problem.
  - Model + prompt visible here (not hidden in a config file) so the
    contribution can be defended at the panel: this is the LLM's job,
    verbatim.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

log = logging.getLogger("courselab.explanation")

_SYSTEM_PROMPT = (
    "You are a warm, direct academic adviser helping a Nigerian secondary-school "
    "leaver choose a JAMB course. For each recommended course you receive, write "
    "one paragraph (2-4 sentences, ~40-70 words) that:\n"
    "  1. states plainly WHY the course fits, grounded in the student's actual "
    "grades, strengths, weaknesses, and stated career interest — quote the "
    "concrete data points, not vague reassurance;\n"
    "  2. if the recommendation misaligns with the student's stated interest OR "
    "if one of their weaknesses overlaps the course's specialty subjects, say so "
    "honestly in the same paragraph — never hide it;\n"
    "  3. does NOT invent JAMB rules, university names, cutoff marks, career "
    "salaries, or any fact you were not given;\n"
    "  4. is written directly to the student as \"you\", never in the third "
    "person, never as marketing copy, never with emoji.\n\n"
    "Return JSON of the exact shape: "
    '{"explanations": ["...para for rec 1...", "...para for rec 2...", ...]} '
    "with one string per recommendation, in the same order you received them."
)


def _profile_summary(student: dict[str, Any]) -> dict[str, Any]:
    grades = student.get("olevel_grades", {})
    return {
        "olevel_grades": grades,
        "utme_subjects": sorted(student.get("utme_subjects", [])),
        "strengths": sorted(student.get("strengths", [])),
        "weaknesses": sorted(student.get("weaknesses", [])),
        "career_interest": student.get("career_interest"),
        "work_environment": student.get("work_environment"),
        "quantitative_aptitude_1_to_5": student.get("aptitude"),
    }


def _rec_summary(rec: dict[str, Any], course_meta: Optional[dict[str, Any]]) -> dict[str, Any]:
    out = {
        "course": rec["course"],
        "faculty": rec.get("faculty"),
        "career_cluster": rec.get("career_cluster"),
        "fit_score": round(float(rec.get("probability", 0)) * 100, 1),
    }
    if course_meta:
        out["specialty_subjects"] = course_meta.get("specialty_subjects", [])
        out["required_credit_subjects"] = course_meta.get("olevel_subjects", [])
    return out


def enhance_explanations(
    student: dict[str, Any],
    recommendations: list[dict[str, Any]],
    course_by_name: Optional[dict[str, dict[str, Any]]] = None,
    *,
    timeout_seconds: float = 8.0,
) -> Optional[list[str]]:
    """Return a list of enhanced explanation strings, one per rec, or
    None if the LLM path is unavailable / failed for any reason."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key or not recommendations:
        return None

    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    try:
        from groq import Groq
    except ImportError:
        log.warning("groq package not installed; skipping LLM enhancement")
        return None

    payload = {
        "student": _profile_summary(student),
        "recommendations": [
            _rec_summary(r, (course_by_name or {}).get(r["course"]))
            for r in recommendations
        ],
    }

    try:
        client = Groq(api_key=api_key, timeout=timeout_seconds)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
            temperature=0.35,
            max_tokens=900,
        )
        raw = response.choices[0].message.content or ""
        parsed = json.loads(raw)
        items = parsed.get("explanations")
        if not isinstance(items, list) or len(items) != len(recommendations):
            log.warning("LLM returned wrong shape (got %r); falling back", type(items))
            return None
        # Enforce string type + strip; drop any obviously empty items
        cleaned = [str(x).strip() for x in items]
        if any(not c for c in cleaned):
            log.warning("LLM returned empty explanation; falling back")
            return None
        return cleaned
    except Exception as e:
        log.warning("Groq call failed (%s); falling back to template", e)
        return None
