from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, normalize_items, option, scalar_arg


async def SandboxViolationExpandedView(*args: Any, **kwargs: Any) -> Any:
    violation = option(args, kwargs, "violation", scalar_arg(args, first_options(args)))
    details = normalize_items(option(args, kwargs, "details", violation.get("details", []) if isinstance(violation, dict) else []))
    return component_payload("sandbox_violation_expanded_view", violation=violation, details=details, blocked=True)


__all__ = ["SandboxViolationExpandedView"]
