export const SOURCE_LABEL: Record<string, string> = {
  plugin: "Jira ProjectTimesheet",
  plugin_team: "Jira ProjectTimesheet (team)",
};

export function sourceLabel(source: string): string {
  return SOURCE_LABEL[source] ?? source;
}

export function sourceTone(source: string): string {
  if (source === "plugin" || source === "plugin_team") return "ok";
  return "default";
}
