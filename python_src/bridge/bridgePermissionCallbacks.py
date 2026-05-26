"""Permission callback payload helpers for bridge control requests."""

from __future__ import annotations

from typing import Any


def isBridgePermissionResponse(value: Any) -> bool:
    return isinstance(value, dict) and value.get("behavior") in {"allow", "deny"}
