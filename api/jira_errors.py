"""Lỗi khi lấy dữ liệu Jira — không fallback sang mock."""


class JiraFetchError(Exception):
    """Plugin/REST Jira thất bại — trả lỗi rõ ràng cho UI."""

    def __init__(self, message: str, *, detail: str | None = None):
        super().__init__(message)
        self.detail = detail or message
