"""Env-less bridge timing/configuration helpers."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from .bridgeEnabled import isEnvLessBridgeEnabled

DEFAULT_ENV_LESS_BRIDGE_CONFIG = {
    "init_retry_max_attempts": 3,
    "init_retry_base_delay_ms": 500,
    "init_retry_jitter_fraction": 0.25,
    "init_retry_max_delay_ms": 4000,
    "http_timeout_ms": 10_000,
    "uuid_dedup_buffer_size": 2000,
    "heartbeat_interval_ms": 20_000,
    "heartbeat_jitter_fraction": 0.1,
    "token_refresh_buffer_ms": 300_000,
    "teardown_archive_timeout_ms": 1500,
    "connect_timeout_ms": 15_000,
    "min_version": "0.0.0",
    "should_show_app_upgrade_message": False,
}


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(p) for p in re.findall(r"\d+", version)[:3]) or (0,)


def _validate(raw: dict[str, Any]) -> dict[str, Any] | None:
    cfg = dict(DEFAULT_ENV_LESS_BRIDGE_CONFIG)
    cfg.update(raw)
    checks = [
        1 <= int(cfg["init_retry_max_attempts"]) <= 10,
        int(cfg["init_retry_base_delay_ms"]) >= 100,
        0 <= float(cfg["init_retry_jitter_fraction"]) <= 1,
        int(cfg["init_retry_max_delay_ms"]) >= 500,
        int(cfg["http_timeout_ms"]) >= 2000,
        100 <= int(cfg["uuid_dedup_buffer_size"]) <= 50_000,
        5000 <= int(cfg["heartbeat_interval_ms"]) <= 30_000,
        0 <= float(cfg["heartbeat_jitter_fraction"]) <= 0.5,
        30_000 <= int(cfg["token_refresh_buffer_ms"]) <= 1_800_000,
        500 <= int(cfg["teardown_archive_timeout_ms"]) <= 2000,
        5000 <= int(cfg["connect_timeout_ms"]) <= 60_000,
        isinstance(cfg["min_version"], str),
    ]
    if not all(checks):
        return None
    return cfg


async def getEnvLessBridgeConfig(raw: dict[str, Any] | None = None) -> dict[str, Any]:
    if raw is None:
        env = os.getenv("DEEPSEEK_ENVLESS_BRIDGE_CONFIG")
        if env:
            try:
                raw = json.loads(env)
            except ValueError:
                raw = None
    return _validate(raw or {}) or dict(DEFAULT_ENV_LESS_BRIDGE_CONFIG)


async def checkEnvLessBridgeMinVersion(current_version: str | None = None) -> str | None:
    cfg = await getEnvLessBridgeConfig()
    current = current_version or os.getenv("DEEPCODE_VERSION", "0.0.0")
    required = cfg.get("min_version", "0.0.0")
    if required and _version_tuple(current) < _version_tuple(str(required)):
        return (
            f"Your version of DeepCode ({current}) is too old for Remote Control.\n"
            f"Version {required} or higher is required."
        )
    return None


async def shouldShowAppUpgradeMessage() -> bool:
    if not isEnvLessBridgeEnabled():
        return False
    cfg = await getEnvLessBridgeConfig()
    return bool(cfg.get("should_show_app_upgrade_message"))
