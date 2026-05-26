from __future__ import annotations

import difflib
from typing import Any

from python_src.components._shared import component_payload, option, path_label


async def FileEditToolDiff(*args: Any, **kwargs: Any) -> Any:
    old = str(option(args, kwargs, "oldText", option(args, kwargs, "old_text", "")))
    new = str(option(args, kwargs, "newText", option(args, kwargs, "new_text", "")))
    path = path_label(option(args, kwargs, "path", "file"))
    diff = "\n".join(difflib.unified_diff(old.splitlines(), new.splitlines(), fromfile=f"a/{path}", tofile=f"b/{path}", lineterm=""))
    return component_payload("file_edit_tool_diff", path=path, diff=diff, changed=old != new)


__all__ = ["FileEditToolDiff"]
