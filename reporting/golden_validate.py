"""So khớp báo cáo với golden file QA (CSV/Excel export)."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path

from ..domain.penalty import DEFAULT_PENALTY_PER_MD


@dataclass
class GoldenRow:
    account: str
    actual_md: float
    required_md: float
    missed_md: float
    penalty: int


def _parse_float(s: str) -> float:
    return float(s.strip().replace(",", ""))


def _parse_int(s: str) -> int:
    return int(float(s.strip().replace(",", "")))


def load_golden_csv(path: Path) -> list[GoldenRow]:
    return load_golden_csv_text(path.read_text(encoding="utf-8-sig"))


def load_golden_csv_text(text: str) -> list[GoldenRow]:
    rows: list[GoldenRow] = []

    with io.StringIO(text) as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return rows
        fields = {h.strip().lower(): h for h in reader.fieldnames}

        def col(*names: str) -> str | None:
            for n in names:
                if n.lower() in fields:
                    return fields[n.lower()]
            return None

        c_account = col("account")
        c_actual = col("actual (md)", "actual")
        c_required = col("required (md)", "required")
        c_missed = col("missed (md)", "missed")
        c_penalty = col("penalty (vnd)", "penalty", "trừ phụ cấp kinh doanh (dự kiến)")

        if not all([c_account, c_actual, c_required, c_missed, c_penalty]):
            raise ValueError(f"Thieu cot bat buoc: {reader.fieldnames}")

        for row in reader:
            acc = row[c_account].strip()
            if not acc:
                continue
            rows.append(
                GoldenRow(
                    account=acc,
                    actual_md=_parse_float(row[c_actual]),
                    required_md=_parse_float(row[c_required]),
                    missed_md=_parse_float(row[c_missed]),
                    penalty=_parse_int(row[c_penalty]),
                )
            )
    return rows


def golden_rows_to_map(rows: list[GoldenRow]) -> dict[str, GoldenRow]:
    return {r.account: r for r in rows}


def report_to_golden_map(report) -> dict[str, GoldenRow]:
    """Chuyển WeeklyReport → map Account → GoldenRow (cho so khớp QA)."""
    from ..domain.penalty import hours_to_md

    out: dict[str, GoldenRow] = {}
    for s in report.summaries:
        out[s.employee_id] = GoldenRow(
            account=s.employee_id,
            actual_md=round(hours_to_md(s.actual_hours), 2),
            required_md=round(hours_to_md(s.required_hours), 2),
            missed_md=round(hours_to_md(s.missed_hours), 2),
            penalty=s.penalty,
        )
    return out


def compare_golden_maps(
    engine: dict[str, GoldenRow],
    golden: dict[str, GoldenRow],
    *,
    tolerance_md: float = 0.02,
) -> tuple[list[str], list[str]]:
    """So từng Account — logic giống compare_engine_to_golden nhưng in-memory."""
    errors: list[str] = []
    warnings: list[str] = []
    all_accounts = set(engine) | set(golden)
    for acc in sorted(all_accounts):
        e = engine.get(acc)
        g = golden.get(acc)
        if e is None:
            warnings.append(f"{acc}: có trong golden, không có trong engine")
            continue
        if g is None:
            warnings.append(f"{acc}: có trong engine, không có trong golden")
            continue
        if abs(e.missed_md - g.missed_md) > tolerance_md:
            errors.append(f"{acc}: missed_md engine={e.missed_md} golden={g.missed_md}")
        if e.penalty != g.penalty:
            errors.append(f"{acc}: penalty engine={e.penalty} golden={g.penalty}")
    return errors, warnings


def validate_golden_rows(
    rows: list[GoldenRow],
) -> tuple[list[str], list[str]]:
    """
    Returns (errors, warnings).
    Error: penalty != missed_md × 20k (quy tac cung).
    Warning: missed != required - actual (QA co the tinh Required = Target - Holiday).
    """
    errors: list[str] = []
    warnings: list[str] = []
    for r in rows:
        if r.missed_md <= 0:
            continue
        expected_penalty = int(round(r.missed_md * DEFAULT_PENALTY_PER_MD))
        if r.penalty != expected_penalty:
            errors.append(
                f"{r.account}: penalty {r.penalty} != {expected_penalty} "
                f"(missed {r.missed_md} MD x 20,000)"
            )
        calc_missed = round(r.required_md - r.actual_md, 2)
        if abs(calc_missed - r.missed_md) > 0.02:
            warnings.append(
                f"{r.account}: missed {r.missed_md} vs required-actual {calc_missed}"
            )
    return errors, warnings


def validate_golden_file(path: Path) -> tuple[int, list[str], list[str]]:
    rows = load_golden_csv(path)
    errors, warnings = validate_golden_rows(rows)
    return len(rows), errors, warnings


def load_engine_summary_csv(path: Path) -> dict[str, GoldenRow]:
    """Đọc summary.csv do engine xuất (cùng format golden)."""
    by_account: dict[str, GoldenRow] = {}
    for row in load_golden_csv(path):
        by_account[row.account] = row
    return by_account


def compare_engine_to_golden(
    engine_csv: Path,
    golden_csv: Path,
    *,
    tolerance_md: float = 0.02,
) -> tuple[list[str], list[str]]:
    """
    So từng Account: missed_md, penalty.
    Returns (errors, warnings) — accounts chỉ có ở một phía → warning.
    """
    engine = load_engine_summary_csv(engine_csv)
    golden = load_engine_summary_csv(golden_csv)
    return compare_golden_maps(engine, golden, tolerance_md=tolerance_md)
