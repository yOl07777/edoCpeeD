from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, path_label, scalar_arg


async def FileEditToolUseRejectedMessage(*args: Any, **kwargs: Any) -> Any:
    path = path_label(option(args, kwargs, "path", scalar_arg(args, "")))
    reason = str(option(args, kwargs, "reason", "edit rejected"))
    return component_payload("file_edit_tool_use_rejected_message", path=path, reason=reason, summary=f"Edit rejected: {path}" if path else "Edit rejected")


__all__ = ["FileEditToolUseRejectedMessage"]
