from __future__ import annotations

from typing import Any


async def formatErrorMessage(error: Exception | str, *args: Any, **kwargs: Any) -> str:
    return str(error)


async def getErrorGuidance(error: Exception | str, *args: Any, **kwargs: Any) -> list[str]:
    message = str(error).lower()
    if "manifest" in message or "json" in message:
        return ["Check that plugin.json is valid JSON.", "Ensure required fields such as name and version exist."]
    if "scope" in message:
        return ["Use one of the supported scopes: user, project, local."]
    return ["Run `/plugin help` for supported local plugin commands."]


__all__ = ["formatErrorMessage", "getErrorGuidance"]
