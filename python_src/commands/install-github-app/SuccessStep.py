"""Structured success step."""

from __future__ import annotations

from typing import Any

from ._shared import step_payload


async def SuccessStep(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return step_payload(
        "success",
        dryRun=bool(kwargs.get("dryRun", True)),
        message="DeepSeek GitHub Actions setup guidance was generated. Apply it manually after review.",
    )


__all__ = ["SuccessStep"]
