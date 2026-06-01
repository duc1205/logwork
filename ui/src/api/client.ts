import { apiUrl } from "./base";
import type {
  AuditSettings,
  GoldenCompareResult,
  HeatmapData,
  HolidaysList,
  JiraAccountOption,
  NotificationList,
  OtRules,
  OvertimeList,
  PredictiveData,
  ScheduleInfo,
  TokenResponse,
  UserInfo,
  WeeklySummary,
} from "./types";

const TOKEN_KEY = "logwork_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function handleUnauthorized(): void {
  clearToken();
  const loginPath = `${import.meta.env.BASE_URL}login`;
  if (!window.location.pathname.endsWith("/login")) {
    window.location.assign(`${loginPath}?expired=1`);
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };
  const isForm = options.body instanceof FormData;
  if (!isForm) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(apiUrl(path), { ...options, headers });
  if (res.status === 401) {
    handleUnauthorized();
    throw new ApiError(401, "Phiên đăng nhập hết hạn");
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = parseErrorBody(body as Record<string, unknown>);
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, String(detail));
  }
  return res.json() as Promise<T>;
}

function parseErrorBody(body: Record<string, unknown>): string {
  const raw = body.detail;
  const detail =
    typeof raw === "string"
      ? raw
      : Array.isArray(raw)
        ? raw.map((x) => (typeof x === "object" && x && "msg" in x ? String((x as { msg: string }).msg) : String(x))).join("; ")
        : "Lỗi API";
  const jira = body.jira_error ? String(body.jira_error) : "";
  const hint = body.hint ? String(body.hint) : "";
  let msg = jira && jira !== detail ? `${detail} (${jira})` : detail;
  if (hint && !msg.includes(hint)) msg += ` — ${hint}`;
  return msg;
}

