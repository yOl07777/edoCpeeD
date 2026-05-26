from __future__ import annotations

import time
from copy import deepcopy
from typing import Any, Iterable


def now_ms() -> int:
    return int(time.time() * 1000)


def first_mapping(*values: Any) -> dict[str, Any]:
    for value in values:
        if isinstance(value, dict):
            return dict(value)
    return {}


def listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    return [value]


def pick(options: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in options:
            return options[name]
    return default


def merge_dicts(*values: dict[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for value in values:
        if value:
            merged.update(deepcopy(value))
    return merged


def normalize_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "enabled"}
    return bool(value)


def text_filter(items: Iterable[Any], query: str, key: str | None = None) -> list[Any]:
    needle = query.lower().strip()
    result = []
    for item in items:
        haystack = item.get(key, "") if key and isinstance(item, dict) else item
        if not needle or needle in str(haystack).lower():
            result.append(item)
    return result
