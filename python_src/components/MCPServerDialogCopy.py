from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def MCPServerDialogCopy(*args: Any, **kwargs: Any) -> Any:
    name = str(option(args, kwargs, "name", scalar_arg(args, "mcp-server")))
    command = str(option(args, kwargs, "command", f"/mcp add {name}"))
    return component_payload("mcp_server_dialog_copy", name=name, command=command, copied=bool(option(args, kwargs, "copied", False)))


__all__ = ["MCPServerDialogCopy"]
