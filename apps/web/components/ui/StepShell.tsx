"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

export function StepShell({
  index,
  total,
  title,
  hint,
  children,
}: {
  index: number;
  total: number;
  title: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <motion.section
      key={index}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -6 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      className="flex flex-col gap-8"
      aria-labelledby={`step-${index}-title`}
    >
      <header className="flex flex-col gap-3">
        <p className="text-xs uppercase tracking-[0.2em] text-ink-muted">
          Step {index + 1} of {total}
        </p>
        <h2 id={`step-${index}-title`} className="font-display text-3xl leading-tight tracking-tight sm:text-4xl">
          {title}
        </h2>
        {hint ? <p className="max-w-prose text-sm leading-relaxed text-ink-muted">{hint}</p> : null}
      </header>
      {children}
    </motion.section>
  );
}
