"""
Client cho plugin ProjectTimesheet của Tinh Vân (jira.tinhvan.com).

REST endpoints (không cần Jira API key, dùng Basic auth):
  GET /rest/common-control/1.0/api/get-all-user
        → [{"id": <int>, "text": "<username>"}, ...]

  GET /rest/projectTimesheet/1.0/timesheet-log/count
        ?account=<user_id>&fromDate=<d/Mon/yy>&toDate=<d/Mon/yy>&unit=<unit_id>
        → {"totalRecords": N, "totalPages": P, ...}

  GET /rest/projectTimesheet/1.0/timesheet-log/search
        ?account=<user_id>&fromDate=<d/Mon/yy>&toDate=<d/Mon/yy>&page=<n>&limit=<n>
        → list[{"projectname","user","date","time","estimate","issueKey","description"}]

  GET /plugins/servlet/timesheetlogreport
        ?account=<user_id>&fromDate=<d/Mon/yy>&toDate=<d/Mon/yy>
        → binary file (Excel/CSV export)
"""

from __future__ import annotations

import base64
import calendar as _calendar
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

from ..domain.models import TimesheetEntry

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
_DATE_RE = re.compile(
    r"(\d{1,2})/([A-Za-z]+)/(\d{2,4})"  # 29/May/2026 hoặc 29/May/26
)
_MON_ABBREV = {v.lower(): i for i, v in enumerate(_calendar.month_abbr) if v}


def _plugin_date(d: date) -> str:
    """date → định dạng plugin: '1/May/26' (ngày không đệm 0, năm 2 số)."""
    return f"{d.day}/{d.strftime('%b')}/{d.strftime('%y')}"


def _parse_plugin_date(s: str) -> date | None:
    """'29/May/2026' hoặc '29/May/26' → date."""
    m = _DATE_RE.match(s.strip())
    if not m:
        return None
    day, mon, year = int(m.group(1)), m.group(2).lower(), m.group(3)
    month = _MON_ABBREV.get(mon[:3])
    if not month:
        return None
    yr = int(year)
    if yr < 100:
        yr += 2000
    try:
        return date(yr, month, day)
    except ValueError:
        return None


def _parse_hours(s: str) -> float:
    """'8.00' hoặc '1h30m' → float hours."""
    s = s.strip()
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        pass
    total = 0.0
    for h_m in re.findall(r"(\d+(?:\.\d+)?)\s*([hm])", s.lower()):
        val, unit = float(h_m[0]), h_m[1]
        total += val if unit == "h" else val / 60
    return total


def _issue_to_project(issue_key: str) -> str | None:
    """'TVE2516TK-793' → 'TVE2516TK'."""
    parts = issue_key.rsplit("-", 1)
    return parts[0] if len(parts) == 2 else None


@dataclass
class TimesheetPluginConfig:
    base_url: str = "https://jira.tinhvan.com"
    username: str = ""
    password: str = ""
    page_size: int = 100
    request_timeout: int = 30
    retry_count: int = 2


@dataclass
class UserInfo:
    id: int
    username: str


