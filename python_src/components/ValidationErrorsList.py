from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def ValidationErrorsList(*args: Any, **kwargs: Any) -> dict[str, Any]:
    errors = normalize_items(option(args, kwargs, "errors", scalar_arg(args, [])), text_key="message")
    return component_payload("validation_errors_list", errors=errors, count=len(errors), valid=len(errors) == 0)


__all__ = ["ValidationErrorsList"]
