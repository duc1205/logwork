"""
Client cho plugin Holiday / Effort của Tinh Vân (jira.tinhvan.com).

REST endpoint:
  GET /rest/effort/1.0/holiday/list
        [?account=<id>&from=<d/Mon/yy>&to=<d/Mon/yy>]
        → list[{"id","lowerUserName","fullName","avatarId",
                "fromDate","toDate","time","reason",
                "holidayTypeId","holidayType"}]

Lưu ý:
- Endpoint là session-scoped: luôn trả về leave của user đang auth.
  Cần credentials riêng cho từng NV, HOẶC admin account để thấy tất cả.
- holidayType: "Cả ngày" (8h), "Buổi sáng" (4h), "Buổi chiều" (4h)
- Đây là NGHỈ PHÉP CÁ NHÂN (personal leave), không phải ngày lễ công ty.
- Ngày lễ công ty: cấu hình thủ công trong holidays.json.

Export servlet (chỉ admin):
  GET /plugins/servlet/holidayExport?account=...&from=...&to=...
  → file XLS binary
"""

from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ..domain.models import EmployeeLeave, LeaveType
from .timesheet_plugin_client import _parse_plugin_date

VN_LEAVE_TYPES = {
    "1": LeaveType.ANNUAL,   # Cả ngày
    "2": LeaveType.ANNUAL,   # Buổi sáng
    "3": LeaveType.ANNUAL,   # Buổi chiều
}


def _parse_leave_hours(time_str: str) -> float:
    try:
        return float(time_str)
    except (ValueError, TypeError):
        return 8.0


def _expand_leave_range(from_date: date, to_date: date, hours: float) -> list[tuple[date, float]]:
    """Mở rộng khoảng nghỉ phép thành list (ngày, giờ). Bỏ qua T7/CN."""
    days: list[tuple[date, float]] = []
    current = from_date
    while current <= to_date:
        if current.weekday() < 5:  # T2-T6
            days.append((current, hours))
        current = date.fromordinal(current.toordinal() + 1)
    return days


@dataclass
class HolidayPluginConfig:
    base_url: str = "https://jira.tinhvan.com"
    username: str = ""
    password: str = ""
    request_timeout: int = 20


class HolidayPluginClient:
    """
    Lấy nghỉ phép cá nhân từ REST plugin Effort.
    Xác thực: Basic auth (username + password/PAT).
    Session-scoped: trả về leave của user auth.
    """

    def __init__(self, config: HolidayPluginConfig):
        self.config = config
        self._auth = base64.b64encode(
            f"{config.username}:{config.password}".encode()
        ).decode()
        self._headers = {
            "Authorization": f"Basic {self._auth}",
            "Accept": "application/json",
            "User-Agent": "LogworkAudit/1.0",
        }

    def _get_json(self, path: str) -> list | dict:
        url = self.config.base_url.rstrip("/") + path
        req = urllib.request.Request(url, headers=self._headers)
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=self.config.request_timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(
                f"HTTP {exc.code} {path}: {detail}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                f"Timeout/error {path}: {exc}"
            ) from exc

    def fetch_raw(self) -> list[dict]:
        """Tất cả leave records của user hiện tại (raw JSON)."""
        data = self._get_json("/rest/effort/1.0/holiday/list")
        return data if isinstance(data, list) else []

    def fetch_leaves(
        self,
        *,
        employee_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[EmployeeLeave]:
        """
        Trả về list[EmployeeLeave] của user auth.
        - employee_id: override account_id (mặc định = username auth)
        - start_date/end_date: lọc theo ngày
        """
        rows = self.fetch_raw()
        leaves: list[EmployeeLeave] = []

        for row in rows:
            from_d = _parse_plugin_date(row.get("fromDate", ""))
            to_d = _parse_plugin_date(row.get("toDate", ""))
            if from_d is None or to_d is None:
                continue

            hours = _parse_leave_hours(row.get("time", "8"))
            type_id = str(row.get("holidayTypeId", "1"))
            leave_type = VN_LEAVE_TYPES.get(type_id, LeaveType.ANNUAL)
            emp_id = employee_id or row.get("lowerUserName", self.config.username).lower()

            for leave_date, leave_hours in _expand_leave_range(from_d, to_d, hours):
                if start_date and leave_date < start_date:
                    continue
                if end_date and leave_date > end_date:
                    continue
                leaves.append(
                    EmployeeLeave(
                        employee_id=emp_id,
                        leave_date=leave_date,
                        leave_type=leave_type,
                        source="jira_plugin",
                    )
                )
        return leaves

    def download_export(
        self,
        *,
        from_date: date,
        to_date: date,
        dest: Path,
    ) -> Path:
        """Tải file XLS export về dest (cần quyền admin)."""
        from .timesheet_plugin_client import _plugin_date

        params = urllib.parse.urlencode({
            "from": _plugin_date(from_date),
            "to": _plugin_date(to_date),
        })
        url = self.config.base_url.rstrip("/") + "/plugins/servlet/holidayExport?" + params
        req = urllib.request.Request(url, headers=self._headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        return dest


def holiday_config_from_env() -> HolidayPluginConfig:
    import os

    return HolidayPluginConfig(
        base_url=os.environ.get("JIRA_BASE_URL", "https://jira.tinhvan.com").strip(),
        username=(
            os.environ.get("JIRA_USERNAME", "").strip()
            or os.environ.get("JIRA_EMAIL", "").strip()
        ),
        password=os.environ.get("JIRA_API_TOKEN", "").strip(),
        request_timeout=int(os.environ.get("JIRA_TIMEOUT", "20")),
    )


def create_holiday_client(
    *, config: HolidayPluginConfig | None = None
) -> HolidayPluginClient:
    return HolidayPluginClient(config or holiday_config_from_env())
