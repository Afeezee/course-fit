// Shape mirrors apps/api/main.py's CoursesResponse / RecommendResponse.
// Keep this file in sync with the API's Pydantic models — they are the
// source of truth.

export type Grade =
  | "A1" | "B2" | "B3" | "C4" | "C5" | "C6"
  | "D7" | "E8" | "F9";

export interface Course {
  course: string;
  faculty: string;
  career_cluster: string;
  utme_subjects: string[];
  utme_alt_subject: string | null;
  olevel_subjects: string[];
  // The API doesn't currently ship olevel_pass_subjects on /api/courses,
  // so the client-side eligibility filter treats every course's
  // olevel_subjects as credit-required. This is deliberately stricter
  // than the real server-side filter — the client counter may under-
  // count Political Science / Psychology / Sociology / Geography for
  // students with only a pass in Math. The recommend call re-runs the
  // full server filter, so the final result is correct; only the live
  // counter is slightly conservative. See lib/eligibility.ts.
}

export interface Subject {
  code: string;
  name: string;
}

export interface CoursesResponse {
  courses: Course[];
  subjects: Subject[];
  career_clusters: string[];
  credit_grades: Grade[];
  grade_scale: Grade[];
  faculties: string[];
}

export interface StudentPayload {
  olevel_grades: Record<string, Grade>;
  utme_subjects: string[];
  strengths: string[];
  weaknesses: string[];
  career_interest: string;
  work_environment: string;
  aptitude: 1 | 2 | 3 | 4 | 5;
}

export interface Recommendation {
  course: string;
  faculty: string;
  career_cluster: string;
  probability: number;
  explanation: string;
}

export interface RecommendResponse {
  status: "ok" | "no_eligible_courses";
  recommendations: Recommendation[];
  eligible_count: number;
  model_name: string | null;
  // "template" = deterministic explanation from ml/recommend.py.
  // "llm" = Groq-generated per-student explanation (upgrade path).
  explanation_source: "template" | "llm";
}

export interface RecentItem {
  id: number;
  created_at: string;
  career_interest: string;
  eligible_count: number;
  top_course: string;
  top_faculty: string;
  top_cluster: string;
  top_probability: number;
}

export interface RecentResponse {
  enabled: boolean;
  items: RecentItem[];
}

export interface HistoryItem {
  id: number;
  created_at: string;
  career_interest: string;
  eligible_count: number;
  top_course: string;
  top_faculty: string;
  top_cluster: string;
  top_probability: number;
  explanation_source: string;
  snapshot: {
    profile: StudentPayload;
    recommendations: Recommendation[];
  } | null;
}

export interface HistoryResponse {
  items: HistoryItem[];
}
