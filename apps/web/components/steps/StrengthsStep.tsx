"use client";

import { useMemo } from "react";
import { useWizard } from "@/lib/store";
import { CREDIT_GRADES } from "@/lib/eligibility";
import type { Subject } from "@/lib/types";
import { StepShell } from "@/components/ui/StepShell";
import { NavButtons } from "@/components/ui/NavButtons";

export function StrengthsStep({
  subjects,
  onNext,
  onBack,
}: {
  subjects: Subject[];
  onNext: () => void;
  onBack: () => void;
}) {
  const { state, dispatch } = useWizard();
  const nameByCode = useMemo(() => Object.fromEntries(subjects.map((s) => [s.code, s.name])), [subjects]);

  const eligible = useMemo(
    () =>
      Object.entries(state.olevel_grades)
        .filter(([, g]) => g && CREDIT_GRADES.has(g))
        .map(([code]) => code),
    [state.olevel_grades]
  );

  return (
    <StepShell
      index={1}
      total={6}
      title="Your strongest subjects"
      hint="Pick up to three subjects you're genuinely confident in. Only subjects you passed at credit (C6 or better) are shown — you can't call something a strength if you didn't clear the credit bar."
    >
      {eligible.length === 0 ? (
        <p className="rounded-md border border-rule p-4 text-sm text-ink-muted">
          You don&apos;t have any subjects at credit level yet. Go back and add
          more grades.
        </p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {eligible.map((code) => {
            const on = state.strengths.includes(code);
            const isWeak = state.weaknesses.includes(code);
            return (
              <button
                key={code}
                type="button"
                aria-pressed={on}
                onClick={() => dispatch({ type: "TOGGLE_STRENGTH", subject: code })}
                className={
                  "group inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm transition-colors " +
                  (on
                    ? "border-eligible bg-eligible/10 text-eligible"
                    : "border-rule text-ink hover:border-ink")
                }
              >
                <span>{nameByCode[code]}</span>
                <span className="text-xs uppercase tracking-widest text-ink-muted">
                  {state.olevel_grades[code]}
                </span>
                {isWeak && !on && (
                  <span className="ml-1 text-xs text-seal">(was a weakness)</span>
                )}
              </button>
            );
          })}
        </div>
      )}

      <p className="text-xs text-ink-muted">
        {state.strengths.length} / 3 selected
      </p>

      <NavButtons onBack={onBack} onNext={onNext} />
    </StepShell>
  );
}
