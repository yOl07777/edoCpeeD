from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, safe_int


async def IdleReturnDialog(*args: Any, **kwargs: Any) -> Any:
    elapsed = safe_int(option(args, kwargs, "elapsedSeconds", option(args, kwargs, "elapsed", 0)))
    changes = normalize_items(option(args, kwargs, "changes", []))
    return component_payload("idle_return_dialog", elapsedSeconds=elapsed, changes=changes, changed=bool(changes))


__all__ = ["IdleReturnDialog"]
