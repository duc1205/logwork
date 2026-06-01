"""Jira client — mock fixtures; LiveJiraClient (Jira Server + Cloud)."""

from __future__ import annotations

import base64
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .excel_import import import_timesheet_csv
from ..domain.models import TimesheetEntry
from ..paths import MOCK_DIR

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
_JIRA_STARTED_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?([+-]\d{4}|Z)?$"
)


@dataclass
class JiraConfig:
    base_url: str = ""
    email: str = ""  # Cloud: email; Server: username (JIRA_USERNAME alias)
    token: str = ""  # API token (Cloud) hoac password/PAT (Server)
    project_keys: tuple[str, ...] = ()
    account_field: str = "name"  # name | email | accountId | displayName
    api_version: int = 2  # 2 = Jira Server; 3 = Jira Cloud


class JiraClient(ABC):
    @abstractmethod
    def fetch_worklogs(
        self,
        *,
        start_date: date,
        end_date: date,
        project_keys: tuple[str, ...] = (),
    ) -> list[TimesheetEntry]:
        ...


class MockJiraClient(JiraClient):
    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or MOCK_DIR

    def fetch_worklogs(
        self,
        *,
        start_date: date,
        end_date: date,
        project_keys: tuple[str, ...] = (),
    ) -> list[TimesheetEntry]:
        csv_path = self.data_dir / "jira_timesheet.csv"
        if csv_path.is_file():
            entries = import_timesheet_csv(csv_path, project_keys=project_keys)
        else:
            entries = self._from_json()

        return [e for e in entries if start_date <= e.work_date <= end_date]

    def _from_json(self) -> list[TimesheetEntry]:
        rows = json.loads((self.data_dir / "timesheet.json").read_text(encoding="utf-8"))
        return [
            TimesheetEntry(
                employee_id=r["employee_id"],
                work_date=date.fromisoformat(r["work_date"]),
                hours=float(r["hours"]),
                issue_key=r.get("issue_key"),
                project_key=r.get("project_key"),
            )
            for r in rows
        ]


def _parse_jira_started(value: str) -> date:
    """Parse Jira worklog `started` → ngày làm việc (timezone VN)."""
    m = _JIRA_STARTED_RE.match(value.strip())
    if not m:
        return date.fromisoformat(value[:10])
    day_s, hh, mm, ss, tz = m.groups()
    if tz in (None, "Z"):
        dt = datetime.fromisoformat(f"{day_s}T{hh}:{mm}:{ss}")
        if tz == "Z":
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        return dt.astimezone(VN_TZ).date()
    dt = datetime.strptime(f"{day_s}T{hh}:{mm}:{ss}{tz}", "%Y-%m-%dT%H:%M:%S%z")
    return dt.astimezone(VN_TZ).date()


def author_to_employee_id(author: dict, *, field: str = "name") -> str:
    """Map Jira worklog author → account_id nội bộ."""
    if field == "name":
        username = (author.get("name") or author.get("key") or "").strip()
        if username:
            return username.lower()
    if field == "email":
        email = (author.get("emailAddress") or "").strip()
        if email and "@" in email:
            return email.split("@", 1)[0].lower()
    if field == "displayName":
        name = (author.get("displayName") or "").strip()
        if name:
            return re.sub(r"\s+", "", name).lower()
    account_id = (author.get("accountId") or author.get("name") or "").strip()
    return account_id or "unknown"


def _build_jql(
    start_date: date,
    end_date: date,
    project_keys: tuple[str, ...],
) -> str:
    jql = (
        f'worklogDate >= "{start_date.isoformat()}" '
        f'AND worklogDate <= "{end_date.isoformat()}"'
    )
    if project_keys:
        keys = ", ".join(project_keys)
        jql += f" AND project in ({keys})"
    return jql


def _aggregate_entries(entries: list[TimesheetEntry]) -> list[TimesheetEntry]:
    """Gộp nhiều worklog cùng (account, ngày, issue) thành một dòng."""
    totals: dict[tuple[str, date, str | None, str | None], float] = defaultdict(float)
    for e in entries:
        key = (e.employee_id, e.work_date, e.issue_key, e.project_key)
        totals[key] += e.hours
    return [
        TimesheetEntry(
            employee_id=k[0],
            work_date=k[1],
            hours=h,
            issue_key=k[2],
            project_key=k[3],
        )
        for k, h in sorted(totals.items(), key=lambda x: (x[0][0], x[0][1]))
    ]


def infer_jira_api_version(base_url: str) -> int:
    """Jira Cloud → v3; Jira Server (vd. jira.tinhvan.com) → v2."""
    host = base_url.lower()
    if "atlassian.net" in host or "atlassian.com" in host:
        return 3
    return 2


def infer_jira_account_field(base_url: str) -> str:
    return "email" if infer_jira_api_version(base_url) == 3 else "name"


