// -------------------------------------------------------------------
// Client-side eligibility filter.
//
// This is a direct port of the credit + UTME logic in
// ml/eligibility.py, used ONLY to drive the live "still-possible"
// counter as the student fills in the wizard — without a per-keystroke
// network round-trip to /api/recommend.
//
// The authoritative filter for the actual recommendation call lives on
// the server (ml/eligibility.py). If you change one, change the other
// too. In particular:
//   - the CREDIT_GRADES set here must match ml/eligibility.py:19
//   - the alt-subject substitution rule (exactly one missing UTME
//     slot may be filled by the documented alternate) must match
//     ml/eligibility.py:is_eligible
//
// Two DELIBERATE simplifications on the client relative to the server:
//   1. /api/courses does not currently ship the olevel_pass_subjects
//      field (added in ml/eligibility.py for "pass in Math" courses),
//      so the client conservatively treats every olevel_subjects entry
//      as credit-required. This means the client counter may UNDER-
//      count eligibility for Political Science / Psychology /
//      Sociology / Geography for students with only a pass (D7) in
//      Math. The server still does the full pass-check on
//      /api/recommend, so the final result is always correct.
//   2. English is not enforced here (a student who hasn't picked ENG
//      as a UTME subject yet is still exploring). The server enforces
//      it via Pydantic validation on submit.
// -------------------------------------------------------------------

import type { Course, Grade } from "./types";

export const CREDIT_GRADES: ReadonlySet<Grade> = new Set([
  "A1", "B2", "B3", "C4", "C5", "C6",
]);

function hasCredit(grades: Record<string, Grade | undefined>, subject: string): boolean {
  const g = grades[subject];
  return g !== undefined && CREDIT_GRADES.has(g);
}

export function isEligible(
  student: {
    olevel_grades: Record<string, Grade | undefined>;
    utme_subjects: ReadonlySet<string>;
  },
  course: Course
): boolean {
  for (const subj of course.olevel_subjects) {
    if (!hasCredit(student.olevel_grades, subj)) return false;
  }
  const required = new Set(course.utme_subjects);
  const missing = [...required].filter((s) => !student.utme_subjects.has(s));
  if (missing.length === 0) return true;
  if (
    missing.length === 1 &&
    course.utme_alt_subject &&
    student.utme_subjects.has(course.utme_alt_subject)
  ) {
    return true;
  }
  return false;
}

export function eligibleCourses(
  student: {
    olevel_grades: Record<string, Grade | undefined>;
    utme_subjects: ReadonlySet<string>;
  },
  courses: Course[]
): Course[] {
  return courses.filter((c) => isEligible(student, c));
}

// Derive the assumed UTME subject set from a student's O-Level grades.
// JAMB UTME is ALWAYS exactly 4 subjects (English + 3), so we pick
// English + the 3 best-graded credit subjects. Passing every credit
// subject (which an earlier version did) both misrepresents what a
// real UTME registration looks like AND overflows the API's
// max_length=6 validator once a student enters more than 5 grades.
//
// The counter is a preview — the student's real UTME choice would be
// driven by the course they want. This heuristic gives the most
// permissive view: a course that qualifies under the student's four
// best subjects is the one most worth showing they qualify for.
const GRADE_RANK: Record<Grade, number> = {
  A1: 8, B2: 7, B3: 6, C4: 5, C5: 4, C6: 3, D7: 2, E8: 1, F9: 0,
};

export function inferUtmeSubjects(
  grades: Record<string, Grade | undefined>
): Set<string> {
  const credits: Array<[string, Grade]> = [];
  for (const [subj, g] of Object.entries(grades)) {
    if (g && CREDIT_GRADES.has(g) && subj !== "ENG") credits.push([subj, g]);
  }
  // Best grade first (A1 before C6), then alphabetical for stable ties.
  credits.sort((a, b) => {
    const d = GRADE_RANK[b[1]] - GRADE_RANK[a[1]];
    return d !== 0 ? d : a[0].localeCompare(b[0]);
  });
  const s = new Set<string>(["ENG"]);
  for (const [subj] of credits) {
    if (s.size >= 4) break;
    s.add(subj);
  }
  return s;
}
