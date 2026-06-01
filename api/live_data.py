"""Đường dẫn dữ liệu cấu hình live — tách khỏi fixtures/mock (chỉ dùng cho test)."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from ..paths import LOGWORK_DIR

logger = logging.getLogger("logwork.api")

_DEFAULT_LIVE = LOGWORK_DIR / "fixtures" / "live"


def _has_live_config(path: Path) -> bool:
    return (path / "config.json").is_file()


def live_data_dir() -> Path:
    """Thư mục config/roster/holidays cho API.

    Ưu tiên ``LOGWORK_DATA_DIR`` chỉ khi có ``config.json``; nếu env trỏ path cũ/sai
    (vd. sau khi clone repo sang ``d:\\logwork``) thì fallback về ``fixtures/live`` của package.
    """
    override = os.environ.get("LOGWORK_DATA_DIR", "").strip()
    if override:
        candidate = Path(override)
        if _has_live_config(candidate):
            return candidate
        logger.warning(
            "LOGWORK_DATA_DIR=%s không có config.json — dùng %s",
            candidate,
            _DEFAULT_LIVE,
        )
    if not _has_live_config(_DEFAULT_LIVE):
        raise FileNotFoundError(
            f"Thiếu cấu hình live: {_DEFAULT_LIVE / 'config.json'}. "
            "Copy từ fixtures/live hoặc đặt LOGWORK_DATA_DIR đúng."
        )
    return _DEFAULT_LIVE
