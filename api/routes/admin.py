"""Admin routes — golden QA compare."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from ..auth_service import AuthUser
from ..credential_store import JiraCredentials
from ..deps import get_jira_credentials, require_admin
from ...reporting.golden_validate import (
    compare_golden_maps,
    golden_rows_to_map,
    load_golden_csv_text,
    report_to_golden_map,
    validate_golden_rows,
)
from ..period_helpers import clip_report
from ..period_query import resolve_period
from ..report_fetch import fetch_team_report
from ..schemas import GoldenCompareResponse, GoldenCompareRow

router = APIRouter(prefix="/admin", tags=["admin"])


def _build_compare_rows(
    engine: dict,
    golden: dict,
    errors: list[str],
    warnings: list[str],
) -> list[GoldenCompareRow]:
    error_accounts = {e.split(":")[0] for e in errors}
    warn_accounts = {w.split(":")[0] for w in warnings}
    rows: list[GoldenCompareRow] = []
    for acc in sorted(set(engine) | set(golden)):
        e = engine.get(acc)
        g = golden.get(acc)
        if acc in error_accounts:
            status = "error"
        elif acc in warn_accounts:
            status = "warning"
        else:
            status = "ok"
        rows.append(
            GoldenCompareRow(
                account=acc,
                engine_missed_md=e.missed_md if e else None,
                golden_missed_md=g.missed_md if g else None,
                engine_penalty=e.penalty if e else None,
                golden_penalty=g.penalty if g else None,
                status=status,
            )
        )
    return rows


@router.post("/golden/compare", response_model=GoldenCompareResponse)
async def golden_compare(
    file: UploadFile = File(..., description="CSV golden QA (cùng format export)"),
    week: date | None = Query(None),
    month: str | None = Query(None),
    start: date | None = Query(None),
    end: date | None = Query(None),
    _user: AuthUser = Depends(require_admin),
    creds: JiraCredentials = Depends(get_jira_credentials),
) -> GoldenCompareResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, detail="Chỉ chấp nhận file .csv")

    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    try:
        golden_list = load_golden_csv_text(text)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc

    golden_map = golden_rows_to_map(golden_list)
    _, val_errors, val_warnings = validate_golden_rows(golden_list)

    period = resolve_period(week=week, month=month, start=start, end=end)
    report, source, as_of = fetch_team_report(creds, period)
    report = clip_report(report, as_of)
    engine_map = report_to_golden_map(report)

    errors, warnings = compare_golden_maps(engine_map, golden_map)
    errors = val_errors + errors
    warnings = val_warnings + warnings

    matched = sum(
        1
        for acc in set(engine_map) & set(golden_map)
        if acc not in {e.split(":")[0] for e in errors}
        and acc not in {w.split(":")[0] for w in warnings}
    )

    return GoldenCompareResponse(
        week_start=report.week_start,
        week_end=report.week_end,
        period_mode=period.mode,
        data_source=source,
        golden_rows=len(golden_map),
        engine_rows=len(engine_map),
        matched=matched,
        errors=errors,
        warnings=warnings,
        ok=len(errors) == 0,
        rows=_build_compare_rows(engine_map, golden_map, errors, warnings),
    )


@router.post("/golden/validate")
async def golden_validate_upload(
    file: UploadFile = File(...),
    _user: AuthUser = Depends(require_admin),
) -> dict:
    """Kiểm tra cấu trúc + công thức penalty của file golden (không cần engine)."""
    raw = await file.read()
    text = raw.decode("utf-8-sig", errors="replace")
    try:
        rows = load_golden_csv_text(text)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    errors, warnings = validate_golden_rows(rows)
    return {
        "rows": len(rows),
        "errors": errors,
        "warnings": warnings,
        "ok": len(errors) == 0,
    }
