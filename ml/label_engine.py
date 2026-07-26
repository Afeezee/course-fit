"""
label_engine.py
----------------
Objective (i)/(ii): the rule engine that assigns a "best-fit course"
label to a (simulated) student profile. This is what resolves the
ground-truth problem described in the proposal — it is the source of
truth the classifier is trained to reproduce and generalise from.

Scoring logic (transparent, documented, defensible at defence):
  1. Eligibility filter removes any course the student can't register
     for (see eligibility.py). Ineligible courses score 0.
  2. +3 points per O-Level "strength" subject the student named that
     is also required by the course.
  3. -2 points per O-Level "weakness" subject the student named that
     is also required by the course (a weak subject required by a
     course is a bad sign for later academic performance).
  4. SPECIALTY match: +4 per strength that is in the course's
     specialty_subjects list, -6 per weakness that is in the specialty.
     Specialty subjects capture what the course is fundamentally about
     — Mechanical Engineering's specialty is [PHY, MTH], Computer
     Science's specialty is [MTH]. Both require Physics per JAMB, but
     only Mech Eng is *about* Physics; the heavy specialty-weakness
     penalty (-6) means a Physics-averse student who is
     Engineering-interested is steered away from Mech Eng towards CS or
     Chemical Eng, rather than tied with them as the pre-specialty
     scheme did.
  5. +4 points if the course's career_cluster matches the student's
     stated career interest.
  6. +2 points if the course's career_cluster matches the student's
     preferred work-environment category.
  7. Quantitative-aptitude gate: Sciences & Mathematics AND Engineering
     & Computing courses get -3 if the student's self-rated aptitude
     is 1 or 2 (of 5).
  8. Ties broken deterministically per-student by a hash of (student
     profile, course name), so tied candidates within a cluster get a
     fair share of the training labels rather than a single course
     winning every tie.

The top-scoring eligible course is the label. If no course is
eligible, the profile is discarded from the training set.
"""

import hashlib
from eligibility import eligible_courses

APTITUDE_PENALISED_CLUSTERS = {
    "Sciences & Mathematics",
    "Engineering & Computing",
}

STRENGTH_REQUIRED_BONUS = 3
WEAKNESS_REQUIRED_PENALTY = -2
STRENGTH_SPECIALTY_BONUS = 4
WEAKNESS_SPECIALTY_PENALTY = -6
CAREER_MATCH_BONUS = 4
ENVIRONMENT_MATCH_BONUS = 2
LOW_APTITUDE_PENALTY = -3


def score_course(student: dict, course: dict) -> float:
    score = 0.0
    required = set(course["utme_subjects"]) | set(course["olevel_subjects"])
    specialty = set(course.get("specialty_subjects", []))

    for s in student["strengths"]:
        if s in required:
            score += STRENGTH_REQUIRED_BONUS
        if s in specialty:
            score += STRENGTH_SPECIALTY_BONUS

    for w in student["weaknesses"]:
        if w in required:
            score += WEAKNESS_REQUIRED_PENALTY
        if w in specialty:
            score += WEAKNESS_SPECIALTY_PENALTY

    if course["career_cluster"] == student["career_interest"]:
        score += CAREER_MATCH_BONUS

    if course["career_cluster"] == student["work_environment"]:
        score += ENVIRONMENT_MATCH_BONUS

    if course["career_cluster"] in APTITUDE_PENALISED_CLUSTERS \
            and student["aptitude"] <= 2:
        score += LOW_APTITUDE_PENALTY

    return score


def _student_key(student: dict) -> str:
    """Deterministic string summarising a student profile — used to
    seed per-student tie-breaks so different profiles pick different
    courses among a cluster of tied options."""
    return "|".join([
        ",".join(sorted(f"{k}={v}" for k, v in student["olevel_grades"].items())),
        ",".join(sorted(student.get("strengths", []))),
        ",".join(sorted(student.get("weaknesses", []))),
        str(student.get("career_interest", "")),
        str(student.get("work_environment", "")),
        str(student.get("aptitude", "")),
    ])


def _tiebreak_key(student_key: str, course_name: str) -> int:
    h = hashlib.md5(f"{student_key}||{course_name}".encode()).hexdigest()
    return int(h[:12], 16)


def best_fit_course(student: dict):
    candidates = eligible_courses(student)
    if not candidates:
        return None
    sk = _student_key(student)
    scored = [
        (-score_course(student, c), _tiebreak_key(sk, c["course"]), c["course"])
        for c in candidates
    ]
    scored.sort()
    return scored[0][2]
