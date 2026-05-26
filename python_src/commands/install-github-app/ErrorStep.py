"""Structured error step."""

from __future__ import annotations

from typing import Any

from ._shared import step_payload


async def ErrorStep(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return step_payload(
        "error",
        error=kwargs.get("error") or (args[0] if args else "GitHub app setup could not continue."),
        errorReason=kwargs.get("errorReason", "local_shim"),
        errorInstructions=kwargs.get("errorInstructions", []),
    )


__all__ = ["ErrorStep"]
