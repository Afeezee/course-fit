"""
eligibility.py
--------------
Hard eligibility filter (Objective ii, stage 1). This is deliberately
NOT learned — it's a direct lookup against jamb_data.py, so a course
can never be recommended to a student whose subjects don't meet its
JAMB requirement, regardless of what the classifier predicts.

A student is eligible for a course if:
  1. Their O-Level credits are a superset of the course's required
     credit-level O-Level subjects (grade <= C6), AND
  2. Any subject the course only requires at PASS level (grade <= D7 —
     e.g. "a pass in Mathematics is required", common for Political
     Science, Psychology, Sociology and other Social Sciences per the
     JAMB brochure) is present at at least a pass, AND
  3. Their registered/assumed UTME subjects can satisfy the course's
     UTME combination (English + 3 course-relevant subjects, allowing
     the documented alternate subject where the brochure lists one).

Two grade tiers matter here because the JAMB brochure genuinely
distinguishes them: some Social Sciences courses require Mathematics
only as a pass, not a credit. Treating everything as credit-required
(as an earlier version of this file did) silently rejected students
who would in fact qualify.
"""

from jamb_data import COURSES

# Ordered strongest-first so downstream code can slice.
CREDIT_GRADES = {"A1", "B2", "B3", "C4", "C5", "C6"}
PASS_GRADES = CREDIT_GRADES | {"D7"}  # a "pass" per WAEC


def has_credit(olevel_grades: dict, subject: str) -> bool:
    """olevel_grades: {"ENG": "B3", "MTH": "C6", ...}"""
    return olevel_grades.get(subject) in CREDIT_GRADES


def has_pass(olevel_grades: dict, subject: str) -> bool:
    """A pass is any of A1..D7 (not F9, not 'didn't sit')."""
    return olevel_grades.get(subject) in PASS_GRADES


def is_eligible(student: dict, course: dict) -> bool:
    """
    student = {
        "olevel_grades": {"ENG": "B3", "MTH": "C4", ...},
        "utme_subjects": {"ENG", "MTH", "PHY", "CHM"},  # 4 registered subjects
    }
    """
    # O-Level credit check: every required subject must be a credit.
    for subj in course["olevel_subjects"]:
        if not has_credit(student["olevel_grades"], subj):
            return False

    # O-Level pass check: subjects the brochure only asks for at pass
    # level (e.g. Mathematics for Political Science / Psychology /
    # Sociology). Absent means the student did not sit it — not a pass.
    for subj in course.get("olevel_pass_subjects", []):
        if not has_pass(student["olevel_grades"], subj):
            return False

    # UTME check: English is compulsory (enforced upstream); the
    # remaining 3 registered subjects must cover the course's required
    # set, allowing the documented alternate subject to substitute for
    # exactly one slot.
    required = set(course["utme_subjects"])
    alt = course.get("utme_alt_subject")
    registered = set(student["utme_subjects"])

    missing = required - registered
    if not missing:
        return True
    if len(missing) == 1 and alt and alt in registered:
        return True
    return False


def eligible_courses(student: dict) -> list:
    return [c for c in COURSES if is_eligible(student, c)]


if __name__ == "__main__":
    # Quick smoke test — the historical demo profile stays eligible.
    demo_student = {
        "olevel_grades": {"ENG": "B3", "MTH": "C4", "PHY": "C6",
                           "CHM": "C5", "BIO": "B2"},
        "utme_subjects": {"ENG", "MTH", "PHY", "CHM"},
    }
    for c in eligible_courses(demo_student):
        print(c["course"])
