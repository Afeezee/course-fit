"use client";

import { useWizard } from "@/lib/store";
import { StepShell } from "@/components/ui/StepShell";
import { NavButtons } from "@/components/ui/NavButtons";

export function InterestsStep({
  clusters,
  onNext,
  onBack,
}: {
  clusters: string[];
  onNext: () => void;
  onBack: () => void;
}) {
  const { state, dispatch } = useWizard();
  const canContinue = state.career_interest !== null && state.work_environment !== null;

  return (
    <StepShell
      index={3}
      total={6}
      title="What you want to work on"
      hint="Two questions. Pick the closest match — none of these will be a perfect fit for any real person, and that's fine."
    >
      <div className="flex flex-col gap-4">
        <fieldset>
          <legend className="mb-3 text-sm font-medium">
            Which of these is closest to what you'd want to spend your career on?
          </legend>
          <ClusterChoices
            name="career_interest"
            clusters={clusters}
            value={state.career_interest}
            onChange={(v) => dispatch({ type: "SET_CAREER_INTEREST", value: v })}
          />
        </fieldset>

        <fieldset>
          <legend className="mb-3 text-sm font-medium">
            And where would you rather spend your working day?
          </legend>
          <ClusterChoices
            name="work_environment"
            clusters={clusters}
            value={state.work_environment}
            onChange={(v) => dispatch({ type: "SET_WORK_ENVIRONMENT", value: v })}
          />
        </fieldset>
      </div>

      <NavButtons onBack={onBack} onNext={onNext} nextDisabled={!canContinue} />
    </StepShell>
  );
}

function ClusterChoices({
  name,
  clusters,
  value,
  onChange,
}: {
  name: string;
  clusters: string[];
  value: string | null;
  onChange: (v: string) => void;
}) {
  return (
    <div className="grid gap-2 sm:grid-cols-2">
      {clusters.map((c) => {
        const on = value === c;
        return (
          <label
            key={c}
            className={
              "cursor-pointer rounded-md border px-3 py-3 text-sm transition-colors " +
              (on
                ? "border-ink bg-ink/5"
                : "border-rule hover:border-ink")
            }
          >
            <input
              type="radio"
              name={name}
              value={c}
              checked={on}
              onChange={() => onChange(c)}
              className="sr-only"
            />
            <span className="block font-medium">{c}</span>
          </label>
        );
      })}
    </div>
  );
}
