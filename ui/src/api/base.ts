/** URL backend — dev: Vite proxy `/api`; production: env hoặc `public/config.json`. */

export interface ApiRuntimeConfig {
  apiBaseUrl: string;
}

let resolvedBase = "";

function normalizeBase(url: string): string {
  return url.trim().replace(/\/$/, "");
}

/** Gọi một lần trước khi render app (main.tsx). */
export async function initApiConfig(): Promise<void> {
  if (import.meta.env.DEV) {
    resolvedBase = "";
    return;
  }

  const fromEnv = normalizeBase(import.meta.env.VITE_API_BASE_URL ?? "");
  if (fromEnv) {
    resolvedBase = fromEnv;
    return;
  }

  try {
    const cfgUrl = new URL("config.json", window.location.href).href;
    const res = await fetch(cfgUrl, { cache: "no-store" });
    if (res.ok) {
      const cfg = (await res.json()) as ApiRuntimeConfig;
      const fromFile = normalizeBase(cfg.apiBaseUrl ?? "");
      if (fromFile) {
        resolvedBase = fromFile;
      }
    }
  } catch {
    /* config.json tùy chọn */
  }
}

export function apiBaseUrl(): string {
  return resolvedBase;
}

export function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return resolvedBase ? `${resolvedBase}${p}` : p;
}

/** Nhãn hiển thị trên UI — kiểm tra UI đang gọi BE nào. */
export function apiEndpointLabel(): string {
  if (import.meta.env.DEV) {
    return "Vite proxy /api → http://127.0.0.1:8001";
  }
  if (resolvedBase) {
    return resolvedBase;
  }
  return "Chưa kết nối — chạy API :8001 và npm run dev (hoặc npm run preview)";
}
