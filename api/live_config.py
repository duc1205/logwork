"""Cấu hình runtime cho API live (Jira)."""

from __future__ import annotations

import os

from ..infra.data_loader import load_config
from ..domain.models import AuditConfig
from .live_data import live_data_dir


def load_audit_config() -> AuditConfig:
    """Config đối soát — project_keys có thể override bằng env."""
    cfg = load_config(live_data_dir())
    raw = os.environ.get("LOGWORK_PROJECT_KEYS", "").strip()
    if raw == "*":
        keys: tuple[str, ...] = ()
    elif raw:
        keys = tuple(k.strip() for k in raw.split(",") if k.strip())
    else:
        keys = ()
    return AuditConfig(
        min_hours=cfg.min_hours,
        max_hours=cfg.max_hours,
        tolerance_hours=cfg.tolerance_hours,
        penalty_per_md=cfg.penalty_per_md,
        compensation_threshold=cfg.compensation_threshold,
        project_keys=keys,
        predictive_tue_pace_min=cfg.predictive_tue_pace_min,
        predictive_wed_pace_min=cfg.predictive_wed_pace_min,
    )
