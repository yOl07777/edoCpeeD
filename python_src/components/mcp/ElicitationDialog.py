from __future__ import annotations

from typing import Any

from python_src.components.mcp._shared import mcp_payload


async def ElicitationDialog(*args: Any, **kwargs: Any) -> Any:
    prompt = str(kwargs.get("prompt") or (args[0] if args else "MCP server requested input."))
    fields = kwargs.get("fields") or []
    return mcp_payload(
        "mcp_elicitation_dialog",
        prompt=prompt,
        fields=fields,
        responses=kwargs.get("responses") or {},
        actions=["submit", "cancel"],
    )


__all__ = ["ElicitationDialog"]
