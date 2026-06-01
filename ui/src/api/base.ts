/** Base URL API — dev: proxy `/api`; production (GitHub Pages): `VITE_API_BASE_URL`. */

const raw = (import.meta.env.VITE_API_BASE_URL ?? "").trim().replace(/\/$/, "");

export function apiBaseUrl(): string {
  return raw;
}

export function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return raw ? `${raw}${p}` : p;
}
