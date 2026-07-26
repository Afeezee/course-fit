import Link from "next/link";
import { ActivityFeed } from "@/components/ActivityFeed";
import { AuthHeader } from "@/components/AuthHeader";

export default function Landing() {
  return (
    <main className="mx-auto flex min-h-dvh max-w-measure flex-col justify-between px-6 py-10 sm:py-16">
      <header className="flex items-center justify-between gap-4">
        <div className="flex items-baseline gap-2">
          <span className="font-display text-xl font-semibold tracking-tight">
            CourseFit
          </span>
          <span aria-hidden className="text-seal">
            &#10023;
          </span>
        </div>
        <div className="flex items-center gap-4">
          <p className="hidden text-xs uppercase tracking-[0.2em] text-ink-muted sm:block">
            UTME 2026 / 2027
          </p>
          <AuthHeader />
        </div>
      </header>

      <section className="my-16 flex flex-col gap-10">
        <div>
          <p className="mb-6 text-xs uppercase tracking-[0.2em] text-ink-muted">
            For a Nigerian UTME candidate
          </p>
          <h1 className="font-display text-4xl leading-[1.05] tracking-tight sm:text-5xl">
            Find the university course
            <br />
            <span className="text-seal">you actually qualify for.</span>
          </h1>
        </div>

        <p className="max-w-prose text-lg leading-relaxed text-ink-muted">
          CourseFit checks your WAEC grades and UTME subjects against real JAMB
          brochure requirements first — then ranks the courses you qualify for
          using a trained model, and shows you why each one fits.
        </p>

        <ul className="grid gap-4 sm:grid-cols-2">
          <FactCard k="50" v="courses currently modelled across all 9 JAMB faculties" />
          <FactCard k="94.1%" v="test-set accuracy on rule-labelled profiles" />
          <FactCard k="0" v="account required — no email, no password" />
          <FactCard k="~2 min" v="from your first grade to your top 3 courses" />
        </ul>

        <p className="text-sm leading-relaxed text-ink-muted">
          Coverage is honest, not total: the JAMB brochure lists several hundred
          course variants across all universities. The 50 courses here are the
          most representative from each faculty, compiled directly from the
          brochure PDFs. Coverage will grow.
        </p>
      </section>

      <div className="flex flex-col gap-4">
        <Link
          href="/wizard"
          className="group inline-flex items-center justify-between rounded-full border border-ink bg-ink px-6 py-4 text-paper transition-colors hover:bg-seal hover:border-seal focus-visible:outline-seal"
        >
          <span className="font-medium">Start — takes about two minutes</span>
          <span aria-hidden className="transition-transform group-hover:translate-x-1">
            &rarr;
          </span>
        </Link>
        <p className="text-xs text-ink-muted">
          Your grades and personal answers stay in this browser tab. Only the
          anonymous outcome (the field you said you wanted plus the course we
          recommended) joins the activity feed below — no grades, no
          identifiers.
        </p>
      </div>

      <div className="mt-16">
        <ActivityFeed />
      </div>

      <footer className="mt-16 border-t border-rule pt-6 text-xs text-ink-muted">
        <p>
          A final-year project by Uche Samuel Ifeanyi (U/23/CS/433),
          Oduduwa University, supervised by Miss Sadare.
        </p>
      </footer>
    </main>
  );
}

function FactCard({ k, v }: { k: string; v: string }) {
  return (
    <li className="rounded-lg border border-rule p-4">
      <div className="font-display text-2xl tracking-tight">{k}</div>
      <div className="mt-1 text-sm text-ink-muted">{v}</div>
    </li>
  );
}
