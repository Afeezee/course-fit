"use client";

import { useMemo } from "react";
import { useWizard } from "@/lib/store";
import { CREDIT_GRADES } from "@/lib/eligibility";
import type { Subject } from "@/lib/types";
import { StepShell } from "@/components/ui/StepShell";
import { NavButtons } from "@/components/ui/NavButtons";

export function WeaknessesStep({
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
      index={2}
      total={6}
      title="Where you're least confident"
      hint="Up to two — subjects you passed but wouldn't want a whole degree built around. A subject you picked as a strength can't also be a weakness."
    >
      {eligible.length === 0 ? (
        <p className="rounded-md border border-rule p-4 text-sm text-ink-muted">
          Nothing at credit level yet.
        </p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {eligible.map((code) => {
            const on = state.weaknesses.includes(code);
            const isStrong = state.strengths.includes(code);
            const disabled = isStrong && !on;
            return (
              <button
                key={code}
                type="button"
                aria-pressed={on}
                disabled={disabled}
                onClick={() => dispatch({ type: "TOGGLE_WEAKNESS", subject: code })}
                className={
                  "inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm transition-colors " +
                  (on
                    ? "border-seal bg-seal/10 text-seal"
                    : disabled
                    ? "cursor-not-allowed border-rule text-ink-muted opacity-60"
                    : "border-rule text-ink hover:border-ink")
                }
              >
                <span>{nameByCode[code]}</span>
                <span className="text-xs uppercase tracking-widest text-ink-muted">
                  {state.olevel_grades[code]}
                </span>
                {isStrong && !on && (
                  <span className="ml-1 text-xs text-eligible">(strength)</span>
                )}
              </button>
            );
          })}
        </div>
      )}

      <p className="text-xs text-ink-muted">
        {state.weaknesses.length} / 2 selected — leave empty if none apply.
      </p>

      <NavButtons onBack={onBack} onNext={onNext} />
    </StepShell>
  );
}
