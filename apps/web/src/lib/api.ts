const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type User = {
  id: string;
  telegram_id: number;
  username?: string;
  first_name?: string;
  locale: string;
  timezone: string;
  is_premium: boolean;
  onboarding_done: boolean;
  profile?: {
    city?: string;
    quiet_hours_start?: string;
    quiet_hours_end?: string;
    notify_streak_nudge: boolean;
    notify_cycle: boolean;
    notify_bills: boolean;
    notify_digest: boolean;
  };
};

async function request<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const detail = await res.text();
    const err = new Error(detail || res.statusText) as Error & { status?: number };
    err.status = res.status;
    throw err;
  }
  return res.json() as Promise<T>;
}

export const api = {
  auth: (initData: string) =>
    request<{ access_token: string; user: User }>("/api/auth/telegram", {
      method: "POST",
      body: JSON.stringify({ initData }),
    }),
  me: (token: string) => request<User>("/api/me", {}, token),
  patchMe: (token: string, body: Record<string, unknown>) =>
    request<User>("/api/me", { method: "PATCH", body: JSON.stringify(body) }, token),
  home: (token: string) =>
    request<{
      habits_active: number;
      habits_checked_today: number;
      next_bill: { title: string; next_due: string } | null;
      streak_best: number;
      is_premium: boolean;
      digest_enabled: boolean;
    }>("/api/home", {}, token),
  habits: {
    list: (token: string) =>
      request<
        {
          id: string;
          kind: string;
          title: string;
          emoji?: string;
          streak_current: number;
          streak_best: number;
          checked_today: boolean;
        }[]
      >("/api/habits", {}, token),
    create: (token: string, body: { kind: string; title: string; emoji?: string }) =>
      request("/api/habits", { method: "POST", body: JSON.stringify(body) }, token),
    checkin: (token: string, id: string) =>
      request(`/api/habits/${id}/checkin`, { method: "POST" }, token),
  },
  bills: {
    list: (token: string) =>
      request<
        {
          id: string;
          title: string;
          amount?: string;
          currency: string;
          next_due: string;
          warn_days: number;
        }[]
      >("/api/bills", {}, token),
    create: (token: string, body: Record<string, unknown>) =>
      request("/api/bills", { method: "POST", body: JSON.stringify(body) }, token),
    paid: (token: string, id: string) =>
      request(`/api/bills/${id}/paid`, { method: "POST" }, token),
  },
  cycle: {
    get: (token: string) =>
      request<{
        avg_cycle_days: number;
        avg_period_days: number;
        last_start?: string;
        predicted_next?: string;
        reminders_enabled: boolean;
      }>("/api/cycle", {}, token),
    patch: (token: string, body: Record<string, unknown>) =>
      request("/api/cycle", { method: "PATCH", body: JSON.stringify(body) }, token),
    log: (token: string, start_date: string) =>
      request("/api/cycle/log", { method: "POST", body: JSON.stringify({ start_date }) }, token),
  },
  calendar: {
    list: (token: string) =>
      request<{ id: string; title: string; starts_at: string; source: string }[]>(
        "/api/calendar",
        {},
        token
      ),
    create: (token: string, body: Record<string, unknown>) =>
      request("/api/calendar", { method: "POST", body: JSON.stringify(body) }, token),
  },
  digest: {
    prefs: (token: string) => request<Record<string, unknown>>("/api/digest/prefs", {}, token),
    patch: (token: string, body: Record<string, unknown>) =>
      request("/api/digest/prefs", { method: "PATCH", body: JSON.stringify(body) }, token),
    preview: (token: string) => request<{ text: string }>("/api/digest/preview", {}, token),
  },
  billing: {
    plans: (token: string) =>
      request<{ code: string; name: string; stars_price: number }[]>("/api/billing/plans", {}, token),
    status: (token: string) =>
      request<{ is_premium: boolean; status: string; ends_at?: string }>("/api/billing/status", {}, token),
  },
};
