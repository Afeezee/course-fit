"use client";

const LABELS = ["Grades", "Strengths", "Weaknesses", "Interests", "UTME subjects", "Aptitude"];

type Step = 0 | 1 | 2 | 3 | 4 | 5;

export function ProgressRail({
  step,
  onJump,
}: {
  step: Step;
  onJump: (i: Step) => void;
}) {
  return (
    <nav aria-label="Wizard steps" className="hidden lg:block">
      <ol className="sticky top-24 flex flex-col gap-6 border-l border-rule pl-6">
        {LABELS.map((label, i) => {
          const done = i < step;
          const current = i === step;
          const reachable = i <= step; // no jump-ahead
          return (
            <li key={label} className="relative">
              <span
                aria-hidden
                className={
                  "absolute -left-[27px] top-1 h-2.5 w-2.5 rounded-full transition-colors " +
                  (current
                    ? "bg-seal"
                    : done
                    ? "bg-ink"
                    : "border border-ink/30 bg-paper")
                }
              />
              <button
                type="button"
                disabled={!reachable}
                onClick={() => reachable && onJump(i as Step)}
                className={
                  "block text-left text-sm transition-colors " +
                  (current
                    ? "font-medium text-ink"
                    : done
                    ? "text-ink hover:text-seal"
                    : "text-ink-muted")
                }
              >
                <span className="mr-2 tabular-nums text-xs uppercase tracking-widest text-ink-muted">
                  {String(i + 1).padStart(2, "0")}
                </span>
                {label}
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
