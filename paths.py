"""Đường dẫn artifact logwork."""

import os
from pathlib import Path

LOGWORK_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = LOGWORK_DIR / "fixtures"
MOCK_DIR = FIXTURES_DIR / "mock"  # chỉ dùng cho python -m logwork test / CLI offline
LIVE_DATA_DIR = FIXTURES_DIR / "live"
OUTPUT_DIR = LOGWORK_DIR / "output"
