"use client";

import { createContext, useContext, useReducer, type Dispatch, type ReactNode, createElement } from "react";
import type { Grade } from "./types";

export interface WizardState {
  step: 0 | 1 | 2 | 3 | 4 | 5;
  olevel_grades: Record<string, Grade | undefined>;
  // 4 UTME subjects the student plans to register — English is
  // always required, so the wizard forces ENG and lets the student
  // pick 3 others.
  utme_subjects: string[];
  strengths: string[];
  weaknesses: string[];
  career_interest: string | null;
  work_environment: string | null;
  aptitude: 1 | 2 | 3 | 4 | 5;
}

export const initialState: WizardState = {
  step: 0,
  olevel_grades: {},
  utme_subjects: ["ENG"],
  strengths: [],
  weaknesses: [],
  career_interest: null,
  work_environment: null,
  aptitude: 3,
};

export type Action =
  | { type: "GO_TO"; step: WizardState["step"] }
  | { type: "NEXT" }
  | { type: "BACK" }
  | { type: "SET_GRADE"; subject: string; grade: Grade | undefined }
  | { type: "TOGGLE_UTME"; subject: string }
  | { type: "SET_UTME"; subjects: string[] }
  | { type: "TOGGLE_STRENGTH"; subject: string }
  | { type: "TOGGLE_WEAKNESS"; subject: string }
  | { type: "SET_CAREER_INTEREST"; value: string }
  | { type: "SET_WORK_ENVIRONMENT"; value: string }
  | { type: "SET_APTITUDE"; value: 1 | 2 | 3 | 4 | 5 }
  | { type: "RESET" };

const MAX_STEP: WizardState["step"] = 5;

export function reducer(state: WizardState, a: Action): WizardState {
  switch (a.type) {
    case "GO_TO":
      return { ...state, step: a.step };
    case "NEXT":
      return { ...state, step: Math.min(MAX_STEP, state.step + 1) as WizardState["step"] };
    case "BACK":
      return { ...state, step: Math.max(0, state.step - 1) as WizardState["step"] };
    case "SET_GRADE": {
      const next = { ...state.olevel_grades };
      if (a.grade === undefined) delete next[a.subject];
      else next[a.subject] = a.grade;
      // Dropping a subject invalidates its strength/weakness designation.
      const strengths = state.strengths.filter((s) => next[s] !== undefined);
      const weaknesses = state.weaknesses.filter((s) => next[s] !== undefined);
      return { ...state, olevel_grades: next, strengths, weaknesses };
    }
    case "TOGGLE_UTME": {
      if (a.subject === "ENG") return state; // ENG is compulsory, can't be toggled off
      const on = state.utme_subjects.includes(a.subject);
      if (on) {
        return { ...state, utme_subjects: state.utme_subjects.filter((s) => s !== a.subject) };
      }
      if (state.utme_subjects.length >= 4) return state; // cap at 4
      return { ...state, utme_subjects: [...state.utme_subjects, a.subject] };
    }
    case "SET_UTME":
      return { ...state, utme_subjects: a.subjects };
    case "TOGGLE_STRENGTH": {
      const inList = state.strengths.includes(a.subject);
      if (inList) return { ...state, strengths: state.strengths.filter((s) => s !== a.subject) };
      if (state.strengths.length >= 3) return state;
      return {
        ...state,
        strengths: [...state.strengths, a.subject],
        weaknesses: state.weaknesses.filter((s) => s !== a.subject),
      };
    }
    case "TOGGLE_WEAKNESS": {
      const inList = state.weaknesses.includes(a.subject);
      if (inList) return { ...state, weaknesses: state.weaknesses.filter((s) => s !== a.subject) };
      if (state.weaknesses.length >= 2) return state;
      return {
        ...state,
        weaknesses: [...state.weaknesses, a.subject],
        strengths: state.strengths.filter((s) => s !== a.subject),
      };
    }
    case "SET_CAREER_INTEREST":
      return { ...state, career_interest: a.value };
    case "SET_WORK_ENVIRONMENT":
      return { ...state, work_environment: a.value };
    case "SET_APTITUDE":
      return { ...state, aptitude: a.value };
    case "RESET":
      return initialState;
  }
}

const WizardCtx = createContext<{
  state: WizardState;
  dispatch: Dispatch<Action>;
} | null>(null);

export function WizardProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return createElement(WizardCtx.Provider, { value: { state, dispatch } }, children);
}

export function useWizard() {
  const v = useContext(WizardCtx);
  if (!v) throw new Error("useWizard must be inside <WizardProvider>");
  return v;
}
