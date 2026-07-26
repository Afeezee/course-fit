"use client";

import { motion } from "framer-motion";
import type { RecommendResponse } from "@/lib/types";

export function ResultsPanel({
  data,
  onReset,
  onEdit,
  careerInterest,
}: {
  data: RecommendResponse;
  onReset: () => void;
  onEdit: () => void;
  careerInterest: string | null;
}) {
  if (data.status === "no_eligible_courses") {
    return (
      <motion.section
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="flex flex-col gap-6"
      >
        <p className="text-xs uppercase tracking-[0.2em] text-ink-muted">Result</p>
        <h2 className="font-display text-3xl leading-tight tracking-tight sm:text-4xl">
          Nothing in the current catalogue matches these grades yet.
        </h2>
        <p className="max-w-prose text-ink-muted">
          Every one of the 50 courses currently modelled needs a specific set of
          O-Level credits or UTME subjects that these answers don&apos;t cover.
          This is JAMB&apos;s eligibility rule, not an opinion — a real
          registration would be rejected too. The two useful moves from here
          are to sit an extra WAEC subject in the next diet, or to talk to a
          school counsellor about a foundation / diploma programme first.
        </p>
        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={onEdit}
            className="rounded-full border border-rule px-4 py-2 text-sm text-ink-muted hover:border-ink hover:text-ink"
          >
            &larr; Edit my answers
          </button>
          <button
            type="button"
            onClick={onReset}
            className="rounded-full border border-ink bg-ink px-4 py-2 text-sm text-paper hover:bg-seal hover:border-seal"
          >
            Start over
          </button>
        </div>
      </motion.section>
    );
  }

  const recs = data.recommendations;
  const tooFew = data.eligible_count <= 2;
  const interestMismatch =
    careerInterest !== null &&
    recs.length > 0 &&
    recs[0].career_cluster !== careerInterest;

  return (
    <section className="flex flex-col gap-8">
      <motion.header
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="flex flex-col gap-3"
      >
        <p className="text-xs uppercase tracking-[0.2em] text-ink-muted">Your top 3</p>
        <h2 className="font-display text-3xl leading-tight tracking-tight sm:text-4xl">
          Ranked from the {data.eligible_count} course
          {data.eligible_count === 1 ? "" : "s"} you qualify for
        </h2>
        <p className="text-sm text-ink-muted">
          Ordered by <span className="font-medium">{data.model_name ?? "the ranking model"}</span>.{" "}
          {data.explanation_source === "llm" ? (
            <>
              Explanations personalised to your profile by an LLM (Groq /
              Llama); the ranking itself is still the deterministic
              rule + ML pipeline.
            </>
          ) : (
            <>Each explanation was produced by the same rule engine that trained the model.</>
          )}
        </p>
      </motion.header>

      {(tooFew || interestMismatch) && (
        <motion.aside
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.1 }}
          className="rounded-md border border-seal/40 bg-seal/5 p-4 text-sm"
        >
          <p className="mb-1 text-xs uppercase tracking-widest text-seal">
            Worth reading before you rely on this
          </p>
          {tooFew && (
            <p className="mb-2 leading-relaxed text-ink">
              Only {data.eligible_count} course{data.eligible_count === 1 ? "" : "s"}{" "}
              matched your grades and UTME subjects. The fit score below reflects
              that scarcity as much as it does the model&apos;s confidence — with
              one option, the model has nothing to compare it against, so 100%
              means &quot;this is what&apos;s left,&quot; not &quot;this is a strong fit.&quot;
              Go back and check the UTME step: adding Physics/Chemistry (for
              science courses) or Government/Literature (for arts) commonly
              opens up 20+ more options.
            </p>
          )}
          {interestMismatch && !tooFew && (
            <p className="leading-relaxed text-ink">
              The top match is in{" "}
              <span className="font-medium">{recs[0].career_cluster}</span>,
              which isn&apos;t the field you said you wanted
              (<span className="font-medium">{careerInterest}</span>). This
              usually means the courses that fit your stated interest aren&apos;t
              eligible under your current O-Level credits or UTME subject choice
              — go back to those steps to see what would need to change.
            </p>
          )}
        </motion.aside>
      )}

      <ol className="flex flex-col gap-4">
        {recs.map((r, i) => (
          <motion.li
            key={r.course}
            initial={{ opacity: 0, y: 12, scale: i === 0 ? 0.97 : 1 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{
              duration: 0.4,
              delay: 0.15 + i * 0.09,
              ease: [0.22, 1, 0.36, 1],
            }}
            className={
              "relative flex flex-col gap-3 rounded-lg border p-6 " +
              (i === 0 ? "border-ink" : "border-rule")
            }
          >
            {i === 0 && (
              <span
                aria-hidden
                className="absolute -top-3 left-6 rounded-full border border-gold bg-paper px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-gold"
              >
                &#10023; Top match
              </span>
            )}
            <div className="flex items-baseline justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-widest text-ink-muted">
                  #{i + 1} &middot; {r.faculty}
                </p>
                <h3 className="font-display text-2xl leading-snug tracking-tight">
                  {r.course}
                </h3>
              </div>
              <FitBar probability={r.probability} highlight={i === 0} />
            </div>
            <p className="text-sm leading-relaxed text-ink">{r.explanation}</p>
            <p className="text-xs uppercase tracking-widest text-ink-muted">
              {r.career_cluster}
            </p>
          </motion.li>
        ))}
      </ol>

      <div className="flex flex-wrap gap-3 pt-2">
        <button
          type="button"
          onClick={onEdit}
          className="rounded-full border border-rule px-4 py-2 text-sm text-ink-muted hover:border-ink hover:text-ink"
        >
          &larr; Adjust an answer
        </button>
        <button
          type="button"
          onClick={onReset}
          className="rounded-full border border-ink bg-ink px-4 py-2 text-sm text-paper hover:bg-seal hover:border-seal"
        >
          Start over
        </button>
      </div>

      <p className="border-t border-rule pt-4 text-xs leading-relaxed text-ink-muted">
        A fit score is the trained model&apos;s predicted probability that this
        course is the single best label for your profile, among the courses
        you&apos;re eligible for. It is a ranking signal, not an admission
        prediction — final admission still depends on each university&apos;s
        cut-off and post-UTME.
      </p>
    </section>
  );
}

function FitBar({ probability, highlight }: { probability: number; highlight: boolean }) {
  const pct = Math.round(probability * 100);
  return (
    <div className="flex flex-col items-end gap-1">
      <span
        className={
          "font-display text-lg tabular-nums " +
          (highlight ? "text-gold" : "text-ink")
        }
      >
        {pct}%
      </span>
      <span className="text-[10px] uppercase tracking-widest text-ink-muted">
        fit score
      </span>
    </div>
  );
}
