from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option


async def ExitFlow(*args: Any, **kwargs: Any) -> Any:
    pending = normalize_items(option(args, kwargs, "pending", option(args, kwargs, "tasks", [])))
    return component_payload("exit_flow", canExit=not pending, pending=pending, message="Ready to exit" if not pending else "Pending work remains")


__all__ = ["ExitFlow"]
