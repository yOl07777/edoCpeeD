from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, path_label, scalar_arg


async def NotebookEditToolUseRejectedMessage(*args: Any, **kwargs: Any) -> Any:
    path = path_label(option(args, kwargs, "path", scalar_arg(args, "")))
    cell = option(args, kwargs, "cell", option(args, kwargs, "cellIndex", None))
    return component_payload("notebook_edit_tool_use_rejected_message", path=path, cell=cell, reason=str(option(args, kwargs, "reason", "notebook edit rejected")))


__all__ = ["NotebookEditToolUseRejectedMessage"]
