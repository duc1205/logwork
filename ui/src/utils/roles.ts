/** Quyền Logwork (env) — không liên quan quyền Administrator trên Jira. */

export function isQaRole(role: string | undefined): boolean {
  return role === "admin" || role === "qa";
}

export function isSettingsAdmin(role: string | undefined): boolean {
  return role === "admin";
}

export function roleLabel(role: string | undefined): string {
  if (role === "admin") return "Cấu hình";
  if (role === "qa") return "QA";
  return "NV";
}
