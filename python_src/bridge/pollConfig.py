"""Bridge poll interval config parsing."""

from __future__ import annotations

import json
import os
from typing import Any

from .pollConfigDefaults import DEFAULT_POLL_CONFIG


def _int_value(raw: Any, default: int) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _validate(config: dict[str, Any]) -> dict[str, int] | None:
    merged = dict(DEFAULT_POLL_CONFIG)
    merged.update(config)
    result = {key: _int_value(value, DEFAULT_POLL_CONFIG[key]) for key, value in merged.items()}
    if result["poll_interval_ms_not_at_capacity"] < 100:
        return None
    if result["poll_interval_ms_at_capacity"] not in (0,) and result["poll_interval_ms_at_capacity"] < 100:
        return None
    if result["non_exclusive_heartbeat_interval_ms"] < 0:
        return None
    if result["multisession_poll_interval_ms_not_at_capacity"] < 100:
        return None
    if result["multisession_poll_interval_ms_partial_capacity"] < 100:
        return None
    if result["multisession_poll_interval_ms_at_capacity"] not in (0,) and result["multisession_poll_interval_ms_at_capacity"] < 100:
        return None
    if result["reclaim_older_than_ms"] < 1:
        return None
    if result["session_keepalive_interval_v2_ms"] < 0:
        return None
    if result["non_exclusive_heartbeat_interval_ms"] == 0 and (
        result["poll_interval_ms_at_capacity"] == 0
        or result["multisession_poll_interval_ms_at_capacity"] == 0
    ):
        return None
    return result


def getPollIntervalConfig(raw: dict[str, Any] | None = None) -> dict[str, int]:
    if raw is None:
        env = os.getenv("DEEPSEEK_BRIDGE_POLL_CONFIG")
        if env:
            try:
                raw = json.loads(env)
            except ValueError:
                raw = None
    parsed = _validate(raw or {})
    return parsed or dict(DEFAULT_POLL_CONFIG)
