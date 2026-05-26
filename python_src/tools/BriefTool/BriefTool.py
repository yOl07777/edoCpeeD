"""Migrated local BriefTool shim."""

from __future__ import annotations

import os
from typing import Any

from python_src.tools.base import PythonTool, object_schema
from python_src.tools.BriefTool.attachments import resolveAttachments


async def isBriefEnabled(*args: Any, **kwargs: Any) -> bool:
    value = kwargs.get("enabled")
    if value is not None:
        return bool(value)
    env = os.getenv("DEEPCODE_BRIEF_ENABLED", "1").strip().lower()
    return env not in {"0", "false", "no", "off"}


async def isBriefEntitled(*args: Any, **kwargs: Any) -> bool:
    value = kwargs.get("entitled")
    if value is not None:
        return bool(value)
    env = os.getenv("DEEPCODE_BRIEF_ENTITLED", "1").strip().lower()
    return env not in {"0", "false", "no", "off"}


async def brief_tool(
    title: str = "Brief",
    body: str = "",
    attachments: list[str] | None = None,
    cwd: str | None = None,
) -> dict[str, Any]:
    resolved = await resolveAttachments(attachments or [], cwd=cwd or os.getcwd())
    return {
        "ok": True,
        "briefId": "local-brief",
        "title": title,
        "body": body,
        "attachments": resolved,
        "uploaded": False,
    }


BriefTool = PythonTool(
    name="brief",
    description="Create a local structured brief with optional workspace attachments.",
    parameters=object_schema(
        {
            "title": {"type": "string"},
            "body": {"type": "string"},
            "attachments": {"type": "array", "items": {"type": "string"}},
        }
    ),
    handler=brief_tool,
    read_only=True,
)


__all__ = ["BriefTool", "brief_tool", "isBriefEnabled", "isBriefEntitled"]
