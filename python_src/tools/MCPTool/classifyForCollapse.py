"""Classify MCP tool result display density."""

from __future__ import annotations

from typing import Any


async def classifyMcpToolForCollapse(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = args[0] if args else kwargs.get("result") or kwargs
    text = str(value)
    collapse = len(text) > int(kwargs.get("threshold", 4_000))
    return {"collapse": collapse, "reason": "large-output" if collapse else "small-output", "chars": len(text)}


__all__ = ["classifyMcpToolForCollapse"]
