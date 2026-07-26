"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import type { RecentItem } from "@/lib/types";

export function ActivityFeed() {
  const [state, setState] = useState<
    | { kind: "loading" }
    | { kind: "disabled" }
    | { kind: "empty" }
    | { kind: "ok"; items: RecentItem[] }
    | { kind: "error"; detail: string }
  >({ kind: "loading" });

  useEffect(() => {
    api
      .recent(12)
      .then((r) => {
        if (!r.enabled) setState({ kind: "disabled" });
        else if (r.items.length === 0) setState({ kind: "empty" });
        else setState({ kind: "ok", items: r.items });
      })
      .catch((e) => setState({ kind: "error", detail: String(e) }));
  }, []);

  // Persistence off (or fetch error): render nothing — the landing
  // has plenty of other content and this feed is deliberately
  // optional. Silence is better than a broken widget.
  if (state.kind === "disabled" || state.kind === "error") return null;

  return (
    <section aria-labelledby="activity-heading" className="flex flex-col gap-4">
      <header className="flex items-baseline justify-between gap-4 border-b border-rule pb-3">
        <h2
          id="activity-heading"
          className="font-display text-lg font-semibold tracking-tight"
        >
          Latest recommendations
        </h2>
        <p className="text-xs uppercase tracking-[0.18em] text-ink-muted">
          Anonymous outcomes &middot; live
        </p>
      </header>

      {state.kind === "loading" && (
        <ul className="flex flex-col gap-2" aria-hidden>
          {[0, 1, 2, 3].map((i) => (
            <li key={i} className="h-8 animate-pulse rounded bg-rule/60" />
          ))}
        </ul>
      )}

      {state.kind === "empty" && (
        <p className="rounded-md border border-rule p-4 text-sm text-ink-muted">
          No recommendations yet — be the first.
        </p>
      )}

      {state.kind === "ok" && (
        <ol className="flex flex-col divide-y divide-rule">
          {state.items.map((item, i) => (
            <motion.li
              key={item.id}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.28, delay: Math.min(i * 0.03, 0.3) }}
              className="grid grid-cols-[auto_1fr_auto] items-baseline gap-3 py-2.5 text-sm"
            >
              <span className="tabular-nums text-xs text-ink-muted">
                {timeAgo(item.created_at)}
              </span>
              <span className="min-w-0 truncate">
                <span className="text-ink-muted">wanted</span>{" "}
                <span className="text-ink">{item.career_interest}</span>{" "}
                <span className="text-ink-muted">&rarr;</span>{" "}
                <span className="font-medium text-ink">{item.top_course}</span>
              </span>
              <span className="tabular-nums text-xs font-medium text-eligible">
                {Math.round(item.top_probability * 100)}%
              </span>
            </motion.li>
          ))}
        </ol>
      )}

      <p className="text-xs leading-relaxed text-ink-muted">
        Only the anonymous outcome (the field the student wanted plus the top
        course we recommended) is saved. No grades, no personal answers, no
        identifiers.
      </p>
    </section>
  );
}

const RTF = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
const DIVISIONS: Array<[number, Intl.RelativeTimeFormatUnit]> = [
  [60, "second"],
  [60, "minute"],
  [24, "hour"],
  [7, "day"],
  [4.34524, "week"],
  [12, "month"],
  [Number.POSITIVE_INFINITY, "year"],
];

function timeAgo(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "";
  let diff = (then - Date.now()) / 1000;
  for (const [step, unit] of DIVISIONS) {
    if (Math.abs(diff) < step) return RTF.format(Math.round(diff), unit);
    diff /= step;
  }
  return "";
}
