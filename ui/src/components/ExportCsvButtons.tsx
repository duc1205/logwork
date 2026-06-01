interface ExportCsvButtonsProps {
  exporting: "summary" | "compensation" | null;
  disabled?: boolean;
  isQa: boolean;
  onExport: (kind: "summary" | "compensation") => void;
}

export function ExportCsvButtons({
  exporting,
  disabled,
  isQa,
  onExport,
}: ExportCsvButtonsProps) {
  return (
    <div className="export-actions">
      <button
        type="button"
        className="btn-secondary btn-sm"
        disabled={disabled || !!exporting}
        onClick={() => onExport("summary")}
      >
        {exporting === "summary" ? "Đang tải…" : isQa ? "Export CSV team" : "Export CSV của tôi"}
      </button>
      <button
        type="button"
        className="btn-secondary btn-sm"
        disabled={disabled || !!exporting}
        onClick={() => onExport("compensation")}
      >
        {exporting === "compensation" ? "Đang tải…" : isQa ? "Export bù trừ team" : "Export bù trừ"}
      </button>
    </div>
  );
}
