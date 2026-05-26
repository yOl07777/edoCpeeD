"""Structured OAuth flow step."""

from __future__ import annotations

from typing import Any

from ._shared import step_payload


async def OAuthFlowStep(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return step_payload(
        "oauth-flow",
        supported=False,
        message="Claude OAuth token creation is not available in the DeepSeek migration shim; use a DeepSeek API key secret instead.",
    )


__all__ = ["OAuthFlowStep"]
