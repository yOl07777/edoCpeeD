"""Terminal IO helpers for migrated Ink shims."""

from __future__ import annotations

from typing import Any


def createTermioState(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {
        "provider": "deepseek",
        "input": kwargs.get("input"),
        "output": kwargs.get("output"),
        "rawMode": bool(kwargs.get("rawMode", False)),
    }


default = createTermioState
