from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def showInvalidConfigDialog(*args: Any, **kwargs: Any) -> Any:
    errors = normalize_items(option(args, kwargs, "errors", scalar_arg(args, [])))
    return component_payload("invalid_config_dialog", visible=bool(errors) or bool(option(args, kwargs, "visible", True)), errors=errors, count=len(errors))


__all__ = ["showInvalidConfigDialog"]
