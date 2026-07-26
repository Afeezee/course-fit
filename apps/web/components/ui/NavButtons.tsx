"use client";

export function NavButtons({
  onBack,
  onNext,
  nextLabel = "Continue",
  nextDisabled = false,
  hideBack = false,
}: {
  onBack?: () => void;
  onNext: () => void;
  nextLabel?: string;
  nextDisabled?: boolean;
  hideBack?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4 pt-4">
      {!hideBack ? (
        <button
          type="button"
          onClick={onBack}
          className="rounded-full border border-rule px-4 py-2 text-sm text-ink-muted transition-colors hover:border-ink hover:text-ink"
        >
          &larr; Back
        </button>
      ) : (
        <span />
      )}
      <button
        type="button"
        onClick={onNext}
        disabled={nextDisabled}
        className="group inline-flex items-center gap-2 rounded-full border border-ink bg-ink px-5 py-2.5 text-sm font-medium text-paper transition-colors hover:bg-seal hover:border-seal disabled:cursor-not-allowed disabled:opacity-40"
      >
        <span>{nextLabel}</span>
        <span aria-hidden className="transition-transform group-hover:translate-x-0.5">
          &rarr;
        </span>
      </button>
    </div>
  );
}
