"""Đường dẫn dữ liệu cấu hình live — tách khỏi fixtures/mock (chỉ dùng cho test)."""

from __future__ import annotations

import os
from pathlib import Path

from ..paths import LIVE_DATA_DIR


def live_data_dir() -> Path:
    """Thư mục config/roster/holidays cho API. Override: LOGWORK_DATA_DIR."""
    return Path(os.environ.get("LOGWORK_DATA_DIR", LIVE_DATA_DIR))
