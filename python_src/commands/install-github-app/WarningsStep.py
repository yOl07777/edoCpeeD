"""Structured warnings step."""

from __future__ import annotations

from typing import Any

from ._shared import step_payload


async def WarningsStep(*args: Any, **kwargs: Any) -> dict[str, Any]:
    warnings = kwargs.get("warnings")
    if warnings is None and args:
        warnings = args[0]
    return step_payload("warnings", warnings=list(warnings or []))


__all__ = ["WarningsStep"]
