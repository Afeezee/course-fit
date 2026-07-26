"use client";

import { useMemo, useState } from "react";
import { useWizard } from "@/lib/store";
import type { Grade, Subject } from "@/lib/types";
import { StepShell } from "@/components/ui/StepShell";
import { NavButtons } from "@/components/ui/NavButtons";

// Subject grouping matches the JAMB brochure's rough clustering so a
// student can scan by category on mobile rather than parsing a 14-row
// alphabetical wall.
const SUBJECT_GROUPS: { title: string; codes: string[] }[] = [
  { title: "Compulsory", codes: ["ENG", "MTH"] },
  { title: "Sciences", codes: ["PHY", "CHM", "BIO"] },
  { title: "Social Sciences", codes: ["ECO", "GEO", "GOV", "HIS"] },
  { title: "Arts", codes: ["LIT", "FRN"] },
  { title: "Business", codes: ["ACC", "COM"] },
  { title: "Agriculture & Faith", codes: ["AGR", "ARA", "ISL"] },
];

export function GradesStep({
  subjects,
  gradeScale,
  onNext,
}: {
  subjects: Subject[];
  gradeScale: Grade[];
  onNext: () => void;
}) {
  const { state, dispatch } = useWizard();
  const [query, setQuery] = useState("");

  const nameByCode = useMemo(() => Object.fromEntries(subjects.map((s) => [s.code, s.name])), [subjects]);

  const gradedCount = Object.keys(state.olevel_grades).length;
  const engGrade = state.olevel_grades["ENG"];
  const canContinue = engGrade !== undefined && gradedCount >= 4;

  const q = query.trim().toLowerCase();
  const matches = (code: string) =>
    !q ||
    code.toLowerCase().includes(q) ||
    (nameByCode[code] ?? "").toLowerCase().includes(q);

  return (
    <StepShell
      index={0}
      total={6}
      title="Your WAEC / SSCE grades"
      hint="Enter a grade for every subject you sat. Leave the others blank. English and Mathematics are compulsory for almost every JAMB course."
    >
      <label className="flex flex-col gap-2">
        <span className="text-xs uppercase tracking-widest text-ink-muted">
          Filter subjects
        </span>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type to filter e.g. physics, ECO"
          className="rounded-md border border-rule bg-transparent px-3 py-2 text-sm focus:border-ink focus:outline-none"
        />
      </label>

      <div className="flex flex-col gap-6">
        {SUBJECT_GROUPS.map((group) => {
          const codes = group.codes.filter((c) => nameByCode[c] && matches(c));
          if (codes.length === 0) return null;
          return (
            <div key={group.title}>
              <p className="mb-2 text-xs uppercase tracking-widest text-ink-muted">
                {group.title}
              </p>
              <div className="grid gap-2">
                {codes.map((code) => (
                  <GradeRow
                    key={code}
                    code={code}
                    name={nameByCode[code]}
                    scale={gradeScale}
                    value={state.olevel_grades[code]}
                    onChange={(g) => dispatch({ type: "SET_GRADE", subject: code, grade: g })}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {!engGrade && gradedCount > 0 && (
        <p className="text-sm text-seal">
          You need a grade for English — no JAMB course accepts a student without an English result.
        </p>
      )}

      <NavButtons
        hideBack
        onNext={onNext}
        nextDisabled={!canContinue}
        nextLabel={canContinue ? "Continue" : "Enter English + 3 more"}
      />
    </StepShell>
  );
}

function GradeRow({
  code,
  name,
  scale,
  value,
  onChange,
}: {
  code: string;
  name: string;
  scale: Grade[];
  value: Grade | undefined;
  onChange: (g: Grade | undefined) => void;
}) {
  const id = `grade-${code}`;
  return (
    <div className="flex items-center justify-between gap-3 border-b border-rule py-2 last:border-b-0">
      <label htmlFor={id} className="text-sm">
        <span className="font-medium">{name}</span>
        <span className="ml-2 text-xs uppercase tracking-widest text-ink-muted">{code}</span>
      </label>
      <select
        id={id}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value === "" ? undefined : (e.target.value as Grade))}
        className="rounded-md border border-rule bg-transparent px-2 py-1 text-sm tabular-nums focus:border-ink focus:outline-none"
      >
        <option value="">— didn&apos;t sit</option>
        {scale.map((g) => (
          <option key={g} value={g}>
            {g}
          </option>
        ))}
      </select>
    </div>
  );
}
