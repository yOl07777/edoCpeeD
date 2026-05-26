from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def KeybindingWarnings(*args: Any, **kwargs: Any) -> Any:
    warnings = normalize_items(option(args, kwargs, "warnings", scalar_arg(args, [])))
    return component_payload("keybinding_warnings", warnings=warnings, count=len(warnings), hasWarnings=bool(warnings))


__all__ = ["KeybindingWarnings"]
