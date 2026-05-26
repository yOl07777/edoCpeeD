from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, safe_int, scalar_arg


async def VimTextInput(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = str(option(args, kwargs, "value", scalar_arg(args, "")) or "")
    mode = str(option(args, kwargs, "mode", "insert") or "insert")
    cursor = max(0, min(safe_int(option(args, kwargs, "cursor", len(value)), len(value)), len(value)))
    return component_payload("vim_text_input", value=value, mode=mode, cursor=cursor, normalMode=mode == "normal")


_module_migration_placeholder = VimTextInput


__all__ = ["VimTextInput"]
