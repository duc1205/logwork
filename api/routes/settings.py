"""Admin — cấu hình phạt và ngày nghỉ lễ."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from ..auth_service import AuthUser
from ..deps import require_settings_admin
from ..schemas import (
    AuditSettingsResponse,
    AuditSettingsUpdate,
    HolidayCreate,
    HolidayItem,
    HolidaysListResponse,
    OtRulesResponse,
    OtRulesUpdate,
    OvertimeCreate,
    OvertimeItem,
    OvertimeListResponse,
)
from ..settings_store import (
    add_holiday,
    add_overtime_record,
    get_audit_settings,
    list_holidays,
    list_overtime,
    remove_holiday,
    remove_overtime_record,
    update_audit_settings,
    update_ot_rules,
)

router = APIRouter(
    prefix="/admin/settings",
    tags=["settings"],
    dependencies=[Depends(require_settings_admin)],
)


@router.get("/audit", response_model=AuditSettingsResponse)
def get_settings(_user: AuthUser = Depends(require_settings_admin)) -> AuditSettingsResponse:
    return AuditSettingsResponse(**get_audit_settings())


@router.put("/audit", response_model=AuditSettingsResponse)
def put_settings(
    body: AuditSettingsUpdate,
    _user: AuthUser = Depends(require_settings_admin),
) -> AuditSettingsResponse:
    if (
        body.penalty_per_md is None
        and body.tolerance_hours is None
        and body.compensation_threshold is None
    ):
        raise HTTPException(400, detail="Cần ít nhất một trường cấu hình")
    try:
        result = update_audit_settings(
            penalty_per_md=body.penalty_per_md,
            tolerance_hours=body.tolerance_hours,
            compensation_threshold=body.compensation_threshold,
        )
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    return AuditSettingsResponse(**result)


@router.get("/holidays", response_model=HolidaysListResponse)
def get_holidays(_user: AuthUser = Depends(require_settings_admin)) -> HolidaysListResponse:
    items = [HolidayItem(**h) for h in list_holidays()]
    return HolidaysListResponse(total=len(items), items=items)


@router.post("/holidays", response_model=HolidaysListResponse)
def post_holiday(
    body: HolidayCreate,
    _user: AuthUser = Depends(require_settings_admin),
) -> HolidaysListResponse:
    try:
        items = add_holiday(
            holiday_date=body.holiday_date,
            name=body.name,
            is_company_wide=body.is_company_wide,
        )
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    rows = [HolidayItem(**h) for h in items]
    return HolidaysListResponse(total=len(rows), items=rows)


@router.delete("/holidays/{holiday_date}", response_model=HolidaysListResponse)
def delete_holiday(
    holiday_date: date,
    _user: AuthUser = Depends(require_settings_admin),
) -> HolidaysListResponse:
    try:
        items = remove_holiday(holiday_date)
    except ValueError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    rows = [HolidayItem(**h) for h in items]
    return HolidaysListResponse(total=len(rows), items=rows)


@router.get("/ot-rules", response_model=OtRulesResponse)
def get_ot_rules(_user: AuthUser = Depends(require_settings_admin)) -> OtRulesResponse:
    cfg = get_audit_settings()
    return OtRulesResponse(**cfg["ot_rules"])


@router.put("/ot-rules", response_model=OtRulesResponse)
def put_ot_rules(
    body: OtRulesUpdate,
    _user: AuthUser = Depends(require_settings_admin),
) -> OtRulesResponse:
    fields = body.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(400, detail="Cần ít nhất một trường ot_rules")
    try:
        result = update_ot_rules(**fields)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    return OtRulesResponse(**result)


@router.get("/overtime", response_model=OvertimeListResponse)
def get_overtime(_user: AuthUser = Depends(require_settings_admin)) -> OvertimeListResponse:
    items = [OvertimeItem(**r) for r in list_overtime()]
    return OvertimeListResponse(total=len(items), items=items)


@router.post("/overtime", response_model=OvertimeListResponse)
def post_overtime(
    body: OvertimeCreate,
    _user: AuthUser = Depends(require_settings_admin),
) -> OvertimeListResponse:
    try:
        items = add_overtime_record(
            employee_id=body.employee_id,
            ot_date=body.ot_date,
            ot_hours=body.ot_hours,
            reason=body.reason,
            status=body.status,
            approved_by=body.approved_by,
        )
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    rows = [OvertimeItem(**r) for r in items]
    return OvertimeListResponse(total=len(rows), items=rows)


@router.delete("/overtime/{employee_id}/{ot_date}", response_model=OvertimeListResponse)
def delete_overtime(
    employee_id: str,
    ot_date: date,
    _user: AuthUser = Depends(require_settings_admin),
) -> OvertimeListResponse:
    try:
        items = remove_overtime_record(employee_id, ot_date)
    except ValueError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    rows = [OvertimeItem(**r) for r in items]
    return OvertimeListResponse(total=len(rows), items=rows)
