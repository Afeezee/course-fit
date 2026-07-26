"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useAuth, useUser } from "@clerk/nextjs";
import { AuthHeader } from "@/components/AuthHeader";
import { AUTH_ENABLED } from "@/lib/clerkFlag";
import { api } from "@/lib/api";
import type { HistoryItem } from "@/lib/types";

export default function HistoryPage() {
  // If Clerk isn't configured, this route shouldn't exist — the
  // middleware short-circuits to pass-through and there's no signed-
  // in state to fetch. Render a soft "auth not enabled" message so
  // anyone hitting /history directly sees a coherent explanation.
  if (!AUTH_ENABLED) return <AuthOff />;

  // eslint-disable-next-line react-hooks/rules-of-hooks
  const { getToken, isLoaded, isSignedIn } = useAuth();
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const { user } = useUser();
  const [state, setState] = useState<
    | { kind: "loading" }
    | { kind: "ok"; items: HistoryItem[] }
    | { kind: "error"; detail: string }
  >({ kind: "loading" });

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    (async () => {
      try {
        const token = await getToken();
        if (!token) throw new Error("no session token");
        const res = await api.history(token);
        setState({ kind: "ok", items: res.items });
      } catch (e) {
        setState({ kind: "error", detail: String(e) });
      }
    })();
  }, [isLoaded, isSignedIn, getToken]);

  const firstName = user?.firstName ?? user?.username ?? null;

  return (
    <main className="mx-auto flex min-h-dvh max-w-3xl flex-col gap-10 px-6 py-8 sm:py-12">
      <header className="flex items-center justify-between gap-4">
        <Link
          href="/"
          className="inline-flex items-baseline gap-2 text-sm text-ink-muted hover:text-ink"
        >
          <span aria-hidden>&larr;</span>
          <span className="font-display font-semibold text-ink">CourseFit</span>
        </Link>
        <AuthHeader />
      </header>

      <div className="flex flex-col gap-3">
        <p className="text-xs uppercase tracking-[0.2em] text-ink-muted">Your history</p>
        <h1 className="font-display text-3xl leading-tight tracking-tight sm:text-4xl">
          {firstName ? `${firstName}, here's` : "Here are"} your past
          recommendations
        </h1>
        <p className="text-sm text-ink-muted">
          Only submissions you made while signed in appear here — anonymous runs
          aren&apos;t linked to your account.
        </p>
      </div>

      {state.kind === "loading" && (
        <ul className="flex flex-col gap-3" aria-hidden>
          {[0, 1, 2].map((i) => (
            <li key={i} className="h-24 animate-pulse rounded-lg border border-rule bg-rule/30" />
          ))}
        </ul>
      )}

      {state.kind === "error" && (
        <div className="rounded-md border border-seal/40 bg-seal/5 p-4 text-sm">
          <p className="font-medium text-seal">Couldn&apos;t load your history.</p>
          <p className="mt-1 text-ink-muted">{state.detail}</p>
        </div>
      )}

      {state.kind === "ok" && state.items.length === 0 && (
        <div className="rounded-md border border-rule p-6 text-sm">
          <p className="mb-2 font-medium">No signed-in submissions yet.</p>
          <p className="mb-4 text-ink-muted">
            Run the wizard while signed in and your submission will appear here.
          </p>
          <Link
            href="/wizard"
            className="inline-flex items-center gap-2 rounded-full border border-ink bg-ink px-4 py-2 text-xs font-medium text-paper hover:bg-seal hover:border-seal"
          >
            Start the wizard <span aria-hidden>&rarr;</span>
          </Link>
        </div>
      )}

      {state.kind === "ok" && state.items.length > 0 && (
        <ol className="flex flex-col gap-4">
          {state.items.map((item, i) => (
            <HistoryCard key={item.id} item={item} index={i} />
          ))}
        </ol>
      )}
    </main>
  );
}

function HistoryCard({ item, index }: { item: HistoryItem; index: number }) {
  const recs = item.snapshot?.recommendations ?? [];
  return (
    <motion.li
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: Math.min(index * 0.05, 0.3) }}
      className="rounded-lg border border-rule p-5"
    >
      <div className="mb-3 flex items-baseline justify-between gap-3 text-xs">
        <span className="uppercase tracking-widest text-ink-muted">
          {formatDate(item.created_at)}
        </span>
        <span className="text-ink-muted">
          wanted <span className="text-ink">{item.career_interest}</span>
        </span>
      </div>
      <h2 className="font-display text-xl leading-tight tracking-tight">
        {item.top_course}{" "}
        <span className="font-sans text-sm tabular-nums text-eligible">
          {Math.round(item.top_probability * 100)}%
        </span>
      </h2>
      <p className="mt-1 text-xs text-ink-muted">
        {item.top_faculty} &middot; {item.top_cluster} &middot;{" "}
        {item.eligible_count} eligible course{item.eligible_count === 1 ? "" : "s"}
      </p>

      {recs.length > 1 && (
        <details className="mt-4 text-sm">
          <summary className="cursor-pointer text-xs uppercase tracking-widest text-ink-muted hover:text-ink">
            See all {recs.length} recommendations
          </summary>
          <ol className="mt-3 flex flex-col gap-3">
            {recs.map((r, ri) => (
              <li key={ri} className="border-l-2 border-rule pl-3 text-sm">
                <p className="text-xs uppercase tracking-widest text-ink-muted">
                  #{ri + 1} &middot; {Math.round(r.probability * 100)}%
                </p>
                <p className="font-medium">{r.course}</p>
                <p className="mt-1 text-ink-muted">{r.explanation}</p>
              </li>
            ))}
          </ol>
        </details>
      )}
    </motion.li>
  );
}

function AuthOff() {
  return (
    <main className="mx-auto flex min-h-dvh max-w-measure flex-col justify-center gap-4 px-6">
      <p className="text-xs uppercase tracking-[0.2em] text-ink-muted">
        Sign-in not configured
      </p>
      <h1 className="font-display text-3xl">
        This deploy is running in anonymous-only mode.
      </h1>
      <p className="text-sm text-ink-muted">
        Per-user history requires Clerk keys in the environment. Ask whoever
        set up this deploy to add <code className="rounded bg-rule/50 px-1 py-0.5 text-xs">NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY</code>{" "}
        and <code className="rounded bg-rule/50 px-1 py-0.5 text-xs">CLERK_SECRET_KEY</code> to <code className="rounded bg-rule/50 px-1 py-0.5 text-xs">apps/web/.env.local</code>.
      </p>
      <Link href="/" className="text-sm underline">
        Back to landing
      </Link>
    </main>
  );
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}
