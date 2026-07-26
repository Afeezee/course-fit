"use client";

import Link from "next/link";
import { AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { AUTH_ENABLED } from "@/lib/clerkFlag";
import { api } from "@/lib/api";
import type {
  CoursesResponse,
  Grade,
  RecommendResponse,
  StudentPayload,
} from "@/lib/types";
import { WizardProvider, useWizard } from "@/lib/store";
import { AuthHeader } from "@/components/AuthHeader";
import { EligibilityCounter } from "@/components/EligibilityCounter";
import { ProgressRail } from "@/components/ProgressRail";
import { GradesStep } from "@/components/steps/GradesStep";
import { StrengthsStep } from "@/components/steps/StrengthsStep";
import { WeaknessesStep } from "@/components/steps/WeaknessesStep";
import { InterestsStep } from "@/components/steps/InterestsStep";
import { UtmeSubjectsStep } from "@/components/steps/UtmeSubjectsStep";
import { AptitudeStep } from "@/components/steps/AptitudeStep";
import { ResultsPanel } from "@/components/ResultsPanel";

export default function WizardPage() {
  return (
    <WizardProvider>
      <WizardInner />
    </WizardProvider>
  );
}

function WizardInner() {
  const [meta, setMeta] = useState<CoursesResponse | null>(null);
  const [metaError, setMetaError] = useState<string | null>(null);

  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<RecommendResponse | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { state, dispatch } = useWizard();
  // AUTH_ENABLED is a compile-time constant (backed by
  // NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, inlined at build time), so the
  // branch below is fixed per build — the hook order never changes at
  // runtime. useAuth() would throw when ClerkProvider isn't mounted,
  // hence the shim.
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const clerk = AUTH_ENABLED
    // eslint-disable-next-line react-hooks/rules-of-hooks
    ? useAuth()
    : { getToken: async () => null, isSignedIn: false };
  const { getToken, isSignedIn } = clerk;

  useEffect(() => {
    api
      .courses()
      .then(setMeta)
      .catch((e) => setMetaError(String(e)));
  }, []);

  async function submit() {
    setSubmitting(true);
    setSubmitError(null);
    try {
      const payload: StudentPayload = {
        olevel_grades: state.olevel_grades as Record<string, Grade>,
        utme_subjects: state.utme_subjects,
        strengths: state.strengths,
        weaknesses: state.weaknesses,
        career_interest: state.career_interest ?? "",
        work_environment: state.work_environment ?? "",
        aptitude: state.aptitude,
      };
      // If signed in, attach the Clerk session token so the API can
      // save this submission to the user's history. Anonymous
      // submissions send no token and still work end-to-end.
      const token = isSignedIn ? await getToken() : null;
      const res = await api.recommend(payload, token);
      setResult(res);
    } catch (e) {
      setSubmitError(String(e));
    } finally {
      setSubmitting(false);
    }
  }

  function reset() {
    setResult(null);
    setSubmitError(null);
    dispatch({ type: "RESET" });
  }

  function editAnswers() {
    setResult(null);
  }

  if (metaError) {
    return (
      <ErrorShell
        title="Couldn't reach the recommendation service."
        detail={metaError}
      />
    );
  }
  if (!meta) return <LoadingShell />;

  const showResults = result !== null;

  return (
    <div className="mx-auto grid min-h-dvh max-w-5xl grid-cols-1 gap-8 px-6 py-8 sm:py-12 lg:grid-cols-[220px_minmax(0,1fr)]">
      <aside className="flex flex-col gap-8">
        <div className="flex items-center justify-between gap-3">
          <Link
            href="/"
            className="inline-flex items-baseline gap-2 text-sm text-ink-muted hover:text-ink"
          >
            <span aria-hidden>&larr;</span>
            <span className="font-display font-semibold text-ink">CourseFit</span>
          </Link>
          <div className="lg:hidden">
            <AuthHeader />
          </div>
        </div>
        <div className="hidden lg:block">
          <AuthHeader />
        </div>
        {!showResults && (
          <ProgressRail
            step={state.step}
            onJump={(i) => dispatch({ type: "GO_TO", step: i })}
          />
        )}
      </aside>

      <main className="flex flex-col gap-8">
        {!showResults && (
          <div className="flex justify-end">
            <EligibilityCounter
              courses={meta.courses}
              grades={state.olevel_grades}
              utmeSubjects={state.utme_subjects}
            />
          </div>
        )}

        {submitting ? (
          <SubmittingShell />
        ) : showResults && result ? (
          <ResultsPanel
            data={result}
            onReset={reset}
            onEdit={editAnswers}
            careerInterest={state.career_interest}
          />
        ) : (
          <div className="max-w-measure">
            {submitError && (
              <div className="mb-6 rounded-md border border-seal/40 bg-seal/5 p-4 text-sm text-seal">
                <p className="font-medium">
                  Something went wrong asking the recommender.
                </p>
                <p className="mt-1 text-ink-muted">{submitError}</p>
                <button
                  type="button"
                  onClick={submit}
                  className="mt-3 rounded-full border border-seal px-3 py-1 text-xs text-seal hover:bg-seal hover:text-paper"
                >
                  Try again
                </button>
              </div>
            )}

            <AnimatePresence mode="wait">
              {state.step === 0 && (
                <GradesStep
                  key="grades"
                  subjects={meta.subjects}
                  gradeScale={meta.grade_scale}
                  onNext={() => dispatch({ type: "NEXT" })}
                />
              )}
              {state.step === 1 && (
                <StrengthsStep
                  key="strengths"
                  subjects={meta.subjects}
                  onNext={() => dispatch({ type: "NEXT" })}
                  onBack={() => dispatch({ type: "BACK" })}
                />
              )}
              {state.step === 2 && (
                <WeaknessesStep
                  key="weaknesses"
                  subjects={meta.subjects}
                  onNext={() => dispatch({ type: "NEXT" })}
                  onBack={() => dispatch({ type: "BACK" })}
                />
              )}
              {state.step === 3 && (
                <InterestsStep
                  key="interests"
                  clusters={meta.career_clusters}
                  onNext={() => dispatch({ type: "NEXT" })}
                  onBack={() => dispatch({ type: "BACK" })}
                />
              )}
              {state.step === 4 && (
                <UtmeSubjectsStep
                  key="utme"
                  subjects={meta.subjects}
                  onNext={() => dispatch({ type: "NEXT" })}
                  onBack={() => dispatch({ type: "BACK" })}
                />
              )}
              {state.step === 5 && (
                <AptitudeStep
                  key="aptitude"
                  onNext={submit}
                  onBack={() => dispatch({ type: "BACK" })}
                />
              )}
            </AnimatePresence>
          </div>
        )}
      </main>
    </div>
  );
}

function LoadingShell() {
  return (
    <main className="mx-auto flex min-h-dvh max-w-measure items-center px-6">
      <p className="text-ink-muted">Loading course catalogue&hellip;</p>
    </main>
  );
}

function SubmittingShell() {
  return (
    <div className="flex min-h-[40vh] flex-col justify-center gap-3">
      <p className="text-xs uppercase tracking-[0.2em] text-ink-muted">
        Filtering &amp; ranking
      </p>
      <p className="font-display text-2xl">Checking eligibility and asking the model&hellip;</p>
    </div>
  );
}

function ErrorShell({ title, detail }: { title: string; detail: string }) {
  return (
    <main className="mx-auto flex min-h-dvh max-w-measure flex-col justify-center gap-4 px-6">
      <p className="text-xs uppercase tracking-[0.2em] text-seal">Service unreachable</p>
      <h1 className="font-display text-3xl">{title}</h1>
      <p className="text-sm text-ink-muted">
        The API this app talks to (<code className="rounded bg-rule/50 px-1 py-0.5 text-xs">
          {process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}
        </code>) didn&apos;t answer.
      </p>
      <details className="text-xs text-ink-muted">
        <summary className="cursor-pointer">Technical detail</summary>
        <pre className="mt-2 overflow-auto rounded-md border border-rule p-3 text-[11px]">{detail}</pre>
      </details>
      <Link href="/" className="text-sm underline">
        Back to landing
      </Link>
    </main>
  );
}