class TimesheetPluginClient:
    """
    Lấy worklog qua REST plugin ProjectTimesheet.
    Xác thực: Basic auth (username + password/PAT).
    """

    def __init__(self, config: TimesheetPluginConfig):
        self.config = config
        self._auth = base64.b64encode(
            f"{config.username}:{config.password}".encode()
        ).decode()
        self._headers = {
            "Authorization": f"Basic {self._auth}",
            "Accept": "application/json",
            "User-Agent": "LogworkAudit/1.0",
        }
        self._user_cache: dict[str, int] | None = None

    def _get(self, path: str) -> bytes:
        url = self.config.base_url.rstrip("/") + path
        req = urllib.request.Request(url, headers=self._headers)
        last_exc: Exception | None = None
        for attempt in range(self.config.retry_count + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.config.request_timeout) as r:
                    return r.read()
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:400]
                raise RuntimeError(
                    f"HTTP {exc.code} {path}: {detail}"
                ) from exc
            except Exception as exc:
                last_exc = exc
                if attempt < self.config.retry_count:
                    time.sleep(1)
        raise RuntimeError(f"Timeout/error {path} after retries: {last_exc}") from last_exc

    def _json(self, path: str) -> object:
        raw = self._get(path)
        return json.loads(raw.decode("utf-8"))

    # ------------------------------------------------------------------ users
    def fetch_all_users(self) -> list[UserInfo]:
        """Tất cả user trong hệ thống: list[UserInfo(id, username)]."""
        data = self._json("/rest/common-control/1.0/api/get-all-user")
        return [UserInfo(id=u["id"], username=u["text"]) for u in data]

    def username_to_id(self, username: str) -> int | None:
        """Tra ID số từ username (có cache)."""
        if self._user_cache is None:
            self._user_cache = {u.username.lower(): u.id for u in self.fetch_all_users()}
        return self._user_cache.get(username.lower())

    def build_user_map(self, usernames: list[str]) -> dict[str, int]:
        """username → numeric_id cho danh sách NV."""
        if self._user_cache is None:
            self._user_cache = {u.username.lower(): u.id for u in self.fetch_all_users()}
        result: dict[str, int] = {}
        for un in usernames:
            uid = self._user_cache.get(un.lower())
            if uid is not None:
                result[un] = uid
        return result

    # -------------------------------------------------------------- timesheets
    def count_worklogs(
        self,
        *,
        user_id: int | None = None,
        from_date: date,
        to_date: date,
        unit_id: int | None = None,
    ) -> int:
        params: dict[str, object] = {
            "fromDate": _plugin_date(from_date),
            "toDate": _plugin_date(to_date),
        }
        if user_id is not None:
            params["account"] = user_id
        if unit_id is not None:
            params["unit"] = unit_id
        path = "/rest/projectTimesheet/1.0/timesheet-log/count?" + urllib.parse.urlencode(params)
        data = self._json(path)
        if isinstance(data, dict):
            return int(data.get("totalRecords", 0))
        return 0

    def fetch_worklogs_raw(
        self,
        *,
        user_id: int | None = None,
        from_date: date,
        to_date: date,
        unit_id: int | None = None,
    ) -> list[dict]:
        """Tất cả trang dữ liệu raw từ plugin API (20 records/page, server-fixed)."""
        base_params: dict[str, object] = {
            "fromDate": _plugin_date(from_date),
            "toDate": _plugin_date(to_date),
        }
        if user_id is not None:
            base_params["account"] = user_id
        if unit_id is not None:
            base_params["unit"] = unit_id

        # Lấy tổng số trang từ count endpoint
        count_path = "/rest/projectTimesheet/1.0/timesheet-log/count?" + urllib.parse.urlencode(base_params)
        count_data = self._json(count_path)
        total_pages = int(count_data.get("totalPages", 1)) if isinstance(count_data, dict) else 1

        all_rows: list[dict] = []
        for page in range(1, total_pages + 1):
            params = {**base_params, "page": page}
            path = "/rest/projectTimesheet/1.0/timesheet-log/search?" + urllib.parse.urlencode(params)
            batch = self._json(path)
            if not isinstance(batch, list) or not batch:
                break
            all_rows.extend(batch)
        return all_rows

    def fetch_worklogs(
        self,
        *,
        start_date: date,
        end_date: date,
        project_keys: tuple[str, ...] = (),
        usernames: list[str] | None = None,
        unit_id: int | None = None,
    ) -> list[TimesheetEntry]:
        """
        Trả về list[TimesheetEntry] trong khoảng [start_date, end_date].
        - usernames=None  → lấy tất cả NV
        - usernames=[...] → chỉ lấy các NV trong danh sách
        """
        if usernames:
            user_map = self.build_user_map(usernames)
            ids_to_fetch: list[tuple[str, int | None]] = [
                (un, uid) for un, uid in user_map.items()
            ]
        else:
            # Không chỉ định NV → lấy toàn bộ (cẩn thận: chậm với nhiều NV)
            ids_to_fetch = [("", None)]

        rows: list[dict] = []
        for _, uid in ids_to_fetch:
            rows.extend(
                self.fetch_worklogs_raw(
                    user_id=uid,
                    from_date=start_date,
                    to_date=end_date,
                    unit_id=unit_id,
                )
            )

        entries: list[TimesheetEntry] = []
        for row in rows:
            work_date = _parse_plugin_date(row.get("date", ""))
            if work_date is None:
                continue
            if work_date < start_date or work_date > end_date:
                continue
            hours = _parse_hours(row.get("time", "0"))
            if hours <= 0:
                continue
            issue_key = (row.get("issueKey") or "").strip() or None
            project_key = _issue_to_project(issue_key) if issue_key else None
            if project_keys and project_key and project_key not in project_keys:
                continue
            employee_id = (row.get("user") or "").strip().lower()
            if usernames and employee_id not in {u.lower() for u in usernames}:
                continue
            entries.append(
                TimesheetEntry(
                    employee_id=employee_id,
                    work_date=work_date,
                    hours=hours,
                    issue_key=issue_key,
                    project_key=project_key,
                )
            )
        return entries

    def download_export(
        self,
        *,
        from_date: date,
        to_date: date,
        user_id: int | None = None,
        unit_id: int | None = None,
        dest: Path,
    ) -> Path:
        """Tải file export (Excel) từ servlet về dest."""
        params: dict[str, object] = {
            "fromDate": _plugin_date(from_date),
            "toDate": _plugin_date(to_date),
        }
        if user_id is not None:
            params["account"] = user_id
        if unit_id is not None:
            params["unit"] = unit_id
        path = "/plugins/servlet/timesheetlogreport?" + urllib.parse.urlencode(params)
        raw = self._get(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        return dest


def plugin_config_from_env() -> TimesheetPluginConfig:
    import os
    return TimesheetPluginConfig(
        base_url=os.environ.get("JIRA_BASE_URL", "https://jira.tinhvan.com").strip(),
        username=(
            os.environ.get("JIRA_USERNAME", "").strip()
            or os.environ.get("JIRA_EMAIL", "").strip()
        ),
        password=os.environ.get("JIRA_API_TOKEN", "").strip(),
        page_size=int(os.environ.get("JIRA_PAGE_SIZE", "100")),
        request_timeout=int(os.environ.get("JIRA_TIMEOUT", "30")),
    )


def create_plugin_client(
    *, config: TimesheetPluginConfig | None = None
) -> TimesheetPluginClient:
    return TimesheetPluginClient(config or plugin_config_from_env())
