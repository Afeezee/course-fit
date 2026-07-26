"use client";

import { useEffect, useMemo } from "react";
import { useWizard } from "@/lib/store";
import { CREDIT_GRADES } from "@/lib/eligibility";
import type { Grade, Subject } from "@/lib/types";
import { StepShell } from "@/components/ui/StepShell";
import { NavButtons } from "@/components/ui/NavButtons";

// A rough hint per career cluster of "the subjects a student targeting
// this field would typically sit at UTME". This is only used to
// suggest a default selection — the student can override any pick.
const CLUSTER_SUGGESTED: Record<string, string[]> = {
  "Health & Life Sciences": ["PHY", "CHM", "BIO"],
  "Sciences & Mathematics": ["MTH", "PHY", "CHM"],
  "Engineering & Computing": ["MTH", "PHY", "CHM"],
  "Business & Management": ["MTH", "ECO", "ACC"],
  "Public Service & Social Science": ["GOV", "ECO", "HIS"],
  "Law & Legal Studies": ["LIT", "GOV", "ECO"],
  "Agriculture & Environmental Science": ["BIO", "CHM", "MTH"],
  "Arts & Humanities": ["LIT", "GOV", "HIS"],
  "Education & Teaching": ["MTH", "ECO", "GOV"],
};

const GRADE_RANK: Record<Grade, number> = {
  A1: 8, B2: 7, B3: 6, C4: 5, C5: 4, C6: 3, D7: 2, E8: 1, F9: 0,
};

export function UtmeSubjectsStep({
  subjects,
  onNext,
  onBack,
}: {
  subjects: Subject[];
  onNext: () => void;
  onBack: () => void;
}) {
  const { state, dispatch } = useWizard();
  const nameByCode = useMemo(
    () => Object.fromEntries(subjects.map((s) => [s.code, s.name])),
    [subjects]
  );

  // Seed the UTME picks the first time this step is entered: prefer
  // the interest-based suggestion where the student HAS the grade,
  // then fall back to their best-graded credit subjects.
  useEffect(() => {
    if (state.utme_subjects.length > 1) return; // already picked
    const suggested = state.career_interest
      ? CLUSTER_SUGGESTED[state.career_interest] ?? []
      : [];
    const graded = new Set(Object.keys(state.olevel_grades));
    const chosen = new Set<string>(["ENG"]);
    for (const s of suggested) {
      if (graded.has(s) && chosen.size < 4) chosen.add(s);
    }
    if (chosen.size < 4) {
      const byGrade = Object.entries(state.olevel_grades)
        .filter(([s, g]) => s !== "ENG" && g && CREDIT_GRADES.has(g))
        .sort((a, b) => GRADE_RANK[b[1] as Grade] - GRADE_RANK[a[1] as Grade]);
      for (const [s] of byGrade) {
        if (chosen.size >= 4) break;
        chosen.add(s);
      }
    }
    dispatch({ type: "SET_UTME", subjects: Array.from(chosen) });
    // Deliberately omit deps other than the trigger — we only want to
    // run this seeding once when the student arrives on this step.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const canContinue = state.utme_subjects.length === 4 && state.utme_subjects.includes("ENG");

  return (
    <StepShell
      index={4}
      total={6}
      title="Which 4 subjects will you sit at UTME?"
      hint="JAMB UTME is exactly four subjects, and English is compulsory. Pick the three others — the ones you'll actually register for, not necessarily your best grades. If you didn't sit a subject at WAEC but plan to sit it at UTME, you can still pick it here."
    >
      <div className="rounded-md border border-rule bg-paper/60 p-3 text-xs text-ink-muted">
        Selected so far:{" "}
        <span className="font-medium text-ink">
          {state.utme_subjects.length} / 4
        </span>{" "}
        &middot; English is fixed as one of them.
      </div>

      <div className="flex flex-wrap gap-2">
        {subjects.map((s) => {
          const on = state.utme_subjects.includes(s.code);
          const isEng = s.code === "ENG";
          const grade = state.olevel_grades[s.code];
          const atCap = state.utme_subjects.length >= 4 && !on;
          return (
            <button
              key={s.code}
              type="button"
              aria-pressed={on}
              disabled={isEng || atCap}
              onClick={() => dispatch({ type: "TOGGLE_UTME", subject: s.code })}
              className={
                "inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm transition-colors " +
                (on
                  ? isEng
                    ? "cursor-not-allowed border-ink bg-ink/10 text-ink"
                    : "border-ink bg-ink/10 text-ink"
                  : atCap
                  ? "cursor-not-allowed border-rule text-ink-muted opacity-40"
                  : "border-rule text-ink hover:border-ink")
              }
            >
              <span>{s.name}</span>
              <span className="text-xs uppercase tracking-widest text-ink-muted">
                {grade ?? "—"}
              </span>
              {isEng && (
                <span className="text-[10px] uppercase tracking-widest text-seal">
                  Fixed
                </span>
              )}
            </button>
          );
        })}
      </div>

      <NavButtons
        onBack={onBack}
        onNext={onNext}
        nextDisabled={!canContinue}
        nextLabel={canContinue ? "Continue" : `Pick ${4 - state.utme_subjects.length} more`}
      />
    </StepShell>
  );
}
