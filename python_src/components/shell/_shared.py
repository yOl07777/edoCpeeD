from __future__ import annotations

from typing import Any


def shell_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def format_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{round(seconds * 1000)}ms"
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    rest = int(seconds % 60)
    return f"{minutes}m {rest}s"

