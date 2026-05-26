"""Structured replacement for the React API-key step."""

from __future__ import annotations

from typing import Any

from ._shared import DEFAULT_SECRET_NAME, step_payload


async def ApiKeyStep(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return step_payload(
        "api-key",
        secretName=kwargs.get("secretName", DEFAULT_SECRET_NAME),
        selectedApiKeyOption=kwargs.get("selectedApiKeyOption", "existing"),
        message="Use a DeepSeek API key stored as a GitHub Actions secret; this shim never stores or prints the key.",
    )


__all__ = ["ApiKeyStep"]