class LiveJiraClient(JiraClient):
    """
    Jira REST API — env:
      JIRA_BASE_URL=https://jira.tinhvan.com
      JIRA_USERNAME (hoac JIRA_EMAIL), JIRA_API_TOKEN (password/PAT)
      JIRA_API_VERSION=2 (tu dong neu khong dat; tinhvan = Server 8.3.3)
    Thieu credential → fallback CSV/mock trong data_dir.
    """

    def __init__(self, config: JiraConfig, *, fallback_dir: Path | None = None):
        self.config = config
        self.fallback = MockJiraClient(fallback_dir)
        self._api_enabled = bool(config.base_url and config.token)

    @property
    def api_enabled(self) -> bool:
        return self._api_enabled

    def _api_prefix(self) -> str:
        return f"/rest/api/{self.config.api_version}"

    def fetch_worklogs(
        self,
        *,
        start_date: date,
        end_date: date,
        project_keys: tuple[str, ...] = (),
    ) -> list[TimesheetEntry]:
        keys = project_keys or self.config.project_keys
        if not self._api_enabled:
            return self.fallback.fetch_worklogs(
                start_date=start_date,
                end_date=end_date,
                project_keys=keys,
            )
        raw = self._fetch_worklogs_api(start_date, end_date, keys)
        return _aggregate_entries(raw)

    def _api_request(self, method: str, path: str, body: dict | None = None) -> dict:
        base = self.config.base_url.rstrip("/")
        url = f"{base}{path}"
        data = None
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.config.email:
            token = base64.b64encode(
                f"{self.config.email}:{self.config.token}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {token}"
        else:
            headers["Authorization"] = f"Bearer {self.config.token}"

        if body is not None:
            data = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(
                f"Jira API {method} {path} failed ({exc.code}): {detail}"
            ) from exc

    def _search_issues(self, jql: str) -> list[dict]:
        issues: list[dict] = []
        start_at = 0
        page_size = 100
        prefix = self._api_prefix()

        while True:
            payload = {
                "jql": jql,
                "fields": ["key", "project"],
                "maxResults": page_size,
                "startAt": start_at,
            }
            data = self._api_request("POST", f"{prefix}/search", payload)
            batch = data.get("issues") or []
            issues.extend(batch)
            if start_at + len(batch) >= data.get("total", 0) or not batch:
                break
            start_at += len(batch)
        return issues

    def _fetch_issue_worklogs(self, issue_key: str) -> list[dict]:
        worklogs: list[dict] = []
        start_at = 0
        page_size = 100
        prefix = self._api_prefix()

        while True:
            qs = urllib.parse.urlencode({"startAt": start_at, "maxResults": page_size})
            path = f"{prefix}/issue/{urllib.parse.quote(issue_key)}/worklog?{qs}"
            data = self._api_request("GET", path)
            batch = data.get("worklogs") or []
            worklogs.extend(batch)
            if start_at + len(batch) >= data.get("total", 0) or not batch:
                break
            start_at += len(batch)
        return worklogs

    def _fetch_worklogs_api(
        self,
        start_date: date,
        end_date: date,
        project_keys: tuple[str, ...],
    ) -> list[TimesheetEntry]:
        jql = _build_jql(start_date, end_date, project_keys)
        issues = self._search_issues(jql)
        entries: list[TimesheetEntry] = []

        for issue in issues:
            issue_key = issue.get("key", "")
            fields = issue.get("fields") or {}
            project = fields.get("project") or {}
            project_key = project.get("key")

            for wl in self._fetch_issue_worklogs(issue_key):
                work_date = _parse_jira_started(wl.get("started", ""))
                if work_date < start_date or work_date > end_date:
                    continue
                author = wl.get("author") or {}
                employee_id = author_to_employee_id(
                    author, field=self.config.account_field
                )
                hours = float(wl.get("timeSpentSeconds", 0)) / 3600.0
                if hours <= 0:
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


def jira_config_from_env() -> JiraConfig:
    base_url = os.environ.get("JIRA_BASE_URL", "").strip()
    username = (
        os.environ.get("JIRA_USERNAME", "").strip()
        or os.environ.get("JIRA_EMAIL", "").strip()
    )
    token = os.environ.get("JIRA_API_TOKEN", "").strip()

    api_version_raw = os.environ.get("JIRA_API_VERSION", "").strip()
    if api_version_raw:
        api_version = int(api_version_raw)
    else:
        api_version = infer_jira_api_version(base_url) if base_url else 2

    field = os.environ.get("JIRA_ACCOUNT_FIELD", "").strip().lower()
    if not field:
        field = infer_jira_account_field(base_url) if base_url else "name"
    field_map = {
        "email": "email",
        "accountid": "accountId",
        "displayname": "displayName",
        "name": "name",
        "username": "name",
    }
    account_field = field_map.get(field, field if field in field_map.values() else "name")

    return JiraConfig(
        base_url=base_url,
        email=username,
        token=token,
        project_keys=tuple(
            p.strip()
            for p in os.environ.get("JIRA_PROJECT_KEYS", "").split(",")
            if p.strip()
        ),
        account_field=account_field,
        api_version=api_version,
    )


def create_jira_client(
    *, mock: bool = True, data_dir: Path | None = None
) -> JiraClient:
    if mock:
        return MockJiraClient(data_dir)
    return LiveJiraClient(jira_config_from_env(), fallback_dir=data_dir)
