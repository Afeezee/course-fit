import type {
  CoursesResponse,
  HistoryResponse,
  RecentResponse,
  RecommendResponse,
  StudentPayload,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function j<T>(path: string, init?: RequestInit, token?: string | null): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${body || path}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  courses: () => j<CoursesResponse>("/api/courses"),
  recommend: (payload: StudentPayload, token?: string | null) =>
    j<RecommendResponse>(
      "/api/recommend",
      { method: "POST", body: JSON.stringify(payload) },
      token,
    ),
  recent: (limit = 12) => j<RecentResponse>(`/api/recent?limit=${limit}`),
  history: (token: string, limit = 25) =>
    j<HistoryResponse>(`/api/history?limit=${limit}`, undefined, token),
};
