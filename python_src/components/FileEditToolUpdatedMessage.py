from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, path_label, scalar_arg


async def FileEditToolUpdatedMessage(*args: Any, **kwargs: Any) -> Any:
    path = path_label(option(args, kwargs, "path", scalar_arg(args, "")))
    return component_payload("file_edit_tool_updated_message", path=path, summary=f"Updated {path}" if path else "File updated")


__all__ = ["FileEditToolUpdatedMessage"]