export const api = {
  login(username: string, password: string): Promise<TokenResponse> {
    return request<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
  },

  me(): Promise<UserInfo> {
    return request<UserInfo>("/api/auth/me");
  },

  summary(periodQuery?: string, account?: string): Promise<WeeklySummary> {
    const params = new URLSearchParams(periodQuery ?? "");
    if (account) params.set("account", account);
    const q = params.toString() ? `?${params.toString()}` : "";
    return request<WeeklySummary>(`/api/dashboard/summary${q}`);
  },

  allSummaries(periodQuery?: string): Promise<WeeklySummary[]> {
    const q = periodQuery ? `?${periodQuery}` : "";
    return request<WeeklySummary[]>(`/api/dashboard/summaries${q}`);
  },

  heatmap(periodQuery?: string): Promise<HeatmapData> {
    const q = periodQuery ? `?${periodQuery}` : "";
    return request(`/api/dashboard/heatmap${q}`);
  },

  predictive(periodQuery?: string): Promise<PredictiveData> {
    const q = periodQuery ? `?${periodQuery}` : "";
    return request<PredictiveData>(`/api/dashboard/predictive${q}`);
  },

  async goldenCompare(file: File, periodQuery: string): Promise<GoldenCompareResult> {
    const token = getToken();
    const fd = new FormData();
    fd.append("file", file);
    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;
    const q = periodQuery ? `?${periodQuery}` : "";
    const res = await fetch(apiUrl(`/api/admin/golden/compare${q}`), {
      method: "POST",
      headers,
      body: fd,
    });
    if (res.status === 401) {
      handleUnauthorized();
      throw new ApiError(401, "Phiên đăng nhập hết hạn");
    }
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = parseErrorBody(body as Record<string, unknown>);
      } catch {
        /* ignore */
      }
      throw new ApiError(res.status, String(detail));
    }
    return res.json() as Promise<GoldenCompareResult>;
  },

  async goldenValidate(file: File): Promise<{ rows: number; errors: string[]; warnings: string[]; ok: boolean }> {
    const token = getToken();
    const fd = new FormData();
    fd.append("file", file);
    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;
    const res = await fetch(apiUrl("/api/admin/golden/validate"), {
      method: "POST",
      headers,
      body: fd,
    });
    if (res.status === 401) {
      handleUnauthorized();
      throw new ApiError(401, "Phiên đăng nhập hết hạn");
    }
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = parseErrorBody(body as Record<string, unknown>);
      } catch {
        /* ignore */
      }
      throw new ApiError(res.status, String(detail));
    }
    return res.json() as Promise<{ rows: number; errors: string[]; warnings: string[]; ok: boolean }>;
  },

  notifications(periodQuery?: string, refresh?: boolean): Promise<NotificationList> {
    const params = new URLSearchParams(periodQuery ?? "");
    if (refresh) params.set("refresh", "true");
    const q = params.toString() ? `?${params.toString()}` : "";
    return request<NotificationList>(`/api/notifications${q}`);
  },

  purgeNotifications(): Promise<{ purged: number; message: string }> {
    return request("/api/notifications/purge", { method: "POST" });
  },

  schedule(): Promise<ScheduleInfo> {
    return request<ScheduleInfo>("/api/schedule");
  },

  health(): Promise<{
    status: string;
    mode: string;
    data_dir: string;
    config_ready?: boolean;
  }> {
    return request("/api/health");
  },

  triggerReminders(): Promise<Record<string, unknown>> {
    return request("/api/notifications/trigger", { method: "POST" });
  },

  auditSettings(): Promise<AuditSettings> {
    return request<AuditSettings>("/api/admin/settings/audit");
  },

  updateAuditSettings(body: {
    penalty_per_md?: number;
    tolerance_hours?: number;
    compensation_threshold?: number;
  }): Promise<AuditSettings> {
    return request<AuditSettings>("/api/admin/settings/audit", {
      method: "PUT",
      body: JSON.stringify(body),
    });
  },

  holidays(): Promise<HolidaysList> {
    return request<HolidaysList>("/api/admin/settings/holidays");
  },

  addHoliday(body: { holiday_date: string; name: string; is_company_wide?: boolean }): Promise<HolidaysList> {
    return request<HolidaysList>("/api/admin/settings/holidays", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  deleteHoliday(holidayDate: string): Promise<HolidaysList> {
    return request<HolidaysList>(`/api/admin/settings/holidays/${holidayDate}`, {
      method: "DELETE",
    });
  },

  jiraEmployees(q?: string): Promise<{ total: number; items: JiraAccountOption[] }> {
    const params = q ? `?q=${encodeURIComponent(q)}` : "";
    return request(`/api/dashboard/employees${params}`);
  },

  updateOtRules(body: Partial<OtRules>): Promise<OtRules> {
    return request<OtRules>("/api/admin/settings/ot-rules", {
      method: "PUT",
      body: JSON.stringify(body),
    });
  },

  overtime(): Promise<OvertimeList> {
    return request<OvertimeList>("/api/admin/settings/overtime");
  },

  addOvertime(body: {
    employee_id: string;
    ot_date: string;
    ot_hours: number;
    reason?: string;
    status?: string;
    approved_by?: string;
  }): Promise<OvertimeList> {
    return request<OvertimeList>("/api/admin/settings/overtime", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  deleteOvertime(employeeId: string, otDate: string): Promise<OvertimeList> {
    return request<OvertimeList>(`/api/admin/settings/overtime/${employeeId}/${otDate}`, {
      method: "DELETE",
    });
  },

  async downloadExport(kind: "summary" | "compensation", periodQuery?: string): Promise<void> {
    const token = getToken();
    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;
    const q = periodQuery ? `?${periodQuery}` : "";
    const res = await fetch(apiUrl(`/api/dashboard/export/${kind}${q}`), { headers });
    if (res.status === 401) {
      handleUnauthorized();
      throw new ApiError(401, "Phiên đăng nhập hết hạn");
    }
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = parseErrorBody(body as Record<string, unknown>);
      } catch {
        /* ignore */
      }
      throw new ApiError(res.status, String(detail));
    }
    const blob = await res.blob();
    const dispo = res.headers.get("Content-Disposition") ?? "";
    const match = /filename="([^"]+)"/.exec(dispo);
    const filename = match?.[1] ?? `logwork_${kind}.csv`;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  },
};

export { ApiError };
