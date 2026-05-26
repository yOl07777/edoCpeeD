from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def ToolUseLoader(*args: Any, **kwargs: Any) -> dict[str, Any]:
    tool = str(option(args, kwargs, "tool", option(args, kwargs, "name", scalar_arg(args, ""))) or "")
    status = str(option(args, kwargs, "status", "running") or "running")
    return component_payload("tool_use_loader", tool=tool, status=status, loading=status in {"pending", "running"})


__all__ = ["ToolUseLoader"]
