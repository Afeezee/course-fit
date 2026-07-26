"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useMemo } from "react";
import type { Course, Grade } from "@/lib/types";
import { eligibleCourses, inferUtmeSubjects } from "@/lib/eligibility";

export function EligibilityCounter({
  courses,
  grades,
  utmeSubjects,
}: {
  courses: Course[];
  grades: Record<string, Grade | undefined>;
  // If the student has already explicitly picked UTME subjects in the
  // wizard, use those; otherwise auto-infer from grades so the counter
  // still shows a meaningful number during the earlier steps.
  utmeSubjects?: string[];
}) {
  const { count, total } = useMemo(() => {
    const total = courses.length;
    const gradeCount = Object.keys(grades).length;
    if (gradeCount === 0) return { count: total, total };
    const utme =
      utmeSubjects && utmeSubjects.length > 1
        ? new Set(utmeSubjects)
        : inferUtmeSubjects(grades);
    const eligible = eligibleCourses({ olevel_grades: grades, utme_subjects: utme }, courses);
    return { count: eligible.length, total };
  }, [courses, grades, utmeSubjects]);

  return (
    <div
      role="status"
      aria-live="polite"
      className="inline-flex items-baseline gap-2 rounded-full border border-rule bg-paper/80 px-4 py-2 backdrop-blur"
    >
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={count}
          initial={{ y: 6, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -6, opacity: 0 }}
          transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
          className="font-display text-lg font-semibold tabular-nums text-eligible"
        >
          {count}
        </motion.span>
      </AnimatePresence>
      <span className="text-xs uppercase tracking-[0.18em] text-ink-muted">
        of {total} still possible
      </span>
      <PulseMark trigger={count} />
    </div>
  );
}

function PulseMark({ trigger }: { trigger: number }) {
  return (
    <motion.span
      aria-hidden
      key={`pulse-${trigger}`}
      initial={{ scale: 0.6, opacity: 0.4 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      className="ml-1 text-eligible"
    >
      &#10023;
    </motion.span>
  );
}
