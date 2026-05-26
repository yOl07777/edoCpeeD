from __future__ import annotations

from pathlib import Path
from typing import Any


def normalize_rule(rule: Any = None, **kwargs: Any) -> dict[str, Any]:
    if isinstance(rule, dict):
        data = dict(rule)
    elif rule is None:
        data = {}
    else:
        data = {"value": str(rule)}
    data.update({k: v for k, v in kwargs.items() if v is not None})
    data.setdefault("tool", data.get("toolName") or data.get("tool_name") or "*")
    data.setdefault("value", "*")
    data.setdefault("behavior", "allow")
    return data


def normalize_rules(raw: Any = None) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, dict):
        raw = raw.get("rules") or [raw]
    if isinstance(raw, str):
        raw = [raw]
    return [normalize_rule(item) for item in raw or []]


def workspace_entry(path: Any) -> dict[str, Any]:
    target = Path(str(path or ".")).expanduser().resolve()
    return {"path": str(target), "exists": target.exists(), "allowed": True}


__all__ = ["normalize_rule", "normalize_rules", "workspace_entry"]
