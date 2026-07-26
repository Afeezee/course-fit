"use client";

import { useWizard } from "@/lib/store";
import { StepShell } from "@/components/ui/StepShell";
import { NavButtons } from "@/components/ui/NavButtons";

const LABELS = [
  "I actively avoid it.",
  "Slow going for me.",
  "Comfortable, if I focus.",
  "One of my stronger areas.",
  "It's how I think.",
];

export function AptitudeStep({
  onNext,
  onBack,
  nextLabel = "See my top courses",
}: {
  onNext: () => void;
  onBack: () => void;
  nextLabel?: string;
}) {
  const { state, dispatch } = useWizard();
  const v = state.aptitude;

  return (
    <StepShell
      index={5}
      total={6}
      title="Quantitative aptitude"
      hint="A rough self-rating on how you handle problems with numbers, equations, and formal reasoning. The model uses this to soften recommendations for engineering and physical-science courses when it isn't your strong suit."
    >
      <div className="flex flex-col gap-4">
        <input
          type="range"
          min={1}
          max={5}
          step={1}
          value={v}
          onChange={(e) => dispatch({ type: "SET_APTITUDE", value: Number(e.target.value) as 1 | 2 | 3 | 4 | 5 })}
          aria-valuemin={1}
          aria-valuemax={5}
          aria-valuenow={v}
          aria-label="Quantitative aptitude 1 to 5"
          className="w-full accent-ink"
        />
        <div className="flex items-baseline justify-between text-xs uppercase tracking-widest text-ink-muted">
          <span>1</span>
          <span>2</span>
          <span>3</span>
          <span>4</span>
          <span>5</span>
        </div>
        <p className="rounded-md border border-rule p-4">
          <span className="font-display text-2xl tabular-nums text-seal">{v}</span>
          <span className="ml-3 text-sm text-ink-muted">{LABELS[v - 1]}</span>
        </p>
      </div>

      <NavButtons onBack={onBack} onNext={onNext} nextLabel={nextLabel} />
    </StepShell>
  );
}
