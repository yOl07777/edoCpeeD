from __future__ import annotations

from typing import Any


def first_mapping(*values: Any) -> dict[str, Any]:
    for value in values:
        if isinstance(value, dict):
            return dict(value)
    return {}


def pick(options: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in options:
            return options[name]
    return default


def truthy(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "enabled", "connected", "ready"}
    return bool(value)


def notification(
    *,
    visible: bool,
    title: str,
    message: str,
    level: str = "info",
    **extra: Any,
) -> dict[str, Any]:
    return {
        "provider": "deepseek",
        "visible": visible,
        "level": level,
        "title": title,
        "message": message if visible else "",
        **extra,
    }
