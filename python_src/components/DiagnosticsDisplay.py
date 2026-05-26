from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def DiagnosticsDisplay(*args: Any, **kwargs: Any) -> Any:
    diagnostics = normalize_items(option(args, kwargs, "diagnostics", scalar_arg(args, [])))
    errors = [item for item in diagnostics if str(item.get("severity", "")).lower() in {"error", "fatal"}]
    warnings = [item for item in diagnostics if str(item.get("severity", "")).lower() == "warning"]
    return component_payload("diagnostics_display", diagnostics=diagnostics, errors=len(errors), warnings=len(warnings), ok=not errors)


__all__ = ["DiagnosticsDisplay"]
